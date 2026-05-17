# Beginner

Twelve single-file agents you can run end-to-end in under two minutes each. Most are pure illustration — wrap a handler, hand it to `bindufy()`, see the agent come online with a DID, an agent card, and an A2A endpoint.

Pick whichever one matches the framework you already use; the wiring around it is identical.

## Setup

```bash
export OPENROUTER_API_KEY=<get one at https://openrouter.ai/keys>
uv sync --extra agents
```

By default `AUTH__ENABLED=true` and the agent demands OAuth + a DID-signed body on every request. To send unsigned curls while you're learning, set `AUTH__ENABLED=false` in `examples/.env`. The signed-request flow is in [`docs/AUTH.md`](../../docs/AUTH.md).

## The agents

| File | What it does | Extra requirement |
| --- | --- | --- |
| `echo_simple_agent.py` | Returns whatever you send it. No LLM. Good first sanity check. | — |
| `beginner_zero_config_agent.py` | Minimal agent with web-search via DuckDuckGo. | — |
| `agno_simple_example.py` | Smallest possible Agno wrap. | — |
| `agno_example.py` | Agno research assistant with DuckDuckGo. | — |
| `faq_agent.py` | Answers questions from a hand-written FAQ table. | — |
| `motivational_agent.py` | One-line pep talks. | — |
| `ag2_simple_example.py` | AG2 (formerly AutoGen) wrapped with `bindufy()`. | — |
| `dspy_agent.py` | DSPy structured prompting via OpenAI. | `OPENAI_API_KEY` |
| `minimax_example.py` | OpenAI-compatible client pointed at MiniMax. | `MINIMAX_API_KEY` |
| `agno_notion_agent.py` | Reads from a Notion workspace. | `NOTION_API_KEY` + `NOTION_DATABASE_ID` |
| `agno_paywall_example.py` | Same as `agno_example` but gated by x402. Returns HTTP 402 until paid. | x402 wallet (Base Sepolia USDC) |
| `echo_agent_behind_paywall.py` | Echo gated by x402. | x402 wallet |

## Run one

```bash
uv run examples/beginner/echo_simple_agent.py
# bound to http://localhost:3773
```

`BINDU_PORT=4000` overrides the port. The agent card is at `/.well-known/agent.json`, the DID document at `/.well-known/did.json`.

## Talk to it

With `AUTH__ENABLED=false`:

```bash
curl -sS http://localhost:3773/ \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"message/send","id":"1","params":{"message":{"role":"user","parts":[{"kind":"text","text":"Hello!"}],"kind":"message","messageId":"m1","contextId":"c1","taskId":"t1"}}}'
```

The response is a `Task` object. Poll `tasks/get` with the same `taskId` for the final artifact.

With auth on, every request needs a Hydra OAuth token in `Authorization: Bearer …` plus three `X-DID-*` headers signing the body. `examples/hermes_agent/call.py` is a working reference client for that flow.

## Build your own from here

```python
from bindu.penguin.bindufy import bindufy

def handler(messages):
    return f"You said: {messages[-1]['content']}"

bindufy(
    {
        "author": "you@example.com",
        "name": "my_agent",
        "description": "what my agent does",
        "deployment": {"url": "http://localhost:3773", "expose": True},
        "skills": [],
    },
    handler,
)
```
