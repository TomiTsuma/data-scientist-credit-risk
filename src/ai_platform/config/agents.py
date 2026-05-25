"""Agent registry for AI platform - defines available agents and their capabilities."""

from __future__ import annotations

from typing import Dict, List

# Agent definitions
AGENTS: Dict[str, Dict[str, any]] = {
    "customer_analysis": {
        "display_name": "Customer Analysis Agent",
        "description": "Analyzes customer segments, churn, and lifetime value",
        "provider": "openai",
        "model": "gpt-4o-mini",
        "capabilities": [
            "segment_analysis",
            "churn_prediction",
            "lifetime_value",
            "retention_analysis",
        ],
        "skills": ["DataSkill", "AnalysisSkill", "VisualizationSkill"],
    },
    
    "growth_operations": {
        "display_name": "Growth Operations Agent",
        "description": "Optimizes marketing channels, lead scoring, and product adoption",
        "provider": "openai",
        "model": "gpt-4o-mini",
        "capabilities": [
            "lead_scoring",
            "channel_optimization",
            "product_adoption",
            "pipeline_analysis",
        ],
        "skills": ["DataSkill", "AnalysisSkill", "VisualizationSkill"],
    },
    
    "recommendations": {
        "display_name": "Recommendations Agent",
        "description": "Provides strategic product and business recommendations",
        "provider": "openai",
        "model": "gpt-4o-mini",
        "capabilities": [
            "product_recommendations",
            "strategy_recommendations",
            "pricing_recommendations",
            "market_recommendations",
        ],
        "skills": ["AnalysisSkill", "ReportSkill"],
    },
    
    "orchestrator": {
        "display_name": "Task Orchestrator",
        "description": "Coordinates multiple agents and manages task execution workflow",
        "provider": "openai",
        "model": "gpt-4o-mini",
        "capabilities": [
            "intent_classification",
            "task_routing",
            "result_synthesis",
            "report_generation",
        ],
        "skills": ["IntentClassificationSkill", "ReportSkill"],
    },
}


def get_agent_config(agent_name: str) -> Dict[str, any]:
    """Get configuration for an agent."""
    return AGENTS.get(agent_name, {})


def list_agents() -> List[str]:
    """List all available agents."""
    return list(AGENTS.keys())


def get_agent_capabilities(agent_name: str) -> List[str]:
    """Get capabilities for an agent."""
    config = get_agent_config(agent_name)
    return config.get("capabilities", [])


def register_agent(agent_name: str, config: Dict[str, any]) -> None:
    """Register a new agent configuration."""
    AGENTS[agent_name] = config
