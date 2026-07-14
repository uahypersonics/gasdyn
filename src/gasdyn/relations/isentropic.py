"""Isentropic flow relations."""

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
class IsentropicResult:
    """Result of solve_isentropic."""

    # freestream / stagnation ratios

    # Mach number [-]
    mach: float
    # static-to-total pressure ratio p/p0 [-]
    p_ratio: float
    # static-to-total temperature ratio T/T0 [-]
    t_ratio: float
    # static-to-total density ratio rho/rho0 [-]
    rho_ratio: float
    # stream-tube area ratio A/A* [-]
    area_ratio: float
    # ratio of specific heats [-]
    gamma: float

    # units for each field (used by CLI formatter)
    _UNITS: ClassVar[dict[str, str]] = {
        "mach":       "-",
        "p_ratio":    "-",
        "t_ratio":    "-",
        "rho_ratio":  "-",
        "area_ratio": "-",
        "gamma":      "-",
    }


def format_isentropic_result(result: IsentropicResult, as_json: bool) -> str:
    """Format isentropic result for CLI output."""
    if as_json:
        return _to_json_isentropic(result)
    return _to_str_isentropic(result)


def _to_str_isentropic(result: IsentropicResult) -> str:
    """Format isentropic result as a human-readable table."""
    units = getattr(type(result), "_UNITS", {})
    fields = dataclasses.fields(result)

    # determine column width from the longest field name
    col_width = max(len(f.name) for f in fields)

    lines = ["=" * 60, "Isentropic Results", "=" * 60]
    for f in fields:
        val = getattr(result, f.name)
        unit = units.get(f.name, "-")
        lines.append(f"{f.name:<{col_width}}  :  {val:>14g}  [{unit}]")
    lines.append("=" * 60)

    return "\n".join(lines)


def _to_json_isentropic(result: IsentropicResult) -> str:
    """Serialise isentropic result to JSON with [value, unit] pairs."""
    units = getattr(type(result), "_UNITS", {})
    values = dataclasses.asdict(result)
    payload = {key: [value, units.get(key, "-")] for key, value in values.items()}
    return json.dumps(payload, indent=2)


def solve_isentropic(
    mach: float = None,
    p_ratio: float = None,
    t_ratio: float = None,
    rho_ratio: float = None,
    area_ratio: float = None,
    gamma: float = 1.4,
    branch: str = "supersonic",
) -> IsentropicResult:
    """
    Solve isentropic flow relations for a perfect gas.

    Accepts exactly ONE of the following inputs and solves for all others:
    mach, p_ratio, t_ratio, rho_ratio, or area_ratio.

    Ratios are static-to-stagnation: p/p0, T/T0, rho/rho0.
    Area ratio is A/A* (area over sonic throat area).

    Args:
        mach: Mach number (M).
        p_ratio: Static-to-stagnation pressure ratio (p/p0).
        t_ratio: Static-to-stagnation temperature ratio (T/T0).
        rho_ratio: Static-to-stagnation density ratio (rho/rho0).
        area_ratio: Area ratio (A/A*).
        gamma: Ratio of specific heats (default 1.4 for air).
        branch: For area_ratio input, "subsonic" or "supersonic" (default "supersonic").

    Returns:
        GasdynResult containing mach, p_ratio, t_ratio, rho_ratio, area_ratio, and gamma.

    Raises:
        ValueError: If zero or more than one input is provided, or if inputs are invalid.

    Examples:
        >>> result = solve_isentropic(mach=2.0)
        >>> result.p_ratio
        0.12780...
        >>> result = solve_isentropic(area_ratio=1.6875, branch="supersonic")
        >>> result.mach
        2.0...
    """
    # validate inputs
    inputs = [mach, p_ratio, t_ratio, rho_ratio, area_ratio]
    provided = sum(x is not None for x in inputs)

    if provided == 0:
        raise ValueError("Must provide exactly one input")
    if provided > 1:
        raise ValueError("Must provide exactly one input, got multiple")

    # validate gamma
    if gamma <= 1:
        raise ValueError(f"gamma must be > 1, got {gamma}")

    # validate branch
    if branch not in ["subsonic", "supersonic"]:
        raise ValueError(f"branch must be 'subsonic' or 'supersonic', got '{branch}'")

    # --------------------------------------------------
    # solve for mach number
    # --------------------------------------------------

    if mach is not None:
        # validate mach
        if mach <= 0:
            raise ValueError(f"Mach number must be > 0, got {mach}")
        M = mach

    elif t_ratio is not None:
        # solve from t_ratio: t_ratio = 1 / (1 + (gamma-1)/2 * M^2)
        # => M = sqrt(2/(gamma-1) * (1/t_ratio - 1))
        if t_ratio <= 0 or t_ratio > 1:
            raise ValueError(f"t_ratio must be in (0, 1], got {t_ratio}")
        M = math.sqrt(2.0 / (gamma - 1) * (1.0 / t_ratio - 1.0))

    elif p_ratio is not None:
        # solve from p_ratio: p_ratio = (1 + (gamma-1)/2 * M^2)^(-gamma/(gamma-1))
        # => M = sqrt(2/(gamma-1) * (p_ratio^(-(gamma-1)/gamma) - 1))
        if p_ratio <= 0 or p_ratio > 1:
            raise ValueError(f"p_ratio must be in (0, 1], got {p_ratio}")
        exponent = -(gamma - 1) / gamma
        M = math.sqrt(2.0 / (gamma - 1) * (p_ratio**exponent - 1.0))

    elif rho_ratio is not None:
        # solve from rho_ratio: rho_ratio = (1 + (gamma-1)/2 * M^2)^(-1/(gamma-1))
        # => M = sqrt(2/(gamma-1) * (rho_ratio^(-(gamma-1)) - 1))
        if rho_ratio <= 0 or rho_ratio > 1:
            raise ValueError(f"rho_ratio must be in (0, 1], got {rho_ratio}")
        exponent = -(gamma - 1)
        M = math.sqrt(2.0 / (gamma - 1) * (rho_ratio**exponent - 1.0))

    elif area_ratio is not None:
        # solve from area_ratio using root finding
        if area_ratio < 1:
            raise ValueError(f"area_ratio must be >= 1, got {area_ratio}")

        # define residual function
        def residual(M_guess):
            return _compute_area_ratio(M_guess, gamma) - area_ratio

        # find root in appropriate branch
        if branch == "subsonic":
            # subsonic: 0 < M < 1
            try:
                M = brentq(residual, 1e-6, 1.0 - 1e-6)
            except ValueError as e:
                raise ValueError(
                    f"No subsonic solution found for area_ratio={area_ratio}"
                ) from e
        else:
            # supersonic: M > 1
            # upper bound: start with reasonable guess and extend if needed
            M_upper = 10.0
            while residual(M_upper) < 0:
                M_upper *= 2
                if M_upper > 1e6:
                    raise ValueError(
                        f"No supersonic solution found for area_ratio={area_ratio}"
                    )
            try:
                M = brentq(residual, 1.0 + 1e-6, M_upper)
            except ValueError as e:
                raise ValueError(
                    f"No supersonic solution found for area_ratio={area_ratio}"
                ) from e
    else:
        raise ValueError("No valid input provided")

    # --------------------------------------------------
    # compute all ratios from mach number
    # --------------------------------------------------

    t_rat = _compute_t_ratio(M, gamma)
    p_rat = _compute_p_ratio(M, gamma)
    rho_rat = _compute_rho_ratio(M, gamma)
    a_rat = _compute_area_ratio(M, gamma)

    # --------------------------------------------------
    # return result
    # --------------------------------------------------

    return IsentropicResult(
        mach=M,
        p_ratio=p_rat,
        t_ratio=t_rat,
        rho_ratio=rho_rat,
        area_ratio=a_rat,
        gamma=gamma,
    )


