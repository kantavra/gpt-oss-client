from enum import Enum


class Provider(str, Enum):
    OPENAI_COMPAT = "openai"
    OLLAMA = "ollama"
