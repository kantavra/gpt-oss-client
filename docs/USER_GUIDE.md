# Руководство пользователя: gpt-oss-client

Это простой инструмент, который помогает «общаться» с локально запущенной нейросетью GPT‑OSS 20B.
Вы можете использовать его:
- как консольную команду (CLI),
- как REST‑сервис (HTTP) для интеграций (например, n8n),
- через Docker (без установки Python).

Если вы «не технарь» — выбирайте способ «Через Docker» или «REST‑сервис + n8n». Мы описали всё максимально просто.

---

## Что понадобится

- Компьютер с macOS, Windows или Linux
- Одна из программ для запуска модели:
  - LM Studio (рекомендуется для начинающих)
  - либо Ollama (альтернатива)
- Установленная модель `gpt-oss-20b` внутри выбранной программы

> Подсказка: LM Studio имеет вшитый «локальный сервер», который понимает OpenAI‑подобный протокол. Это удобно для большинства интеграций.

---

## Вариант A. Быстрый старт через Docker (самый простой)

1) Установите Docker Desktop.
2) Откройте LM Studio, скачайте модель `gpt-oss-20b`, включите локальный сервер (обычно на `http://localhost:1234/v1`).
3) В терминале запустите:
```bash
docker build -t gpt-oss-client:latest .
docker run --rm -p 8001:8001 gpt-oss-client:latest
```
4) Проверьте сервис:
```bash
curl -X POST http://localhost:8001/chat \
  -H 'Content-Type: application/json' \
  -d '{
    "message": "Привет",
    "provider": "openai",
    "base_url": "http://host.docker.internal:1234/v1",
    "model": "gpt-oss-20b",
    "json_output": true,
    "strict_json": true
  }'
```
Ожидаемый ответ:
```json
{"reasoning":"...","final":"Привет! Чем могу помочь?"}
```

---

## Вариант B. Установка без Docker (CLI и REST)

1) Установите Python 3.9+.
2) Откройте терминал и выполните:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
pip install -e .
```
3) Проверьте CLI (LM Studio должен работать на `http://localhost:1234/v1`):
```bash
gptoss chat -m "Привет" --base-url http://localhost:1234/v1 --model gpt-oss-20b
```
4) Запустите REST‑сервис:
```bash
gptoss serve --host 0.0.0.0 --port 8001
```
5) Проверьте сервис (как выше через `curl`).

---

## Как подготовить LM Studio (рекомендуется)

1) Установите LM Studio с официального сайта и запустите.
2) Вкладка «Models» → найдите и скачайте `gpt-oss-20b`.
3) Включите локальный сервер (обычно «Enable Local Server») — адрес по умолчанию `http://localhost:1234/v1`.
4) Готово. Теперь gpt-oss-client сможет подключиться по `--base-url http://localhost:1234/v1` и `--model gpt-oss-20b`.

Плейсхолдеры изображений:
- lmstudio-download.png — скриншот окна LM Studio со списком моделей. Подпись: «Скачайте модель gpt‑oss‑20b».  [Описание: окно LM Studio, вкладка Models, в поиске введено gpt-oss-20b, видна кнопка Download]
- lmstudio-server.png — скрин локального сервера LM Studio. Подпись: «Включите Local Server на порту 1234».  [Описание: окно настроек LM Studio с активным переключателем Enable Local Server, указан адрес http://localhost:1234/v1]

---

## Как подготовить Ollama (альтернатива)

1) Установите Ollama с официального сайта и запустите службу.
2) Загрузите модель в Ollama (примерная команда может отличаться; уточняйте документацию модели):
```bash
ollama pull gpt-oss-20b
```
3) Запустите чат‑сервер Ollama (по умолчанию `http://localhost:11434`).
4) Используйте в CLI:
```bash
gptoss chat -m "Привет" --provider ollama --base-url http://localhost:11434 --model gpt-oss-20b
```

Плейсхолдер изображения:
- ollama-terminal.png — терминал с успешной загрузкой модели. Подпись: «Модель gpt‑oss‑20b доступна в Ollama».  [Описание: окно терминала, команда `ollama pull gpt-oss-20b` завершилась успешно]

---

## Использование CLI (для ручных запросов)

- Простой запрос:
```bash
gptoss chat -m "Сколько будет 2+3?" --base-url http://localhost:1234/v1 --model gpt-oss-20b
```
- Потоковый режим ( reasoning серым, финал жирным ):
```bash
gptoss chat -m "Реши задачу и кратко обоснуй" --stream
```
- Настройка «творчества» ответа:
```bash
gptoss chat -m "Сделай ответ детальнее" --temperature 0.7 --top-p 0.9 --max-tokens 512
```
- Жёсткий JSON для автоматизаций (рекомендуется для n8n):
```bash
gptoss chat -m "Верни reasoning и final в JSON" --json-output --strict-json
```

