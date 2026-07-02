#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON="${ROOT_DIR}/.venv/bin/python"

if [ ! -x "${PYTHON}" ]; then
  echo "Missing virtualenv Python at ${PYTHON}. Run the README installation commands first." >&2
  exit 1
fi

export PYTHONPATH="${ROOT_DIR}/mcp_server:${PYTHONPATH:-}"
cd "${ROOT_DIR}"
exec "${PYTHON}" mcp_server/server.py
