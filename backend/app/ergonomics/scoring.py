from dataclasses import dataclass

from ..config import (
    HEAD_TILT_WARNING_DEGREES,
    HEAD_TILT_BAD_DEGREES,
    SHOULDER_ALIGNMENT_WARNING_DEGREES,
    SHOULDER_ALIGNMENT_BAD_DEGREES,
    NECK_OFFSET_WARNING,
    NECK_OFFSET_BAD,
    FORWARD_HEAD_WARNING,
    FORWARD_HEAD_BAD,
    GAZE_WARNING_DEGREES,
    GAZE_BAD_DEGREES,
    SCORE_WEIGHT_HEAD_TILT,
    SCORE_WEIGHT_SHOULDER,
    SCORE_WEIGHT_NECK_OFFSET,
    SCORE_WEIGHT_FORWARD_HEAD,
    SCORE_WEIGHT_GAZE,
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


def compute_score(m: ErgonomicMeasurements) -> tuple[int, ScoreBreakdown]:
    if not m.person_detected:
        return 0, ScoreBreakdown()

    breakdown = ScoreBreakdown(
        head_tilt_penalty=_penalty(m.head_tilt_degrees, HEAD_TILT_WARNING_DEGREES, HEAD_TILT_BAD_DEGREES) * SCORE_WEIGHT_HEAD_TILT,
        shoulder_penalty=_penalty(m.shoulder_alignment_degrees, SHOULDER_ALIGNMENT_WARNING_DEGREES, SHOULDER_ALIGNMENT_BAD_DEGREES) * SCORE_WEIGHT_SHOULDER,
        neck_offset_penalty=_penalty(abs(m.neck_offset), NECK_OFFSET_WARNING, NECK_OFFSET_BAD) * SCORE_WEIGHT_NECK_OFFSET,
        forward_head_penalty=_penalty(m.forward_head_indicator, FORWARD_HEAD_WARNING, FORWARD_HEAD_BAD) * SCORE_WEIGHT_FORWARD_HEAD,
        gaze_penalty=_penalty(m.gaze_vertical_degrees, GAZE_WARNING_DEGREES, GAZE_BAD_DEGREES) * SCORE_WEIGHT_GAZE,
    )

    total_penalty = (
        breakdown.head_tilt_penalty
        + breakdown.shoulder_penalty
        + breakdown.neck_offset_penalty
        + breakdown.forward_head_penalty
        + breakdown.gaze_penalty
    )

    return int(round(clamp(100 - total_penalty, 0, 100))), breakdown


def _penalty(value: float, warning: float, bad: float) -> float:
    if abs(value) <= warning:
        return 0.0
    if abs(value) >= bad:
        return 1.0
    return normalize_value(abs(value), warning, bad)