# Gateway Test Fleet

Five tiny agents on local ports + a 13-case test matrix. Used as the reproducible setup that exercises the [Bindu Gateway](../../docs/GATEWAY.md) end-to-end. If you're new to bindu start at [`docs/GATEWAY.md`](../../docs/GATEWAY.md) — this folder is what its walkthrough uses under the hood.

## Setup

```bash
export OPENROUTER_API_KEY=<get one at https://openrouter.ai/keys>
uv sync --extra agents
```

Each agent is ~60 lines of Python that wires `openai/gpt-4o-mini` to a few lines of instructions.

## Ports

| Agent | Port |
| --- | --- |
| joke_agent | 3773 |
| math_agent | 3775 |
| poet_agent | 3776 |
| research_agent | 3777 |
| faq_agent | 3778 |

Gateway sits at 3774 (when running).

## Start / stop the fleet

```bash
./examples/gateway_test_fleet/start_fleet.sh   # boots all five in the background
./examples/gateway_test_fleet/stop_fleet.sh    # stops them cleanly
```

Logs land in `logs/<agent>.log`. PIDs in `pids/<agent>.pid` (so `stop_fleet.sh` can find them).

## Run the test matrix

```bash
./examples/gateway_test_fleet/run_matrix.sh              # all 13 cases
./examples/gateway_test_fleet/run_matrix.sh Q_MULTIHOP   # one case by id
```

Case definitions live in `matrix.json`. SSE logs per case land in `logs/cases/`.

## Talk to one agent directly

With `AUTH__ENABLED=false`, hit joke_agent on its port:

```bash
curl -sS http://localhost:3773/ \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"message/send","id":"1","params":{"message":{"role":"user","parts":[{"kind":"text","text":"tell me a joke about cats"}],"kind":"message","messageId":"m1","contextId":"c1","taskId":"t1"}}}'
```

With auth on, sign each body with the agent's DID key — see [`docs/AUTH.md`](../../docs/AUTH.md). The Hydra smoke test in `hydra_smoke_test.sh` is a good place to start if auth is misbehaving.
