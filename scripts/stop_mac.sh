#!/usr/bin/env bash
set -euo pipefail

STATE_DIR="$HOME/.ergovision"
PIDFILE="$STATE_DIR/app.pid"
PORT="${PORT:-8000}"

if [ -f "$PIDFILE" ]; then
  PID="$(cat "$PIDFILE" 2>/dev/null || true)"
  if [ -n "$PID" ] && kill -0 "$PID" >/dev/null 2>&1; then
    kill -TERM "$PID" >/dev/null 2>&1 || true
    for _ in 1 2 3 4 5 6 7 8 9 10; do
      if ! kill -0 "$PID" >/dev/null 2>&1; then
        break
      fi
      sleep 0.2
    done
    if kill -0 "$PID" >/dev/null 2>&1; then
      kill -KILL "$PID" >/dev/null 2>&1 || true
    fi
  fi
  rm -f "$PIDFILE"
fi

if command -v lsof >/dev/null 2>&1; then
  PIDS="$(lsof -tiTCP:"$PORT" -sTCP:LISTEN 2>/dev/null || true)"
  if [ -n "$PIDS" ]; then
    echo "$PIDS" | xargs kill -TERM 2>/dev/null || true
  fi
fi

echo "ErgoVision stopped and camera resources released."
