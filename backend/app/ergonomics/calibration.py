from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, pstdev

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
    samples: int = 0

    @classmethod
    def load(cls) -> "CalibrationProfile":
        try:
            data = json.loads(CALIBRATION_PATH.read_text(encoding="utf-8"))
            return cls(**data)
        except (OSError, ValueError, TypeError):
            return cls()

    def capture(self, samples: list[ErgonomicMeasurements]) -> None:
        valid = [s for s in samples if s.person_detected and s.torso_length_ratio > 0 and s.head_shoulder_gap_ratio > 0]
        if len(valid) < 20:
            raise ValueError("Calibration needs a stable view of your head, shoulders and hips. Hold an upright posture for 2–3 seconds and try again.")
        torso = [s.torso_length_ratio for s in valid]
        gaps = [s.head_shoulder_gap_ratio for s in valid]
        depths = [s.torso_depth_ratio for s in valid]
        forward = [s.forward_head_indicator for s in valid]
        if mean(estimate_slouch(s) for s in valid) >= 0.45:
            raise ValueError("Sit upright before calibrating, then hold still for 2–3 seconds.")
        if _relative_variation(torso) > 0.08 or _relative_variation(gaps) > 0.10 or pstdev(forward) > 0.10:
            raise ValueError("Too much movement was detected. Hold still and try calibration again.")
        self.calibrated = True
        self.captured_at = datetime.now(timezone.utc).isoformat()
        self.torso_length_ratio = mean(torso)
        self.head_shoulder_gap_ratio = mean(gaps)
        self.torso_depth_ratio = mean(depths)
        self.forward_head_indicator = mean(forward)
        self.samples = len(valid)
        self.save()

    def clear(self) -> None:
        self.calibrated = False
        self.captured_at = None
        self.torso_length_ratio = 0.0
        self.head_shoulder_gap_ratio = 0.0
        self.torso_depth_ratio = 0.0
        self.forward_head_indicator = 0.0
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

    def slouch_indicator(self, measurement: ErgonomicMeasurements) -> float:
        if not self.calibrated:
            return estimate_slouch(measurement)
        signals: list[float] = []
        if self.torso_length_ratio > 0 and measurement.torso_length_ratio > 0:
            drop = self.torso_length_ratio - measurement.torso_length_ratio
            signals.append(clamp(drop / max(self.torso_length_ratio * 0.24, 0.22), 0.0, 1.0))
            depth_change = measurement.torso_depth_ratio - self.torso_depth_ratio
            signals.append(clamp(depth_change / 0.55, 0.0, 1.0))
        if self.head_shoulder_gap_ratio > 0 and measurement.head_shoulder_gap_ratio > 0:
            gap_drop = self.head_shoulder_gap_ratio - measurement.head_shoulder_gap_ratio
            signals.append(clamp(gap_drop / max(self.head_shoulder_gap_ratio * 0.28, 0.18), 0.0, 1.0))
        forward_change = measurement.forward_head_indicator - self.forward_head_indicator
        signals.append(clamp(forward_change / 0.35, 0.0, 1.0))
        return max(signals, default=estimate_slouch(measurement))

    def as_dict(self) -> dict:
        return asdict(self)


def _relative_variation(values: list[float]) -> float:
    average = mean(values)
    return 0.0 if abs(average) < 1e-6 else pstdev(values) / abs(average)
