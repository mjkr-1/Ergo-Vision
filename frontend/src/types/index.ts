export type PostureStatus = 'GOOD' | 'WARNING' | 'BAD' | 'NO_PERSON' | 'UNKNOWN'

export interface Measurements {
  head_tilt_degrees: number
  shoulder_alignment_score: number
  shoulder_alignment_degrees: number
  neck_offset: number
  forward_head_indicator: number
  gaze_vertical_degrees: number
}

export interface PostureEvent {
  score: number
  status: PostureStatus
  measurements: Measurements
  feedback: string[]
  timestamp: string
  person_detected: boolean
}

export interface SessionStats {
  session_duration_seconds: number
  good_duration_seconds: number
  warning_duration_seconds: number
  bad_duration_seconds: number
  no_person_duration_seconds: number
  good_percentage: number
  warning_percentage: number
  bad_percentage: number
  no_person_percentage: number
  warning_count: number
  bad_count: number
  average_score: number
  current_score: number
  longest_poor_posture_seconds: number
  active: boolean
}

export interface AppConfig {
  head_tilt_warning_degrees: number
  head_tilt_bad_degrees: number
  shoulder_alignment_warning_degrees: number
  shoulder_alignment_bad_degrees: number
  neck_offset_warning: number
  neck_offset_bad: number
  forward_head_warning: number
  forward_head_bad: number
  gaze_warning_degrees: number
  gaze_bad_degrees: number
  score_good_threshold: number
  score_warning_threshold: number
  smoothing_alpha: number
  warning_frames_before_escalation: number
  bad_frames_before_escalation: number
  camera_index: number
  frame_width: number
  frame_height: number
  target_fps: number
  demo_mode: boolean
}

export interface HealthStatus {
  status: string
  camera_available: boolean
  model_loaded: boolean
  demo_mode: boolean
  uptime_seconds: number
  fps: number
}