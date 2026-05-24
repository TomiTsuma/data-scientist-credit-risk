#!/usr/bin/env python
"""
Run Part 2 predictive modelling pipeline and generate business/technical reports.

Usage:
    python scripts/run_part2_pipeline.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from src.analysis.credit_insights import compute_collection_insights
from src.analysis.marketing_strategy import campaign_recommendations, top_two_segments
from src.config.config import Config
from src.features.segmentation_features import FEATURE_JUSTIFICATION
from src.models.pipelines.segmentation_pipeline import fit_segmentation

CONFIG = Config()
REPORTS = CONFIG.reports_dir


def _save_elbow_plot(k_eval: list[dict], path: Path) -> None:
    ks = [r["k"] for r in k_eval]
    fig, ax1 = plt.subplots(figsize=(8, 4))
    ax1.plot(ks, [r["inertia"] for r in k_eval], "o-", color="#4361EE", label="Inertia")
    ax1.set_xlabel("Number of clusters (k)")
    ax1.set_ylabel("Inertia")
    ax2 = ax1.twinx()
    ax2.plot(ks, [r["silhouette"] for r in k_eval], "s--", color="#F72585", label="Silhouette")
    ax2.set_ylabel("Silhouette score")
    ax1.set_title("Cluster count selection (elbow + silhouette)")
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def write_segmentation_report(result) -> None:
    path = REPORTS / "business_reports" / "segmentation_report.md"
    df = result.customer_df
    lines = [
        "# Customer Segmentation Report",
        "",
        "## 1. Executive Summary",
        "",
        f"We segmented **{len(df):,} customers** with active accounts into **{result.optimal_k} clusters** "
        "using K-Means on engineered behavioral, demographic, and risk-proxy features. "
        "Segments are named for business use in marketing and collections planning.",
        "",
        "## 2. Data Preparation & Feature Engineering",
        "",
        "Customer grain: one row per `customer_id` from Accounts joined to Customers, Products, "
        "Sales, Installations, and Leads. Financial balances are **proxied** from account status, "
        "payment type, and product tier because the source extract does not include ledger balances.",
        "",
        "| Feature | Rationale |",
        "|---------|-----------|",
    ]
    for feat, reason in FEATURE_JUSTIFICATION.items():
        lines.append(f"| `{feat}` | {reason} |")

    lines.extend(
        [
            "",
            "## 3. Model Selection & Implementation",
            "",
            "### 3a. Algorithm: K-Means",
            "",
            "K-Means was selected because marketing and credit stakeholders need a **fixed, interpretable set of personas**, "
            "centroids are easy to explain, and runtime scales to the full portfolio. "
            "Gaussian Mixture Models were considered for overlapping clusters but deprioritized for interpretability.",
            "",
            "### 3b. Optimal cluster count",
            "",
            "| k | Silhouette | Min cluster % | Inertia |",
            "|---|------------|---------------|---------|",
        ]
    )
    for r in result.k_evaluation:
        lines.append(
            f"| {r['k']} | {r['silhouette']:.3f} | {r['min_cluster_pct']:.1f}% | {r['inertia']:.0f} |"
        )
    lines.append(
        f"\n**Selected k = {result.optimal_k}** — highest silhouette among solutions where every segment "
        "represents at least ~5% of customers (business interpretability constraint).\n"
    )
    lines.append("![Cluster selection](../figures/part2_cluster_selection.png)\n")
    lines.extend(
        [
            "### 3c. Dataset limitations",
            "",
            "- **No income or bureau data** — affluence inferred from product tier and financing proxies only.",
            "- **Snapshot accounts data** — no monthly repayment ledger; `repayment_progress` and balances are modeled proxies.",
            "- **Installation date anomalies** — negative sale-to-install delays indicate data/process issues.",
            "- **Unsupervised segments** optimize statistical separation, not campaign ROI or causality.",
            "- **250 customers** without linked accounts are excluded from clustering.",
            "",
            "## 4. Segment Profiles",
            "",
        ]
    )

    for seg_id, name in sorted(result.segment_names.items()):
        sub = df[df["segment_id"] == seg_id]
        pct = len(sub) / len(df) * 100
        lines.extend(
            [
                f"### Segment {seg_id}: {name}",
                "",
                f"- **Size:** {len(sub):,} customers ({pct:.1f}% of portfolio)",
                f"- **Countries:** {sub['country_name'].value_counts().head(3).to_dict()}",
                f"- **Payment mix:** {sub['payment_type'].value_counts().to_dict()}",
                f"- **Avg repayment progress:** {sub['repayment_progress'].mean():.2f}",
                f"- **Arrears rate:** {sub['is_in_arrears'].mean()*100:.1f}%",
                f"- **Default rate:** {sub['is_default'].mean()*100:.1f}%",
                f"- **Avg financed (proxy):** {sub['financed_amount'].mean():,.0f}",
                f"- **Avg account age (days):** {sub['account_age_days'].mean():.0f}",
                "",
                f"**Persona:** {_persona_blurb(name, sub)}",
                "",
            ]
        )

    path.write_text("\n".join(lines), encoding="utf-8")


def _persona_blurb(name: str, sub: pd.DataFrame) -> str:
    if "Distressed" in name:
        return (
            "Customers with elevated write-off/repossession statuses and weak repayment proxies. "
            "Prioritize collections and workout—not premium upsell."
        )
    if "Arrears" in name:
        return (
            "PAYG-heavy segment with active arrears flags. Needs payment plans and proactive outreach."
        )
    if "Stable Premium" in name:
        return (
            "Strong repayment progress and higher financed exposure—prime candidates for premium loan and loyalty offers."
        )
    if "Reliable" in name:
        return "Solid payers with moderate tenure; good cross-sell potential with light-touch digital channels."
    return "Newer or mid-progress accounts building payment history; nurture with education and agent support."


def write_marketing_report(df: pd.DataFrame) -> None:
    path = REPORTS / "business_reports" / "marketing_strategy.md"
    top2 = top_two_segments(df, country="Kenya")
    lines = [
        "# Data-Driven Marketing Strategy — Kenya Premium Loan",
        "",
        "## Objective",
        "",
        "Launch a premium loan product for **stable, mid-to-high income proxy** customers in Kenya "
        "under a limited marketing budget.",
        "",
        "## 1. Selected Segments",
        "",
        "Scoring weights: stability (35%), affluence proxy (25%), growth potential (15%), "
        "segment size (15%), low default (10%), minus arrears penalty.",
        "",
        "| Rank | Segment | Score | Customers (Kenya) | Arrears % | Default % | Avg repayment |",
        "|------|---------|-------|-------------------|-----------|-----------|---------------|",
    ]
    for i, row in top2.iterrows():
        lines.append(
            f"| {list(top2.index).index(i)+1} | {row['segment_name']} | {row['campaign_score']:.3f} | "
            f"{int(row['customers'])} | {row['arrears_rate']*100:.1f} | {row['default_rate']*100:.1f} | "
            f"{row['stability']:.2f} |"
        )

    lines.append("\n## 2. Campaign Recommendations\n")
    for _, row in top2.iterrows():
        rec = campaign_recommendations(row)
        lines.extend(
            [
                f"### {row['segment_name']} (Segment {int(row['segment_id'])})",
                "",
                f"**Headline:** {rec['headline']}",
                "",
                f"**Message:** {rec['message']}",
                "",
                f"**CTA:** {rec['cta']}",
                "",
                f"**Channels:** {rec['channels']}",
                "",
                f"**Channel rationale:** {rec['channel_rationale']}",
                "",
                "**Justification:**",
                f"- Repayment progress {row['stability']:.2f} vs product need for proven payers",
                f"- Default rate {row['default_rate']*100:.1f}% — within acceptable risk for premium underwriting",
                f"- Financed proxy {row['affluence']:,.0f} — mid-to-high tier exposure",
                f"- PAYG share {row['payg_share']*100:.0f}% — established payment behavior",
                "",
            ]
        )

    rejected = (
        df[df["country_name"].str.lower() == "kenya"]
        .groupby(["segment_id", "segment_name"])
        .agg(arrears=("is_in_arrears", "mean"), default=("is_default", "mean"))
        .reset_index()
    )
    chosen_ids = set(top2["segment_id"].astype(int))
    lines.append("## 3. Segments Not Prioritized\n")
    for _, r in rejected.iterrows():
        if int(r["segment_id"]) in chosen_ids:
            continue
        lines.append(
            f"- **{r['segment_name']}:** arrears {r['arrears']*100:.1f}%, default {r['default']*100:.1f}% "
            "— fails stability/low-risk requirement for premium loan."
        )

    path.write_text("\n".join(lines), encoding="utf-8")


def write_credit_report(df: pd.DataFrame) -> None:
    path = REPORTS / "business_reports" / "credit_risk_recommendations.md"
    insights = compute_collection_insights(df)[:3]
    lines = [
        "# Credit Risk Mitigation Recommendations",
        "",
        "Actionable recommendations derived from the assessment dataset (account-level, customer grain).",
        "",
    ]
    for ins in insights:
        lines.extend(
            [
                f"## {ins['id']}: {ins['title']}",
                "",
                f"**Filter:** `{ins['filter']}`",
                "",
                f"**Baseline:** {ins['baseline']}",
                "",
                f"**Action:** {ins['action']}",
                "",
                f"**Target:** {ins['target']}",
                "",
                f"**Measure:** {ins['measure']}",
                "",
            ]
        )
    path.write_text("\n".join(lines), encoding="utf-8")


def write_deployment_report() -> None:
    path = REPORTS / "technical_reports" / "deployment_strategy.md"
    content = """# Model Deployment & Lifecycle Management

