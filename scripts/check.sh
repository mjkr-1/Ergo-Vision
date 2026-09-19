#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV="$ROOT/.venv"

if [ ! -f "$VENV/bin/activate" ]; then
  echo "Virtual environment missing. Run: bash scripts/setup_mac.sh"
  exit 1
fi

source "$VENV/bin/activate"

printf "\n== Backend tests ==\n"
(
  cd "$ROOT/backend"
  DEMO_MODE=1 python -m pytest tests/ -v
)

printf "\n== Frontend build ==\n"
(
  cd "$ROOT/frontend"
  npm run build
)

printf "\nAll checks passed.\n"
