import math


def calculate_angle(point_a, point_b, point_c) -> float:
    """Angle at point_b formed by A-B-C, in degrees."""
    ba = (point_a[0] - point_b[0], point_a[1] - point_b[1])
    bc = (point_c[0] - point_b[0], point_c[1] - point_b[1])
    dot = ba[0] * bc[0] + ba[1] * bc[1]
    mag_ba = math.sqrt(ba[0] ** 2 + ba[1] ** 2)
    mag_bc = math.sqrt(bc[0] ** 2 + bc[1] ** 2)
    if mag_ba < 1e-10 or mag_bc < 1e-10:
        return 0.0
    cos_angle = max(-1.0, min(1.0, dot / (mag_ba * mag_bc)))
    return math.degrees(math.acos(cos_angle))


def calculate_distance(point_a, point_b) -> float:
    dx = point_a[0] - point_b[0]
    dy = point_a[1] - point_b[1]
    return math.sqrt(dx * dx + dy * dy)


def calculate_midpoint(point_a, point_b):
    return ((point_a[0] + point_b[0]) / 2.0, (point_a[1] + point_b[1]) / 2.0)


def calculate_vertical_difference(point_a, point_b) -> float:
    return abs(point_a[1] - point_b[1])


def calculate_horizontal_difference(point_a, point_b) -> float:
    return abs(point_a[0] - point_b[0])


def angle_from_horizontal(point_a, point_b) -> float:
    """Angle of the line A-B relative to horizontal, in degrees."""
    dx = point_b[0] - point_a[0]
    dy = point_b[1] - point_a[1]
    return math.degrees(math.atan2(dy, dx))


def angle_from_vertical(point_a, point_b) -> float:
    """Angle of the line A-B relative to vertical, in degrees."""
    dx = point_b[0] - point_a[0]
    dy = point_b[1] - point_a[1]
    return math.degrees(math.atan2(abs(dx), abs(dy)))


def normalize_value(value, min_val, max_val) -> float:
    if max_val - min_val < 1e-10:
        return 0.0
    return max(0.0, min(1.0, (value - min_val) / (max_val - min_val)))


def clamp(value, min_val, max_val):
    return max(min_val, min(max_val, value))
