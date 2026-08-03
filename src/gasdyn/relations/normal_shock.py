"""Normal shock relations."""

from __future__ import annotations

import dataclasses
import json
import math
from dataclasses import dataclass
from typing import ClassVar


# --------------------------------------------------
# result dataclass
# --------------------------------------------------
@dataclass
class NormalShockResult:
    """Result of solve_normal_shock."""

    # upstream Mach number [-]
    mach_1: float
    # downstream Mach number [-]
    mach_2: float
    # static pressure ratio p2/p1 [-]
    pres_ratio: float
    # static temperature ratio T2/T1 [-]
    temp_ratio: float
    # density ratio rho2/rho1 [-]
    dens_ratio: float
    # total pressure ratio p02/p01 [-]
    pres_stag_ratio: float
    # ratio of specific heats [-]
    gamma: float

    # units for each field (used by CLI formatter)
    _UNITS: ClassVar[dict[str, str]] = {
        "mach_1":          "-",
        "mach_2":          "-",
        "pres_ratio":      "-",
        "temp_ratio":      "-",
        "dens_ratio":      "-",
        "pres_stag_ratio": "-",
        "gamma":           "-",
    }


def format_normal_shock_result(result: NormalShockResult, as_json: bool) -> str:
    """Format normal-shock result for CLI output."""
    if as_json:
        return _to_json_normal_shock(result)
    return _to_str_normal_shock(result)


def _to_str_normal_shock(result: NormalShockResult) -> str:
    """Format normal-shock result as a human-readable table."""
    units = getattr(type(result), "_UNITS", {})
    fields = dataclasses.fields(result)

    # determine column width from the longest field name
    col_width = max(len(f.name) for f in fields)

    lines = ["=" * 60, "Normal Shock Results", "=" * 60]
    for f in fields:
        val = getattr(result, f.name)
        unit = units.get(f.name, "-")
        lines.append(f"{f.name:<{col_width}}  :  {val:>14g}  [{unit}]")
    lines.append("=" * 60)

    return "\n".join(lines)


def _to_json_normal_shock(result: NormalShockResult) -> str:
    """Serialise normal-shock result to JSON with [value, unit] pairs."""
    units = getattr(type(result), "_UNITS", {})
    values = dataclasses.asdict(result)
    payload = {key: [value, units.get(key, "-")] for key, value in values.items()}
    return json.dumps(payload, indent=2)


