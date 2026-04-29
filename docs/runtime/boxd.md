# Boxd runtime

`runtime={"provider": "boxd", ...}` runs your bindu agent inside a
[boxd](https://boxd.sh) microVM. The host process becomes a deploy tool;
the agent serves traffic from its own VM with a public HTTPS URL.

## Requirements

- A boxd account and API key (`BOXD_API_KEY=bxk_...` or `BOXD_TOKEN=...`
  in the host environment).
- For now, the boxd Python SDK installed locally (until PyPI release):
  `pip install -e ~/boxd/sdk/python`.

## Config reference

| Key | Type | Default | Meaning |
|---|---|---|---|
| `provider` | str | `"in-process"` | Set to `"boxd"` for VM mode. |
| `image` | str | `None` | If set, **A1 mode**: VM is created from this image; no source ship. See [custom-image.md](custom-image.md). |
| `vcpu` | int | `2` | vCPUs for the VM. |
| `memory` | str | `"4G"` | RAM. Accepts boxd size strings (`"512M"`, `"4G"`, ...). |
| `disk` | str | `"20G"` | Disk size. |
| `auto_suspend` | int | `60` | Seconds of inactivity before boxd auto-suspends the VM. Used for `on_exit: "suspend"`. |
| `on_exit` | str | `"suspend"` | Behavior on Ctrl-C: `"suspend"` (detach + auto-suspend), `"destroy"` (tear down VM), `"detach"` (leave running). |
| `bindu_version` | str | `None` | Pin the bindu version installed in the VM. Defaults to latest from PyPI. |
| `env` | dict | `{}` | Extra env vars merged into the VM agent's environment. |

## Lifecycle

1. **First run:** host packages your project source, ships it to a fresh
   VM, runs `pip install bindu` + your project's deps, exec's
   `bindu serve --script <your-script>`, polls `/health` until ready.
   Cold path: ~10–30 seconds depending on dep weight.
2. **Subsequent runs (same agent name):** host reuses the existing VM,
   updates source, restarts the agent. ~1–3 seconds.
3. **Ctrl-C with `on_exit: "suspend"` (default):** host detaches; VM
   auto-suspends after `auto_suspend` seconds of no traffic. Re-run to
   resume.

## Identity and secrets

- The agent's DID keys, x402 wallet, OAuth tokens are all generated and
  persisted **inside the VM**. `BOXD_API_KEY` stays on the host and is
  never shipped to the VM.
- User secrets (`OPENAI_API_KEY`, etc.) ship via:
  - a `.env` file in your project root (committed to the source tarball)
  - or the `env` field in the runtime config

## Source packaging

Your project root is auto-discovered by walking up from your entry script
looking for `pyproject.toml`, `setup.py`, `requirements.txt`, or `.git`.

**Always shipped:** `*.py`, `*.toml`, `*.txt`, `*.md`, `*.json`,
`*.yaml`, `.env`.
**Always excluded:** `__pycache__/`, `.git/`, `.venv/`, `venv/`,
`node_modules/`, `*.pyc`, `*.log`, `*.sqlite`, `*.db`, plus everything
in your `.gitignore` and `.binduignore`.
**Hard cap:** 50 MB compressed. Bigger sources fail fast with a pointer
to `.binduignore`.

## Dev DX

- `bindu logs <agent>` — stream the agent's VM logs to your terminal.
- `bindu shell <agent>` — open an interactive shell on the agent's VM
  (`/app` is the working directory).

## Troubleshooting

| Problem | Likely cause | Action |
|---|---|---|
| `BOXD_API_KEY or BOXD_TOKEN must be set` | No credentials in host env | `export BOXD_API_KEY=bxk_...` |
| `agent at <url> did not become healthy within 60s` | VM up but agent failed to start | `bindu logs <agent>` and inspect; common causes: missing dependency, syntax error in your script, port 3773 already in use inside VM |
| `pip install` failure | Dep not on PyPI, native build fails | Switch to A1 (custom image) and install the dep at image-build time |
| Source >50 MB | Large data files included | Add to `.binduignore` |
