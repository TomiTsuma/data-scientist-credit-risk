"""Paths for the OpenClaw-style Sunculture workspace."""

from __future__ import annotations

from pathlib import Path

from src.ai_platform.config import AI_CONFIG

WORKSPACE_ROOT = AI_CONFIG.workspace_root
SESSIONS_DIR = AI_CONFIG.sessions_dir
SKILLS_DIR = WORKSPACE_ROOT / "skills"
AGENTS_DIR = WORKSPACE_ROOT / "agents"
KNOWLEDGE_DIR = WORKSPACE_ROOT / "knowledge"
DOCUMENT_STRUCTURE_DIR = WORKSPACE_ROOT / "document_structure"

SOUL_FILES = (
    "AGENTS.md",
    "IDENTITY.md",
    "SOUL.md",
    "TOOLS.md",
    "USER.md",
    "BOOTSTRAP.md",
    "SECURITY.md",
    "VISION.md",
)
