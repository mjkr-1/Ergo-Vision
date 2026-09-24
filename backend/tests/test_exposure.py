from app.ergonomics.exposure import ExposureEngine


def test_first_update_sets_risk_without_accumulating_time():
    engine = ExposureEngine()
    snapshot = engine.update(risk=0.3, confidence=0.9, reliable=True, timestamp=10.0)
    assert snapshot.available
    assert snapshot.instantaneous_risk == 0.3
    assert snapshot.confidence_weighted_risk == 0.27
    assert snapshot.cumulative_dose == 0.0


def test_exposure_accumulates_with_time_and_confidence():
    engine = ExposureEngine(recovery_rate=0.0)
    engine.update(risk=0.5, confidence=1.0, reliable=True, timestamp=0.0)
    snapshot = engine.update(risk=0.5, confidence=1.0, reliable=True, timestamp=1.0)
    assert snapshot.cumulative_dose == 0.5
    assert snapshot.continuous_poor_seconds == 1.0


def test_unreliable_tracking_freezes_exposure():
    engine = ExposureEngine(recovery_rate=0.0)
    engine.update(risk=0.8, confidence=1.0, reliable=True, timestamp=0.0)
    before = engine.update(risk=0.8, confidence=1.0, reliable=True, timestamp=1.0)
    after = engine.update(risk=1.0, confidence=0.1, reliable=False, timestamp=2.0)
    assert not after.available
    assert after.cumulative_dose == before.cumulative_dose


def test_good_posture_recovers_dose_and_resets_streak():
    engine = ExposureEngine(recovery_rate=0.5)
    engine.update(risk=0.8, confidence=1.0, reliable=True, timestamp=0.0)
    poor = engine.update(risk=0.8, confidence=1.0, reliable=True, timestamp=1.0)
    recovered = engine.update(risk=0.0, confidence=1.0, reliable=True, timestamp=2.0)
    assert poor.cumulative_dose > recovered.cumulative_dose
    assert recovered.continuous_poor_seconds == 0.0
