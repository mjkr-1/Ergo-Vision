# Ergonomic Model

## Scope

ErgoVision derives ergonomic indicators from 2D image-space landmarks. These values are designed for real-time posture feedback, not clinical measurement.

## Measurements

### Head tilt

The line between the outer eye landmarks is compared with the horizontal axis. The absolute angle is reported in degrees.

Default thresholds: warning at 8°, bad at 15°.

### Shoulder alignment

The line between shoulder landmarks is compared with the horizontal axis. ErgoVision exposes both the angular difference and a normalized alignment score.

Default thresholds: warning at 5°, bad at 10°.

### Neck offset

The horizontal position of the nose is compared with the midpoint of both shoulders and normalized by shoulder width.

Default thresholds: warning at 0.15, bad at 0.30.

### Forward-head indicator

Because a normal webcam does not provide reliable metric depth, ErgoVision uses apparent face size relative to shoulder width as a proxy. This is an indicator rather than a physical distance measurement.

Default thresholds: warning at 0.60, bad at 0.80.

### Vertical gaze indicator

The forehead-to-nose orientation is used as a supplementary indicator for looking downward.

Default thresholds: warning at 15°, bad at 25°.

## Score

The 0–100 score starts at 100 and subtracts weighted penalties once a measurement moves beyond its warning threshold.

```text
head tilt        max 35 points
shoulder angle   max 25 points
neck offset      max 20 points
forward head     max 15 points
gaze              max 5 points
```

Each penalty scales linearly between warning and bad thresholds.

## Classification

GOOD / WARNING / BAD classification is not a simple score-range lookup. The classifier examines the worst threshold severity across current measurements and applies temporal streaks before escalating posture state.

By default, warning-level measurements must persist for 30 processed frames before WARNING and bad-level measurements for 60 processed frames before BAD. A good frame resets escalation streaks. Missing-person state produces `NO_PERSON`.

## Temporal smoothing

ErgoVision applies an exponential moving average:

```text
smoothed = alpha × new + (1 - alpha) × previous
```

The default alpha is 0.3. Smoothing resets when no person is detected.

## Limitations

- 2D landmarks cannot measure true spinal curvature or physical camera distance.
- Perspective and webcam placement affect apparent geometry.
- Lighting and occlusion affect landmark quality.
- Thresholds are prototype ergonomic heuristics and have not been clinically validated.
- The system is designed for one visible user at a time.
