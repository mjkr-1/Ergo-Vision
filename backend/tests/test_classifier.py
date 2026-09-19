from app.config import (
    BAD_FRAMES_BEFORE_ESCALATION,
    WARNING_FRAMES_BEFORE_ESCALATION,
)
from app.ergonomics.classifier import PostureClassifier
from app.ergonomics.measurements import ErgonomicMeasurements


def neutral():
    return ErgonomicMeasurements(person_detected=True)


def with_head_tilt(degrees):
    m = neutral()
    m.head_tilt_degrees = degrees
    return m


def with_shoulder_tilt(degrees):
    m = neutral()
    m.shoulder_alignment_degrees = degrees
    return m


def test_no_person_status():
    clf = PostureClassifier()
    assert clf.classify(ErgonomicMeasurements(person_detected=False)) == "NO_PERSON"


def test_good_after_no_escalation_frames():
    clf = PostureClassifier()
    for _ in range(WARNING_FRAMES_BEFORE_ESCALATION + 5):
        clf.classify(neutral())
    assert clf.classify(neutral()) == "GOOD"


def test_warning_after_escalation_frames():
    clf = PostureClassifier()
    m = with_head_tilt(10.0)
    for _ in range(WARNING_FRAMES_BEFORE_ESCALATION):
        clf.classify(m)
    assert clf.classify(m) == "WARNING"


def test_bad_after_escalation_frames():
    clf = PostureClassifier()
    m = with_head_tilt(18.0)
    for _ in range(BAD_FRAMES_BEFORE_ESCALATION):
        clf.classify(m)
    assert clf.classify(m) == "BAD"


def test_reset_works():
    clf = PostureClassifier()
    m = with_head_tilt(18.0)
    for _ in range(BAD_FRAMES_BEFORE_ESCALATION):
        clf.classify(m)
    clf.reset()
    m2 = with_head_tilt(2.0)
    assert clf.classify(m2) == "GOOD"


def test_smoothing_prevents_oscillation():
    """Validates that the duration-based classifier doesn't rapidly flip."""
    clf = PostureClassifier()
    statuses = []
    for i in range(60):
        if i < 20:
            m = neutral()
        elif i < 40:
            m = with_head_tilt(10.0)
        else:
            m = neutral()
        statuses.append(clf.classify(m))
    transitions = sum(1 for i in range(1, len(statuses)) if statuses[i] != statuses[i - 1])
    assert transitions <= 4