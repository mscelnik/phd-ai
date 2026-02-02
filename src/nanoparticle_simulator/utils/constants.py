"""
Physical constants.

Defines fundamental physical constants used throughout the package.
All values are in SI units.
"""

import numpy as np

# Mathematical constants
PI = np.pi

# Fundamental constants (CODATA 2018 values)
AVOGADRO = 6.02214076e23  # Avogadro's number (mol⁻¹)
BOLTZMANN = 1.380649e-23  # Boltzmann constant (J/K)
PLANCK = 6.62607015e-34  # Planck constant (J·s)
SPEED_OF_LIGHT = 299792458.0  # Speed of light (m/s)
ELEMENTARY_CHARGE = 1.602176634e-19  # Elementary charge (C)

# Derived constants
GAS_CONSTANT = AVOGADRO * BOLTZMANN  # Universal gas constant (J/(mol·K))

# Atomic masses (kg/mol)
ATOMIC_MASS = {
    "H": 1.00794e-3,
    "C": 12.0107e-3,
    "N": 14.0067e-3,
    "O": 15.9994e-3,
    "Ar": 39.948e-3,
}

# Material properties
CARBON_DENSITY = 1800.0  # Soot density (kg/m³)
GRAPHITE_DENSITY = 2260.0  # Graphite density (kg/m³)

# Standard conditions
STANDARD_TEMPERATURE = 298.15  # Standard temperature (K)
STANDARD_PRESSURE = 101325.0  # Standard pressure (Pa)
