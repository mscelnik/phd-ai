"""
Particle processes for population balance.

Implements the fundamental particle processes:
- Nucleation (inception)
- Surface growth (HACA mechanism)
- Coagulation (collision and sticking)
- Oxidation (burnout)

References:
    M.S. Celnik et al., "An aromatic site description of soot particles",
    Combustion and Flame 155 (2008)

    M.S. Celnik, "Modelling soot formation in turbulent flames",
    PhD Thesis, University of Cambridge (2007)
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Protocol, Optional
import numpy as np
from numpy.typing import NDArray

from nanoparticle_simulator.particles.particle import Particle, create_nascent_particle


# Physical constants
KB = 1.380649e-23  # Boltzmann constant (J/K)
AVOGADRO = 6.02214076e23  # Avogadro's number (mol⁻¹)
PI = np.pi


class GasPhaseInterface(Protocol):
    """Protocol for gas-phase interface needed by particle processes."""

    @property
    def T(self) -> float:
        """Temperature in K."""
        ...

    @property
    def P(self) -> float:
        """Pressure in Pa."""
        ...

    def species_concentration(self, name: str) -> float:
        """Get species concentration in kmol/m³."""
        ...


@dataclass
class ProcessRates:
    """
    Container for process rates.

    Attributes:
        nucleation: Nucleation rate (#/m³/s)
        growth: Growth rate (kg/m³/s)
        coagulation: Coagulation rate (#/m³/s)
        oxidation: Oxidation rate (kg/m³/s)
    """

    nucleation: float = 0.0
    growth: float = 0.0
    coagulation: float = 0.0
    oxidation: float = 0.0

    @property
    def total_rate(self) -> float:
        """Return sum of all rates."""
        return abs(self.nucleation) + abs(self.growth) + abs(self.coagulation) + abs(self.oxidation)


class ParticleProcess(ABC):
    """
    Abstract base class for particle processes.

    Defines the interface for all particle transformation processes.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Process name."""
        ...

    @abstractmethod
    def rate(self, gas: GasPhaseInterface, particle: Optional[Particle] = None) -> float:
        """
        Calculate process rate.

        Args:
            gas: Gas-phase interface
            particle: Target particle (if applicable)

        Returns:
            Process rate in appropriate units
        """
        ...

    @abstractmethod
    def apply(
        self,
        gas: GasPhaseInterface,
        particle: Optional[Particle] = None,
        dt: float = 0.0,
    ) -> Optional[Particle]:
        """
        Apply the process.

        Args:
            gas: Gas-phase interface
            particle: Target particle
            dt: Time step

        Returns:
            New or modified particle
        """
        ...


class NucleationProcess(ParticleProcess):
    """
    Nucleation (inception) process.

    Models the formation of nascent soot particles from gas-phase
    precursors (typically pyrene, C16H10).

    The nucleation rate is proportional to the collision frequency
    of PAH molecules.

    Attributes:
        precursor: Precursor species name (default: "A4" for pyrene)
        n_carbon_nascent: Carbon atoms in nascent particle
        n_hydrogen_nascent: Hydrogen atoms in nascent particle
    """

    def __init__(
        self,
        precursor: str = "A4",  # Pyrene (C16H10)
        n_carbon_nascent: int = 32,  # Two pyrene molecules
        n_hydrogen_nascent: int = 18,  # After H2 loss
    ) -> None:
        """
        Initialize nucleation process.

        Args:
            precursor: Precursor species name
            n_carbon_nascent: Carbon atoms in nascent particle
            n_hydrogen_nascent: Hydrogen atoms in nascent particle
        """
        self._precursor = precursor
        self._n_carbon = n_carbon_nascent
        self._n_hydrogen = n_hydrogen_nascent

        # Rate constant (m³/mol/s) - collision efficiency
        self._k_nuc = 2.0e9

    @property
    def name(self) -> str:
        return "nucleation"

    def rate(self, gas: GasPhaseInterface, particle: Optional[Particle] = None) -> float:
        """
        Calculate nucleation rate in #/m³/s.

        Rate is proportional to [A4]² for pyrene dimerization.

        Args:
            gas: Gas-phase interface
            particle: Not used

        Returns:
            Nucleation rate (#/m³/s)
        """
        try:
            c_precursor = gas.species_concentration(self._precursor) * 1000.0  # kmol -> mol
        except (KeyError, ValueError):
            return 0.0

        # Bimolecular nucleation: rate ∝ [A4]²
        return 0.5 * self._k_nuc * c_precursor**2 * AVOGADRO

    def apply(
        self,
        gas: GasPhaseInterface,
        particle: Optional[Particle] = None,
        dt: float = 0.0,
    ) -> Particle:
        """
        Create a nascent particle.

        Args:
            gas: Gas-phase interface
            particle: Not used
            dt: Current time for creation timestamp

        Returns:
            New nascent particle
        """
        return create_nascent_particle(
            n_carbon=self._n_carbon,
            n_hydrogen=self._n_hydrogen,
            creation_time=dt,
        )


class GrowthProcess(ParticleProcess):
    """
    Surface growth process via HACA mechanism.

    Models the Hydrogen-Abstraction-Carbon-Addition mechanism for
    soot particle growth. The process involves:
    1. H-abstraction by H atoms creating active sites
    2. C₂H₂ addition to active sites

    Reference:
        Frenklach & Wang, "Detailed modeling of soot particle nucleation
        and growth", Proc. Combust. Inst. 23 (1991)
    """

    def __init__(
        self,
        k_growth: float = 8.0e7,  # Rate constant (m³/mol/s)
        chi: float = 1.0,  # Steric factor
    ) -> None:
        """
        Initialize growth process.

        Args:
            k_growth: Growth rate constant
            chi: Steric factor for active site coverage
        """
        self._k_growth = k_growth
        self._chi = chi

    @property
    def name(self) -> str:
        return "growth"

    def rate(self, gas: GasPhaseInterface, particle: Optional[Particle] = None) -> float:
        """
        Calculate growth rate per particle surface area.

        Rate is proportional to [C₂H₂] and active surface area.

        Args:
            gas: Gas-phase interface
            particle: Target particle

        Returns:
            Growth rate (C atoms/m²/s)
        """
        if particle is None:
            return 0.0

        try:
            c_c2h2 = gas.species_concentration("C2H2") * 1000.0  # kmol -> mol/m³
        except (KeyError, ValueError):
            return 0.0

        # Rate per unit surface area
        return self._k_growth * self._chi * c_c2h2

    def carbon_addition_rate(self, gas: GasPhaseInterface, particle: Particle) -> float:
        """
        Calculate carbon atom addition rate for a particle.

        Args:
            gas: Gas-phase interface
            particle: Target particle

        Returns:
            Carbon addition rate (atoms/s)
        """
        rate_per_area = self.rate(gas, particle)
        return rate_per_area * particle.surface_area * AVOGADRO

    def apply(
        self,
        gas: GasPhaseInterface,
        particle: Optional[Particle] = None,
        dt: float = 1e-6,
    ) -> Optional[Particle]:
        """
        Apply growth to a particle.

        Adds carbon and hydrogen atoms based on HACA stoichiometry.

        Args:
            gas: Gas-phase interface
            particle: Target particle
            dt: Time step (s)

        Returns:
            Modified particle (same object)
        """
        if particle is None:
            return None

        rate = self.carbon_addition_rate(gas, particle)
        n_carbon_add = int(rate * dt)

        if n_carbon_add > 0:
            particle.add_carbon(n_carbon_add * 2)  # C₂ addition
            # Add ~0.5 H per 2 C (net)
            particle.add_hydrogen(n_carbon_add // 2)

        return particle


class CoagulationProcess(ParticleProcess):
    """
    Coagulation (collision) process.

    Models the collision and sticking of two particles to form
    an aggregate. Uses the free-molecular and continuum coagulation
    kernels with transition regime interpolation.

    Reference:
        Fuchs, "The Mechanics of Aerosols" (1964)
    """

    def __init__(
        self,
        sticking_prob: float = 1.0,  # Collision efficiency
    ) -> None:
        """
        Initialize coagulation process.

        Args:
            sticking_prob: Probability of sticking upon collision
        """
        self._sticking_prob = sticking_prob

    @property
    def name(self) -> str:
        return "coagulation"

    def kernel(
        self,
        p1: Particle,
        p2: Particle,
        T: float,
        P: float,
    ) -> float:
        """
        Calculate coagulation kernel β(i,j).

        Uses free-molecular regime kernel:
        β = ε * (3/(4πρ))^(1/6) * (6kT/ρ)^(1/2) * (1/m1 + 1/m2)^(1/2) * (d1 + d2)²

        Args:
            p1: First particle
            p2: Second particle
            T: Temperature (K)
            P: Pressure (Pa)

        Returns:
            Coagulation kernel (m³/s)
        """
        d1 = p1.diameter
        d2 = p2.diameter
        m1 = p1.mass
        m2 = p2.mass

        if m1 <= 0 or m2 <= 0:
            return 0.0

        # Free-molecular kernel
        coeff = np.sqrt(6.0 * KB * T) * (d1 + d2) ** 2
        mass_term = np.sqrt(1.0 / m1 + 1.0 / m2)

        return self._sticking_prob * coeff * mass_term / 4.0

    def rate(self, gas: GasPhaseInterface, particle: Optional[Particle] = None) -> float:
        """
        Calculate total coagulation rate.

        Note: This returns a per-particle rate; the actual rate
        requires knowledge of the full population.

        Args:
            gas: Gas-phase interface
            particle: Not used (requires population)

        Returns:
            Characteristic rate scale
        """
        # This is a placeholder; actual rate computed in solver
        return 0.0

    def apply(
        self,
        gas: GasPhaseInterface,
        particle: Optional[Particle] = None,
        dt: float = 0.0,
    ) -> Optional[Particle]:
        """
        Apply coagulation (not applicable here).

        Coagulation requires two particles and is handled
        directly by the stochastic solver.

        Args:
            gas: Gas-phase interface
            particle: Not used
            dt: Not used

        Returns:
            None
        """
        return None

    def coagulate(self, p1: Particle, p2: Particle) -> Particle:
        """
        Coagulate two particles.

        Args:
            p1: First particle
            p2: Second particle

        Returns:
            Coagulated particle
        """
        return p1.coagulate(p2)


class OxidationProcess(ParticleProcess):
    """
    Oxidation (burnout) process.

    Models the removal of carbon from particles by reaction
    with O₂ and OH radicals.

    The rate is proportional to oxidizer concentration and
    particle surface area.
    """

    def __init__(
        self,
        k_o2: float = 1.0e4,  # O₂ oxidation rate constant
        k_oh: float = 1.0e8,  # OH oxidation rate constant
    ) -> None:
        """
        Initialize oxidation process.

        Args:
            k_o2: O₂ oxidation rate constant (m/s)
            k_oh: OH oxidation rate constant (m/s)
        """
        self._k_o2 = k_o2
        self._k_oh = k_oh

    @property
    def name(self) -> str:
        return "oxidation"

    def rate(self, gas: GasPhaseInterface, particle: Optional[Particle] = None) -> float:
        """
        Calculate oxidation rate per particle surface area.

        Args:
            gas: Gas-phase interface
            particle: Target particle

        Returns:
            Oxidation rate (C atoms/m²/s)
        """
        try:
            c_o2 = gas.species_concentration("O2") * 1000.0  # mol/m³
        except (KeyError, ValueError):
            c_o2 = 0.0

        try:
            c_oh = gas.species_concentration("OH") * 1000.0  # mol/m³
        except (KeyError, ValueError):
            c_oh = 0.0

        return (self._k_o2 * c_o2 + self._k_oh * c_oh) * AVOGADRO

    def carbon_removal_rate(self, gas: GasPhaseInterface, particle: Particle) -> float:
        """
        Calculate carbon removal rate for a particle.

        Args:
            gas: Gas-phase interface
            particle: Target particle

        Returns:
            Carbon removal rate (atoms/s)
        """
        rate_per_area = self.rate(gas, particle)
        return rate_per_area * particle.surface_area

    def apply(
        self,
        gas: GasPhaseInterface,
        particle: Optional[Particle] = None,
        dt: float = 1e-6,
    ) -> Optional[Particle]:
        """
        Apply oxidation to a particle.

        Removes carbon atoms based on oxidation rate.

        Args:
            gas: Gas-phase interface
            particle: Target particle
            dt: Time step (s)

        Returns:
            Modified particle, or None if fully oxidized
        """
        if particle is None:
            return None

        rate = self.carbon_removal_rate(gas, particle)
        n_carbon_remove = int(rate * dt)

        if n_carbon_remove > 0:
            success = particle.remove_carbon(n_carbon_remove)
            if not success or particle.n_carbon <= 0:
                return None  # Particle fully oxidized

            # Remove proportional hydrogen
            n_h_remove = max(1, n_carbon_remove // 4)
            particle.remove_hydrogen(n_h_remove)

        return particle
