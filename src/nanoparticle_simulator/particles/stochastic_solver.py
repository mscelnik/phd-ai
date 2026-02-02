"""
Stochastic solver for particle population balance.

Implements the Direct Simulation Algorithm (DSA) for solving the
particle population balance equation using Monte Carlo methods.

The algorithm uses the linear process deferment technique to
efficiently sample and execute particle events.

References:
    M.S. Celnik et al., "Coupling a stochastic soot population balance to
    gas-phase chemistry using operator splitting", Combustion and Flame 148 (2007)

    A. Eibeck & W. Wagner, "Stochastic particle approximations for
    Smoluchowski's coagulation equation", Ann. Appl. Probab. 11 (2001)
"""

# FIXME: check for long running tests - put time limits when testing!
import logging
from dataclasses import dataclass, field
from typing import Optional, Callable
from enum import Enum, auto

import numpy as np
from numpy.typing import NDArray

from nanoparticle_simulator.particles.particle import Particle
from nanoparticle_simulator.particles.ensemble import ParticleEnsemble
from nanoparticle_simulator.particles.processes import (
    ParticleProcess,
    NucleationProcess,
    GrowthProcess,
    CoagulationProcess,
    OxidationProcess,
    GasPhaseInterface,
    ProcessRates,
)

logger = logging.getLogger(__name__)


class EventType(Enum):
    """Types of stochastic events."""

    NUCLEATION = auto()
    GROWTH = auto()
    COAGULATION = auto()
    OXIDATION = auto()
    NONE = auto()


@dataclass
class StochasticEvent:
    """
    Record of a stochastic event.

    Attributes:
        time: Time of event
        event_type: Type of event
        particle_index: Index of affected particle
        rate: Rate at which event occurred
    """

    time: float
    event_type: EventType
    particle_index: Optional[int] = None
    rate: float = 0.0


@dataclass
class SolverConfig:
    """
    Configuration for stochastic solver.

    Attributes:
        max_particles: Maximum particles in ensemble
        min_particles: Minimum particles before doubling
        sample_volume: Sample volume (m³)
        seed: Random seed for reproducibility
        defer_growth: Use linear process deferment for growth
        defer_oxidation: Use linear process deferment for oxidation
    """

    max_particles: int = 4096
    min_particles: int = 512
    sample_volume: float = 1.0e-9
    seed: Optional[int] = None
    defer_growth: bool = True
    defer_oxidation: bool = True


