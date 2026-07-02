#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON="${ROOT_DIR}/.venv/bin/python"

if [ ! -x "${PYTHON}" ]; then
  echo "Missing virtualenv Python at ${PYTHON}. Run the README installation commands first." >&2
  exit 1
fi

export PYTHONPATH="${ROOT_DIR}/backend:${ROOT_DIR}/mcp_server:${PYTHONPATH:-}"
exec "${PYTHON}" -m uvicorn app.main:app --host 127.0.0.1 --port "${PORT:-8000}" --app-dir "${ROOT_DIR}/backend"
