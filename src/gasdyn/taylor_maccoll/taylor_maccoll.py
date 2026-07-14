"""Taylor-Maccoll conical flow solver.

Solves the Taylor-Maccoll equation for inviscid supersonic flow over a
right-circular cone at zero angle of attack.

References
----------
Taylor, G. I. and Maccoll, J. W. (1933).
    "The Air Pressure on a Cone Moving at High Speeds."
    Proceedings of the Royal Society of London, Series A, 139(838), 278-311.
    https://doi.org/10.1098/rspa.1933.0017

Anderson, J. D. (2003).
    Modern Compressible Flow: With Historical Perspective, 3rd ed.
    McGraw-Hill. Section 10.4.
"""

# --------------------------------------------------
# load necessary modules
# --------------------------------------------------
from __future__ import annotations

import dataclasses
import json
import logging
import math
import warnings
from dataclasses import dataclass
from typing import ClassVar

from scipy.integrate import solve_ivp
from scipy.optimize import brentq

from gasdyn.relations.isentropic import pres_ratio_isentropic, temp_ratio_isentropic
from gasdyn.relations.oblique_shock import (
    mach_downstream_oblique,
    pres_ratio_oblique,
    temp_ratio_oblique,
    theta_beta_m,
)


# --------------------------------------------------
# Taylor-Maccoll result data class
# --------------------------------------------------
@dataclass
class TaylorMaccollResult:
    """Result of solve_taylor_maccoll."""

    # freestream Mach number [-]
    mach: float
    # cone half-angle [deg]
    cone_angle: float
    # shock wave angle [deg]
    shock_angle: float
    # surface static pressure ratio p_s/p_inf [-]
    surface_pressure_ratio: float
    # surface static temperature ratio T_s/T_inf [-]
    surface_temp_ratio: float
    # ratio of specific heats [-]
    gamma: float

    # units for each field (used by CLI formatter)
    _UNITS: ClassVar[dict[str, str]] = {
        "mach":                   "-",
        "cone_angle":             "deg",
        "shock_angle":            "deg",
        "surface_pressure_ratio": "-",
        "surface_temp_ratio":     "-",
        "gamma":                  "-",
    }


def format_taylor_maccoll_result(result: TaylorMaccollResult, as_json: bool) -> str:
    """Format Taylor-Maccoll result for CLI output."""
    if as_json:
        return _to_json_taylor_maccoll(result)
    return _to_str_taylor_maccoll(result)


def _to_str_taylor_maccoll(result: TaylorMaccollResult) -> str:
    """Format Taylor-Maccoll result as a human-readable table."""
    units = getattr(type(result), "_UNITS", {})
    fields = dataclasses.fields(result)

    # determine column width from the longest field name
    col_width = max(len(f.name) for f in fields)

    lines = ["=" * 60, "Taylor-Maccoll Results", "=" * 60]
    for f in fields:
        val = getattr(result, f.name)
        unit = units.get(f.name, "-")
        lines.append(f"{f.name:<{col_width}}  :  {val:>14g}  [{unit}]")
    lines.append("=" * 60)
    return "\n".join(lines)


def _to_json_taylor_maccoll(result: TaylorMaccollResult) -> str:
    """Serialise Taylor-Maccoll result to JSON with [value, unit] pairs."""
    units = getattr(type(result), "_UNITS", {})
    values = dataclasses.asdict(result)
    payload = {key: [value, units.get(key, "-")] for key, value in values.items()}
    return json.dumps(payload, indent=2)

