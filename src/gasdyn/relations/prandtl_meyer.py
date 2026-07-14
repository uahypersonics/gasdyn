"""Prandtl-Meyer expansion relations."""

from __future__ import annotations

import dataclasses
import json
import math
from dataclasses import dataclass
from typing import ClassVar

from scipy.optimize import brentq


# --------------------------------------------------
# result dataclass
# --------------------------------------------------
@dataclass
class PrandtlMeyerResult:
    """Result of solve_prandtl_meyer."""

    # upstream Mach number [-]
    mach_1: float
    # downstream Mach number [-]
    mach_2: float
    # upstream Prandtl-Meyer angle [deg]
    nu_1: float
    # downstream Prandtl-Meyer angle [deg]
    nu_2: float
    # flow turning angle [deg]
    deflection_angle: float
    # static pressure ratio p2/p1 [-]
    p_ratio: float
    # static temperature ratio T2/T1 [-]
    t_ratio: float
    # density ratio rho2/rho1 [-]
    rho_ratio: float
    # ratio of specific heats [-]
    gamma: float

    # units for each field (used by CLI formatter)
    _UNITS: ClassVar[dict[str, str]] = {
        "mach_1":          "-",
        "mach_2":          "-",
        "nu_1":            "deg",
        "nu_2":            "deg",
        "deflection_angle": "deg",
        "p_ratio":         "-",
        "t_ratio":         "-",
        "rho_ratio":       "-",
        "gamma":           "-",
    }


def format_prandtl_meyer_result(result: PrandtlMeyerResult, as_json: bool) -> str:
    """Format Prandtl-Meyer result for CLI output."""
    if as_json:
        return _to_json_prandtl_meyer(result)
    return _to_str_prandtl_meyer(result)


def _to_str_prandtl_meyer(result: PrandtlMeyerResult) -> str:
    """Format Prandtl-Meyer result as a human-readable table."""
    units = getattr(type(result), "_UNITS", {})
    fields = dataclasses.fields(result)

    # determine column width from the longest field name
    col_width = max(len(f.name) for f in fields)

    lines = ["=" * 60, "Prandtl-Meyer Results", "=" * 60]
    for f in fields:
        val = getattr(result, f.name)
        unit = units.get(f.name, "-")
        lines.append(f"{f.name:<{col_width}}  :  {val:>14g}  [{unit}]")
    lines.append("=" * 60)

    return "\n".join(lines)


def _to_json_prandtl_meyer(result: PrandtlMeyerResult) -> str:
    """Serialise Prandtl-Meyer result to JSON with [value, unit] pairs."""
    units = getattr(type(result), "_UNITS", {})
    values = dataclasses.asdict(result)
    payload = {key: [value, units.get(key, "-")] for key, value in values.items()}
    return json.dumps(payload, indent=2)


