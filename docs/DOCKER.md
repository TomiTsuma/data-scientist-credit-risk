# Docker deployment

Run the full stack locally: **ClickHouse** (schema + Excel load), **FastAPI** (`src/ai_platform` + deployment API), and **React UI** (`src/ui`).

## Prerequisites

- Docker Desktop (or Docker Engine + Compose v2)
- Optional: `OPENAI_API_KEY` for live AI chat (set in `.env` or shell)

## Quick start

```powershell
cd C:\Users\tsuma.thomas\Documents\Sunculture
docker compose up --build
```

| Service | URL |
|---------|-----|
| UI | http://localhost:8080 |
| API | http://localhost:8000 |
| API docs | http://localhost:8000/docs |
| ClickHouse HTTP | http://localhost:8123 |

On first boot, `db-init` runs once:

1. Applies `src/sql/01_dimension_tables.sql` and `02_fact_tables.sql`
2. Loads `data/raw/Senior_Data_Scientist_Assessment_Data*.xlsx` (same logic as `notebooks/01_data_understanding.ipynb`)
3. Builds analytical marts via `scripts/populate_marts.py`
4. Writes `data/processed/customer_features_base.parquet` for the AI platform

## Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | (empty) | OpenAI key for streaming chat |
| `SUNAI_PROVIDER` | `openai` | LLM provider |
| `SUNAI_MODEL` | `gpt-4o-mini` | Model id |
| `CLICKHOUSE_HOST` | `clickhouse` | Set automatically in Compose |

## Push to Docker Hub

```powershell
$env:DOCKERHUB_USER = "your-dockerhub-username"
.\scripts\docker-push.ps1
```

Images published:

- `{user}/sunculture-api:latest`
- `{user}/sunculture-ui:latest`
- `{user}/sunculture-db-init:latest`

After push, others can run API/UI images and provide their own ClickHouse + init, or use the full `docker-compose.yml` from this repo.

## Re-load data

```powershell
docker compose run --rm db-init
```

Or reset ClickHouse volume:

```powershell
docker compose down -v
docker compose up --build
```
