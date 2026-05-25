"""Build agent context: system prompt, MCP tools schema, runner kwargs."""

from __future__ import annotations

from typing import Any

from src.ai_platform.config import AI_CONFIG
from src.ai_platform.core.session import SessionManager
from src.ai_platform.mcp.server import mcp
from src.ai_platform.prompt_templates.system import build_system_prompt


def _tool_to_openai_schema(tool_obj: Any) -> dict[str, Any]:
    if hasattr(tool_obj, "to_mcp_tool"):
        try:
            mcp_tool = tool_obj.to_mcp_tool()
            t_name = mcp_tool.name
            t_desc = mcp_tool.description or ""
            t_params = mcp_tool.inputSchema
        except Exception:
            t_name = getattr(tool_obj, "name", str(tool_obj))
            t_desc = getattr(tool_obj, "description", "")
            t_params = {"type": "object", "properties": {}}
    else:
        t_name = getattr(tool_obj, "name", str(tool_obj))
        t_desc = getattr(tool_obj, "description", "")
        t_params = getattr(tool_obj, "parameters", {"type": "object", "properties": {}})

    if isinstance(t_params, dict) and "$ref" in t_params and "$defs" in t_params:
        ref_path = t_params["$ref"]
        if ref_path.startswith("#/$defs/"):
            ref_name = ref_path.split("/")[-1]
            if ref_name in t_params["$defs"]:
                t_params = t_params["$defs"][ref_name].copy()

    return {
        "type": "function",
        "function": {"name": t_name, "description": t_desc, "parameters": t_params},
    }


async def build_agent_context(
    session_id: str | None = None,
) -> tuple[str, list[dict], list[Any], dict[str, Any]]:
    system_message = build_system_prompt(session_id)

    tools_output = await mcp.get_tools()
    tools_list = (
        list(tools_output.values())
        if isinstance(tools_output, dict)
        else list(tools_output)
    )
    tools_schema = [_tool_to_openai_schema(t) for t in tools_list]

    AI_CONFIG.workspace_root.mkdir(parents=True, exist_ok=True)
    AI_CONFIG.sessions_dir.mkdir(parents=True, exist_ok=True)
    session_mgr = SessionManager(AI_CONFIG.workspace_root)
    if session_id:
        session_mgr.create_session(session_id)

    runner_kwargs = {
        "provider_type": AI_CONFIG.provider,
        "model_id": AI_CONFIG.model,
        "session_manager": session_mgr,
        "base_url": None,
    }
    return system_message, tools_schema, tools_list, runner_kwargs
