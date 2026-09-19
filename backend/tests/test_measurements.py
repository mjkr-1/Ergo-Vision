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
        "left_shoulder": Landmark2D(0.42, 0.60),
        "right_shoulder": Landmark2D(0.58, 0.60),
    }
    base.update(overrides)
    return LandmarkSet(landmarks=base)


def test_neutral_has_zero_tilt():
    lm = make_landmarks()
    from app.ergonomics.measurements import compute_measurements
    m = compute_measurements(lm)
    assert m.person_detected
    assert m.head_tilt_degrees == 0.0
    assert m.shoulder_alignment_degrees == 0.0
    assert m.shoulder_alignment_score == 1.0
    assert m.neck_offset == 0.0


def test_shoulder_imbalance_detected():
    lm = make_landmarks(left_shoulder=Landmark2D(0.40, 0.62), right_shoulder=Landmark2D(0.60, 0.58))
    from app.ergonomics.measurements import compute_measurements
    m = compute_measurements(lm)
    assert m.shoulder_alignment_degrees > 0.0
    assert 0.0 <= m.shoulder_alignment_score < 1.0


def test_head_tilt_detected():
    lm = make_landmarks(left_eye_outer=Landmark2D(0.44, 0.33), right_eye_outer=Landmark2D(0.56, 0.35))
    from app.ergonomics.measurements import compute_measurements
    m = compute_measurements(lm)
    assert m.head_tilt_degrees > 0.0


def test_missing_all_landmarks():
    from app.ergonomics.measurements import compute_measurements
    m = compute_measurements(None)
    assert not m.person_detected


def test_missing_shoulders_graceful():
    lm = LandmarkSet(landmarks={"nose_tip": Landmark2D(0.5, 0.35), "left_eye_outer": Landmark2D(0.45, 0.33),
                                "right_eye_outer": Landmark2D(0.55, 0.33), "chin": Landmark2D(0.5, 0.42),
                                "forehead": Landmark2D(0.5, 0.28), "nose_bridge": Landmark2D(0.5, 0.31)})
    from app.ergonomics.measurements import compute_measurements
    m = compute_measurements(lm)
    assert m.person_detected
    assert m.shoulder_alignment_score == 1.0


def test_forward_head_large_face():
    nose = Landmark2D(0.5, 0.40)
    lm = make_landmarks(nose_tip=nose, chin=Landmark2D(0.5, 0.50),
                        forehead=Landmark2D(0.5, 0.10))
    lm2 = make_landmarks()
    lm2.landmarks["nose_tip"] = nose
    lm2.landmarks["chin"] = Landmark2D(0.5, 0.50)
    lm2.landmarks["forehead"] = Landmark2D(0.5, 0.10)
    from app.ergonomics.measurements import compute_measurements
    m = compute_measurements(lm2)
    assert m.forward_head_indicator >= 0.0
    assert m.forward_head_indicator <= 1.0