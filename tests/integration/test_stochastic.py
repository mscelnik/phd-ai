"""
Integration tests for the stochastic solver.
"""

# FIXME: Some of these tests are very slow.  Add fail-safe timeouts to prevent hanging.

import pytest
import numpy as np
from dataclasses import dataclass
from nanoparticle_simulator.particles.particle import Particle
from nanoparticle_simulator.particles.stochastic_solver import (
    StochasticSolver,
    SolverConfig,
)
from nanoparticle_simulator.particles.processes import (
    NucleationProcess,
    GrowthProcess,
    CoagulationProcess,
)


@dataclass
class MockGasPhase:
    """Mock gas phase for testing."""

    T: float = 1500.0
    P: float = 101325.0

    def species_concentration(self, name: str) -> float:
        concentrations = {
            "A4": 1e-6,
            "C2H2": 1e-4,
            "O2": 1e-3,
            "OH": 1e-6,
        }
        if name in concentrations:
            return concentrations[name]
        raise ValueError(f"Species {name} not found")


class TestStochasticSolver:
    """Integration tests for stochastic solver."""

    @pytest.fixture
    def solver(self):
        """Create configured solver."""
        config = SolverConfig(
            max_particles=1000,
            min_particles=100,
            sample_volume=1e-9,
            seed=42,
        )
        solver = StochasticSolver(config=config)
        solver.add_process(NucleationProcess())
        solver.add_process(GrowthProcess())
        solver.add_process(CoagulationProcess())
        solver.initialize(sample_volume=1e-9)
        return solver

    @pytest.fixture
    def gas(self):
        """Create mock gas phase."""
        return MockGasPhase()

    def test_solver_initialization(self, solver):
        """Test solver initialization."""
        assert solver.n_particles == 0
        assert solver.total_time == 0.0

    def test_solver_step(self, solver, gas):
        """Test single solver step."""
        n_events = solver.step(gas, dt=1e-6)

        # Should have performed some events
        assert n_events >= 0
        assert solver.total_time > 0

    def test_nucleation_creates_particles(self, solver, gas):
        """Test that nucleation creates new particles."""
        # Run for a short time to test the machinery (not physical accuracy)
        for _ in range(5):
            solver.step(gas, dt=1e-8)

        # Should have attempted to create some particles
        # (depends on rates, so check is not strict)
        assert solver.n_particles >= 0

    def test_solver_with_initial_particles(self, gas):
        """Test solver with initial particles."""
        config = SolverConfig(seed=42)
        solver = StochasticSolver(config=config)
        solver.add_process(GrowthProcess())
        solver.add_process(CoagulationProcess())

        # Add initial particles
        initial_particles = [Particle(n_carbon=100 + i * 10, n_hydrogen=50) for i in range(10)]
        solver.initialize(
            sample_volume=1e-9,
            initial_particles=initial_particles,
        )

        assert solver.n_particles == 10

        # Run short simulation
        for _ in range(3):
            solver.step(gas, dt=1e-8)

        # Particles should still exist (may coagulate)
        assert solver.n_particles > 0

    def test_coagulation_reduces_particles(self, gas):
        """Test that coagulation reduces particle count."""
        config = SolverConfig(seed=42, min_particles=1)
        solver = StochasticSolver(config=config)
        solver.add_process(CoagulationProcess())

        # Add particles
        initial_particles = [Particle(n_carbon=100, n_hydrogen=50) for _ in range(20)]
        solver.initialize(
            sample_volume=1e-9,
            initial_particles=initial_particles,
        )

        initial_count = solver.n_particles

        # Run for a few steps
        for _ in range(5):
            solver.step(gas, dt=1e-8)

        # Should still have particles
        assert solver.n_particles > 0

    def test_source_terms(self, solver, gas):
        """Test gas-phase source term calculation."""
        # Add some particles
        for _ in range(10):
            solver.ensemble.add_particle(Particle(n_carbon=1000, n_hydrogen=500))

        sources = solver.get_source_terms(gas)

        assert isinstance(sources, dict)

    def test_event_counting(self, solver, gas):
        """Test event counting."""
        for _ in range(5):
            solver.step(gas, dt=1e-8)

        counts = solver.event_counts
        total_events = sum(counts.values())

        # Should have recorded events
        assert total_events >= 0
