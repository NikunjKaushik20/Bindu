# Document Analyzer

Hand it a PDF or DOCX as a base64-encoded `file` part in the A2A message, plus a prompt, and the agent extracts text and answers questions about the document. Agno + OpenRouter (`openai/gpt-oss-120b`). Uses `pypdf` for PDFs and `python-docx` for Word.

## Setup

```bash
export OPENROUTER_API_KEY=<get one at https://openrouter.ai/keys>
uv sync --extra agents
```

## Run

```bash
uv run examples/document-analyzer/document_analyzer.py
# http://localhost:3773
```

## Talk to it

The agent reads `parts[].kind == "file"` for the document and `parts[].kind == "text"` for the prompt. A2A bodies carry files as base64.

With `AUTH__ENABLED=false`, no document attached:

```bash
curl -sS http://localhost:3773/ \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"message/send","id":"00000000-0000-0000-0000-000000000004","params":{"message":{"role":"user","parts":[{"kind":"text","text":"What is this about?"}],"kind":"message","messageId":"00000000-0000-0000-0000-000000000001","contextId":"00000000-0000-0000-0000-000000000002","taskId":"00000000-0000-0000-0000-000000000003"},"configuration":{"acceptedOutputModes":["application/json"]}}}'
# → "No valid document found in the messages."
```

To actually analyse a document, append a `file` part with base64 bytes alongside the `text` part. The full file-handling shape lives in [`docs/FILE_HANDLING_&_UPLOADS.md`](../../docs/FILE_HANDLING_&_UPLOADS.md). With auth on, sign each body with the agent's DID key — see [`docs/AUTH.md`](../../docs/AUTH.md).
