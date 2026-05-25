# Methodology

## Part 2 — Predictive Modelling

### Pipeline

1. **Ingest** — Excel assessment workbook (`data/raw/Senior_Data_Scientist_Assessment_Data*.xlsx`) or ClickHouse mart.
2. **Join** — `src/data/joins.py` builds account-level then customer-level tables.
3. **Features** — `src/features/*` engineers segmentation, risk, and behavioral variables.
4. **Segment** — `src/models/pipelines/segmentation_pipeline.py` fits preprocessor + K-Means; saves artifacts to `models/segmentation/`.
5. **Report** — `scripts/run_part2_pipeline.py` writes business and technical reports under `reports/`.

### Reproducibility

```powershell
python3.11 scripts/run_part2_pipeline.py
pytest
docker compose up --build api
```

### Deliverables map

| Task | Notebook | Report |
|------|----------|--------|
| 2.1 Segmentation | `notebooks/04_customer_segmentation.ipynb` | `reports/business_reports/segmentation_report.md` |
| 2.2 Marketing | `notebooks/05_marketing_strategy.ipynb` | `reports/business_reports/marketing_strategy.md` |
| 2.3 Deployment | — | `reports/technical_reports/deployment_strategy.md` |
| 2.4 Credit insights | `notebooks/06_credit_risk_analysis.ipynb` | `reports/business_reports/credit_risk_recommendations.md` |
| 2.5 Risk strategy | — | `reports/business_reports/post_sale_risk_strategy.md` |
