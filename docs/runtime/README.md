# Runtime providers

A bindu agent's *runtime* is where its Python process actually executes.
The default runtime is in-process: `python my_agent.py` runs the agent
in your own terminal. A `RuntimeProvider` lets you swap that — the
canonical example is `BoxdRuntimeProvider`, which runs the agent inside
a [boxd](https://boxd.sh) microVM with its own public URL, DID, and
HTTPS domain.

## When to use

- **Default (in-process):** local development, anywhere you control the
  process and the network.
- **Boxd runtime:** when you want the agent to be a *real* microservice —
  isolated from your laptop, addressable on a public URL, with its own
  identity and persistent state. Required for hosted multi-tenant agents.

## Quickstart

```python
from bindu.penguin.bindufy import bindufy


def handler(messages):
    return [{"role": "assistant", "content": messages[-1]["content"]}]


config = {
    "name": "my-agent",
    "description": "echo agent",
    "deployment": {"url": "http://localhost:3773"},
}

bindufy(
    config,
    handler,
    runtime={"provider": "boxd"},
)
```

Run it: `BOXD_API_KEY=bxk_... python my_agent.py`. Output:

```
✓ my-agent serving at https://my-agent.boxd.sh

[my-agent] INFO: Started server process [12]
[my-agent] INFO: Application startup complete.
```

A2A clients can now reach the agent at `https://my-agent.boxd.sh`. Ctrl-C
detaches; the VM auto-suspends after 60s of inactivity. Re-running the
script resumes the same VM and updates the source.

## See also

- [boxd.md](boxd.md) — full boxd-runtime config reference.
- [custom-image.md](custom-image.md) — A1 mode (user-built Docker images).
- [`docs/superpowers/specs/2026-04-29-bindu-runtime-design.md`](../superpowers/specs/2026-04-29-bindu-runtime-design.md) — design rationale.

## Limitations (v1)

- One runtime provider ships in-tree: `boxd`. The abstraction supports
  others (e2b, modal, fly.io) but no providers besides boxd are bundled.
- No live source-watch / auto-redeploy. Editing your agent script
  requires re-running the entry point.
- The boxd Python SDK is not yet on PyPI, so until it ships, both bindu
  and boxd must be installed editably from local checkouts.
