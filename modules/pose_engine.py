"""
pose_engine.py
Wraps MediaPipe Pose and provides joint-angle geometry helpers.
No Streamlit dependency -> independently testable.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Tuple
import math

try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except ImportError:  # pragma: no cover - environment without mediapipe
    MEDIAPIPE_AVAILABLE = False

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:  # pragma: no cover
    CV2_AVAILABLE = False


@dataclass
class Landmark:
    x: float
    y: float
    z: float = 0.0
    visibility: float = 1.0


def calculate_angle(a: Tuple[float, float], b: Tuple[float, float], c: Tuple[float, float]) -> float:
    """
    Calculate the angle (in degrees) at point b, formed by points a-b-c.
    Pure geometry, no external dependency -> safe to unit test.
    """
    ax, ay = a
    bx, by = b
    cx, cy = c

    ba = (ax - bx, ay - by)
    bc = (cx - bx, cy - by)

    dot = ba[0] * bc[0] + ba[1] * bc[1]
    mag_ba = math.hypot(*ba)
    mag_bc = math.hypot(*bc)

    if mag_ba == 0 or mag_bc == 0:
        return 0.0

    cos_angle = max(-1.0, min(1.0, dot / (mag_ba * mag_bc)))
    angle = math.degrees(math.acos(cos_angle))
    return angle


class PoseEngine:
    """
    Thin wrapper around MediaPipe Pose. Falls back gracefully when
    mediapipe/opencv are not installed (e.g. constrained environments),
    so the rest of the app can still be imported and its logic tested.
    """

    LANDMARK_NAMES = [
        "nose", "left_eye_inner", "left_eye", "left_eye_outer",
        "right_eye_inner", "right_eye", "right_eye_outer",
        "left_ear", "right_ear", "mouth_left", "mouth_right",
        "left_shoulder", "right_shoulder", "left_elbow", "right_elbow",
        "left_wrist", "right_wrist", "left_pinky", "right_pinky",
        "left_index", "right_index", "left_thumb", "right_thumb",
        "left_hip", "right_hip", "left_knee", "right_knee",
        "left_ankle", "right_ankle", "left_heel", "right_heel",
        "left_foot_index", "right_foot_index",
    ]

    def __init__(self, min_detection_confidence: float = 0.6, min_tracking_confidence: float = 0.6):
        self.available = MEDIAPIPE_AVAILABLE and CV2_AVAILABLE
        self._pose = None
        if self.available:
            self._mp_pose = mp.solutions.pose
            self._pose = self._mp_pose.Pose(
                min_detection_confidence=min_detection_confidence,
                min_tracking_confidence=min_tracking_confidence,
            )

    def process_frame(self, frame_bgr) -> Optional[dict]:
        """
        Runs pose detection on a single BGR frame (numpy array from OpenCV).
        Returns a dict of {landmark_name: Landmark} or None if unavailable /
        no person detected.
        """
        if not self.available or self._pose is None:
            return None

        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        results = self._pose.process(rgb)
        if not results.pose_landmarks:
            return None

        landmarks = {}
        for name, lm in zip(self.LANDMARK_NAMES, results.pose_landmarks.landmark):
            landmarks[name] = Landmark(x=lm.x, y=lm.y, z=lm.z, visibility=lm.visibility)
        return landmarks

    def close(self):
        if self._pose is not None:
            self._pose.close()


def landmark_visible(lm: Optional[Landmark], threshold: float = 0.5) -> bool:
    return lm is not None and lm.visibility >= threshold
