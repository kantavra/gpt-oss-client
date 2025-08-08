from __future__ import annotations
import json
import httpx
from typing import Any, Dict, Iterable, List, Optional

from ..schema import Message, GenerationParams


def _normalize_base_url(url: str) -> str:
    u = url.rstrip("/")
    if u.endswith("/v1"):
        u = u[:-3]
    return u


class OpenAICompatAdapter:
    def __init__(self, base_url: str, api_key: Optional[str] = None, timeout: float = 60.0):
        self.base_url = _normalize_base_url(base_url)
        self.api_key = api_key
        self.timeout = timeout

    def _build_payload(self, model: str, messages: List[Message], gen: Optional[GenerationParams], stream: bool) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "model": model,
            "messages": [m.model_dump() for m in messages],
            "stream": stream,
        }
        if gen:
            if gen.temperature is not None:
                payload["temperature"] = gen.temperature
            if gen.top_p is not None:
                payload["top_p"] = gen.top_p
            if gen.max_tokens is not None:
                payload["max_tokens"] = gen.max_tokens
            if gen.json_output:
                payload["response_format"] = {"type": "json_object"}
        return payload

    def chat(self, model: str, messages: List[Message], gen: Optional[GenerationParams] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/v1/chat/completions"
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        payload = self._build_payload(model, messages, gen, stream=False)
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.post(url, headers=headers, json=payload)
            if resp.status_code == 400 and "response_format" in payload:
                # повторяем без response_format для несовместимых серверов (например, LM Studio)
                payload.pop("response_format", None)
                resp = client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            return resp.json()

    def stream_chat(self, model: str, messages: List[Message], gen: Optional[GenerationParams] = None) -> Iterable[str]:
        url = f"{self.base_url}/v1/chat/completions"
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        payload = self._build_payload(model, messages, gen, stream=True)
        with httpx.Client(timeout=self.timeout) as client:
            def do_stream(p: Dict[str, Any]) -> Iterable[str]:
                with client.stream("POST", url, headers=headers, json=p) as resp:
                    resp.raise_for_status()
                    for line in resp.iter_lines():
                        if not line:
                            continue
                        try:
                            if line.startswith("data: "):
                                line = line[6:]
                            if line.strip() == "[DONE]":
                                break
                            obj = json.loads(line)
                            delta = obj.get("choices", [{}])[0].get("delta", {})
                            content = delta.get("content")
                            if content:
                                yield content
                        except Exception:
                            continue
            # первая попытка
            try:
                yield from do_stream(payload)
                return
            except httpx.HTTPStatusError as e:
                if e.response is not None and e.response.status_code == 400 and "response_format" in payload:
                    payload.pop("response_format", None)
                    yield from do_stream(payload)
                    return
                raise

    @staticmethod
    def extract_text(response_json: Dict[str, Any]) -> str:
        try:
            return response_json["choices"][0]["message"]["content"]
        except Exception:
            return str(response_json)
