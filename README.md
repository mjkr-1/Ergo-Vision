# ErgoVision

ErgoVision is a privacy-focused, webcam-based ergonomics and posture monitoring app. It runs locally, analyzes face and pose landmarks with MediaPipe, and shows live posture feedback in a React dashboard.

**ErgoVision is not a medical diagnostic system.** It provides ergonomic indicators and reminders, not clinical assessments.

## Features

- Real-time webcam posture monitoring
- Head tilt, shoulder alignment, neck offset, forward-head and gaze indicators
- 0-100 posture score with GOOD / WARNING / BAD states
- Live landmark overlay
- Actionable posture feedback
- Session timing, posture percentages and average score
- Pause, resume and reset session controls
- Demo mode when a camera is unavailable
- Automatic MediaPipe model download
- Single-server production mode after the frontend is built
- Local-only processing with no footage saved to disk

## Mac Quick Start

Requirements:

- macOS
- Python 3.11+
- Node.js 18+
- A webcam

Clone and set up:

```bash
git clone https://github.com/mjkr-1/Ergo-Vision.git
cd Ergo-Vision
bash scripts/setup_mac.sh
```

Run:

```bash
bash scripts/run_mac.sh
```

The app opens at:

```text
http://127.0.0.1:8000
```

On the first real-camera run, macOS may ask Terminal or Python for camera permission. If the camera is unavailable, open **System Settings → Privacy & Security → Camera** and allow the terminal application you are using.

## MediaPipe Models

The `.task` model files are intentionally not stored in Git. ErgoVision downloads the official Face Landmarker and Pose Landmarker Lite model bundles during Mac setup and also attempts to provision them automatically on first backend startup.

To disable automatic downloads:

```bash
AUTO_DOWNLOAD_MODELS=0 python -m uvicorn app.main:app --port 8000
```

## Development Mode

Backend:

```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Then open `http://127.0.0.1:5173`.

## Demo Mode

macOS / Linux:

```bash
cd backend
DEMO_MODE=1 python -m uvicorn app.main:app --reload --port 8000
```

Windows PowerShell:

```powershell
cd backend
$env:DEMO_MODE="1"
python -m uvicorn app.main:app --reload --port 8000
```

Demo mode generates local simulated landmarks and does not need a webcam or model files.

## Tests

```bash
cd backend
python -m pytest tests/ -v
```

Frontend production build:

```bash
cd frontend
npm run build
```

## Architecture

```text
Webcam
  ↓
OpenCV capture
  ↓
MediaPipe face + pose landmarks
  ↓
Measurements → smoothing → classification → score → feedback
  ↓
FastAPI
  ├─ REST API
  ├─ WebSocket posture updates
  └─ cached MJPEG stream
  ↓
React dashboard
```

The posture pipeline is the only webcam consumer. It caches the latest annotated JPEG so the dashboard stream cannot compete with posture analysis for camera frames.

## Privacy

- Webcam processing runs locally
- Camera frames are not uploaded
- Footage is not saved
- No external inference API is used
- Session statistics stay in memory and reset when the app exits
- Network access is only needed when installing dependencies or downloading the MediaPipe model bundles

## Important Deployment Note

The current architecture intentionally reads the webcam from the machine running the Python backend. That makes ErgoVision a local application. Hosting this backend on a remote cloud server would make it look for a camera on that server rather than on the visitor's laptop.

If you later want a public hosted website, the camera-capture layer should be moved into the browser and frames or landmarks should be processed client-side or sent to an explicitly designed backend.

## Environment Variables

| Variable | Default | Purpose |
|---|---:|---|
| `DEMO_MODE` | `0` | Use simulated data instead of real CV |
| `AUTO_DOWNLOAD_MODELS` | `1` | Download missing MediaPipe models |
| `CAMERA_INDEX` | `0` | OpenCV camera index |
| `FRAME_WIDTH` | `640` | Capture width |
| `FRAME_HEIGHT` | `480` | Capture height |
| `TARGET_FPS` | `30` | Analysis capture target |
| `STREAM_FPS` | `15` | Dashboard MJPEG stream target |
| `CORS_ORIGINS` | local Vite origins | Allowed development origins |

## Limitations

- Standard webcams provide 2D image information only
- Forward-head and distance indicators are approximations
- Lighting and camera angle affect landmark accuracy
- Single-person monitoring only
- This is an ergonomics tool, not a clinical device

## License

MIT
