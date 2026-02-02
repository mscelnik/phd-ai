"""
Particle ensemble for stochastic simulations.

Manages a collection of particles representing the particle population,
providing methods for statistical sampling and population-level properties.

References:
    M.S. Celnik et al., "Coupling a stochastic soot population balance to
    gas-phase chemistry using operator splitting", Combustion and Flame 148 (2007)
"""

import logging
from dataclasses import dataclass, field
from typing import Iterator, Optional

import numpy as np
from numpy.typing import NDArray

from nanoparticle_simulator.particles.particle import Particle

logger = logging.getLogger(__name__)


@dataclass
class EnsembleStatistics:
    """
    Statistics of a particle ensemble.

    Immutable snapshot of ensemble statistics.

    Attributes:
        n_particles: Number of particles
        total_mass: Total mass (kg/m³)
        mean_diameter: Mean diameter (m)
        std_diameter: Standard deviation of diameter (m)
        mean_carbon: Mean carbon atoms per particle
        mean_primary: Mean primary particles per aggregate
        number_density: Number density (#/m³)
    """

    n_particles: int
    total_mass: float
    mean_diameter: float
    std_diameter: float
    mean_carbon: float
    mean_primary: float
    number_density: float


class ParticleEnsemble:
    """
    Collection of particles for stochastic simulation.

    Manages a particle population with methods for:
    - Adding/removing particles
    - Random selection for stochastic processes
    - Computing population statistics
    - Doubling/halving for controlling ensemble size

    Attributes:
        particles: List of particles
        sample_volume: Volume represented by the ensemble (m³)
        max_particles: Maximum allowed particles (for doubling/halving)
        min_particles: Minimum particles before doubling
    """

    def __init__(
        self,
        sample_volume: float = 1.0e-9,  # 1 mm³
        max_particles: int = 4096,
        min_particles: int = 512,
        seed: Optional[int] = None,
    ) -> None:
        """
        Initialize particle ensemble.

        Args:
            sample_volume: Volume represented by ensemble (m³)
            max_particles: Maximum particles before halving
            min_particles: Minimum particles before doubling
            seed: Random seed for reproducibility
        """
        self._particles: list[Particle] = []
        self._sample_volume = sample_volume
        self._max_particles = max_particles
        self._min_particles = min_particles
        self._statistical_weight = 1.0

        # Random number generator
        self._rng = np.random.default_rng(seed)

        # Particle ID counter
        self._next_id = 0

    @property
    def particles(self) -> list[Particle]:
        """Return list of particles."""
        return self._particles

    @property
    def n_particles(self) -> int:
        """Return number of particles in ensemble."""
        return len(self._particles)

    @property
    def sample_volume(self) -> float:
        """Return sample volume in m³."""
        return self._sample_volume

    @sample_volume.setter
    def sample_volume(self, value: float) -> None:
        """Set sample volume."""
        if value <= 0:
            raise ValueError("Sample volume must be positive")
        self._sample_volume = value

    @property
    def statistical_weight(self) -> float:
        """Return statistical weight of each particle."""
        return self._statistical_weight

    @property
    def number_density(self) -> float:
        """
        Return particle number density in #/m³.

        Accounts for statistical weight from doubling/halving.
        """
        if self._sample_volume <= 0:
            return 0.0
        return self.n_particles * self._statistical_weight / self._sample_volume

    @property
    def total_mass(self) -> float:
        """Return total mass in kg/m³."""
        if self.n_particles == 0:
            return 0.0
        mass = sum(p.mass for p in self._particles)
        return mass * self._statistical_weight / self._sample_volume

    @property
    def total_carbon(self) -> int:
        """Return total carbon atoms in ensemble."""
        return sum(p.n_carbon for p in self._particles)

    @property
    def mean_diameter(self) -> float:
        """Return mean particle diameter in m."""
        if self.n_particles == 0:
            return 0.0
        return np.mean([p.diameter for p in self._particles])

    @property
    def std_diameter(self) -> float:
        """Return standard deviation of diameter in m."""
        if self.n_particles < 2:
            return 0.0
        return np.std([p.diameter for p in self._particles])

    def add_particle(self, particle: Particle) -> None:
        """
        Add a particle to the ensemble.

        Args:
            particle: Particle to add
        """
        particle._id = self._next_id
        self._next_id += 1
        self._particles.append(particle)

        # Check if halving is needed
        if self.n_particles > self._max_particles:
            self._halve()

    def remove_particle(self, index: int) -> Particle:
        """
        Remove a particle by index.

        Args:
            index: Index of particle to remove

        Returns:
            Removed particle
        """
        particle = self._particles.pop(index)

        # Check if doubling is needed
        if self.n_particles < self._min_particles and self.n_particles > 0:
            self._double()

        return particle

    def remove_random_particle(self) -> Optional[Particle]:
        """
        Remove a random particle.

        Returns:
            Removed particle, or None if ensemble is empty
        """
        if self.n_particles == 0:
            return None
        idx = self._rng.integers(0, self.n_particles)
        return self.remove_particle(idx)

    def select_random(self) -> Optional[Particle]:
        """
        Select a random particle (without removal).

        Returns:
            Selected particle, or None if ensemble is empty
        """
        if self.n_particles == 0:
            return None
        idx = self._rng.integers(0, self.n_particles)
        return self._particles[idx]

    def select_random_pair(self) -> Optional[tuple[int, int]]:
        """
        Select two distinct random particles.

        Returns:
            Tuple of (index1, index2), or None if less than 2 particles
        """
        if self.n_particles < 2:
            return None
        idx1 = self._rng.integers(0, self.n_particles)
        idx2 = self._rng.integers(0, self.n_particles - 1)
        if idx2 >= idx1:
            idx2 += 1
        return (idx1, idx2)

    def select_weighted(self, weights: NDArray[np.float64]) -> Optional[tuple[int, Particle]]:
        """
        Select a particle with given weights.

        Args:
            weights: Selection weights (must sum to positive value)

        Returns:
            Tuple of (index, particle), or None if ensemble is empty
        """
        if self.n_particles == 0:
            return None

        total_weight = np.sum(weights)
        if total_weight <= 0:
            return None

        probs = weights / total_weight
        idx = self._rng.choice(self.n_particles, p=probs)
        return (idx, self._particles[idx])

    def _halve(self) -> None:
        """
        Halve the ensemble by random removal.

        Doubles the statistical weight of remaining particles.
        """
        n_remove = self.n_particles // 2
        indices = self._rng.choice(self.n_particles, size=n_remove, replace=False)
        # Remove in reverse order to maintain indices
        for idx in sorted(indices, reverse=True):
            self._particles.pop(idx)
        self._statistical_weight *= 2.0
        logger.debug(f"Halved ensemble: {self.n_particles} particles remaining")

    def _double(self) -> None:
        """
        Double the ensemble by copying particles.

        Halves the statistical weight of all particles.
        """
        original_particles = list(self._particles)
        for p in original_particles:
            self._particles.append(p.copy())
        self._statistical_weight *= 0.5
        logger.debug(f"Doubled ensemble: {self.n_particles} particles now")

    def get_statistics(self) -> EnsembleStatistics:
        """
        Compute ensemble statistics.

        Returns:
            Snapshot of current statistics
        """
        if self.n_particles == 0:
            return EnsembleStatistics(
                n_particles=0,
                total_mass=0.0,
                mean_diameter=0.0,
                std_diameter=0.0,
                mean_carbon=0.0,
                mean_primary=0.0,
                number_density=0.0,
            )

        diameters = [p.diameter for p in self._particles]
        return EnsembleStatistics(
            n_particles=self.n_particles,
            total_mass=self.total_mass,
            mean_diameter=np.mean(diameters),
            std_diameter=np.std(diameters) if len(diameters) > 1 else 0.0,
            mean_carbon=np.mean([p.n_carbon for p in self._particles]),
            mean_primary=np.mean([p.n_primary for p in self._particles]),
            number_density=self.number_density,
        )

    def diameter_distribution(
        self, bins: int = 50, range: Optional[tuple[float, float]] = None
    ) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
        """
        Compute particle size distribution.

        Args:
            bins: Number of histogram bins
            range: (min, max) diameter range in m

        Returns:
            Tuple of (bin_centers, counts)
        """
        if self.n_particles == 0:
            return np.array([]), np.array([])

        diameters = np.array([p.diameter for p in self._particles])
        counts, edges = np.histogram(diameters, bins=bins, range=range)
        centers = (edges[:-1] + edges[1:]) / 2
        return centers, counts.astype(float) * self._statistical_weight

    def clear(self) -> None:
        """Remove all particles from ensemble."""
        self._particles.clear()
        self._statistical_weight = 1.0

    def __len__(self) -> int:
        return self.n_particles

    def __iter__(self) -> Iterator[Particle]:
        return iter(self._particles)

    def __getitem__(self, index: int) -> Particle:
        return self._particles[index]

    def __repr__(self) -> str:
        return f"ParticleEnsemble(n={self.n_particles}, " f"N={self.number_density:.2e} #/m³)"
