from dataclasses import dataclass
from typing import Optional


@dataclass
class Landmark2D:
    x: float
    y: float
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
    "left_eye_center": 159,
    "right_eye_inner": 362,
    "right_eye_outer": 263,
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
    "left_shoulder": 11,
    "right_shoulder": 12,
    "left_elbow": 13,
    "right_elbow": 14,
    "left_wrist": 15,
    "right_wrist": 16,
    "nose": 0,
    "left_eye": 2,
    "right_eye": 5,
    "left_ear": 7,
    "right_ear": 8,
}


def landmarks_from_face_results(face_landmarks_list) -> Optional[LandmarkSet]:
    if not face_landmarks_list or len(face_landmarks_list) == 0:
        return None
    face_lms = face_landmarks_list[0]
    landmarks = {}
    for name, idx in FACE_LANDMARK_NAMES.items():
        if idx < len(face_lms):
            lm = face_lms[idx]
            landmarks[name] = Landmark2D(
                x=lm.x, y=lm.y,
                visibility=getattr(lm, 'visibility', 0.0) or 0.0,
                presence=getattr(lm, 'presence', 0.0) or 0.0,
            )
    return LandmarkSet(landmarks=landmarks) if landmarks else None


def landmarks_from_pose_results(pose_landmarks_list) -> Optional[LandmarkSet]:
    if not pose_landmarks_list or len(pose_landmarks_list) == 0:
        return None
    pose_lms = pose_landmarks_list[0]
    landmarks = {}
    for name, idx in POSE_LANDMARK_NAMES.items():
        if idx < len(pose_lms):
            lm = pose_lms[idx]
            landmarks[name] = Landmark2D(
                x=lm.x, y=lm.y,
                visibility=getattr(lm, 'visibility', 0.0) or 0.0,
                presence=getattr(lm, 'presence', 0.0) or 0.0,
            )
    return LandmarkSet(landmarks=landmarks) if landmarks else None


def merge_landmarks(face: Optional[LandmarkSet], pose: Optional[LandmarkSet]) -> LandmarkSet:
    merged = {}
    if face:
        merged.update(face.landmarks)
    if pose:
        merged.update(pose.landmarks)
    return LandmarkSet(landmarks=merged)
