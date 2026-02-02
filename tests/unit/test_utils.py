"""
Unit tests for utility functions.
"""

import pytest
import numpy as np
from nanoparticle_simulator.utils.constants import (
    AVOGADRO,
    BOLTZMANN,
    GAS_CONSTANT,
    PI,
)
from nanoparticle_simulator.utils.units import (
    convert_units,
    convert_temperature,
    format_scientific,
)


class TestConstants:
    """Tests for physical constants."""

    def test_avogadro(self):
        """Test Avogadro's number."""
        assert AVOGADRO == pytest.approx(6.02214076e23, rel=1e-8)

    def test_boltzmann(self):
        """Test Boltzmann constant."""
        assert BOLTZMANN == pytest.approx(1.380649e-23, rel=1e-8)

    def test_gas_constant(self):
        """Test gas constant equals NA * kB."""
        assert GAS_CONSTANT == pytest.approx(AVOGADRO * BOLTZMANN, rel=1e-8)
        assert GAS_CONSTANT == pytest.approx(8.314, rel=1e-3)

    def test_pi(self):
        """Test pi value."""
        assert PI == pytest.approx(np.pi)


class TestUnitConversion:
    """Tests for unit conversion functions."""

    def test_length_conversion(self):
        """Test length unit conversions."""
        # nm to m
        assert convert_units(1.0, "nm", "m", "length") == pytest.approx(1e-9)

        # m to nm
        assert convert_units(1e-9, "m", "nm", "length") == pytest.approx(1.0)

        # cm to m
        assert convert_units(100.0, "cm", "m", "length") == pytest.approx(1.0)

    def test_time_conversion(self):
        """Test time unit conversions."""
        # ms to s
        assert convert_units(1000.0, "ms", "s", "time") == pytest.approx(1.0)

        # s to us
        assert convert_units(1.0, "s", "us", "time") == pytest.approx(1e6)

    def test_pressure_conversion(self):
        """Test pressure unit conversions."""
        # atm to Pa
        assert convert_units(1.0, "atm", "Pa", "pressure") == pytest.approx(101325.0)

        # Pa to bar
        assert convert_units(100000.0, "Pa", "bar", "pressure") == pytest.approx(1.0)

    def test_temperature_conversion(self):
        """Test temperature conversions."""
        # Celsius to Kelvin
        assert convert_temperature(0.0, "C", "K") == pytest.approx(273.15)
        assert convert_temperature(100.0, "C", "K") == pytest.approx(373.15)

        # Kelvin to Celsius
        assert convert_temperature(273.15, "K", "C") == pytest.approx(0.0)

        # Fahrenheit to Kelvin
        assert convert_temperature(32.0, "F", "K") == pytest.approx(273.15, rel=1e-3)

    def test_invalid_quantity(self):
        """Test error for invalid quantity type."""
        with pytest.raises(ValueError):
            convert_units(1.0, "m", "s", "invalid_quantity")

    def test_invalid_unit(self):
        """Test error for invalid unit."""
        with pytest.raises(ValueError):
            convert_units(1.0, "invalid_unit", "m", "length")

    def test_array_conversion(self):
        """Test conversion of numpy arrays."""
        values = np.array([1.0, 2.0, 3.0])
        result = convert_units(values, "nm", "m", "length")

        expected = np.array([1e-9, 2e-9, 3e-9])
        np.testing.assert_allclose(result, expected)


class TestFormatting:
    """Tests for formatting functions."""

    def test_format_scientific(self):
        """Test scientific notation formatting."""
        assert format_scientific(1.23e-6, precision=3) == "1.230e-06"
        assert format_scientific(1.0e10, precision=2) == "1.00e+10"

    def test_format_zero(self):
        """Test formatting zero."""
        assert format_scientific(0.0) == "0"
