# Implementation Plan

## Milestone 0: Inspection and Planning ✅

### What was done
- Inspected empty git repository
- Verified Python 3.13.14, no Node.js installed
- Investigated MediaPipe 1.0.1 Tasks API (NOT legacy mp.solutions)
- Discovered `HolisticLandmarker`, `FaceLandmarker`, `PoseLandmarker`
- Installed Node.js 24.19.0 via winget
- Verified all dependency versions: mediapipe 1.0.1, opencv 5.0.0.93, numpy, fastapi, pytest

### Key findings
- MediaPipe 1.0.1 uses the new Tasks API exclusively
- `mp.solutions` does NOT exist in this version
- `NormalizedLandmark` has fields: x, y, z, visibility, presence (all Optional[float])
- `FaceLandmarker` and `PoseLandmarker` support LIVE_STREAM with async callbacks

## Milestone 1: Project Structure ✅

Created full directory structure with all modules.
Installed all Python and Node.js dependencies.

## Milestone 2: OpenCV Webcam Capture ✅

- `vision/camera.py`: Camera class with read, open, release, FPS tracking
- Handles camera unavailable gracefully (DEMO_MODE support)
- Targets configurable resolution and FPS

## Milestone 3: MediaPipe Landmark Detection ✅

- `vision/landmarks.py`: Landmark abstraction layer wrapping MediaPipe
- `Landmark2D` and `LandmarkSet` dataclasses
- Mapping from MediaPipe indices to semantic names
- `vision/detector.py`: Detector class orchestrating camera + MediaPipe
- `DemoLandmarkProvider` for deterministic simulation
- Face and pose detection run as separate async services
- Model files: face_landmarker.task + pose_landmarker_lite.task

## Milestone 4: Geometry Engine ✅

- `ergonomics/geometry.py`: Pure math functions
- `calculate_angle`, `calculate_distance`, `calculate_midpoint`, `clamp`, `normalize_value`
- `angle_from_horizontal`, `angle_from_vertical`
- Full unit test suite: 14 tests in `tests/test_geometry.py`

## Milestone 5: Ergonomic Measurements ✅

- `ergonomics/measurements.py`: ErgonomicMeasurements dataclass
- Head tilt, shoulder alignment, neck offset, forward head indicator, gaze vertical
- Graceful handling of missing landmarks
- 7 tests in `tests/test_measurements.py`

## Milestone 6: Temporal Smoothing ✅

- `ergonomics/smoothing.py`: Exponential Moving Average (EMA)
- Alpha=0.3, resets when person not detected
- 5 tests in `tests/test_smoothing.py`

## Milestone 7: Classification + Scoring ✅

- `ergonomics/classifier.py`: GOOD/WARNING/BAD with duration-based escalation
- Anti-oscillation: must sustain state for N frames before changing
- `ergonomics/scoring.py`: Weighted 0-100 score
  - Head tilt: 35 points
  - Shoulder: 25 points
  - Neck offset: 20 points
  - Forward head: 15 points
  - Gaze: 5 points
- 15 tests in `tests/test_scoring.py` + `tests/test_classifier.py`

## Milestone 8: Feedback Engine ✅

- `ergonomics/feedback.py`: Actionable messages based on measurements
- Priority system: BAD > WARNING > GOOD
- Messages are specific to what's wrong (head tilt, shoulders, neck offset, forward head)

## Milestone 9: Session Tracker ✅

- `session/tracker.py`: In-memory session statistics
- Duration tracking per state, percentage calculations
- Warning/bad count, longest poor posture period
- 6 tests in `tests/test_session.py`

## Milestone 10: FastAPI Backend ✅

- `api/routes.py`: REST endpoints (health, posture, session, config)
- `api/websocket.py`: WebSocket posture updates
- `api/schemas.py`: Pydantic response models
- `pipeline.py`: Full analysis pipeline running in background thread
- `main.py`: FastAPI app with lifespan, CORS, routes
- MJPEG stream endpoint for camera display
- 6 integration tests in `tests/test_api.py`

## Milestone 11: React Dashboard ✅

- TypeScript types, API service layer
- `usePostureSocket` hook with auto-reconnect
- Components: PostureScore, CameraFeed, Metrics, Feedback, SessionPanel
- Dark theme, responsive layout
- Vite dev server with proxy to backend

## Milestone 12: Integration ✅

- Full flow: Backend (MJPEG + WebSocket + REST) ↔ Frontend
- Vite proxies WebSocket, API, and stream to backend
- IPv6/IPv4 binding resolved (127.0.0.1)

## Milestone 13: Demo Mode ✅

- `DEMO_MODE=1` environment variable
- `DemoLandmarkProvider`: deterministic cycle through GOOD/WARNING/BAD
- 40-second cycle: head tilt, shoulder offset, forward head variations
- Full pipeline runs with simulated landmarks

## Milestone 14: Polish and Testing ✅

- All 55 tests pass (14 geometry + 7 measurements + 5 smoothing + 8 scoring + 6 classifier + 6 session + 6 API + 3 WebSocket)
- Documentation complete (README, ARCHITECTURE, ERGONOMIC_MODEL, API, AGENTS.md)
- Error handling throughout: no crashes on missing landmarks, camera unavailable
- Clean architecture: math is testable independently of API/camera

## What is included at ~60% completion

| Feature | Status |
|---------|--------|
| Webcam capture | ✅ |
| MediaPipe landmark detection | ✅ |
| Live landmark visualization | ✅ |
| Ergonomic measurements | ✅ |
| Temporal smoothing | ✅ |
| Posture classification | ✅ |
| Posture scoring (0-100) | ✅ |
| Feedback engine | ✅ |
| Session statistics | ✅ |
| FastAPI backend | ✅ |
| React dashboard | ✅ |
| Frontend/backend integration | ✅ |
| Demo mode | ✅ |
| Core unit tests | ✅ |
| README | ✅ |
| Architecture docs | ✅ |

## Known limitations

- Camera not available on this development machine; demo mode used for all integration testing
- 2D webcam only; true 3D posture estimation not possible
- No calibration for distance estimation
- Single-person use only

## Future improvements (post-prototype)

- Real-time landmark visualization with bone connections
- Historical posture charts over time
- Posture reminders/alerts
- Side-view camera option
- Mobile companion app
- User profiles and session history
