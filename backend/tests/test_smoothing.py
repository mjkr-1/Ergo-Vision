from app.ergonomics.measurements import ErgonomicMeasurements
from app.ergonomics.smoothing import SmoothingBuffer


def val(tilt):
    m = ErgonomicMeasurements(person_detected=True)
    m.head_tilt_degrees = tilt
    return m


def test_first_frame_passthrough():
    s = SmoothingBuffer()
    m = val(10.0)
    assert s.smooth(m).head_tilt_degrees == 10.0


def test_smoothing_reduces_jump():
    s = SmoothingBuffer(alpha=0.3)
    s.smooth(val(0.0))
    result = s.smooth(val(10.0))
    assert result.head_tilt_degrees < 10.0
    assert result.head_tilt_degrees > 0.0


def test_converges_to_steady_state():
    s = SmoothingBuffer(alpha=0.5)
    s.smooth(val(0.0))
    for _ in range(50):
        out = s.smooth(val(5.0))
    assert abs(out.head_tilt_degrees - 5.0) < 0.01


def test_no_person_resets_buffer():
    s = SmoothingBuffer()
    s.smooth(val(10.0))
    result = s.smooth(ErgonomicMeasurements(person_detected=False))
    assert not result.person_detected
    after = s.smooth(val(20.0))
    assert after.head_tilt_degrees == 20.0


def test_reset_method():
    s = SmoothingBuffer()
    s.smooth(val(10.0))
    s.reset()
    assert s.smooth(val(20.0)).head_tilt_degrees == 20.0