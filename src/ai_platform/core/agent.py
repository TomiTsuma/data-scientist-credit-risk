"""Base agent class for AI platform agents with LLM provider abstraction."""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from .context import ContextManager
from .execution_log import ExecutionLog
from .skills import Skill


class BaseAgent(ABC):
    """Base class for all agents - handles LLM provider abstraction and skill composition."""
    
    def __init__(
        self,
        name: str,
        provider: str = "openai",
        model: Optional[str] = None,
        execution_log: Optional[ExecutionLog] = None,
        context_manager: Optional[ContextManager] = None,
    ):
        self.name = name
        self.provider = provider.lower()
        self.model = model or self._get_default_model()
        self.execution_log = execution_log
        self.context_manager = context_manager
        self.llm_service = self._initialize_llm_service()
        self.skills: Dict[str, Skill] = {}
    
    def _get_default_model(self) -> str:
        """Get default model for provider."""
        defaults = {
            "openai": "gpt-4o-mini",
            "gemini": "gemini-2.0-flash",
            "ollama": "llama3",
            "claude": "claude-3-5-sonnet-20240620",
        }
        return defaults.get(self.provider, "gpt-4o-mini")
    
    def _initialize_llm_service(self) -> Any:
        """Initialize LLM service based on provider."""
        try:
            if self.provider == "openai":
                from ..providers.openai import OpenAIService
                return OpenAIService(model=self.model)
            elif self.provider == "gemini":
                from ..providers.gemini import GeminiService
                return GeminiService(model=self.model)
            elif self.provider == "ollama":
                from ..providers.ollama import OllamaService
                return OllamaService(model=self.model)
            elif self.provider == "claude":
                from ..providers.claude import ClaudeService
                return ClaudeService(model=self.model)
            else:
                raise ValueError(f"Unsupported provider: {self.provider}")
        except ImportError as e:
            raise RuntimeError(f"Provider '{self.provider}' not available: {e}")
    
    def register_skill(self, skill_name: str, skill: Skill) -> None:
        """Register a skill for use by this agent."""
        self.skills[skill_name] = skill
    
    def get_skill(self, skill_name: str) -> Optional[Skill]:
        """Retrieve a registered skill."""
        return self.skills.get(skill_name)
    
    async def call_llm(
        self,
        prompt: str,
        task_name: str = "general",
        stream: bool = False,
        **kwargs,
    ) -> str:
        """Call the LLM service with prompt."""
        start_time = time.time()
        
        try:
            if stream:
                response = await self.llm_service.generate_async_stream(
                    prompt, model=self.model, **kwargs
                )
            else:
                response = await self.llm_service.generate_async(
                    prompt, model=self.model, **kwargs
                )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Log the interaction
            if self.execution_log:
                self.execution_log.log_llm_interaction(
                    agent=self.name,
                    task=task_name,
                    model=self.model,
                    prompt=prompt,
                    response=response,
                    latency_ms=latency_ms,
                )
            
            # Log to context if available
            if self.context_manager:
                self.context_manager.log_llm_interaction(
                    agent_name=self.name,
                    prompt=prompt,
                    response=response,
                    model=self.model,
                )
            
            return response
        
        except Exception as e:
            error_msg = str(e)
            if self.execution_log:
                self.execution_log.log_llm_interaction(
                    agent=self.name,
                    task=task_name,
                    model=self.model,
                    prompt=prompt,
                    response="",
                    status="error",
                    error=error_msg,
                )
                self.execution_log.log_error(
                    error_message=f"LLM call failed: {error_msg}",
                    phase=f"Agent: {self.name}",
                )
            raise
    
    @abstractmethod
    async def execute(self, input_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Execute the agent's main task."""
        pass


class MicroAgent(BaseAgent):
    """Specialized agent for specific micro-tasks within a larger workflow."""
    
    def __init__(
        self,
        name: str,
        task_type: str,
        provider: str = "openai",
        model: Optional[str] = None,
        execution_log: Optional[ExecutionLog] = None,
        context_manager: Optional[ContextManager] = None,
    ):
        super().__init__(
            name=name,
            provider=provider,
            model=model,
            execution_log=execution_log,
            context_manager=context_manager,
        )
        self.task_type = task_type
        self.input_sections: List[str] = []
        self.output_sections: List[str] = []
    
    async def execute(self, input_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Execute micro-agent task."""
        try:
            # Extract input sections from context
            if self.context_manager:
                self.input_sections = self.context_manager._context.get(
                    "completed_sections", []
                )
            
            # Perform micro-task
            result = await self._perform_task(input_data, **kwargs)
            
            # Track execution
            if self.execution_log:
                self.execution_log.log_micro_agent_execution(
                    agent_name=self.name,
                    input_sections=self.input_sections,
                    output_sections=self.output_sections,
                    status="success",
                )
            
            return result
        
        except Exception as e:
            if self.execution_log:
                self.execution_log.log_micro_agent_execution(
                    agent_name=self.name,
                    input_sections=self.input_sections,
                    output_sections=self.output_sections,
                    status="error",
                    error=str(e),
                )
            raise
    
    @abstractmethod
    async def _perform_task(
        self, input_data: Dict[str, Any], **kwargs
    ) -> Dict[str, Any]:
        """Perform the specific micro-task."""
        pass
