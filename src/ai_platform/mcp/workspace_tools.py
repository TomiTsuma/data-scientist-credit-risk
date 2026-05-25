"""OpenClaw-style workspace MCP tools: skills, agents, knowledge, sessions."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.ai_platform.config import AI_CONFIG
from src.ai_platform.mcp._instance import mcp
from src.ai_platform.workspace import loader as ws_loader
from src.ai_platform.workspace.paths import (
    DOCUMENT_STRUCTURE_DIR,
    KNOWLEDGE_DIR,
    SESSIONS_DIR,
)
from src.ai_platform.workspace.skill_loader import SkillLoader


def _session_workspace(session_id: str) -> Path:
    return SESSIONS_DIR / session_id / "workspace"


def _build_tree(current_path: Path, depth: int, current_depth: int = 0) -> dict:
    ignore = {
        ".git",
        "__pycache__",
        ".venv",
        "node_modules",
        ".pytest_cache",
    }
    if current_depth > depth:
        return {"type": "directory", "name": current_path.name, "children": []}
    children = []
    try:
        for item in sorted(current_path.iterdir()):
            if item.name in ignore:
                continue
            if item.is_dir():
                children.append(_build_tree(item, depth, current_depth + 1))
            else:
                children.append({"type": "file", "name": item.name})
    except PermissionError:
        return {
            "type": "directory",
            "name": current_path.name,
            "error": "Permission denied",
        }
    return {"type": "directory", "name": current_path.name, "children": children}


@mcp.tool(
    name="list_skills",
    description="List markdown skills from workspace/skills (OpenClaw SKILL.md files).",
)
def list_skills() -> dict[str, Any]:
    loader = SkillLoader()
    skills = loader.discover()
    return {
        "skills": [
            {
                "name": s.name,
                "description": s.description,
                "path": str(s.path),
            }
            for s in skills
        ]
    }


@mcp.tool(
    name="read_skill",
    description="Read full instructions for a skill by name (folder name or frontmatter name).",
)
def read_skill(skill_name: str, max_chars: int = 12000) -> dict[str, Any]:
    loader = SkillLoader()
    loader.discover()
    skill = loader.skills.get(skill_name)
    if not skill:
        for s in loader.skills.values():
            if s.path.parent.name == skill_name:
                skill = s
                break
    if not skill:
        return {
            "error": f"Unknown skill: {skill_name}",
            "available": list(loader.skills.keys()),
        }
    text = skill.path.read_text(encoding="utf-8")
    truncated = len(text) > max_chars
    if truncated:
        text = text[:max_chars] + "\n\n...[truncated]"
    return {
        "name": skill.name,
        "path": str(skill.path),
        "content": text,
        "truncated": truncated,
    }


@mcp.tool(
    name="list_agents",
    description="List agent definitions from workspace/agents/*.md.",
)
def list_agents() -> dict[str, Any]:
    return {"agents": ws_loader.list_agents()}


@mcp.tool(
    name="read_agent",
    description="Read an agent markdown definition by id (filename stem).",
)
def read_agent(agent_id: str) -> dict[str, Any]:
    return ws_loader.read_agent(agent_id)


@mcp.tool(
    name="list_knowledge",
    description="List knowledge base markdown files in workspace/knowledge/.",
)
def list_knowledge() -> dict[str, Any]:
    return {"files": ws_loader.list_markdown_files(KNOWLEDGE_DIR)}


@mcp.tool(
    name="read_knowledge",
    description="Read a knowledge file by id (filename without .md).",
)
def read_knowledge(doc_id: str) -> dict[str, Any]:
    path = KNOWLEDGE_DIR / f"{doc_id.replace('.md', '')}.md"
    return ws_loader.read_markdown_file(path)


@mcp.tool(
    name="list_document_structures",
    description="List report/document outline templates in workspace/document_structure/.",
)
def list_document_structures() -> dict[str, Any]:
    return {
        "structures": ws_loader.list_markdown_files(DOCUMENT_STRUCTURE_DIR)
    }


@mcp.tool(
    name="read_document_structure",
    description="Read a document structure template by id (filename stem).",
)
def read_document_structure(structure_id: str) -> dict[str, Any]:
    path = DOCUMENT_STRUCTURE_DIR / f"{structure_id.replace('.md', '')}.md"
    return ws_loader.read_markdown_file(path)


@mcp.tool(
    name="get_session_folder_structure",
    description="List files in a session workspace (workspace/sessions/{id}/workspace).",
)
def get_session_folder_structure(session_id: str, depth: int = 2) -> dict[str, Any]:
    session_path = _session_workspace(session_id)
    if not session_path.exists():
        return {
            "error": f"Session workspace not found: {session_id}",
            "expected": str(session_path),
        }
    tree = _build_tree(session_path, max(1, min(depth, 5)))
    return {"status": "success", "session_id": session_id, "path": str(session_path), "structure": tree}


@mcp.tool(
    name="get_workspace_structure",
    description="List top-level OpenClaw workspace folders (agents, skills, knowledge, etc.).",
)
def get_workspace_structure(depth: int = 2) -> dict[str, Any]:
    root = AI_CONFIG.workspace_root
    if not root.exists():
        return {"error": f"Workspace root missing: {root}"}
    tree = _build_tree(root, max(1, min(depth, 4)))
    return {"status": "success", "path": str(root), "structure": tree}
