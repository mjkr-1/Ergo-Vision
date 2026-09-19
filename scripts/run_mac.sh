#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV="$ROOT/.venv"

if [ -f "$ROOT/.env" ]; then
  set -a
  source "$ROOT/.env"
  set +a
fi

PORT="${PORT:-8000}"
SERVER_PID=""

if [ ! -f "$VENV/bin/activate" ]; then
  echo "ErgoVision is not set up yet. Run: bash scripts/setup_mac.sh"
  exit 1
fi

if command -v lsof >/dev/null 2>&1 && lsof -tiTCP:"$PORT" -sTCP:LISTEN >/dev/null 2>&1; then
  echo "Port $PORT is already in use."
  echo "Inspect it with: lsof -nP -iTCP:$PORT -sTCP:LISTEN"
  echo "Or run ErgoVision on another port: PORT=8001 bash scripts/run_mac.sh"
  exit 1
fi

cleanup() {
  if [ -n "${SERVER_PID:-}" ] && kill -0 "$SERVER_PID" >/dev/null 2>&1; then
    kill -CONT "$SERVER_PID" >/dev/null 2>&1 || true
    kill -TERM "$SERVER_PID" >/dev/null 2>&1 || true
    for _ in 1 2 3 4 5; do
      if ! kill -0 "$SERVER_PID" >/dev/null 2>&1; then
        break
      fi
      sleep 0.1
    done
    if kill -0 "$SERVER_PID" >/dev/null 2>&1; then
      kill -KILL "$SERVER_PID" >/dev/null 2>&1 || true
    fi
    wait "$SERVER_PID" 2>/dev/null || true
  fi
}

on_signal() {
  cleanup
  exit 130
}

trap on_signal INT TERM HUP TSTP
trap cleanup EXIT

source "$VENV/bin/activate"
cd "$ROOT/backend"

python -m uvicorn app.main:app --host 127.0.0.1 --port "$PORT" &
SERVER_PID=$!

(
  sleep 1.5
  open "http://127.0.0.1:$PORT" >/dev/null 2>&1 || true
) &

set +e
wait "$SERVER_PID"
STATUS=$?
set -e
SERVER_PID=""
trap - EXIT INT TERM HUP TSTP
exit "$STATUS"
