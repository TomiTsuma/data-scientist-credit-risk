"""Task system for AI platform - defines execution workflows and coordinates agents."""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional

from .agent import BaseAgent, MicroAgent
from .context import ContextManager
from .execution_log import ExecutionLog
from .session import SessionManager


class Task(ABC):
    """Base class for all tasks - defines a complete execution workflow."""
    
    # Task registry for routing
    _registry: Dict[str, type] = {}
    
    def __init__(
        self,
        task_name: str,
        session_manager: SessionManager,
        session_id: Optional[str] = None,
    ):
        self.task_name = task_name
        self.session_manager = session_manager
        self.session_id = session_id or str(uuid.uuid4())[:8]
        
        # Initialize session infrastructure
        self.session_manager.create_session(
            session_id=self.session_id,
            task_name=task_name,
        )
        
        self.execution_log = self.session_manager.execution_log
        self.context_manager = self.session_manager.context_manager
        self.micro_agents: Dict[str, MicroAgent] = {}
        self.plan_steps: List[Dict[str, Any]] = []
    
    @classmethod
    def register(cls, task_name: str) -> callable:
        """Decorator to register a task class."""
        def decorator(task_class):
            cls._registry[task_name.lower()] = task_class
            return task_class
        return decorator
    
    @classmethod
    def get_task(cls, task_name: str, **kwargs) -> Optional[Task]:
        """Retrieve a task class from registry."""
        task_class = cls._registry.get(task_name.lower())
        if task_class:
            return task_class(**kwargs)
        return None
    
    @classmethod
    def list_tasks(cls) -> List[str]:
        """List all registered tasks."""
        return list(cls._registry.keys())
    
    def register_micro_agent(self, agent_name: str, agent: MicroAgent) -> None:
        """Register a micro-agent for use in this task."""
        self.micro_agents[agent_name] = agent
    
    def get_micro_agent(self, agent_name: str) -> Optional[MicroAgent]:
        """Retrieve a registered micro-agent."""
        return self.micro_agents.get(agent_name)
    
    def add_plan_step(
        self,
        step_name: str,
        description: str,
        agent_names: List[str],
    ) -> None:
        """Add a step to the execution plan."""
        self.plan_steps.append({
            "name": step_name,
            "description": description,
            "agents": agent_names,
        })
        self.execution_log.add_plan_step(step_name, description)
    
    async def execute_plan_step(self, step_index: int, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single step of the plan."""
        if step_index >= len(self.plan_steps):
            raise IndexError(f"Plan step {step_index} does not exist")
        
        step = self.plan_steps[step_index]
        self.execution_log.update_plan_step(step_index, "in_progress")
        
        try:
            results = {}
            for agent_name in step["agents"]:
                agent = self.get_micro_agent(agent_name)
                if agent:
                    result = await agent.execute(input_data)
                    results[agent_name] = result
            
            self.execution_log.update_plan_step(step_index, "completed")
            return results
        
        except Exception as e:
            self.execution_log.update_plan_step(step_index, "failed")
            self.execution_log.log_error(
                error_message=f"Plan step failed: {e}",
                phase=step["name"],
            )
            raise
    
    async def execute_workflow(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the complete task workflow."""
        self.execution_log.update_task_info(status="running")
        
        try:
            # Phase 1: Plan building (already done in task setup)
            self.session_manager.log_progress("Phase 1: Plan generation complete")
            
            # Phase 2: Data gathering and context building
            self.session_manager.log_progress("Phase 2: Gathering context")
            context_data = await self._gather_context(input_data)
            self.context_manager.set_metadata(**context_data)
            
            # Phase 3: Micro-agent execution
            self.session_manager.log_progress("Phase 3: Executing micro-agents")
            for step_idx in range(len(self.plan_steps)):
                await self.execute_plan_step(step_idx, input_data)
            
            # Phase 4: Finalization
            self.session_manager.log_progress("Phase 4: Finalizing results")
            final_output = await self._finalize(input_data)
            
            self.execution_log.finalize("completed")
            return final_output
        
        except Exception as e:
            self.execution_log.log_error(f"Workflow execution failed: {e}", "general")
            self.execution_log.finalize("failed")
            raise
    
    @abstractmethod
    async def _gather_context(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Phase 2: Gather context and metadata for the task."""
        pass
    
    @abstractmethod
    async def _finalize(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Phase 4: Finalize results and generate output."""
        pass


class TaskRegistry:
    """Global registry for managing all available tasks."""
    
    def __init__(self):
        self.tasks = Task._registry
    
    def get_task(self, task_name: str, **kwargs) -> Optional[Task]:
        """Get a task instance by name."""
        return Task.get_task(task_name, **kwargs)
    
    def list_available_tasks(self) -> List[str]:
        """List all available tasks."""
        return Task.list_tasks()
    
    def register_custom_task(self, task_name: str, task_class: type) -> None:
        """Register a custom task class."""
        Task._registry[task_name.lower()] = task_class
