#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APP="$HOME/Applications/ErgoVision.app"

"$ROOT/scripts/stop_mac.sh" || true
rm -rf "$APP"
echo "Removed $APP"
