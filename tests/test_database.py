import sys, os, tempfile
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from modules.database import Database
from modules.auth import hash_password, verify_password, validate_signup
from modules.workout_planner import generate_plan


def _fresh_db():
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    tmp.close()
    return Database(sqlite_path=tmp.name)


def test_database_falls_back_to_sqlite_without_supabase_creds():
    db = _fresh_db()
    assert db.backend == "sqlite"


def test_create_and_fetch_user():
    db = _fresh_db()
    uid = db.create_user("test@example.com", hash_password("Password123"))
    assert uid is not None
    user = db.get_user_by_email("test@example.com")
    assert user is not None
    assert user["email"] == "test@example.com"


def test_duplicate_email_rejected():
    db = _fresh_db()
    db.create_user("dup@example.com", hash_password("Password123"))
    second = db.create_user("dup@example.com", hash_password("Password456"))
    assert second is None


def test_password_hash_and_verify_roundtrip():
    h = hash_password("MySecret123")
    assert verify_password("MySecret123", h) is True
    assert verify_password("WrongPassword", h) is False


def test_validate_signup_rules():
    assert validate_signup("bad-email", "Password123", "Password123").ok is False
    assert validate_signup("a@b.com", "short1", "short1").ok is False
    assert validate_signup("a@b.com", "onlyletters", "onlyletters").ok is False
    assert validate_signup("a@b.com", "Password123", "Different123").ok is False
    assert validate_signup("a@b.com", "Password123", "Password123").ok is True


def test_workout_session_save_and_history():
    db = _fresh_db()
    uid = db.create_user("hist@example.com", hash_password("Password123"))
    db.save_workout_session(uid, "Squat", sets=3, reps=30, correct_reps=27,
                             incorrect_reps=3, form_score=88.5, duration_seconds=300)
    history = db.get_workout_history(uid)
    assert len(history) == 1
    assert history[0]["exercise"] == "Squat"


def test_dashboard_stats_empty_user():
    db = _fresh_db()
    uid = db.create_user("empty@example.com", hash_password("Password123"))
    stats = db.get_dashboard_stats(uid)
    assert stats["total_workouts"] == 0
    assert stats["current_streak"] == 0


def test_dashboard_stats_with_sessions():
    db = _fresh_db()
    uid = db.create_user("stats@example.com", hash_password("Password123"))
    db.save_workout_session(uid, "Squat", 3, 30, 27, 3, 90.0, 300)
    db.save_workout_session(uid, "Bicep Curl", 3, 36, 34, 2, 85.0, 240)
    stats = db.get_dashboard_stats(uid)
    assert stats["total_workouts"] == 2
    assert stats["total_reps"] == 66
    assert stats["avg_form_score"] == 87.5


def test_profile_upsert_and_fetch():
    db = _fresh_db()
    uid = db.create_user("profile@example.com", hash_password("Password123"))
    ok = db.upsert_profile(uid, {
        "name": "Test User", "age": 22, "height_cm": 175, "weight_kg": 70,
        "fitness_goal": "Strength", "experience": "Beginner", "training_days": 4,
        "equipment": "Bodyweight",
    })
    assert ok is True
    profile = db.get_profile(uid)
    assert profile["name"] == "Test User"


def test_workout_planner_generates_correct_day_count():
    plan = generate_plan("Strength", "Intermediate", 4, "Bodyweight", 30)
    assert len(plan.days) == 4
    for day in plan.days:
        assert len(day.exercises) > 0


def test_workout_planner_handles_unusual_days_per_week():
    plan = generate_plan("Endurance", "Beginner", 2, "Dumbbells", 20)
    assert len(plan.days) in (3, 4, 5, 6)  # snaps to nearest supported split


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-v"]))
