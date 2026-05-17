# Medical Agent

Educational medical-research assistant. Agno + OpenRouter (`openai/gpt-oss-120b`) + DuckDuckGo. Every reply includes a "this is not medical advice" disclaimer and points to a clinician for anything actionable — that's baked into the system prompt, not a separate guardrail.

## Setup

```bash
export OPENROUTER_API_KEY=<get one at https://openrouter.ai/keys>
uv sync --extra agents
```

## Run

```bash
uv run examples/medical_agent/medical_agent.py
# http://localhost:3773
```

## Talk to it

With `AUTH__ENABLED=false`:

```bash
curl -sS http://localhost:3773/ \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"message/send","id":"00000000-0000-0000-0000-000000000004","params":{"message":{"role":"user","parts":[{"kind":"text","text":"What are the symptoms of vitamin D deficiency?"}],"kind":"message","messageId":"00000000-0000-0000-0000-000000000001","contextId":"00000000-0000-0000-0000-000000000002","taskId":"00000000-0000-0000-0000-000000000003"},"configuration":{"acceptedOutputModes":["application/json"]}}}'
```

Then `tasks/get` for the response. With auth on, sign each body with the agent's DID key — see [`docs/AUTH.md`](../../docs/AUTH.md).

> Not a clinical tool. The disclaimer in the system prompt is the whole safety story — don't put this behind a patient-facing surface.
