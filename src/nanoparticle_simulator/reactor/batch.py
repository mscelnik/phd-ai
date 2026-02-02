"""
Batch reactor model.

Implements a constant-volume or constant-pressure batch reactor
with coupled gas-phase chemistry and particle dynamics.
"""

import logging
from dataclasses import dataclass
from typing import Optional, Callable

import numpy as np
from numpy.typing import NDArray

from nanoparticle_simulator.chemistry.gas_phase import GasPhase
from nanoparticle_simulator.particles.stochastic_solver import StochasticSolver
from nanoparticle_simulator.particles.processes import (
    NucleationProcess,
    GrowthProcess,
    CoagulationProcess,
    OxidationProcess,
)
from nanoparticle_simulator.reactor.base import (
    ReactorBase,
    ReactorState,
    SimulationResult,
)
from nanoparticle_simulator.reactor.ode_solver import ODESolver, ODEConfig
from nanoparticle_simulator.reactor.splitting import (
    OperatorSplitter,
    StrangSplitter,
    SplittingType,
    SplittingConfig,
    create_splitter,
)

logger = logging.getLogger(__name__)


@dataclass
class BatchReactorConfig:
    """
    Configuration for batch reactor.

    Attributes:
        constant_pressure: Constant pressure (True) or volume (False)
        energy_enabled: Solve energy equation
        splitting_type: Operator splitting scheme
        ode_config: ODE solver configuration
        splitting_config: Splitting configuration
    """

    constant_pressure: bool = True
    energy_enabled: bool = True
    splitting_type: SplittingType = SplittingType.STRANG
    ode_config: Optional[ODEConfig] = None
    splitting_config: Optional[SplittingConfig] = None


