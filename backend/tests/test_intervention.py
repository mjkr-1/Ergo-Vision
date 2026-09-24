from app.ergonomics.intervention import InterventionEngine


def test_alert_requires_sustained_poor_posture():
    engine = InterventionEngine(trigger_seconds=5.0, recovery_seconds=2.0)
    engine.update(0.7, "BAD", True, timestamp=0.0)
    before = engine.update(0.7, "BAD", True, timestamp=4.9)
    after = engine.update(0.7, "BAD", True, timestamp=5.1)
    assert before.state == "PENDING"
    assert after.state == "ALERTING"
    assert after.active


def test_alert_clears_only_after_verified_recovery():
    engine = InterventionEngine(trigger_seconds=1.0, recovery_seconds=2.0)
    engine.update(0.7, "BAD", True, timestamp=0.0)
    engine.update(0.7, "BAD", True, timestamp=1.1)
    verifying = engine.update(0.1, "GOOD", True, timestamp=1.2)
    assert verifying.state == "VERIFYING"

    interrupted = engine.update(0.1, "GOOD", False, timestamp=2.0)
    assert interrupted.state == "ALERTING"

    engine.update(0.1, "GOOD", True, timestamp=2.1)
    corrected = engine.update(0.1, "GOOD", True, timestamp=4.2)
    assert corrected.state == "CORRECTED"
    assert corrected.successful_corrections == 1
    assert corrected.improvement_percent > 0
