import streamlit as st
import pandas as pd


def render(db, user):
    st.markdown('<h1 class="gt-gradient-text">Progress &amp; Workout History</h1>', unsafe_allow_html=True)

    history = db.get_workout_history(user["id"])
    if not history:
        st.markdown(
            '<div class="gt-card" style="text-align:center; padding:2.5rem;">'
            '<h3>No workout history yet</h3>'
            '<p style="color:#9aa5ab;">Your completed sessions will appear here.</p></div>',
            unsafe_allow_html=True,
        )
        return

    df = pd.DataFrame(history)
    df["created_at"] = pd.to_datetime(df["created_at"])
    df["date"] = df["created_at"].dt.date

    fc1, fc2, fc3 = st.columns(3)
    exercises = ["All"] + sorted(df["exercise"].unique().tolist())
    exercise_filter = fc1.selectbox("Filter by exercise", exercises)
    min_score = fc2.slider("Minimum form score", 0, 100, 0)
    date_sort = fc3.selectbox("Sort by date", ["Newest first", "Oldest first"])

    filtered = df.copy()
    if exercise_filter != "All":
        filtered = filtered[filtered["exercise"] == exercise_filter]
    filtered = filtered[filtered["form_score"] >= min_score]
    filtered = filtered.sort_values("created_at", ascending=(date_sort == "Oldest first"))

    st.markdown('<div class="gt-section-title">Session History</div>', unsafe_allow_html=True)
    display_df = filtered[["date", "exercise", "sets", "reps", "correct_reps", "incorrect_reps",
                            "form_score", "duration_seconds"]].rename(columns={
        "date": "Date", "exercise": "Exercise", "sets": "Sets", "reps": "Reps",
        "correct_reps": "Correct", "incorrect_reps": "Incorrect", "form_score": "Form Score",
        "duration_seconds": "Duration (s)",
    })
    st.dataframe(display_df, use_container_width=True, hide_index=True)

    st.markdown('<div class="gt-section-title">Progress Over Time</div>', unsafe_allow_html=True)
    import plotly.graph_objects as go
    trend = filtered.sort_values("created_at")
    fig = go.Figure(go.Scatter(x=trend["created_at"], y=trend["form_score"], mode="lines+markers",
                                line=dict(color="#00e6a8", width=3)))
    fig.update_layout(template="plotly_dark", height=320, margin=dict(l=10, r=10, t=10, b=10),
                       paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", yaxis=dict(range=[0, 100]))
    st.plotly_chart(fig, use_container_width=True)
