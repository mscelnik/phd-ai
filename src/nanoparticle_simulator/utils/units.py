"""
Unit conversion utilities.

Provides functions for converting between different unit systems.
"""

from typing import Union
import numpy as np
from numpy.typing import NDArray


# Unit conversion factors (multiply to convert TO SI)
UNIT_FACTORS: dict[str, dict[str, float]] = {
    # Length
    "length": {
        "m": 1.0,
        "cm": 1e-2,
        "mm": 1e-3,
        "um": 1e-6,
        "nm": 1e-9,
        "angstrom": 1e-10,
        "A": 1e-10,
    },
    # Time
    "time": {
        "s": 1.0,
        "ms": 1e-3,
        "us": 1e-6,
        "ns": 1e-9,
        "min": 60.0,
        "h": 3600.0,
    },
    # Mass
    "mass": {
        "kg": 1.0,
        "g": 1e-3,
        "mg": 1e-6,
        "ug": 1e-9,
        "amu": 1.66053906660e-27,
    },
    # Temperature
    "temperature": {
        "K": 1.0,
        # Celsius requires offset - handled separately
    },
    # Pressure
    "pressure": {
        "Pa": 1.0,
        "kPa": 1e3,
        "MPa": 1e6,
        "bar": 1e5,
        "atm": 101325.0,
        "torr": 133.322,
        "mmHg": 133.322,
    },
    # Amount
    "amount": {
        "mol": 1.0,
        "kmol": 1e3,
        "mmol": 1e-3,
        "umol": 1e-6,
    },
    # Volume
    "volume": {
        "m3": 1.0,
        "m³": 1.0,
        "L": 1e-3,
        "mL": 1e-6,
        "cm3": 1e-6,
        "cm³": 1e-6,
    },
}


def convert_units(
    value: Union[float, NDArray[np.float64]],
    from_unit: str,
    to_unit: str,
    quantity: str,
) -> Union[float, NDArray[np.float64]]:
    """
    Convert between units.

    Args:
        value: Value to convert
        from_unit: Source unit
        to_unit: Target unit
        quantity: Physical quantity (e.g., "length", "time")

    Returns:
        Converted value

    Raises:
        ValueError: If units are not recognized

    Example:
        >>> convert_units(1.0, "nm", "m", "length")
        1e-9
        >>> convert_units(101325, "Pa", "atm", "pressure")
        1.0
    """
    if quantity not in UNIT_FACTORS:
        raise ValueError(f"Unknown quantity type: {quantity}")

    units = UNIT_FACTORS[quantity]

    if from_unit not in units:
        raise ValueError(f"Unknown {quantity} unit: {from_unit}")
    if to_unit not in units:
        raise ValueError(f"Unknown {quantity} unit: {to_unit}")

    # Convert to SI, then to target
    si_value = value * units[from_unit]
    return si_value / units[to_unit]


def convert_temperature(
    value: Union[float, NDArray[np.float64]],
    from_unit: str,
    to_unit: str,
) -> Union[float, NDArray[np.float64]]:
    """
    Convert temperature between units.

    Handles offset units (Celsius, Fahrenheit).

    Args:
        value: Temperature value
        from_unit: Source unit ("K", "C", "F")
        to_unit: Target unit ("K", "C", "F")

    Returns:
        Converted temperature
    """
    # Convert to Kelvin first
    if from_unit == "K":
        kelvin = value
    elif from_unit in ["C", "°C"]:
        kelvin = value + 273.15
    elif from_unit in ["F", "°F"]:
        kelvin = (value + 459.67) * 5 / 9
    else:
        raise ValueError(f"Unknown temperature unit: {from_unit}")

    # Convert from Kelvin to target
    if to_unit == "K":
        return kelvin
    elif to_unit in ["C", "°C"]:
        return kelvin - 273.15
    elif to_unit in ["F", "°F"]:
        return kelvin * 9 / 5 - 459.67
    else:
        raise ValueError(f"Unknown temperature unit: {to_unit}")


def si_to_cgs(value: float, quantity: str) -> float:
    """
    Convert from SI to CGS units.

    Args:
        value: Value in SI units
        quantity: Physical quantity

    Returns:
        Value in CGS units
    """
    cgs_factors = {
        "length": 100.0,  # m -> cm
        "mass": 1000.0,  # kg -> g
        "time": 1.0,  # s -> s
        "force": 1e5,  # N -> dyn
        "energy": 1e7,  # J -> erg
        "pressure": 10.0,  # Pa -> Ba
    }

    if quantity not in cgs_factors:
        raise ValueError(f"CGS conversion not defined for: {quantity}")

    return value * cgs_factors[quantity]


def format_scientific(value: float, precision: int = 3) -> str:
    """
    Format value in scientific notation.

    Args:
        value: Value to format
        precision: Number of significant figures

    Returns:
        Formatted string
    """
    if value == 0:
        return "0"
    return f"{value:.{precision}e}"
