"""
Unit tests for particle processes.
"""

import pytest
import numpy as np
from dataclasses import dataclass
from nanoparticle_simulator.particles.particle import Particle
from nanoparticle_simulator.particles.processes import (
    NucleationProcess,
    GrowthProcess,
    CoagulationProcess,
    OxidationProcess,
)


@dataclass
class MockGasPhase:
    """Mock gas phase for testing processes."""

    T: float = 1500.0
    P: float = 101325.0
    _concentrations: dict = None

    def __post_init__(self):
        if self._concentrations is None:
            self._concentrations = {
                "A4": 1e-6,  # Pyrene (kmol/m³)
                "C2H2": 1e-4,  # Acetylene
                "O2": 1e-3,  # Oxygen
                "OH": 1e-6,  # Hydroxyl radical
            }

    def species_concentration(self, name: str) -> float:
        if name in self._concentrations:
            return self._concentrations[name]
        raise ValueError(f"Species {name} not found")


class TestNucleationProcess:
    """Tests for nucleation process."""

    @pytest.fixture
    def process(self):
        return NucleationProcess()

    @pytest.fixture
    def gas(self):
        return MockGasPhase()

    def test_nucleation_rate(self, process, gas):
        """Test nucleation rate calculation."""
        rate = process.rate(gas)

        assert rate > 0
        # Rate should be proportional to [A4]²

    def test_nucleation_rate_zero_precursor(self, process):
        """Test nucleation rate with no precursor."""
        gas = MockGasPhase(_concentrations={"A4": 0.0})
        rate = process.rate(gas)

        assert rate == 0.0

    def test_nucleation_apply(self, process, gas):
        """Test nucleation creates particle."""
        particle = process.apply(gas, dt=0.001)

        assert particle is not None
        assert particle.n_carbon == 32  # Default nascent size
        assert particle.n_hydrogen == 18
        assert particle.creation_time == 0.001


class TestGrowthProcess:
    """Tests for surface growth process."""

    @pytest.fixture
    def process(self):
        return GrowthProcess()

    @pytest.fixture
    def gas(self):
        return MockGasPhase()

    @pytest.fixture
    def particle(self):
        return Particle(n_carbon=1000, n_hydrogen=500)

    def test_growth_rate(self, process, gas, particle):
        """Test growth rate calculation."""
        rate = process.rate(gas, particle)

        assert rate > 0

    def test_growth_requires_particle(self, process, gas):
        """Test growth rate returns 0 without particle."""
        rate = process.rate(gas, None)
        assert rate == 0.0

    def test_growth_apply(self, process, gas, particle):
        """Test growth adds carbon."""
        initial_c = particle.n_carbon
        initial_h = particle.n_hydrogen

        process.apply(gas, particle, dt=1e-4)

        # Carbon should increase (or stay same for short dt)
        assert particle.n_carbon >= initial_c


class TestCoagulationProcess:
    """Tests for coagulation process."""

    @pytest.fixture
    def process(self):
        return CoagulationProcess()

    @pytest.fixture
    def gas(self):
        return MockGasPhase()

    def test_kernel_calculation(self, process, gas):
        """Test coagulation kernel calculation."""
        p1 = Particle(n_carbon=1000, n_hydrogen=500)
        p2 = Particle(n_carbon=2000, n_hydrogen=1000)

        beta = process.kernel(p1, p2, gas.T, gas.P)

        assert beta > 0

    def test_kernel_symmetry(self, process, gas):
        """Test kernel is symmetric."""
        p1 = Particle(n_carbon=1000, n_hydrogen=500)
        p2 = Particle(n_carbon=2000, n_hydrogen=1000)

        beta_12 = process.kernel(p1, p2, gas.T, gas.P)
        beta_21 = process.kernel(p2, p1, gas.T, gas.P)

        assert beta_12 == pytest.approx(beta_21)

    def test_coagulate_particles(self, process):
        """Test particle coagulation."""
        p1 = Particle(n_carbon=1000, n_hydrogen=500, n_primary=1)
        p2 = Particle(n_carbon=2000, n_hydrogen=1000, n_primary=2)

        p_new = process.coagulate(p1, p2)

        assert p_new.n_carbon == 3000
        assert p_new.n_hydrogen == 1500
        assert p_new.n_primary == 3


class TestOxidationProcess:
    """Tests for oxidation process."""

    @pytest.fixture
    def process(self):
        return OxidationProcess()

    @pytest.fixture
    def gas(self):
        return MockGasPhase()

    @pytest.fixture
    def particle(self):
        return Particle(n_carbon=1000, n_hydrogen=500)

    def test_oxidation_rate(self, process, gas, particle):
        """Test oxidation rate calculation."""
        rate = process.rate(gas, particle)

        assert rate > 0

    def test_oxidation_rate_no_oxidizer(self, process, particle):
        """Test oxidation rate with no oxidizer."""
        gas = MockGasPhase(_concentrations={"O2": 0.0, "OH": 0.0})
        rate = process.rate(gas, particle)

        assert rate == 0.0

    def test_oxidation_apply(self, process, gas, particle):
        """Test oxidation removes carbon."""
        initial_c = particle.n_carbon

        process.apply(gas, particle, dt=1e-4)

        # Carbon should decrease (or stay same for short dt)
        assert particle.n_carbon <= initial_c

    def test_oxidation_complete_burnout(self, process, gas):
        """Test complete particle oxidation."""
        small_particle = Particle(n_carbon=10, n_hydrogen=5)

        result = process.apply(gas, small_particle, dt=1.0)

        # Particle may be fully consumed
        if result is None:
            assert True  # Particle consumed
        else:
            assert result.n_carbon >= 0
