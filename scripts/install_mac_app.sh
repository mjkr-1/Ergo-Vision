#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APP_ROOT="$HOME/Applications"
APP="$APP_ROOT/ErgoVision.app"
CONTENTS="$APP/Contents"
MACOS="$CONTENTS/MacOS"
RESOURCES="$CONTENTS/Resources"
STATE="$HOME/.ergovision"

if [ ! -f "$ROOT/scripts/run_mac.sh" ]; then
  echo "Could not locate ErgoVision at $ROOT"
  exit 1
fi

mkdir -p "$APP_ROOT" "$MACOS" "$RESOURCES" "$STATE"
rm -rf "$APP"
mkdir -p "$MACOS" "$RESOURCES"

ROOT_ESCAPED="$(printf '%q' "$ROOT")"

cat > "$MACOS/ErgoVision" <<LAUNCHER
#!/usr/bin/env bash
set -euo pipefail
ROOT=$ROOT_ESCAPED
STATE="\$HOME/.ergovision"
PIDFILE="\$STATE/app.pid"
LOGFILE="\$STATE/ergovision.log"
PORT="\${PORT:-8000}"
mkdir -p "\$STATE"

if command -v lsof >/dev/null 2>&1 && lsof -tiTCP:"\$PORT" -sTCP:LISTEN >/dev/null 2>&1; then
  open "http://127.0.0.1:\$PORT"
  exit 0
fi

cd "\$ROOT"
bash scripts/run_mac.sh >>"\$LOGFILE" 2>&1 &
RUN_PID=\$!
echo "\$RUN_PID" > "\$PIDFILE"

cleanup() {
  if kill -0 "\$RUN_PID" >/dev/null 2>&1; then
    kill -TERM "\$RUN_PID" >/dev/null 2>&1 || true
    wait "\$RUN_PID" 2>/dev/null || true
  fi
  rm -f "\$PIDFILE"
}
trap cleanup EXIT INT TERM HUP

wait "\$RUN_PID"
LAUNCHER
chmod +x "$MACOS/ErgoVision"

cat > "$CONTENTS/Info.plist" <<'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>CFBundleDevelopmentRegion</key>
  <string>en</string>
  <key>CFBundleDisplayName</key>
  <string>ErgoVision</string>
  <key>CFBundleExecutable</key>
  <string>ErgoVision</string>
  <key>CFBundleIdentifier</key>
  <string>io.ergovision.local</string>
  <key>CFBundleInfoDictionaryVersion</key>
  <string>6.0</string>
  <key>CFBundleName</key>
  <string>ErgoVision</string>
  <key>CFBundlePackageType</key>
  <string>APPL</string>
  <key>CFBundleShortVersionString</key>
  <string>1.1</string>
  <key>CFBundleVersion</key>
  <string>1</string>
  <key>LSMinimumSystemVersion</key>
  <string>12.0</string>
  <key>NSCameraUsageDescription</key>
  <string>ErgoVision uses the camera locally to estimate ergonomic posture. Video is not uploaded or saved.</string>
</dict>
</plist>
PLIST

if command -v plutil >/dev/null 2>&1; then
  plutil -lint "$CONTENTS/Info.plist" >/dev/null
fi

printf '\nErgoVision.app installed at:\n%s\n\n' "$APP"
echo "Open Finder → Applications in your Home folder, or run:"
echo "open \"$APP\""
echo
echo "To remove it: bash scripts/uninstall_mac_app.sh"
