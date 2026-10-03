import streamlit as st

EXERCISE_LIBRARY = [
    {"name": "Squat", "muscles": "Quads, Glutes, Hamstrings", "difficulty": "Beginner", "category": "Legs",
     "instructions": "Stand with feet shoulder-width apart, lower hips back and down until thighs are near parallel, then drive back up.",
     "mistakes": "Knees caving inward, heels lifting, rounding the lower back.",
     "tips": "Keep your chest up and drive through your heels."},
    {"name": "Bicep Curl", "muscles": "Biceps, Forearms", "difficulty": "Beginner", "category": "Arms",
     "instructions": "Hold weights at your sides, curl up by bending the elbow, then lower with control.",
     "mistakes": "Swinging the shoulders, using momentum, partial range of motion.",
     "tips": "Keep elbows pinned to your torso throughout the movement."},
    {"name": "Push-up", "muscles": "Chest, Shoulders, Triceps, Core", "difficulty": "Intermediate", "category": "Chest",
     "instructions": "Start in a plank, lower your chest toward the floor, then press back up to full extension.",
     "mistakes": "Sagging hips, flaring elbows too wide, incomplete range of motion.",
     "tips": "Keep a straight line from shoulders to ankles."},
    {"name": "Shoulder Press", "muscles": "Shoulders, Triceps", "difficulty": "Intermediate", "category": "Shoulders",
     "instructions": "Press weights overhead from shoulder height until arms are fully extended, then lower with control.",
     "mistakes": "Arching the lower back, incomplete lockout.",
     "tips": "Brace your core to keep your torso stable."},
    {"name": "Lunges", "muscles": "Quads, Glutes, Hamstrings", "difficulty": "Beginner", "category": "Legs",
     "instructions": "Step forward, lower your back knee toward the floor, then push back to standing.",
     "mistakes": "Front knee traveling past the toes, leaning forward excessively.",
     "tips": "Keep your torso upright and step far enough forward."},
    {"name": "Plank", "muscles": "Core, Shoulders", "difficulty": "Beginner", "category": "Core",
     "instructions": "Hold a straight-line position on your forearms and toes, bracing your core.",
     "mistakes": "Hips sagging or piking too high.",
     "tips": "Squeeze your glutes and keep your body in one straight line."},
    {"name": "Jumping Jacks", "muscles": "Full Body, Cardio", "difficulty": "Beginner", "category": "Full Body",
     "instructions": "Jump feet out while raising arms overhead, then jump back to the starting position.",
     "mistakes": "Incomplete arm extension, limited leg spread.",
     "tips": "Keep a steady, rhythmic pace and land softly."},
    {"name": "Sit-up", "muscles": "Abdominals, Hip Flexors", "difficulty": "Beginner", "category": "Core",
     "instructions": "Lie on your back, curl your torso up toward your knees, then lower with control.",
     "mistakes": "Using momentum, pulling on the neck.",
     "tips": "Cross arms over your chest and lead with your chest, not your chin."},
]

CATEGORIES = ["All", "Chest", "Back", "Shoulders", "Arms", "Legs", "Core", "Full Body"]


def render():
    st.markdown('<h1 class="gt-gradient-text">Exercise Library</h1>', unsafe_allow_html=True)
    category = st.selectbox("Filter by category", CATEGORIES)

    filtered = EXERCISE_LIBRARY if category == "All" else [e for e in EXERCISE_LIBRARY if e["category"] == category]

    cols = st.columns(2)
    for i, ex in enumerate(filtered):
        with cols[i % 2]:
            st.markdown(
                f"""
                <div class="gt-card" style="margin-bottom:1rem;">
                    <h4>{ex['name']} <span class="gt-badge">{ex['difficulty']}</span></h4>
                    <p style="color:#9aa5ab; margin-bottom:0.4rem;"><strong>Target muscles:</strong> {ex['muscles']}</p>
                    <p style="margin-bottom:0.4rem;"><strong>Instructions:</strong> {ex['instructions']}</p>
                    <p style="margin-bottom:0.4rem;"><strong>Common mistakes:</strong> {ex['mistakes']}</p>
                    <p style="margin-bottom:0;"><strong>Form tip:</strong> {ex['tips']}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
