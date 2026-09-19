# Ergonomic Model

## Measurements

All measurements are derived from 2D image-space landmarks. They are geometric
indicators, not clinical measurements.

### 1. Head Tilt (Lateral)

**What**: How much the head is tilted left/right relative to vertical.

**Method**: Compute the angle between the line connecting left-eye-outer and
right-eye-outer relative to horizontal. Alternatively, use the nose-to-midpoint
of eyes relative to vertical.

**Output**: Angle in degrees. 0 = perfectly upright.

**Thresholds**: Warning at ~8 degrees, Bad at ~15 degrees.

### 2. Shoulder Alignment

**What**: How level the shoulders are.

**Method**: Compare the Y-coordinates of left and right shoulder landmarks.
Compute the angular difference from horizontal.

**Output**: Alignment score (0-1 where 1 = perfectly level) and angle in degrees.

**Thresholds**: Warning at ~5 degrees difference, Bad at ~10 degrees.

### 3. Head-Shoulder Center Offset (Neck Posture)

**What**: Whether the head is centered over the shoulders or leaning.

**Method**: Compute the horizontal offset between the nose landmark and the
midpoint of the two shoulders, normalized by shoulder width.

**Output**: Normalized offset (-1 to 1, where 0 = centered).

**Thresholds**: Warning at ~0.15 offset, Bad at ~0.30 offset.

### 4. Forward Head Indicator

**What**: Whether the head appears to be jutting forward.

**Method**: Use the apparent size of the face relative to shoulder width as a
proxy. A larger face-to-shoulder ratio may indicate the head is closer to the
camera (forward). Also use the vertical position of the chin relative to
shoulders.

**Note**: This is a 2D approximation. True forward-head posture requires depth
information or calibrated side-view analysis.

**Output**: Forward indicator score (0-1).

**Thresholds**: Warning at ~0.6, Bad at ~0.8.

### 5. Gaze Vertical Indicator

**What**: Whether the user is looking down at the screen excessively.

**Method**: Use the vertical position of the iris/eye landmarks relative to
the nose to estimate gaze direction.

**Output**: Vertical gaze angle in degrees.

**Thresholds**: Warning at ~15 degrees below horizontal, Bad at ~25 degrees.

## Scoring

The posture score is a 0-100 integer derived from weighted penalties:

```
score = 100
  - head_tilt_penalty      (max 35)
  - shoulder_penalty       (max 25)
  - neck_offset_penalty    (max 20)
  - forward_head_penalty   (max 15)
  - gaze_penalty           (max 5)
```

Each penalty scales linearly from 0 (good) to its maximum (bad).

The final score is clamped to [0, 100].

### Weight Rationale

- Head tilt and shoulder alignment are the most observable indicators
- Neck offset and forward head are important but harder to measure precisely
- Gaze is supplementary

These are prototype weights and should be tuned based on user testing.

## Classification

| Score Range | Status |
|-------------|--------|
| 70-100 | GOOD |
| 40-69 | WARNING |
| 0-39 | BAD |

With optional duration-based escalation: sustained WARNING for >60 seconds
escalates to BAD.

## Temporal Smoothing

Exponential Moving Average (EMA) with alpha=0.3:

```
smoothed = alpha * new_value + (1 - alpha) * previous_smoothed
```

Applied to each measurement independently. This reduces frame-to-frame jitter
without introducing significant lag. Alpha=0.3 provides ~3 frame responsiveness.

Classification uses an additional hysteresis mechanism: the status must remain
different for at least `POSTURE_WARNING_FRAMES` or `POSTURE_BAD_FRAMES`
consecutive frames before the classification changes.
