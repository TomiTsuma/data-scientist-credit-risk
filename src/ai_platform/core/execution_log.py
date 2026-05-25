"""Execution logging system for AI platform - tracks all steps, transformations, and LLM calls."""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Optional, Dict, List


@dataclass
class TransformationLog:
    """Record of a data transformation operation."""
    
    transformation_id: str
    input_dataset: str
    output_dataset: str
    method: str
    parameters: Dict[str, Any]
    timestamp: str
    rows_in: int = 0
    rows_out: int = 0
    columns_added: List[str] = None
    
    def __post_init__(self):
        if self.columns_added is None:
            self.columns_added = []


@dataclass
class LLMInteraction:
    """Record of an LLM API call."""
    
    interaction_id: str
    agent: str
    task: str
    model: str
    prompt: str
    response: str
    timestamp: str
    tokens_in: int = 0
    tokens_out: int = 0
    latency_ms: float = 0.0
    status: str = "success"
    error: Optional[str] = None


@dataclass
class DataInput:
    """Record of input data source."""
    
    input_id: str
    source: str  # e.g., "database", "file", "api"
    name: str
    row_count: int
    column_count: int
    timestamp: str


class ExecutionLog:
    """Manages execution logging for a task session."""
    
    def __init__(self, session_path: Path):
        self.session_path = Path(session_path)
        self.log_file = self.session_path / "execution_log.json"
        
        # Initialize log structure
        self._data = {
            "task_id": self.session_path.name,
            "started_at": datetime.utcnow().isoformat(),
            "agent_version": "1.0.0",
            "plan": [],
            "data_inputs": [],
            "transformations": [],
            "llm_interactions": [],
            "micro_agents": [],
            "errors": [],
            "warnings": [],
            "status": "started",
        }
        self._save()
    
    def update_task_info(self, **kwargs) -> None:
        """Update task-level information (user, prompt, context, etc.)."""
        self._data.update(kwargs)
        self._save()
    
    def add_plan_step(self, step_name: str, description: str, status: str = "pending") -> None:
        """Add a step to the execution plan."""
        self._data["plan"].append({
            "step_id": str(uuid.uuid4())[:8],
            "name": step_name,
            "description": description,
            "status": status,
            "timestamp": datetime.utcnow().isoformat(),
        })
        self._save()
    
    def update_plan_step(self, step_index: int, status: str) -> None:
        """Update status of a plan step."""
        if 0 <= step_index < len(self._data["plan"]):
            self._data["plan"][step_index]["status"] = status
            self._data["plan"][step_index]["updated_at"] = datetime.utcnow().isoformat()
            self._save()
    
    def log_data_input(
        self,
        source: str,
        name: str,
        row_count: int,
        column_count: int,
    ) -> str:
        """Log a data input source."""
        input_id = str(uuid.uuid4())[:8]
        data_input = DataInput(
            input_id=input_id,
            source=source,
            name=name,
            row_count=row_count,
            column_count=column_count,
            timestamp=datetime.utcnow().isoformat(),
        )
        self._data["data_inputs"].append(asdict(data_input))
        self._save()
        return input_id
    
    def log_transformation(
        self,
        input_dataset: str,
        output_dataset: str,
        method: str,
        parameters: Dict[str, Any] = None,
        rows_in: int = 0,
        rows_out: int = 0,
        columns_added: List[str] = None,
    ) -> str:
        """Log a data transformation step."""
        transformation_id = str(uuid.uuid4())[:8]
        transform = TransformationLog(
            transformation_id=transformation_id,
            input_dataset=input_dataset,
            output_dataset=output_dataset,
            method=method,
            parameters=parameters or {},
            timestamp=datetime.utcnow().isoformat(),
            rows_in=rows_in,
            rows_out=rows_out,
            columns_added=columns_added or [],
        )
        self._data["transformations"].append(asdict(transform))
        self._save()
        return transformation_id
    
    def log_llm_interaction(
        self,
        agent: str,
        task: str,
        model: str,
        prompt: str,
        response: str,
        tokens_in: int = 0,
        tokens_out: int = 0,
        latency_ms: float = 0.0,
        status: str = "success",
        error: Optional[str] = None,
    ) -> str:
        """Log an LLM API interaction."""
        interaction_id = str(uuid.uuid4())[:8]
        llm_call = LLMInteraction(
            interaction_id=interaction_id,
            agent=agent,
            task=task,
            model=model,
            prompt=prompt[:500],  # Store first 500 chars of prompt
            response=response[:1000],  # Store first 1000 chars of response
            timestamp=datetime.utcnow().isoformat(),
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            latency_ms=latency_ms,
            status=status,
            error=error,
        )
        self._data["llm_interactions"].append(asdict(llm_call))
        self._save()
        return interaction_id
    
    def log_micro_agent_execution(
        self,
        agent_name: str,
        input_sections: List[str],
        output_sections: List[str],
        status: str = "success",
        error: Optional[str] = None,
    ) -> None:
        """Log execution of a micro-agent."""
        self._data["micro_agents"].append({
            "agent_name": agent_name,
            "input_sections": input_sections,
            "output_sections": output_sections,
            "timestamp": datetime.utcnow().isoformat(),
            "status": status,
            "error": error,
        })
        self._save()
    
    def log_error(self, error_message: str, phase: str = "general") -> None:
        """Log an error."""
        self._data["errors"].append({
            "phase": phase,
            "message": error_message,
            "timestamp": datetime.utcnow().isoformat(),
        })
        self._save()
    
    def log_warning(self, warning_message: str, phase: str = "general") -> None:
        """Log a warning."""
        self._data["warnings"].append({
            "phase": phase,
            "message": warning_message,
            "timestamp": datetime.utcnow().isoformat(),
        })
        self._save()
    
    def finalize(self, status: str = "completed") -> None:
        """Mark the execution as finalized."""
        self._data["status"] = status
        self._data["completed_at"] = datetime.utcnow().isoformat()
        self._save()
    
    def _save(self) -> None:
        """Save the log to disk."""
        self.session_path.mkdir(parents=True, exist_ok=True)
        with self.log_file.open("w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2, default=str)
    
    def to_dict(self) -> Dict[str, Any]:
        """Return the full log as a dictionary."""
        return self._data
