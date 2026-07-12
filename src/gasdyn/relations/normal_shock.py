"""Normal shock relations."""

from __future__ import annotations

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
        "mach_1":   "-",
        "mach_2":   "-",
        "p_ratio":  "-",
        "t_ratio":  "-",
        "rho_ratio": "-",
        "p0_ratio": "-",
        "gamma":    "-",
    }


def solve_normal_shock(
    mach_1: float = None,
    p_ratio: float = None,
    gamma: float = 1.4,
) -> NormalShockResult:
    """
    Solve normal shock relations for a perfect gas.

    Accepts exactly ONE of: mach_1 or p_ratio, and solves for all others.

    Ratios are downstream/upstream: p2/p1, T2/T1, rho2/rho1, p02/p01.

    Args:
        mach_1: Upstream Mach number (M1).
        p_ratio: Static pressure ratio across shock (p2/p1).
        gamma: Ratio of specific heats (default 1.4 for air).

    Returns:
        GasdynResult containing mach_1, mach_2, p_ratio, t_ratio, rho_ratio,
        p0_ratio, and gamma.

    Raises:
        ValueError: If zero or more than one input is provided, or if inputs are invalid.

    Examples:
        >>> result = solve_normal_shock(mach_1=2.0)
        >>> result.mach_2
        0.5774...
        >>> result.p_ratio
        4.5
    """
    # validate inputs
    inputs = [mach_1, p_ratio]
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

    elif p_ratio is not None:
        # solve from p_ratio: p_ratio = 1 + (2*gamma/(gamma+1)) * (M1^2 - 1)
        # => M1 = sqrt(1 + (p_ratio - 1) * (gamma+1) / (2*gamma))
        if p_ratio <= 1:
            raise ValueError(f"p_ratio must be > 1, got {p_ratio}")
        M1 = math.sqrt(1.0 + (p_ratio - 1.0) * (gamma + 1) / (2.0 * gamma))

    else:
        raise ValueError("No valid input provided")

    # --------------------------------------------------
    # compute all quantities from mach_1
    # --------------------------------------------------

    # pressure ratio
    p_rat = 1.0 + (2.0 * gamma / (gamma + 1)) * (M1**2 - 1.0)

    # density ratio
    rho_rat = ((gamma + 1) * M1**2) / ((gamma - 1) * M1**2 + 2.0)

    # temperature ratio
    t_rat = p_rat / rho_rat

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
        p_ratio=p_rat,
        t_ratio=t_rat,
        rho_ratio=rho_rat,
        p0_ratio=p0_rat,
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


def temp_ratio_normal(mn1: float, gamma: float) -> float:
    """Static temperature ratio T2/T1 across a normal shock.

    Args:
        mn1:   Upstream normal Mach number.
        gamma: Ratio of specific heats.

    Returns:
        T2/T1 [-]
    """
    p_rat   = pres_ratio_normal(mn1, gamma)
    rho_rat = ((gamma + 1) * mn1**2) / ((gamma - 1) * mn1**2 + 2.0)
    return p_rat / rho_rat


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
