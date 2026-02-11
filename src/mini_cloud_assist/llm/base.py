from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol, Optional, Dict, Any


@dataclass(frozen=True)
class LLMResult:
    text: str
    raw: Optional[Dict[str, Any]] = None


class LLM(Protocol):
    async def complete(self, prompt: str) -> LLMResult:
        ...