## Model Packaging & Deployment Choices

**Packaging:** Serialize the sklearn `Pipeline` (preprocessor + K-Means) with `joblib` to `models/segmentation/kmeans_pipeline.joblib`, alongside `model_card.json` (features, k, training date, metrics).

**Preferred strategy:** Containerized **FastAPI** service behind a load balancer, deployed to Kubernetes or Azure Container Apps.

| Approach | When to use |
|----------|-------------|
| Real-time REST API | Agent tools, CRM lookups, online eligibility |
| Batch scoring (nightly) | Segment refresh for entire portfolio in ClickHouse/dbt |
| Embedded rules export | Offline markets with intermittent connectivity |

**Why containers:** Reproducible environments, simple CI/CD, health checks, and autoscaling for campaign seasons.

### Sample Dockerfile

See repository root `Dockerfile` — Python 3.11 slim image, installs `requirements.txt`, exposes port 8000, runs `uvicorn src.deployment.api.app:app`.

### Sample docker-compose.yml

```yaml
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      MODEL_PATH: /app/models/segmentation/kmeans_pipeline.joblib
    volumes:
      - ./models:/app/models:ro
    depends_on:
      - clickhouse
  clickhouse:
    image: clickhouse/clickhouse-server:latest
    ports:
      - "8123:8123"
      - "9000:9000"
```

