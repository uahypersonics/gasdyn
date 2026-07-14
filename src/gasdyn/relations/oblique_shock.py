"""Oblique shock relations."""

from __future__ import annotations

import dataclasses
import json
import math
from dataclasses import dataclass
from typing import ClassVar

from scipy.optimize import brentq

from gasdyn.relations.normal_shock import (
    mach_downstream_normal,
    pres_ratio_normal,
    temp_ratio_normal,
)


# --------------------------------------------------
# result dataclass
# --------------------------------------------------
@dataclass
class ObliqueResult:
    """Result of solve_oblique."""

    # upstream Mach number [-]
    mach_1: float
    # downstream Mach number [-]
    mach_2: float
    # upstream normal Mach number [-]
    mn_1: float
    # downstream normal Mach number [-]
    mn_2: float
    # flow deflection angle [deg]
    deflection_angle: float
    # shock wave angle [deg]
    shock_angle: float
    # static pressure ratio p2/p1 [-]
    p_ratio: float
    # static temperature ratio T2/T1 [-]
    t_ratio: float
    # density ratio rho2/rho1 [-]
    rho_ratio: float
    # total pressure ratio p02/p01 [-]
    p0_ratio: float
    # ratio of specific heats [-]
    gamma: float

    # units for each field (used by CLI formatter)
    _UNITS: ClassVar[dict[str, str]] = {
        "mach_1":          "-",
        "mach_2":          "-",
        "mn_1":            "-",
        "mn_2":            "-",
        "deflection_angle": "deg",
        "shock_angle":     "deg",
        "p_ratio":         "-",
        "t_ratio":         "-",
        "rho_ratio":       "-",
        "p0_ratio":        "-",
        "gamma":           "-",
    }


def format_oblique_result(result: ObliqueResult, as_json: bool) -> str:
    """Format oblique-shock result for CLI output."""
    if as_json:
        return _to_json_oblique(result)
    return _to_str_oblique(result)


def _to_str_oblique(result: ObliqueResult) -> str:
    """Format oblique-shock result as a human-readable table."""
    units = getattr(type(result), "_UNITS", {})
    fields = dataclasses.fields(result)

    # determine column width from the longest field name
    col_width = max(len(f.name) for f in fields)

    lines = ["=" * 60, "Oblique Shock Results", "=" * 60]
    for f in fields:
        val = getattr(result, f.name)
        unit = units.get(f.name, "-")
        lines.append(f"{f.name:<{col_width}}  :  {val:>14g}  [{unit}]")
    lines.append("=" * 60)

    return "\n".join(lines)


def _to_json_oblique(result: ObliqueResult) -> str:
    """Serialise oblique-shock result to JSON with [value, unit] pairs."""
    units = getattr(type(result), "_UNITS", {})
    values = dataclasses.asdict(result)
    payload = {key: [value, units.get(key, "-")] for key, value in values.items()}
    return json.dumps(payload, indent=2)


