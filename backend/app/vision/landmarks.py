from dataclasses import dataclass
from typing import Optional


@dataclass
class Landmark2D:
    x: float
    y: float
    z: float = 0.0
    visibility: float = 0.0
    presence: float = 0.0


@dataclass
class LandmarkSet:
    """Abstraction over MediaPipe landmarks."""

    landmarks: dict[str, Landmark2D]

    def get(self, name: str) -> Optional[Landmark2D]:
        return self.landmarks.get(name)

    def has(self, name: str) -> bool:
        return name in self.landmarks

    def get_pos(self, name: str) -> Optional[tuple[float, float]]:
        lm = self.get(name)
        if lm is None:
            return None
        return (lm.x, lm.y)

    def available_names(self) -> list[str]:
        return list(self.landmarks.keys())


FACE_LANDMARK_NAMES = {
    "nose_tip": 4,
    "nose_bridge": 6,
    "left_eye_inner": 133,
    "left_eye_outer": 33,
    "left_eye_upper_outer": 160,
    "left_eye_upper_inner": 158,
    "left_eye_lower_inner": 153,
    "left_eye_lower_outer": 144,
    "left_eye_center": 159,
    "right_eye_inner": 362,
    "right_eye_outer": 263,
    "right_eye_upper_inner": 385,
    "right_eye_upper_outer": 387,
    "right_eye_lower_outer": 373,
    "right_eye_lower_inner": 380,
    "right_eye_center": 386,
    "left_ear": 234,
    "right_ear": 454,
    "chin": 152,
    "forehead": 10,
    "mouth_left": 61,
    "mouth_right": 291,
    "left_iris": 468,
    "right_iris": 473,
}

POSE_LANDMARK_NAMES = {
    "nose": 0,
    "left_eye": 2,
    "right_eye": 5,
    "left_ear": 7,
    "right_ear": 8,
    "left_shoulder": 11,
    "right_shoulder": 12,
    "left_elbow": 13,
    "right_elbow": 14,
    "left_wrist": 15,
    "right_wrist": 16,
    "left_hip": 23,
    "right_hip": 24,
}


def _to_landmark(lm) -> Landmark2D:
    return Landmark2D(
        x=lm.x,
        y=lm.y,
        z=getattr(lm, "z", 0.0) or 0.0,
        visibility=getattr(lm, "visibility", 0.0) or 0.0,
        presence=getattr(lm, "presence", 0.0) or 0.0,
    )


def landmarks_from_face_results(face_landmarks_list) -> Optional[LandmarkSet]:
    if not face_landmarks_list:
        return None
    face_lms = face_landmarks_list[0]
    landmarks = {
        name: _to_landmark(face_lms[idx])
        for name, idx in FACE_LANDMARK_NAMES.items()
        if idx < len(face_lms)
    }
    return LandmarkSet(landmarks=landmarks) if landmarks else None


def landmarks_from_pose_results(pose_landmarks_list) -> Optional[LandmarkSet]:
    if not pose_landmarks_list:
        return None
    pose_lms = pose_landmarks_list[0]
    landmarks = {
        name: _to_landmark(pose_lms[idx])
        for name, idx in POSE_LANDMARK_NAMES.items()
        if idx < len(pose_lms)
    }
    return LandmarkSet(landmarks=landmarks) if landmarks else None


def merge_landmarks(face: Optional[LandmarkSet], pose: Optional[LandmarkSet]) -> LandmarkSet:
    merged = {}
    if face:
        merged.update(face.landmarks)
    if pose:
        merged.update(pose.landmarks)
    return LandmarkSet(landmarks=merged)
