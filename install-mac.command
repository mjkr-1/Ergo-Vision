#!/bin/bash
set -euo pipefail

SOURCE="$(cd "$(dirname "$0")" && pwd)"
DEST="$HOME/Library/Application Support/ErgoVision"

echo "Installing ErgoVision for macOS"
echo "Install location: $DEST"
echo

if [ "$SOURCE" != "$DEST" ]; then
  mkdir -p "$DEST"
  rsync -a --delete \
    --exclude '.git' \
    --exclude '.venv' \
    --exclude 'frontend/node_modules' \
    "$SOURCE/" "$DEST/"
fi

cd "$DEST"
bash scripts/setup_mac.sh
bash scripts/install_mac_app.sh

echo
echo "ErgoVision installed successfully."
open "$HOME/Applications/ErgoVision.app"