def solve_oblique(
    mach: float = None,
    deflection_angle: float = None,
    shock_angle: float = None,
    gamma: float = 1.4,
    branch: str = "weak",
) -> ObliqueResult:
    """
    Solve oblique shock relations using theta-beta-Mach relation.

    Accepts exactly TWO of: mach, deflection_angle, shock_angle.

    Args:
        mach: Upstream Mach number.
        deflection_angle: Flow deflection angle (degrees by default, or (value, "rad")).
        shock_angle: Shock wave angle (degrees by default, or (value, "rad")).
        gamma: Ratio of specific heats (default 1.4).
        branch: For mach + deflection_angle, "weak" or "strong" (default "weak").

    Returns:
        GasdynResult with mach_1, mach_2, mn_1, mn_2, deflection_angle, shock_angle,
        p_ratio, t_ratio, rho_ratio, p0_ratio, gamma.

    Raises:
        ValueError: If wrong number of inputs or invalid values.

    Examples:
        >>> result = solve_oblique(mach=2.0, deflection_angle=10.0)
        >>> result.shock_angle
        39.3...
    """
    # validate inputs
    inputs = [mach, deflection_angle, shock_angle]
    provided = sum(x is not None for x in inputs)

    if provided != 2:
        raise ValueError("Must provide exactly two of: mach, deflection_angle, shock_angle")

    # validate gamma
    if gamma <= 1:
        raise ValueError(f"gamma must be > 1, got {gamma}")

    # convert angles from degrees to radians
    theta = math.radians(deflection_angle) if deflection_angle is not None else None
    beta  = math.radians(shock_angle) if shock_angle is not None else None

    # --------------------------------------------------
    # case 1: mach + deflection_angle -> solve for shock_angle
    # --------------------------------------------------

    if mach is not None and theta is not None and beta is None:
        if mach <= 1:
            raise ValueError(f"mach must be > 1, got {mach}")
        if theta < 0:
            raise ValueError(f"deflection_angle must be >= 0, got {math.degrees(theta)}")

        # find maximum deflection angle
        theta_max, beta_max = _find_max_deflection(mach, gamma)

        if theta > theta_max:
            raise ValueError(
                f"deflection_angle {math.degrees(theta):.2f} deg exceeds "
                f"maximum {math.degrees(theta_max):.2f} deg for M={mach}"
            )

        # validate branch
        if branch not in ["weak", "strong"]:
            raise ValueError(f"branch must be 'weak' or 'strong', got '{branch}'")

        # define theta-beta-Mach residual
        def residual(beta_guess):
            return theta_beta_m(mach, beta_guess, gamma) - theta

        # solve for shock angle
        mu = math.asin(1.0 / mach)  # mach angle
        if branch == "weak":
            beta = brentq(residual, mu, beta_max)
        else:
            beta = brentq(residual, beta_max, math.pi / 2)

    # --------------------------------------------------
    # case 2: mach + shock_angle -> solve for deflection_angle
    # --------------------------------------------------

    elif mach is not None and beta is not None and theta is None:
        if mach <= 1:
            raise ValueError(f"mach must be > 1, got {mach}")

        mu = math.asin(1.0 / mach)
        if beta < mu or beta > math.pi / 2:
            raise ValueError(
                f"shock_angle must be between mach angle {math.degrees(mu):.2f} deg "
                f"and 90 deg, got {math.degrees(beta):.2f} deg"
            )

        theta = theta_beta_m(mach, beta, gamma)

    # --------------------------------------------------
    # case 3: deflection_angle + shock_angle -> solve for mach
    # --------------------------------------------------

    elif theta is not None and beta is not None and mach is None:
        if theta < 0:
            raise ValueError("deflection_angle must be >= 0")
        if beta <= theta:
            raise ValueError("shock_angle must be > deflection_angle")
        if beta > math.pi / 2:
            raise ValueError("shock_angle must be <= 90 deg")

        # solve for mach
        def residual(M_guess):
            return theta_beta_m(M_guess, beta, gamma) - theta

        # find suitable upper bound
        M_upper = 20.0
        mach = brentq(residual, 1.0 + 1e-6, M_upper)

    else:
        raise ValueError("Invalid combination of inputs")

    # --------------------------------------------------
    # compute downstream properties
    # --------------------------------------------------

    # normal component of upstream mach
    Mn1 = mach * math.sin(beta)

    # normal shock relations for normal component
    p_rat = 1.0 + (2.0 * gamma / (gamma + 1)) * (Mn1**2 - 1.0)
    rho_rat = ((gamma + 1) * Mn1**2) / ((gamma - 1) * Mn1**2 + 2.0)
    t_rat = p_rat / rho_rat

    # downstream normal mach
    Mn2_squared = (1.0 + 0.5 * (gamma - 1) * Mn1**2) / (
        gamma * Mn1**2 - 0.5 * (gamma - 1)
    )
    Mn2 = math.sqrt(Mn2_squared)

    # downstream mach number
    M2 = Mn2 / math.sin(beta - theta)

    # stagnation pressure ratio
    p01_p1 = (1.0 + (gamma - 1) / 2.0 * mach**2) ** (gamma / (gamma - 1))
    p02_p2 = (1.0 + (gamma - 1) / 2.0 * M2**2) ** (gamma / (gamma - 1))
    p0_rat = p_rat * p02_p2 / p01_p1

    # --------------------------------------------------
    # return result (angles in degrees)
    # --------------------------------------------------

    return ObliqueResult(
        mach_1=mach,
        mach_2=M2,
        mn_1=Mn1,
        mn_2=Mn2,
        deflection_angle=math.degrees(theta),
        shock_angle=math.degrees(beta),
        p_ratio=p_rat,
        t_ratio=t_rat,
        rho_ratio=rho_rat,
        p0_ratio=p0_rat,
        gamma=gamma,
    )


# --------------------------------------------------
# helper functions
# --------------------------------------------------


def theta_beta_m(M: float, beta: float, gamma: float) -> float:
    """
    Compute deflection angle from theta-beta-Mach relation.

    tan(theta) = 2*cot(beta) * (M^2*sin(beta)^2 - 1) / (M^2*(gamma + cos(2*beta)) + 2)
    """
    numerator = 2.0 * (1.0 / math.tan(beta)) * (M**2 * math.sin(beta) ** 2 - 1.0)
    denominator = M**2 * (gamma + math.cos(2.0 * beta)) + 2.0
    return math.atan(numerator / denominator)


def _find_max_deflection(M: float, gamma: float) -> tuple[float, float]:
    """Find maximum deflection angle and corresponding shock angle."""
    # maximize theta as function of beta
    from scipy.optimize import minimize_scalar

    def neg_theta(beta):
        return -theta_beta_m(M, beta, gamma)

    mu = math.asin(1.0 / M)
    result = minimize_scalar(neg_theta, bounds=(mu, math.pi / 2), method="bounded")
    beta_max = result.x
    theta_max = -result.fun
    return theta_max, beta_max


# --------------------------------------------------
# scalar ratio helpers (reusable by other modules)
# --------------------------------------------------
def pres_ratio_oblique(mach: float, beta: float, gamma: float) -> float:
    """Static pressure ratio p2/p1 across an oblique shock.

    Args:
        mach:  Freestream Mach number.
        beta:  Shock wave angle [rad].
        gamma: Ratio of specific heats.

    Returns:
        p2/p1 [-]
    """
    mn1 = mach * math.sin(beta)
    return pres_ratio_normal(mn1, gamma)


def temp_ratio_oblique(mach: float, beta: float, gamma: float) -> float:
    """Static temperature ratio T2/T1 across an oblique shock.

    Args:
        mach:  Freestream Mach number.
        beta:  Shock wave angle [rad].
        gamma: Ratio of specific heats.

    Returns:
        T2/T1 [-]
    """
    mn1 = mach * math.sin(beta)
    return temp_ratio_normal(mn1, gamma)


def mach_downstream_oblique(mach: float, beta: float, gamma: float) -> float:
    """Post-shock Mach number M2 downstream of an oblique shock.

    Args:
        mach:  Freestream Mach number.
        beta:  Shock wave angle [rad].
        gamma: Ratio of specific heats.

    Returns:
        M2 [-]
    """
    mn1   = mach * math.sin(beta)
    mn2   = mach_downstream_normal(mn1, gamma)
    delta = theta_beta_m(mach, beta, gamma)
    return mn2 / math.sin(beta - delta)
