"""Tests for oblique shock relations."""

import pytest

from gasdyn.relations.oblique_shock import solve_oblique

# --------------------------------------------------
# solve shock_angle from mach + deflection_angle
# --------------------------------------------------


def test_solve_weak_shock_angle():
    """Test solving weak shock angle from M and deflection."""
    result = solve_oblique(mach=2.0, deflection_angle=10.0, branch="weak")
    assert abs(result.shock_angle - 39.3) < 1e-1
    assert abs(result.deflection_angle - 10.0) < 1e-3


def test_solve_strong_shock_angle():
    """Test solving strong shock angle from M and deflection."""
    result = solve_oblique(mach=2.0, deflection_angle=10.0, branch="strong")
    # strong shock has larger angle
    assert result.shock_angle > 60
    assert abs(result.deflection_angle - 10.0) < 1e-3


def test_weak_vs_strong():
    """Test that weak and strong branches give different shock angles."""
    weak = solve_oblique(mach=3.0, deflection_angle=15.0, branch="weak")
    strong = solve_oblique(mach=3.0, deflection_angle=15.0, branch="strong")
    assert weak.shock_angle < strong.shock_angle
    # both should have same deflection
    assert abs(weak.deflection_angle - 15.0) < 1e-3
    assert abs(strong.deflection_angle - 15.0) < 1e-3


# --------------------------------------------------
# solve deflection_angle from mach + shock_angle
# --------------------------------------------------


def test_solve_deflection_angle():
    """Test solving deflection angle from M and shock angle."""
    result = solve_oblique(mach=2.0, shock_angle=39.3)
    assert abs(result.deflection_angle - 10.0) < 1e-1
    assert abs(result.shock_angle - 39.3) < 1e-3


# --------------------------------------------------
# solve mach from deflection_angle + shock_angle
# --------------------------------------------------


def test_solve_mach():
    """Test solving Mach number from angles."""
    result = solve_oblique(deflection_angle=10.0, shock_angle=39.3)
    assert abs(result.mach_1 - 2.0) < 1e-1


# --------------------------------------------------
# angle unit conversion
# --------------------------------------------------


# --------------------------------------------------
# error handling
# --------------------------------------------------


def test_wrong_number_inputs():
    """Test that providing wrong number of inputs raises ValueError."""
    with pytest.raises(ValueError, match="exactly two"):
        solve_oblique(mach=2.0)

    with pytest.raises(ValueError, match="exactly two"):
        solve_oblique(mach=2.0, deflection_angle=10.0, shock_angle=39.3)


def test_invalid_gamma():
    """Test that gamma <= 1 raises ValueError."""
    with pytest.raises(ValueError, match="gamma must be > 1"):
        solve_oblique(mach=2.0, deflection_angle=10.0, gamma=1.0)


def test_invalid_mach():
    """Test that mach <= 1 raises ValueError."""
    with pytest.raises(ValueError, match="mach must be > 1"):
        solve_oblique(mach=0.9, deflection_angle=10.0)


def test_deflection_exceeds_maximum():
    """Test that excessive deflection angle raises ValueError."""
    with pytest.raises(ValueError, match="exceeds maximum"):
        solve_oblique(mach=2.0, deflection_angle=50.0)


def test_invalid_shock_angle():
    """Test that invalid shock angle raises ValueError."""
    # shock angle below mach angle
    with pytest.raises(ValueError, match="must be between"):
        solve_oblique(mach=2.0, shock_angle=20.0)


def test_invalid_branch():
    """Test that invalid branch raises ValueError."""
    with pytest.raises(ValueError, match="branch must be"):
        solve_oblique(mach=2.0, deflection_angle=10.0, branch="invalid")


# --------------------------------------------------
# physical consistency
# --------------------------------------------------


def test_downstream_properties():
    """Test that downstream properties are computed."""
    result = solve_oblique(mach=2.0, deflection_angle=10.0)
    assert result.mach_2 > 0
    assert result.p_ratio > 1  # pressure increases
    assert result.t_ratio > 1  # temperature increases
    assert result.p0_ratio < 1  # stagnation pressure decreases


def test_normal_components():
    """Test that normal mach components are computed."""
    result = solve_oblique(mach=2.0, deflection_angle=10.0)
    assert result.mn_1 > 0
    assert result.mn_2 > 0
    assert result.mn_1 > result.mn_2  # normal component decreases


# --------------------------------------------------
# result structure
# --------------------------------------------------


def test_result_structure():
    """Test that result contains expected fields."""
    result = solve_oblique(mach=2.0, deflection_angle=10.0)
    assert hasattr(result, "mach_1")
    assert hasattr(result, "mach_2")
    assert hasattr(result, "mn_1")
    assert hasattr(result, "mn_2")
    assert hasattr(result, "deflection_angle")
    assert hasattr(result, "shock_angle")
    assert hasattr(result, "p_ratio")
    assert hasattr(result, "gamma")
