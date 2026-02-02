"""
Species representation for chemical species.

Provides a data class for representing chemical species with their
thermodynamic and transport properties.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Species:
    """
    Representation of a chemical species.

    Attributes:
        name: Species name (e.g., 'CH4', 'O2')
        mw: Molecular weight in kg/mol
        h_formation: Standard enthalpy of formation in J/mol
        s_formation: Standard entropy of formation in J/(mol·K)
        cp_coeffs: Coefficients for heat capacity polynomial (NASA format)
        transport: Transport properties dictionary
    """

    name: str
    mw: float  # kg/mol
    h_formation: Optional[float] = None  # J/mol
    s_formation: Optional[float] = None  # J/(mol·K)
    cp_coeffs: list[float] = field(default_factory=list)
    transport: dict = field(default_factory=dict)

    @property
    def molar_mass(self) -> float:
        """Return molar mass in kg/mol."""
        return self.mw

    def __repr__(self) -> str:
        return f"Species({self.name}, MW={self.mw:.4f} kg/mol)"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Species):
            return NotImplemented
        return self.name == other.name

    def __hash__(self) -> int:
        return hash(self.name)
