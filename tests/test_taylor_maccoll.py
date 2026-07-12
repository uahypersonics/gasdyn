"""Tests for Taylor-Maccoll conical flow solver."""

import pytest

from gasdyn.taylor_maccoll.taylor_maccoll import (
    solve_taylor_maccoll,
    solve_taylor_maccoll_cone_shock,
    solve_taylor_maccoll_mach_cone,
    solve_taylor_maccoll_mach_shock,
)

# --------------------------------------------------
# named solver functions
# --------------------------------------------------


def test_mach_cone_returns_shock_angle():
    """solve_taylor_maccoll_mach_cone: M=2, cone=15 deg returns a valid shock angle."""
    result = solve_taylor_maccoll_mach_cone(mach=2.0, cone_angle=15.0)
    assert result.shock_angle > 15.0       # shock angle > cone angle
    assert result.shock_angle < 90.0
    assert result.surface_pressure_ratio > 1.0


def test_mach_shock_returns_cone_angle():
    """solve_taylor_maccoll_mach_shock: M=3, shock=25 deg returns cone angle."""
    result = solve_taylor_maccoll_mach_shock(mach=3.0, shock_angle=25.0)
    assert 0.0 < result.cone_angle < 25.0  # cone angle < shock angle
    assert result.surface_pressure_ratio > 1.0


def test_cone_shock_returns_mach():
    """solve_taylor_maccoll_cone_shock: cone=14.68, shock=25 deg returns Mach > 1."""
    result = solve_taylor_maccoll_cone_shock(cone_angle=14.68, shock_angle=25.0)
    assert result.mach > 1.0
    assert abs(result.mach - 3.0) < 0.1   # should recover approximately M=3
    assert result.surface_pressure_ratio > 1.0


# --------------------------------------------------
# basic functionality (dispatcher)
# --------------------------------------------------


def test_solve_taylor_maccoll_from_mach_and_cone_angle():
    """Test known configuration: M=2, cone_angle=15 deg."""
    result = solve_taylor_maccoll(mach=2.0, cone_angle=15.0)
    # shock angle should be reasonable for this configuration
    assert result.shock_angle > result.cone_angle
    assert result.shock_angle < 90.0
    assert abs(result.cone_angle - 15.0) < 1e-3
    assert abs(result.mach - 2.0) < 1e-6


def test_solve_taylor_maccoll_returns_result():
    """Test that solve_taylor_maccoll returns a TaylorMaccollResult."""
    from gasdyn import TaylorMaccollResult
    result = solve_taylor_maccoll(mach=3.0, cone_angle=10.0)
    assert isinstance(result, TaylorMaccollResult)
    assert hasattr(result, "mach")
    assert hasattr(result, "cone_angle")
    assert hasattr(result, "shock_angle")


def test_solve_taylor_maccoll_angle_from_mach_and_shock():
    """Test solving cone angle from Mach and shock angle."""
    result = solve_taylor_maccoll(mach=3.0, shock_angle=25.0)
    assert result.cone_angle > 0
    assert result.cone_angle < result.shock_angle


def test_solve_mach_from_angles():
    """Test solving Mach number from angles."""
    result = solve_taylor_maccoll(cone_angle=10.0, shock_angle=25.0)
    # should give reasonable Mach
    assert result.mach > 2.0
    assert result.mach < 5.0


# --------------------------------------------------
# angle unit conversion
# --------------------------------------------------


# --------------------------------------------------
# error handling
# --------------------------------------------------

def test_wrong_number_inputs():
    """Test that providing wrong number of inputs raises ValueError."""
    with pytest.raises(ValueError, match="exactly two"):
        solve_taylor_maccoll(mach=2.0)

    with pytest.raises(ValueError, match="exactly two"):
        solve_taylor_maccoll(mach=2.0, cone_angle=15.0, shock_angle=45.5)


def test_invalid_mach():
    """Test that mach <= 1 raises ValueError."""
    with pytest.raises(ValueError, match="mach must be > 1"):
        solve_taylor_maccoll(mach=0.9, cone_angle=15.0)


def test_invalid_cone_angle():
    """Test that cone_angle <= 0 raises ValueError."""
    with pytest.raises(ValueError, match="cone_angle must be > 0"):
        solve_taylor_maccoll(mach=2.0, cone_angle=0.0)


def test_invalid_shock_angle():
    """Test that invalid shock angle raises ValueError."""
    with pytest.raises(ValueError, match="must be between"):
        solve_taylor_maccoll(mach=2.0, shock_angle=20.0)


def test_no_attached_shock():
    """Test that excessive cone angle raises ValueError."""
    with pytest.raises(ValueError, match="No attached-shock"):
        solve_taylor_maccoll(mach=2.0, cone_angle=50.0)


# --------------------------------------------------
# physical consistency
# --------------------------------------------------


def test_surface_properties():
    """Test that surface properties are computed."""
    result = solve_taylor_maccoll(mach=3.0, cone_angle=10.0)
    assert result.surface_pressure_ratio > 1  # pressure increases
    assert result.surface_temp_ratio > 1  # temperature increases


def test_shock_angle_exceeds_cone_angle():
    """Test that shock angle is always greater than cone angle."""
    result = solve_taylor_maccoll(mach=3.0, cone_angle=15.0)
    assert result.shock_angle > result.cone_angle


# --------------------------------------------------
# result structure
# --------------------------------------------------


def test_result_structure():
    """Test that result contains expected fields."""
    result = solve_taylor_maccoll(mach=2.0, cone_angle=15.0)
    assert hasattr(result, "mach")
    assert hasattr(result, "cone_angle")
    assert hasattr(result, "shock_angle")
    assert hasattr(result, "surface_pressure_ratio")
    assert hasattr(result, "surface_temp_ratio")
    assert hasattr(result, "gamma")
