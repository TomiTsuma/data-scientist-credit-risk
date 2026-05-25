"""Agent loop with tool calling and SSE event emission (Cropnuts-style)."""

from __future__ import annotations

import asyncio
import inspect
import json
from typing import Any, Awaitable, Callable

from src.ai_platform.config import AI_CONFIG
from src.ai_platform.core.providers.base import ChatProvider
from src.ai_platform.core.providers.ollama import OllamaProvider
from src.ai_platform.core.providers.openai import OpenAIProvider
from src.ai_platform.core.session import SessionManager

EventCallback = Callable[[dict], Awaitable[None]]


class AgentRunner:
    def __init__(
        self,
        provider_type: str = "openai",
        model_id: str = "gpt-4o-mini",
        session_manager: SessionManager | None = None,
        max_iterations: int | None = None,
    ):
        self.provider_type = provider_type
        self.model_id = model_id
        self.session_manager = session_manager
        self.max_iterations = max_iterations or AI_CONFIG.max_tool_iterations

    def _get_task_plan_reminder(self) -> dict[str, Any] | None:
        if not self.session_manager or not self.session_manager.workspace_path:
            return None
        plan_path = self.session_manager.workspace_path / "task_plan.md"
        if not plan_path.exists():
            return None
        try:
            plan_content = plan_path.read_text(encoding="utf-8").strip()
            if not plan_content:
                return None
            return {
                "role": "system",
                "content": (
                    "[TASK PLAN REMINDER — follow unless the user redirects]\n"
                    f"{plan_content}\n"
                    "[END TASK PLAN]"
                ),
            }
        except Exception:
            return None

    def _provider(self, provider_type: str, base_url: str | None) -> ChatProvider:
        if provider_type == "ollama":
            return OllamaProvider(base_url=base_url or AI_CONFIG.ollama_base_url)
        return OpenAIProvider(
            api_key=AI_CONFIG.openai_api_key,
            base_url=base_url or AI_CONFIG.openai_base_url,
        )

    async def run(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
        tools_list: list[Any],
        base_url: str | None = None,
        event_callback: EventCallback | None = None,
    ) -> dict[str, Any]:
        provider = self._provider(self.provider_type, base_url)
        if self.session_manager:
            self.session_manager.log_progress(
                f"Starting run with {self.provider_type}/{self.model_id}"
            )

        response = await provider.chat_complete(messages, self.model_id, tools=tools)
        if event_callback:
            msg = response["choices"][0]["message"]
            if msg.get("content") or msg.get("reasoning"):
                await event_callback(
                    {
                        "type": "thinking",
                        "content": msg.get("content", ""),
                        "reasoning": msg.get("reasoning", ""),
                    }
                )

        return await self._tool_loop(
            response, provider, messages, tools, tools_list, event_callback
        )

    async def _tool_loop(
        self,
        response: dict,
        provider: ChatProvider,
        messages: list[dict],
        tools: list[dict],
        tools_list: list[Any],
        event_callback: EventCallback | None,
    ) -> dict:
        iterations = 0
        while (
            response["choices"][0].get("finish_reason") == "tool_calls"
            and iterations < self.max_iterations
        ):
            iterations += 1
            reminder = self._get_task_plan_reminder()
            if reminder:
                messages.append(reminder)

            assistant_msg = response["choices"][0]["message"]
            tool_calls = assistant_msg.get("tool_calls", [])

            if event_callback:
                await event_callback({"type": "assistant", "message": assistant_msg})
            messages.append(assistant_msg)

            for tool_call in tool_calls:
                name = tool_call["function"]["name"]
                try:
                    args = json.loads(tool_call["function"]["arguments"])
                except json.JSONDecodeError:
                    args = {}

                if event_callback:
                    await event_callback(
                        {
                            "type": "tool_call",
                            "id": tool_call["id"],
                            "name": name,
                            "args": args,
                        }
                    )

                result = await self._execute_tool(name, args, tools_list)

                if self.session_manager:
                    self.session_manager.log_transcript(
                        "tool_result", result, id=tool_call["id"], name=name
                    )

                if event_callback:
                    await event_callback(
                        {
                            "type": "tool_result",
                            "id": tool_call["id"],
                            "name": name,
                            "result": result,
                        }
                    )

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call["id"],
                        "name": name,
                        "content": json.dumps(result, default=str),
                    }
                )

            response = await provider.chat_complete(messages, self.model_id, tools=tools)
            if event_callback:
                msg = response["choices"][0]["message"]
                if msg.get("content") or msg.get("reasoning"):
                    await event_callback(
                        {
                            "type": "thinking",
                            "content": msg.get("content", ""),
                            "reasoning": msg.get("reasoning", ""),
                        }
                    )

        if event_callback:
            final = response["choices"][0]["message"]
            await event_callback({"type": "done", "message": final})

        return response

    async def _execute_tool(
        self, name: str, args: dict, tools_list: list[Any]
    ) -> Any:
        tool_obj = next(
            (t for t in tools_list if getattr(t, "name", None) == name),
            None,
        )
        if not tool_obj:
            return {"error": f"Tool {name} not found"}

        from src.ai_platform.mcp.server import mcp

        def _filter_kwargs(func, passed: dict) -> dict:
            try:
                sig = inspect.signature(func)
                valid = set(sig.parameters)
                if any(
                    p.kind == inspect.Parameter.VAR_KEYWORD
                    for p in sig.parameters.values()
                ):
                    return passed
                return {k: v for k, v in passed.items() if k in valid}
            except ValueError:
                return passed

        try:
            raw_fn = getattr(tool_obj, "fn", None) or getattr(tool_obj, "func", None)
            if raw_fn and callable(raw_fn):
                filtered = _filter_kwargs(raw_fn, args)
                if inspect.iscoroutinefunction(raw_fn):
                    return await raw_fn(**filtered)
                return await asyncio.to_thread(raw_fn, **filtered)
            return await mcp.call_tool(name, args)
        except Exception as exc:
            return {"error": str(exc)}
