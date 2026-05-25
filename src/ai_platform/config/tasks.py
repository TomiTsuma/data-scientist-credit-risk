"""Task registry for AI platform - defines available tasks and their execution plans."""

from __future__ import annotations

from typing import Dict, List

# Task definitions
TASKS: Dict[str, Dict[str, any]] = {
    "customer_segmentation": {
        "display_name": "Customer Segmentation Analysis",
        "description": "Analyze and segment customers based on behavior, value, and characteristics",
        "primary_agent": "customer_analysis",
        "micro_agents": ["customer_analysis"],
        "phases": [
            "data_gathering",
            "segmentation",
            "analysis",
            "recommendations",
        ],
        "skills": ["DataSkill", "AnalysisSkill", "VisualizationSkill"],
        "output_type": "report",
    },
    
    "churn_analysis": {
        "display_name": "Churn Risk Analysis",
        "description": "Identify at-risk customers and provide retention strategies",
        "primary_agent": "customer_analysis",
        "micro_agents": ["customer_analysis"],
        "phases": [
            "data_gathering",
            "risk_assessment",
            "cohort_analysis",
            "recommendations",
        ],
        "skills": ["DataSkill", "AnalysisSkill", "VisualizationSkill"],
        "output_type": "report",
    },
    
    "growth_planning": {
        "display_name": "Growth Operations Planning",
        "description": "Plan growth initiatives including lead scoring, channel optimization, and product adoption",
        "primary_agent": "growth_operations",
        "micro_agents": ["growth_operations"],
        "phases": [
            "baseline_analysis",
            "channel_analysis",
            "lead_scoring",
            "strategic_plan",
        ],
        "skills": ["DataSkill", "AnalysisSkill", "VisualizationSkill", "ReportSkill"],
        "output_type": "report",
    },
    
    "market_analysis": {
        "display_name": "Market and Competitive Analysis",
        "description": "Analyze market position, competitive landscape, and strategic opportunities",
        "primary_agent": "recommendations",
        "micro_agents": ["recommendations"],
        "phases": [
            "market_research",
            "competitive_analysis",
            "positioning_analysis",
            "strategy_development",
        ],
        "skills": ["AnalysisSkill", "ReportSkill"],
        "output_type": "report",
    },
    
    "quick_insight": {
        "display_name": "Quick Insight",
        "description": "Generate quick insights on a specific question or metric",
        "primary_agent": "orchestrator",
        "micro_agents": ["customer_analysis", "growth_operations"],
        "phases": [
            "intent_classification",
            "data_gathering",
            "analysis",
            "insight_synthesis",
        ],
        "skills": ["DataSkill", "AnalysisSkill"],
        "output_type": "text",
    },
}


def get_task_config(task_name: str) -> Dict[str, any]:
    """Get configuration for a task."""
    return TASKS.get(task_name, {})


def list_tasks() -> List[str]:
    """List all available tasks."""
    return list(TASKS.keys())


def get_task_phases(task_name: str) -> List[str]:
    """Get execution phases for a task."""
    config = get_task_config(task_name)
    return config.get("phases", [])


def get_task_agents(task_name: str) -> List[str]:
    """Get micro-agents for a task."""
    config = get_task_config(task_name)
    return config.get("micro_agents", [])


def register_task(task_name: str, config: Dict[str, any]) -> None:
    """Register a new task configuration."""
    TASKS[task_name] = config
