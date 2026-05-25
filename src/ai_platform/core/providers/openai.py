"""OpenAI-compatible chat completions provider."""

from __future__ import annotations

import asyncio
import json
from typing import Any

import httpx

from src.ai_platform.core.providers.base import ChatProvider


class OpenAIProvider(ChatProvider):
    def __init__(self, api_key: str, base_url: str = "https://api.openai.com/v1"):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")

    async def chat_complete(
        self,
        messages: list[dict[str, Any]],
        model: str,
        tools: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        if not self.api_key:
            raise ValueError(
                "OPENAI_API_KEY is not set. Export it before using the AI chat endpoint."
            )

        payload: dict[str, Any] = {"model": model, "messages": messages}
        if tools:
            payload["tools"] = tools

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=httpx.Timeout(300.0)) as client:
            resp = await client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
            )
            if resp.status_code != 200:
                raise RuntimeError(
                    f"OpenAI API error {resp.status_code}: {resp.text[:500]}"
                )
            return resp.json()
