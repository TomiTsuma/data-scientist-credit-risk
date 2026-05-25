"""Prompt registry for AI platform - centralized prompt management."""

from __future__ import annotations

from typing import Dict, Optional

# Prompt registry - maps (agent_name, task_name) to prompt template
PROMPTS: Dict[str, Dict[str, str]] = {
    # Customer Analysis Agent
    "customer_analysis": {
        "segment_analysis": """You are a customer analytics expert specializing in SaaS metrics.
Analyze the provided customer segment data and provide:
1. Key characteristics of the segment
2. Growth trends and patterns
3. Churn risks and retention opportunities
4. Revenue potential and expansion opportunities
5. Actionable recommendations

Data context: {context}

Provide detailed, data-driven insights.""",
        
        "churn_prediction": """You are a customer success strategist.
Analyze the customer data and predict churn risks based on:
1. Product usage patterns
2. Support ticket frequency and sentiment
3. Payment behavior
4. Feature adoption rates

Identify at-risk customers and recommend proactive interventions.
Data: {data}""",
        
        "lifetime_value": """You are a financial analyst specializing in customer economics.
Calculate and analyze customer lifetime value (LTV) based on:
1. Historical spend patterns
2. Contract terms and expansion history
3. Churn probability
4. Growth trajectory

Provide LTV estimates by segment and recommend pricing/packaging strategies.
Data: {data}""",
    },
    
    # Growth Operations Agent
    "growth_operations": {
        "lead_scoring": """You are a growth consultant specializing in lead qualification.
Analyze lead data and provide scores (0-100) based on:
1. Company fit (industry, size, location)
2. Buying signals (website behavior, content engagement)
3. Intent indicators (feature requests, pricing inquiries)
4. Historical conversion patterns

Segment leads into: high priority, medium, low.
Data: {data}""",
        
        "channel_optimization": """You are a marketing analytics expert.
Analyze marketing channel performance and recommend optimizations:
1. Channel ROI analysis
2. Customer acquisition cost (CAC) by channel
3. Lifetime value to CAC ratios
4. Budget allocation recommendations

Data: {data}""",
        
        "product_adoption": """You are a product adoption strategist.
Analyze feature adoption data and provide recommendations:
1. Feature adoption rates and trends
2. Correlation with retention and expansion
3. Barriers to adoption
4. Rollout and education strategies

Data: {data}""",
    },
    
    # Recommendation Agent
    "recommendations": {
        "product_rec": """You are a product recommendation engine.
Based on customer segment characteristics, recommend:
1. Optimal product features for this segment
2. Pricing strategy
3. Packaging recommendations
4. Upsell/cross-sell opportunities

Segment data: {segment}
Current offerings: {offerings}""",
        
        "strategy_rec": """You are a strategic advisor.
Provide strategic recommendations for:
1. Market positioning
2. Competitive differentiation
3. Growth priorities
4. Risk mitigation strategies

Market context: {market}
Company position: {position}""",
    },
    
    # General task
    "general": {
        "default": """You are a helpful AI assistant with expertise in SaaS analytics and business intelligence.
Provide clear, data-driven insights and actionable recommendations.

Context: {context}
Task: {task}""",
    },
}


def get_prompt(agent_name: str, task_name: str = "default", **kwargs) -> str:
    """Get a prompt template for an agent and task."""
    agent_prompts = PROMPTS.get(agent_name, {})
    prompt = agent_prompts.get(task_name, "")
    
    if not prompt:
        # Fallback to general default
        prompt = PROMPTS.get("general", {}).get("default", "")
    
    # Format with provided kwargs
    if kwargs:
        try:
            prompt = prompt.format(**kwargs)
        except KeyError:
            # If some keys missing, just return as-is
            pass
    
    return prompt


def register_prompt(agent_name: str, task_name: str, prompt_template: str) -> None:
    """Register a new prompt template."""
    if agent_name not in PROMPTS:
        PROMPTS[agent_name] = {}
    PROMPTS[agent_name][task_name] = prompt_template


def list_prompts() -> Dict[str, list]:
    """List all available prompts."""
    return {agent: list(tasks.keys()) for agent, tasks in PROMPTS.items()}
