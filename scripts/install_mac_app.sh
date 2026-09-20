#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APP="$HOME/Applications/ErgoVision.app"; STATE="$HOME/.ergovision"
rm -rf "$APP"; mkdir -p "$APP/Contents/MacOS" "$APP/Contents/Resources" "$STATE"
ROOT_ESCAPED="$(printf '%q' "$ROOT")"
cat > "$APP/Contents/MacOS/ErgoVision" <<LAUNCHER
#!/bin/bash
set -u
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
ROOT=$ROOT_ESCAPED; STATE="\$HOME/.ergovision"; LOGFILE="\$STATE/ergovision.log"; PIDFILE="\$STATE/app.pid"; PORT="\${PORT:-8000}"
mkdir -p "\$STATE"
if /usr/sbin/lsof -tiTCP:"\$PORT" -sTCP:LISTEN >/dev/null 2>&1; then /usr/bin/open "http://127.0.0.1:\$PORT"; exit 0; fi
cd "\$ROOT" || exit 1
ERGOVISION_NO_AUTO_OPEN=1 /usr/bin/nohup /bin/bash scripts/run_mac.sh >>"\$LOGFILE" 2>&1 & RUN_PID=\$!; echo "\$RUN_PID" > "\$PIDFILE"
for _ in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15; do if /usr/sbin/lsof -tiTCP:"\$PORT" -sTCP:LISTEN >/dev/null 2>&1; then /usr/bin/open "http://127.0.0.1:\$PORT"; exit 0; fi; /bin/sleep .4; done
/usr/bin/osascript -e 'display dialog "ErgoVision could not start. Check ~/.ergovision/ergovision.log." buttons {"OK"} default button "OK" with icon caution' >/dev/null 2>&1 || true
exit 1
LAUNCHER
chmod +x "$APP/Contents/MacOS/ErgoVision"
cat > "$APP/Contents/Info.plist" <<'PLIST'
<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd"><plist version="1.0"><dict><key>CFBundleDisplayName</key><string>ErgoVision</string><key>CFBundleExecutable</key><string>ErgoVision</string><key>CFBundleIdentifier</key><string>io.ergovision.local</string><key>CFBundlePackageType</key><string>APPL</string><key>CFBundleShortVersionString</key><string>1.2</string><key>CFBundleVersion</key><string>2</string><key>LSMinimumSystemVersion</key><string>12.0</string><key>LSUIElement</key><true/><key>NSCameraUsageDescription</key><string>ErgoVision uses the camera locally to estimate ergonomic posture.</string></dict></plist>
PLIST
plutil -lint "$APP/Contents/Info.plist" >/dev/null
xattr -dr com.apple.quarantine "$APP" >/dev/null 2>&1 || true
codesign --force --deep --sign - "$APP" >/dev/null 2>&1 || true
echo "Installed: $APP"
