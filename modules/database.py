"""
database.py
Data access layer. Uses Supabase (Postgres) when credentials are supplied,
and transparently falls back to a local SQLite file otherwise, so the app
remains fully usable for local development/testing/demo without any
external service configured.

Deliberately does not import streamlit — configuration (supabase_url /
supabase_key) is passed in explicitly by the caller (app.py reads
st.secrets and forwards them), which keeps this module independently
unit-testable.
"""
from __future__ import annotations
import sqlite3
import json
import uuid
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

SQLITE_PATH = "gymtrainer.db"

SQLITE_SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS profiles (
    user_id TEXT PRIMARY KEY,
    name TEXT,
    age INTEGER,
    height_cm REAL,
    weight_kg REAL,
    fitness_goal TEXT,
    experience TEXT,
    training_days INTEGER,
    equipment TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS workout_sessions (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    exercise TEXT NOT NULL,
    sets INTEGER,
    reps INTEGER,
    correct_reps INTEGER,
    incorrect_reps INTEGER,
    form_score REAL,
    duration_seconds REAL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
"""


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class SupabaseUnavailable(Exception):
    pass


class Database:
    """
    Unified data-access facade. Backend is chosen at construction time:
    - If supabase_url and supabase_key are both provided AND the
      `supabase` package is importable AND the connection succeeds,
      use Supabase Postgres.
    - Otherwise, fall back to local SQLite (always available).
    """

    def __init__(self, supabase_url: Optional[str] = None, supabase_key: Optional[str] = None,
                 sqlite_path: str = SQLITE_PATH):
        self.backend = "sqlite"
        self._sqlite_path = sqlite_path
        self._supabase_client = None

        if supabase_url and supabase_key:
            try:
                from supabase import create_client  # optional dependency
                self._supabase_client = create_client(supabase_url, supabase_key)
                # cheap connectivity check
                self._supabase_client.table("users").select("id").limit(1).execute()
                self.backend = "supabase"
            except Exception:
                # Any failure (missing package, bad creds, network) -> fall back silently.
                self._supabase_client = None
                self.backend = "sqlite"

        if self.backend == "sqlite":
            self._init_sqlite()

    # ---------- setup ----------

    def _init_sqlite(self):
        with self._sqlite_conn() as conn:
            conn.executescript(SQLITE_SCHEMA)

    @contextmanager
    def _sqlite_conn(self):
        conn = sqlite3.connect(self._sqlite_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    # ---------- users ----------

    def create_user(self, email: str, password_hash: str) -> Optional[str]:
        user_id = str(uuid.uuid4())
        if self.backend == "supabase":
            try:
                self._supabase_client.table("users").insert({
                    "id": user_id, "email": email, "password_hash": password_hash,
                    "created_at": _now_iso(),
                }).execute()
                return user_id
            except Exception:
                return None
        with self._sqlite_conn() as conn:
            try:
                conn.execute(
                    "INSERT INTO users (id, email, password_hash, created_at) VALUES (?, ?, ?, ?)",
                    (user_id, email, password_hash, _now_iso()),
                )
                return user_id
            except sqlite3.IntegrityError:
                return None

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        if self.backend == "supabase":
            try:
                res = self._supabase_client.table("users").select("*").eq("email", email).limit(1).execute()
                return res.data[0] if res.data else None
            except Exception:
                return None
        with self._sqlite_conn() as conn:
            row = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
            return dict(row) if row else None

    # ---------- profiles ----------

    def upsert_profile(self, user_id: str, profile: Dict[str, Any]) -> bool:
        if self.backend == "supabase":
            try:
                data = {"user_id": user_id, **profile}
                self._supabase_client.table("profiles").upsert(data).execute()
                return True
            except Exception:
                return False
        with self._sqlite_conn() as conn:
            existing = conn.execute("SELECT user_id FROM profiles WHERE user_id = ?", (user_id,)).fetchone()
            fields = ["name", "age", "height_cm", "weight_kg", "fitness_goal", "experience",
                      "training_days", "equipment"]
            values = [profile.get(f) for f in fields]
            if existing:
                set_clause = ", ".join(f"{f} = ?" for f in fields)
                conn.execute(f"UPDATE profiles SET {set_clause} WHERE user_id = ?", (*values, user_id))
            else:
                conn.execute(
                    f"INSERT INTO profiles (user_id, {', '.join(fields)}) VALUES (?, {', '.join('?' for _ in fields)})",
                    (user_id, *values),
                )
            return True

    def get_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        if self.backend == "supabase":
            try:
                res = self._supabase_client.table("profiles").select("*").eq("user_id", user_id).limit(1).execute()
                return res.data[0] if res.data else None
            except Exception:
                return None
        with self._sqlite_conn() as conn:
            row = conn.execute("SELECT * FROM profiles WHERE user_id = ?", (user_id,)).fetchone()
            return dict(row) if row else None

    # ---------- workout sessions ----------

    def save_workout_session(self, user_id: str, exercise: str, sets: int, reps: int,
                              correct_reps: int, incorrect_reps: int, form_score: float,
                              duration_seconds: float) -> Optional[str]:
        session_id = str(uuid.uuid4())
        record = {
            "id": session_id, "user_id": user_id, "exercise": exercise, "sets": sets, "reps": reps,
            "correct_reps": correct_reps, "incorrect_reps": incorrect_reps, "form_score": form_score,
            "duration_seconds": duration_seconds, "created_at": _now_iso(),
        }
        if self.backend == "supabase":
            try:
                self._supabase_client.table("workout_sessions").insert(record).execute()
                return session_id
            except Exception:
                return None
        with self._sqlite_conn() as conn:
            conn.execute(
                """INSERT INTO workout_sessions
                   (id, user_id, exercise, sets, reps, correct_reps, incorrect_reps, form_score,
                    duration_seconds, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (session_id, user_id, exercise, sets, reps, correct_reps, incorrect_reps,
                 form_score, duration_seconds, record["created_at"]),
            )
            return session_id

    def get_workout_history(self, user_id: str) -> List[Dict[str, Any]]:
        if self.backend == "supabase":
            try:
                res = (self._supabase_client.table("workout_sessions").select("*")
                       .eq("user_id", user_id).order("created_at", desc=True).execute())
                return res.data or []
            except Exception:
                return []
        with self._sqlite_conn() as conn:
            rows = conn.execute(
                "SELECT * FROM workout_sessions WHERE user_id = ? ORDER BY created_at DESC", (user_id,)
            ).fetchall()
            return [dict(r) for r in rows]

    def get_dashboard_stats(self, user_id: str) -> Dict[str, Any]:
        history = self.get_workout_history(user_id)
        if not history:
            return {
                "total_workouts": 0, "total_reps": 0, "total_minutes": 0.0,
                "avg_form_score": 0.0, "best_exercise": "-", "current_streak": 0,
            }

        total_workouts = len(history)
        total_reps = sum(h.get("reps") or 0 for h in history)
        total_minutes = sum((h.get("duration_seconds") or 0) for h in history) / 60.0
        avg_form_score = sum(h.get("form_score") or 0 for h in history) / total_workouts

        by_exercise: Dict[str, list] = {}
        for h in history:
            by_exercise.setdefault(h["exercise"], []).append(h.get("form_score") or 0)
        best_exercise = max(by_exercise.items(), key=lambda kv: sum(kv[1]) / len(kv[1]))[0] if by_exercise else "-"

        streak = _compute_streak([h["created_at"] for h in history])

        return {
            "total_workouts": total_workouts,
            "total_reps": total_reps,
            "total_minutes": round(total_minutes, 1),
            "avg_form_score": round(avg_form_score, 1),
            "best_exercise": best_exercise,
            "current_streak": streak,
        }


def _compute_streak(created_at_list: List[str]) -> int:
    """Consecutive-day streak counting back from the most recent workout day."""
    if not created_at_list:
        return 0
    try:
        dates = sorted({datetime.fromisoformat(c).date() for c in created_at_list}, reverse=True)
    except ValueError:
        return 0

    streak = 1
    for i in range(1, len(dates)):
        if (dates[i - 1] - dates[i]).days == 1:
            streak += 1
        else:
            break
    return streak
