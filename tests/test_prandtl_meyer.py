"""Tests for Prandtl-Meyer expansion relations."""

import pytest

from gasdyn.relations.prandtl_meyer import solve_prandtl_meyer

# --------------------------------------------------
# forward solve from mach_1
# --------------------------------------------------


def test_prandtl_meyer_function_value():
    """Test Prandtl-Meyer function at M=2."""
    result = solve_prandtl_meyer(mach_1=2.0, mach_2=2.1)
    # at M=2, nu should be around 26.38 deg
    assert abs(result.nu_1 - 26.38) < 1e-1


def test_solve_mach_2_from_deflection():
    """Test solving mach_2 from mach_1 and deflection angle."""
    result = solve_prandtl_meyer(mach_1=2.0, deflection_angle=10.0)
    assert result.mach_2 > result.mach_1
    assert abs(result.deflection_angle - 10.0) < 1e-3


def test_solve_deflection_from_mach_numbers():
    """Test solving deflection angle from mach_1 and mach_2."""
    result = solve_prandtl_meyer(mach_1=2.0, mach_2=3.0)
    assert result.deflection_angle > 0
    # nu(3) - nu(2) should give positive deflection
    assert result.mach_1 == 2.0
    assert result.mach_2 == 3.0


def test_solve_mach_1_from_mach_2_and_deflection():
    """Test solving mach_1 from mach_2 and deflection angle."""
    result = solve_prandtl_meyer(mach_2=3.0, deflection_angle=10.0)
    assert result.mach_1 < result.mach_2
    assert abs(result.deflection_angle - 10.0) < 1e-3


# --------------------------------------------------
# expansion properties
# --------------------------------------------------


def test_expansion_decreases_pressure():
    """Test that expansion decreases pressure."""
    result = solve_prandtl_meyer(mach_1=2.0, deflection_angle=10.0)
    assert result.p_ratio < 1.0


def test_expansion_decreases_temperature():
    """Test that expansion decreases temperature."""
    result = solve_prandtl_meyer(mach_1=2.0, deflection_angle=10.0)
    assert result.t_ratio < 1.0


def test_expansion_decreases_density():
    """Test that expansion decreases density."""
    result = solve_prandtl_meyer(mach_1=2.0, deflection_angle=10.0)
    assert result.rho_ratio < 1.0


# --------------------------------------------------
# angle unit conversion
# --------------------------------------------------


# --------------------------------------------------
# error handling
# --------------------------------------------------


def test_wrong_number_inputs():
    """Test that providing wrong number of inputs raises ValueError."""
    with pytest.raises(ValueError, match="exactly two"):
        solve_prandtl_meyer(mach_1=2.0)

    with pytest.raises(ValueError, match="exactly two"):
        solve_prandtl_meyer(mach_1=2.0, mach_2=3.0, deflection_angle=10.0)


def test_invalid_gamma():
    """Test that gamma <= 1 raises ValueError."""
    with pytest.raises(ValueError, match="gamma must be > 1"):
        solve_prandtl_meyer(mach_1=2.0, mach_2=3.0, gamma=1.0)


def test_invalid_mach_1():
    """Test that mach_1 <= 1 raises ValueError."""
    with pytest.raises(ValueError, match="mach_1 must be > 1"):
        solve_prandtl_meyer(mach_1=0.9, mach_2=2.0)


def test_invalid_mach_2():
    """Test that mach_2 <= 1 raises ValueError."""
    with pytest.raises(ValueError, match="mach_2 must be > 1"):
        solve_prandtl_meyer(mach_1=2.0, mach_2=0.9)


def test_compression_error():
    """Test that compression (M2 < M1) raises ValueError."""
    with pytest.raises(ValueError, match="must be > mach_1"):
        solve_prandtl_meyer(mach_1=3.0, mach_2=2.0)


def test_negative_deflection():
    """Test that negative deflection raises ValueError."""
    with pytest.raises(ValueError, match="must be >= 0"):
        solve_prandtl_meyer(mach_1=2.0, deflection_angle=-5.0)


# --------------------------------------------------
# different gamma values
# --------------------------------------------------


def test_different_gamma():
    """Test with non-air gamma value."""
    result = solve_prandtl_meyer(mach_1=2.0, mach_2=3.0, gamma=1.67)
    assert result.gamma == 1.67
    # PM angle should be different from air
    result_air = solve_prandtl_meyer(mach_1=2.0, mach_2=3.0, gamma=1.4)
    assert abs(result.nu_1 - result_air.nu_1) > 1.0


# --------------------------------------------------
# result structure
# --------------------------------------------------


def test_result_structure():
    """Test that result contains expected fields."""
    result = solve_prandtl_meyer(mach_1=2.0, deflection_angle=10.0)
    assert hasattr(result, "mach_1")
    assert hasattr(result, "mach_2")
    assert hasattr(result, "nu_1")
    assert hasattr(result, "nu_2")
    assert hasattr(result, "deflection_angle")
    assert hasattr(result, "p_ratio")
    assert hasattr(result, "t_ratio")
    assert hasattr(result, "rho_ratio")
    assert hasattr(result, "gamma")
