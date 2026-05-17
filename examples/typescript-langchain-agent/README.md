# TypeScript LangChain Agent

LangChain.js research agent, bindufied via the TypeScript SDK. `ChatOpenAI` pointed at OpenRouter — same key as the rest of the example fleet.

## Setup

```bash
export OPENROUTER_API_KEY=<get one at https://openrouter.ai/keys>
cd examples/typescript-langchain-agent
npm install
```

## Run

```bash
npx tsx index.ts
# http://localhost:3773
```

The TS SDK spawns `uv run bindu serve --grpc --grpc-port 4774` as a child. If 4774 is held by the gateway dev server, change `coreAddress` in the bindufy config to a free port.

## Talk to it

With `AUTH__ENABLED=false`:

```bash
curl -sS http://localhost:3773/ \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"message/send","id":"00000000-0000-0000-0000-000000000004","params":{"message":{"role":"user","parts":[{"kind":"text","text":"Reply with one plain-text sentence: capital of Japan?"}],"kind":"message","messageId":"00000000-0000-0000-0000-000000000001","contextId":"00000000-0000-0000-0000-000000000002","taskId":"00000000-0000-0000-0000-000000000003"},"configuration":{"acceptedOutputModes":["application/json"]}}}'
```

With auth on, sign each body with the agent's DID key — see [`docs/AUTH.md`](../../docs/AUTH.md).
