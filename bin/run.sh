#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [ ! -x .venv/bin/uvicorn ]; then python3 -m venv .venv; .venv/bin/pip install -r requirements.txt; fi
[ -f .env ] && { set -a; . ./.env; set +a; }
exec .venv/bin/uvicorn app.main:app --host 127.0.0.1 --port "${PORT:-8094}"
