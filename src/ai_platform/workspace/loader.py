"""
Load OpenClaw-style workspace markdown: soul files, agents, knowledge, document structures.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

from src.ai_platform.workspace.paths import (
    AGENTS_DIR,
    DOCUMENT_STRUCTURE_DIR,
    KNOWLEDGE_DIR,
    SOUL_FILES,
    WORKSPACE_ROOT,
)
from src.ai_platform.workspace.skill_loader import SkillLoader, get_skills_for_workspace


def load_soul_files(workspace_root: Path | None = None) -> str:
    """Concatenate AGENTS.md, IDENTITY.md, USER.md, etc. for system context."""
    root = Path(workspace_root or WORKSPACE_ROOT)
    chunks: list[str] = []
    for filename in SOUL_FILES:
        path = root / filename
        if path.exists():
            chunks.append(f"\n--- {filename} ---\n")
            chunks.append(path.read_text(encoding="utf-8"))
    return "\n".join(chunks)


def list_markdown_files(directory: Path) -> list[dict[str, str]]:
    if not directory.exists():
        return []
    items = []
    for path in sorted(directory.glob("*.md")):
        items.append({"id": path.stem, "path": str(path), "name": path.stem})
    return items


def read_markdown_file(path: Path, max_chars: int = 12000) -> dict[str, Any]:
    if not path.exists():
        return {"error": f"File not found: {path}"}
    text = path.read_text(encoding="utf-8")
    truncated = len(text) > max_chars
    if truncated:
        text = text[:max_chars] + "\n\n...[truncated]"
    return {"path": str(path), "content": text, "truncated": truncated}


def list_agents(workspace_root: Path | None = None) -> list[dict[str, str]]:
    """Agent definitions are markdown files in workspace/agents/."""
    root = Path(workspace_root or WORKSPACE_ROOT)
    agents_dir = root / "agents"
    if not agents_dir.exists():
        return []
    agents = []
    for path in sorted(agents_dir.glob("*.md")):
        meta = _parse_frontmatter(path)
        agents.append(
            {
                "id": path.stem,
                "name": meta.get("name", path.stem),
                "description": meta.get("description", ""),
                "path": str(path),
            }
        )
    return agents


def read_agent(agent_id: str, workspace_root: Path | None = None) -> dict[str, Any]:
    root = Path(workspace_root or WORKSPACE_ROOT)
    path = root / "agents" / f"{agent_id.replace('.md', '')}.md"
    if not path.exists():
        return {"error": f"Unknown agent: {agent_id}", "available": list_agents(root)}
    meta = _parse_frontmatter(path)
    body = _strip_frontmatter(path.read_text(encoding="utf-8"))
    return {"id": path.stem, "metadata": meta, "content": body, "path": str(path)}


def _parse_frontmatter(path: Path) -> dict[str, Any]:
    content = path.read_text(encoding="utf-8")
    parts = re.split(r"^---$", content, flags=re.MULTILINE)
    if len(parts) >= 3:
        return yaml.safe_load(parts[1].strip()) or {}
    return {}


def _strip_frontmatter(content: str) -> str:
    parts = re.split(r"^---$", content, flags=re.MULTILINE)
    if len(parts) >= 3:
        return parts[2].strip()
    return content.strip()


def build_workspace_context(session_id: str | None = None) -> str:
    """Full workspace context block for the system prompt (Cropnuts live.py pattern)."""
    root = WORKSPACE_ROOT
    session_workspace = ""
    if session_id:
        session_workspace = str(root / "sessions" / session_id / "workspace")

    parts = [
        load_soul_files(root),
        f"\n## Available Skills\n{get_skills_for_workspace(root)}",
    ]

    doc_files = list_markdown_files(DOCUMENT_STRUCTURE_DIR)
    if doc_files:
        parts.append("\n## Document structures (use read_document_structure tool)\n")
        parts.append(", ".join(d["id"] for d in doc_files))

    knowledge_files = list_markdown_files(KNOWLEDGE_DIR)
    if knowledge_files:
        parts.append("\n## Knowledge base (use read_knowledge tool)\n")
        parts.append(", ".join(d["id"] for d in knowledge_files))

    agent_defs = list_agents(root)
    if agent_defs:
        parts.append("\n## Agent definitions (workspace/agents/*.md)\n")
        for a in agent_defs:
            parts.append(f"- **{a['name']}**: {a['description']}")

    if session_id and session_workspace:
        parts.append(
            f"\n## Active session\n"
            f"- Session id: `{session_id}`\n"
            f"- Session workspace: `{session_workspace}`\n"
            f"- Store `task_plan.md`, `findings.md`, `progress.md` ONLY under the session workspace.\n"
            f"- Use `get_session_folder_structure` to inspect session files between steps.\n"
        )

    return "\n".join(parts)
