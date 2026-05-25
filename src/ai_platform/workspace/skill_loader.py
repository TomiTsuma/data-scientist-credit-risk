"""
Markdown skill loader (OpenClaw / Cropnuts pattern).

Skills live in `workspace/skills/<name>/SKILL.md` with YAML frontmatter.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from src.ai_platform.workspace.paths import SKILLS_DIR, WORKSPACE_ROOT


@dataclass
class MarkdownSkill:
    name: str
    description: str
    instructions: str
    path: Path
    metadata: dict[str, Any]


class SkillLoader:
    def __init__(self, workspace_root: Path | None = None):
        self.workspace_root = Path(workspace_root or WORKSPACE_ROOT)
        self.skills: dict[str, MarkdownSkill] = {}

    def discover(self) -> list[MarkdownSkill]:
        """Load skills from workspace/skills (highest precedence)."""
        self.skills.clear()
        skills_dir = self.workspace_root / "skills"
        if not skills_dir.exists():
            return []

        for entry in sorted(skills_dir.iterdir()):
            if not entry.is_dir():
                continue
            skill_md = entry / "SKILL.md"
            if skill_md.exists():
                parsed = self._parse(skill_md)
                if parsed:
                    self.skills[parsed.name] = parsed
        return list(self.skills.values())

    def _parse(self, path: Path) -> MarkdownSkill | None:
        try:
            content = path.read_text(encoding="utf-8")
            parts = re.split(r"^---$", content, flags=re.MULTILINE)
            if len(parts) < 3:
                return None
            meta = yaml.safe_load(parts[1].strip()) or {}
            if meta.get("disable-model-invocation") or meta.get("disable_model_invocation"):
                return None
            name = str(meta.get("name", path.parent.name))
            return MarkdownSkill(
                name=name,
                description=str(meta.get("description", "")),
                instructions=parts[2].strip(),
                path=path.resolve(),
                metadata=dict(meta.get("metadata") or {}),
            )
        except Exception:
            return None

    def format_for_prompt(self, max_chars: int = 4000) -> str:
        if not self.skills:
            return ""
        xml = "<available_skills>\n"
        for skill in self.skills.values():
            desc = (
                skill.description.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
            )
            xml += "  <skill>\n"
            xml += f"    <name>{skill.name}</name>\n"
            xml += f"    <location>{skill.path}</location>\n"
            xml += f"    <description>{desc}</description>\n"
            xml += "  </skill>\n"
        xml += "</available_skills>"
        if len(xml) > max_chars:
            compact = "<available_skills>\n"
            for skill in self.skills.values():
                compact += f"  <skill><name>{skill.name}</name>"
                compact += f"<location>{skill.path}</location></skill>\n"
            compact += "</available_skills>"
            return compact[: max_chars - 20] + "\n...[truncated]"
        return xml


def get_skills_for_workspace(workspace_root: Path | None = None) -> str:
    loader = SkillLoader(workspace_root)
    loader.discover()
    return loader.format_for_prompt()
