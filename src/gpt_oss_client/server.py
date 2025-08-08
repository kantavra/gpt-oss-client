from __future__ import annotations
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

from .client import LLMClient
from .providers import Provider
from .schema import GenerationParams

app = FastAPI(title="gpt-oss-client", version="0.2.0")


class ChatIn(BaseModel):
    message: str
    provider: Provider = Provider.OPENAI_COMPAT
    base_url: str = "http://localhost:1234/v1"
    model: str = "gpt-oss-20b"
    api_key: Optional[str] = None
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    max_tokens: Optional[int] = None
    json_output: bool = False
    strict_json: bool = False


class ChatOut(BaseModel):
    reasoning: Optional[str] = None
    final: Optional[str] = None


@app.post("/chat", response_model=ChatOut)
async def chat(payload: ChatIn) -> ChatOut:
    try:
        client = LLMClient(
            provider=payload.provider,
            base_url=payload.base_url,
            model=payload.model,
            api_key=payload.api_key,
        )
        gen = GenerationParams(
            temperature=payload.temperature,
            top_p=payload.top_p,
            max_tokens=payload.max_tokens,
            json_output=payload.json_output,
            strict_json=payload.strict_json,
        )
        result = client.chat(payload.message, gen=gen)
        return ChatOut(reasoning=result.reasoning, final=result.final_answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