# --------------------------------------------------
# taylor maccoll solver dispatcher
# can have 2 inputs compute the third quantity
# --------------------------------------------------
def solve_taylor_maccoll(
    mach: float = None,
    cone_angle: float = None,
    shock_angle: float = None,
    gamma: float = 1.4,
    beta_guess: float | None = None,
) -> TaylorMaccollResult:
    """Dispatcher: solve Taylor-Maccoll equations from any two of mach, cone_angle, shock_angle.

    All angles in degrees.  Exactly two of the three inputs must be provided.

    Args:
        mach:        Freestream Mach number.
        cone_angle:  Cone half-angle [deg].
        shock_angle: Shock wave angle [deg].
        gamma:       Ratio of specific heats (default 1.4).
        beta_guess:  Optional initial guess for the shock angle [deg], used to
                     narrow the root-finding bracket when solving for beta.
                     Provide from a lookup table or a previous nearby solve to
                     reduce the number of ODE evaluations.  Only used when
                     mach + cone_angle are the two provided inputs.

    Returns:
        TaylorMaccollResult.

    Raises:
        ValueError: If not exactly two inputs are provided or values are invalid.

    Examples:
        >>> result = solve_taylor_maccoll(mach=5.0, cone_angle=15.0)
        >>> result.shock_angle  # doctest: +SKIP
        24.5...
    """

    # --------------------------------------------------
    # check that exactly two inputs are provided
    # --------------------------------------------------
    inputs   = [mach, cone_angle, shock_angle]
    provided = sum(x is not None for x in inputs)

    if provided != 2:
        raise ValueError("Must provide exactly two of: mach, cone_angle, shock_angle")

    # --------------------------------------------------
    # input validation
    # --------------------------------------------------

    # make sure mach is supersonic
    if mach is not None and mach <= 1:
        raise ValueError(f"mach must be > 1, got {mach}")

    # make sure cone angle is positive
    if cone_angle is not None and cone_angle <= 0:
        raise ValueError(f"cone_angle must be > 0, got {cone_angle}")

    if mach is not None and shock_angle is not None:
        # shock angle must be between the Mach angle and 90 degrees
        mu = math.degrees(math.asin(1.0 / mach))

        if shock_angle <= mu or shock_angle >= 90.0:
            raise ValueError(
                f"shock_angle must be between mach angle {mu:.2f} deg and 90 deg, "
                f"got {shock_angle:.2f} deg"
            )

    # check that shock angle is greater than cone angle and less than 90 degrees
    # if both cone angle and shock angle are provided
    if cone_angle is not None and shock_angle is not None:
        # shock angle must be greater than cone angle
        if shock_angle <= cone_angle:
            raise ValueError("shock_angle must be > cone_angle")
        if shock_angle >= 90.0:
            raise ValueError("shock_angle must be < 90 deg")

    # --------------------------------------------------
    # select appropriate solver based on provided inputs
    # --------------------------------------------------

    if mach is not None and cone_angle is not None:
        # known mach and cone angle
        # use brentq to find the shock angle that satisfies the cone angle condition
        return solve_taylor_maccoll_mach_cone(mach, cone_angle, gamma, beta_guess)
    elif mach is not None and shock_angle is not None:
        # known mach and shock angle
        # direct integration — no iteration needed
        return solve_taylor_maccoll_mach_shock(mach, shock_angle, gamma)
    else:
        # known cone angle and shock angle
        # use brentq to find the mach number that satisfies the cone and shock angle condition
        return solve_taylor_maccoll_cone_shock(cone_angle, shock_angle, gamma)

