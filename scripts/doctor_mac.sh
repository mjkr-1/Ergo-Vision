#!/usr/bin/env bash
set -u

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV="$ROOT/.venv"
MODELS="$ROOT/backend/app/models"
FAILED=0

pass() { printf "✓ %s\n" "$1"; }
warn() { printf "! %s\n" "$1"; }
fail() { printf "✗ %s\n" "$1"; FAILED=1; }

printf "ErgoVision macOS doctor\n\n"

if command -v python3 >/dev/null 2>&1; then
  pass "python3: $(python3 --version 2>&1)"
else
  fail "python3 not found"
fi

if command -v node >/dev/null 2>&1; then
  pass "node: $(node --version)"
else
  fail "Node.js not found"
fi

if command -v npm >/dev/null 2>&1; then
  pass "npm: $(npm --version)"
else
  fail "npm not found"
fi

if [ -f "$VENV/bin/activate" ]; then
  pass "virtual environment exists"
  source "$VENV/bin/activate"
  if python - <<'PY' >/dev/null 2>&1
import cv2
import fastapi
import mediapipe
import numpy
import uvicorn
PY
  then
    pass "Python runtime imports succeeded"
  else
    fail "Python runtime imports failed; rerun scripts/setup_mac.sh"
  fi
else
  fail "virtual environment missing; run scripts/setup_mac.sh"
fi

if [ -f "$ROOT/frontend/dist/index.html" ]; then
  pass "frontend production build exists"
else
  fail "frontend build missing; run scripts/setup_mac.sh"
fi

for model in face_landmarker.task pose_landmarker_lite.task; do
  if [ -s "$MODELS/$model" ]; then
    size=$(wc -c < "$MODELS/$model" | tr -d ' ')
    pass "$model present (${size} bytes)"
  else
    fail "$model missing or empty"
  fi
done

PORT="${PORT:-8000}"
if command -v lsof >/dev/null 2>&1 && lsof -tiTCP:"$PORT" -sTCP:LISTEN >/dev/null 2>&1; then
  warn "port $PORT is already in use"
else
  pass "port $PORT is available"
fi

printf "\n"
if [ "$FAILED" -eq 0 ]; then
  echo "Environment looks ready."
else
  echo "One or more checks failed. See docs/TROUBLESHOOTING.md."
fi

exit "$FAILED"
