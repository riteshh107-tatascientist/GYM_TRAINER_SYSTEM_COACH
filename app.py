"""
GymTrainer AI — main entrypoint.
"Train Smarter. Move Better. Become Stronger."
"""
import streamlit as st

from modules import theme
from modules.database import Database
from views import home, dashboard, workout, coach, exercises, planner, progress, profile, login, settings_page

st.set_page_config(
    page_title="GymTrainer AI",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded",
)

theme.inject(st)


@st.cache_resource(show_spinner=False)
def get_database() -> Database:
    """
    Reads Supabase credentials from st.secrets if present. If secrets.toml
    doesn't exist at all (common in local dev), st.secrets access is
    wrapped defensively so the app never crashes — it just falls back to
    SQLite, exactly as required.
    """
    supabase_url, supabase_key = None, None
    try:
        supabase_url = st.secrets.get("SUPABASE_URL")
        supabase_key = st.secrets.get("SUPABASE_KEY")
    except Exception:
        pass
    return Database(supabase_url=supabase_url, supabase_key=supabase_key)


def _init_state():
    if "user" not in st.session_state:
        st.session_state.user = None
    if "nav" not in st.session_state:
        st.session_state.nav = "Home"


def main():
    _init_state()

    try:
        db = get_database()
    except Exception as exc:
        st.error(f"Database initialization failed unexpectedly: {exc}. The app will continue with limited functionality.")
        db = None

    st.session_state.db = db

    NAV_ITEMS = [
        ("🏠", "Home"), ("📊", "Dashboard"), ("🏋️", "AI Workout"), ("🤖", "AI Coach"),
        ("📚", "Exercises"), ("📅", "Workout Planner"), ("📈", "Progress"), ("👤", "Profile"),
        ("⚙️", "Settings"),
    ]

    with st.sidebar:
        st.markdown('<h2 class="gt-gradient-text">GYMTRAINER AI</h2>', unsafe_allow_html=True)
        st.caption("Train Smarter. Move Better. Become Stronger.")
        st.markdown("---")

        if st.session_state.user:
            st.success(f"👋 {st.session_state.user['email']}")
        else:
            st.info("Not logged in — login to save your history.")

        labels = [f"{icon} {name}" for icon, name in NAV_ITEMS]
        current_label = f"{dict((n, i) for i, n in NAV_ITEMS).get(st.session_state.nav, '🏠')} {st.session_state.nav}"
        try:
            default_index = labels.index(current_label)
        except ValueError:
            default_index = 0
        choice = st.radio("Navigate", labels, index=default_index, label_visibility="collapsed")
        st.session_state.nav = choice.split(" ", 1)[1]

        st.markdown("---")
        if st.session_state.user:
            if st.button("🔐 Logout", use_container_width=True):
                st.session_state.user = None
                st.rerun()
        else:
            if st.button("🔐 Login / Sign Up", use_container_width=True):
                st.session_state.nav = "Login"
                st.rerun()

    page = st.session_state.nav
    user = st.session_state.user

    # Pages that require login
    auth_required_pages = {"Dashboard", "AI Coach", "Progress", "Profile"}

    try:
        if page == "Login":
            if db is None:
                st.error("Database is unavailable, so login can't work right now.")
            else:
                login.render(db)
        elif page == "Home":
            home.render()
        elif page == "AI Workout":
            workout.render()
        elif page == "Exercises":
            exercises.render()
        elif page == "Workout Planner":
            planner.render()
        elif page == "Settings":
            settings_page.render(db)
        elif page in auth_required_pages:
            if not user:
                st.warning("Please log in to view this page.")
                login.render(db)
            elif db is None:
                st.error("Database is unavailable, so this page can't load right now.")
            else:
                if page == "Dashboard":
                    dashboard.render(db, user)
                elif page == "AI Coach":
                    coach.render(db, user)
                elif page == "Progress":
                    progress.render(db, user)
                elif page == "Profile":
                    profile.render(db, user)
        else:
            home.render()
    except Exception as exc:  # never let one page crash the whole app
        st.error(f"Something went wrong loading this page: {exc}")
        st.caption("Try navigating to Home and back, or refresh the app.")


if __name__ == "__main__":
    main()
