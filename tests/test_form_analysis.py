import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from modules import form_analyzer


def test_squat_good_form_scores_high():
    result = form_analyzer.analyze_squat(knee_angle=95, hip_angle=90, torso_lean=10)
    assert result.score >= 90
    assert "Depth" in result.breakdown


def test_squat_poor_form_scores_low():
    result = form_analyzer.analyze_squat(knee_angle=170, hip_angle=170, torso_lean=50)
    assert result.score < 60


def test_bicep_curl_full_rom_scores_high():
    result = form_analyzer.analyze_bicep_curl(elbow_angle=45, shoulder_sway=3, control_score=90)
    assert result.score >= 85


def test_pushup_scoring_breakdown_keys():
    result = form_analyzer.analyze_pushup(elbow_angle=170, body_line_angle=180, depth_angle=90)
    assert set(result.breakdown.keys()) == {"Depth", "Body Alignment", "Lockout"}


def test_plank_endurance_scales_with_hold_time():
    short_hold = form_analyzer.analyze_plank(hip_alignment_angle=180, hold_seconds=10, target_seconds=60)
    long_hold = form_analyzer.analyze_plank(hip_alignment_angle=180, hold_seconds=60, target_seconds=60)
    assert long_hold.score > short_hold.score


def test_score_never_exceeds_100_or_below_0():
    result = form_analyzer.analyze_squat(knee_angle=95, hip_angle=90, torso_lean=0)
    for v in result.breakdown.values():
        assert 0 <= v <= 100
    assert 0 <= result.score <= 100


def test_form_disclaimer_present():
    assert "not medical advice" in form_analyzer.FORM_DISCLAIMER.lower()


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-v"]))
