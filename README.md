# Sunculture Senior Data Scientist Assessment

This repository is structured to support an end-to-end analytics platform for customer segmentation, marketing strategy, credit risk modeling, and an AI self-service capability.

## Structure

- `data/` — raw, interim, and processed datasets.
- `notebooks/` — exploratory analysis, feature engineering, segmentation, credit risk, evaluation, and AI platform proof-of-concept notebooks.
- `src/` — reusable data ingestion, feature engineering, modeling, deployment, monitoring, and AI platform code.
- `reports/` — business, technical, and executive artifacts.
- `models/` — serialized model and feature store artifacts.
- `tests/` — unit and integration test coverage.
- `docs/` — architecture, methodology, assumptions, and improvement recommendations.

## Quick start

```powershell
python3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Development

- `python3.11 scripts/run_part2_pipeline.py` — build segmentation, artifacts, and Part 2 reports.
- `docker-compose up --build` to start ClickHouse + API (`POST /api/segment`).
- `pytest` to run tests.
- `python3.11 -m uvicorn src.deployment.api.app:app --reload --port 8000` to run the FastAPI app locally.

### AI assistant (streaming + MCP)

- `POST /api/ai/v1/chat/stream` — SSE chat (see `src/ai_platform/`)
- `python3.11 scripts/test_streaming.py "Your question"`
- Set `OPENAI_API_KEY` before using OpenAI provider

### Part 2 deliverables

| Task | Report |
|------|--------|
| 2.1 Segmentation | `reports/business_reports/segmentation_report.md` |
| 2.2 Marketing | `reports/business_reports/marketing_strategy.md` |
| 2.3 Deployment | `reports/technical_reports/deployment_strategy.md` |
| 2.4 Credit insights | `reports/business_reports/credit_risk_recommendations.md` |
| 2.5 Risk strategy | `reports/business_reports/post_sale_risk_strategy.md` |

## Notes

This scaffold includes placeholder datasets, model artifacts, notebooks, and documentation to support rapid project handoff and iterative development.

### Manual Clickhouse setup
- Get-Content C:\Users\tsuma.thomas\Documents\Sunculture\src\sql\01_dimension_tables.sql | docker exec -i sunculture_clickhouse clickhouse-client --multiquery
- Get-Content C:\Users\tsuma.thomas\Documents\Sunculture\src\sql\02_fact_tables.sql | docker exec -i sunculture_clickhouse clickhouse-client --multiquery
- Get-Content C:\Users\tsuma.thomas\Documents\Sunculture\src\sql\03_clickhouse_dictionaries.sql | docker exec -i sunculture_clickhouse clickhouse-client --multiquery
- Get-Content C:\Users\tsuma.thomas\Documents\Sunculture\src\sql\04_analytical_marts.sql | docker exec -i sunculture_clickhouse clickhouse-client --multiquery