# --------------------------------------------------
# taylor maccoll solver (known mach and cone angle)
# --------------------------------------------------
def solve_taylor_maccoll_mach_cone(
    mach: float,
    cone_angle: float,
    gamma: float = 1.4,
    beta_guess: float | None = None,
) -> TaylorMaccollResult:
    """Solve Taylor-Maccoll for known Mach number and cone half-angle.

    Finds the shock angle and surface conditions for an attached conical shock.

    Args:
        mach:        Freestream Mach number (> 1).
        cone_angle:  Cone half-angle [deg].
        gamma:       Ratio of specific heats (default 1.4).
        beta_guess:  Optional shock angle guess [deg].  When provided, narrows the
                     brentq bracket to ±5 deg around the guess, reducing ODE evaluations.
                     Falls back to the full bracket if the guess is not within range.

    Returns:
        TaylorMaccollResult with shock_angle and surface conditions.

    Raises:
        ValueError: If no attached-shock solution exists.
    """
    # --------------------------------------------------
    # convert cone angle to radians
    # --------------------------------------------------
    theta_c = math.radians(cone_angle)

    # --------------------------------------------------
    # bracket shock angle
    # --------------------------------------------------

    # lower bound for beta:
    # physical minimum is the Mach angle mu (no shock below this)
    # using theta_c + 1 deg as a tighter lower bound when it exceeds mu
    # (shock angle is always > cone angle for an attached shock)
    mu = math.asin(1.0 / mach)
    beta_lo = max(math.radians(cone_angle) + math.radians(1.0), mu + math.radians(0.001))
    # higher bound: slightly less than 90 degrees to avoid singularity
    beta_hi  = math.pi / 2 * 0.95

    # narrow the bracket if a guess is provided
    if beta_guess is not None:

        # convert guess from degrees to radians and bracket plus and minus 5 degrees around it
        beta_guess = math.radians(beta_guess)

        # update beta_lo and beta_hi bracket based on the provided guess (+/- 5 degrees above/below initial guess)
        beta_lo_narrow = max(beta_lo, beta_guess - math.radians(5.0))
        beta_hi_narrow = min(beta_hi, beta_guess + math.radians(5.0))

        # use the narrow bracket only if it brackets the root (opposite residual signs)
        try:
            res_lo = _residual_beta(beta_lo_narrow, mach, theta_c, gamma)
            res_hi = _residual_beta(beta_hi_narrow, mach, theta_c, gamma)

            if res_lo * res_hi < 0:
                beta_lo = beta_lo_narrow
                beta_hi = beta_hi_narrow

        except (ValueError, RuntimeError):
            # output warning if the narrow bracket is not suitable for brentq -> fall back to full bracket
            warnings.warn(
                f"beta_guess={beta_guess:.2f} rad could not be used to narrow the bracket. "
                "falling back to full bracket.",
                UserWarning,
                stacklevel=3,
            )

    # --------------------------------------------------
    # check that a solution exists within the bounds of the shock angle
    # --------------------------------------------------

    try:
        theta_lo, _ = _integrate_taylor_maccoll(mach, beta_lo, gamma)
        theta_hi, _ = _integrate_taylor_maccoll(mach, beta_hi, gamma)
    except (ValueError, RuntimeError) as e:
        raise ValueError(
            f"No attached-shock solution found for cone_angle={cone_angle:.2f} deg at M={mach}"
        ) from e

    if theta_c < theta_lo or theta_c > theta_hi:
        raise ValueError(
            f"No attached-shock solution exists for cone_angle={cone_angle:.2f} deg at M={mach}"
        )

    # --------------------------------------------------
    # find shock angle by root-finding (brentq method)
    # --------------------------------------------------

    # find beta (shock angle) such that the cone angle condition is satisfied
    # note: first argument of _residual_beta is the shock angle beta (in radians)
    # other arguments are passed in through the args parameter of brentq
    beta = brentq(_residual_beta, beta_lo, beta_hi,
                  args=(mach, theta_c, gamma))

    # integrate one more time with the found shock angle to get the surface Mach number
    theta_c_computed, mach_cone = _integrate_taylor_maccoll(mach, beta, gamma)

    # compute relative error in cone angle
    epsilon_theta_c = abs(theta_c_computed - theta_c) / theta_c

    # check if the relative error in cone angle is within tolerance
    if epsilon_theta_c > 1e-6:
        delta_deg = abs(math.degrees(theta_c_computed) - cone_angle)
        raise ValueError(
            f"Cone angle convergence failed: target {cone_angle:.4f} deg, "
            f"computed {math.degrees(theta_c_computed):.4f} deg "
            f"(discrepancy {delta_deg:.2e} deg, relative error {epsilon_theta_c:.2e})."
        )
    else:
        # debug output for devs
        logging.getLogger("gasdyn").debug(
            "Cone angle convergence: target %.4f deg, computed %.4f deg "
            "(relative error %.2e)",
            cone_angle,
            math.degrees(theta_c_computed),
            epsilon_theta_c,
        )

    # compute Mach number behind the oblique shock
    M2 = mach_downstream_oblique(mach, beta, gamma)

    # compute surface pressure and temperature ratios
    pres_ratio = pres_ratio_oblique(mach, beta, gamma) * pres_ratio_isentropic(M2, mach_cone, gamma)
    temp_ratio = temp_ratio_oblique(mach, beta, gamma) * temp_ratio_isentropic(M2, mach_cone, gamma)

    return TaylorMaccollResult(
        mach=mach,
        cone_angle=cone_angle,
        shock_angle=math.degrees(beta),
        surface_pressure_ratio=pres_ratio,
        surface_temp_ratio=temp_ratio,
        gamma=gamma,
    )

