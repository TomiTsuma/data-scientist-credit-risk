"""Concrete agent implementations for Sunculture AI platform."""

from __future__ import annotations

from typing import Any, Dict, Optional

from ..config.prompts import get_prompt
from ..core.agent import MicroAgent
from ..core.context import ContextManager
from ..core.execution_log import ExecutionLog
from .concrete_skills import SunCultureAnalysisSkill, SunCultureDataSkill


class CustomerAnalysisAgent(MicroAgent):
    """Micro-agent for analyzing customer segments and churn."""
    
    def __init__(
        self,
        execution_log: Optional[ExecutionLog] = None,
        context_manager: Optional[ContextManager] = None,
    ):
        super().__init__(
            name="CustomerAnalysisAgent",
            task_type="customer_analysis",
            provider="openai",
            model="gpt-4o-mini",
            execution_log=execution_log,
            context_manager=context_manager,
        )
        
        # Register skills
        self.data_skill = SunCultureDataSkill(execution_log)
        self.analysis_skill = SunCultureAnalysisSkill(execution_log)
        self.register_skill("data", self.data_skill)
        self.register_skill("analysis", self.analysis_skill)
    
    async def _perform_task(
        self, input_data: Dict[str, Any], **kwargs
    ) -> Dict[str, Any]:
        """Perform customer analysis."""
        # Phase 1: Fetch data
        customer_data = self.data_skill.fetch_data(
            source=input_data.get("data_source", "parquet"),
            file_path=input_data.get("file_path"),
            name="customer_features",
        )
        
        # Phase 2: Analyze data
        analysis_results = self.analysis_skill.analyze(
            customer_data,
            analysis_type=input_data.get("analysis_type", "descriptive"),
        )
        
        # Phase 3: Generate insights with LLM
        prompt = get_prompt(
            "customer_analysis",
            "segment_analysis",
            context=str(analysis_results)[:500],
        )
        
        insights = await self.call_llm(prompt, task_name="segment_analysis")
        
        self.output_sections = ["customer_analysis", "insights"]
        
        return {
            "analysis": analysis_results,
            "insights": insights,
            "data_shape": (len(customer_data), len(customer_data.columns)),
        }


class GrowthOperationsAgent(MicroAgent):
    """Micro-agent for growth operations analysis."""
    
    def __init__(
        self,
        execution_log: Optional[ExecutionLog] = None,
        context_manager: Optional[ContextManager] = None,
    ):
        super().__init__(
            name="GrowthOperationsAgent",
            task_type="growth_operations",
            provider="openai",
            model="gpt-4o-mini",
            execution_log=execution_log,
            context_manager=context_manager,
        )
        
        # Register skills
        self.data_skill = SunCultureDataSkill(execution_log)
        self.analysis_skill = SunCultureAnalysisSkill(execution_log)
        self.register_skill("data", self.data_skill)
        self.register_skill("analysis", self.analysis_skill)
    
    async def _perform_task(
        self, input_data: Dict[str, Any], **kwargs
    ) -> Dict[str, Any]:
        """Perform growth operations analysis."""
        # Phase 1: Fetch and analyze growth data
        growth_data = self.data_skill.fetch_data(
            source=input_data.get("data_source", "parquet"),
            file_path=input_data.get("file_path"),
            name="growth_metrics",
        )
        
        # Phase 2: Perform analysis
        analysis_results = self.analysis_skill.analyze(
            growth_data,
            analysis_type="aggregation",
            group_by=input_data.get("group_by", ["channel"]),
        )
        
        # Phase 3: Generate recommendations with LLM
        prompt = get_prompt(
            "growth_operations",
            "channel_optimization",
            data=str(analysis_results)[:500],
        )
        
        recommendations = await self.call_llm(prompt, task_name="channel_optimization")
        
        self.output_sections = ["growth_analysis", "recommendations"]
        
        return {
            "analysis": analysis_results,
            "recommendations": recommendations,
        }


class RecommendationAgent(MicroAgent):
    """Micro-agent for generating strategic recommendations."""
    
    def __init__(
        self,
        execution_log: Optional[ExecutionLog] = None,
        context_manager: Optional[ContextManager] = None,
    ):
        super().__init__(
            name="RecommendationAgent",
            task_type="recommendations",
            provider="openai",
            model="gpt-4o-mini",
            execution_log=execution_log,
            context_manager=context_manager,
        )
        
        self.analysis_skill = SunCultureAnalysisSkill(execution_log)
        self.register_skill("analysis", self.analysis_skill)
    
    async def _perform_task(
        self, input_data: Dict[str, Any], **kwargs
    ) -> Dict[str, Any]:
        """Generate strategic recommendations."""
        context = input_data.get("context", "")
        analysis = input_data.get("analysis", "")
        
        prompt = get_prompt(
            "recommendations",
            "strategy_rec",
            market="B2B SaaS",
            position=context,
        )
        
        recommendations = await self.call_llm(prompt, task_name="strategy_rec")
        
        self.output_sections = ["strategic_recommendations"]
        
        return {
            "recommendations": recommendations,
            "confidence": 0.85,
        }
