"""
Streaming chat API (SSE) — mirrors Cropnuts `backend/api/live.py` pattern.

POST /api/ai/v1/chat/stream
"""

from __future__ import annotations

import asyncio
import json

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

from src.ai_platform.api.context import build_agent_context
from src.ai_platform.config import AI_CONFIG
from src.ai_platform.core.agents.runner import AgentRunner

router = APIRouter(tags=["ai"])


@router.post("/v1/chat/stream")
async def chat_stream(request: Request):
    """
    Server-Sent Events stream. Event types:
      thinking | assistant | tool_call | tool_result | done | error
    """
    data = await request.json()
    conv_id = data.get("conv_id") or data.get("session_id")
    messages = data.get("messages", [])
    provider = data.get("provider", AI_CONFIG.provider)
    model = data.get("model", AI_CONFIG.model)

    system_message, tools_schema, tools_list, rk = await build_agent_context(conv_id)
    augmented = [{"role": "system", "content": system_message}] + messages

    runner = AgentRunner(
        provider_type=provider,
        model_id=model,
        session_manager=rk["session_manager"],
    )

    if rk["session_manager"]:
        rk["session_manager"].create_session(session_id=conv_id)

    queue: asyncio.Queue = asyncio.Queue()

    async def on_event(event: dict):
        await queue.put(json.dumps(event, default=str))

    async def run_agent():
        try:
            await runner.run(
                messages=augmented,
                tools=tools_schema,
                tools_list=tools_list,
                base_url=rk.get("base_url"),
                event_callback=on_event,
            )
        except Exception as exc:
            await queue.put(json.dumps({"type": "error", "detail": str(exc)}))
        finally:
            await queue.put(None)

    async def event_generator():
        asyncio.create_task(run_agent())
        while True:
            item = await queue.get()
            if item is None:
                break
            yield f"data: {item}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.get("/v1/health")
async def ai_health():
    from src.ai_platform.data_access import load_customer_frame

    data_ok = AI_CONFIG.customer_features_path.exists()
    model_ok = (AI_CONFIG.models_dir / "segmentation" / "kmeans_pipeline.joblib").exists()
    try:
        n = len(load_customer_frame()) if data_ok else 0
    except Exception:
        n = 0
    return {
        "status": "ok",
        "provider": AI_CONFIG.provider,
        "model": AI_CONFIG.model,
        "data_ready": data_ok,
        "segmentation_model_ready": model_ok,
        "customers_loaded": n,
        "openai_key_set": bool(AI_CONFIG.openai_api_key),
    }
