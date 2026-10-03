"""
theme.py
Custom CSS injected once per page render to give GymTrainer AI a premium
dark fitness-tech look and to hide default Streamlit chrome. Pure string
constant -> no external dependency, safe to import from app.py.
"""

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&family=Inter:wght@400;500;600&display=swap');

:root {
    --bg-primary: #0a0e12;
    --bg-secondary: #10161c;
    --bg-card: rgba(255, 255, 255, 0.035);
    --border-glow: rgba(0, 230, 168, 0.25);
    --accent-green: #00e6a8;
    --accent-cyan: #22d3ee;
    --accent-blue: #3b82f6;
    --text-primary: #f2f5f7;
    --text-secondary: #9aa5ab;
}

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
h1, h2, h3, h4, h5 { font-family: 'Poppins', sans-serif !important; }

.stApp {
    background: radial-gradient(circle at 15% 0%, #0d2b24 0%, var(--bg-primary) 45%),
                var(--bg-primary);
    color: var(--text-primary);
}

/* Hide default Streamlit chrome */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header[data-testid="stHeader"] { background: transparent; }

section[data-testid="stSidebar"] {
    background: #0b1116;
    border-right: 1px solid rgba(255,255,255,0.06);
}

.gt-hero {
    padding: 2.5rem 2rem;
    border-radius: 24px;
    background: linear-gradient(135deg, rgba(0,230,168,0.10), rgba(34,211,238,0.05));
    border: 1px solid var(--border-glow);
    margin-bottom: 1.5rem;
}

.gt-gradient-text {
    background: linear-gradient(90deg, var(--accent-green), var(--accent-cyan));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-weight: 800;
}

.gt-card {
    background: var(--bg-card);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 18px;
    padding: 1.4rem 1.5rem;
    backdrop-filter: blur(6px);
    transition: border-color 0.2s ease, transform 0.2s ease;
}
.gt-card:hover { border-color: var(--border-glow); transform: translateY(-2px); }

.gt-metric-value {
    font-size: 2rem;
    font-weight: 800;
    background: linear-gradient(90deg, var(--accent-green), var(--accent-cyan));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.gt-metric-label { color: var(--text-secondary); font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.06em; }

.gt-badge {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    border-radius: 999px;
    background: rgba(0,230,168,0.12);
    border: 1px solid rgba(0,230,168,0.35);
    color: var(--accent-green);
    font-size: 0.78rem;
    font-weight: 600;
}

.gt-founder-photo img {
    border-radius: 50%;
    border: 3px solid rgba(0,230,168,0.45);
    box-shadow: 0 0 40px rgba(0,230,168,0.25);
}

.gt-disclaimer {
    font-size: 0.78rem;
    color: var(--text-secondary);
    border-left: 3px solid var(--accent-cyan);
    padding-left: 0.75rem;
    margin-top: 0.75rem;
}

.stButton > button {
    border-radius: 12px;
    border: 1px solid var(--border-glow);
    background: linear-gradient(90deg, rgba(0,230,168,0.18), rgba(34,211,238,0.12));
    color: var(--text-primary);
    font-weight: 600;
    padding: 0.55rem 1.4rem;
}
.stButton > button:hover {
    border-color: var(--accent-green);
    color: var(--accent-green);
}

.gt-section-title {
    font-weight: 700;
    font-size: 1.4rem;
    margin: 1.8rem 0 0.8rem 0;
}
</style>
"""


def inject(st_module) -> None:
    """Call once near the top of app.py: theme.inject(st)"""
    st_module.markdown(CUSTOM_CSS, unsafe_allow_html=True)
