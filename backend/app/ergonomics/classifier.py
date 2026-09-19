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
    WARNING_FRAMES_BEFORE_ESCALATION,
    BAD_FRAMES_BEFORE_ESCALATION,
)
from .measurements import ErgonomicMeasurements


class PostureClassifier:
    def __init__(self):
        self._warning_streak = 0
        self._bad_streak = 0
        self._current_status = "UNKNOWN"

    def classify(self, m: ErgonomicMeasurements) -> str:
        if not m.person_detected:
            self._warning_streak = 0
            self._bad_streak = 0
            self._current_status = "NO_PERSON"
            return "NO_PERSON"

        _SEVERITY = {"GOOD": 0, "WARNING": 1, "BAD": 2}

        head_tilt_severity = self._check_threshold(m.head_tilt_degrees, HEAD_TILT_WARNING_DEGREES, HEAD_TILT_BAD_DEGREES)
        shoulder_severity = self._check_threshold(m.shoulder_alignment_degrees, SHOULDER_ALIGNMENT_WARNING_DEGREES, SHOULDER_ALIGNMENT_BAD_DEGREES)
        neck_severity = self._check_threshold(abs(m.neck_offset), NECK_OFFSET_WARNING, NECK_OFFSET_BAD)
        forward_severity = self._check_threshold(m.forward_head_indicator, FORWARD_HEAD_WARNING, FORWARD_HEAD_BAD)
        gaze_severity = self._check_threshold(m.gaze_vertical_degrees, GAZE_WARNING_DEGREES, GAZE_BAD_DEGREES)

        worst = max(
            (head_tilt_severity, shoulder_severity, neck_severity, forward_severity, gaze_severity),
            key=lambda s: _SEVERITY[s],
        )

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
