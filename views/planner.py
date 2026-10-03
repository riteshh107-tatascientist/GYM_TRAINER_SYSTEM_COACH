import streamlit as st
from modules.workout_planner import generate_plan


def render():
    st.markdown('<h1 class="gt-gradient-text">AI Workout Planner</h1>', unsafe_allow_html=True)
    st.write("Answer a few questions and get a structured weekly training plan.")

    c1, c2 = st.columns(2)
    goal = c1.selectbox("Goal", ["Strength", "Muscle Building", "General Fitness", "Endurance"])
    experience = c2.selectbox("Experience", ["Beginner", "Intermediate", "Advanced"])

    c3, c4 = st.columns(2)
    days = c3.selectbox("Days per week", [3, 4, 5, 6])
    equipment = c4.selectbox("Equipment", ["Bodyweight", "Dumbbells", "Full Gym"])

    duration = st.select_slider("Session duration (minutes)", options=[20, 30, 45, 60], value=30)

    if st.button("Generate My Plan", use_container_width=True):
        plan = generate_plan(goal, experience, days, equipment, duration)
        st.session_state["generated_plan"] = plan

    plan = st.session_state.get("generated_plan")
    if plan:
        st.markdown('<div class="gt-section-title">Your Weekly Plan</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="gt-card">Goal: <strong>{plan.goal}</strong> · Experience: <strong>{plan.experience}</strong> '
            f'· {plan.days_per_week} days/week · Equipment: <strong>{plan.equipment}</strong> · '
            f'~{plan.duration_minutes} min/session<br>{plan.rest_guidance}</div>',
            unsafe_allow_html=True,
        )
        for day in plan.days:
            st.markdown(f'<div class="gt-section-title">DAY {day.day_number} — {day.focus}</div>',
                         unsafe_allow_html=True)
            rows = "".join(
                f"<tr><td style='padding:0.4rem 0.8rem;'>{ex['exercise']}</td>"
                f"<td style='padding:0.4rem 0.8rem;'>{ex['sets']}</td>"
                f"<td style='padding:0.4rem 0.8rem;'>{ex['reps']}</td></tr>"
                for ex in day.exercises
            )
            st.markdown(
                f"""
                <div class="gt-card">
                <table style="width:100%; border-collapse:collapse;">
                <tr style="color:#9aa5ab; text-align:left;">
                    <th style="padding:0.4rem 0.8rem;">Exercise</th>
                    <th style="padding:0.4rem 0.8rem;">Sets</th>
                    <th style="padding:0.4rem 0.8rem;">Reps</th>
                </tr>
                {rows}
                </table>
                </div>
                """,
                unsafe_allow_html=True,
            )
        st.markdown(f'<div class="gt-disclaimer">{plan.disclaimer}</div>', unsafe_allow_html=True)
