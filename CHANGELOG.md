# Changelog

## [0.2.0] - 2025-02-XX
### Added
- REST-сервер (FastAPI) с эндпоинтом POST /chat для интеграций (n8n и др.)
- Поддержка стриминга reasoning/final
- Harmony-парсер: теги, каналы LM Studio, строгий JSON и восстановление JSON
- Параметры генерации: temperature, top_p, max_tokens
- CLI `gptoss`: команды `chat` и `serve`
- Dockerfile для развёртывания сервиса
- Подробный `docs/USER_GUIDE.md` для нетехнических пользователей

### Changed
- Улучшена совместимость с OpenAI-совместимыми серверами (fallback без response_format)

### Fixed
- Корректная нормализация base_url и парсинг незакрытого </final>