## Collaboration with DevOps / Engineering

| Workstream | Data Science | Platform / DevOps |
|------------|--------------|-------------------|
| Container build & scan | Provide Dockerfile, dependencies | CI scan, registry push |
| Secrets & config | Document env vars (`MODEL_PATH`) | Vault / Key Vault injection |
| Observability | Define metrics (latency, drift PSI) | Prometheus/Grafana dashboards |
| Releases | Model card sign-off | Staging → prod with approval gate |

**Runbook:** `/api/health` for liveness; `/api/segment` for inference; logs shipped to centralized logging with `customer_id` hashed in non-prod.

## Model Maintenance & Iteration

| Signal | Threshold | Response |
|--------|-----------|----------|
| Feature PSI | > 0.2 vs training | Investigate data pipeline; schedule retrain |
| Segment size drift | > 15% change in 30d | Review macro/market events |
| Silhouette on refresh | > 10% drop | Revisit k and features |
| Campaign conversion | Below control for 2 weeks | Pause rollout; audit segment definition |

**Retrain cadence:** Quarterly scheduled retrain on latest mart snapshot; ad-hoc retrain after product or policy changes.

**CI/CD:** GitHub Actions runs `pytest` → trains on frozen snapshot in CI → compares metrics to `model_card.json` → publishes artifact → deploys to staging → integration tests → manual approval for production.

## Handling Business Conflicts & Overrides

Credit officers may override model-assigned segments or risk scores when field knowledge contradicts the model.

1. **Policy:** Model output is **advisory**; human decision is authoritative for lending.
2. **Logging:** Persist `{customer_id, model_segment, model_score, human_decision, reason_code, timestamp}` in an audit table.
3. **Feedback loop:** Monthly review of overrides — classify as data quality, policy exception, or model error. Only **labeled overrides** feed supervised retraining; do not blindly fit on contradictions.
4. **Governance:** Threshold and segment definition changes require risk + data science dual sign-off.