class StochasticSolver:
    """
    Stochastic solver for particle population balance.

    Uses the Direct Simulation Algorithm with linear process
    deferment to efficiently solve the population balance equation.

    The solver handles:
    - Nucleation: Formation of new particles
    - Surface growth: Addition of mass to existing particles
    - Coagulation: Collision and sticking of particles
    - Oxidation: Removal of mass from particles

    Example:
        >>> solver = StochasticSolver()
        >>> solver.initialize(sample_volume=1e-9)
        >>> solver.add_process(NucleationProcess())
        >>> solver.add_process(GrowthProcess())
        >>> solver.add_process(CoagulationProcess())
        >>> solver.step(gas, dt=1e-6)
    """

    def __init__(
        self,
        config: Optional[SolverConfig] = None,
    ) -> None:
        """
        Initialize stochastic solver.

        Args:
            config: Solver configuration
        """
        self._config = config or SolverConfig()

        # Create ensemble
        self._ensemble = ParticleEnsemble(
            sample_volume=self._config.sample_volume,
            max_particles=self._config.max_particles,
            min_particles=self._config.min_particles,
            seed=self._config.seed,
        )

        # Processes
        self._nucleation: Optional[NucleationProcess] = None
        self._growth: Optional[GrowthProcess] = None
        self._coagulation: Optional[CoagulationProcess] = None
        self._oxidation: Optional[OxidationProcess] = None

        # Random number generator
        self._rng = np.random.default_rng(self._config.seed)

        # Deferred process accumulators
        self._deferred_growth: NDArray[np.float64] = np.array([])
        self._deferred_oxidation: NDArray[np.float64] = np.array([])

        # Statistics
        self._total_time = 0.0
        self._n_events = 0
        self._event_counts: dict[EventType, int] = {e: 0 for e in EventType}

    @property
    def ensemble(self) -> ParticleEnsemble:
        """Return the particle ensemble."""
        return self._ensemble

    @property
    def n_particles(self) -> int:
        """Return number of particles."""
        return self._ensemble.n_particles

    @property
    def total_time(self) -> float:
        """Return total simulated time."""
        return self._total_time

    @property
    def event_counts(self) -> dict[EventType, int]:
        """Return counts of each event type."""
        return self._event_counts.copy()

    def initialize(
        self,
        sample_volume: Optional[float] = None,
        initial_particles: Optional[list[Particle]] = None,
    ) -> None:
        """
        Initialize the solver.

        Args:
            sample_volume: Sample volume (m³)
            initial_particles: List of initial particles
        """
        if sample_volume is not None:
            self._ensemble.sample_volume = sample_volume

        self._ensemble.clear()
        self._total_time = 0.0
        self._n_events = 0
        self._event_counts = {e: 0 for e in EventType}

        if initial_particles is not None:
            for p in initial_particles:
                self._ensemble.add_particle(p)

        self._reset_deferred()

    def _reset_deferred(self) -> None:
        """Reset deferred process accumulators."""
        n = max(1, self.n_particles)
        self._deferred_growth = np.zeros(n)
        self._deferred_oxidation = np.zeros(n)

    def add_process(self, process: ParticleProcess) -> None:
        """
        Add a process to the solver.

        Args:
            process: Process to add
        """
        if isinstance(process, NucleationProcess):
            self._nucleation = process
        elif isinstance(process, GrowthProcess):
            self._growth = process
        elif isinstance(process, CoagulationProcess):
            self._coagulation = process
        elif isinstance(process, OxidationProcess):
            self._oxidation = process
        else:
            raise ValueError(f"Unknown process type: {type(process)}")

    def compute_rates(self, gas: GasPhaseInterface) -> ProcessRates:
        """
        Compute all process rates.

        Args:
            gas: Gas-phase interface

        Returns:
            Container with all rates
        """
        rates = ProcessRates()

        # Nucleation rate (#/m³/s)
        if self._nucleation is not None:
            rates.nucleation = self._nucleation.rate(gas)

        # Growth and oxidation require particles
        if self.n_particles > 0:
            # Total growth rate
            if self._growth is not None:
                total_growth = 0.0
                for p in self._ensemble:
                    total_growth += self._growth.carbon_addition_rate(gas, p)
                rates.growth = total_growth

            # Total oxidation rate
            if self._oxidation is not None:
                total_ox = 0.0
                for p in self._ensemble:
                    total_ox += self._oxidation.carbon_removal_rate(gas, p)
                rates.oxidation = total_ox

            # Coagulation rate
            if self._coagulation is not None and self.n_particles > 1:
                rates.coagulation = self._compute_coagulation_rate(gas)

        return rates

    def _compute_coagulation_rate(self, gas: GasPhaseInterface) -> float:
        """
        Compute total coagulation rate.

        Uses majorant kernel for efficiency.

        Args:
            gas: Gas-phase interface

        Returns:
            Total coagulation rate (#/m³/s)
        """
        if self._coagulation is None or self.n_particles < 2:
            return 0.0

        T = gas.T
        P = gas.P
        V = self._ensemble.sample_volume
        N = self.n_particles
        w = self._ensemble.statistical_weight

        # Use average kernel as estimate
        total_rate = 0.0
        n_samples = min(100, N * (N - 1) // 2)

        for _ in range(n_samples):
            pair = self._ensemble.select_random_pair()
            if pair is not None:
                i, j = pair
                beta = self._coagulation.kernel(self._ensemble[i], self._ensemble[j], T, P)
                total_rate += beta

        if n_samples > 0:
            total_rate *= N * (N - 1) / (2 * n_samples)

        # Convert to volumetric rate
        return total_rate * w**2 / V

    def step(
        self,
        gas: GasPhaseInterface,
        dt: float,
        callback: Optional[Callable[[StochasticEvent], None]] = None,
    ) -> int:
        """
        Advance the solver by one time step.

        Uses the Direct Simulation Algorithm to perform stochastic
        events within the time step.

        Args:
            gas: Gas-phase interface
            dt: Time step (s)
            callback: Optional callback for each event

        Returns:
            Number of events performed
        """
        t_start = self._total_time
        t_end = t_start + dt
        n_events = 0
        max_iterations = 10000  # Safety limit to prevent infinite loops

        for _ in range(max_iterations):
            if self._total_time >= t_end:
                break

            # Compute rates
            rates = self.compute_rates(gas)
            total_rate = rates.total_rate

            if total_rate <= 0:
                self._total_time = t_end
                break

            # Sample waiting time
            tau = self._rng.exponential(1.0 / total_rate)

            if self._total_time + tau > t_end:
                # No more events in this step
                # Apply deferred processes
                self._apply_deferred(gas, t_end - self._total_time)
                self._total_time = t_end
                break

            self._total_time += tau

            # Select event type
            event_type = self._select_event(rates)

            # Perform event
            event = self._perform_event(event_type, gas)

            if event is not None:
                n_events += 1
                self._n_events += 1
                self._event_counts[event_type] += 1

                if callback is not None:
                    callback(event)

        return n_events

    def _select_event(self, rates: ProcessRates) -> EventType:
        """
        Select event type based on rates.

        Args:
            rates: Process rates

        Returns:
            Selected event type
        """
        total = rates.total_rate
        if total <= 0:
            return EventType.NONE

        r = self._rng.uniform() * total
        cumulative = 0.0

        cumulative += rates.nucleation
        if r < cumulative:
            return EventType.NUCLEATION

        cumulative += rates.growth
        if r < cumulative:
            return EventType.GROWTH

        cumulative += rates.coagulation
        if r < cumulative:
            return EventType.COAGULATION

        return EventType.OXIDATION

    def _perform_event(self, event_type: EventType, gas: GasPhaseInterface) -> Optional[StochasticEvent]:
        """
        Perform a stochastic event.

        Args:
            event_type: Type of event
            gas: Gas-phase interface

        Returns:
            Event record, or None if event failed
        """
        if event_type == EventType.NUCLEATION:
            return self._do_nucleation(gas)
        elif event_type == EventType.GROWTH:
            return self._do_growth(gas)
        elif event_type == EventType.COAGULATION:
            return self._do_coagulation(gas)
        elif event_type == EventType.OXIDATION:
            return self._do_oxidation(gas)
        return None

    def _do_nucleation(self, gas: GasPhaseInterface) -> Optional[StochasticEvent]:
        """Perform nucleation event."""
        if self._nucleation is None:
            return None

        particle = self._nucleation.apply(gas, dt=self._total_time)
        self._ensemble.add_particle(particle)
        self._reset_deferred()

        return StochasticEvent(
            time=self._total_time,
            event_type=EventType.NUCLEATION,
            rate=self._nucleation.rate(gas),
        )

    def _do_growth(self, gas: GasPhaseInterface) -> Optional[StochasticEvent]:
        """Perform growth event."""
        if self._growth is None or self.n_particles == 0:
            return None

        # Select particle weighted by growth rate
        weights = np.array([self._growth.carbon_addition_rate(gas, p) for p in self._ensemble])

        result = self._ensemble.select_weighted(weights)
        if result is None:
            return None

        idx, particle = result

        # Add 2 carbon atoms (C₂ addition)
        particle.add_carbon(2)
        particle.add_hydrogen(1)

        return StochasticEvent(
            time=self._total_time,
            event_type=EventType.GROWTH,
            particle_index=idx,
            rate=np.sum(weights),
        )

    def _do_coagulation(self, gas: GasPhaseInterface) -> Optional[StochasticEvent]:
        """Perform coagulation event."""
        if self._coagulation is None or self.n_particles < 2:
            return None

        # Select random pair
        pair = self._ensemble.select_random_pair()
        if pair is None:
            return None

        i, j = pair
        p1 = self._ensemble[i]
        p2 = self._ensemble[j]

        # Check acceptance (majorant kernel)
        beta = self._coagulation.kernel(p1, p2, gas.T, gas.P)
        # Accept with probability 1 for now (exact kernel)

        # Coagulate
        new_particle = self._coagulation.coagulate(p1, p2)

        # Remove old particles (higher index first)
        if i > j:
            self._ensemble.remove_particle(i)
            self._ensemble.remove_particle(j)
        else:
            self._ensemble.remove_particle(j)
            self._ensemble.remove_particle(i)

        # Add new particle
        self._ensemble.add_particle(new_particle)
        self._reset_deferred()

        return StochasticEvent(
            time=self._total_time,
            event_type=EventType.COAGULATION,
            rate=beta,
        )

    def _do_oxidation(self, gas: GasPhaseInterface) -> Optional[StochasticEvent]:
        """Perform oxidation event."""
        if self._oxidation is None or self.n_particles == 0:
            return None

        # Select particle weighted by oxidation rate
        weights = np.array([self._oxidation.carbon_removal_rate(gas, p) for p in self._ensemble])

        result = self._ensemble.select_weighted(weights)
        if result is None:
            return None

        idx, particle = result

        # Remove carbon atoms
        n_remove = max(1, int(particle.n_carbon * 0.01))  # ~1% removal
        particle.remove_carbon(n_remove)
        particle.remove_hydrogen(n_remove // 4)

        # Check if particle is depleted
        if particle.n_carbon <= 0:
            self._ensemble.remove_particle(idx)
            self._reset_deferred()

        return StochasticEvent(
            time=self._total_time,
            event_type=EventType.OXIDATION,
            particle_index=idx,
            rate=np.sum(weights),
        )

    def _apply_deferred(self, gas: GasPhaseInterface, dt: float) -> None:
        """
        Apply deferred (linear) processes.

        For efficiency, growth and oxidation can be accumulated
        and applied at the end of the time step.

        Args:
            gas: Gas-phase interface
            dt: Remaining time (s)
        """
        if not self._config.defer_growth and not self._config.defer_oxidation:
            return

        for i, particle in enumerate(self._ensemble):
            if self._config.defer_growth and self._growth is not None:
                rate = self._growth.carbon_addition_rate(gas, particle)
                n_add = int(rate * dt)
                if n_add > 0:
                    particle.add_carbon(n_add)
                    particle.add_hydrogen(n_add // 2)

    def get_source_terms(self, gas: GasPhaseInterface) -> dict[str, float]:
        """
        Compute source terms for gas-phase coupling.

        Returns the rates of consumption/production of gas-phase
        species due to particle processes.

        Args:
            gas: Gas-phase interface

        Returns:
            Dictionary of species source terms (mol/m³/s)
        """
        sources: dict[str, float] = {}
        rates = self.compute_rates(gas)

        # Nucleation consumes PAH precursor
        # 2 A4 -> nascent particle + H2
        if self._nucleation is not None:
            nuc_rate = rates.nucleation / 6.022e23  # #/m³/s -> mol/m³/s
            sources["A4"] = sources.get("A4", 0.0) - 2.0 * nuc_rate
            sources["H2"] = sources.get("H2", 0.0) + nuc_rate

        # Growth consumes C2H2, produces H2
        if self._growth is not None:
            # Convert carbon addition rate to C2H2 consumption
            growth_rate = rates.growth / (6.022e23 * 2)  # atoms/s -> mol C2H2/m³/s
            sources["C2H2"] = sources.get("C2H2", 0.0) - growth_rate
            sources["H2"] = sources.get("H2", 0.0) + growth_rate * 0.5

        # Oxidation consumes O2/OH, produces CO
        if self._oxidation is not None:
            ox_rate = rates.oxidation / 6.022e23  # atoms/s -> mol/m³/s
            sources["O2"] = sources.get("O2", 0.0) - ox_rate * 0.5
            sources["CO"] = sources.get("CO", 0.0) + ox_rate

        return sources

    def __repr__(self) -> str:
        return f"StochasticSolver(n={self.n_particles}, " f"t={self._total_time:.2e} s, events={self._n_events})"
