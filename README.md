# ErgoVision

A privacy-focused, webcam-based screen ergonomics and posture monitoring application.

## What It Does

ErgoVision uses your laptop webcam to monitor your posture while you work. It
provides real-time feedback to help you maintain healthy sitting habits.

**This is NOT a medical diagnostic system.** It provides ergonomic indicators,
not clinical assessments.

## Features

- Real-time posture monitoring via webcam
- Head tilt detection
- Shoulder alignment analysis
- Forward-head posture indicator
- Posture scoring (0-100)
- Actionable feedback messages
- Session statistics tracking
- Live camera feed with landmark overlay
- Demo mode for testing without a camera

## Privacy

- All processing happens locally on your machine
- No webcam data is uploaded anywhere
- No footage is saved to disk
- No external AI services are used
- Session data is held in memory only

## Prerequisites

- Python 3.11+
- Node.js 18+
- A webcam
- Good lighting

## Installation

### Backend

```bash
cd backend
pip install -r requirements.txt
```

### Frontend

```bash
cd frontend
npm install
```

## Running

### Backend

```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm run dev
```

Open http://localhost:5173 in your browser.

### Demo Mode

Set the `DEMO_MODE` environment variable:

```bash
cd backend
set DEMO_MODE=1
python -m uvicorn app.main:app --reload --port 8000
```

Demo mode uses simulated landmark data to demonstrate the full pipeline
without requiring a camera.

## Running Tests

```bash
cd backend
python -m pytest tests/ -v
```

## Architecture

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the full architecture.

```
Webcam → OpenCV → MediaPipe → Landmarks → Measurements → Smoothing
    → Classification → Scoring → Feedback → FastAPI → React Dashboard
```

## Limitations

- A standard webcam provides 2D image information only
- True 3D posture cannot be measured without depth sensors
- Distance estimates are approximate
- Single-person use only
- Lighting conditions affect accuracy
- This is a prototype, not a clinical tool

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Computer Vision | OpenCV + MediaPipe |
| Backend API | FastAPI + Uvicorn |
| Frontend | React + Vite + TypeScript |
| Geometry | NumPy |

## License

MIT
