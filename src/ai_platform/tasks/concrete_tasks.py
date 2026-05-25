"""Concrete task implementations for Sunculture AI platform."""

from __future__ import annotations

from typing import Any, Dict, Optional

from ..core.session import SessionManager
from ..core.task import Task
from .concrete_agents import (
    CustomerAnalysisAgent,
    GrowthOperationsAgent,
    RecommendationAgent,
)
from .concrete_skills import SunCultureReportSkill


@Task.register("customer_segmentation")
class CustomerSegmentationTask(Task):
    """Task for customer segmentation analysis."""
    
    def __init__(
        self,
        session_manager: SessionManager,
        session_id: Optional[str] = None,
    ):
        super().__init__(
            task_name="customer_segmentation",
            session_manager=session_manager,
            session_id=session_id,
        )
        
        # Register micro-agents
        customer_agent = CustomerAnalysisAgent(
            execution_log=self.execution_log,
            context_manager=self.context_manager,
        )
        self.register_micro_agent("customer_analysis", customer_agent)
        
        recommendation_agent = RecommendationAgent(
            execution_log=self.execution_log,
            context_manager=self.context_manager,
        )
        self.register_micro_agent("recommendations", recommendation_agent)
        
        # Build execution plan
        self.add_plan_step(
            "data_gathering",
            "Gather and prepare customer data",
            ["customer_analysis"],
        )
        self.add_plan_step(
            "segmentation",
            "Perform customer segmentation analysis",
            ["customer_analysis"],
        )
        self.add_plan_step(
            "recommendations",
            "Generate strategic recommendations",
            ["recommendations"],
        )
    
    async def _gather_context(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Phase 2: Gather context."""
        return {
            "analysis_type": "segmentation",
            "data_source": input_data.get("data_source", "parquet"),
            "file_path": input_data.get("file_path"),
        }
    
    async def _finalize(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Phase 4: Finalize and generate report."""
        # Assemble report from context
        narrative = self.context_manager.get_narrative()
        
        report_skill = SunCultureReportSkill(execution_log=self.execution_log)
        report = report_skill.assemble_report(
            title="Customer Segmentation Analysis",
            subtitle="AI-Generated Insights and Recommendations",
            executive_summary=narrative[:500],
            metadata={
                "session_id": self.session_id,
                "task": "customer_segmentation",
            },
        )
        
        # Save report
        report_path = self.session_manager.save_report(
            "customer_segmentation_report.md",
            report,
        )
        
        return {
            "status": "completed",
            "report_path": str(report_path),
            "session_id": self.session_id,
        }


@Task.register("growth_planning")
class GrowthPlanningTask(Task):
    """Task for growth operations planning."""
    
    def __init__(
        self,
        session_manager: SessionManager,
        session_id: Optional[str] = None,
    ):
        super().__init__(
            task_name="growth_planning",
            session_manager=session_manager,
            session_id=session_id,
        )
        
        # Register micro-agents
        growth_agent = GrowthOperationsAgent(
            execution_log=self.execution_log,
            context_manager=self.context_manager,
        )
        self.register_micro_agent("growth_ops", growth_agent)
        
        recommendation_agent = RecommendationAgent(
            execution_log=self.execution_log,
            context_manager=self.context_manager,
        )
        self.register_micro_agent("recommendations", recommendation_agent)
        
        # Build execution plan
        self.add_plan_step(
            "baseline_analysis",
            "Analyze current growth metrics",
            ["growth_ops"],
        )
        self.add_plan_step(
            "channel_analysis",
            "Analyze marketing channel performance",
            ["growth_ops"],
        )
        self.add_plan_step(
            "strategic_plan",
            "Develop growth strategy",
            ["recommendations"],
        )
    
    async def _gather_context(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Phase 2: Gather context."""
        return {
            "analysis_type": "growth",
            "data_source": input_data.get("data_source", "parquet"),
            "file_path": input_data.get("file_path"),
            "group_by": input_data.get("group_by", ["channel"]),
        }
    
    async def _finalize(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Phase 4: Finalize and generate report."""
        narrative = self.context_manager.get_narrative()
        
        report_skill = SunCultureReportSkill(execution_log=self.execution_log)
        report = report_skill.assemble_report(
            title="Growth Operations Plan",
            subtitle="Strategic Growth Initiative Recommendations",
            executive_summary=narrative[:500],
            metadata={
                "session_id": self.session_id,
                "task": "growth_planning",
            },
        )
        
        report_path = self.session_manager.save_report(
            "growth_plan_report.md",
            report,
        )
        
        return {
            "status": "completed",
            "report_path": str(report_path),
            "session_id": self.session_id,
        }


@Task.register("quick_insight")
class QuickInsightTask(Task):
    """Task for generating quick insights on specific questions."""
    
    def __init__(
        self,
        session_manager: SessionManager,
        session_id: Optional[str] = None,
    ):
        super().__init__(
            task_name="quick_insight",
            session_manager=session_manager,
            session_id=session_id,
        )
        
        # Register micro-agents
        customer_agent = CustomerAnalysisAgent(
            execution_log=self.execution_log,
            context_manager=self.context_manager,
        )
        self.register_micro_agent("customer_analysis", customer_agent)
        
        growth_agent = GrowthOperationsAgent(
            execution_log=self.execution_log,
            context_manager=self.context_manager,
        )
        self.register_micro_agent("growth_ops", growth_agent)
        
        # Build execution plan
        self.add_plan_step(
            "data_analysis",
            "Analyze data to answer the question",
            ["customer_analysis", "growth_ops"],
        )
    
    async def _gather_context(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Phase 2: Gather context."""
        return {
            "question": input_data.get("question", ""),
            "data_source": input_data.get("data_source", "parquet"),
            "file_path": input_data.get("file_path"),
        }
    
    async def _finalize(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Phase 4: Finalize and return insight."""
        narrative = self.context_manager.get_narrative()
        
        return {
            "status": "completed",
            "insight": narrative,
            "session_id": self.session_id,
        }
