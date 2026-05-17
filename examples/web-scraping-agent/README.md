# Web Scraping

Hand it a URL and an extraction prompt, get structured JSON back. Agno orchestrates two tools: ScrapeGraph for the actual fetch + parse, and Mem0 so the agent remembers which URLs it already scraped (and your extraction preferences) across runs.

## Setup

```bash
export OPENROUTER_API_KEY=<get one at https://openrouter.ai/keys>
export SCRAPEGRAPH_API_KEY=<get one at https://scrapegraphai.com>
export MEM0_API_KEY=<get one at https://app.mem0.ai/dashboard/api-keys>
uv sync --extra agents
uv pip install scrapegraph-py mem0ai
```

`scrapegraph-py` and `mem0ai` aren't in the `agents` extra yet — install them explicitly. Without `MEM0_API_KEY` the agent crashes at boot; without `SCRAPEGRAPH_API_KEY` it crashes the moment you ask it to scrape.

## Run

```bash
uv run examples/web-scraping-agent/web_scraping_agent.py
# http://localhost:3773
```

## Talk to it

With `AUTH__ENABLED=false`:

```bash
curl -sS http://localhost:3773/ \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"message/send","id":"00000000-0000-0000-0000-000000000004","params":{"message":{"role":"user","parts":[{"kind":"text","text":"Scrape https://example.com — extract the page title and first paragraph."}],"kind":"message","messageId":"00000000-0000-0000-0000-000000000001","contextId":"00000000-0000-0000-0000-000000000002","taskId":"00000000-0000-0000-0000-000000000003"},"configuration":{"acceptedOutputModes":["application/json"]}}}'
```

Then `tasks/get` for the JSON. Re-running with the same URL hits Mem0 first — the agent will say "already scraped this" instead of re-fetching.

With auth on, sign each body with the agent's DID key — see [`docs/AUTH.md`](../../docs/AUTH.md).
