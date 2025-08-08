from __future__ import annotations
import httpx
import json
from typing import Any, Dict, Iterable, List, Optional

from ..schema import Message, GenerationParams


class OllamaAdapter:
    def __init__(self, base_url: str, timeout: float = 60.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _build_payload(self, model: str, messages: List[Message], gen: Optional[GenerationParams], stream: bool) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "model": model,
            "messages": [m.model_dump() for m in messages],
            "stream": stream,
        }
        options: Dict[str, Any] = {}
        if gen:
            if gen.temperature is not None:
                options["temperature"] = gen.temperature
            if gen.top_p is not None:
                options["top_p"] = gen.top_p
            if gen.max_tokens is not None:
                options["num_predict"] = gen.max_tokens
            if gen.json_output:
                payload["format"] = "json"
        if options:
            payload["options"] = options
        return payload

    def chat(self, model: str, messages: List[Message], gen: Optional[GenerationParams] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/api/chat"
        payload = self._build_payload(model, messages, gen, stream=False)
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.post(url, json=payload)
            resp.raise_for_status()
            return resp.json()

    def stream_chat(self, model: str, messages: List[Message], gen: Optional[GenerationParams] = None) -> Iterable[str]:
        url = f"{self.base_url}/api/chat"
        payload = self._build_payload(model, messages, gen, stream=True)
        with httpx.Client(timeout=self.timeout) as client:
            with client.stream("POST", url, json=payload) as resp:
                resp.raise_for_status()
                for line in resp.iter_lines():
                    if not line:
                        continue
                    try:
                        obj = json.loads(line)
                        msg = obj.get("message") or {}
                        content = msg.get("content")
                        if content:
                            yield content
                        if obj.get("done") is True:
                            break
                    except Exception:
                        continue

    @staticmethod
    def extract_text(response_json: Dict[str, Any]) -> str:
        try:
            return response_json["message"]["content"]
        except Exception:
            return str(response_json)
