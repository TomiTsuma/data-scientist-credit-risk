"""Ollama OpenAI-compatible API provider."""

from __future__ import annotations

from typing import Any

import httpx

from src.ai_platform.core.providers.base import ChatProvider


class OllamaProvider(ChatProvider):
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url.rstrip("/")

    async def chat_complete(
        self,
        messages: list[dict[str, Any]],
        model: str,
        tools: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {"model": model, "messages": messages, "stream": False}
        if tools:
            payload["tools"] = tools

        async with httpx.AsyncClient(timeout=httpx.Timeout(300.0)) as client:
            resp = await client.post(
                f"{self.base_url}/v1/chat/completions",
                json=payload,
            )
            if resp.status_code != 200:
                raise RuntimeError(
                    f"Ollama API error {resp.status_code}: {resp.text[:500]}"
                )
            return resp.json()
