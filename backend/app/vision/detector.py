import logging
import math
import threading
import time

import cv2
import mediapipe as mp
import numpy as np

from ..config import AUTO_DOWNLOAD_MODELS, DEMO_MODE, FRAME_HEIGHT
from .camera import Camera
from .landmarks import (
    Landmark2D,
    LandmarkSet,
    landmarks_from_face_results,
    landmarks_from_pose_results,
    merge_landmarks,
)
from .models import MODELS_DIR, ensure_models

logger = logging.getLogger(__name__)

mp_image = mp.Image

FACE_MODEL_PATH = str(MODELS_DIR / "face_landmarker.task")
POSE_MODEL_PATH = str(MODELS_DIR / "pose_landmarker_lite.task")


class Detector:
    def __init__(self, camera: Camera):
        self.camera = camera
        self.face_landmarker = None
        self.pose_landmarker = None
        self.model_loaded = False
        self.last_landmarks: LandmarkSet | None = None
        self._last_face: LandmarkSet | None = None
        self._last_pose: LandmarkSet | None = None
        self._landmark_lock = threading.Lock()
        self._demo_provider = DemoLandmarkProvider()

    def load_models(self) -> bool:
        if not ensure_models(auto_download=AUTO_DOWNLOAD_MODELS):
            return False

        try:
            base_options = mp.tasks.BaseOptions
            vision = mp.tasks.vision
            running_mode = vision.RunningMode.LIVE_STREAM

            face_options = vision.FaceLandmarkerOptions(
                base_options=base_options(model_asset_path=FACE_MODEL_PATH),
                running_mode=running_mode,
                num_faces=1,
                min_face_detection_confidence=0.3,
                min_face_presence_confidence=0.3,
                min_tracking_confidence=0.3,
                result_callback=self._face_callback,
            )
            self.face_landmarker = vision.FaceLandmarker.create_from_options(face_options)

            pose_options = vision.PoseLandmarkerOptions(
                base_options=base_options(model_asset_path=POSE_MODEL_PATH),
                running_mode=running_mode,
                num_poses=1,
                min_pose_detection_confidence=0.3,
                min_pose_presence_confidence=0.3,
                min_tracking_confidence=0.3,
                result_callback=self._pose_callback,
            )
            self.pose_landmarker = vision.PoseLandmarker.create_from_options(pose_options)

            self.model_loaded = True
            logger.info("MediaPipe models loaded")
            return True
        except Exception as e:
            logger.error("Failed to load MediaPipe models: %s", e)
            self.model_loaded = False
            return False

    def _face_callback(self, result, image, timestamp_ms):
        face = landmarks_from_face_results(result.face_landmarks)
        with self._landmark_lock:
            self._last_face = face
            merged = merge_landmarks(self._last_face, self._last_pose)
            self.last_landmarks = merged if merged.landmarks else None

    def _pose_callback(self, result, image, timestamp_ms):
        pose = landmarks_from_pose_results(result.pose_landmarks)
        with self._landmark_lock:
            self._last_pose = pose
            merged = merge_landmarks(self._last_face, self._last_pose)
            self.last_landmarks = merged if merged.landmarks else None

    def process_frame(self, frame: np.ndarray) -> tuple[LandmarkSet | None, np.ndarray]:
        annotated = frame.copy()
        timestamp = time.monotonic_ns() // 1_000_000

        if self.model_loaded and not DEMO_MODE:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = mp_image(image_format=mp.ImageFormat.SRGB, data=rgb)
            try:
                self.face_landmarker.detect_async(image, timestamp)
                self.pose_landmarker.detect_async(image, timestamp)
            except Exception as e:
                logger.debug("Detection error: %s", e)
        elif DEMO_MODE:
            with self._landmark_lock:
                self.last_landmarks = self._demo_provider.get_landmarks()
            cv2.putText(
                annotated,
                "DEMO MODE",
                (10, FRAME_HEIGHT - 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (100, 100, 100),
                2,
            )

        with self._landmark_lock:
            landmarks = self.last_landmarks

        if landmarks is not None:
            annotated = self._draw_landmarks(annotated, landmarks)

        return landmarks, annotated

    def _draw_landmarks(self, frame: np.ndarray, landmarks: LandmarkSet) -> np.ndarray:
        h, w = frame.shape[:2]
        for lm in landmarks.landmarks.values():
            x, y = int(lm.x * w), int(lm.y * h)
            cv2.circle(frame, (x, y), 3, (0, 255, 0), -1)

        ls = landmarks.get_pos("left_shoulder")
        rs = landmarks.get_pos("right_shoulder")
        nose = landmarks.get_pos("nose_tip")
        chin = landmarks.get_pos("chin")
        if ls and rs:
            a = (int(ls[0] * w), int(ls[1] * h))
            b = (int(rs[0] * w), int(rs[1] * h))
            cv2.line(frame, a, b, (255, 0, 0), 2)
        if nose and chin:
            a = (int(nose[0] * w), int(nose[1] * h))
            b = (int(chin[0] * w), int(chin[1] * h))
            cv2.line(frame, a, b, (0, 255, 255), 2)

        cv2.putText(
            frame,
            f"FPS: {self.camera.current_fps:.1f}",
            (10, 25),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 0),
            2,
        )
        return frame

    def release(self):
        if self.face_landmarker:
            self.face_landmarker.close()
        if self.pose_landmarker:
            self.pose_landmarker.close()
        self.camera.release()


