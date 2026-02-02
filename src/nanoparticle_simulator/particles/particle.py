"""
Particle representation.

Defines the Particle class for representing individual particles in the
stochastic population balance model.

The particle model uses a detailed description including:
- Primary particle count (aggregation)
- Carbon atom count (size)
- Hydrogen atom count (composition)
- Active surface sites (aromatic site model)

References:
    M.S. Celnik et al., "An aromatic site description of soot particles",
    Combustion and Flame 155 (2008)
"""

from dataclasses import dataclass, field
from typing import Optional
import numpy as np


# Physical constants
C_MASS = 12.011e-3  # Carbon atomic mass (kg/mol)
H_MASS = 1.008e-3  # Hydrogen atomic mass (kg/mol)
AVOGADRO = 6.02214076e23  # Avogadro's number (mol⁻¹)
CARBON_DENSITY = 1800.0  # Soot density (kg/m³)


@dataclass
class Particle:
    """
    Individual particle representation.

    Models a soot or CNT particle using a detailed description that
    tracks chemical composition and surface sites.

    Attributes:
        n_carbon: Number of carbon atoms
        n_hydrogen: Number of hydrogen atoms
        n_primary: Number of primary particles (for aggregates)
        active_sites: Number of active surface sites (radicals)
        creation_time: Time of particle creation (s)

    Properties:
        mass: Particle mass (kg)
        diameter: Spherical equivalent diameter (m)
        surface_area: Surface area (m²)
        volume: Volume (m³)
    """

    n_carbon: int = 0
    n_hydrogen: int = 0
    n_primary: int = 1
    active_sites: int = 0
    creation_time: float = 0.0

    # Optional tracking
    _id: Optional[int] = field(default=None, repr=False)

    def __post_init__(self) -> None:
        """Validate particle state."""
        if self.n_carbon < 0:
            raise ValueError("Carbon count cannot be negative")
        if self.n_hydrogen < 0:
            raise ValueError("Hydrogen count cannot be negative")
        if self.n_primary < 1:
            raise ValueError("Primary particle count must be at least 1")
        if self.active_sites < 0:
            raise ValueError("Active site count cannot be negative")

    @property
    def mass(self) -> float:
        """
        Calculate particle mass in kg.

        Returns:
            Mass in kg
        """
        return self.n_carbon * C_MASS / AVOGADRO + self.n_hydrogen * H_MASS / AVOGADRO

    @property
    def carbon_mass(self) -> float:
        """
        Calculate carbon mass in kg.

        Returns:
            Carbon mass in kg
        """
        return self.n_carbon * C_MASS / AVOGADRO

    @property
    def volume(self) -> float:
        """
        Calculate particle volume in m³.

        Uses carbon density for soot particles.

        Returns:
            Volume in m³
        """
        # Approximate volume using carbon mass and soot density
        return self.carbon_mass / CARBON_DENSITY

    @property
    def diameter(self) -> float:
        """
        Calculate spherical equivalent diameter in m.

        For aggregates, this is the diameter of a sphere with
        equivalent volume.

        Returns:
            Diameter in m
        """
        return (6.0 * self.volume / np.pi) ** (1.0 / 3.0)

    @property
    def primary_diameter(self) -> float:
        """
        Calculate primary particle diameter in m.

        Diameter of individual primary particles in the aggregate.

        Returns:
            Primary diameter in m
        """
        if self.n_primary <= 0:
            return 0.0
        v_primary = self.volume / self.n_primary
        return (6.0 * v_primary / np.pi) ** (1.0 / 3.0)

    @property
    def surface_area(self) -> float:
        """
        Calculate surface area in m².

        For aggregates, uses primary particle model.

        Returns:
            Surface area in m²
        """
        d_p = self.primary_diameter
        return self.n_primary * np.pi * d_p**2

    @property
    def c_to_h_ratio(self) -> float:
        """
        Calculate carbon to hydrogen ratio.

        Returns:
            C/H ratio (dimensionless)
        """
        if self.n_hydrogen == 0:
            return float("inf")
        return self.n_carbon / self.n_hydrogen

    @property
    def is_valid(self) -> bool:
        """
        Check if particle is in a valid state.

        Returns:
            True if particle is valid
        """
        return self.n_carbon >= 0 and self.n_hydrogen >= 0 and self.n_primary >= 1

    def add_carbon(self, n: int = 1) -> None:
        """
        Add carbon atoms to the particle.

        Args:
            n: Number of carbon atoms to add
        """
        self.n_carbon += n

    def add_hydrogen(self, n: int = 1) -> None:
        """
        Add hydrogen atoms to the particle.

        Args:
            n: Number of hydrogen atoms to add
        """
        self.n_hydrogen += n

    def remove_carbon(self, n: int = 1) -> bool:
        """
        Remove carbon atoms from the particle.

        Args:
            n: Number of carbon atoms to remove

        Returns:
            True if successful, False if not enough carbon
        """
        if self.n_carbon >= n:
            self.n_carbon -= n
            return True
        return False

    def remove_hydrogen(self, n: int = 1) -> bool:
        """
        Remove hydrogen atoms from the particle.

        Args:
            n: Number of hydrogen atoms to remove

        Returns:
            True if successful, False if not enough hydrogen
        """
        if self.n_hydrogen >= n:
            self.n_hydrogen -= n
            return True
        return False

    def coagulate(self, other: "Particle") -> "Particle":
        """
        Coagulate this particle with another.

        Creates a new particle representing the aggregate of
        this particle and the other particle.

        Args:
            other: Particle to coagulate with

        Returns:
            New coagulated particle
        """
        return Particle(
            n_carbon=self.n_carbon + other.n_carbon,
            n_hydrogen=self.n_hydrogen + other.n_hydrogen,
            n_primary=self.n_primary + other.n_primary,
            active_sites=self.active_sites + other.active_sites,
            creation_time=min(self.creation_time, other.creation_time),
        )

    def copy(self) -> "Particle":
        """
        Create a copy of this particle.

        Returns:
            New particle with same properties
        """
        return Particle(
            n_carbon=self.n_carbon,
            n_hydrogen=self.n_hydrogen,
            n_primary=self.n_primary,
            active_sites=self.active_sites,
            creation_time=self.creation_time,
            _id=self._id,
        )

    def __repr__(self) -> str:
        return f"Particle(C={self.n_carbon}, H={self.n_hydrogen}, " f"d={self.diameter*1e9:.2f} nm)"


def create_nascent_particle(
    n_carbon: int,
    n_hydrogen: int,
    creation_time: float = 0.0,
) -> Particle:
    """
    Create a nascent (newly nucleated) particle.

    Factory function for creating new particles from nucleation.

    Args:
        n_carbon: Number of carbon atoms
        n_hydrogen: Number of hydrogen atoms
        creation_time: Time of creation

    Returns:
        New particle
    """
    return Particle(
        n_carbon=n_carbon,
        n_hydrogen=n_hydrogen,
        n_primary=1,
        active_sites=2,  # Assume 2 active sites for nascent particles
        creation_time=creation_time,
    )
