# ErgoVision - Agent Instructions

## Project overview

ErgoVision is a privacy-focused, webcam-based screen ergonomics and posture monitoring application. It uses OpenCV + MediaPipe Tasks API for landmark detection, geometric analysis for ergonomic measurements, and a FastAPI + React stack for real-time feedback.

## Supported development environment

- Python 3.11+
- MediaPipe 0.10.21 Tasks API
- OpenCV Contrib 4.11.0.86
- NumPy 1.26.4
- Node.js 18+
- Primary local target: macOS

## MediaPipe

Do not use the legacy `mp.solutions` API in new code.

ErgoVision runs `FaceLandmarker` and `PoseLandmarker` in live-stream mode and merges their landmarks. Model bundles live under `backend/app/models/`, are ignored by Git, and are provisioned by `app.vision.models`.

## Setup

```bash
bash scripts/setup_mac.sh
```

## Run

```bash
bash scripts/run_mac.sh
```

## Validate

```bash
bash scripts/check.sh
```

Backend tests:

```bash
source .venv/bin/activate
cd backend
python -m pytest tests/ -v
```

Frontend build:

```bash
cd frontend
npm run build
```

## Engineering rules

- Keep camera capture single-owner; consumers use cached pipeline frames.
- Keep ergonomic math testable and separate from API routes.
- Handle missing landmarks and unavailable hardware gracefully.
- Use Pydantic models for API responses.
- Keep frontend TypeScript contracts aligned with backend schemas.
- Preserve the local-first privacy model.
- Do not commit generated MediaPipe `.task` files.
- Update tests and docs when behaviour or API contracts change.
- Avoid unnecessary abstractions and unrelated refactors.
