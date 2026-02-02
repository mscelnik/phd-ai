"""
Base reactor class.

Provides the abstract interface for reactor models.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, Callable, Any

import numpy as np
from numpy.typing import NDArray

from nanoparticle_simulator.chemistry.gas_phase import GasPhase, GasPhaseState
from nanoparticle_simulator.particles.ensemble import EnsembleStatistics
from nanoparticle_simulator.particles.stochastic_solver import StochasticSolver


@dataclass
class ReactorState:
    """
    Complete state of a reactor at a point in time.

    Attributes:
        time: Current time (s)
        gas: Gas-phase state
        particles: Particle ensemble statistics
        temperature: Temperature (K)
        pressure: Pressure (Pa)
        volume: Reactor volume (m³)
    """

    time: float
    gas: GasPhaseState
    particles: EnsembleStatistics
    temperature: float
    pressure: float
    volume: float


@dataclass
class SimulationResult:
    """
    Results from a reactor simulation.

    Attributes:
        times: Time points (s)
        temperatures: Temperature history (K)
        pressures: Pressure history (Pa)
        species: Species mass fractions (n_times, n_species)
        n_particles: Particle count history
        mean_diameter: Mean particle diameter history (m)
        number_density: Number density history (#/m³)
        total_mass: Particle mass concentration history (kg/m³)
        states: List of full reactor states (optional)
    """

    times: NDArray[np.float64] = field(default_factory=lambda: np.array([]))
    temperatures: NDArray[np.float64] = field(default_factory=lambda: np.array([]))
    pressures: NDArray[np.float64] = field(default_factory=lambda: np.array([]))
    species: NDArray[np.float64] = field(default_factory=lambda: np.array([]))
    species_names: list[str] = field(default_factory=list)
    n_particles: NDArray[np.int64] = field(default_factory=lambda: np.array([]))
    mean_diameter: NDArray[np.float64] = field(default_factory=lambda: np.array([]))
    number_density: NDArray[np.float64] = field(default_factory=lambda: np.array([]))
    total_mass: NDArray[np.float64] = field(default_factory=lambda: np.array([]))
    states: list[ReactorState] = field(default_factory=list)


class ReactorBase(ABC):
    """
    Abstract base class for reactors.

    Defines the interface for all reactor models.

    Attributes:
        gas: Gas-phase chemistry
        particles: Particle solver
        volume: Reactor volume (m³)
    """

    def __init__(
        self,
        gas: GasPhase,
        particles: Optional[StochasticSolver] = None,
        volume: float = 1.0e-6,  # 1 cm³
    ) -> None:
        """
        Initialize reactor.

        Args:
            gas: Gas-phase chemistry interface
            particles: Particle solver (optional)
            volume: Reactor volume (m³)
        """
        self._gas = gas
        self._particles = particles
        self._volume = volume
        self._time = 0.0

    @property
    def gas(self) -> GasPhase:
        """Return gas-phase interface."""
        return self._gas

    @property
    def particles(self) -> Optional[StochasticSolver]:
        """Return particle solver."""
        return self._particles

    @property
    def volume(self) -> float:
        """Return reactor volume in m³."""
        return self._volume

    @volume.setter
    def volume(self, value: float) -> None:
        """Set reactor volume."""
        if value <= 0:
            raise ValueError("Volume must be positive")
        self._volume = value

    @property
    def time(self) -> float:
        """Return current time in s."""
        return self._time

    @property
    def temperature(self) -> float:
        """Return current temperature in K."""
        return self._gas.T

    @property
    def pressure(self) -> float:
        """Return current pressure in Pa."""
        return self._gas.P

    def get_state(self) -> ReactorState:
        """
        Get current reactor state.

        Returns:
            Snapshot of reactor state
        """
        gas_state = self._gas.get_state()
        particle_stats = (
            self._particles.ensemble.get_statistics()
            if self._particles is not None
            else EnsembleStatistics(0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
        )

        return ReactorState(
            time=self._time,
            gas=gas_state,
            particles=particle_stats,
            temperature=self.temperature,
            pressure=self.pressure,
            volume=self._volume,
        )

    @abstractmethod
    def step(self, dt: float) -> None:
        """
        Advance reactor by one time step.

        Args:
            dt: Time step (s)
        """
        ...

    @abstractmethod
    def run(
        self,
        duration: float,
        dt: float,
        output_interval: Optional[float] = None,
        callback: Optional[Callable[[ReactorState], None]] = None,
    ) -> SimulationResult:
        """
        Run simulation for a given duration.

        Args:
            duration: Total simulation time (s)
            dt: Time step (s)
            output_interval: Interval for saving output (s)
            callback: Optional callback after each output

        Returns:
            Simulation results
        """
        ...

    def reset(self) -> None:
        """Reset reactor to initial state."""
        self._time = 0.0
        if self._particles is not None:
            self._particles.initialize(sample_volume=self._volume)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"T={self.temperature:.1f} K, "
            f"P={self.pressure:.0f} Pa, "
            f"V={self._volume:.2e} m³)"
        )
