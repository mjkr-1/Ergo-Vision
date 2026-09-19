from app.ergonomics.measurements import compute_measurements
from app.vision.landmarks import Landmark2D, LandmarkSet


def make_landmarks(**overrides) -> LandmarkSet:
    base = {
        "nose_tip": Landmark2D(0.5, 0.35),
        "nose_bridge": Landmark2D(0.5, 0.31),
        "left_eye_outer": Landmark2D(0.45, 0.33),
        "right_eye_outer": Landmark2D(0.55, 0.33),
        "left_ear": Landmark2D(0.42, 0.35),
        "right_ear": Landmark2D(0.58, 0.35),
        "chin": Landmark2D(0.5, 0.42),
        "forehead": Landmark2D(0.5, 0.28),
        "left_shoulder": Landmark2D(0.42, 0.60, z=0.0),
        "right_shoulder": Landmark2D(0.58, 0.60, z=0.0),
        "left_hip": Landmark2D(0.44, 0.88, z=0.0),
        "right_hip": Landmark2D(0.56, 0.88, z=0.0),
    }
    base.update(overrides)
    return LandmarkSet(landmarks=base)


def test_neutral_has_zero_tilt_and_torso_lean():
    measurement = compute_measurements(make_landmarks())
    assert measurement.person_detected
    assert measurement.head_tilt_degrees == 0.0
    assert measurement.shoulder_alignment_degrees == 0.0
    assert measurement.shoulder_alignment_score == 1.0
    assert measurement.neck_offset == 0.0
    assert measurement.torso_lean_degrees == 0.0
    assert measurement.torso_length_ratio > 1.0


def test_shoulder_imbalance_detected():
    landmarks = make_landmarks(
        left_shoulder=Landmark2D(0.40, 0.62),
        right_shoulder=Landmark2D(0.60, 0.58),
    )
    measurement = compute_measurements(landmarks)
    assert measurement.shoulder_alignment_degrees > 0.0
    assert 0.0 <= measurement.shoulder_alignment_score < 1.0


def test_head_tilt_detected():
    landmarks = make_landmarks(
        left_eye_outer=Landmark2D(0.44, 0.33),
        right_eye_outer=Landmark2D(0.56, 0.35),
    )
    assert compute_measurements(landmarks).head_tilt_degrees > 0.0


def test_missing_all_landmarks():
    assert not compute_measurements(None).person_detected


def test_missing_hips_is_graceful():
    landmarks = make_landmarks()
    del landmarks.landmarks["left_hip"]
    del landmarks.landmarks["right_hip"]
    measurement = compute_measurements(landmarks)
    assert measurement.person_detected
    assert measurement.torso_length_ratio == 0.0
    assert measurement.torso_lean_degrees == 0.0


def test_hunched_torso_has_high_slouch_indicator():
    landmarks = make_landmarks(
        left_shoulder=Landmark2D(0.42, 0.72, z=-0.10),
        right_shoulder=Landmark2D(0.58, 0.72, z=-0.10),
        nose_tip=Landmark2D(0.5, 0.43),
        left_ear=Landmark2D(0.42, 0.43),
        right_ear=Landmark2D(0.58, 0.43),
    )
    measurement = compute_measurements(landmarks)
    assert measurement.torso_length_ratio < 1.35
    assert measurement.slouch_indicator >= 0.35


def test_side_torso_lean_detected():
    landmarks = make_landmarks(
        left_shoulder=Landmark2D(0.49, 0.60),
        right_shoulder=Landmark2D(0.65, 0.60),
    )
    measurement = compute_measurements(landmarks)
    assert measurement.torso_lean_degrees > 8.0
