"""
form_analyzer.py
Rule-based form scoring. Produces a 0-100 score plus a component breakdown
and human-readable feedback strings, per exercise. This is explicitly
labeled as fitness guidance, not medical advice (enforced at the UI layer).
No Streamlit dependency -> unit testable.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class FormResult:
    score: float
    breakdown: Dict[str, float]
    feedback: List[str] = field(default_factory=list)


def _clamp(value: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, value))


def _score_from_target(value: float, target: float, tolerance: float) -> float:
    """Linear falloff score: 100 at target, 0 at target +/- tolerance*2."""
    diff = abs(value - target)
    if diff <= tolerance:
        return 100.0
    score = 100.0 - ((diff - tolerance) / tolerance) * 50.0
    return _clamp(score)


def analyze_squat(knee_angle: float, hip_angle: float, torso_lean: float) -> FormResult:
    depth = _score_from_target(knee_angle, target=95, tolerance=25)
    hip_depth = _score_from_target(hip_angle, target=90, tolerance=30)
    torso = _score_from_target(torso_lean, target=10, tolerance=15)

    breakdown = {"Depth": depth, "Hip Depth": hip_depth, "Torso Stability": torso}
    score = sum(breakdown.values()) / len(breakdown)

    feedback = []
    feedback.append("Good squat depth." if depth >= 80 else "Try squatting a little deeper for full range of motion.")
    feedback.append("Solid hip hinge." if hip_depth >= 80 else "Sit back more through the hips as you descend.")
    feedback.append("Torso stayed upright and stable." if torso >= 80 else "Try maintaining a more stable, upright torso.")
    return FormResult(score=round(score, 1), breakdown={k: round(v, 1) for k, v in breakdown.items()}, feedback=feedback)


def analyze_bicep_curl(elbow_angle: float, shoulder_sway: float, control_score: float) -> FormResult:
    range_of_motion = _score_from_target(elbow_angle, target=45, tolerance=30)
    shoulder_stability = _score_from_target(shoulder_sway, target=5, tolerance=10)
    control = _clamp(control_score)

    breakdown = {"Range of Motion": range_of_motion, "Shoulder Stability": shoulder_stability, "Movement Control": control}
    score = sum(breakdown.values()) / len(breakdown)

    feedback = []
    feedback.append("Great full range of motion on the curl." if range_of_motion >= 80 else "Curl a little higher for full contraction.")
    feedback.append("Elbow stayed stable and close to the torso." if shoulder_stability >= 80 else "Keep your elbow pinned — avoid swinging your shoulder.")
    feedback.append("Controlled tempo throughout." if control >= 80 else "Slow down the lowering (eccentric) phase for better control.")
    return FormResult(score=round(score, 1), breakdown={k: round(v, 1) for k, v in breakdown.items()}, feedback=feedback)


def analyze_pushup(elbow_angle: float, body_line_angle: float, depth_angle: float) -> FormResult:
    depth = _score_from_target(depth_angle, target=90, tolerance=25)
    body_line = _score_from_target(body_line_angle, target=180, tolerance=15)
    lockout = _score_from_target(elbow_angle, target=170, tolerance=20)

    breakdown = {"Depth": depth, "Body Alignment": body_line, "Lockout": lockout}
    score = sum(breakdown.values()) / len(breakdown)

    feedback = []
    feedback.append("Good chest-to-floor depth." if depth >= 80 else "Lower your chest closer to the floor.")
    feedback.append("Body stayed in a straight line." if body_line >= 80 else "Avoid sagging or piking your hips — keep a straight body line.")
    feedback.append("Full lockout at the top." if lockout >= 80 else "Extend your arms fully at the top of each rep.")
    return FormResult(score=round(score, 1), breakdown={k: round(v, 1) for k, v in breakdown.items()}, feedback=feedback)


def analyze_shoulder_press(elbow_angle: float, torso_lean: float, lockout_angle: float) -> FormResult:
    press_path = _score_from_target(elbow_angle, target=90, tolerance=25)
    torso = _score_from_target(torso_lean, target=5, tolerance=10)
    lockout = _score_from_target(lockout_angle, target=170, tolerance=20)

    breakdown = {"Press Path": press_path, "Torso Stability": torso, "Lockout": lockout}
    score = sum(breakdown.values()) / len(breakdown)

    feedback = []
    feedback.append("Clean vertical press path." if press_path >= 80 else "Keep the press moving in a straight vertical line.")
    feedback.append("Core stayed braced and upright." if torso >= 80 else "Avoid leaning back — brace your core through the press.")
    feedback.append("Full overhead lockout." if lockout >= 80 else "Extend fully overhead at the top of the rep.")
    return FormResult(score=round(score, 1), breakdown={k: round(v, 1) for k, v in breakdown.items()}, feedback=feedback)


def analyze_lunge(front_knee_angle: float, torso_lean: float, back_knee_angle: float) -> FormResult:
    depth = _score_from_target(front_knee_angle, target=90, tolerance=25)
    torso = _score_from_target(torso_lean, target=5, tolerance=12)
    back_knee = _score_from_target(back_knee_angle, target=100, tolerance=25)

    breakdown = {"Front Knee Depth": depth, "Torso Stability": torso, "Back Knee Position": back_knee}
    score = sum(breakdown.values()) / len(breakdown)

    feedback = []
    feedback.append("Great front knee depth." if depth >= 80 else "Lower until your front thigh is closer to parallel with the floor.")
    feedback.append("Upright, stable torso." if torso >= 80 else "Keep your chest up and avoid leaning forward.")
    feedback.append("Good back knee control." if back_knee >= 80 else "Lower the back knee closer to the floor with control.")
    return FormResult(score=round(score, 1), breakdown={k: round(v, 1) for k, v in breakdown.items()}, feedback=feedback)


def analyze_plank(hip_alignment_angle: float, hold_seconds: float, target_seconds: float) -> FormResult:
    alignment = _score_from_target(hip_alignment_angle, target=180, tolerance=12)
    endurance = _clamp((hold_seconds / max(target_seconds, 1)) * 100)

    breakdown = {"Body Alignment": alignment, "Hold Duration": round(endurance, 1)}
    score = sum(breakdown.values()) / len(breakdown)

    feedback = []
    feedback.append("Excellent straight-line plank position." if alignment >= 80 else "Keep your hips level — avoid sagging or piking.")
    feedback.append("Great endurance on the hold." if endurance >= 80 else "Keep building your hold duration over time.")
    return FormResult(score=round(score, 1), breakdown={k: round(v, 1) for k, v in breakdown.items()}, feedback=feedback)


def analyze_situp(torso_angle: float, control_score: float) -> FormResult:
    range_of_motion = _score_from_target(torso_angle, target=45, tolerance=25)
    control = _clamp(control_score)

    breakdown = {"Range of Motion": range_of_motion, "Movement Control": control}
    score = sum(breakdown.values()) / len(breakdown)

    feedback = []
    feedback.append("Good full crunch range." if range_of_motion >= 80 else "Curl up further for a fuller contraction.")
    feedback.append("Smooth, controlled tempo." if control >= 80 else "Avoid using momentum — control both directions of the rep.")
    return FormResult(score=round(score, 1), breakdown={k: round(v, 1) for k, v in breakdown.items()}, feedback=feedback)


def analyze_jumping_jack(arm_spread_angle: float, leg_spread_ratio: float, sync_score: float) -> FormResult:
    arms = _score_from_target(arm_spread_angle, target=160, tolerance=25)
    legs = _clamp(leg_spread_ratio * 100)
    sync = _clamp(sync_score)

    breakdown = {"Arm Extension": arms, "Leg Spread": round(legs, 1), "Arm-Leg Sync": sync}
    score = sum(breakdown.values()) / len(breakdown)

    feedback = []
    feedback.append("Full arm extension overhead." if arms >= 80 else "Raise your arms fully overhead.")
    feedback.append("Good wide leg spread." if legs >= 80 else "Widen your leg spread for a fuller range of motion.")
    feedback.append("Arms and legs moving in sync." if sync >= 80 else "Try to time your arm and leg movement together.")
    return FormResult(score=round(score, 1), breakdown={k: round(v, 1) for k, v in breakdown.items()}, feedback=feedback)


FORM_DISCLAIMER = "Fitness guidance only — not medical advice."
