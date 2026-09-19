#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV="$ROOT/.venv"
PORT="${PORT:-8000}"

if [ ! -f "$VENV/bin/activate" ]; then
  echo "ErgoVision is not set up yet. Run: bash scripts/setup_mac.sh"
  exit 1
fi

source "$VENV/bin/activate"
cd "$ROOT/backend"

(
  sleep 1.5
  open "http://127.0.0.1:$PORT" >/dev/null 2>&1 || true
) &

exec python -m uvicorn app.main:app --host 127.0.0.1 --port "$PORT"
