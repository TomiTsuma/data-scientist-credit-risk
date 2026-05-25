import pytest

from src.ai_platform.config import AI_CONFIG
from src.ai_platform.mcp.server import (
    get_portfolio_kpis,
    list_customer_segments,
    query_customers,
    read_business_report,
)
from src.ai_platform.workspace.loader import (
    build_workspace_context,
    list_agents,
    list_markdown_files,
)
from src.ai_platform.workspace.paths import (
    DOCUMENT_STRUCTURE_DIR,
    KNOWLEDGE_DIR,
    SKILLS_DIR,
)
from src.ai_platform.workspace.skill_loader import SkillLoader


def test_get_portfolio_kpis():
    result = get_portfolio_kpis()
    assert "customers" in result or "error" in result


def test_query_customers_kenya():
    result = query_customers(country="Kenya", limit=5)
    assert "matched" in result


def test_list_segments_or_hint():
    result = list_customer_segments()
    assert "segments" in result or "error" in result


def test_read_segmentation_report():
    result = read_business_report("segmentation_report")
    assert "content" in result or "error" in result


def test_workspace_paths_exist():
    assert AI_CONFIG.workspace_root.exists()
    assert (AI_CONFIG.workspace_root / "AGENTS.md").exists()
    assert SKILLS_DIR.exists()
    assert len(list(SKILLS_DIR.glob("*/SKILL.md"))) >= 3


def test_skill_loader_discovers_markdown_skills():
    loader = SkillLoader()
    skills = loader.discover()
    names = {s.name for s in skills}
    assert "portfolio-analytics" in names or "customer-segmentation" in names


def test_list_agents_markdown():
    agents = list_agents()
    ids = {a["id"] for a in agents}
    assert "customer-analytics" in ids
    assert "credit-risk" in ids


def test_knowledge_and_document_structure():
    knowledge = list_markdown_files(KNOWLEDGE_DIR)
    structures = list_markdown_files(DOCUMENT_STRUCTURE_DIR)
    assert len(knowledge) >= 2
    assert len(structures) >= 2


def test_build_workspace_context_includes_soul_and_skills():
    ctx = build_workspace_context("test-session-1")
    assert "AGENTS.md" in ctx or "Workspace" in ctx
    assert "customer-analytics" in ctx or "Available Skills" in ctx
    assert "test-session-1" in ctx


@pytest.mark.asyncio
async def test_build_agent_context():
    pytest.importorskip("fastmcp")
    from src.ai_platform.api.context import build_agent_context

    system, tools, tools_list, rk = await build_agent_context("test-session")
    assert "Sunculture" in system
    assert "list_skills" in system or "OpenClaw" in system
    tool_names = {t["function"]["name"] for t in tools}
    assert "get_portfolio_kpis" in tool_names
    assert "read_skill" in tool_names
    assert "get_session_folder_structure" in tool_names
    assert "create_echarts_chart" in tool_names
    assert len(tools_list) >= 12
