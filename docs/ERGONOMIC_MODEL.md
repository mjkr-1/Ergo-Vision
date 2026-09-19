# Ergonomic Model

## Scope

ErgoVision derives ergonomic indicators from webcam landmarks for real-time feedback. These values are ergonomic heuristics, not clinical measurements.

A standard webcam cannot directly measure spinal curvature. ErgoVision therefore combines face, shoulder and hip geometry with MediaPipe depth estimates and a personal neutral calibration to detect visible slouching and forward collapse more reliably.

## Measurements

### Head tilt

The line between the outer eye landmarks is compared with the horizontal axis.

Default thresholds: warning at 8°, bad at 15°.

### Shoulder alignment

The line between both shoulders is compared with the horizontal axis.

Default thresholds: warning at 5°, bad at 10°.

### Neck offset

The horizontal nose position is compared with the midpoint of both shoulders and normalized by shoulder width.

Default thresholds: warning at 0.15, bad at 0.30.

### Forward-head indicator

Apparent face size relative to shoulder width is used as a depth proxy. This is an indicator rather than a physical distance measurement.

Default thresholds: warning at 0.60, bad at 0.80.

### Vertical gaze indicator

The forehead-to-nose orientation provides a supplementary indication of looking downward.

Default thresholds: warning at 15°, bad at 25°.

### Torso lean

When both hips are visible, ErgoVision compares the shoulder midpoint to the hip midpoint and measures lateral deviation from vertical.

Default thresholds: warning at 8°, bad at 15°.

### Slouch / hunch indicator

The slouch indicator combines several upper-body signals:

- projected shoulder-to-hip length normalized by shoulder width
- head-to-shoulder vertical separation
- relative shoulder-versus-hip depth from MediaPipe pose landmarks
- change in the forward-head indicator

The result is normalized to 0–1. A higher value means the current geometry has moved further toward a collapsed/forward posture.

Default thresholds: warning at 0.35, bad at 0.70.

## Personal calibration

The dashboard includes a calibration action. The user sits in a normal upright position for a few seconds and ErgoVision averages recent valid measurements into a local baseline.

Calibration improves slouch detection because camera height, body proportions and normal neutral posture differ between users. The profile is stored locally under `~/.ergovision/calibration.json` and contains measurements only, never images.

For best results, shoulders must be visible. Keeping the hips visible lets ErgoVision use torso geometry as well.

## Score

The 0–100 score starts at 100 and subtracts weighted penalties once a measurement moves beyond its warning threshold.

```text
head tilt        max 20 points
shoulder angle   max 15 points
neck offset      max 15 points
forward head     max 15 points
gaze              max 5 points
torso lean       max 10 points
slouch / hunch   max 20 points
```

Each penalty scales linearly between warning and bad thresholds.

## Classification

GOOD / WARNING / BAD classification examines the worst threshold severity across current measurements and requires poor posture to persist before escalation.

By default, warning-level measurements must persist for 30 processed frames before WARNING and bad-level measurements for 60 processed frames before BAD. Good posture resets the escalation streak. Missing-person state produces `NO_PERSON`.

## Temporal smoothing

ErgoVision applies an exponential moving average:

```text
smoothed = alpha × new + (1 - alpha) × previous
```

The default alpha is 0.3. Smoothing resets when no person is detected.

## Limitations

- A front-facing 2D webcam cannot directly observe true spinal curvature.
- Slouch detection is based on visible posture proxies, not an anatomical spine model.
- Hip visibility substantially improves torso analysis.
- Camera placement, clothing, lighting and occlusion affect landmark quality.
- MediaPipe depth values are relative estimates, not metric depth measurements.
- Thresholds are ergonomic heuristics and have not been clinically validated.
- ErgoVision is designed for one visible user at a time.
