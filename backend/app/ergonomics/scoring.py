from dataclasses import dataclass

from ..config import (
    FORWARD_HEAD_BAD,
    FORWARD_HEAD_WARNING,
    GAZE_BAD_DEGREES,
    GAZE_WARNING_DEGREES,
    HEAD_TILT_BAD_DEGREES,
    HEAD_TILT_WARNING_DEGREES,
    NECK_OFFSET_BAD,
    NECK_OFFSET_WARNING,
    SCORE_WEIGHT_FORWARD_HEAD,
    SCORE_WEIGHT_GAZE,
    SCORE_WEIGHT_HEAD_TILT,
    SCORE_WEIGHT_NECK_OFFSET,
    SCORE_WEIGHT_SHOULDER,
    SCORE_WEIGHT_SLOUCH,
    SCORE_WEIGHT_TORSO_LEAN,
    SHOULDER_ALIGNMENT_BAD_DEGREES,
    SHOULDER_ALIGNMENT_WARNING_DEGREES,
    SLOUCH_BAD,
    SLOUCH_WARNING,
    TORSO_LEAN_BAD_DEGREES,
    TORSO_LEAN_WARNING_DEGREES,
)
from .geometry import clamp, normalize_value
from .measurements import ErgonomicMeasurements


@dataclass
class ScoreBreakdown:
    head_tilt_penalty: float = 0.0
    shoulder_penalty: float = 0.0
    neck_offset_penalty: float = 0.0
    forward_head_penalty: float = 0.0
    gaze_penalty: float = 0.0
    torso_lean_penalty: float = 0.0
    slouch_penalty: float = 0.0


def compute_score(measurement: ErgonomicMeasurements) -> tuple[int, ScoreBreakdown]:
    if not measurement.person_detected:
        return 0, ScoreBreakdown()

    breakdown = ScoreBreakdown(
        head_tilt_penalty=_penalty(measurement.head_tilt_degrees, HEAD_TILT_WARNING_DEGREES, HEAD_TILT_BAD_DEGREES) * SCORE_WEIGHT_HEAD_TILT,
        shoulder_penalty=_penalty(measurement.shoulder_alignment_degrees, SHOULDER_ALIGNMENT_WARNING_DEGREES, SHOULDER_ALIGNMENT_BAD_DEGREES) * SCORE_WEIGHT_SHOULDER,
        neck_offset_penalty=_penalty(abs(measurement.neck_offset), NECK_OFFSET_WARNING, NECK_OFFSET_BAD) * SCORE_WEIGHT_NECK_OFFSET,
        forward_head_penalty=_penalty(measurement.forward_head_indicator, FORWARD_HEAD_WARNING, FORWARD_HEAD_BAD) * SCORE_WEIGHT_FORWARD_HEAD,
        gaze_penalty=_penalty(measurement.gaze_vertical_degrees, GAZE_WARNING_DEGREES, GAZE_BAD_DEGREES) * SCORE_WEIGHT_GAZE,
        torso_lean_penalty=_penalty(measurement.torso_lean_degrees, TORSO_LEAN_WARNING_DEGREES, TORSO_LEAN_BAD_DEGREES) * SCORE_WEIGHT_TORSO_LEAN,
        slouch_penalty=_penalty(measurement.slouch_indicator, SLOUCH_WARNING, SLOUCH_BAD) * SCORE_WEIGHT_SLOUCH,
    )

    total_penalty = sum(breakdown.__dict__.values())
    return int(round(clamp(100 - total_penalty, 0, 100))), breakdown


def _penalty(value: float, warning: float, bad: float) -> float:
    if abs(value) <= warning:
        return 0.0
    if abs(value) >= bad:
        return 1.0
    return normalize_value(abs(value), warning, bad)
