from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean

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
        valid = [sample for sample in samples if sample.person_detected]
        if len(valid) < 12:
            raise ValueError("Keep your upright posture in frame for a moment, then try calibration again.")

        torso_samples = [sample.torso_length_ratio for sample in valid if sample.torso_length_ratio > 0]
        gap_samples = [sample.head_shoulder_gap_ratio for sample in valid if sample.head_shoulder_gap_ratio > 0]
        depth_samples = [sample.torso_depth_ratio for sample in valid if sample.torso_length_ratio > 0]

        self.calibrated = True
        self.captured_at = datetime.now(timezone.utc).isoformat()
        self.torso_length_ratio = mean(torso_samples) if torso_samples else 0.0
        self.head_shoulder_gap_ratio = mean(gap_samples) if gap_samples else 0.0
        self.torso_depth_ratio = mean(depth_samples) if depth_samples else 0.0
        self.forward_head_indicator = mean(sample.forward_head_indicator for sample in valid)
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
