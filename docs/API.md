# ErgoVision API

## Base URL

```
http://localhost:8000
```

## Endpoints

### Health Check

```
GET /health
```

Response:
```json
{
  "status": "healthy",
  "camera_available": true,
  "model_loaded": true,
  "uptime_seconds": 342.1
}
```

### Current Posture

```
GET /api/posture/current
```

Response:
```json
{
  "score": 82,
  "status": "GOOD",
  "measurements": {
    "head_tilt_degrees": 4.2,
    "shoulder_alignment_score": 0.94,
    "shoulder_alignment_degrees": 3.1,
    "neck_offset": 0.05,
    "forward_head_indicator": 0.32,
    "gaze_vertical_degrees": 8.5
  },
  "feedback": ["Your posture looks good."],
  "timestamp": "2025-01-15T10:30:45.123Z",
  "person_detected": true
}
```

### Session Statistics

```
GET /api/session/stats
```

Response:
```json
{
  "session_duration_seconds": 1961,
  "good_duration_seconds": 1392,
  "warning_duration_seconds": 412,
  "bad_duration_seconds": 157,
  "good_percentage": 71.0,
  "warning_percentage": 21.0,
  "bad_percentage": 8.0,
  "warning_count": 14,
  "average_score": 78.5,
  "current_score": 82,
  "longest_poor_posture_seconds": 95
}
```

### Configuration

```
GET /api/config
```

Response:
```json
{
  "head_tilt_warning_degrees": 8.0,
  "head_tilt_bad_degrees": 15.0,
  "shoulder_alignment_warning_degrees": 5.0,
  "shoulder_alignment_bad_degrees": 10.0,
  "neck_offset_warning": 0.15,
  "neck_offset_bad": 0.30,
  "forward_head_warning": 0.6,
  "forward_head_bad": 0.8,
  "gaze_warning_degrees": 15.0,
  "gaze_bad_degrees": 25.0,
  "score_good_threshold": 70,
  "score_warning_threshold": 40,
  "smoothing_alpha": 0.3,
  "warning_frames_before_escalation": 30,
  "bad_frames_before_escalation": 60,
  "camera_index": 0,
  "frame_width": 640,
  "frame_height": 480,
  "target_fps": 30
}
```

### Camera Stream

```
GET /api/stream
```

Returns an MJPEG stream of annotated camera frames. Content-Type: multipart/x-mixed-replace; boundary=frame

### Processed Frame (single)

```
GET /api/stream/frame
```

Returns a single JPEG frame with landmarks drawn.

## WebSocket

### Posture Updates

```
WS /ws/posture
```

Receives real-time posture updates as JSON:

```json
{
  "score": 82,
  "status": "GOOD",
  "measurements": {
    "head_tilt_degrees": 4.2,
    "shoulder_alignment_score": 0.94,
    "shoulder_alignment_degrees": 3.1,
    "neck_offset": 0.05,
    "forward_head_indicator": 0.32,
    "gaze_vertical_degrees": 8.5
  },
  "feedback": ["Your posture looks good."],
  "timestamp": "2025-01-15T10:30:45.123Z",
  "person_detected": true
}
```

Updates are sent at approximately 10-15 Hz (every processed frame that differs
significantly from the last update).

## Error Responses

```json
{
  "detail": "Camera not available"
}
```

Status codes:
- 200: Success
- 503: Camera not available or model not loaded