# --------------------------------------------------
# taylor maccoll solver (known mach and shock angle)
# --------------------------------------------------
def solve_taylor_maccoll_mach_shock(
    mach: float,
    shock_angle: float,
    gamma: float = 1.4,
) -> TaylorMaccollResult:
    """Solve Taylor-Maccoll for known Mach number and shock angle.

    Finds the cone half-angle and surface conditions for the given shock.

    Args:
        mach:        Freestream Mach number (> 1).
        shock_angle: Shock wave angle [deg].
        gamma:       Ratio of specific heats (default 1.4).

    Returns:
        TaylorMaccollResult with cone_angle and surface conditions.

    Raises:
        ValueError: If shock angle is out of valid range.
    """
    beta = math.radians(shock_angle)

    theta_c, mach_cone = _integrate_taylor_maccoll(mach, beta, gamma)
    M2 = mach_downstream_oblique(mach, beta, gamma)

    # compute surface pressure and temperature ratios
    pres_ratio = pres_ratio_oblique(mach, beta, gamma) * pres_ratio_isentropic(M2, mach_cone, gamma)
    temp_ratio = temp_ratio_oblique(mach, beta, gamma) * temp_ratio_isentropic(M2, mach_cone, gamma)

    return TaylorMaccollResult(
        mach=mach,
        cone_angle=math.degrees(theta_c),
        shock_angle=shock_angle,
        surface_pressure_ratio=pres_ratio,
        surface_temp_ratio=temp_ratio,
        gamma=gamma,
    )

# --------------------------------------------------
# taylor maccoll solver (known cone angle and shock angle)
# --------------------------------------------------
def solve_taylor_maccoll_cone_shock(
    cone_angle: float,
    shock_angle: float,
    gamma: float = 1.4,
) -> TaylorMaccollResult:
    """Solve Taylor-Maccoll for known cone half-angle and shock angle.

    Finds the freestream Mach number consistent with the given geometry.

    Args:
        cone_angle:  Cone half-angle [deg].
        shock_angle: Shock wave angle [deg].
        gamma:       Ratio of specific heats (default 1.4).

    Returns:
        TaylorMaccollResult with mach and surface conditions.

    Raises:
        ValueError: If inputs are geometrically inconsistent.
    """
    theta_c = math.radians(cone_angle)
    beta    = math.radians(shock_angle)

    # find Mach number by root-finding (Brent's method)
    # lower bound: Mach at which shock_angle equals the Mach angle (M = 1/sin(beta))
    mach_lower = 1.0 / math.sin(beta) + 1e-6

    mach = brentq(_residual_mach, mach_lower, 50.0,
                  args=(theta_c, beta, gamma))
    _, mach_cone = _integrate_taylor_maccoll(mach, beta, gamma)
    M2 = mach_downstream_oblique(mach, beta, gamma)

    # compute surface pressure and temperature ratios
    pres_ratio = pres_ratio_oblique(mach, beta, gamma) * pres_ratio_isentropic(M2, mach_cone, gamma)
    temp_ratio = temp_ratio_oblique(mach, beta, gamma) * temp_ratio_isentropic(M2, mach_cone, gamma)

    return TaylorMaccollResult(
        mach=mach,
        cone_angle=cone_angle,
        shock_angle=shock_angle,
        surface_pressure_ratio=pres_ratio,
        surface_temp_ratio=temp_ratio,
        gamma=gamma,
    )

