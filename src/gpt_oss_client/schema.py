from __future__ import annotations
from typing import Any, List, Optional
from pydantic import BaseModel


class ChatResult(BaseModel):
    reasoning: Optional[str] = None
    final_answer: Optional[str] = None
    raw: Optional[Any] = None


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    model: str
    messages: List[Message]


class GenerationParams(BaseModel):
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    max_tokens: Optional[int] = None
    json_output: bool = False
    strict_json: bool = False