# --------------------------------------------------
# helper functions
# --------------------------------------------------


def _compute_t_ratio(M: float, gamma: float) -> float:
    """Compute T/T0 from Mach number."""
    return 1.0 / (1.0 + (gamma - 1) / 2.0 * M**2)


def _compute_p_ratio(M: float, gamma: float) -> float:
    """Compute p/p0 from Mach number."""
    t_rat = _compute_t_ratio(M, gamma)
    exponent = gamma / (gamma - 1)
    return t_rat**exponent


def _compute_rho_ratio(M: float, gamma: float) -> float:
    """Compute rho/rho0 from Mach number."""
    t_rat = _compute_t_ratio(M, gamma)
    exponent = 1.0 / (gamma - 1)
    return t_rat**exponent


def _compute_area_ratio(M: float, gamma: float) -> float:
    """Compute A/A* from Mach number."""
    term1 = 1.0 / M
    term2 = (2.0 / (gamma + 1)) * (1.0 + (gamma - 1) / 2.0 * M**2)
    exponent = (gamma + 1) / (2.0 * (gamma - 1))
    return term1 * term2**exponent


# --------------------------------------------------
# scalar ratio helpers (reusable by other modules)
# --------------------------------------------------
def pres_ratio_isentropic(mach_1: float, mach_2: float, gamma: float) -> float:
    """Isentropic static pressure ratio p2/p1 between two Mach numbers.

    Uses the same stagnation pressure, so the ratio is:
        p2/p1 = (1 + (gamma-1)/2 * M2^2)^(-gamma/(gamma-1))
              / (1 + (gamma-1)/2 * M1^2)^(-gamma/(gamma-1))

    Args:
        mach_1: Upstream Mach number.
        mach_2: Downstream Mach number.
        gamma:  Ratio of specific heats.

    Returns:
        p2/p1 [-]
    """
    p1_p0 = _compute_p_ratio(mach_1, gamma)
    p2_p0 = _compute_p_ratio(mach_2, gamma)
    return p2_p0 / p1_p0


def temp_ratio_isentropic(mach_1: float, mach_2: float, gamma: float) -> float:
    """Isentropic static temperature ratio T2/T1 between two Mach numbers.

    Args:
        mach_1: Upstream Mach number.
        mach_2: Downstream Mach number.
        gamma:  Ratio of specific heats.

    Returns:
        T2/T1 [-]
    """
    t1_t0 = _compute_t_ratio(mach_1, gamma)
    t2_t0 = _compute_t_ratio(mach_2, gamma)
    return t2_t0 / t1_t0
