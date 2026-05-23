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
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Development

- `docker-compose up --build` to start the API service.
- `pytest` to run tests.
- `python -m src.deployment.api.app` to run the FastAPI app locally.

## Notes

This scaffold includes placeholder datasets, model artifacts, notebooks, and documentation to support rapid project handoff and iterative development.
