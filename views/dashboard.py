import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from collections import defaultdict
from datetime import datetime

PLOT_TEMPLATE = "plotly_dark"
ACCENT = "#00e6a8"
ACCENT2 = "#22d3ee"


def _empty_state():
    st.markdown(
        '<div class="gt-card" style="text-align:center; padding:3rem;">'
        '<h3>No workouts yet</h3>'
        '<p style="color:#9aa5ab;">Complete your first AI Workout session to see your analytics here.</p>'
        '</div>', unsafe_allow_html=True,
    )


def render(db, user):
    st.markdown('<h1 class="gt-gradient-text">Your Dashboard</h1>', unsafe_allow_html=True)

    stats = db.get_dashboard_stats(user["id"])
    history = db.get_workout_history(user["id"])

    if stats["total_workouts"] == 0:
        _empty_state()
        return

    metrics = [
        ("Total Workouts", stats["total_workouts"]),
        ("Total Reps", stats["total_reps"]),
        ("Workout Minutes", stats["total_minutes"]),
        ("Avg Form Score", f'{stats["avg_form_score"]}%'),
        ("Best Exercise", stats["best_exercise"]),
        ("Current Streak", f'{stats["current_streak"]} days'),
    ]
    cols = st.columns(3)
    for i, (label, value) in enumerate(metrics):
        with cols[i % 3]:
            st.markdown(
                f'<div class="gt-card"><div class="gt-metric-value">{value}</div>'
                f'<div class="gt-metric-label">{label}</div></div>', unsafe_allow_html=True,
            )

    df = pd.DataFrame(history)
    df["created_at"] = pd.to_datetime(df["created_at"])
    df["date"] = df["created_at"].dt.date

    st.markdown('<div class="gt-section-title">Weekly Workout Duration</div>', unsafe_allow_html=True)
    daily_minutes = df.groupby("date")["duration_seconds"].sum() / 60.0
    fig1 = go.Figure(go.Bar(x=daily_minutes.index.astype(str), y=daily_minutes.values,
                             marker_color=ACCENT))
    fig1.update_layout(template=PLOT_TEMPLATE, height=320, margin=dict(l=10, r=10, t=10, b=10),
                        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig1, use_container_width=True)

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown('<div class="gt-section-title">Reps per Exercise</div>', unsafe_allow_html=True)
        reps_by_ex = df.groupby("exercise")["reps"].sum()
        fig2 = go.Figure(go.Bar(x=reps_by_ex.index, y=reps_by_ex.values, marker_color=ACCENT2))
        fig2.update_layout(template=PLOT_TEMPLATE, height=300, margin=dict(l=10, r=10, t=10, b=10),
                            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig2, use_container_width=True)

    with col_b:
        st.markdown('<div class="gt-section-title">Exercise Distribution</div>', unsafe_allow_html=True)
        dist = df["exercise"].value_counts()
        fig3 = go.Figure(go.Pie(labels=dist.index, values=dist.values, hole=0.55,
                                 marker=dict(colors=[ACCENT, ACCENT2, "#3b82f6", "#a78bfa", "#f472b6",
                                                      "#facc15", "#fb923c", "#f87171"])))
        fig3.update_layout(template=PLOT_TEMPLATE, height=300, margin=dict(l=10, r=10, t=10, b=10),
                            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig3, use_container_width=True)

    st.markdown('<div class="gt-section-title">Form Score Trend</div>', unsafe_allow_html=True)
    df_sorted = df.sort_values("created_at")
    fig4 = go.Figure(go.Scatter(x=df_sorted["created_at"], y=df_sorted["form_score"],
                                 mode="lines+markers", line=dict(color=ACCENT, width=3)))
    fig4.update_layout(template=PLOT_TEMPLATE, height=300, margin=dict(l=10, r=10, t=10, b=10),
                        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                        yaxis=dict(range=[0, 100]))
    st.plotly_chart(fig4, use_container_width=True)

    st.markdown('<div class="gt-section-title">Workout Frequency</div>', unsafe_allow_html=True)
    freq = df.groupby("date").size()
    fig5 = go.Figure(go.Bar(x=freq.index.astype(str), y=freq.values, marker_color=ACCENT2))
    fig5.update_layout(template=PLOT_TEMPLATE, height=280, margin=dict(l=10, r=10, t=10, b=10),
                        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig5, use_container_width=True)
