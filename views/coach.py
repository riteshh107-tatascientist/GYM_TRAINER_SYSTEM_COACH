import streamlit as st
from modules.ai_coach import build_coach_message


def render(db, user):
    st.markdown('<h1 class="gt-gradient-text">AI Coach</h1>', unsafe_allow_html=True)
    st.write("Your AI Coach reviews your most recent workout and gives you prioritized, specific feedback.")

    history = db.get_workout_history(user["id"])
    if not history:
        st.markdown(
            '<div class="gt-card" style="text-align:center; padding:2.5rem;">'
            '<h3>No sessions yet</h3><p style="color:#9aa5ab;">Complete an AI Workout to get your first coaching summary.</p>'
            '</div>', unsafe_allow_html=True,
        )
        return

    latest = history[0]
    st.markdown('<div class="gt-section-title">Latest Session</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.metric("Exercise", latest["exercise"])
    c2.metric("Reps", latest["reps"])
    c3.metric("Form Score", f'{latest["form_score"]:.0f}%')

    coach_msg = build_coach_message(
        exercise_name=latest["exercise"], reps=latest["reps"] or 0,
        correct_reps=latest["correct_reps"] or 0, incorrect_reps=latest["incorrect_reps"] or 0,
        avg_form_score=latest["form_score"] or 0, feedback_points=[],
    )
    st.markdown(f'<div class="gt-card"><h4>🤖 Coach Feedback</h4><p style="white-space:pre-line;">{coach_msg}</p></div>',
                 unsafe_allow_html=True)

    st.markdown('<div class="gt-section-title">Overall Trends</div>', unsafe_allow_html=True)
    avg_score = sum(h["form_score"] or 0 for h in history) / len(history)
    if avg_score >= 85:
        trend_msg = "Your form has been consistently strong across sessions — keep it up!"
    elif avg_score >= 70:
        trend_msg = "Your form is solid overall, with room to tighten consistency between sessions."
    else:
        trend_msg = "Consider slowing your tempo and focusing on range of motion across sessions."
    st.markdown(f'<div class="gt-card">{trend_msg}</div>', unsafe_allow_html=True)
    st.markdown('<div class="gt-disclaimer">Fitness guidance only — not medical advice.</div>', unsafe_allow_html=True)
