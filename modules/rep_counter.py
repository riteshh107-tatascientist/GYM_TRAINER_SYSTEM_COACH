"""
rep_counter.py
State-machine based repetition counting. A rep is only counted after a full
UP -> DOWN -> UP (or DOWN -> UP -> DOWN) cycle crosses configured angle
thresholds, so noisy single-frame angle jitter can't inflate the count.
No Streamlit / CV dependency -> fully unit testable.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Literal

State = Literal["UP", "DOWN", "UNKNOWN"]


@dataclass
class ExerciseThresholds:
    """Angle thresholds (degrees) that define the two end states of a rep."""
    down_angle: float   # angle at/below which the exercise is considered "DOWN"
    up_angle: float      # angle at/above which the exercise is considered "UP"
    lower_is_down: bool = True  # True: smaller angle = DOWN (e.g. squat knee)


# Reference thresholds per exercise, tuned to typical body-angle ranges.
EXERCISE_THRESHOLDS: dict[str, ExerciseThresholds] = {
    "squat": ExerciseThresholds(down_angle=100, up_angle=160),
    "bicep_curl": ExerciseThresholds(down_angle=155, up_angle=60, lower_is_down=False),
    "pushup": ExerciseThresholds(down_angle=95, up_angle=160),
    "shoulder_press": ExerciseThresholds(down_angle=90, up_angle=160, lower_is_down=False),
    "lunge": ExerciseThresholds(down_angle=100, up_angle=165),
    "situp": ExerciseThresholds(down_angle=70, up_angle=140, lower_is_down=False),
    "jumping_jack": ExerciseThresholds(down_angle=25, up_angle=150, lower_is_down=False),
    # plank is a hold, not a rep-based exercise; handled separately
}


class RepCounter:
    def __init__(self, exercise_key: str):
        if exercise_key not in EXERCISE_THRESHOLDS and exercise_key != "plank":
            raise ValueError(f"Unknown exercise: {exercise_key}")
        self.exercise_key = exercise_key
        self.state: State = "UNKNOWN"
        self.reps = 0
        self.correct_reps = 0
        self.incorrect_reps = 0
        self._pending_form_ok = True

    def _classify(self, angle: float) -> State:
        th = EXERCISE_THRESHOLDS[self.exercise_key]
        if th.lower_is_down:
            if angle <= th.down_angle:
                return "DOWN"
            if angle >= th.up_angle:
                return "UP"
        else:
            if angle >= th.down_angle:
                return "DOWN"
            if angle <= th.up_angle:
                return "UP"
        return self.state if self.state != "UNKNOWN" else "UP"

    def update(self, angle: float, form_ok: bool = True) -> dict:
        """
        Feed the latest primary joint angle for this frame.
        A rep completes on a DOWN -> UP transition (the "return to start").
        Returns a dict describing what happened this frame.
        """
        if self.exercise_key == "plank":
            raise RuntimeError("Plank is a hold exercise; use PlankTimer instead.")

        new_state = self._classify(angle)
        rep_completed = False

        if new_state == "DOWN" and self.state != "DOWN":
            self._pending_form_ok = form_ok
        elif new_state == "DOWN":
            self._pending_form_ok = self._pending_form_ok and form_ok

        if self.state == "DOWN" and new_state == "UP":
            self.reps += 1
            rep_completed = True
            if self._pending_form_ok and form_ok:
                self.correct_reps += 1
            else:
                self.incorrect_reps += 1
            self._pending_form_ok = True

        self.state = new_state
        return {
            "state": self.state,
            "reps": self.reps,
            "correct_reps": self.correct_reps,
            "incorrect_reps": self.incorrect_reps,
            "rep_completed": rep_completed,
        }

    def reset(self):
        self.state = "UNKNOWN"
        self.reps = 0
        self.correct_reps = 0
        self.incorrect_reps = 0
        self._pending_form_ok = True


class PlankTimer:
    """Tracks total held-plank seconds and whether the hold is currently valid."""

    def __init__(self):
        self.total_seconds = 0.0
        self.is_holding = False

    def tick(self, dt_seconds: float, form_ok: bool):
        if form_ok:
            self.total_seconds += dt_seconds
            self.is_holding = True
        else:
            self.is_holding = False

    def reset(self):
        self.total_seconds = 0.0
        self.is_holding = False
