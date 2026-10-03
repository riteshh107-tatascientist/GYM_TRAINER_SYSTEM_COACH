"""
workout_planner.py
Generates a structured multi-day workout plan from goal / experience /
days-per-week / equipment / duration inputs. Pure logic, no Streamlit
dependency -> unit testable.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict

PLANNER_DISCLAIMER = (
    "Workout recommendations are general fitness guidance and are not a "
    "substitute for advice from a qualified healthcare or fitness professional."
)

EXERCISE_POOL = {
    "bodyweight": {
        "upper": [("Push-ups", "3", "10-15"), ("Bicep Curl (bodyweight/band)", "3", "12"),
                  ("Shoulder Press (band)", "3", "10"), ("Plank Shoulder Taps", "3", "20")],
        "lower": [("Squat", "4", "15"), ("Lunges", "3", "12 each leg"), ("Glute Bridges", "3", "15"),
                  ("Jumping Jacks", "3", "30 sec")],
        "core": [("Sit-ups", "3", "15"), ("Plank", "3", "30-45 sec"), ("Mountain Climbers", "3", "20")],
        "full_body": [("Jumping Jacks", "3", "30 sec"), ("Squat", "3", "15"), ("Push-ups", "3", "10"),
                       ("Plank", "3", "30 sec")],
    },
    "dumbbells": {
        "upper": [("Push-ups", "3", "12"), ("Dumbbell Bicep Curl", "3", "12"),
                  ("Dumbbell Shoulder Press", "3", "10"), ("Dumbbell Row", "3", "12")],
        "lower": [("Dumbbell Squat", "4", "12"), ("Dumbbell Lunges", "3", "12 each leg"),
                  ("Romanian Deadlift", "3", "10"), ("Calf Raises", "3", "15")],
        "core": [("Sit-ups", "3", "15"), ("Plank", "3", "45 sec"), ("Russian Twists", "3", "20")],
        "full_body": [("Dumbbell Squat", "3", "12"), ("Push-ups", "3", "12"), ("Dumbbell Row", "3", "12"),
                       ("Plank", "3", "30 sec")],
    },
    "full_gym": {
        "upper": [("Bench Press", "4", "10"), ("Bicep Curl", "3", "12"), ("Shoulder Press", "4", "10"),
                  ("Lat Pulldown", "3", "12")],
        "lower": [("Barbell Squat", "4", "10"), ("Leg Press", "3", "12"), ("Lunges", "3", "12 each leg"),
                  ("Leg Curl", "3", "12")],
        "core": [("Sit-ups", "3", "15"), ("Plank", "3", "45 sec"), ("Cable Crunch", "3", "15")],
        "full_body": [("Barbell Squat", "3", "10"), ("Bench Press", "3", "10"), ("Deadlift", "3", "8"),
                       ("Plank", "3", "30 sec")],
    },
}

REST_GUIDANCE = {
    "Strength": "Rest 90-120 sec between sets.",
    "Muscle Building": "Rest 60-90 sec between sets.",
    "General Fitness": "Rest 45-60 sec between sets.",
    "Endurance": "Rest 30-45 sec between sets.",
}

DAY_SPLITS = {
    3: ["full_body", "full_body", "full_body"],
    4: ["upper", "lower", "upper", "lower"],
    5: ["upper", "lower", "core", "upper", "lower"],
    6: ["upper", "lower", "core", "upper", "lower", "core"],
}

SPLIT_LABELS = {
    "upper": "UPPER BODY", "lower": "LOWER BODY", "core": "CORE", "full_body": "FULL BODY",
}


@dataclass
class PlanDay:
    day_number: int
    focus: str
    exercises: List[Dict[str, str]]


@dataclass
class WorkoutPlan:
    goal: str
    experience: str
    days_per_week: int
    equipment: str
    duration_minutes: int
    rest_guidance: str
    days: List[PlanDay] = field(default_factory=list)
    disclaimer: str = PLANNER_DISCLAIMER


def generate_plan(goal: str, experience: str, days_per_week: int, equipment: str,
                   duration_minutes: int) -> WorkoutPlan:
    equipment_key = equipment.lower().replace(" ", "_")
    if equipment_key not in EXERCISE_POOL:
        equipment_key = "bodyweight"

    if days_per_week not in DAY_SPLITS:
        days_per_week = min(DAY_SPLITS.keys(), key=lambda k: abs(k - days_per_week))

    split = DAY_SPLITS[days_per_week]
    pool = EXERCISE_POOL[equipment_key]

    # Advanced experience gets an extra exercise per day; beginners get fewer.
    exercise_count = {"Beginner": 3, "Intermediate": 4, "Advanced": 5}.get(experience, 4)

    plan_days = []
    for i, focus in enumerate(split, start=1):
        available = pool[focus]
        exercises = []
        for j in range(min(exercise_count, len(available) + 2)):
            name, sets, reps = available[j % len(available)]
            exercises.append({"exercise": name, "sets": sets, "reps": reps})
        plan_days.append(PlanDay(day_number=i, focus=SPLIT_LABELS[focus], exercises=exercises))

    return WorkoutPlan(
        goal=goal, experience=experience, days_per_week=days_per_week, equipment=equipment,
        duration_minutes=duration_minutes,
        rest_guidance=REST_GUIDANCE.get(goal, "Rest 60-90 sec between sets."),
        days=plan_days,
    )
