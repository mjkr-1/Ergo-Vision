import time

from app.session.tracker import SessionTracker


def test_initial_state():
    t = SessionTracker()
    stats = t.get_stats()
    assert stats.session_duration_seconds == 0.0
    assert stats.average_score == 100.0


def test_single_update():
    t = SessionTracker()
    t.update("GOOD", 85)
    stats = t.get_stats()
    assert stats.current_score == 85
    assert stats.average_score == 85.0
    assert stats.active


def test_multiple_scores_average():
    t = SessionTracker()
    t.update("GOOD", 80)
    t.update("GOOD", 90)
    t.update("WARNING", 70)
    stats = t.get_stats()
    assert stats.average_score == 80.0
    assert stats.warning_count >= 1


def test_duration_accounting():
    t = SessionTracker()
    t.update("GOOD", 80)
    time.sleep(0.05)
    t.update("GOOD", 82)
    stats = t.get_stats()
    assert stats.good_duration_seconds >= 0.04
    assert stats.good_percentage == 100.0


def test_longest_poor_detected():
    t = SessionTracker()
    t.update("GOOD", 90)
    t.update("WARNING", 60)
    time.sleep(0.05)
    t.update("BAD", 30)
    time.sleep(0.05)
    t.update("GOOD", 95)
    stats = t.get_stats()
    assert stats.longest_poor_posture_seconds >= 0.08
    assert stats.warning_count >= 1
    assert stats.bad_count >= 1


def test_pause_does_not_count_time_or_scores():
    t = SessionTracker()
    t.update("GOOD", 80)
    time.sleep(0.02)
    t.stop()
    before = t.get_stats()
    time.sleep(0.03)
    t.update("BAD", 10)
    after = t.get_stats()
    assert not after.active
    assert after.average_score == 80.0
    assert after.session_duration_seconds == before.session_duration_seconds


def test_resume_continues_same_session():
    t = SessionTracker()
    t.update("GOOD", 80)
    time.sleep(0.11)
    t.stop()
    paused = t.get_stats().session_duration_seconds
    t.start()
    time.sleep(0.11)
    t.update("GOOD", 90)
    resumed = t.get_stats()
    assert resumed.active
    assert resumed.session_duration_seconds > paused
    assert resumed.average_score == 85.0


def test_reset():
    t = SessionTracker()
    t.update("GOOD", 80)
    t.reset()
    stats = t.get_stats()
    assert not stats.active
    assert stats.average_score == 100.0
