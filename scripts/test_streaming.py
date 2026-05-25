"""
SSE client for Sunculture AI chat — mirrors Cropnuts test_streaming.py.

Usage:
  # Terminal 1: python3.11 -m uvicorn src.deployment.api.app:app --reload --port 8000
  # Terminal 2:
  python3.11 scripts/test_streaming.py "What are portfolio arrears rates by country?"
"""
from __future__ import annotations

import json
import sys
import uuid

import httpx

GATEWAY = "http://localhost:8000"


def stream_chat(
    user_message: str,
    conv_id: str | None = None,
    provider: str | None = None,
    model: str | None = None,
):
    conv_id = conv_id or str(uuid.uuid4())
    payload: dict = {
        "messages": [{"role": "user", "content": user_message}],
        "conv_id": conv_id,
    }
    if provider:
        payload["provider"] = provider
    if model:
        payload["model"] = model

    print(f"\n--- Session: {conv_id} ---")
    print(f"--- Sending: {user_message!r} ---\n")

    with httpx.Client(timeout=None) as client:
        with client.stream(
            "POST",
            f"{GATEWAY}/api/ai/v1/chat/stream",
            json=payload,
            headers={"Content-Type": "application/json"},
        ) as response:
            response.raise_for_status()
            buffer = ""
            for chunk in response.iter_text():
                buffer += chunk
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    line = line.strip()
                    if not line.startswith("data: "):
                        continue
                    raw = line[6:]
                    try:
                        event = json.loads(raw)
                    except json.JSONDecodeError:
                        continue

                    ev_type = event.get("type", "unknown")
                    if ev_type == "thinking":
                        c = event.get("content") or event.get("reasoning") or ""
                        if c:
                            print(f"[THINKING] {c[:300]}")
                    elif ev_type == "tool_call":
                        print(f"[TOOL_CALL] {event.get('name')} args={event.get('args')}")
                    elif ev_type == "tool_result":
                        res = json.dumps(event.get("result", {}), default=str)
                        print(f"[TOOL_RESULT] {event.get('name')}: {res[:400]}")
                    elif ev_type == "done":
                        msg = event.get("message", {})
                        print(f"\n[DONE]\n{msg.get('content', '')}")
                    elif ev_type == "error":
                        print(f"[ERROR] {event.get('detail')}")
                    else:
                        print(f"[{ev_type.upper()}] {str(event)[:200]}")

    print("\n--- Stream ended ---")


if __name__ == "__main__":
    msg = (
        " ".join(sys.argv[1:])
        if len(sys.argv) > 1
        else "Summarize portfolio KPIs for Kenya and recommend which customer segment to target for a premium loan."
    )
    stream_chat(msg)
