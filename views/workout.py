import streamlit as st
import time
import tempfile
import os

from modules.exercise_engine import ExerciseSession, SUPPORTED_EXERCISES, EXERCISE_PRIMARY_JOINTS
from modules.pose_engine import PoseEngine, MEDIAPIPE_AVAILABLE, CV2_AVAILABLE
from modules.ai_coach import build_coach_message

try:
    import cv2
except ImportError:
    cv2 = None

try:
    from streamlit_webrtc import webrtc_streamer, VideoProcessorBase
    import av
    WEBRTC_AVAILABLE = True
except ImportError:
    WEBRTC_AVAILABLE = False


def _init_session_state():
    if "workout_session" not in st.session_state:
        st.session_state.workout_session = None
    if "workout_start_time" not in st.session_state:
        st.session_state.workout_start_time = None
    if "workout_exercise_key" not in st.session_state:
        st.session_state.workout_exercise_key = None


def _metrics_card(result, exercise_key):
    is_plank = exercise_key == "plank"
    st.markdown('<div class="gt-card">', unsafe_allow_html=True)
    st.markdown("#### 🏋️ AI FITNESS COACH — Live Metrics")
    c1, c2, c3 = st.columns(3)
    c1.metric("Exercise", SUPPORTED_EXERCISES[exercise_key])
    if is_plank:
        c2.metric("Hold Time", f"{result.hold_seconds:.0f}s")
        c3.metric("State", result.state or "-")
    else:
        c2.metric("Reps", result.reps)
        c3.metric("State", result.state or "-")
    if not is_plank:
        c4, c5 = st.columns(2)
        c4.metric("Correct Reps", result.correct_reps)
        c5.metric("Incorrect Reps", result.incorrect_reps)
    if result.form_score is not None:
        st.progress(min(int(result.form_score), 100) / 100, text=f"Form Score: {result.form_score:.0f}%")
    if result.breakdown:
        bd_cols = st.columns(len(result.breakdown))
        for c, (k, v) in zip(bd_cols, result.breakdown.items()):
            c.metric(k, f"{v:.0f}%")
    st.markdown('</div>', unsafe_allow_html=True)


def _process_video_file(video_path: str, exercise_key: str, sample_every_n: int = 3):
    if cv2 is None:
        st.error("OpenCV is not available in this environment, so video analysis can't run here.")
        return None

    pose_engine = PoseEngine()
    if not pose_engine.available:
        st.warning(
            "MediaPipe / OpenCV pose detection isn't available in this environment. "
            "Install the full requirements (see requirements.txt) to enable real video analysis."
        )
        return None

    session = ExerciseSession(exercise_key)
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    dt = sample_every_n / fps

    frame_idx = 0
    last_result = None
    no_person_frames = 0
    progress_bar = st.progress(0, text="Analyzing video...")
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 1

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame_idx += 1
        if frame_idx % sample_every_n != 0:
            continue

        landmarks = pose_engine.process_frame(frame)
        if landmarks is None:
            no_person_frames += 1
            continue

        last_result = session.process_landmarks(landmarks, dt_seconds=dt)
        progress_bar.progress(min(frame_idx / total_frames, 1.0), text="Analyzing video...")

    cap.release()
    pose_engine.close()
    progress_bar.empty()

    if last_result is None:
        st.warning("No person was clearly detected in the uploaded video. Try a clearer, well-lit video.")
        return None

    return session, last_result


