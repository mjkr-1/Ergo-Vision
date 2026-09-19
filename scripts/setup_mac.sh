#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV="$ROOT/.venv"

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
python -m pip install -r "$ROOT/backend/requirements.txt"

(
  cd "$ROOT/frontend"
  npm install
  npm run build
)

(
  cd "$ROOT/backend"
  python -m app.vision.models
)

echo
echo "ErgoVision setup is complete."
echo "Start it with: bash scripts/run_mac.sh"
