from ..config import (
    BAD_FRAMES_BEFORE_ESCALATION,
    FORWARD_HEAD_BAD,
    FORWARD_HEAD_WARNING,
    GAZE_BAD_DEGREES,
    GAZE_WARNING_DEGREES,
    HEAD_TILT_BAD_DEGREES,
    HEAD_TILT_WARNING_DEGREES,
    NECK_OFFSET_BAD,
    NECK_OFFSET_WARNING,
    SHOULDER_ALIGNMENT_BAD_DEGREES,
    SHOULDER_ALIGNMENT_WARNING_DEGREES,
    SLOUCH_BAD,
    SLOUCH_WARNING,
    TORSO_LEAN_BAD_DEGREES,
    TORSO_LEAN_WARNING_DEGREES,
    WARNING_FRAMES_BEFORE_ESCALATION,
)
from .measurements import ErgonomicMeasurements


class PostureClassifier:
    def __init__(self):
        self._warning_streak = 0
        self._bad_streak = 0
        self._current_status = "UNKNOWN"

    def classify(self, measurement: ErgonomicMeasurements) -> str:
        if not measurement.person_detected:
            self._warning_streak = 0
            self._bad_streak = 0
            self._current_status = "NO_PERSON"
            return "NO_PERSON"

        severity = {"GOOD": 0, "WARNING": 1, "BAD": 2}
        checks = (
            self._check_threshold(measurement.head_tilt_degrees, HEAD_TILT_WARNING_DEGREES, HEAD_TILT_BAD_DEGREES),
            self._check_threshold(measurement.shoulder_alignment_degrees, SHOULDER_ALIGNMENT_WARNING_DEGREES, SHOULDER_ALIGNMENT_BAD_DEGREES),
            self._check_threshold(abs(measurement.neck_offset), NECK_OFFSET_WARNING, NECK_OFFSET_BAD),
            self._check_threshold(measurement.forward_head_indicator, FORWARD_HEAD_WARNING, FORWARD_HEAD_BAD),
            self._check_threshold(measurement.gaze_vertical_degrees, GAZE_WARNING_DEGREES, GAZE_BAD_DEGREES),
            self._check_threshold(measurement.slouch_indicator, SLOUCH_WARNING, SLOUCH_BAD),
        )
        worst = max(checks, key=lambda value: severity[value])

        if worst == "BAD":
            self._bad_streak += 1
            self._warning_streak += 1
            if self._bad_streak >= BAD_FRAMES_BEFORE_ESCALATION:
                self._current_status = "BAD"
            elif self._warning_streak >= WARNING_FRAMES_BEFORE_ESCALATION:
                self._current_status = "WARNING"
        elif worst == "WARNING":
            self._warning_streak += 1
            self._bad_streak = 0
            if self._warning_streak >= WARNING_FRAMES_BEFORE_ESCALATION:
                self._current_status = "WARNING"
        else:
            self._warning_streak = 0
            self._bad_streak = 0
            self._current_status = "GOOD"

        return self._current_status

    def _check_threshold(self, value: float, warning: float, bad: float) -> str:
        if abs(value) >= bad:
            return "BAD"
        if abs(value) >= warning:
            return "WARNING"
        return "GOOD"

    def reset(self):
        self._warning_streak = 0
        self._bad_streak = 0
        self._current_status = "UNKNOWN"
