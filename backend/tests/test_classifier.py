from app.config import BAD_FRAMES_BEFORE_ESCALATION, WARNING_FRAMES_BEFORE_ESCALATION
from app.ergonomics.classifier import PostureClassifier
from app.ergonomics.measurements import ErgonomicMeasurements


def neutral():
    return ErgonomicMeasurements(person_detected=True)


def test_no_person_status():
    classifier = PostureClassifier()
    assert classifier.classify(ErgonomicMeasurements(person_detected=False)) == "NO_PERSON"


def test_good_after_no_escalation_frames():
    classifier = PostureClassifier()
    for _ in range(WARNING_FRAMES_BEFORE_ESCALATION + 5):
        classifier.classify(neutral())
    assert classifier.classify(neutral()) == "GOOD"


def test_warning_after_escalation_frames():
    classifier = PostureClassifier()
    measurement = neutral()
    measurement.head_tilt_degrees = 10.0
    for _ in range(WARNING_FRAMES_BEFORE_ESCALATION):
        classifier.classify(measurement)
    assert classifier.classify(measurement) == "WARNING"


def test_bad_after_escalation_frames():
    classifier = PostureClassifier()
    measurement = neutral()
    measurement.head_tilt_degrees = 18.0
    for _ in range(BAD_FRAMES_BEFORE_ESCALATION):
        classifier.classify(measurement)
    assert classifier.classify(measurement) == "BAD"


def test_slouch_escalates_to_bad():
    classifier = PostureClassifier()
    measurement = neutral()
    measurement.slouch_indicator = 0.9
    for _ in range(BAD_FRAMES_BEFORE_ESCALATION):
        classifier.classify(measurement)
    assert classifier.classify(measurement) == "BAD"


def test_reset_works():
    classifier = PostureClassifier()
    measurement = neutral()
    measurement.slouch_indicator = 0.9
    for _ in range(BAD_FRAMES_BEFORE_ESCALATION):
        classifier.classify(measurement)
    classifier.reset()
    assert classifier.classify(neutral()) == "GOOD"