# --------------------------------------------------
# residual function for brentq root-finding when beta is unknown
# --------------------------------------------------
def _residual_beta(
    beta_guess: float,
    mach: float,
    theta_c: float,
    gamma: float,
) -> float:
    """Residual for brentq when solving for shock angle beta.

    Returns zero when the ODE integration with the given beta_guess produces
    the target cone angle theta_c.

    Args:
        beta_guess: Trial shock wave angle [rad].
        mach:       Freestream Mach number.
        theta_c:    Target cone half-angle [rad].
        gamma:      Ratio of specific heats.
    """
    theta_found, _ = _integrate_taylor_maccoll(mach, beta_guess, gamma)
    return theta_found - theta_c

# --------------------------------------------------
# residual function for brentq root-finding when mach is unknown
# --------------------------------------------------
def _residual_mach(
    mach_guess: float,
    theta_c: float,
    beta: float,
    gamma: float,
) -> float:
    """Residual for brentq when solving for freestream Mach number.

    Returns zero when the ODE integration with the given mach_guess produces
    the target cone angle theta_c.

    Args:
        mach_guess: Trial freestream Mach number.
        theta_c:    Target cone half-angle [rad].
        beta:       Known shock wave angle [rad].
        gamma:      Ratio of specific heats.
    """
    try:
        theta_found, _ = _integrate_taylor_maccoll(mach_guess, beta, gamma)
        return theta_found - theta_c
    except (ValueError, RuntimeError):
        return 1e10

# --------------------------------------------------
# initial condition functions for the Taylor-Maccoll ODE
# --------------------------------------------------
def _shock_initial_conditions(
    mach_inf: float, beta: float, gamma: float
) -> tuple[float, float]:
    """Compute non-dimensional velocity components just behind the conical shock.

    Uses oblique shock relations to get M2, then converts to the non-dimensional
    radial and polar velocity components (Vr0, Vtheta0) that serve as initial
    conditions for the Taylor-Maccoll ODE.

    Args:
        mach_inf: Freestream Mach number.
        beta:     Shock wave angle [rad].
        gamma:    Ratio of specific heats.

    Returns:
        Vr0:     Non-dimensional radial velocity at the shock [-]
        Vtheta0: Non-dimensional polar velocity at the shock [-]  (always < 0)
    """
    # post-shock Mach number and flow deflection angle
    M2    = mach_downstream_oblique(mach_inf, beta, gamma)
    delta = theta_beta_m(mach_inf, beta, gamma)

    # non-dimensional speed: V0 = 1 / sqrt(1 + 2/((gamma-1)*M2^2))
    V0 = (1.0 + 2.0 / ((gamma - 1) * M2**2)) ** (-0.5)

    # velocity components at the shock (in conical frame)
    Vr0      =  V0 * math.cos(beta - delta)
    Vtheta0  = -V0 * math.sin(beta - delta)   # negative: flow deflects toward axis

    return Vr0, Vtheta0

