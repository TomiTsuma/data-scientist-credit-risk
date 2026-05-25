"""
Sunculture MCP server — analytics + OpenClaw workspace tools.

Run standalone: python3.11 -m src.ai_platform.mcp.server
"""

from __future__ import annotations

from src.ai_platform.mcp._instance import mcp

# Register tools via decorators on shared `mcp` instance
from src.ai_platform.mcp import analytics_tools as _analytics_tools  # noqa: F401
from src.ai_platform.mcp import echarts_tools as _echarts_tools  # noqa: F401
from src.ai_platform.mcp import workspace_tools as _workspace_tools  # noqa: F401

# Re-export analytics callables for tests and scripts
from src.ai_platform.mcp.analytics_tools import (
    get_portfolio_kpis,
    list_customer_segments,
    predict_customer_segment,
    query_customers,
    read_business_report,
    read_file,
    run_clickhouse_select,
)

__all__ = [
    "mcp",
    "get_portfolio_kpis",
    "query_customers",
    "list_customer_segments",
    "predict_customer_segment",
    "read_business_report",
    "run_clickhouse_select",
    "read_file",
]

if __name__ == "__main__":
    mcp.run()
