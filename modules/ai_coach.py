"""
ai_coach.py
Rule-based coaching feedback generator (always available, no API key
required). Optionally enhances the message with an LLM call if an API key
is present in Streamlit secrets — this is purely additive and the app must
work correctly without it.
"""
from __future__ import annotations
from typing import Dict, List, Optional


def generate_rule_based_feedback(exercise_name: str, reps: int, correct_reps: int,
                                  incorrect_reps: int, avg_form_score: float,
                                  feedback_points: List[str]) -> str:
    lines = [f"Great work! You completed {reps} {exercise_name.lower()}{'s' if reps != 1 else ''}."]

    if reps > 0:
        accuracy = (correct_reps / reps) * 100
        if accuracy >= 90:
            lines.append("Your form consistency was excellent throughout the set.")
        elif accuracy >= 70:
            lines.append("Your movement consistency is good, with a few reps to tighten up.")
        else:
            lines.append("Focus on slowing down — several reps had inconsistent form.")

    if avg_form_score >= 90:
        lines.append(f"Average form score: {avg_form_score:.0f}% — outstanding technique.")
    elif avg_form_score >= 75:
        lines.append(f"Average form score: {avg_form_score:.0f}% — solid technique overall.")
    else:
        lines.append(f"Average form score: {avg_form_score:.0f}% — there's good room to sharpen your technique.")

    if feedback_points:
        lines.append("")
        lines.append("Focus on:")
        # de-duplicate while preserving order, cap at 3 for a digestible summary
        seen = set()
        unique_points = []
        for p in feedback_points:
            if p not in seen:
                seen.add(p)
                unique_points.append(p)
        for p in unique_points[:3]:
            lines.append(f"\u2022 {p}")

    return "\n".join(lines)


def get_llm_enhanced_feedback(base_feedback: str, exercise_name: str, api_key: Optional[str]) -> Optional[str]:
    """
    Optionally enhances feedback using an LLM if configured via st.secrets.
    Returns None if no key is configured or the call fails, so the caller
    should always fall back to `base_feedback`. Kept isolated from
    Streamlit so it can be unit tested with a mocked key/response.
    """
    if not api_key:
        return None

    try:
        import requests  # local import: optional dependency path only
        # NOTE: Placeholder for a Gemini/OpenAI-compatible endpoint.
        # Left intentionally conservative — real deployments should point
        # this at their configured provider. Any failure here must never
        # break the core app, hence the broad except below.
        raise NotImplementedError("Configure your LLM endpoint in ai_coach.py")
    except Exception:
        return None


def build_coach_message(exercise_name: str, reps: int, correct_reps: int, incorrect_reps: int,
                         avg_form_score: float, feedback_points: List[str],
                         llm_api_key: Optional[str] = None) -> str:
    base = generate_rule_based_feedback(exercise_name, reps, correct_reps, incorrect_reps,
                                         avg_form_score, feedback_points)
    enhanced = get_llm_enhanced_feedback(base, exercise_name, llm_api_key)
    return enhanced if enhanced else base
