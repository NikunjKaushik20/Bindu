# Summarizer

Turns any long blob of text into a 2–3 sentence summary. Agno + OpenRouter (`openai/gpt-oss-120b`), one skill (`text-summarization-skill`), no extra deps beyond the `agents` extra.

## Setup

```bash
export OPENROUTER_API_KEY=<get one at https://openrouter.ai/keys>
uv sync --extra agents
```

## Run

```bash
uv run examples/summarizer/summarizer_agent.py
# http://localhost:3773
```

## Talk to it

With `AUTH__ENABLED=false` (set in `examples/.env`):

```bash
curl -sS http://localhost:3773/ \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"message/send","id":"00000000-0000-0000-0000-000000000004","params":{"message":{"role":"user","parts":[{"kind":"text","text":"Summarize: <paste your long text here>"}],"kind":"message","messageId":"00000000-0000-0000-0000-000000000001","contextId":"00000000-0000-0000-0000-000000000002","taskId":"00000000-0000-0000-0000-000000000003"},"configuration":{"acceptedOutputModes":["application/json"]}}}'
```

Then `tasks/get` with the same `taskId` for the artifact. With auth on, sign each body with the agent's DID key — see [`docs/AUTH.md`](../../docs/AUTH.md).
