#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON="${ROOT_DIR}/.venv/bin/python"

if [ ! -x "${PYTHON}" ]; then
  echo "Missing virtualenv Python at ${PYTHON}. Run the README installation commands first." >&2
  exit 1
fi

cd "${ROOT_DIR}"
"${PYTHON}" -m pytest -q
npm --prefix "${ROOT_DIR}/frontend" run typecheck
