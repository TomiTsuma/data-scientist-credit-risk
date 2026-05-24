# Strategic Proposal: Post-Sale Credit Risk Scoring Model

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
