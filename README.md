# gpt-oss-client

Клиент для взаимодействия с моделью GPT-OSS 20B через:
- OpenAI-совместимые серверы (LM Studio, vLLM, OpenAI-совместимые гейтвеи)
- Ollama

Поддерживает разбор ответа на «рассуждения» и «финальный ответ» с помощью модуля `harmony`. Есть стриминг и принудительный JSON-режим со строгой валидацией.

## Установка

```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
pip install -e .
```

## Быстрый старт (CLI)

```bash
gptoss chat -m "Сумма 23 и 19?" --base-url http://localhost:1234/v1 --model gpt-oss-20b
```

Потоковый режим:
```bash
gptoss chat -m "Сумма 2 и 3? Обоснуй кратко." --stream
```

Параметры генерации и JSON-режим:
```bash
gptoss chat -m "Ответь JSON-ом" --temperature 0.2 --top-p 0.9 --max-tokens 256 --json-output --strict-json
```

Провайдеры:
- `--provider openai` (по умолчанию) с `--base-url http://localhost:1234/v1` (LM Studio) или `http://localhost:8000/v1` (vLLM)
- `--provider ollama` с `--base-url http://localhost:11434` и `--model gpt-oss-20b`

## Пример кода

```python
from gpt_oss_client.client import LLMClient
from gpt_oss_client.providers import Provider
from gpt_oss_client.schema import GenerationParams

client = LLMClient(provider=Provider.OPENAI_COMPAT, base_url="http://localhost:1234/v1", model="gpt-oss-20b")
result = client.chat("Сумма 23 и 19?", gen=GenerationParams(json_output=True, strict_json=True))
print(result.reasoning)
print(result.final_answer)
```

## Harmony
Модуль `harmony` парсит ответы с тегами `<thinking>…</thinking>` и `<final>…</final>` либо JSON с ключами `reasoning`/`final`.
Доступна строгая валидация JSON по схеме.
