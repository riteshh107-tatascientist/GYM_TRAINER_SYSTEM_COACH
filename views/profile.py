import streamlit as st


def render(db, user):
    st.markdown('<h1 class="gt-gradient-text">Your Profile</h1>', unsafe_allow_html=True)

    existing = db.get_profile(user["id"]) or {}

    with st.form("profile_form"):
        c1, c2 = st.columns(2)
        name = c1.text_input("Name", value=existing.get("name") or "")
        age = c2.number_input("Age", min_value=10, max_value=100, value=int(existing.get("age") or 20))

        c3, c4 = st.columns(2)
        height_cm = c3.number_input("Height (cm)", min_value=100.0, max_value=250.0,
                                     value=float(existing.get("height_cm") or 170.0))
        weight_kg = c4.number_input("Weight (kg)", min_value=30.0, max_value=250.0,
                                     value=float(existing.get("weight_kg") or 65.0))

        c5, c6 = st.columns(2)
        fitness_goal = c5.selectbox("Fitness Goal", ["Strength", "Muscle Building", "General Fitness", "Endurance"],
                                     index=_safe_index(["Strength", "Muscle Building", "General Fitness", "Endurance"],
                                                        existing.get("fitness_goal")))
        experience = c6.selectbox("Experience", ["Beginner", "Intermediate", "Advanced"],
                                   index=_safe_index(["Beginner", "Intermediate", "Advanced"], existing.get("experience")))

        c7, c8 = st.columns(2)
        training_days = c7.selectbox("Training Days per Week", [3, 4, 5, 6],
                                      index=_safe_index([3, 4, 5, 6], existing.get("training_days"), default=1))
        equipment = c8.selectbox("Equipment", ["Bodyweight", "Dumbbells", "Full Gym"],
                                  index=_safe_index(["Bodyweight", "Dumbbells", "Full Gym"], existing.get("equipment")))

        submitted = st.form_submit_button("Save Profile", use_container_width=True)
        if submitted:
            db.upsert_profile(user["id"], {
                "name": name, "age": age, "height_cm": height_cm, "weight_kg": weight_kg,
                "fitness_goal": fitness_goal, "experience": experience,
                "training_days": training_days, "equipment": equipment,
            })
            st.success("Profile saved.")

    st.markdown('<div class="gt-disclaimer">We only store what you enter here to personalize your plan — nothing else.</div>',
                unsafe_allow_html=True)


def _safe_index(options, value, default=0):
    try:
        return options.index(value) if value in options else default
    except (ValueError, TypeError):
        return default
