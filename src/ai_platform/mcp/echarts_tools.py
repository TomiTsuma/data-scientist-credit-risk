"""MCP tool that returns Apache ECharts option JSON for the analytics UI."""

from __future__ import annotations

import json
import uuid
from typing import Any, Literal

from src.ai_platform.data_access import load_customer_frame
from src.ai_platform.mcp._instance import mcp

ChartType = Literal["bar", "line", "pie", "scatter", "stacked_bar"]

SUN_COLORS = [
    "#1B7F4E",
    "#F4A623",
    "#2E86AB",
    "#E84855",
    "#6C4B7A",
    "#88B04B",
]


def _build_bar_line_option(
    chart_type: str,
    title: str,
    categories: list[str],
    series: list[dict[str, Any]],
    y_axis_name: str | None,
    subtitle: str | None,
    stacked: bool,
) -> dict[str, Any]:
    is_line = chart_type == "line"
    echarts_series = []
    for i, s in enumerate(series):
        name = str(s.get("name", f"Series {i + 1}"))
        data = s.get("data", [])
        item: dict[str, Any] = {
            "name": name,
            "type": "line" if is_line else "bar",
            "data": data,
            "emphasis": {"focus": "series"},
        }
        if stacked and not is_line:
            item["stack"] = "total"
        echarts_series.append(item)

    option: dict[str, Any] = {
        "color": SUN_COLORS,
        "title": {"text": title, "left": "center"},
        "tooltip": {"trigger": "axis"},
        "legend": {"top": 32, "data": [x["name"] for x in echarts_series]},
        "grid": {"left": "3%", "right": "4%", "bottom": "3%", "containLabel": True},
        "xAxis": {
            "type": "category",
            "data": categories,
            "axisLabel": {"rotate": 25 if len(categories) > 6 else 0},
        },
        "yAxis": {"type": "value", "name": y_axis_name or ""},
        "series": echarts_series,
    }
    if subtitle:
        option["title"]["subtext"] = subtitle
    return option


def _build_pie_option(
    title: str,
    series: list[dict[str, Any]],
    subtitle: str | None,
) -> dict[str, Any]:
    first = series[0] if series else {"name": "Share", "data": []}
    data = first.get("data", [])
    if data and isinstance(data[0], (int, float)):
        labels = [f"Item {i + 1}" for i in range(len(data))]
        pie_data = [{"name": labels[i], "value": data[i]} for i in range(len(data))]
    else:
        pie_data = data

    option: dict[str, Any] = {
        "color": SUN_COLORS,
        "title": {"text": title, "left": "center"},
        "tooltip": {"trigger": "item", "formatter": "{b}: {c} ({d}%)"},
        "legend": {"orient": "vertical", "left": "left", "top": "middle"},
        "series": [
            {
                "name": str(first.get("name", "Share")),
                "type": "pie",
                "radius": ["40%", "70%"],
                "avoidLabelOverlap": True,
                "itemStyle": {"borderRadius": 6, "borderColor": "#fff", "borderWidth": 2},
                "label": {"show": True, "formatter": "{b}\n{d}%"},
                "data": pie_data,
            }
        ],
    }
    if subtitle:
        option["title"]["subtext"] = subtitle
    return option


def _build_scatter_option(
    title: str,
    series: list[dict[str, Any]],
    subtitle: str | None,
) -> dict[str, Any]:
    echarts_series = []
    for i, s in enumerate(series):
        echarts_series.append(
            {
                "name": str(s.get("name", f"Series {i + 1}")),
                "type": "scatter",
                "data": s.get("data", []),
                "symbolSize": 10,
            }
        )
    option: dict[str, Any] = {
        "color": SUN_COLORS,
        "title": {"text": title, "left": "center"},
        "tooltip": {"trigger": "item"},
        "legend": {"top": 32},
        "xAxis": {"type": "value", "scale": True},
        "yAxis": {"type": "value", "scale": True},
        "series": echarts_series,
    }
    if subtitle:
        option["title"]["subtext"] = subtitle
    return option


