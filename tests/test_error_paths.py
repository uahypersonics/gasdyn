"""Tests for error paths and edge cases in solvers."""

import pytest

from gasdyn import (
    solve_isentropic,
    solve_normal_shock,
    solve_oblique,
    solve_prandtl_meyer,
    solve_taylor_maccoll,
)

# --------------------------------------------------
# isentropic error paths
# --------------------------------------------------


def test_isentropic_no_subsonic_solution():
    """Test when no subsonic solution exists for area ratio."""
    # this should still work but test the bounds checking
    result = solve_isentropic(area_ratio=1.0001, branch="subsonic")
    assert result.mach < 1.0


def test_isentropic_large_supersonic_area_ratio():
    """Test supersonic with very large area ratio."""
    result = solve_isentropic(area_ratio=50.0, branch="supersonic")
    assert result.mach > 5.0


# --------------------------------------------------
# oblique shock error paths
# --------------------------------------------------


def test_oblique_deflection_at_limit():
    """Test oblique shock at maximum deflection."""
    # get near the maximum deflection
    result = solve_oblique(mach=2.0, deflection_angle=22.0)
    assert result.shock_angle > 0


def test_oblique_invalid_combination():
    """Test oblique with impossible angle combination."""
    with pytest.raises(ValueError):
        solve_oblique(deflection_angle=5.0, shock_angle=4.0)  # shock < deflection


def test_oblique_shock_near_mach_angle():
    """Test oblique shock angle near mach angle."""
    import math

    mach = 3.0
    mu = math.degrees(math.asin(1.0 / mach))
    result = solve_oblique(mach=mach, shock_angle=mu + 1.0)
    assert result.deflection_angle > 0


# --------------------------------------------------
# prandtl-meyer error paths
# --------------------------------------------------


def test_prandtl_meyer_small_deflection():
    """Test Prandtl-Meyer with very small deflection."""
    result = solve_prandtl_meyer(mach_1=2.0, deflection_angle=0.1)
    assert result.mach_2 > result.mach_1


def test_prandtl_meyer_compression_detected():
    """Test that compression is detected."""
    with pytest.raises(ValueError, match="mach_2 must be > mach_1"):
        solve_prandtl_meyer(mach_1=3.0, mach_2=2.0)


def test_prandtl_meyer_invalid_state():
    """Test Prandtl-Meyer with invalid state."""
    with pytest.raises(ValueError):
        solve_prandtl_meyer(mach_2=3.0, deflection_angle=100.0)


def test_prandtl_meyer_near_zero_deflection():
    """Test Prandtl-Meyer with very small deflection."""
    result = solve_prandtl_meyer(mach_1=2.0, deflection_angle=0.01)
    # Very small deflection should give M2 very close to M1
    assert result.mach_2 > result.mach_1
    assert result.mach_2 - result.mach_1 < 0.01


# --------------------------------------------------
# taylor-maccoll error paths
# --------------------------------------------------


def test_cone_invalid_angle_combination():
    """Test cone with invalid angle combination."""
    with pytest.raises(ValueError, match="must be > cone_angle"):
        solve_taylor_maccoll(cone_angle=20.0, shock_angle=15.0)


def test_cone_shock_too_large():
    """Test cone with shock angle too large."""
    with pytest.raises(ValueError, match="must be <"):
        solve_taylor_maccoll(cone_angle=10.0, shock_angle=91.0)


def test_cone_small_cone_angle():
    """Test cone with small cone angle."""
    result = solve_taylor_maccoll(mach=3.0, cone_angle=5.0)
    assert result.shock_angle > result.cone_angle


def test_cone_high_mach():
    """Test cone at high Mach number."""
    result = solve_taylor_maccoll(mach=8.0, cone_angle=10.0)
    assert result.shock_angle > result.cone_angle


# --------------------------------------------------
# normal shock error paths
# --------------------------------------------------


def test_normal_shock_high_mach():
    """Test normal shock at high Mach number."""
    result = solve_normal_shock(mach_1=10.0)
    assert result.p_ratio > 100


def test_normal_shock_near_sonic():
    """Test normal shock just above sonic."""
    result = solve_normal_shock(mach_1=1.01)
    assert result.mach_2 < 1.0
    assert result.p_ratio > 1.0


# --------------------------------------------------
# edge cases in result object tests removed — GasdynResult replaced by typed result dataclasses
