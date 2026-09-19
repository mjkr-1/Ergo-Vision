# ErgoVision - Agent Instructions

## Project Overview

ErgoVision is a privacy-focused, webcam-based screen ergonomics and posture monitoring application. It uses OpenCV + MediaPipe (Tasks API v1.0.1) for landmark detection, geometric analysis for ergonomic measurements, and a FastAPI + React stack for real-time feedback.

## Environment

- **Python**: 3.13.14
- **MediaPipe**: 1.0.1 (Tasks API, NOT the legacy `mp.solutions` API)
- **OpenCV**: 5.0.0.93 (via opencv-contrib-python)
- **Node.js**: 24.19.0 / npm 11.17.0
- **OS**: Windows 10/11

## Key MediaPipe Facts

MediaPipe 1.0.1 uses the **Tasks API**. The old `mp.solutions` module does NOT exist.

```python
import mediapipe as mp
# Correct: mp.tasks.vision.FaceLandmarker, PoseLandmarker, HolisticLandmarker
# Wrong:   mp.solutions.face_mesh, mp.solutions.pose (DOES NOT EXIST)
```

We use `HolisticLandmarker` for combined face + pose detection in a single pass.

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

## Running Frontend

```bash
cd frontend
npm install
npm run dev
```

## Code Style

- No comments unless explicitly asked
- No unnecessary abstractions
- Keep math testable and separate from API routes
- Use Pydantic models for API responses
- Handle missing landmarks gracefully (never crash)
