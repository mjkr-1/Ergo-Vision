#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV="$ROOT/.venv"
MODELS="$ROOT/backend/app/models"

if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3 is required. Install Python 3.11+ and run this script again."
  exit 1
fi

if ! command -v node >/dev/null 2>&1 || ! command -v npm >/dev/null 2>&1; then
  echo "Node.js and npm are required. Install Node.js 18+ and run this script again."
  exit 1
fi

python3 - <<'PY'
import sys
if sys.version_info < (3, 11):
    raise SystemExit("Python 3.11 or newer is required.")
PY

if [ ! -d "$VENV" ]; then
  python3 -m venv "$VENV"
fi

source "$VENV/bin/activate"
python -m pip install --upgrade pip
python -m pip install -r "$ROOT/backend/requirements-dev.txt"

(
  cd "$ROOT/frontend"
  npm ci
  npm run build
)

mkdir -p "$MODELS"
if ! (
  cd "$ROOT/backend"
  python -m app.vision.models
); then
  if ! command -v curl >/dev/null 2>&1; then
    echo "Model download failed and curl is unavailable. See docs/TROUBLESHOOTING.md."
    exit 1
  fi

  echo "Python model download failed; retrying with curl..."
  curl -L --fail --retry 3 \
    "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/latest/face_landmarker.task" \
    -o "$MODELS/face_landmarker.task"
  curl -L --fail --retry 3 \
    "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/latest/pose_landmarker_lite.task" \
    -o "$MODELS/pose_landmarker_lite.task"
fi

for model in face_landmarker.task pose_landmarker_lite.task; do
  if [ ! -s "$MODELS/$model" ]; then
    echo "Missing MediaPipe model: $MODELS/$model"
    exit 1
  fi
done

echo
echo "ErgoVision setup is complete."
echo "Run diagnostics: bash scripts/doctor_mac.sh"
echo "Start ErgoVision: bash scripts/run_mac.sh"
