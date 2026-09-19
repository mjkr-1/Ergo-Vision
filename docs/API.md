# API Reference

Base URL for local use: `http://127.0.0.1:8000`

Interactive OpenAPI documentation: `http://127.0.0.1:8000/docs`

## Health

### `GET /health`

```json
{
  "status": "healthy",
  "camera_available": true,
  "model_loaded": true,
  "demo_mode": false,
  "uptime_seconds": 342.1,
  "fps": 29.8
}
```

## Current posture

### `GET /api/posture/current`

Returns score, status, measurements, feedback, timestamp and person detection state.

Status values are `GOOD`, `WARNING`, `BAD` and `NO_PERSON`.

## Session

### `GET /api/session/stats`

Returns duration by posture state, percentages, counts, average/current score, longest poor-posture interval and whether session accounting is active.

### `POST /api/session/start`

Resumes session accounting.

### `POST /api/session/stop`

Pauses session accounting.

### `POST /api/session/reset`

Clears session statistics and starts a fresh session.

## Configuration

### `GET /api/config`

Returns runtime ergonomic and capture configuration.

## Camera stream

### `GET /api/stream`

Returns an MJPEG stream of the most recent annotated frame.

### `GET /api/stream/frame`

Returns the latest annotated JPEG frame with `Cache-Control: no-store`.

## WebSocket

### `WS /ws/posture`

Streams the same posture event shape returned by `/api/posture/current`. The frontend automatically reconnects after temporary disconnects.

## Errors

FastAPI errors use the standard shape:

```json
{
  "detail": "Pipeline not initialized"
}
```

Typical status codes are `200`, `404` and `503`.
