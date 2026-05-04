#!/usr/bin/env sh

set -eu

APP_MODULE="${APP_MODULE:-app.main:app}"
HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-8000}"

if [ -d ".venv" ]; then
    # shellcheck disable=SC1091
    . ".venv/bin/activate"
    echo "Activated virtual environment: .venv"
else
    echo "Virtual environment .venv not found; using current shell environment."
fi

if ! command -v uvicorn >/dev/null 2>&1; then
    echo "Error: uvicorn is not installed in the active environment." >&2
    echo "Install dependencies with: pip install -r requirements.txt" >&2
    exit 1
fi

echo "Starting ${APP_MODULE} in debug mode at http://${HOST}:${PORT}"
exec uvicorn "${APP_MODULE}" --host "${HOST}" --port "${PORT}" --reload --log-level debug