def solve_normal_shock(
    mach_1: float = None,
    pres_ratio: float = None,
    gamma: float = 1.4,
) -> NormalShockResult:
    """
    Solve normal shock relations for a perfect gas.

    Accepts exactly ONE of: mach_1 or pres_ratio, and solves for all others.

    Ratios are downstream/upstream: p2/p1, T2/T1, rho2/rho1, p02/p01.

    Args:
        mach_1: Upstream Mach number (M1).
        pres_ratio: Static pressure ratio across shock (p2/p1).
        gamma: Ratio of specific heats (default 1.4 for air).

    Returns:
        NormalShockResult containing mach_1, mach_2, pres_ratio, temp_ratio,
        dens_ratio, pres_stag_ratio, and gamma.

    Raises:
        ValueError: If zero or more than one input is provided, or if inputs are invalid.

    Examples:
        >>> result = solve_normal_shock(mach_1=2.0)
        >>> result.mach_2
        0.5774...
        >>> result.pres_ratio
        4.5
    """
    # validate inputs
    inputs = [mach_1, pres_ratio]
    provided = sum(x is not None for x in inputs)

    if provided == 0:
        raise ValueError("Must provide exactly one input")
    if provided > 1:
        raise ValueError("Must provide exactly one input, got multiple")

    # validate gamma
    if gamma <= 1:
        raise ValueError(f"gamma must be > 1, got {gamma}")

    # --------------------------------------------------
    # solve for mach_1
    # --------------------------------------------------

    if mach_1 is not None:
        # validate mach_1
        if mach_1 <= 1:
            raise ValueError(f"mach_1 must be > 1, got {mach_1}")
        M1 = mach_1

    elif pres_ratio is not None:
        # solve from p_ratio: p_ratio = 1 + (2*gamma/(gamma+1)) * (M1^2 - 1)
        # => M1 = sqrt(1 + (p_ratio - 1) * (gamma+1) / (2*gamma))
        if pres_ratio <= 1:
            raise ValueError(f"pres_ratio must be > 1, got {pres_ratio}")
        M1 = math.sqrt(1.0 + (pres_ratio - 1.0) * (gamma + 1) / (2.0 * gamma))

    else:
        raise ValueError("No valid input provided")

    # --------------------------------------------------
    # compute all quantities from mach_1
    # --------------------------------------------------

    # pressure ratio
    p_rat = 1.0 + (2.0 * gamma / (gamma + 1)) * (M1**2 - 1.0)

    # density ratio
    dens_rat = dens_ratio_normal(M1, gamma)

    # temperature ratio
    temp_rat = p_rat / dens_rat

    # downstream mach number
    M2_squared = (1.0 + 0.5 * (gamma - 1) * M1**2) / (
        gamma * M1**2 - 0.5 * (gamma - 1)
    )
    M2 = math.sqrt(M2_squared)

    # stagnation pressure ratio
    # p0_ratio = p02/p01 = (p2/p1) * (p02/p2) / (p01/p1)
    # where p0/p = (1 + (gamma-1)/2 * M^2)^(gamma/(gamma-1))
    p01_p1 = (1.0 + (gamma - 1) / 2.0 * M1**2) ** (gamma / (gamma - 1))
    p02_p2 = (1.0 + (gamma - 1) / 2.0 * M2**2) ** (gamma / (gamma - 1))
    p0_rat = p_rat * p02_p2 / p01_p1

    # --------------------------------------------------
    # return result
    # --------------------------------------------------

    return NormalShockResult(
        mach_1=M1,
        mach_2=M2,
        pres_ratio=p_rat,
        temp_ratio=temp_rat,
        dens_ratio=dens_rat,
        pres_stag_ratio=p0_rat,
        gamma=gamma,
    )


# --------------------------------------------------
# scalar ratio helpers (reusable by other modules)
# --------------------------------------------------
def pres_ratio_normal(mn1: float, gamma: float) -> float:
    """Static pressure ratio p2/p1 across a normal shock.

    Args:
        mn1:   Upstream normal Mach number.
        gamma: Ratio of specific heats.

    Returns:
        p2/p1 [-]
    """
    return 1.0 + (2.0 * gamma / (gamma + 1)) * (mn1**2 - 1.0)


def dens_ratio_normal(mn1: float, gamma: float) -> float:
    """Static density ratio rho2/rho1 across a normal shock.

    Args:
        mn1: Upstream normal Mach number.
        gamma: Ratio of specific heats.

    Returns:
        rho2/rho1 [-]
    """
    numerator = (gamma + 1.0) * mn1**2
    denominator = (gamma - 1.0) * mn1**2 + 2.0
    dens_ratio = numerator / denominator

    return dens_ratio


def temp_ratio_normal(mn1: float, gamma: float) -> float:
    """Static temperature ratio T2/T1 across a normal shock.

    Args:
        mn1:   Upstream normal Mach number.
        gamma: Ratio of specific heats.

    Returns:
        T2/T1 [-]
    """
    p_rat = pres_ratio_normal(mn1, gamma)
    dens_rat = dens_ratio_normal(mn1, gamma)
    return p_rat / dens_rat


def mach_downstream_normal(mn1: float, gamma: float) -> float:
    """Downstream normal Mach number Mn2 across a normal shock.

    Args:
        mn1:   Upstream normal Mach number.
        gamma: Ratio of specific heats.

    Returns:
        Mn2 [-]
    """
    mn2_sq = (mn1**2 + 2.0 / (gamma - 1)) / (2.0 * gamma / (gamma - 1) * mn1**2 - 1.0)
    return math.sqrt(mn2_sq)
