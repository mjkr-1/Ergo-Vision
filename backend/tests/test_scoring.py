from app.config import (
    SCORE_GOOD_THRESHOLD,
    SCORE_WARNING_THRESHOLD,
)
from app.ergonomics.measurements import ErgonomicMeasurements
from app.ergonomics.scoring import compute_score


def neutral():
    return ErgonomicMeasurements(person_detected=True)


def tilted(degrees):
    m = neutral()
    m.head_tilt_degrees = degrees
    return m


def test_perfect_posture_scores_100():
    score, breakdown = compute_score(neutral())
    assert score == 100
    assert breakdown.head_tilt_penalty == 0


def test_slight_tilt_scores_high():
    score, _ = compute_score(tilted(3.0))
    assert score >= 90


def test_severe_tilt_low_score():
    score, _ = compute_score(tilted(20.0))
    assert score <= 65


def test_no_person_zero_score():
    score, _ = compute_score(ErgonomicMeasurements(person_detected=False))
    assert score == 0


def test_worst_case_score_zero():
    m = ErgonomicMeasurements(
        person_detected=True,
        head_tilt_degrees=30.0,
        shoulder_alignment_degrees=30.0,
        neck_offset=0.6,
        forward_head_indicator=1.0,
        gaze_vertical_degrees=35.0,
    )
    score, _ = compute_score(m)
    assert score == 0


def test_score_bounded():
    for _ in range(50):
        import random
        m = ErgonomicMeasurements(
            person_detected=True,
            head_tilt_degrees=random.uniform(0, 25),
            shoulder_alignment_degrees=random.uniform(0, 15),
            neck_offset=random.uniform(-0.5, 0.5),
            forward_head_indicator=random.uniform(0, 1),
            gaze_vertical_degrees=random.uniform(0, 30),
        )
        score, _ = compute_score(m)
        assert 0 <= score <= 100


def test_good_threshold():
    assert SCORE_GOOD_THRESHOLD > SCORE_WARNING_THRESHOLD