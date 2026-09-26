from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, replace
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, median, pstdev

from .geometry import clamp
from .measurements import ErgonomicMeasurements, estimate_slouch

DATA_DIR = Path(os.environ.get("ERGOVISION_DATA_DIR", str(Path.home() / ".ergovision")))
CALIBRATION_PATH = DATA_DIR / "calibration.json"


@dataclass
class CalibrationProfile:
    calibrated: bool = False
    captured_at: str | None = None
    torso_length_ratio: float = 0.0
    head_shoulder_gap_ratio: float = 0.0
    torso_depth_ratio: float = 0.0
    forward_head_indicator: float = 0.0
    head_tilt_degrees: float = 0.0
    shoulder_alignment_degrees: float = 0.0
    neck_offset: float = 0.0
    gaze_vertical_degrees: float = 0.0
    torso_lean_degrees: float = 0.0
    samples: int = 0

    @classmethod
    def load(cls) -> "CalibrationProfile":
        try:
            data = json.loads(CALIBRATION_PATH.read_text(encoding="utf-8"))
            return cls(**data)
        except (OSError, ValueError, TypeError):
            return cls()

    def capture(self, samples: list[ErgonomicMeasurements]) -> None:
        # Hips are intentionally not required. A normal laptop user often
        # has only the head, face and shoulders visible.
        valid = [
            sample
            for sample in samples
            if sample.person_detected
            and sample.head_shoulder_gap_ratio > 0
        ]

        if len(valid) < 20:
            raise ValueError(
                "Calibration needs a stable view of your head and shoulders. "
                "Sit upright and hold still for 2–3 seconds."
            )

        gaps = [sample.head_shoulder_gap_ratio for sample in valid]
        forward = [sample.forward_head_indicator for sample in valid]

        head_tilts = [
            getattr(
                sample,
                "head_tilt_signed_degrees",
                sample.head_tilt_degrees,
            )
            for sample in valid
        ]

        shoulder_angles = [
            getattr(
                sample,
                "shoulder_alignment_signed_degrees",
                sample.shoulder_alignment_degrees,
            )
            for sample in valid
        ]

        neck_offsets = [sample.neck_offset for sample in valid]
        gaze_angles = [sample.gaze_vertical_degrees for sample in valid]

        # Reject only genuinely unstable upper-body calibration.
        if (
            _relative_variation(gaps) > 0.12
            or pstdev(forward) > 0.12
            or pstdev(head_tilts) > 4.0
            or pstdev(shoulder_angles) > 4.0
        ):
            raise ValueError(
                "Too much movement was detected. Sit upright, hold still, "
                "and try calibration again."
            )

        self.calibrated = True
        self.captured_at = datetime.now(timezone.utc).isoformat()

        # Torso/hip geometry is intentionally excluded.
        self.torso_length_ratio = 0.0
        self.torso_depth_ratio = 0.0

        self.head_shoulder_gap_ratio = median(gaps)
        self.forward_head_indicator = median(forward)

        if hasattr(self, "head_tilt_degrees"):
            self.head_tilt_degrees = median(head_tilts)

        if hasattr(self, "shoulder_alignment_degrees"):
            self.shoulder_alignment_degrees = median(shoulder_angles)

        if hasattr(self, "neck_offset"):
            self.neck_offset = median(neck_offsets)

        if hasattr(self, "gaze_vertical_degrees"):
            self.gaze_vertical_degrees = median(gaze_angles)

        if hasattr(self, "torso_lean_degrees"):
            self.torso_lean_degrees = 0.0

        self.samples = len(valid)
        self.save()

    def personalize(self, measurement: ErgonomicMeasurements) -> ErgonomicMeasurements:
        if not self.calibrated or not measurement.person_detected:
            return measurement

        return replace(
            measurement,
            head_tilt_degrees=max(
                0.0,
                abs(measurement.head_tilt_signed_degrees - self.head_tilt_degrees) - 2.0,
            ),
            shoulder_alignment_degrees=max(
                0.0,
                abs(
                    measurement.shoulder_alignment_signed_degrees
                    - self.shoulder_alignment_degrees
                ) - 2.0,
            ),
            neck_offset=(
                max(
                    0.0,
                    abs(measurement.neck_offset - self.neck_offset) - 0.035,
                )
                * (1 if measurement.neck_offset - self.neck_offset >= 0 else -1)
            ),
            gaze_vertical_degrees=(
                max(
                    0.0,
                    abs(
                        measurement.gaze_vertical_degrees
                        - self.gaze_vertical_degrees
                    ) - 4.0,
                )
                * (
                    1
                    if measurement.gaze_vertical_degrees
                    - self.gaze_vertical_degrees >= 0
                    else -1
                )
            ),
            torso_lean_degrees=max(
                0.0,
                abs(
                    measurement.torso_lean_signed_degrees
                    - self.torso_lean_degrees
                ) - 2.5,
            ),
            forward_head_indicator=max(
                0.0,
                measurement.forward_head_indicator
                - self.forward_head_indicator
                - 0.05
            ),
        )

    def clear(self) -> None:
        self.calibrated = False
        self.captured_at = None
        self.torso_length_ratio = 0.0
        self.head_shoulder_gap_ratio = 0.0
        self.torso_depth_ratio = 0.0
        self.forward_head_indicator = 0.0
        self.head_tilt_degrees = 0.0
        self.shoulder_alignment_degrees = 0.0
        self.neck_offset = 0.0
        self.gaze_vertical_degrees = 0.0
        self.torso_lean_degrees = 0.0
        self.samples = 0
        try:
            CALIBRATION_PATH.unlink(missing_ok=True)
        except OSError:
            pass

    def save(self) -> None:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        temp = CALIBRATION_PATH.with_suffix(".json.tmp")
        temp.write_text(json.dumps(asdict(self), indent=2), encoding="utf-8")
        temp.replace(CALIBRATION_PATH)

    def slouch_indicator(
        self,
        measurement: ErgonomicMeasurements,
    ) -> float:
        """
        Upper-body hunch estimate.

        Uses:
        - head-to-shoulder vertical compression
        - apparent forward-head/proximity change

        Hip landmarks are deliberately ignored.
        """

        if not measurement.person_detected:
            return 0.0

        # Before personal calibration, use conservative upper-body defaults.
        if not self.calibrated:
            gap_signal = 0.0

            if measurement.head_shoulder_gap_ratio > 0:
                gap_signal = clamp(
                    (1.0 - measurement.head_shoulder_gap_ratio) / 0.45,
                    0.0,
                    1.0,
                )

            forward_signal = clamp(
                (measurement.forward_head_indicator - 0.35) / 0.35,
                0.0,
                1.0,
            )

            return clamp(
                0.60 * gap_signal + 0.40 * forward_signal,
                0.0,
                1.0,
            )

        # Personalized hunch detection.
        gap_signal = 0.0

        if (
            self.head_shoulder_gap_ratio > 0
            and measurement.head_shoulder_gap_ratio > 0
        ):
            gap_drop = (
                self.head_shoulder_gap_ratio
                - measurement.head_shoulder_gap_ratio
            )

            gap_signal = clamp(
                gap_drop
                / max(self.head_shoulder_gap_ratio * 0.18, 0.10),
                0.0,
                1.0,
            )

        forward_change = (
            measurement.forward_head_indicator
            - self.forward_head_indicator
        )

        forward_signal = clamp(
            forward_change / 0.20,
            0.0,
            1.0,
        )

        # Ignore tiny normal movements around the calibrated posture.
        if gap_signal < 0.12 and forward_signal < 0.12:
            return 0.0

        return clamp(
            0.60 * gap_signal + 0.40 * forward_signal,
            0.0,
            1.0,
        )

    def as_dict(self) -> dict:
        return asdict(self)


def _relative_variation(values: list[float]) -> float:
    average = mean(values)
    return 0.0 if abs(average) < 1e-6 else pstdev(values) / abs(average)
