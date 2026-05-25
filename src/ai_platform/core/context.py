"""Context management for AI platform - maintains state across agent execution."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class ContextManager:
    """Manages context envelope for task execution - tracks state, narrative, artifacts."""
    
    def __init__(self, session_path: Path, task_name: str):
        self.session_path = Path(session_path)
        self.task_name = task_name
        self.context_file = self.session_path / "context.json"
        
        # Initialize context structure
        self._context = {
            "task_name": task_name,
            "started_at": datetime.utcnow().isoformat(),
            "metadata": {},
            "completed_sections": [],
            "running_narrative": "",
            "data_context": {},
            "artifacts": {},  # Maps section title to list of file paths
            "llm_logs": [],
            "status": "active",
        }
        self._save()
    
    def set_metadata(self, **kwargs) -> None:
        """Set task metadata (customer, segment, analysis type, etc.)."""
        self._context["metadata"].update(kwargs)
        self._save()
    
    def update_data_context(self, key: str, value: Any) -> None:
        """Update data context dictionary."""
        self._context["data_context"][key] = value
        self._save()
    
    def add_section(
        self,
        section_title: str,
        content: str,
        artifacts: Optional[List[str]] = None,
    ) -> None:
        """Add a completed section to the context."""
        self._context["completed_sections"].append(section_title)
        self._context["running_narrative"] += f"\n## {section_title}\n{content}\n"
        
        if artifacts:
            self._context["artifacts"][section_title] = artifacts
        
        self._save()
    
    def append_to_narrative(self, text: str) -> None:
        """Append text to the running narrative."""
        self._context["running_narrative"] += text
        self._save()
    
    def log_llm_interaction(
        self,
        agent_name: str,
        prompt: str,
        response: str,
        model: str = "gpt-4o-mini",
    ) -> None:
        """Log an LLM interaction for audit trail."""
        self._context["llm_logs"].append({
            "agent": agent_name,
            "timestamp": datetime.utcnow().isoformat(),
            "model": model,
            "prompt": prompt,
            "response": response,
        })
        self._save()
    
    def get_summary(self) -> Dict[str, Any]:
        """Return a summary of context for micro-agents."""
        return {
            "metadata": self._context["metadata"],
            "completed_sections": self._context["completed_sections"],
            "brief_narrative": self._context["running_narrative"][-1000:]
            if len(self._context["running_narrative"]) > 1000
            else self._context["running_narrative"],
            "data_context": self._context["data_context"],
        }
    
    def get_narrative(self) -> str:
        """Get the full running narrative."""
        return self._context["running_narrative"]
    
    def get_artifacts(self, section_title: Optional[str] = None) -> Dict[str, List[str]]:
        """Get artifacts by section or all artifacts."""
        if section_title:
            return {section_title: self._context["artifacts"].get(section_title, [])}
        return self._context["artifacts"]
    
    def finalize(self, final_narrative: Optional[str] = None) -> None:
        """Mark context as finalized."""
        if final_narrative:
            self._context["running_narrative"] = final_narrative
        self._context["status"] = "completed"
        self._context["completed_at"] = datetime.utcnow().isoformat()
        self._save()
    
    def _save(self) -> None:
        """Save context to disk."""
        self.session_path.mkdir(parents=True, exist_ok=True)
        with self.context_file.open("w", encoding="utf-8") as f:
            json.dump(self._context, f, indent=2, default=str)
    
    def to_dict(self) -> Dict[str, Any]:
        """Return full context as dictionary."""
        return self._context
