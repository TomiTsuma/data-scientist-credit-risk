# Sunculture — multi-stage image (db-init + API)
FROM python:3.11-slim-bookworm AS python-base

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    CLICKHOUSE_HOST=clickhouse \
    CLICKHOUSE_PORT=9000 \
    CLICKHOUSE_USER=clickhouse_user \
    CLICKHOUSE_PASSWORD=clickhouse_password \
    CLICKHOUSE_DB=sunculture_db

# One-shot: create schema + load Excel + build marts
FROM python-base AS db-init
ENTRYPOINT ["/bin/sh", "docker/entrypoint-db-init.sh"]

# Long-running FastAPI (ai_platform + deployment routes)
FROM python-base AS api
EXPOSE 8000
ENTRYPOINT ["/bin/sh", "docker/entrypoint-api.sh"]
