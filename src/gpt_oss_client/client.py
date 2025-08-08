from __future__ import annotations
from typing import Optional, List, Iterable, Tuple

from .providers import Provider
from .schema import ChatResult, Message, GenerationParams
from .harmony import build_system_instruction, build_json_system_instruction, parse_structured_output, parse_json_strict
from .adapters.openai_compat import OpenAICompatAdapter
from .adapters.ollama import OllamaAdapter


class LLMClient:
    def __init__(
        self,
        provider: Provider,
        base_url: str,
        model: str,
        api_key: Optional[str] = None,
        request_timeout: float = 90.0,
        default_gen: Optional[GenerationParams] = None,
    ) -> None:
        self.provider = provider
        self.base_url = base_url
        self.model = model
        self.api_key = api_key
        self.request_timeout = request_timeout
        self.default_gen = default_gen or GenerationParams()
        if provider == Provider.OPENAI_COMPAT:
            self._adapter = OpenAICompatAdapter(base_url=base_url, api_key=api_key, timeout=request_timeout)
        elif provider == Provider.OLLAMA:
            self._adapter = OllamaAdapter(base_url=base_url, timeout=request_timeout)
        else:
            raise ValueError(f"Unsupported provider: {provider}")

    def _merge_gen(self, gen: Optional[GenerationParams]) -> GenerationParams:
        if gen is None:
            return self.default_gen
        merged = self.default_gen.model_copy(deep=True)
        for field in ["temperature", "top_p", "max_tokens", "json_output", "strict_json"]:
            value = getattr(gen, field)
            if value is not None and field not in ("json_output", "strict_json"):
                setattr(merged, field, value)
            if field in ("json_output", "strict_json") and value is True:
                setattr(merged, field, True)
        return merged

    def chat(self, user_prompt: str, system_prompt: Optional[str] = None, gen: Optional[GenerationParams] = None) -> ChatResult:
        gen_params = self._merge_gen(gen)
        system = system_prompt or (build_json_system_instruction() if gen_params.json_output else build_system_instruction())
        messages: List[Message] = [
            Message(role="system", content=system),
            Message(role="user", content=user_prompt),
        ]
        response_json = self._adapter.chat(model=self.model, messages=messages, gen=gen_params)
        if self.provider == Provider.OPENAI_COMPAT:
            raw_text = OpenAICompatAdapter.extract_text(response_json)
        else:
            raw_text = OllamaAdapter.extract_text(response_json)
        if gen_params.json_output and gen_params.strict_json:
            reasoning, final = parse_json_strict(raw_text)
            if final is None:
                # fallback
                reasoning, final = parse_structured_output(raw_text)
        else:
            reasoning, final = parse_structured_output(raw_text)
        return ChatResult(reasoning=reasoning, final_answer=final, raw=response_json)

    def stream_chat(self, user_prompt: str, system_prompt: Optional[str] = None, gen: Optional[GenerationParams] = None) -> Iterable[Tuple[str, str]]:
        gen_params = self._merge_gen(gen)
        system = system_prompt or (build_json_system_instruction() if gen_params.json_output else build_system_instruction())
        messages: List[Message] = [
            Message(role="system", content=system),
            Message(role="user", content=user_prompt),
        ]
        if self.provider == Provider.OPENAI_COMPAT:
            stream = self._adapter.stream_chat(model=self.model, messages=messages, gen=gen_params)
        else:
            stream = self._adapter.stream_chat(model=self.model, messages=messages, gen=gen_params)

        current_channel: str = "reasoning"
        buffer: str = ""
        for chunk in stream:
            buffer += chunk
            while True:
                start_idx = buffer.lower().find("<final>")
                end_idx = buffer.lower().find("</final>")
                if current_channel == "reasoning" and start_idx != -1:
                    pre = buffer[:start_idx]
                    if pre:
                        yield ("reasoning", pre)
                    buffer = buffer[start_idx + len("<final>") :]
                    current_channel = "final"
                    continue
                if current_channel == "final" and end_idx != -1:
                    pre = buffer[:end_idx]
                    if pre:
                        yield ("final", pre)
                    buffer = buffer[end_idx + len("</final>") :]
                    current_channel = "final"
                    continue
                break
            if buffer and ("<final>" not in buffer.lower() and "</final>" not in buffer.lower()):
                yield (current_channel, buffer)
                buffer = ""
        if buffer:
            yield (current_channel, buffer)
