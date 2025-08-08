# User Guide: gpt-oss-client

This tool lets you “talk” to a local GPT‑OSS 20B model. You can use it:
- as a command line tool (CLI),
- as a REST service (HTTP) for integrations (e.g., n8n),
- via Docker (no Python installation required).

If you are not technical, pick the Docker or REST + n8n option. Steps are kept simple.

---

## Requirements
- macOS / Windows / Linux
- One runtime to host the model:
  - LM Studio (recommended for beginners), or
  - Ollama (alternative)
- The `gpt-oss-20b` model downloaded in your chosen runtime

LM Studio includes a local server that speaks an OpenAI‑compatible API. This is very convenient.

---

## Option A. Quick start with Docker (easiest)
1) Install Docker Desktop.
2) Open LM Studio, download `gpt-oss-20b`, enable Local Server (usually `http://localhost:1234/v1`).
3) In a terminal:
```bash
docker build -t gpt-oss-client:latest .
docker run --rm -p 8001:8001 gpt-oss-client:latest
```
4) Test the service:
```bash
curl -X POST http://localhost:8001/chat \
  -H 'Content-Type: application/json' \
  -d '{
    "message": "Hello",
    "provider": "openai",
    "base_url": "http://host.docker.internal:1234/v1",
    "model": "gpt-oss-20b",
    "json_output": true,
    "strict_json": true
  }'
```
Expected response:
```json
{"reasoning":"...","final":"Hello! How can I help?"}
```

---

## Option B. Installation without Docker (CLI & REST)
1) Install Python 3.9+.
2) In a terminal:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
pip install -e .
```
3) Test CLI (LM Studio must run at `http://localhost:1234/v1`):
```bash
gptoss chat -m "Hello" --base-url http://localhost:1234/v1 --model gpt-oss-20b
```
4) Start REST service:
```bash
gptoss serve --host 0.0.0.0 --port 8001
```
5) Test with `curl` as above.

---

## Prepare LM Studio (recommended)
1) Install LM Studio and launch it.
2) In “Models”, search and download `gpt-oss-20b`.
3) Enable Local Server (default `http://localhost:1234/v1`).
4) Now `gpt-oss-client` can connect via `--base-url http://localhost:1234/v1` and `--model gpt-oss-20b`.

Image placeholders:
- lmstudio-download.png — LM Studio model list with a “Download” button for gpt‑oss‑20b.
- lmstudio-server.png — LM Studio settings with “Enable Local Server” toggled on.

---

## Prepare Ollama (alternative)
1) Install Ollama and start the service.
2) Pull a model (adjust the exact command per the model docs):
```bash
ollama pull gpt-oss-20b
```
3) Ollama runs at `http://localhost:11434` by default.
4) CLI usage:
```bash
gptoss chat -m "Hello" --provider ollama --base-url http://localhost:11434 --model gpt-oss-20b
```

Image placeholder:
- ollama-terminal.png — terminal showing successful `ollama pull gpt-oss-20b`.

---

## CLI usage
- Simple request:
```bash
gptoss chat -m "What is 2+3?" --base-url http://localhost:1234/v1 --model gpt-oss-20b
```
- Streaming (reasoning dim, final bold):
```bash
gptoss chat -m "Solve and explain briefly" --stream
```
- Tune the output “creativity”:
```bash
gptoss chat -m "Make it more detailed" --temperature 0.7 --top-p 0.9 --max-tokens 512
```
- Strict JSON for automations (recommended for n8n):
```bash
gptoss chat -m "Return reasoning and final as JSON" --json-output --strict-json
```

---

## REST service (for integrations & n8n)
Start:
```bash
gptoss serve --host 0.0.0.0 --port 8001
```
Endpoint: `POST /chat`

Request example:
```json
{
  "message": "Hello",
  "provider": "openai",
  "base_url": "http://localhost:1234/v1",
  "model": "gpt-oss-20b",
  "json_output": true,
  "strict_json": true
}
```
Response example:
```json
{"reasoning":"...","final":"Hello! How can I help?"}
```

Important: for automations always enable `json_output: true` and preferably `strict_json: true` to guarantee a consistent structure.

---

## n8n Integration (step by step)
1) Add an “HTTP Request” node.
2) Method: `POST`.
3) URL: `http://<HOST>:8001/chat` (if n8n and the service run on the same machine, use `http://localhost:8001/chat`).
4) Content Type: `JSON`.
5) Body:
```json
{
  "message": "What is 2+3?",
  "provider": "openai",
  "base_url": "http://host.docker.internal:1234/v1",
  "model": "gpt-oss-20b",
  "json_output": true,
  "strict_json": true
}
```
6) Run the node. You will get `reasoning` and `final` in the response.
7) In the next node use `final` as the primary output.

Image placeholders:
- n8n-http-node.png — HTTP Request node config (Method=POST, URL, Body JSON).
- n8n-result.png — Node Output with JSON containing `reasoning` and `final`.

---

## FAQ
- “Why does the reply look like the model is explaining itself?”
  - Enable `json_output: true` and `strict_json: true`. The service will return clean JSON.
- “I get 400 with JSON mode on LM Studio”
  - We automatically retry without `response_format`. Keep `json_output: true` — our client will parse clean JSON from the response.
- “What should I put into base_url?”
  - LM Studio: `http://localhost:1234/v1`
  - vLLM: `http://localhost:8000/v1` (typical)
  - Ollama: `http://localhost:11434` with provider `ollama`
- “Do I need an API key?”
  - For local LM Studio/Ollama — usually no.

---

## Troubleshooting
- Nothing responds at `http://localhost:1234/v1` — ensure LM Studio is running and Local Server is enabled.
- Output looks mixed — switch to JSON mode (`json_output: true`, `strict_json: true`).
- Firewall blocks HTTP — allow ports you use (8001 for our service, 1234/11434 for model backends).

Image placeholder:
- troubleshooting-ports.png — simple diagram: n8n → gpt-oss-client:8001 → LM Studio:1234 or Ollama:11434.

---

## Glossary
- “Reasoning” — model’s chain-of-thought (for logging/analysis).
- “Final” — the final answer to show to end users.
- “JSON mode” — strict JSON output; strongly recommended for automations.

---

## Versions & updates
- Current service version is visible in the REST title.
- Update with `pip install -e .` after pulling latest changes, or rebuild the Docker image.

---

© gpt-oss-client. Feel free to copy and adapt this guide.
