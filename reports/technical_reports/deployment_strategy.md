# Model Deployment & Lifecycle Management

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
