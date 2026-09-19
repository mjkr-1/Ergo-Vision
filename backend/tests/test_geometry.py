import math

import pytest

from app.ergonomics.geometry import (
    calculate_angle,
    calculate_distance,
    calculate_horizontal_difference,
    calculate_midpoint,
    calculate_vertical_difference,
    clamp,
    normalize_value,
)


class TestAngle:
    def test_right_angle(self):
        a, b, c = (1, 0), (0, 0), (0, 1)
        assert math.isclose(calculate_angle(a, b, c), 90.0, abs_tol=1e-6)

    def test_straight_line(self):
        a, b, c = (0, 0), (1, 1), (2, 2)
        assert math.isclose(calculate_angle(a, b, c), 180.0, abs_tol=1e-4)

    def test_45_degrees(self):
        a, b, c = (1, 0), (0, 0), (1, 1)
        assert math.isclose(calculate_angle(a, b, c), 45.0, abs_tol=1e-6)

    def test_identical_points_no_crash(self):
        assert calculate_angle((0, 0), (0, 0), (1, 1)) == 0.0

    def test_collinear_back(self):
        a, b, c = (2, 2), (1, 1), (0, 0)
        assert math.isclose(calculate_angle(a, b, c), 180.0, abs_tol=1e-4)


class TestDistance:
    def test_basic(self):
        assert math.isclose(calculate_distance((0, 0), (3, 4)), 5.0)

    def test_zero(self):
        assert calculate_distance((1, 1), (1, 1)) == 0.0

    def test_negative_coords(self):
        assert math.isclose(calculate_distance((-1, -1), (2, 3)), 5.0)


class TestMidpoint:
    def test_midpoint(self):
        assert calculate_midpoint((0, 0), (10, 10)) == (5.0, 5.0)

    def test_odd_midpoint(self):
        assert calculate_midpoint((1, 2), (4, 6)) == (2.5, 4.0)


class TestDiffs:
    def test_vertical(self):
        assert calculate_vertical_difference((0, 1), (0, 5)) == 4.0

    def test_horizontal(self):
        assert calculate_horizontal_difference((1, 0), (6, 0)) == 5.0


class TestNormalize:
    def test_in_range(self):
        assert normalize_value(5, 0, 10) == 0.5

    def test_below_min(self):
        assert normalize_value(-5, 0, 10) == 0.0

    def test_above_max(self):
        assert normalize_value(15, 0, 10) == 1.0

    def test_zero_range(self):
        assert normalize_value(5, 5, 5) == 0.0


class TestClamp:
    def test_basic(self):
        assert clamp(5, 0, 10) == 5

    def test_lower(self):
        assert clamp(-5, 0, 10) == 0

    def test_upper(self):
        assert clamp(15, 0, 10) == 10
