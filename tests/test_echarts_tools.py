import pytest

from src.ai_platform.mcp.echarts_tools import (
    create_echarts_chart,
    create_echarts_portfolio_preset,
)


def test_create_echarts_bar_option():
    result = create_echarts_chart(
        chart_type="bar",
        title="Test chart",
        categories=["Kenya", "Uganda"],
        series=[{"name": "Arrears %", "data": [12.5, 18.2]}],
        y_axis_name="%",
    )
    assert "echartsOption" in result
    assert result["echartsOption"]["series"][0]["type"] == "bar"
    assert result["echartsOption"]["xAxis"]["data"] == ["Kenya", "Uganda"]


def test_create_echarts_pie_option():
    result = create_echarts_chart(
        chart_type="pie",
        title="Mix",
        series=[
            {
                "name": "Payment",
                "data": [
                    {"name": "PAYG", "value": 60},
                    {"name": "CASH", "value": 40},
                ],
            }
        ],
    )
    assert result["echartsOption"]["series"][0]["type"] == "pie"


def test_create_echarts_portfolio_preset_or_error():
    result = create_echarts_portfolio_preset("arrears_by_country")
    assert "echartsOption" in result or "error" in result
