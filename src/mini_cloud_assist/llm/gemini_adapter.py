from __future__ import annotations
import os
import httpx
from .base import LLMResult


class GeminiAdapter:
    """
    Minimal adapter for a Gemini API style endpoint.
    NOTE: Gemini can be accessed via different surfaces (AI Studio, Vertex).
    This example uses a simple REST pattern; adjust for your environment.
    """
    def __init__(self) -> None:
        self.api_key = os.getenv("GEMINI_API_KEY", "").strip()
        self.model = os.getenv("GEMINI_MODEL", "gemini-1.5-pro").strip()
        if not self.api_key:
            raise RuntimeError("GEMINI_API_KEY is not set")

    async def complete(self, prompt: str) -> LLMResult:
        # Example endpoint pattern (may differ by provider surface).
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        payload = {
            "contents": [
                {"role": "user", "parts": [{"text": prompt}]}
            ],
            "generationConfig": {"temperature": 0.2},
        }

        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.post(url, json=payload)
            r.raise_for_status()
            data = r.json()

            # Typical response contains candidates -> content -> parts -> text
            text = ""
            try:
                text = data["candidates"][0]["content"]["parts"][0]["text"]
            except Exception:
                text = str(data)

            return LLMResult(text=text, raw=data)