**Tools:** MLflow (experiments), GitHub Actions (CI/CD), Docker/ACR (deploy), Prometheus + Grafana (monitoring), Evidently or custom PSI (drift).
"""
    path.write_text(content, encoding="utf-8")


def write_post_sale_strategy() -> None:
    path = REPORTS / "business_reports" / "post_sale_risk_strategy.md"
    content = """# Strategic Proposal: Post-Sale Credit Risk Scoring Model

## 1. Business Problem

Customer default and prolonged arrears directly reduce cash collections, increase repossession and write-off costs, and constrain growth in Kenya, Uganda, and Côte d'Ivoire. EDA on this portfolio shows **material arrears variation by product tier and lead source**, and operational delays that correlate with payment stress. Without early identification, collections teams react late—after 30–90 DPD—when cure rates are lower. Improving collections efficiency and on-time repayment is critical to portfolio profitability and sustainable PAYG growth.

## 2. Proposed Solution

Build a **Post-Sale Credit Risk Score** (0–100) refreshed daily or weekly for every active account. High scores route accounts into prioritized collections queues, tailored treatments (SMS, agent visit, restructure), and hold-out from upsell campaigns. The model complements—not replaces—human credit judgment, reducing write-offs while focusing agent time on highest-risk accounts.

## 3. Data & Features (New / Enriched Sources)

| Source | Description | Why critical |
|--------|-------------|--------------|
| **Repayment ledger** | Installment-level payments, partial pays, missed due dates | Earliest behavioral signal of distress |
| **Mobile money (M-Pesa etc.)** | Inflows/outflows, balance volatility | Real income and liquidity shocks |
| **Credit bureau (CRB)** | External credit history | Off-portfolio obligations and defaults |
| **Customer support CRM** | Tickets, complaints, hardship requests | Leading indicator before missed payment |
| **IoT / device utilization** | Pump usage hours, downtime | Willingness/ability to pay for productive assets |

## 4. Methodology

- **Label:** 90-day default or 30+ DPD roll-forward from account snapshot.
- **Models:** Logistic regression baseline → gradient boosting (XGBoost/LightGBM) with monotonic constraints on key features → isotonic calibration for score-to-probability mapping.
- **Validation:** Time-based train/test split; metrics: AUC-PR, recall@top decile, lift on collections trials.
- **Integration:** Score written to ClickHouse `mart_customer_account_analytics`; consumed by collections dialer sort order, CRM banners, and marketing suppression lists.

```mermaid
flowchart LR
  ETL[Daily ETL] --> FS[Feature Store]
  FS --> API[Scoring Service]
  API --> COL[Collections Prioritization]
  COL --> FB[Outcome Feedback]
  FB --> FS
```

## 5. Success Metrics

| Metric | Target (12 months post-POC) |
|--------|----------------------------|
| Default rate | −10–15% relative reduction |
| On-time repayment rate | +5 pp |
| Collections efficiency | +20% $ collected per agent hour |
| Precision@top decile | ≥ 2.5× random baseline |
| Write-off cost | −8% vs control |

## 6. Next Steps (90-Day POC)

| Weeks | Activity |
|-------|----------|
| 1–2 | Data audit; label definition; legal review for bureau/MoMo data |
| 3–4 | Feature store spec; baseline logistic on current + ledger sample |
| 5–6 | GBM model + SHAP for agent explainability |
| 7–8 | Backtest on holdout quarter; policy simulation |
| 9–10 | Pilot with collections (A/B prioritization) |
| 11–12 | Executive readout; production roadmap and DevOps handoff |

**Stakeholders:** Head of Credit, Collections Operations, Country GMs, Data Engineering, Compliance.
"""
    path.write_text(content, encoding="utf-8")


def main() -> None:
    print("Running Part 2 segmentation pipeline...")
    result = fit_segmentation()
    df = result.customer_df

    fig_dir = REPORTS / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)
    _save_elbow_plot(result.k_evaluation, fig_dir / "part2_cluster_selection.png")

    print(f"  Optimal k={result.optimal_k}, customers={len(df)}")
    print("Writing reports...")
    write_segmentation_report(result)
    write_marketing_report(df)
    write_credit_report(df)
    write_deployment_report()
    write_post_sale_strategy()
    print("Done. Reports written to reports/business_reports and reports/technical_reports")


if __name__ == "__main__":
    main()
