#!/bin/sh
set -e
echo "==> Starting Sunculture API on port 8000"
exec uvicorn src.deployment.api.app:app --host 0.0.0.0 --port 8000