class DemoLandmarkProvider:
    def __init__(self):
        self.time_offset = time.time()

    def get_landmarks(self) -> LandmarkSet:
        t = time.time() - self.time_offset
        phase = t % 40.0
        if 10.0 < phase < 18.0:
            tilt_deg = 12.0
        elif 22.0 < phase < 30.0:
            tilt_deg = 4.0
        else:
            tilt_deg = 1.5

        theta = math.radians(tilt_deg)
        hw = 0.05
        left_eye = (0.5 - hw * math.cos(theta), 0.40 - hw * math.sin(theta))
        right_eye = (0.5 + hw * math.cos(theta), 0.40 + hw * math.sin(theta))
        nose_offset = 0.5 * 0.1 * math.tan(theta)

        face = {
            "nose_tip": Landmark2D(x=0.5 + nose_offset, y=0.42, visibility=1, presence=1),
            "nose_bridge": Landmark2D(x=0.5 + nose_offset * 0.7, y=0.38, visibility=1, presence=1),
            "left_eye_outer": Landmark2D(x=left_eye[0], y=left_eye[1], visibility=1, presence=1),
            "right_eye_outer": Landmark2D(x=right_eye[0], y=right_eye[1], visibility=1, presence=1),
            "left_ear": Landmark2D(x=0.43 - hw * math.sin(theta), y=0.43 + hw * math.sin(theta) * 0.5, visibility=1, presence=1),
            "right_ear": Landmark2D(x=0.57 + hw * math.sin(theta), y=0.43 - hw * math.sin(theta) * 0.5, visibility=1, presence=1),
            "chin": Landmark2D(x=0.5 + nose_offset, y=0.48, visibility=1, presence=1),
            "forehead": Landmark2D(x=0.5 + nose_offset * 0.5, y=0.34, visibility=1, presence=1),
        }

        offset = phase * 0.005 - 0.1
        if phase > 30.0:
            offset = -0.08

        pose = {
            "left_shoulder": Landmark2D(x=0.42 + offset, y=0.68, visibility=1, presence=1),
            "right_shoulder": Landmark2D(x=0.58 - offset, y=0.68, visibility=1, presence=1),
            "nose": Landmark2D(x=0.5 + offset * 0.5, y=0.42, visibility=1, presence=1),
            "left_eye": Landmark2D(x=0.46, y=0.40, visibility=1, presence=1),
            "right_eye": Landmark2D(x=0.54, y=0.40, visibility=1, presence=1),
            "left_ear": Landmark2D(x=0.43, y=0.42, visibility=1, presence=1),
            "right_ear": Landmark2D(x=0.57, y=0.42, visibility=1, presence=1),
        }

        merged = {}
        merged.update(face)
        merged.update(pose)
        return LandmarkSet(landmarks=merged)