def create_echarts_chart(
    chart_type: ChartType,
    title: str,
    categories: list[str] | None = None,
    series: list[dict[str, Any]] | None = None,
    y_axis_name: str | None = None,
    subtitle: str | None = None,
    chart_id: str | None = None,
) -> dict[str, Any]:
    """
    Build a validated Apache ECharts `option` object for the React UI.

    `series` items: `{ "name": str, "data": number[] }`.
    For pie charts, `data` may be numbers (paired with categories) or
    `[{ "name": str, "value": number }, ...]`.
    """
    chart_id = chart_id or str(uuid.uuid4())
    categories = categories or []
    series = series or []

    if not title.strip():
        return {"error": "title is required"}
    if not series:
        return {"error": "series must contain at least one entry with data"}

    ct = chart_type if chart_type != "stacked_bar" else "bar"
    stacked = chart_type == "stacked_bar"

    try:
        if ct == "pie":
            option = _build_pie_option(title, series, subtitle)
        elif ct == "scatter":
            option = _build_scatter_option(title, series, subtitle)
        else:
            if not categories:
                return {"error": "categories required for bar/line charts"}
            option = _build_bar_line_option(
                ct, title, categories, series, y_axis_name, subtitle, stacked
            )

        json.dumps(option)
    except (TypeError, ValueError) as exc:
        return {"error": f"Invalid chart payload: {exc}"}

    return {
        "chartId": chart_id,
        "chartType": chart_type,
        "title": title,
        "echartsOption": option,
        "renderer": "echarts-for-react",
        "version": "5.x",
    }


def create_echarts_portfolio_preset(
    preset: Literal[
        "arrears_by_country",
        "arrears_by_payment_type",
        "segments_overview",
    ],
    title: str | None = None,
) -> dict[str, Any]:
    """Build ECharts JSON from live portfolio / segment data."""
    df = load_customer_frame()
    if df.empty:
        return {"error": "No customer data. Run python3.11 scripts/run_part2_pipeline.py"}

    if preset == "arrears_by_country":
        grp = (
            df.groupby("country_name")["is_in_arrears"]
            .mean()
            .mul(100)
            .round(2)
            .reset_index()
        )
        return create_echarts_chart(
            chart_type="bar",
            title=title or "Arrears rate by country (%)",
            categories=grp["country_name"].astype(str).tolist(),
            series=[
                {
                    "name": "Arrears %",
                    "data": grp["is_in_arrears"].tolist(),
                }
            ],
            y_axis_name="%",
            subtitle="Proxy from account status",
        )

    if preset == "arrears_by_payment_type":
        grp = (
            df.groupby("payment_type")["is_in_arrears"]
            .mean()
            .mul(100)
            .round(2)
            .reset_index()
        )
        return create_echarts_chart(
            chart_type="bar",
            title=title or "Arrears rate by payment type (%)",
            categories=grp["payment_type"].astype(str).tolist(),
            series=[
                {"name": "Arrears %", "data": grp["is_in_arrears"].tolist()}
            ],
            y_axis_name="%",
        )

    if preset == "segments_overview":
        if "segment_name" not in df.columns:
            return {"error": "Segments not available. Run Part 2 pipeline."}
        grp = (
            df.groupby("segment_name")
            .agg(
                customers=("customer_id", "count"),
                arrears_pct=("is_in_arrears", lambda s: round(s.mean() * 100, 2)),
            )
            .reset_index()
            .sort_values("customers", ascending=False)
        )
        return create_echarts_chart(
            chart_type="bar",
            title=title or "Customers and arrears by segment",
            categories=grp["segment_name"].astype(str).tolist(),
            series=[
                {
                    "name": "Customers",
                    "data": grp["customers"].astype(int).tolist(),
                },
                {
                    "name": "Arrears %",
                    "data": grp["arrears_pct"].tolist(),
                },
            ],
            y_axis_name="Count / %",
            subtitle="Dual series — interpret scales separately",
        )

    return {"error": f"Unknown preset: {preset}"}


mcp.tool(
    name="create_echarts_chart",
    description=(
        "Return Apache ECharts option JSON for the analytics UI. Use after fetching metrics "
        "to visualize bar/line/pie/scatter charts. The UI renders tool_result payloads "
        "with echartsOption via echarts-for-react."
    ),
)(create_echarts_chart)

mcp.tool(
    name="create_echarts_portfolio_preset",
    description=(
        "Return ECharts JSON from live portfolio data. Presets: arrears_by_country, "
        "arrears_by_payment_type, segments_overview."
    ),
)(create_echarts_portfolio_preset)
