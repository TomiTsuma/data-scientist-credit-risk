from abc import ABC, abstractmethod
from typing import Any


class ChatProvider(ABC):
    @abstractmethod
    async def chat_complete(
        self,
        messages: list[dict[str, Any]],
        model: str,
        tools: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        raise NotImplementedError
