"""Unit conversion utilities."""

# --------------------------------------------------
# load necessary modules
# --------------------------------------------------
import math


# --------------------------------------------------
# unit conversion functions
# --------------------------------------------------
def to_si(value: float, unit: str) -> float:
    """Convert a value from the given unit to SI.

    Args:
        value: Numeric value to convert.
        unit:  Source unit string (e.g. "deg", "psi", "ft").

    Returns:
        Value in SI units.

    Raises:
        ValueError: If the unit is not recognised.

    Examples:
        >>> to_si(45.0, "deg")
        0.7853981633974483
        >>> to_si(14.7, "psi")
        101352.93...
    """
    # convert angle units
    if unit in ["deg", "degree", "degrees"]:
        return math.radians(value)
    elif unit in ["rad", "radian", "radians"]:
        return float(value)

    # convert pressure units
    elif unit == "Pa":
        return float(value)
    elif unit == "psi":
        return value * 6894.757293168361
    elif unit == "atm":
        return value * 101325.0
    elif unit == "bar":
        return value * 100000.0

    # convert temperature units
    elif unit == "K":
        return float(value)
    elif unit == "C":
        return value + 273.15
    elif unit == "F":
        return (value - 32.0) * 5.0 / 9.0 + 273.15

    # convert length units
    elif unit == "m":
        return float(value)
    elif unit == "ft":
        return value * 0.3048
    elif unit == "km":
        return value * 1000.0

    else:
        raise ValueError(f"Unsupported unit: '{unit}'")
