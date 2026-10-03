import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from modules.rep_counter import RepCounter, PlankTimer
from modules.pose_engine import calculate_angle


def test_calculate_angle_right_angle():
    # a=(0,1), b=(0,0) origin, c=(1,0) -> 90 degrees
    angle = calculate_angle((0, 1), (0, 0), (1, 0))
    assert 89 <= angle <= 91


def test_calculate_angle_straight_line():
    angle = calculate_angle((0, 0), (1, 0), (2, 0))
    assert angle >= 179


def test_squat_rep_counter_full_cycle():
    counter = RepCounter("squat")
    # start UP
    r1 = counter.update(170)
    assert r1["state"] == "UP"
    assert r1["reps"] == 0
    # go DOWN
    r2 = counter.update(90)
    assert r2["state"] == "DOWN"
    assert r2["reps"] == 0
    # back UP -> rep counted
    r3 = counter.update(170)
    assert r3["state"] == "UP"
    assert r3["reps"] == 1
    assert r3["rep_completed"] is True


def test_squat_rep_counter_no_partial_reps():
    counter = RepCounter("squat")
    counter.update(170)  # UP
    counter.update(140)  # partial - not below down_angle(100) -> stays UP-ish, no DOWN state
    r = counter.update(170)
    assert r["reps"] == 0  # never reached DOWN, so no rep


def test_bicep_curl_inverted_thresholds():
    counter = RepCounter("bicep_curl")
    r1 = counter.update(160)  # extended arm = DOWN for curls (lower_is_down=False)
    assert r1["state"] == "DOWN"
    r2 = counter.update(40)  # curled = UP
    assert r2["state"] == "UP"
    assert r2["reps"] == 1


def test_rep_counter_rejects_unknown_exercise():
    try:
        RepCounter("not_a_real_exercise")
        assert False, "should have raised"
    except ValueError:
        pass


def test_plank_timer_accumulates_only_when_form_ok():
    timer = PlankTimer()
    timer.tick(2.0, form_ok=True)
    timer.tick(3.0, form_ok=True)
    timer.tick(5.0, form_ok=False)
    assert timer.total_seconds == 5.0
    assert timer.is_holding is False


def test_multiple_cycles_count_multiple_reps():
    counter = RepCounter("pushup")
    counter.update(170)  # UP
    for _ in range(5):
        counter.update(80)   # DOWN
        counter.update(170)  # UP -> rep
    assert counter.reps == 5
    assert counter.correct_reps + counter.incorrect_reps == 5


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-v"]))