def solve_prandtl_meyer(
    mach_1: float = None,
    mach_2: float = None,
    deflection_angle: float = None,
    gamma: float = 1.4,
) -> PrandtlMeyerResult:
    """
    Solve Prandtl-Meyer expansion relations for isentropic turning.

    Accepts exactly TWO of: mach_1, mach_2, deflection_angle.

    For an isentropic expansion: nu(M2) = nu(M1) + deflection_angle

    Args:
        mach_1: Upstream Mach number.
        mach_2: Downstream Mach number.
        deflection_angle: Flow deflection angle (degrees by default, or (value, "rad")).
        gamma: Ratio of specific heats (default 1.4).

    Returns:
        GasdynResult with mach_1, mach_2, nu_1, nu_2, deflection_angle,
        p_ratio, t_ratio, rho_ratio, gamma.

    Raises:
        ValueError: If wrong number of inputs or invalid values.

    Examples:
        >>> result = solve_prandtl_meyer(mach_1=2.0, deflection_angle=10.0)
        >>> result.mach_2
        2.38...
    """
    # validate inputs
    inputs = [mach_1, mach_2, deflection_angle]
    provided = sum(x is not None for x in inputs)

    if provided != 2:
        raise ValueError("Must provide exactly two of: mach_1, mach_2, deflection_angle")

    # validate gamma
    if gamma <= 1:
        raise ValueError(f"gamma must be > 1, got {gamma}")

    # convert deflection angle from degrees to radians
    theta = math.radians(deflection_angle) if deflection_angle is not None else None

    # --------------------------------------------------
    # case 1: mach_1 + deflection_angle -> solve for mach_2
    # --------------------------------------------------

    if mach_1 is not None and theta is not None and mach_2 is None:
        if mach_1 <= 1:
            raise ValueError(f"mach_1 must be > 1, got {mach_1}")
        if theta < 0:
            raise ValueError("deflection_angle must be >= 0")

        nu1 = _prandtl_meyer_angle(mach_1, gamma)
        nu2 = nu1 + theta

        # solve for mach_2 from nu2
        mach_2 = _inverse_prandtl_meyer(nu2, gamma)

        if mach_2 <= mach_1:
            raise ValueError("Specified state implies compression, not expansion")

    # --------------------------------------------------
    # case 2: mach_1 + mach_2 -> solve for deflection_angle
    # --------------------------------------------------

    elif mach_1 is not None and mach_2 is not None and theta is None:
        if mach_1 <= 1:
            raise ValueError(f"mach_1 must be > 1, got {mach_1}")
        if mach_2 <= 1:
            raise ValueError(f"mach_2 must be > 1, got {mach_2}")
        if mach_2 <= mach_1:
            raise ValueError("mach_2 must be > mach_1 for expansion")

        nu1 = _prandtl_meyer_angle(mach_1, gamma)
        nu2 = _prandtl_meyer_angle(mach_2, gamma)
        theta = nu2 - nu1

        if theta < 0:
            raise ValueError("Specified state implies compression, not expansion")

    # --------------------------------------------------
    # case 3: mach_2 + deflection_angle -> solve for mach_1
    # --------------------------------------------------

    elif mach_2 is not None and theta is not None and mach_1 is None:
        if mach_2 <= 1:
            raise ValueError(f"mach_2 must be > 1, got {mach_2}")
        if theta < 0:
            raise ValueError("deflection_angle must be >= 0")

        nu2 = _prandtl_meyer_angle(mach_2, gamma)
        nu1 = nu2 - theta

        if nu1 < 0:
            raise ValueError("No valid solution for given inputs")

        mach_1 = _inverse_prandtl_meyer(nu1, gamma)

        if mach_1 >= mach_2:
            raise ValueError("Specified state implies compression, not expansion")

    else:
        raise ValueError("Invalid combination of inputs")

    # --------------------------------------------------
    # compute ratios from isentropic relations
    # --------------------------------------------------

    nu1 = _prandtl_meyer_angle(mach_1, gamma)
    nu2 = _prandtl_meyer_angle(mach_2, gamma)
    theta = nu2 - nu1

    # isentropic ratios: downstream/upstream
    t1_t0 = 1.0 / (1.0 + (gamma - 1) / 2.0 * mach_1**2)
    t2_t0 = 1.0 / (1.0 + (gamma - 1) / 2.0 * mach_2**2)
    t_rat = t2_t0 / t1_t0

    exponent = gamma / (gamma - 1)
    p_rat = t_rat**exponent

    exponent = 1.0 / (gamma - 1)
    rho_rat = t_rat**exponent

    # --------------------------------------------------
    # return result (angles in degrees)
    # --------------------------------------------------

    return PrandtlMeyerResult(
        mach_1=mach_1,
        mach_2=mach_2,
        nu_1=math.degrees(nu1),
        nu_2=math.degrees(nu2),
        deflection_angle=math.degrees(theta),
        p_ratio=p_rat,
        t_ratio=t_rat,
        rho_ratio=rho_rat,
        gamma=gamma,
    )


# --------------------------------------------------
# helper functions
# --------------------------------------------------
def _prandtl_meyer_angle(M: float, gamma: float) -> float:
    """
    Compute Prandtl-Meyer function nu(M).

    nu(M) = sqrt((gamma+1)/(gamma-1)) * atan(sqrt((gamma-1)/(gamma+1) * (M^2 - 1)))
            - atan(sqrt(M^2 - 1))
    """
    sqrt_term = math.sqrt((gamma + 1) / (gamma - 1))
    inner_sqrt = math.sqrt((gamma - 1) / (gamma + 1) * (M**2 - 1.0))
    term1 = sqrt_term * math.atan(inner_sqrt)
    term2 = math.atan(math.sqrt(M**2 - 1.0))
    return term1 - term2


def _inverse_prandtl_meyer(nu: float, gamma: float) -> float:
    """Solve for Mach number given Prandtl-Meyer angle."""

    def residual(M_guess):
        return _prandtl_meyer_angle(M_guess, gamma) - nu

    # maximum possible nu for gamma=1.4 is about 130 degrees ~ 2.27 rad
    # search from sonic to high Mach
    M = brentq(residual, 1.0 + 1e-6, 50.0)
    return M
