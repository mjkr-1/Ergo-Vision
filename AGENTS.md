# ErgoVision - Agent Instructions

## Project Overview

ErgoVision is a privacy-focused, webcam-based screen ergonomics and posture monitoring application. It uses OpenCV + MediaPipe Tasks API for landmark detection, geometric analysis for ergonomic measurements, and a FastAPI + React stack for real-time feedback.

## Environment

- Python 3.11+
- MediaPipe 1.0.1 Tasks API
- OpenCV 5.0.0.93 via opencv-contrib-python
- Node.js 18+
- Supported local targets: macOS and Windows

## MediaPipe

Do not use the legacy `mp.solutions` API.

ErgoVision currently runs `FaceLandmarker` and `PoseLandmarker` in live-stream mode and merges their landmarks. Model bundles live under `backend/app/models/`, are ignored by Git, and are provisioned by `app.vision.models`.

## Running Tests

```bash
cd backend
python -m pytest tests/ -v
```

## Running Backend

```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

## Running Frontend During Development

```bash
cd frontend
npm install
npm run dev
```

## Mac Setup

```bash
bash scripts/setup_mac.sh
bash scripts/run_mac.sh
```

## Code Style

- No comments unless explicitly asked
- No unnecessary abstractions
- Keep math testable and separate from API routes
- Use Pydantic models for API responses
- Handle missing landmarks gracefully
- Keep camera capture single-owner; consumers should use cached frames from the pipeline
