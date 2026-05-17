# Cerina CBT Supervisor

A real LangGraph workflow wrapped as one bindu agent. Internally three nodes — Drafter, Safety Guardian, Clinical Critic — collaborate under a Supervisor to produce a CBT (cognitive behavioural therapy) exercise on a user-supplied concern. The Supervisor loops until the Safety Guardian and Clinical Critic both pass.

Different from `agent_swarm` in that the orchestration is a real LangGraph `StateGraph` with merge functions on the shared state, not an ad-hoc Python pipeline.

## Setup

```bash
export OPENROUTER_API_KEY=<get one at https://openrouter.ai/keys>
uv sync --extra agents
```

LangGraph + LangChain-OpenAI come in via the `agents` extra. The agent uses OpenRouter via `langchain_openai.ChatOpenAI(base_url=...)`.

## Run

```bash
uv run examples/cerina_bindu/cbt/supervisor_cbt.py
# http://localhost:3773
```

## Talk to it

With `AUTH__ENABLED=false`:

```bash
curl -sS http://localhost:3773/ \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"message/send","id":"1","params":{"message":{"role":"user","parts":[{"kind":"text","text":"Generate a short CBT exercise for managing test anxiety."}],"kind":"message","messageId":"m1","contextId":"c1","taskId":"t1"}}}'
```

The Drafter → SafetyGuardian → ClinicalCritic → Supervisor loop takes 60–180s. Poll `tasks/get` with a generous timeout — by default the harness times out at 60s and the workflow is still in `working` state. Use ≥180s.

## What's in here

| File | Role |
| --- | --- |
| `supervisor_cbt.py` | bindu wrapper — entry point. |
| `langgraph_integration.py` | Builds the LangGraph workflow + OpenRouter LLM client. |
| `agents.py` | Drafter, Safety Guardian, Clinical Critic, Supervisor implementations. |
| `state.py` | Shared `ProtocolState` TypedDict + merge functions. |
| `state_mapper.py` | Translates between bindu artifacts and LangGraph state. |
| `workflow.py` | `StateGraph` topology and routing. |
| `database.py` | Optional SQLAlchemy persistence for sessions. |

> Educational example. CBT generated here is not clinical advice — same caveat as `medical_agent`.

With auth on, sign each body with the agent's DID key — see [`docs/AUTH.md`](../../../docs/AUTH.md).
