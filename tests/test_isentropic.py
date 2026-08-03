"""Tests for isentropic flow relations."""

import pytest

from gasdyn.relations.isentropic import solve_isentropic

# --------------------------------------------------
# forward solve from mach number
# --------------------------------------------------


def test_solve_from_mach():
    """Test solving isentropic relations from Mach number."""
    result = solve_isentropic(mach=2.0)
    assert abs(result.mach - 2.0) < 1e-10
    assert abs(result.pres_ratio - 0.1278) < 1e-4
    assert abs(result.temp_ratio - 0.5556) < 1e-4
    assert abs(result.area_ratio - 1.6875) < 1e-4


def test_solve_mach_1():
    """Test sonic conditions at M=1."""
    result = solve_isentropic(mach=1.0)
    assert abs(result.mach - 1.0) < 1e-10
    # at M=1, A/A* = 1
    assert abs(result.area_ratio - 1.0) < 1e-4


def test_solve_subsonic():
    """Test subsonic Mach number."""
    result = solve_isentropic(mach=0.5)
    assert abs(result.mach - 0.5) < 1e-10
    # at M=0.5, t_ratio should be close to 1 (low speed)
    assert result.temp_ratio > 0.9


# --------------------------------------------------
# inverse solves
# --------------------------------------------------


def test_solve_from_p_ratio():
    """Test solving from pressure ratio."""
    result = solve_isentropic(pres_ratio=0.1278)
    assert abs(result.mach - 2.0) < 1e-3
    assert abs(result.pres_ratio - 0.1278) < 1e-4


def test_solve_from_t_ratio():
    """Test solving from temperature ratio."""
    result = solve_isentropic(temp_ratio=0.5556)
    assert abs(result.mach - 2.0) < 1e-3
    assert abs(result.temp_ratio - 0.5556) < 1e-4


def test_solve_from_rho_ratio():
    """Test solving from density ratio."""
    # compute expected rho_ratio for M=2
    result_ref = solve_isentropic(mach=2.0)
    rho_ref = result_ref.dens_ratio

    result = solve_isentropic(dens_ratio=rho_ref)
    assert abs(result.mach - 2.0) < 1e-3
    assert abs(result.dens_ratio - rho_ref) < 1e-4


def test_solve_from_area_ratio_supersonic():
    """Test solving from area ratio (supersonic branch)."""
    result = solve_isentropic(area_ratio=1.6875, branch="supersonic")
    assert abs(result.mach - 2.0) < 1e-3
    assert abs(result.area_ratio - 1.6875) < 1e-4


def test_solve_from_area_ratio_subsonic():
    """Test solving from area ratio (subsonic branch)."""
    # for area_ratio = 1.6875, subsonic solution is around M ~ 0.35
    result = solve_isentropic(area_ratio=1.6875, branch="subsonic")
    assert result.mach < 1.0
    assert abs(result.area_ratio - 1.6875) < 1e-4


def test_area_ratio_branches_different():
    """Test that subsonic and supersonic branches give different Mach numbers."""
    sub = solve_isentropic(area_ratio=2.0, branch="subsonic")
    sup = solve_isentropic(area_ratio=2.0, branch="supersonic")
    assert sub.mach < 1.0
    assert sup.mach > 1.0
    # both should have same area ratio
    assert abs(sub.area_ratio - 2.0) < 1e-4
    assert abs(sup.area_ratio - 2.0) < 1e-4


# --------------------------------------------------
# error handling
# --------------------------------------------------


def test_no_input_error():
    """Test that providing no input raises ValueError."""
    with pytest.raises(ValueError, match="Must provide exactly one input"):
        solve_isentropic()


def test_multiple_inputs_error():
    """Test that providing multiple inputs raises ValueError."""
    with pytest.raises(ValueError, match="got multiple"):
        solve_isentropic(mach=2.0, pres_ratio=0.1278)


def test_invalid_gamma():
    """Test that gamma <= 1 raises ValueError."""
    with pytest.raises(ValueError, match="gamma must be > 1"):
        solve_isentropic(mach=2.0, gamma=1.0)

    with pytest.raises(ValueError, match="gamma must be > 1"):
        solve_isentropic(mach=2.0, gamma=0.5)


def test_invalid_mach():
    """Test that Mach <= 0 raises ValueError."""
    with pytest.raises(ValueError, match="Mach number must be > 0"):
        solve_isentropic(mach=0.0)

    with pytest.raises(ValueError, match="Mach number must be > 0"):
        solve_isentropic(mach=-1.0)


def test_invalid_area_ratio():
    """Test that area_ratio < 1 raises ValueError."""
    with pytest.raises(ValueError, match="area_ratio must be >= 1"):
        solve_isentropic(area_ratio=0.5)


def test_invalid_pres_ratio():
    """Test that invalid p_ratio raises ValueError."""
    with pytest.raises(ValueError, match="pres_ratio must be in"):
        solve_isentropic(pres_ratio=1.5)

    with pytest.raises(ValueError, match="pres_ratio must be in"):
        solve_isentropic(pres_ratio=0.0)


def test_invalid_temp_ratio():
    """Test that invalid t_ratio raises ValueError."""
    with pytest.raises(ValueError, match="temp_ratio must be in"):
        solve_isentropic(temp_ratio=1.5)

    with pytest.raises(ValueError, match="temp_ratio must be in"):
        solve_isentropic(temp_ratio=0.0)


def test_invalid_dens_ratio():
    """Test that invalid rho_ratio raises ValueError."""
    with pytest.raises(ValueError, match="dens_ratio must be in"):
        solve_isentropic(dens_ratio=1.5)

    with pytest.raises(ValueError, match="dens_ratio must be in"):
        solve_isentropic(dens_ratio=0.0)


def test_invalid_branch():
    """Test that invalid branch raises ValueError."""
    with pytest.raises(ValueError, match="branch must be"):
        solve_isentropic(area_ratio=1.5, branch="invalid")


# --------------------------------------------------
# different gamma values
# --------------------------------------------------


def test_different_gamma():
    """Test with non-air gamma value."""
    # test with gamma = 1.67 (monatomic gas)
    result = solve_isentropic(mach=2.0, gamma=1.67)
    assert abs(result.mach - 2.0) < 1e-10
    assert result.gamma == 1.67
    # ratios should be different from air
    result_air = solve_isentropic(mach=2.0, gamma=1.4)
    assert abs(result.pres_ratio - result_air.pres_ratio) > 1e-3


# --------------------------------------------------
# result structure
# --------------------------------------------------


def test_result_structure():
    """Test that result contains expected fields."""
    result = solve_isentropic(mach=2.0)
    assert hasattr(result, "mach")
    assert hasattr(result, "pres_ratio")
    assert hasattr(result, "temp_ratio")
    assert hasattr(result, "dens_ratio")
    assert hasattr(result, "area_ratio")
    assert hasattr(result, "gamma")
