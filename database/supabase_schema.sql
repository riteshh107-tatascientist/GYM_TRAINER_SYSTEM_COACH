-- GymTrainer AI — Supabase (Postgres) schema
-- Run this in the Supabase SQL editor before pointing the app at your project.

create extension if not exists "uuid-ossp";

create table if not exists users (
    id text primary key,
    email text unique not null,
    password_hash text not null,
    created_at timestamptz not null default now()
);

create table if not exists profiles (
    user_id text primary key references users(id) on delete cascade,
    name text,
    age integer,
    height_cm real,
    weight_kg real,
    fitness_goal text,
    experience text,
    training_days integer,
    equipment text
);

create table if not exists workout_sessions (
    id text primary key,
    user_id text not null references users(id) on delete cascade,
    exercise text not null,
    sets integer,
    reps integer,
    correct_reps integer,
    incorrect_reps integer,
    form_score real,
    duration_seconds real,
    created_at timestamptz not null default now()
);

create table if not exists exercise_results (
    id text primary key,
    session_id text not null references workout_sessions(id) on delete cascade,
    rep_number integer,
    joint_angle real,
    is_correct boolean,
    created_at timestamptz not null default now()
);

create table if not exists progress (
    id text primary key,
    user_id text not null references users(id) on delete cascade,
    metric_name text not null,
    metric_value real,
    recorded_at timestamptz not null default now()
);

create index if not exists idx_workout_sessions_user on workout_sessions(user_id);
create index if not exists idx_progress_user on progress(user_id);

-- Row Level Security (recommended once you add Supabase Auth on top of
-- this schema instead of the app's own password table).
-- alter table workout_sessions enable row level security;
-- alter table profiles enable row level security;