---

## REST‑сервис (для интеграций и n8n)

Запуск:
```bash
gptoss serve --host 0.0.0.0 --port 8001
```
Эндпоинт: `POST /chat`

Пример запроса:
```json
{
  "message": "Привет",
  "provider": "openai",
  "base_url": "http://localhost:1234/v1",
  "model": "gpt-oss-20b",
  "api_key": null,
  "temperature": 0.2,
  "top_p": 0.9,
  "max_tokens": 256,
  "json_output": true,
  "strict_json": true
}
```
Пример ответа:
```json
{"reasoning":"...","final":"Привет! Чем могу помочь?"}
```

> Важно: для автоматизаций всегда включайте `json_output: true` и по возможности `strict_json: true`, чтобы гарантированно получать одинаковую структуру.

---

## Интеграция с n8n (пошагово)

1) В n8n добавьте ноду «HTTP Request».
2) Выберите Method: `POST`.
3) Введите URL: `http://<HOST>:8001/chat` (если n8n и сервис на одном ПК, используйте `http://localhost:8001/chat`).
4) Content Type: `JSON`.
5) Укажите тело (Body):
```json
{
  "message": "Сумма 2 и 3?",
  "provider": "openai",
  "base_url": "http://host.docker.internal:1234/v1",
  "model": "gpt-oss-20b",
  "json_output": true,
  "strict_json": true
}
```
6) Запустите ноду. В ответе получите поля `reasoning` и `final`.
7) В следующей ноде (например, «Set» или «Function») используйте `final` как основной текст.

Плейсхолдеры изображений:
- n8n-http-node.png — нода HTTP Request с заполненным URL и телом. Подпись: «Настройки запроса в n8n».  [Описание: скрин интерфейса n8n, показаны поля Method=POST, URL, вкладка Body с JSON]
- n8n-result.png — вкладка Output ноды HTTP с JSON‑ответом. Подпись: «Получение reasoning и final».  [Описание: скрин интерфейса n8n, справа виден JSON с ключами reasoning и final]

---

## Частые вопросы (FAQ)

- «Почему ответ странный, как будто модель комментирует свои действия?»
  - Включите `json_output: true` и `strict_json: true`. Наш сервис постарается возвратить чистый JSON.
- «Получаю ошибку 400 при JSON‑режиме на LM Studio»
  - Мы автоматически повторяем запрос без специфичного флага `response_format`. Просто оставьте `json_output: true` — парсер на стороне клиента извлечёт корректный JSON из ответа.
- «Что указывать в base_url?»
  - LM Studio: `http://localhost:1234/v1`
  - vLLM (если используете): обычно `http://localhost:8000/v1`
  - Ollama: `http://localhost:11434` и провайдер `--provider ollama`
- «Нужно ли API‑key?»
  - Для локального LM Studio/Ollama — обычно нет.

---

## Диагностика

- Ничего не отвечает на `http://localhost:1234/v1` — проверьте, что LM Studio запущен и включён Local Server.
- Ответ приходит, но поля перепутаны — используйте JSON‑режим (`json_output: true`, `strict_json: true`).
- Фаервол/антивирус блокирует HTTP — временно разрешите соединения на используемом порту (8001 для сервиса, 1234/11434 для моделей).

Плейсхолдер изображения:
- troubleshooting-ports.png — схемка портов и стрелки запросов. Подпись: «Проверьте, что порты 8001/1234/11434 доступны».  [Описание: блок‑схема: n8n → gpt-oss-client:8001 → LM Studio:1234 или Ollama:11434]

---

## Глоссарий

- «Reasoning» — рассуждения модели; полезно для логирования и анализа.
- «Final» — итоговый ответ, который показывают пользователю.
- «JSON‑режим» — ответ строго в формате JSON; крайне рекомендуется для интеграций.

---

## Примечания по безопасности

- Все запросы обрабатываются локально, данные не отправляются в облако (если вы используете локальные движки LM Studio/Ollama).
- Не отправляйте в модель секреты и персональные данные без необходимости.

---

## Версии и обновления

- Текущая версия клиента указана в заголовке REST‑сервера.
- Обновляйте пакет командой `pip install -e .` после `git pull`, либо пересобирайте Docker‑образ.

---

© gpt-oss-client. Руководство можно копировать и адаптировать.
