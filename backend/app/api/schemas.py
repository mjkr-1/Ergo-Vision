from typing import Optional

from pydantic import BaseModel


class Measurements(BaseModel):
    head_tilt_degrees: float
    shoulder_alignment_score: float
    shoulder_alignment_degrees: float
    neck_offset: float
    forward_head_indicator: float
    gaze_vertical_degrees: float


class PostureCurrent(BaseModel):
    score: int
    status: str
    measurements: Measurements
    feedback: list[str]
    timestamp: str
    person_detected: bool


class SessionStatsResponse(BaseModel):
    session_duration_seconds: float
    good_duration_seconds: float
    warning_duration_seconds: float
    bad_duration_seconds: float
    no_person_duration_seconds: float
    good_percentage: float
    warning_percentage: float
    bad_percentage: float
    no_person_percentage: float
    warning_count: int
    bad_count: int
    average_score: float
    current_score: int
    longest_poor_posture_seconds: float
    active: bool


class ConfigResponse(BaseModel):
    head_tilt_warning_degrees: float
    head_tilt_bad_degrees: float
    shoulder_alignment_warning_degrees: float
    shoulder_alignment_bad_degrees: float
    neck_offset_warning: float
    neck_offset_bad: float
    forward_head_warning: float
    forward_head_bad: float
    gaze_warning_degrees: float
    gaze_bad_degrees: float
    score_good_threshold: int
    score_warning_threshold: int
    smoothing_alpha: float
    warning_frames_before_escalation: int
    bad_frames_before_escalation: int
    camera_index: int
    frame_width: int
    frame_height: int
    target_fps: int
    demo_mode: bool


class HealthResponse(BaseModel):
    status: str
    camera_available: bool
    model_loaded: bool
    demo_mode: bool
    uptime_seconds: float
    fps: float