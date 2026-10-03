import streamlit as st
import base64
import os

FOUNDER_PHOTO_PATH = os.path.join(os.path.dirname(__file__), "..", "assets", "founder", "ritesh_founder.jpg")


def _founder_photo_base64():
    try:
        with open(FOUNDER_PHOTO_PATH, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    except FileNotFoundError:
        return None


def render():
    # ---------- HERO ----------
    st.markdown('<div class="gt-hero">', unsafe_allow_html=True)
    col1, col2 = st.columns([1.3, 1])
    with col1:
        st.markdown('<span class="gt-badge">AI-POWERED COMPUTER VISION FITNESS</span>', unsafe_allow_html=True)
        st.markdown('<h1 class="gt-gradient-text" style="font-size:3rem; margin-top:0.6rem;">GYMTRAINER AI</h1>',
                     unsafe_allow_html=True)
        st.markdown('<h3 style="color:#cfd8dc; font-weight:500;">Where Human Strength Meets Artificial Intelligence.</h3>',
                     unsafe_allow_html=True)
        st.write(
            "GymTrainer AI watches your movement through your camera, counts your reps with a "
            "real state-machine engine, scores your form, and coaches you like a personal trainer "
            "— all running on computer vision, not gimmicks."
        )
        b1, b2 = st.columns(2)
        with b1:
            if st.button("🏋️ Start AI Workout", use_container_width=True):
                st.session_state.nav = "AI Workout"
                st.rerun()
        with b2:
            if st.button("📚 Explore Exercises", use_container_width=True):
                st.session_state.nav = "Exercises"
                st.rerun()
    with col2:
        photo_b64 = _founder_photo_base64()
        st.markdown('<div class="gt-card" style="text-align:center;">', unsafe_allow_html=True)
        if photo_b64:
            st.markdown(
                f'<div class="gt-founder-photo"><img src="data:image/jpeg;base64,{photo_b64}" '
                f'width="180" style="object-fit:cover; height:180px;"></div>',
                unsafe_allow_html=True,
            )
        st.markdown('<p style="margin-top:0.8rem; font-weight:600;">Ritesh Kumar Singh</p>', unsafe_allow_html=True)
        st.markdown('<p style="color:#9aa5ab; font-size:0.85rem;">Founder &amp; Creator — GymTrainer AI</p>',
                     unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ---------- WHY GYMTRAINER AI ----------
    st.markdown('<div class="gt-section-title">Why GymTrainer AI?</div>', unsafe_allow_html=True)
    cols = st.columns(3)
    reasons = [
        ("🎯", "Real Computer Vision", "MediaPipe Pose tracks 33 body landmarks in real time — no fake counters."),
        ("🧠", "State-Machine Rep Counting", "Reps only count on a full UP → DOWN → UP cycle, eliminating false counts."),
        ("📊", "Honest Form Scoring", "Rule-based scoring against real joint angles, with a clear breakdown per rep."),
    ]
    for c, (icon, title, desc) in zip(cols, reasons):
        with c:
            st.markdown(f'<div class="gt-card"><h4>{icon} {title}</h4><p style="color:#9aa5ab;">{desc}</p></div>',
                         unsafe_allow_html=True)

    # ---------- AI FEATURES ----------
    st.markdown('<div class="gt-section-title">AI Features</div>', unsafe_allow_html=True)
    feats = st.columns(4)
    feature_list = [
        ("🎥", "Live Pose Analysis"), ("🔢", "Automatic Rep Counting"),
        ("📈", "Form Score Breakdown"), ("🤖", "AI Coach Feedback"),
    ]
    for c, (icon, title) in zip(feats, feature_list):
        with c:
            st.markdown(f'<div class="gt-card" style="text-align:center;"><h3>{icon}</h3><p>{title}</p></div>',
                         unsafe_allow_html=True)

    # ---------- SUPPORTED EXERCISES ----------
    st.markdown('<div class="gt-section-title">Supported Exercises</div>', unsafe_allow_html=True)
    exercises = ["Squat", "Bicep Curl", "Push-up", "Shoulder Press", "Lunges", "Plank", "Jumping Jacks", "Sit-ups"]
    ex_cols = st.columns(4)
    for i, ex in enumerate(exercises):
        with ex_cols[i % 4]:
            st.markdown(f'<div class="gt-card" style="text-align:center; margin-bottom:0.8rem;">💪<br>{ex}</div>',
                         unsafe_allow_html=True)

    # ---------- HOW IT WORKS ----------
    st.markdown('<div class="gt-section-title">How It Works</div>', unsafe_allow_html=True)
    steps = st.columns(4)
    step_text = [
        ("1", "Choose your exercise & targets"),
        ("2", "Let the camera or an uploaded video capture your movement"),
        ("3", "AI tracks joints, counts reps, and scores your form live"),
        ("4", "Review your AI Coach summary and save it to your history"),
    ]
    for c, (num, text) in zip(steps, step_text):
        with c:
            st.markdown(f'<div class="gt-card"><h3 class="gt-gradient-text">{num}</h3><p>{text}</p></div>',
                         unsafe_allow_html=True)

    # ---------- WORKOUT ANALYTICS TEASER ----------
    st.markdown('<div class="gt-section-title">Workout Analytics</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="gt-card">Track total workouts, reps, minutes trained, average form score, '
        'your best exercise, and your current streak — visualized with interactive charts on your '
        'personal Dashboard.</div>', unsafe_allow_html=True
    )

    # ---------- AI COACH TEASER ----------
    st.markdown('<div class="gt-section-title">AI Coach</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="gt-card">After every session, your AI Coach reviews your reps and form score '
        'and gives you specific, prioritized feedback — always available, with no API key required.</div>',
        unsafe_allow_html=True,
    )

    # ---------- FOUNDER SECTION ----------
    st.markdown('<div class="gt-section-title">Meet the Vision Behind GymTrainer AI</div>', unsafe_allow_html=True)
    fcol1, fcol2 = st.columns([1, 2])
    with fcol1:
        photo_b64 = _founder_photo_base64()
        if photo_b64:
            st.markdown(
                f'<div class="gt-founder-photo" style="text-align:center;">'
                f'<img src="data:image/jpeg;base64,{photo_b64}" width="160" '
                f'style="object-fit:cover; height:160px;"></div>',
                unsafe_allow_html=True,
            )
    with fcol2:
        st.markdown(
            '<div class="gt-card">"Built with vision, technology, and a passion for smarter fitness — '
            'GymTrainer AI is founded by <strong>Ritesh Kumar Singh</strong>."</div>',
            unsafe_allow_html=True,
        )

    # ---------- CTA ----------
    st.markdown('<div class="gt-section-title">Ready to Train Smarter?</div>', unsafe_allow_html=True)
    if st.button("🚀 Start Your First AI Workout", use_container_width=True):
        st.session_state.nav = "AI Workout"
        st.rerun()

    # ---------- FOOTER ----------
    st.markdown(
        '<hr style="border-color:rgba(255,255,255,0.08); margin-top:2rem;">'
        '<p style="text-align:center; color:#5f6b70; font-size:0.8rem;">'
        'GymTrainer AI — Train Smarter. Move Better. Become Stronger.<br>'
        'Fitness guidance only — not medical advice.</p>',
        unsafe_allow_html=True,
    )
