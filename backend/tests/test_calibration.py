from pathlib import Path

import app.ergonomics.calibration as calibration_module
from app.ergonomics.calibration import CalibrationProfile
from app.ergonomics.measurements import ErgonomicMeasurements


def measurement(torso=1.7, gap=1.4, depth=0.0, forward=0.2):
    return ErgonomicMeasurements(
        person_detected=True,
        torso_length_ratio=torso,
        head_shoulder_gap_ratio=gap,
        torso_depth_ratio=depth,
        forward_head_indicator=forward,
    )


def test_calibration_detects_change(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(calibration_module, "DATA_DIR", tmp_path)
    monkeypatch.setattr(calibration_module, "CALIBRATION_PATH", tmp_path / "calibration.json")

    profile = CalibrationProfile()
    profile.capture([measurement() for _ in range(20)])
    assert profile.calibrated
    assert profile.slouch_indicator(measurement()) < 0.1

    hunched = measurement(torso=1.15, gap=0.85, depth=0.5, forward=0.55)
    assert profile.slouch_indicator(hunched) >= 0.7


def test_calibration_requires_enough_samples():
    profile = CalibrationProfile()
    try:
        profile.capture([measurement() for _ in range(3)])
    except ValueError:
        pass
    else:
        raise AssertionError("Expected calibration to require more samples")
