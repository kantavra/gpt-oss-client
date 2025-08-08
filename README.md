# gpt-oss-client

Multilingual README: English below · Русская версия ниже

---

## English

Client for interacting with GPT‑OSS 20B via:
- OpenAI‑compatible servers (LM Studio, vLLM, OpenAI‑compatible gateways)
- Ollama

Features:
- Harmony parsing: separates “reasoning” and “final answer”
- Streaming (separate channels for reasoning/final)
- Forced JSON mode with strict validation
- FastAPI REST server for integrations (e.g., n8n)
- Docker image for easy deployment

### Installation
```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
pip install -e .
```

### Quick Start (CLI)
```bash
gptoss chat -m "What is 23+19?" --base-url http://localhost:1234/v1 --model gpt-oss-20b
```
Streaming:
```bash
gptoss chat -m "Solve and explain briefly" --stream
```
Generation params and JSON mode:
```bash
gptoss chat -m "Return reasoning and final as JSON" \
  --temperature 0.2 --top-p 0.9 --max-tokens 256 --json-output --strict-json
```
Providers:
- `--provider openai` (default) with `--base-url http://localhost:1234/v1` (LM Studio) or `http://localhost:8000/v1` (vLLM)
- `--provider ollama` with `--base-url http://localhost:11434` and `--model gpt-oss-20b`

### REST Server
```bash
gptoss serve --host 0.0.0.0 --port 8001
```
POST `/chat`, request body example:
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
Response:
```json
{"reasoning":"...","final":"Hello! How can I help?"}
```

### Docker
```bash
docker build -t gpt-oss-client:latest .
docker run --rm -p 8001:8001 gpt-oss-client:latest
```

### Docs
- User Guide (EN): docs/USER_GUIDE_EN.md
- Руководство пользователя (RU): docs/USER_GUIDE.md

---

## Русский

Клиент для взаимодействия с GPT‑OSS 20B через:
- OpenAI‑совместимые серверы (LM Studio, vLLM, OpenAI‑совместимые гейтвеи)
- Ollama

Возможности:
- Harmony‑парсинг: разделение «рассуждений» и «финального ответа»
- Стриминг (отдельные каналы reasoning/final)
- Принудительный JSON‑режим с строгой валидацией
- REST‑сервер на FastAPI для интеграций (например, n8n)
- Docker‑образ для развёртывания

### Установка
```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
pip install -e .
```

### Быстрый старт (CLI)
```bash
gptoss chat -m "Сумма 23 и 19?" --base-url http://localhost:1234/v1 --model gpt-oss-20b
```
Стриминг:
```bash
gptoss chat -m "Реши задачу и обоснуй кратко" --stream
```
Параметры генерации и JSON‑режим:
```bash
gptoss chat -m "Верни reasoning и final в JSON" \
  --temperature 0.2 --top-p 0.9 --max-tokens 256 --json-output --strict-json
```
Провайдеры:
- `--provider openai` (по умолчанию) с `--base-url http://localhost:1234/v1` (LM Studio) или `http://localhost:8000/v1` (vLLM)
- `--provider ollama` с `--base-url http://localhost:11434` и `--model gpt-oss-20b`

### REST‑сервер
```bash
gptoss serve --host 0.0.0.0 --port 8001
```
POST `/chat`, пример тела запроса:
```json
{
  "message": "Привет",
  "provider": "openai",
  "base_url": "http://localhost:1234/v1",
  "model": "gpt-oss-20b",
  "json_output": true,
  "strict_json": true
}
```
Ответ:
```json
{"reasoning":"...","final":"Привет! Чем могу помочь?"}
```

### Docker
```bash
docker build -t gpt-oss-client:latest .
docker run --rm -p 8001:8001 gpt-oss-client:latest
```

### Документация
- User Guide (EN): docs/USER_GUIDE_EN.md
- Руководство пользователя (RU): docs/USER_GUIDE.md

### Пример кода
```python
from gpt_oss_client.client import LLMClient
from gpt_oss_client.providers import Provider
from gpt_oss_client.schema import GenerationParams

client = LLMClient(provider=Provider.OPENAI_COMPAT, base_url="http://localhost:1234/v1", model="gpt-oss-20b")
result = client.chat("Сумма 23 и 19?", gen=GenerationParams(json_output=True, strict_json=True))
print(result.reasoning)
print(result.final_answer)
```
