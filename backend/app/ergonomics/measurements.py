import math
from dataclasses import dataclass
from typing import Optional

from ..ergonomics.geometry import (
    calculate_angle,
    calculate_distance,
    calculate_midpoint,
    angle_from_horizontal,
    angle_from_vertical,
)
from ..vision.landmarks import LandmarkSet


@dataclass
class ErgonomicMeasurements:
    head_tilt_degrees: float = 0.0
    shoulder_alignment_score: float = 1.0
    shoulder_alignment_degrees: float = 0.0
    neck_offset: float = 0.0
    forward_head_indicator: float = 0.0
    gaze_vertical_degrees: float = 0.0
    person_detected: bool = False


def compute_measurements(landmarks: LandmarkSet | None) -> ErgonomicMeasurements:
    if landmarks is None:
        return ErgonomicMeasurements(person_detected=False)

    required_face = ["nose_tip", "left_eye_outer", "right_eye_outer", "chin", "forehead"]
    required_pose = ["left_shoulder", "right_shoulder"]

    has_face = all(landmarks.has(n) for n in required_face)
    has_sholders = all(landmarks.has(n) for n in required_pose)

    if not has_face and not has_sholders:
        return ErgonomicMeasurements(person_detected=False)

    measurements = ErgonomicMeasurements(person_detected=True)

    if has_face:
        measurements.head_tilt_degrees = _compute_head_tilt(landmarks)
        measurements.gaze_vertical_degrees = _compute_gaze_vertical(landmarks)

    if has_face and has_sholders:
        measurements.neck_offset = _compute_neck_offset(landmarks)
        measurements.forward_head_indicator = _compute_forward_head(landmarks)

    if has_sholders:
        measurements.shoulder_alignment_score, measurements.shoulder_alignment_degrees = (
            _compute_shoulder_alignment(landmarks)
        )

    return measurements


def _compute_head_tilt(landmarks: LandmarkSet) -> float:
    left = landmarks.get_pos("left_eye_outer")
    right = landmarks.get_pos("right_eye_outer")
    if left is None or right is None:
        return 0.0
    return abs(angle_from_horizontal(left, right))


def _compute_shoulder_alignment(landmarks: LandmarkSet) -> tuple[float, float]:
    ls = landmarks.get_pos("left_shoulder")
    rs = landmarks.get_pos("right_shoulder")
    if ls is None or rs is None:
        return 1.0, 0.0
    angle = abs(angle_from_horizontal(ls, rs))
    degrees = abs(angle) if angle <= 90 else 180 - abs(angle)
    alignment = max(0.0, 1.0 - degrees / 20.0)
    return alignment, degrees


def _compute_neck_offset(landmarks: LandmarkSet) -> float:
    nose = landmarks.get_pos("nose_tip")
    ls = landmarks.get_pos("left_shoulder")
    rs = landmarks.get_pos("right_shoulder")
    if nose is None or ls is None or rs is None:
        return 0.0
    mid = calculate_midpoint(ls, rs)
    shoulder_width = abs(rs[0] - ls[0])
    if shoulder_width < 1e-6:
        return 0.0
    offset = (nose[0] - mid[0]) / shoulder_width
    return max(-1.0, min(1.0, offset))


def _compute_forward_head(landmarks: LandmarkSet) -> float:
    nose = landmarks.get_pos("nose_tip")
    ls = landmarks.get_pos("left_shoulder")
    rs = landmarks.get_pos("right_shoulder")
    chin = landmarks.get_pos("chin")
    if nose is None or ls is None or rs is None or chin is None:
        return 0.0
    shoulder_width = abs(rs[0] - ls[0])
    if shoulder_width < 1e-6:
        return 0.0
    face_height = abs(chin[1] - landmarks.get_pos("forehead")[1]) if landmarks.get_pos("forehead") else 0.0
    face_height = abs(chin[1] - nose[1]) * 2.0 if face_height < 1e-6 else face_height
    ratio = face_height / shoulder_width
    indicator = min(1.0, max(0.0, (ratio - 0.4) / 0.8))
    return indicator


def _compute_gaze_vertical(landmarks: LandmarkSet) -> float:
    nose = landmarks.get_pos("nose_tip")
    forehead = landmarks.get_pos("forehead")
    if nose is None or forehead is None:
        return 0.0
    return angle_from_vertical(forehead, nose)
