#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FRONTEND_DIR="${ROOT_DIR}/frontend"

if [ ! -d "${FRONTEND_DIR}/node_modules" ]; then
  echo "Missing frontend/node_modules. Run npm install in ${FRONTEND_DIR} first." >&2
  exit 1
fi

export NEXT_PUBLIC_API_BASE_URL="${NEXT_PUBLIC_API_BASE_URL:-http://127.0.0.1:8000}"
exec npm --prefix "${FRONTEND_DIR}" run dev -- --hostname 127.0.0.1 --port "${PORT:-3000}"
