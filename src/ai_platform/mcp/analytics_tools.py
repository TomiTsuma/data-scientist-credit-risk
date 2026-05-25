"""Portfolio analytics MCP tools (Sunculture assessment data)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.ai_platform.config import AI_CONFIG
from src.ai_platform.data_access import load_customer_frame, try_clickhouse_query
from src.ai_platform.mcp._instance import mcp


def get_portfolio_kpis(country: str | None = None) -> dict[str, Any]:
    df = load_customer_frame()
    if country:
        df = df[df["country_name"].str.lower() == country.strip().lower()]
    if df.empty:
        return {"error": "No data for filter", "country": country}

    return {
        "customers": int(len(df)),
        "arrears_rate_pct": round(float(df["is_in_arrears"].mean() * 100), 2),
        "default_rate_pct": round(float(df["is_default"].mean() * 100), 2),
        "avg_repayment_progress": round(float(df["repayment_progress"].mean()), 3),
        "avg_financed_proxy": round(float(df["financed_amount"].mean()), 0),
        "by_country": df.groupby("country_name")
        .agg(
            customers=("customer_id", "count"),
            arrears_pct=("is_in_arrears", lambda s: round(s.mean() * 100, 2)),
        )
        .reset_index()
        .to_dict(orient="records"),
        "by_payment_type": df.groupby("payment_type")
        .agg(
            customers=("customer_id", "count"),
            arrears_pct=("is_in_arrears", lambda s: round(s.mean() * 100, 2)),
        )
        .reset_index()
        .to_dict(orient="records"),
    }


mcp.tool(
    name="get_portfolio_kpis",
    description="Portfolio KPIs: customer counts, arrears rate, default rate, by country and payment type.",
)(get_portfolio_kpis)


def query_customers(
    country: str | None = None,
    payment_type: str | None = None,
    in_arrears: bool | None = None,
    is_default: bool | None = None,
    segment_name: str | None = None,
    limit: int = 20,
) -> dict[str, Any]:
    df = load_customer_frame()
    if country:
        df = df[df["country_name"].str.lower() == country.strip().lower()]
    if payment_type:
        df = df[df["payment_type"].str.upper() == payment_type.strip().upper()]
    if in_arrears is not None:
        df = df[df["is_in_arrears"] == int(in_arrears)]
    if is_default is not None:
        df = df[df["is_default"] == int(is_default)]
    if segment_name and "segment_name" in df.columns:
        df = df[df["segment_name"].str.contains(segment_name, case=False, na=False)]

    limit = min(max(limit, 1), 50)
    cols = [
        c
        for c in [
            "customer_id",
            "country_name",
            "payment_type",
            "product_tier",
            "account_status",
            "is_in_arrears",
            "is_default",
            "repayment_progress",
            "financed_amount",
            "segment_name",
        ]
        if c in df.columns
    ]
    sample = df[cols].head(limit).to_dict(orient="records")
    return {
        "matched": int(len(df)),
        "sample": sample,
        "summary": {
            "arrears_rate_pct": round(float(df["is_in_arrears"].mean() * 100), 2)
            if len(df)
            else 0,
            "default_rate_pct": round(float(df["is_default"].mean() * 100), 2)
            if len(df)
            else 0,
        },
    }


mcp.tool(
    name="query_customers",
    description="Filter customers by country, payment_type, arrears/default flags. Returns summary stats and sample rows.",
)(query_customers)


def list_customer_segments() -> dict[str, Any]:
    df = load_customer_frame()
    if "segment_id" not in df.columns:
        return {
            "error": "Segments not found. Run: python3.11 scripts/run_part2_pipeline.py"
        }

    grp = (
        df.groupby(["segment_id", "segment_name"], dropna=False)
        .agg(
            customers=("customer_id", "count"),
            arrears_pct=("is_in_arrears", lambda s: round(s.mean() * 100, 2)),
            default_pct=("is_default", lambda s: round(s.mean() * 100, 2)),
            avg_repayment=("repayment_progress", "mean"),
            avg_financed=("financed_amount", "mean"),
        )
        .reset_index()
    )
    card_path = AI_CONFIG.models_dir / "segmentation" / "model_card.json"
    meta = {}
    if card_path.exists():
        meta = json.loads(card_path.read_text(encoding="utf-8"))
    return {"segments": grp.to_dict(orient="records"), "model": meta}


mcp.tool(
    name="list_customer_segments",
    description="List segmentation clusters with size and risk metrics. Requires Part 2 pipeline to have been run.",
)(list_customer_segments)


def predict_customer_segment(customer_id: str) -> dict[str, Any]:
    import joblib

    df = load_customer_frame()
    row = df[df["customer_id"] == customer_id]
    if row.empty:
        return {"error": f"customer_id {customer_id} not found"}

    model_path = AI_CONFIG.models_dir / "segmentation" / "kmeans_pipeline.joblib"
    if not model_path.exists():
        if "segment_id" in row.columns:
            r = row.iloc[0]
            return {
                "customer_id": customer_id,
                "segment_id": int(r["segment_id"]),
                "segment_name": str(r.get("segment_name", "")),
                "source": "cached_labels",
            }
        return {"error": "Model not trained. Run: python3.11 scripts/run_part2_pipeline.py"}

    from src.features.segmentation_features import create_segmentation_features

    pipeline = joblib.load(model_path)
    featured = create_segmentation_features(row)
    seg_id = int(pipeline.predict(featured)[0])
    card_path = AI_CONFIG.models_dir / "segmentation" / "model_card.json"
    name = f"Segment {seg_id}"
    if card_path.exists():
        names = json.loads(card_path.read_text(encoding="utf-8")).get(
            "segment_names", {}
        )
        name = names.get(str(seg_id), name)
    return {"customer_id": customer_id, "segment_id": seg_id, "segment_name": name}


mcp.tool(
    name="predict_customer_segment",
    description="Assign a segment to one customer by ID using the trained K-Means pipeline.",
)(predict_customer_segment)


def read_business_report(report_name: str, max_chars: int = 12000) -> dict[str, Any]:
    allowed = {
        "segmentation_report": AI_CONFIG.reports_dir
        / "business_reports"
        / "segmentation_report.md",
        "marketing_strategy": AI_CONFIG.reports_dir
        / "business_reports"
        / "marketing_strategy.md",
        "credit_risk_recommendations": AI_CONFIG.reports_dir
        / "business_reports"
        / "credit_risk_recommendations.md",
        "post_sale_risk_strategy": AI_CONFIG.reports_dir
        / "business_reports"
        / "post_sale_risk_strategy.md",
        "deployment_strategy": AI_CONFIG.reports_dir
        / "technical_reports"
        / "deployment_strategy.md",
        "ai_platform_strategy": AI_CONFIG.reports_dir
        / "technical_reports"
        / "ai_platform_strategy.md",
    }
    key = report_name.replace(".md", "").strip().lower()
    path = allowed.get(key)
    if not path or not path.exists():
        return {
            "error": f"Unknown or missing report: {report_name}",
            "available": list(allowed.keys()),
        }
    text = path.read_text(encoding="utf-8")
    if len(text) > max_chars:
        text = text[:max_chars] + "\n\n...[truncated]"
    return {"report": key, "path": str(path), "content": text}


mcp.tool(
    name="read_business_report",
    description="Read a markdown business or technical report from reports/. Name e.g. segmentation_report, marketing_strategy.",
)(read_business_report)


def run_clickhouse_select(sql: str) -> dict[str, Any]:
    return try_clickhouse_query(sql)


mcp.tool(
    name="run_clickhouse_select",
    description="Run a read-only SELECT against sunculture_db (ClickHouse). Falls back with error if DB unavailable.",
)(run_clickhouse_select)


def read_file(relative_path: str, max_lines: int = 200) -> dict[str, Any]:
    root = AI_CONFIG.root_dir.resolve()
    target = (root / relative_path).resolve()
    if not str(target).startswith(str(root)):
        return {"error": "Path escapes project root"}
    if not target.exists():
        return {"error": f"Not found: {relative_path}"}
    lines = target.read_text(encoding="utf-8", errors="replace").splitlines()
    clipped = lines[:max_lines]
    return {
        "path": str(target.relative_to(root)),
        "lines": len(lines),
        "content": "\n".join(clipped),
        "truncated": len(lines) > max_lines,
    }


mcp.tool(
    name="read_file",
    description="Read a text file under the Sunculture project (reports, docs, workspace). Path relative to project root.",
)(read_file)
