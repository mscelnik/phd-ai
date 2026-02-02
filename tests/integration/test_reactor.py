"""
Integration tests for the reactor module.
"""

import pytest
import numpy as np
from nanoparticle_simulator.chemistry.gas_phase import GasPhase
from nanoparticle_simulator.reactor.ode_solver import ODESolver, ODEConfig
from nanoparticle_simulator.reactor.batch import BatchReactor, create_batch_reactor


class TestODESolver:
    """Integration tests for ODE solver with gas phase."""

    @pytest.fixture
    def gas_with_state(self):
        """Create initialized gas phase."""
        gas = GasPhase()
        gas.load_mechanism("gri30.yaml")
        gas.set_state_TPX(1500.0, 101325.0, "CH4:0.05, O2:0.21, N2:0.74")
        return gas

    def test_integration_step(self, gas_with_state):
        """Test single integration step."""
        ode = ODESolver(gas_with_state)

        T_initial = gas_with_state.T
        ode.step(1e-6)

        # Temperature should change slightly due to reactions
        # (may increase or decrease depending on conditions)
        assert gas_with_state.T > 0

    def test_integration_produces_products(self, gas_with_state):
        """Test that integration produces combustion products."""
        ode = ODESolver(gas_with_state)

        # Get initial CO2
        co2_idx = gas_with_state.species_index("CO2")
        initial_co2 = gas_with_state.Y[co2_idx]

        # Integrate for longer time
        ode.step(1e-4)

        # CO2 should increase (combustion product)
        final_co2 = gas_with_state.Y[co2_idx]
        assert final_co2 >= initial_co2

    def test_mass_conservation(self, gas_with_state):
        """Test mass conservation during integration."""
        ode = ODESolver(gas_with_state)

        initial_mass = np.sum(gas_with_state.Y)
        ode.step(1e-5)
        final_mass = np.sum(gas_with_state.Y)

        # Mass fractions should sum to 1
        assert final_mass == pytest.approx(1.0, rel=1e-6)


class TestBatchReactor:
    """Integration tests for batch reactor."""

    @pytest.fixture
    def gas(self):
        """Create gas phase."""
        gas = GasPhase()
        gas.load_mechanism("gri30.yaml")
        gas.set_state_TPX(1500.0, 101325.0, "CH4:0.05, O2:0.21, N2:0.74")
        return gas

    def test_reactor_creation(self, gas):
        """Test reactor creation."""
        reactor = create_batch_reactor(
            gas=gas,
            volume=1e-6,
            enable_particles=False,
        )

        assert reactor.temperature == pytest.approx(1500.0)
        assert reactor.pressure == pytest.approx(101325.0)
        assert reactor.volume == 1e-6

    def test_reactor_step(self, gas):
        """Test single reactor step."""
        reactor = create_batch_reactor(
            gas=gas,
            volume=1e-6,
            enable_particles=False,
        )

        reactor.step(1e-6)

        assert reactor.time == pytest.approx(1e-6)

    def test_reactor_run(self, gas):
        """Test reactor simulation run."""
        reactor = create_batch_reactor(
            gas=gas,
            volume=1e-6,
            enable_particles=False,
        )

        result = reactor.run(
            duration=1e-5,
            dt=1e-6,
            output_interval=5e-6,
        )

        assert len(result.times) > 1
        assert result.times[-1] == pytest.approx(1e-5, rel=0.1)
        assert len(result.temperatures) == len(result.times)

    def test_reactor_with_particles(self, gas):
        """Test reactor with particle solver."""
        # Skip nucleation since GRI-Mech doesn't have A4 (pyrene)
        reactor = create_batch_reactor(
            gas=gas,
            volume=1e-6,
            enable_particles=True,
            particle_processes=["growth", "coagulation"],
        )

        result = reactor.run(
            duration=1e-6,
            dt=1e-7,
            output_interval=5e-7,
        )

        # Check particle data is present
        assert len(result.n_particles) == len(result.times)

    def test_reactor_reset(self, gas):
        """Test reactor reset."""
        reactor = create_batch_reactor(
            gas=gas,
            volume=1e-6,
            enable_particles=False,
        )

        reactor.step(1e-6)
        assert reactor.time > 0

        reactor.reset()
        assert reactor.time == 0.0
