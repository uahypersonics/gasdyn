"""Tests for unit conversion utilities."""

import math

import pytest

from gasdyn.core.units import to_si

# --------------------------------------------------
# angle conversions
# --------------------------------------------------


def test_degrees_to_radians():
    """Test degree to radian conversion."""
    assert abs(to_si(45.0, "deg") - math.pi / 4) < 1e-10
    assert abs(to_si(90.0, "deg") - math.pi / 2) < 1e-10
    assert abs(to_si(180.0, "deg") - math.pi) < 1e-10
    assert abs(to_si(360.0, "deg") - 2 * math.pi) < 1e-10
    assert abs(to_si(90.0, "degree") - math.pi / 2) < 1e-10
    assert abs(to_si(180.0, "degrees") - math.pi) < 1e-10


def test_radians_passthrough():
    """Test radian values are passed through unchanged."""
    assert to_si(1.0, "rad") == 1.0
    assert to_si(math.pi, "radian") == math.pi
    assert to_si(2 * math.pi, "radians") == 2 * math.pi


# --------------------------------------------------
# pressure conversions
# --------------------------------------------------


def test_pressure_pa():
    """Test Pascal values are passed through unchanged."""
    assert to_si(101325.0, "Pa") == 101325.0
    assert to_si(1000.0, "Pa") == 1000.0


def test_pressure_psi():
    """Test psi to Pascal conversion."""
    result = to_si(1.0, "psi")
    assert abs(result - 6894.757293168361) < 1e-6
    result = to_si(14.7, "psi")
    assert abs(result - 101352.93) < 1.0


def test_pressure_atm():
    """Test atm to Pascal conversion."""
    assert to_si(1.0, "atm") == 101325.0
    assert to_si(2.0, "atm") == 202650.0


def test_pressure_bar():
    """Test bar to Pascal conversion."""
    assert to_si(1.0, "bar") == 100000.0
    assert to_si(1.5, "bar") == 150000.0


# --------------------------------------------------
# temperature conversions
# --------------------------------------------------


def test_temperature_kelvin():
    """Test Kelvin values are passed through unchanged."""
    assert to_si(273.15, "K") == 273.15
    assert to_si(300.0, "K") == 300.0


def test_temperature_celsius():
    """Test Celsius to Kelvin conversion."""
    assert abs(to_si(0.0, "C") - 273.15) < 1e-10
    assert abs(to_si(100.0, "C") - 373.15) < 1e-10
    assert abs(to_si(-40.0, "C") - 233.15) < 1e-10


def test_temperature_fahrenheit():
    """Test Fahrenheit to Kelvin conversion."""
    assert abs(to_si(32.0, "F") - 273.15) < 1e-10
    assert abs(to_si(212.0, "F") - 373.15) < 1e-10
    assert abs(to_si(-40.0, "F") - 233.15) < 1e-10


# --------------------------------------------------
# length conversions
# --------------------------------------------------


def test_length_meters():
    """Test meter values are passed through unchanged."""
    assert to_si(100.0, "m") == 100.0
    assert to_si(1.5, "m") == 1.5


def test_length_feet():
    """Test feet to meter conversion."""
    assert abs(to_si(1.0, "ft") - 0.3048) < 1e-10
    assert abs(to_si(10.0, "ft") - 3.048) < 1e-10


def test_length_kilometers():
    """Test kilometer to meter conversion."""
    assert to_si(1.0, "km") == 1000.0
    assert to_si(2.5, "km") == 2500.0


# --------------------------------------------------
# error cases
# --------------------------------------------------


def test_invalid_unit():
    """Test that invalid units raise ValueError."""
    with pytest.raises(ValueError, match="Unsupported unit"):
        to_si(1.0, "invalid")

    with pytest.raises(ValueError, match="Unsupported unit"):
        to_si(1.0, "parsec")