class BatchReactor(ReactorBase):
    """
    Batch (closed) reactor model.

    Models a homogeneous batch reactor with:
    - Detailed gas-phase chemistry
    - Particle nucleation, growth, coagulation, and oxidation
    - Operator-split coupling

    Example:
        >>> gas = GasPhase()
        >>> gas.load_mechanism("gri30.yaml")
        >>> gas.set_state_TPX(1500, 101325, "CH4:0.1, O2:0.2, N2:0.7")
        >>>
        >>> reactor = BatchReactor(gas)
        >>> result = reactor.run(duration=0.001, dt=1e-6)
    """

    def __init__(
        self,
        gas: GasPhase,
        particles: Optional[StochasticSolver] = None,
        volume: float = 1.0e-6,
        config: Optional[BatchReactorConfig] = None,
    ) -> None:
        """
        Initialize batch reactor.

        Args:
            gas: Gas-phase chemistry
            particles: Particle solver (optional)
            volume: Reactor volume (m³)
            config: Reactor configuration
        """
        super().__init__(gas, particles, volume)

        self._config = config or BatchReactorConfig()

        # Create ODE solver
        self._ode = ODESolver(
            gas,
            config=self._config.ode_config,
            energy_enabled=self._config.energy_enabled,
            constant_pressure=self._config.constant_pressure,
        )

        # Create operator splitter
        self._splitter = create_splitter(
            self._config.splitting_type,
            gas,
            self._ode,
            particles,
            self._config.splitting_config,
        )

    @property
    def splitter(self) -> OperatorSplitter:
        """Return operator splitter."""
        return self._splitter

    def step(self, dt: float) -> None:
        """
        Advance reactor by one time step.

        Uses operator splitting to couple gas and particle phases.

        Args:
            dt: Time step (s)
        """
        self._splitter.step(dt)
        self._time += dt

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
            dt: Integration time step (s)
            output_interval: Interval for saving output (s)
            callback: Optional callback after each output

        Returns:
            Simulation results
        """
        if output_interval is None:
            output_interval = dt

        # Calculate number of steps
        n_steps = int(np.ceil(duration / dt))
        n_outputs = int(np.ceil(duration / output_interval)) + 1

        # Initialize result arrays
        times = np.zeros(n_outputs)
        temperatures = np.zeros(n_outputs)
        pressures = np.zeros(n_outputs)
        species = np.zeros((n_outputs, self._gas.n_species))
        n_particles = np.zeros(n_outputs, dtype=np.int64)
        mean_diameter = np.zeros(n_outputs)
        number_density = np.zeros(n_outputs)
        total_mass = np.zeros(n_outputs)
        states: list[ReactorState] = []

        # Save initial state
        output_idx = 0
        self._save_state(
            output_idx, times, temperatures, pressures, species, n_particles, mean_diameter, number_density, total_mass
        )

        if callback is not None:
            callback(self.get_state())

        # Time stepping
        next_output_time = output_interval
        output_idx = 1

        for i in range(n_steps):
            # Take a step
            self.step(dt)

            # Check if output is due
            if self._time >= next_output_time - 1e-12:
                self._save_state(
                    output_idx,
                    times,
                    temperatures,
                    pressures,
                    species,
                    n_particles,
                    mean_diameter,
                    number_density,
                    total_mass,
                )

                state = self.get_state()
                states.append(state)

                if callback is not None:
                    callback(state)

                next_output_time += output_interval
                output_idx += 1

                # Log progress
                progress = 100.0 * self._time / duration
                logger.info(f"Progress: {progress:.1f}%, t={self._time:.2e} s, " f"T={self.temperature:.1f} K")

        # Trim arrays to actual size
        times = times[:output_idx]
        temperatures = temperatures[:output_idx]
        pressures = pressures[:output_idx]
        species = species[:output_idx]
        n_particles = n_particles[:output_idx]
        mean_diameter = mean_diameter[:output_idx]
        number_density = number_density[:output_idx]
        total_mass = total_mass[:output_idx]

        return SimulationResult(
            times=times,
            temperatures=temperatures,
            pressures=pressures,
            species=species,
            species_names=self._gas.species_names,
            n_particles=n_particles,
            mean_diameter=mean_diameter,
            number_density=number_density,
            total_mass=total_mass,
            states=states,
        )

    def _save_state(
        self,
        idx: int,
        times: NDArray[np.float64],
        temperatures: NDArray[np.float64],
        pressures: NDArray[np.float64],
        species: NDArray[np.float64],
        n_particles: NDArray[np.int64],
        mean_diameter: NDArray[np.float64],
        number_density: NDArray[np.float64],
        total_mass: NDArray[np.float64],
    ) -> None:
        """Save current state to arrays."""
        times[idx] = self._time
        temperatures[idx] = self.temperature
        pressures[idx] = self.pressure
        species[idx] = self._gas.Y

        if self._particles is not None:
            stats = self._particles.ensemble.get_statistics()
            n_particles[idx] = stats.n_particles
            mean_diameter[idx] = stats.mean_diameter
            number_density[idx] = stats.number_density
            total_mass[idx] = stats.total_mass


def create_batch_reactor(
    gas: GasPhase,
    volume: float = 1.0e-6,
    enable_particles: bool = True,
    particle_processes: Optional[list[str]] = None,
    config: Optional[BatchReactorConfig] = None,
) -> BatchReactor:
    """
    Factory function to create a batch reactor.

    Args:
        gas: Gas-phase chemistry
        volume: Reactor volume (m³)
        enable_particles: Enable particle solver
        particle_processes: List of process names to enable
                          ["nucleation", "growth", "coagulation", "oxidation"]
        config: Reactor configuration

    Returns:
        Configured batch reactor
    """
    particles = None

    if enable_particles:
        from nanoparticle_simulator.particles.stochastic_solver import (
            StochasticSolver,
            SolverConfig,
        )

        solver_config = SolverConfig(sample_volume=volume)
        particles = StochasticSolver(config=solver_config)
        particles.initialize(sample_volume=volume)

        # Add processes
        if particle_processes is None:
            particle_processes = ["nucleation", "growth", "coagulation", "oxidation"]

        if "nucleation" in particle_processes:
            particles.add_process(NucleationProcess())
        if "growth" in particle_processes:
            particles.add_process(GrowthProcess())
        if "coagulation" in particle_processes:
            particles.add_process(CoagulationProcess())
        if "oxidation" in particle_processes:
            particles.add_process(OxidationProcess())

    return BatchReactor(gas, particles, volume, config)
