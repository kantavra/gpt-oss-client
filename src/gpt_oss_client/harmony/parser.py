import json
import re
from typing import Optional, Tuple, Union
from pydantic import BaseModel, ValidationError


_REASONING_TAG_RE = re.compile(r"<thinking>([\s\S]*?)</thinking>", re.IGNORECASE)
_FINAL_TAG_RE = re.compile(r"<final>([\s\S]*?)</final>", re.IGNORECASE)
_FINAL_OPEN_RE = re.compile(r"<final>", re.IGNORECASE)
_THINKING_OPEN_RE = re.compile(r"<thinking>", re.IGNORECASE)
_THINKING_CLOSE_RE = re.compile(r"</thinking>", re.IGNORECASE)

# LM Studio / Harmony-подобные маркеры
_CHANNEL_BLOCK_RE = re.compile(r"<\|channel\|>[\s\S]*?<\|message\|>([\s\S]+)$", re.IGNORECASE)


def build_system_instruction() -> str:
    return (
        "Вы ассистент. Всегда отвечайте в структурированном формате.\n"
        "Сначала выводите рассуждения в теге <thinking>…</thinking>, затем финальный ответ в теге <final>…</final>.\n"
        "Если необходимо вернуть JSON, используйте: {\"reasoning\": string, \"final\": string}.\n"
        "Никогда не смешивайте финальный ответ с рассуждениями."
    )


def build_json_system_instruction() -> str:
    return (
        "Вы ассистент. Отвечайте строго JSON-объектом в одной строке без пояснений и префиксов.\n"
        "Структура: {\"reasoning\": string, \"final\": string}.\n"
        "Никакого текста вне JSON. Никаких XML-тегов."
    )


class HarmonyJSON(BaseModel):
    reasoning: Optional[str] = None
    final: Union[str, int, float]


def _extract_by_tags(text: str) -> Tuple[Optional[str], Optional[str]]:
    thinking_match = _REASONING_TAG_RE.search(text or "")
    final_match = _FINAL_TAG_RE.search(text or "")
    reasoning = thinking_match.group(1).strip() if thinking_match else None
    final = final_match.group(1).strip() if final_match else None
    return reasoning, final


def _extract_unclosed_final(text: str) -> Tuple[Optional[str], Optional[str]]:
    if not text:
        return None, None
    # Найти thinking блок даже если final не закрыт
    think_open = _THINKING_OPEN_RE.search(text)
    think_close = _THINKING_CLOSE_RE.search(text)
    final_open = _FINAL_OPEN_RE.search(text)
    if final_open and not _FINAL_TAG_RE.search(text):
        # Есть <final>, но нет </final>
        reasoning: Optional[str] = None
        if think_open and think_close and think_close.start() > think_open.end():
            reasoning = text[think_open.end():think_close.start()].strip()
        else:
            # если нет полноценного thinking, возьмём всё до <final>
            reasoning = text[:final_open.start()].strip() or None
        final = text[final_open.end():].strip()
        # Уберём возможные хвостовые теги или маркеры каналов
        final = re.sub(r"<[^>]+>$", "", final).strip()
        return reasoning, (final or None)
    return None, None


def _extract_from_json(text: str) -> Tuple[Optional[str], Optional[str]]:
    if not text:
        return None, None
    try:
        data = json.loads(text)
        reasoning = data.get("reasoning") or data.get("chain_of_thought") or data.get("thinking")
        final = data.get("final") or data.get("answer") or data.get("output")
        if isinstance(reasoning, str):
            reasoning = reasoning.strip()
        else:
            reasoning = None
        if isinstance(final, (str, int, float)):
            final = str(final).strip()
        else:
            final = None
        return reasoning, final
    except Exception:
        return None, None


def _extract_from_lmstudio_channels(text: str) -> Tuple[Optional[str], Optional[str]]:
    if not text:
        return None, None
    m = _CHANNEL_BLOCK_RE.search(text)
    if not m:
        return None, None
    json_part = m.group(1).strip()
    json_obj: Optional[dict] = None
    start = json_part.find('{')
    end = json_part.rfind('}')
    if start != -1 and end != -1 and end > start:
        candidate = json_part[start:end + 1]
        try:
            json_obj = json.loads(candidate)
        except Exception:
            json_obj = None
    pre_text = text[: m.start()].strip()
    reasoning = pre_text or None
    if json_obj is not None:
        final_value = (
            json_obj.get("final")
            or json_obj.get("answer")
            or json_obj.get("output")
            or None
        )
        if isinstance(final_value, (str, int, float)):
            final = str(final_value).strip()
        else:
            final = None
        return reasoning, final
    return reasoning, None


def _extract_trailing_json(text: str) -> Tuple[Optional[str], Optional[str]]:
    if not text:
        return None, None
    start = text.rfind('{')
    end = text.rfind('}')
    if start == -1 or end == -1 or end <= start:
        return None, None
    candidate = text[start:end + 1]
    try:
        data = json.loads(candidate)
        obj = HarmonyJSON.model_validate(data)
        reasoning_prefix = text[:start].strip() or None
        final = str(obj.final).strip()
        reasoning = obj.reasoning.strip() if obj.reasoning else reasoning_prefix
        return reasoning, final
    except (ValidationError, Exception):
        return None, None


def parse_json_strict(text: str) -> Tuple[Optional[str], Optional[str]]:
    try:
        data = json.loads(text)
        obj = HarmonyJSON.model_validate(data)
        return (obj.reasoning.strip() if obj.reasoning else None, str(obj.final).strip())
    except (ValidationError, Exception):
        return _extract_trailing_json(text)


def parse_structured_output(text: str) -> Tuple[Optional[str], Optional[str]]:
    reasoning, final = _extract_by_tags(text)
    if reasoning or final:
        return reasoning, final
    reasoning, final = _extract_unclosed_final(text)
    if reasoning or final:
        return reasoning, final
    reasoning, final = _extract_from_lmstudio_channels(text)
    if reasoning or final:
        return reasoning, final
    reasoning, final = _extract_from_json(text)
    if reasoning or final:
        return reasoning, final
    return None, (text or None)
