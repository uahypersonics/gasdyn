"""Tests for normal shock relations."""

import pytest

from gasdyn.relations.normal_shock import solve_normal_shock

# --------------------------------------------------
# forward solve from mach_1
# --------------------------------------------------


def test_solve_from_mach_1():
    """Test solving normal shock from upstream Mach number."""
    result = solve_normal_shock(mach_1=2.0)
    assert abs(result.mach_1 - 2.0) < 1e-10
    assert abs(result.mach_2 - 0.5774) < 1e-4
    assert abs(result.p_ratio - 4.5) < 1e-4
    assert abs(result.t_ratio - 1.6875) < 1e-4
    assert abs(result.rho_ratio - 2.6667) < 1e-4
    assert abs(result.p0_ratio - 0.7209) < 1e-4


def test_solve_weak_shock():
    """Test weak shock at M1 slightly above 1."""
    result = solve_normal_shock(mach_1=1.1)
    # weak shock should have small jumps
    assert result.p_ratio < 1.3
    assert result.mach_2 < 1.0
    assert result.mach_2 > 0.9


def test_solve_strong_shock():
    """Test strong shock at high Mach."""
    result = solve_normal_shock(mach_1=5.0)
    # strong shock should have large jumps
    assert result.p_ratio > 20
    assert result.mach_2 < 0.5


# --------------------------------------------------
# inverse solve from p_ratio
# --------------------------------------------------


def test_solve_from_p_ratio():
    """Test solving from pressure ratio."""
    result = solve_normal_shock(p_ratio=4.5)
    assert abs(result.mach_1 - 2.0) < 1e-3
    assert abs(result.p_ratio - 4.5) < 1e-4


def test_solve_from_weak_p_ratio():
    """Test solving from weak shock pressure ratio."""
    result = solve_normal_shock(p_ratio=1.245, gamma=1.4)
    assert result.mach_1 > 1.0
    assert result.mach_1 < 1.2


# --------------------------------------------------
# error handling
# --------------------------------------------------


def test_no_input_error():
    """Test that providing no input raises ValueError."""
    with pytest.raises(ValueError, match="Must provide exactly one input"):
        solve_normal_shock()


def test_multiple_inputs_error():
    """Test that providing multiple inputs raises ValueError."""
    with pytest.raises(ValueError, match="got multiple"):
        solve_normal_shock(mach_1=2.0, p_ratio=4.5)


def test_invalid_gamma():
    """Test that gamma <= 1 raises ValueError."""
    with pytest.raises(ValueError, match="gamma must be > 1"):
        solve_normal_shock(mach_1=2.0, gamma=1.0)


def test_invalid_mach_1():
    """Test that mach_1 <= 1 raises ValueError."""
    with pytest.raises(ValueError, match="mach_1 must be > 1"):
        solve_normal_shock(mach_1=1.0)

    with pytest.raises(ValueError, match="mach_1 must be > 1"):
        solve_normal_shock(mach_1=0.5)


def test_invalid_p_ratio():
    """Test that p_ratio <= 1 raises ValueError."""
    with pytest.raises(ValueError, match="p_ratio must be > 1"):
        solve_normal_shock(p_ratio=1.0)

    with pytest.raises(ValueError, match="p_ratio must be > 1"):
        solve_normal_shock(p_ratio=0.5)


# --------------------------------------------------
# different gamma values
# --------------------------------------------------


def test_different_gamma():
    """Test with non-air gamma value."""
    result = solve_normal_shock(mach_1=2.0, gamma=1.67)
    assert abs(result.mach_1 - 2.0) < 1e-10
    assert result.gamma == 1.67
    # ratios should be different from air
    result_air = solve_normal_shock(mach_1=2.0, gamma=1.4)
    assert abs(result.p_ratio - result_air.p_ratio) > 1e-2


# --------------------------------------------------
# physical consistency
# --------------------------------------------------


def test_mach_2_always_subsonic():
    """Test that downstream Mach is always subsonic."""
    for M1 in [1.5, 2.0, 3.0, 5.0, 10.0]:
        result = solve_normal_shock(mach_1=M1)
        assert result.mach_2 < 1.0


def test_entropy_increase():
    """Test that stagnation pressure always decreases (entropy increases)."""
    for M1 in [1.5, 2.0, 3.0, 5.0]:
        result = solve_normal_shock(mach_1=M1)
        assert result.p0_ratio < 1.0


# --------------------------------------------------
# result structure
# --------------------------------------------------


def test_result_structure():
    """Test that result contains expected fields."""
    result = solve_normal_shock(mach_1=2.0)
    assert hasattr(result, "mach_1")
    assert hasattr(result, "mach_2")
    assert hasattr(result, "p_ratio")
    assert hasattr(result, "t_ratio")
    assert hasattr(result, "rho_ratio")
    assert hasattr(result, "p0_ratio")
    assert hasattr(result, "gamma")
