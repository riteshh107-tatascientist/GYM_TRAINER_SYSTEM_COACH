import streamlit as st
from modules.auth import hash_password, verify_password, validate_signup


def render(db):
    st.markdown('<h1 class="gt-gradient-text">Welcome to GymTrainer AI</h1>', unsafe_allow_html=True)

    tab_login, tab_signup = st.tabs(["🔐 Login", "📝 Sign Up"])

    with tab_login:
        with st.form("login_form"):
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_password")
            submitted = st.form_submit_button("Login", use_container_width=True)
            if submitted:
                user = db.get_user_by_email(email.strip().lower())
                if user and verify_password(password, user["password_hash"]):
                    st.session_state.user = {"id": user["id"], "email": user["email"]}
                    st.success("Logged in successfully!")
                    st.rerun()
                else:
                    st.error("Invalid email or password.")

    with tab_signup:
        with st.form("signup_form"):
            email = st.text_input("Email", key="signup_email")
            password = st.text_input("Password", type="password", key="signup_password")
            confirm = st.text_input("Confirm Password", type="password", key="signup_confirm")
            submitted = st.form_submit_button("Create Account", use_container_width=True)
            if submitted:
                validation = validate_signup(email.strip().lower(), password, confirm)
                if not validation.ok:
                    st.error(validation.message)
                else:
                    existing = db.get_user_by_email(email.strip().lower())
                    if existing:
                        st.error("An account with this email already exists.")
                    else:
                        user_id = db.create_user(email.strip().lower(), hash_password(password))
                        if user_id:
                            st.session_state.user = {"id": user_id, "email": email.strip().lower()}
                            st.success("Account created! You're now logged in.")
                            st.rerun()
                        else:
                            st.error("Could not create account. Please try again.")