# --------------------------------------------------
# integrate the Taylor-Maccoll ODE from the shock to the cone surface
# --------------------------------------------------
def _integrate_taylor_maccoll(
    mach_inf: float, beta: float, gamma: float
) -> tuple[float, float]:
    """Integrate the Taylor-Maccoll ODE from the shock to the cone surface.

    Computes the initial conditions from the oblique shock relations at beta,
    then integrates inward until Vtheta = 0 (the cone surface condition).

    Args:
        mach_inf: Freestream Mach number.
        beta:     Shock wave angle [rad] — starting angle of the integration.
        gamma:    Ratio of specific heats.

    Returns:
        theta_cone: Cone half-angle [rad]
        mach_cone:  Mach number at the cone surface [-]
    """
    # compute initial conditions at the shock from oblique shock relations
    Vr0, Vtheta0 = _shock_initial_conditions(mach_inf, beta, gamma)

    # define ODE system
    def dydtheta(theta, y):

        # unpack velocity components (in state vector y)
        Vr, Vtheta = y

        # precompute some common terms

        # gamma -1
        gm1 = (gamma - 1)

        # velocity squared: V^2 = Vr^2 + Vtheta^2
        V2 = Vr**2 + Vtheta**2

        # (gamma-1)/2 * (1 - V^2) appears in both numerator and denominator
        c1 = gm1 / 2 * (1 - V2)

        # compute dVr/dtheta from Taylor-Maccoll equations
        # dVr/dtheta = Vtheta
        dVr_dtheta = Vtheta

        # compute dVtheta/dtheta from Taylor-Maccoll equations
        # dVtheta/dtheta = (Vtheta^2 * Vr - (gamma-1)/2 * (1 - V^2) * (2 * Vr + Vtheta / tan(theta))) / ((gamma-1)/2 * (1 - V^2) - Vtheta^2)

        # compute numerator: Vtheta^2 * Vr - (gamma-1)/2 * (1 - V^2) * (2 * Vr + Vtheta / tan(theta))
        # note: c1 = (gamma-1)/2 * (1 - V^2)
        # numerator = Vtheta^2 * Vr - c1 * (2 * Vr + Vtheta / tan(theta))
        numerator = (
            Vtheta**2 * Vr
            - c1 * (2 * Vr + Vtheta / math.tan(theta))
        )

        # compute denominator: (gamma-1)/2 * (1 - V^2) - Vtheta^2
        # note: c1 = (gamma-1)/2 * (1 - V^2)
        # denominator = c1 - Vtheta^2
        denominator = c1 - Vtheta**2

        # avoid division by zero
        if abs(denominator) < 1e-14:
            return [0.0, 0.0]

        # compute dVtheta/dtheta using the precomputed numerator and denominator
        dVtheta_dtheta = numerator / denominator

        # return derivative of state vector y = [Vr, Vtheta]
        return [dVr_dtheta, dVtheta_dtheta]

    # event: stop when Vtheta crosses zero (cone surface)
    def cone_surface(theta, y):
        # Vtheta = 0
        return y[1]

    cone_surface.terminal = True
    # increasing
    cone_surface.direction = 1

    # integrate from shock toward axis (negative direction)

    # integration of the Taylor-Maccoll ODE from the shock to the cone surface
    # not: integration end at 0.001 to avoid singularity at theta=0
    theta_span = [beta, 0.001]

    # set initial conditions at the shock
    y0 = [Vr0, Vtheta0]

    # use solve_ivp to integrate the Taylor-Maccoll ODE
    sol = solve_ivp(
        dydtheta,
        theta_span,
        y0,
        method="RK45",
        events=cone_surface,
        dense_output=True,
        rtol=1e-9,
        atol=1e-12,
    )

    # check if the integration was successful
    if not sol.success:
        raise RuntimeError("Taylor-Maccoll integration failed")

    # check if cone surface was reached
    if len(sol.t_events[0]) > 0:
        # event triggered: cone surface reached

        # get the values at the cone surface event
        theta_cone   = sol.t_events[0][0]
        Vr_cone      = sol.y_events[0][0][0]
        Vtheta_cone  = sol.y_events[0][0][1]
    else:
        # Vtheta never crossed zero —> no cone surface found within the integration range
        raise RuntimeError(
            "Taylor-Maccoll integration did not reach the cone surface "
            f"(Vtheta never crossed zero between beta={math.degrees(beta):.2f} deg "
            "and theta=0.001 rad)"
        )

    # compute cone surface Mach number
    V_cone_sq = Vr_cone**2 + Vtheta_cone**2
    mach_cone = ((1.0 / V_cone_sq - 1) * (gamma - 1) / 2) ** (-0.5)

    # return the cone surface angle and Mach number
    return theta_cone, mach_cone
