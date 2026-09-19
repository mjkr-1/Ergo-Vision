# Troubleshooting

## Run the doctor first

```bash
bash scripts/doctor_mac.sh
```

## Camera unavailable on macOS

If logs show `not authorized to capture video` or `Cannot open camera 0`:

1. Open **System Settings → Privacy & Security → Camera**.
2. Allow the terminal application you use to launch ErgoVision.
3. Stop ErgoVision completely with Ctrl+C.
4. Start it again with `bash scripts/run_mac.sh`.

If another application is using the webcam, close it and retry.

## Port 8000 already in use

```bash
lsof -nP -iTCP:8000 -sTCP:LISTEN
```

Run on another port:

```bash
PORT=8001 bash scripts/run_mac.sh
```

## Camera stays on after Ctrl+Z

Ctrl+Z normally suspends terminal processes rather than exiting them. The current launcher traps that signal and attempts to release the backend cleanly, but older running copies may remain suspended.

```bash
jobs
fg %1
```

Then press Ctrl+C.

As a last resort for a stale local ErgoVision process:

```bash
pkill -f "uvicorn app.main:app"
```

## MediaPipe model download fails with SSL certificate errors

Rerun setup after updating the repository:

```bash
bash scripts/setup_mac.sh
```

The Python model downloader uses the `certifi` CA bundle, and setup falls back to `curl` if needed.

## Frontend does not load

```bash
cd frontend
npm ci
npm run build
```

Then restart the backend.

## Backend works but dashboard says offline

```bash
curl http://127.0.0.1:8000/health
```

If health responds but WebSocket state remains offline, refresh the browser and inspect Terminal for WebSocket errors.
