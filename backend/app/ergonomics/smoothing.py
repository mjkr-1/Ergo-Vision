from dataclasses import dataclass, field

from ..config import SMOOTHING_ALPHA
from .measurements import ErgonomicMeasurements


@dataclass
class SmoothingBuffer:
    alpha: float = SMOOTHING_ALPHA
    _prev: ErgonomicMeasurements | None = field(default=None, repr=False)

    def smooth(self, new: ErgonomicMeasurements) -> ErgonomicMeasurements:
        if not new.person_detected:
            self._prev = None
            return new

        if self._prev is None or not self._prev.person_detected:
            self._prev = new
            return new

        a = self.alpha
        prev = self._prev

        smoothed = ErgonomicMeasurements(
            head_tilt_degrees=a * new.head_tilt_degrees + (1 - a) * prev.head_tilt_degrees,
            shoulder_alignment_score=a * new.shoulder_alignment_score + (1 - a) * prev.shoulder_alignment_score,
            shoulder_alignment_degrees=a * new.shoulder_alignment_degrees + (1 - a) * prev.shoulder_alignment_degrees,
            neck_offset=a * new.neck_offset + (1 - a) * prev.neck_offset,
            forward_head_indicator=a * new.forward_head_indicator + (1 - a) * prev.forward_head_indicator,
            gaze_vertical_degrees=a * new.gaze_vertical_degrees + (1 - a) * prev.gaze_vertical_degrees,
            person_detected=True,
        )

        self._prev = smoothed
        return smoothed

    def reset(self):
        self._prev = None
