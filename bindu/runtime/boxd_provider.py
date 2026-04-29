"""BoxdRuntimeProvider — runs a bindu agent inside a boxd microVM.

Two modes:

- **A2** (default): ship local source via tar+gzip, install deps in the VM,
  exec ``bindu serve --script <agent>``.
- **A1**: provide an ``image`` field; boxd creates the VM from that image
  and the image's CMD is the entry point. No source ship.

The host's role ends after the agent is healthy. A2A clients then talk
directly to the VM's public URL.
"""

from __future__ import annotations

import asyncio
import os
from pathlib import Path
from typing import Any, AsyncIterator, Literal

import httpx

from bindu.runtime.base import RuntimeHandle, RuntimeProvider, register_provider
from bindu.runtime.config import RuntimeConfig
from bindu.runtime.source_packager import build_tarball


def _make_compute(**kwargs: Any):
    """Indirection so tests can monkey-patch in a fake Compute."""
    from boxd.aio import Compute

    return Compute(**kwargs)


class BoxdRuntimeProvider(RuntimeProvider):
    async def _resolve_vm(
        self, compute: Any, name: str, config: RuntimeConfig
    ) -> Any:
        """Get or create the VM for this agent (idempotent by name)."""
        from boxd import BoxConfig, LifecycleConfig
        from boxd.errors import NotFoundError

        try:
            return await compute.box.get(name)
        except NotFoundError:
            pass

        box_config = BoxConfig(
            vcpu=config.vcpu,
            memory=config.memory,
            disk=config.disk,
            lifecycle=LifecycleConfig(
                auto_suspend_timeout=config.auto_suspend,
            ),
        )
        create_kwargs: dict[str, Any] = {
            "name": name,
            "config": box_config,
        }
        if config.image:
            create_kwargs["image"] = config.image
        return await compute.box.create(**create_kwargs)

    async def _ship_source(self, box: Any, source_dir: Path) -> None:
        """Tar+gzip ``source_dir``, upload, extract to ``/app`` in the VM."""
        blob = build_tarball(source_dir)
        await box.write_file(blob, "/tmp/source.tar.gz")
        await box.exec("mkdir", "-p", "/app")
        result = await box.exec(
            "tar", "xzf", "/tmp/source.tar.gz", "-C", "/app"
        )
        if getattr(result, "exit_code", 0) != 0:
            stderr = getattr(result, "stderr", "")
            raise RuntimeError(f"failed to extract source in VM: {stderr}")

    async def _install_deps(
        self,
        box: Any,
        has_pyproject: bool,
        has_requirements: bool,
        bindu_version: str | None = None,
    ) -> None:
        """Install bindu + the user's deps inside the VM (in /app)."""
        bindu_pkg = f"bindu=={bindu_version}" if bindu_version else "bindu"
        commands: list[tuple[str, ...]] = [("pip", "install", bindu_pkg)]
        if has_requirements:
            commands.append(("pip", "install", "-r", "/app/requirements.txt"))
        if has_pyproject:
            commands.append(("pip", "install", "-e", "."))
        for cmd in commands:
            result = await box.exec(*cmd)
            if getattr(result, "exit_code", 0) != 0:
                stderr = getattr(result, "stderr", "")
                raise RuntimeError(
                    f"command {cmd} failed in VM: {stderr}"
                )

    async def _start_agent(
        self,
        box: Any,
        script: str,
        env: dict[str, str] | None = None,
        public_url: str | None = None,
    ) -> None:
        """Exec ``bindu serve --script /app/<script>`` inside the VM."""
        merged_env = dict(env or {})
        if public_url:
            merged_env["BINDU_PUBLIC_URL"] = public_url

        # nohup + & via sh -c so the exec call returns once the agent is
        # forked. Output captured to a fixed log path; we pipe it via
        # box.stream_logs() later.
        cmd_str = (
            f"nohup bindu serve --script /app/{script} "
            f"> /var/log/bindu-agent.log 2>&1 &"
        )
        result = await box.exec("sh", "-c", cmd_str, env=merged_env)
        if getattr(result, "exit_code", 0) != 0:
            stderr = getattr(result, "stderr", "")
            raise RuntimeError(f"failed to start agent: {stderr}")

    async def _wait_healthy(self, url: str, timeout: float = 60.0) -> None:
        """Poll ``{url}/health`` until 200 or timeout."""
        deadline = asyncio.get_event_loop().time() + timeout
        async with httpx.AsyncClient(timeout=5.0) as client:
            while asyncio.get_event_loop().time() < deadline:
                try:
                    resp = await client.get(f"{url}/health")
                    if resp.status_code == 200:
                        return
                except httpx.HTTPError:
                    pass
                await asyncio.sleep(1.0)
        raise TimeoutError(
            f"agent at {url} did not become healthy within {timeout}s"
        )

    @staticmethod
    def _detect_script_name(source_dir: Path) -> str:
        """Pick the agent's entry script.

        Prefers a top-level ``.py`` file that calls ``bindufy(``. Falls back
        to the first ``.py`` file in alphabetical order.
        """
        candidates = sorted(source_dir.glob("*.py"))
        for c in candidates:
            try:
                if "bindufy(" in c.read_text(errors="ignore"):
                    return c.name
            except OSError:
                continue
        if candidates:
            return candidates[0].name
        raise RuntimeError(
            f"no .py file found in {source_dir} to use as agent entry point"
        )

    async def deploy(
        self,
        agent_name: str,
        source_dir: Path | None,
        config: RuntimeConfig,
        env: dict[str, str] | None = None,
    ) -> RuntimeHandle:
        if not (os.environ.get("BOXD_API_KEY") or os.environ.get("BOXD_TOKEN")):
            raise RuntimeError(
                "BOXD_API_KEY or BOXD_TOKEN must be set in the host environment"
            )

        async with _make_compute() as compute:
            box = await self._resolve_vm(compute, agent_name, config)
            public_url = box.url or f"https://{agent_name}.boxd.sh"

            if config.image is None:
                if source_dir is None:
                    raise RuntimeError(
                        "source_dir is required when config.image is not set"
                    )
                await self._ship_source(box, source_dir)
                has_pyproject = (source_dir / "pyproject.toml").exists()
                has_requirements = (source_dir / "requirements.txt").exists()
                await self._install_deps(
                    box,
                    has_pyproject=has_pyproject,
                    has_requirements=has_requirements,
                    bindu_version=config.bindu_version,
                )
                script = self._detect_script_name(source_dir)
                merged_env = {**config.env, **(env or {})}
                await self._start_agent(
                    box,
                    script=script,
                    env=merged_env,
                    public_url=public_url,
                )
            # else: A1 — image's CMD already starts the agent.

            await self._wait_healthy(public_url, timeout=60.0)

            return RuntimeHandle(
                name=agent_name,
                url=public_url,
                provider="boxd",
                metadata={
                    "vm_id": box.id,
                    "public_ip": box.public_ip,
                },
            )

    async def health(self, handle: RuntimeHandle) -> bool:
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                resp = await client.get(f"{handle.url}/health")
                return resp.status_code == 200
        except httpx.HTTPError:
            return False

    async def stream_logs(
        self, handle: RuntimeHandle, follow: bool = True
    ) -> AsyncIterator[bytes]:
        async with _make_compute() as compute:
            box = await compute.box.get(handle.name)
            async for chunk in box.stream_logs(follow=follow):
                yield chunk

    async def on_exit(
        self,
        handle: RuntimeHandle,
        mode: Literal["suspend", "destroy", "detach"],
    ) -> None:
        if mode == "detach":
            return
        async with _make_compute() as compute:
            try:
                box = await compute.box.get(handle.name)
            except Exception:
                return
            if mode == "destroy":
                await box.destroy()
            # mode == "suspend": rely on boxd's auto_suspend_timeout (set
            # at create time). Nothing to do here.


register_provider("boxd", BoxdRuntimeProvider)
