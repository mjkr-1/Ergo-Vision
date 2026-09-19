# ErgoVision Architecture

## Overview

ErgoVision is a layered, privacy-focused application that processes webcam video locally to provide real-time ergonomic posture feedback.

## Layers

```
┌─────────────────────────────────────────┐
│            React Dashboard              │
│  (Vite + TypeScript)                    │
│  - Posture score display                │
│  - Live camera feed (MJPEG)             │
│  - Ergonomic metrics                    │
│  - Feedback messages                    │
│  - Session statistics                   │
└────────────┬────────────────────────────┘
             │ HTTP / WebSocket
┌────────────┴────────────────────────────┐
│           FastAPI Backend               │
│  - REST endpoints (health, config,      │
│    posture, session stats)              │
│  - WebSocket (real-time posture data)   │
│  - MJPEG camera stream                 │
└────────────┬────────────────────────────┘
             │
┌────────────┴────────────────────────────┐
│         Posture Analysis Pipeline       │
│  1. Camera capture (OpenCV)             │
│  2. Landmark detection (MediaPipe)      │
│  3. Landmark abstraction                │
│  4. Geometric measurements              │
│  5. Temporal smoothing                  │
│  6. Posture classification              │
│  7. Posture scoring                     │
│  8. Feedback generation                 │
│  9. Session tracking                    │
└─────────────────────────────────────────┘
```

## Camera Display Decision

**Chosen approach: Option A (Python-side capture + MJPEG streaming)**

The Python backend captures the webcam, runs MediaPipe, draws landmarks on the
annotated frame, and streams processed frames via an MJPEG endpoint. The React
frontend displays this stream via an `<img>` tag pointing at the stream URL.

Rationale:
- All CV processing stays in Python (no need to ship models to browser)
- MJPEG is natively supported by browsers via `<img>` tag
- Simple to implement and debug
- Acceptable latency for a prototype (~100-200ms)
- Privacy: processed frames never leave the local machine

The alternative (browser captures webcam, sends frames to backend) was rejected
because it adds complexity without benefit for a local-only application.

## Privacy Design

- All processing happens locally on the user's machine
- No webcam data is uploaded to any server
- No raw webcam footage is stored to disk
- No external CV APIs are used
- No database is used in the prototype
- Session data is held in memory only

## Module Responsibilities

| Module | Responsibility |
|--------|---------------|
| `vision/camera.py` | OpenCV webcam capture, frame management |
| `vision/landmarks.py` | Landmark abstraction layer (wraps MediaPipe) |
| `vision/detector.py` | Orchestrates camera + landmark detection |
| `ergonomics/geometry.py` | Pure math functions (angle, distance, midpoint) |
| `ergonomics/measurements.py` | Ergonomic measurements from landmarks |
| `ergonomics/scoring.py` | 0-100 posture score from measurements |
| `ergonomics/classifier.py` | GOOD/WARNING/BAD classification |
| `session/tracker.py` | In-memory session statistics |
| `api/routes.py` | FastAPI REST endpoints |
| `api/websocket.py` | WebSocket for real-time updates |
| `config.py` | All thresholds and configuration |

## Limitations

- A 2D webcam cannot measure true 3D posture or spinal curvature
- Distance estimates are approximations, not calibrated measurements
- The system provides ergonomic indicators, not medical diagnosis
- Model accuracy depends on lighting and camera angle
- Single-person use only
