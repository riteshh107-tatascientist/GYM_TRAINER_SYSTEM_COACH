"""
exercise_engine.py
Bridges pose landmarks -> joint angles -> RepCounter -> FormAnalyzer for
each of the 8 supported exercises. No Streamlit dependency -> unit testable
with synthetic landmark dictionaries.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Optional

from modules.pose_engine import Landmark, calculate_angle, landmark_visible
from modules.rep_counter import RepCounter, PlankTimer
from modules import form_analyzer

SUPPORTED_EXERCISES = {
    "squat": "Squat",
    "bicep_curl": "Bicep Curl",
    "pushup": "Push-up",
    "shoulder_press": "Shoulder Press",
    "lunge": "Lunge",
    "plank": "Plank",
    "jumping_jack": "Jumping Jacks",
    "situp": "Sit-up",
}

EXERCISE_PRIMARY_JOINTS = {
    "squat": "Hip -> Knee -> Ankle (knee angle)",
    "bicep_curl": "Shoulder -> Elbow -> Wrist (elbow angle)",
    "pushup": "Shoulder -> Elbow -> Wrist and Shoulder -> Hip -> Knee",
    "shoulder_press": "Shoulder -> Elbow -> Wrist (elbow angle)",
    "lunge": "Hip -> Knee -> Ankle (front + back knee)",
    "plank": "Shoulder -> Hip -> Ankle (body line)",
    "jumping_jack": "Shoulder -> Elbow -> Wrist / Hip -> Ankle spread",
    "situp": "Shoulder -> Hip -> Knee (torso angle)",
}


def _xy(lm: Landmark) -> tuple:
    return (lm.x, lm.y)


@dataclass
class FrameResult:
    ok: bool
    message: str = ""
    state: Optional[str] = None
    reps: int = 0
    correct_reps: int = 0
    incorrect_reps: int = 0
    rep_completed: bool = False
    form_score: Optional[float] = None
    breakdown: Dict[str, float] = field(default_factory=dict)
    feedback: list = field(default_factory=list)
    hold_seconds: float = 0.0


class ExerciseSession:
    """Stateful session for a single exercise over multiple frames."""

    def __init__(self, exercise_key: str):
        if exercise_key not in SUPPORTED_EXERCISES:
            raise ValueError(f"Unsupported exercise: {exercise_key}")
        self.exercise_key = exercise_key
        self.is_plank = exercise_key == "plank"
        self.rep_counter = None if self.is_plank else RepCounter(exercise_key)
        self.plank_timer = PlankTimer() if self.is_plank else None
        self._last_form: Optional[form_analyzer.FormResult] = None

    def process_landmarks(self, landmarks: Dict[str, Landmark], dt_seconds: float = 0.0) -> FrameResult:
        required_missing = self._missing_required_landmarks(landmarks)
        if required_missing:
            return FrameResult(ok=False, message=f"Cannot see: {', '.join(required_missing)}. Adjust your position.")

        try:
            if self.exercise_key == "squat":
                return self._process_squat(landmarks)
            if self.exercise_key == "bicep_curl":
                return self._process_bicep_curl(landmarks)
            if self.exercise_key == "pushup":
                return self._process_pushup(landmarks)
            if self.exercise_key == "shoulder_press":
                return self._process_shoulder_press(landmarks)
            if self.exercise_key == "lunge":
                return self._process_lunge(landmarks)
            if self.exercise_key == "plank":
                return self._process_plank(landmarks, dt_seconds)
            if self.exercise_key == "jumping_jack":
                return self._process_jumping_jack(landmarks)
            if self.exercise_key == "situp":
                return self._process_situp(landmarks)
        except Exception as exc:  # defensive: never crash the app on one bad frame
            return FrameResult(ok=False, message=f"Frame processing error: {exc}")

        return FrameResult(ok=False, message="Unsupported exercise.")

    def _missing_required_landmarks(self, landmarks: Dict[str, Landmark]) -> list:
        required_by_exercise = {
            "squat": ["left_hip", "left_knee", "left_ankle"],
            "bicep_curl": ["left_shoulder", "left_elbow", "left_wrist"],
            "pushup": ["left_shoulder", "left_elbow", "left_wrist", "left_hip"],
            "shoulder_press": ["left_shoulder", "left_elbow", "left_wrist"],
            "lunge": ["left_hip", "left_knee", "left_ankle", "right_knee"],
            "plank": ["left_shoulder", "left_hip", "left_ankle"],
            "jumping_jack": ["left_shoulder", "left_elbow", "left_hip", "left_ankle", "right_ankle"],
            "situp": ["left_shoulder", "left_hip", "left_knee"],
        }
        needed = required_by_exercise.get(self.exercise_key, [])
        missing = [n for n in needed if not landmark_visible(landmarks.get(n))]
        return missing

    def _process_squat(self, lm) -> FrameResult:
        knee_angle = calculate_angle(_xy(lm["left_hip"]), _xy(lm["left_knee"]), _xy(lm["left_ankle"]))
        hip_angle = calculate_angle(_xy(lm["left_shoulder"]), _xy(lm["left_hip"]), _xy(lm["left_knee"])) if landmark_visible(lm.get("left_shoulder")) else 90.0
        torso_lean = abs(90 - hip_angle)

        form_ok = knee_angle <= 110
        counter_result = self.rep_counter.update(knee_angle, form_ok=True)
        form = form_analyzer.analyze_squat(knee_angle, hip_angle, torso_lean)

        return FrameResult(ok=True, state=counter_result["state"], reps=counter_result["reps"],
                            correct_reps=counter_result["correct_reps"], incorrect_reps=counter_result["incorrect_reps"],
                            rep_completed=counter_result["rep_completed"], form_score=form.score,
                            breakdown=form.breakdown, feedback=form.feedback)

    def _process_bicep_curl(self, lm) -> FrameResult:
        elbow_angle = calculate_angle(_xy(lm["left_shoulder"]), _xy(lm["left_elbow"]), _xy(lm["left_wrist"]))
        shoulder_sway = 5.0
        control_score = 85.0

        counter_result = self.rep_counter.update(elbow_angle, form_ok=True)
        form = form_analyzer.analyze_bicep_curl(elbow_angle, shoulder_sway, control_score)

        return FrameResult(ok=True, state=counter_result["state"], reps=counter_result["reps"],
                            correct_reps=counter_result["correct_reps"], incorrect_reps=counter_result["incorrect_reps"],
                            rep_completed=counter_result["rep_completed"], form_score=form.score,
                            breakdown=form.breakdown, feedback=form.feedback)

    def _process_pushup(self, lm) -> FrameResult:
        elbow_angle = calculate_angle(_xy(lm["left_shoulder"]), _xy(lm["left_elbow"]), _xy(lm["left_wrist"]))
        body_line_angle = calculate_angle(_xy(lm["left_shoulder"]), _xy(lm["left_hip"]),
                                           _xy(lm.get("left_ankle", lm["left_hip"])))
        depth_angle = elbow_angle

        counter_result = self.rep_counter.update(elbow_angle, form_ok=True)
        form = form_analyzer.analyze_pushup(elbow_angle, body_line_angle, depth_angle)

        return FrameResult(ok=True, state=counter_result["state"], reps=counter_result["reps"],
                            correct_reps=counter_result["correct_reps"], incorrect_reps=counter_result["incorrect_reps"],
                            rep_completed=counter_result["rep_completed"], form_score=form.score,
                            breakdown=form.breakdown, feedback=form.feedback)

    def _process_shoulder_press(self, lm) -> FrameResult:
        elbow_angle = calculate_angle(_xy(lm["left_shoulder"]), _xy(lm["left_elbow"]), _xy(lm["left_wrist"]))
        torso_lean = 5.0

        counter_result = self.rep_counter.update(elbow_angle, form_ok=True)
        form = form_analyzer.analyze_shoulder_press(elbow_angle, torso_lean, elbow_angle)

        return FrameResult(ok=True, state=counter_result["state"], reps=counter_result["reps"],
                            correct_reps=counter_result["correct_reps"], incorrect_reps=counter_result["incorrect_reps"],
                            rep_completed=counter_result["rep_completed"], form_score=form.score,
                            breakdown=form.breakdown, feedback=form.feedback)

    def _process_lunge(self, lm) -> FrameResult:
        front_knee_angle = calculate_angle(_xy(lm["left_hip"]), _xy(lm["left_knee"]), _xy(lm["left_ankle"]))
        back_knee_angle = calculate_angle(_xy(lm.get("right_hip", lm["left_hip"])), _xy(lm["right_knee"]),
                                           _xy(lm.get("right_ankle", lm["left_ankle"])))
        torso_lean = 5.0

        counter_result = self.rep_counter.update(front_knee_angle, form_ok=True)
        form = form_analyzer.analyze_lunge(front_knee_angle, torso_lean, back_knee_angle)

        return FrameResult(ok=True, state=counter_result["state"], reps=counter_result["reps"],
                            correct_reps=counter_result["correct_reps"], incorrect_reps=counter_result["incorrect_reps"],
                            rep_completed=counter_result["rep_completed"], form_score=form.score,
                            breakdown=form.breakdown, feedback=form.feedback)

    def _process_plank(self, lm, dt_seconds: float) -> FrameResult:
        hip_align = calculate_angle(_xy(lm["left_shoulder"]), _xy(lm["left_hip"]), _xy(lm["left_ankle"]))
        form_ok = 160 <= hip_align <= 200
        self.plank_timer.tick(dt_seconds, form_ok)
        form = form_analyzer.analyze_plank(hip_align, self.plank_timer.total_seconds, target_seconds=60)

        return FrameResult(ok=True, state="HOLDING" if self.plank_timer.is_holding else "BROKEN",
                            hold_seconds=round(self.plank_timer.total_seconds, 1),
                            form_score=form.score, breakdown=form.breakdown, feedback=form.feedback)

    def _process_jumping_jack(self, lm) -> FrameResult:
        arm_angle = calculate_angle(_xy(lm["left_hip"]), _xy(lm["left_shoulder"]), _xy(lm["left_elbow"]))
        ankle_spread = abs(lm["left_ankle"].x - lm["right_ankle"].x)
        leg_spread_ratio = min(ankle_spread / 0.3, 1.0)
        sync_score = 85.0

        counter_result = self.rep_counter.update(arm_angle, form_ok=True)
        form = form_analyzer.analyze_jumping_jack(arm_angle, leg_spread_ratio, sync_score)

        return FrameResult(ok=True, state=counter_result["state"], reps=counter_result["reps"],
                            correct_reps=counter_result["correct_reps"], incorrect_reps=counter_result["incorrect_reps"],
                            rep_completed=counter_result["rep_completed"], form_score=form.score,
                            breakdown=form.breakdown, feedback=form.feedback)

    def _process_situp(self, lm) -> FrameResult:
        torso_angle = calculate_angle(_xy(lm["left_shoulder"]), _xy(lm["left_hip"]), _xy(lm["left_knee"]))
        control_score = 85.0

        counter_result = self.rep_counter.update(torso_angle, form_ok=True)
        form = form_analyzer.analyze_situp(torso_angle, control_score)

        return FrameResult(ok=True, state=counter_result["state"], reps=counter_result["reps"],
                            correct_reps=counter_result["correct_reps"], incorrect_reps=counter_result["incorrect_reps"],
                            rep_completed=counter_result["rep_completed"], form_score=form.score,
                            breakdown=form.breakdown, feedback=form.feedback)
