"""OpenClaw-style session workspaces under workspace/sessions/{id}/."""

from __future__ import annotations

import json
import time
import uuid
from pathlib import Path
from typing import Any


class SessionManager:
    def __init__(self, workspace_root: Path):
        self.workspace_root = Path(workspace_root)
        self.sessions_root = self.workspace_root / "sessions"
        self.registry_path = self.sessions_root / "sessions.json"
        self.session_id: str | None = None
        self.session_path: Path | None = None
        self.workspace_path: Path | None = None

    def _update_registry(self, session_id: str) -> None:
        registry: dict[str, Any] = {}
        if self.registry_path.exists():
            try:
                registry = json.loads(
                    self.registry_path.read_text(encoding="utf-8")
                )
            except Exception:
                registry = {}
        registry[session_id] = {
            "sessionId": session_id,
            "updatedAt": int(time.time() * 1000),
            "path": str(self.sessions_root / session_id),
        }
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        self.registry_path.write_text(
            json.dumps(registry, indent=2), encoding="utf-8"
        )

    def create_session(self, session_id: str | None = None) -> str:
        new_id = session_id or str(uuid.uuid4())
        self.session_id = new_id
        self.session_path = self.sessions_root / new_id
        self.workspace_path = self.session_path / "workspace"

        self.session_path.mkdir(parents=True, exist_ok=True)
        self.workspace_path.mkdir(parents=True, exist_ok=True)
        (self.workspace_path / "data").mkdir(parents=True, exist_ok=True)

        if not (self.workspace_path / "progress.md").exists():
            (self.workspace_path / "progress.md").write_text(
                f"# Progress Log — {new_id}\n\n", encoding="utf-8"
            )
        if not (self.workspace_path / "task_plan.md").exists():
            (self.workspace_path / "task_plan.md").write_text(
                f"# Task Plan — {new_id}\n\n[ ] Initializing task...\n",
                encoding="utf-8",
            )
        if not (self.workspace_path / "findings.md").exists():
            (self.workspace_path / "findings.md").write_text(
                f"# Research Findings — {new_id}\n\n", encoding="utf-8"
            )

        self._update_registry(new_id)
        return new_id

    def log_transcript(self, role: str, content: Any, **kwargs: Any) -> None:
        if not self.session_path or not self.session_id:
            return
        transcript = self.session_path / f"{self.session_id}.jsonl"
        entry = {
            "role": role,
            "content": content,
            "timestamp": int(time.time() * 1000),
            **kwargs,
        }
        with transcript.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, default=str) + "\n")
        self._update_registry(self.session_id)

    def log_progress(self, message: str) -> None:
        if not self.workspace_path or not self.session_id:
            return
        progress = self.workspace_path / "progress.md"
        stamp = time.strftime("%Y-%m-%d %H:%M:%S")
        with progress.open("a", encoding="utf-8") as f:
            f.write(f"- [{stamp}] {message}\n")
        self._update_registry(self.session_id)

    def update_task(self, task_description: str, status: str = "in-progress") -> None:
        if not self.workspace_path or not self.session_id:
            return
        task_file = self.workspace_path / "task_plan.md"
        icon = "[/]" if status == "in-progress" else "[x]"
        with task_file.open("a", encoding="utf-8") as f:
            f.write(f"{icon} {task_description}\n")
        self._update_registry(self.session_id)
