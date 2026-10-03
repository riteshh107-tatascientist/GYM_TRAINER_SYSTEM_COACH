import streamlit as st
from modules.pose_engine import MEDIAPIPE_AVAILABLE, CV2_AVAILABLE


def render(db):
    st.markdown('<h1 class="gt-gradient-text">Settings</h1>', unsafe_allow_html=True)

    st.markdown('<div class="gt-section-title">System Status</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.metric("Database Backend", "Supabase" if db.backend == "supabase" else "SQLite (local)")
    c2.metric("Pose Detection", "Available" if (MEDIAPIPE_AVAILABLE and CV2_AVAILABLE) else "Unavailable")
    llm_configured = bool(st.secrets.get("LLM_API_KEY", "")) if hasattr(st, "secrets") else False
    c3.metric("LLM Coach Enhancement", "Configured" if llm_configured else "Not configured (using rule-based)")

    st.markdown('<div class="gt-section-title">About</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="gt-card">GymTrainer AI works fully offline with a local SQLite database and '
        'rule-based AI coaching. Configure Supabase credentials in <code>.streamlit/secrets.toml</code> '
        'for a persistent hosted database, and an LLM API key to enhance coach messages — both optional. '
        'See README.md for full setup instructions.</div>', unsafe_allow_html=True,
    )

    if st.session_state.get("user"):
        st.markdown('<div class="gt-section-title">Account</div>', unsafe_allow_html=True)
        st.write(f"Logged in as **{st.session_state.user['email']}**")
        if st.button("Logout", use_container_width=True):
            st.session_state.user = None
            st.rerun()