def render():
    _init_session_state()
    st.markdown('<h1 class="gt-gradient-text">AI Workout</h1>', unsafe_allow_html=True)

    if not (MEDIAPIPE_AVAILABLE and CV2_AVAILABLE):
        st.warning(
            "⚠️ Computer-vision packages (mediapipe / opencv-python) aren't installed in this environment. "
            "Exercise selection, planning and history still work — install `requirements.txt` for full "
            "pose analysis."
        )

    exercise_key = st.selectbox(
        "Choose your exercise", options=list(SUPPORTED_EXERCISES.keys()),
        format_func=lambda k: SUPPORTED_EXERCISES[k],
    )
    st.caption(f"Tracked joints: {EXERCISE_PRIMARY_JOINTS[exercise_key]}")

    target_col1, target_col2 = st.columns(2)
    target_reps = target_col1.number_input("Target Reps", min_value=1, max_value=100, value=12)
    target_sets = target_col2.number_input("Target Sets", min_value=1, max_value=10, value=3)

    mode_options = ["📹 Upload Video", "📸 Photo Snapshot"]
    if WEBRTC_AVAILABLE:
        mode_options.insert(0, "🔴 Live Webcam")
    mode = st.radio("Input method", mode_options, horizontal=True)

    st.markdown('<div class="gt-disclaimer">Fitness guidance only — not medical advice.</div>',
                unsafe_allow_html=True)

    # ---------------- LIVE WEBCAM ----------------
    if mode == "🔴 Live Webcam" and WEBRTC_AVAILABLE:
        st.info("Live webcam mode uses streamlit-webrtc. Allow camera access when prompted by your browser.")

        class ExerciseVideoProcessor(VideoProcessorBase):
            def __init__(self):
                self.pose_engine = PoseEngine()
                self.session = ExerciseSession(exercise_key)
                self.last_result = None

            def recv(self, frame):
                img = frame.to_ndarray(format="bgr24")
                if self.pose_engine.available:
                    landmarks = self.pose_engine.process_frame(img)
                    if landmarks is not None:
                        self.last_result = self.session.process_landmarks(landmarks, dt_seconds=1 / 24)
                return av.VideoFrame.from_ndarray(img, format="bgr24")

        ctx = webrtc_streamer(key="gymtrainer-live", video_processor_factory=ExerciseVideoProcessor)
        if ctx.video_processor:
            st.caption("Live metrics update as MediaPipe detects your pose. Stop the stream to save your session.")

    # ---------------- UPLOAD VIDEO ----------------
    elif mode == "📹 Upload Video":
        uploaded = st.file_uploader("Upload a short workout video (MP4/MOV)", type=["mp4", "mov", "avi"])
        if uploaded and st.button("Analyze Video", use_container_width=True):
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded.name)[1]) as tmp:
                tmp.write(uploaded.read())
                tmp_path = tmp.name
            start = time.time()
            processed = _process_video_file(tmp_path, exercise_key)
            duration = time.time() - start
            os.unlink(tmp_path)

            if processed:
                session, result = processed
                _metrics_card(result, exercise_key)
                st.session_state["last_workout_result"] = {
                    "exercise_key": exercise_key, "session": session, "result": result,
                    "duration_seconds": duration, "target_sets": target_sets,
                }

    # ---------------- PHOTO SNAPSHOT ----------------
    else:
        st.caption("Single-photo mode gives you a form snapshot (no rep counting, since a photo is one instant).")
        photo = st.camera_input("Take a snapshot of your exercise position")
        if photo:
            if not (MEDIAPIPE_AVAILABLE and CV2_AVAILABLE):
                st.warning("Pose detection isn't available in this environment for photo analysis.")
            else:
                import numpy as np
                file_bytes = np.asarray(bytearray(photo.read()), dtype=np.uint8)
                frame = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
                pose_engine = PoseEngine()
                landmarks = pose_engine.process_frame(frame)
                pose_engine.close()
                if landmarks is None:
                    st.warning("No person detected clearly. Try better lighting or a fuller-body framing.")
                else:
                    session = ExerciseSession(exercise_key)
                    result = session.process_landmarks(landmarks, dt_seconds=1.0)
                    _metrics_card(result, exercise_key)

    # ---------------- SAVE WORKOUT ----------------
    last = st.session_state.get("last_workout_result")
    if last and last["exercise_key"] == exercise_key:
        st.markdown('<div class="gt-section-title">Workout Complete 🎉</div>', unsafe_allow_html=True)
        session, result = last["session"], last["result"]
        is_plank = exercise_key == "plank"

        s1, s2, s3, s4 = st.columns(4)
        s1.metric("Total Reps" if not is_plank else "Hold Time",
                   result.reps if not is_plank else f"{result.hold_seconds:.0f}s")
        s2.metric("Correct Reps" if not is_plank else "Form Score",
                   result.correct_reps if not is_plank else f"{result.form_score:.0f}%")
        s3.metric("Avg Form Score", f"{result.form_score:.0f}%" if result.form_score else "-")
        s4.metric("Duration", f"{last['duration_seconds']:.0f}s")

        coach_msg = build_coach_message(
            exercise_name=SUPPORTED_EXERCISES[exercise_key],
            reps=result.reps, correct_reps=result.correct_reps, incorrect_reps=result.incorrect_reps,
            avg_form_score=result.form_score or 0, feedback_points=result.feedback,
        )
        st.markdown(f'<div class="gt-card"><h4>🤖 AI Coach</h4><p style="white-space:pre-line;">{coach_msg}</p></div>',
                     unsafe_allow_html=True)

        if st.button("💾 Save Workout", use_container_width=True):
            db = st.session_state.get("db")
            user = st.session_state.get("user")
            if db and user:
                db.save_workout_session(
                    user["id"], SUPPORTED_EXERCISES[exercise_key], sets=last["target_sets"],
                    reps=result.reps, correct_reps=result.correct_reps, incorrect_reps=result.incorrect_reps,
                    form_score=result.form_score or 0, duration_seconds=last["duration_seconds"],
                )
                st.success("Workout saved to your history!")
                st.session_state["last_workout_result"] = None
            else:
                st.warning("Please log in to save your workout history.")
