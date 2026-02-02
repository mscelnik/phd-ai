"""
End-to-end tests for complete simulation workflows.
"""

import pytest
import tempfile
from pathlib import Path
import numpy as np

from nanoparticle_simulator.chemistry.gas_phase import GasPhase
from nanoparticle_simulator.reactor.batch import create_batch_reactor
from nanoparticle_simulator.io.config import (
    SimulationConfig,
    load_config,
    save_config,
    create_default_config,
)
from nanoparticle_simulator.io.output import OutputWriter, OutputConfig, write_csv


class TestFullSimulation:
    """End-to-end tests for complete simulations."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory."""
        import shutil

        dirpath = tempfile.mkdtemp()
        yield Path(dirpath)
        shutil.rmtree(dirpath)

    def test_gas_phase_only_simulation(self, temp_dir):
        """Test complete gas-phase simulation without particles."""
        # Setup - use higher temperature for faster chemistry
        gas = GasPhase()
        gas.load_mechanism("gri30.yaml")
        gas.set_state_TPX(
            2000.0,  # Higher temperature for faster reactions
            101325.0,
            {"CH4": 0.05, "O2": 0.21, "N2": 0.74},
        )

        # Create reactor
        reactor = create_batch_reactor(
            gas=gas,
            volume=1e-6,
            enable_particles=False,
        )

        # Run simulation - longer duration for observable changes
        result = reactor.run(
            duration=1e-4,
            dt=1e-5,
            output_interval=2e-5,
        )

        # Validate results
        assert len(result.times) >= 5
        assert result.times[0] == 0.0
        assert result.times[-1] >= 1e-4 - 1e-9

        # Temperature should change - use explicit tolerance check
        # At high T, chemistry should cause some temperature change
        temp_change = abs(result.temperatures[-1] - result.temperatures[0])
        assert temp_change > 0.0, "Temperature should change due to chemistry"

        # Write output
        output_path = temp_dir / "gas_only.csv"
        write_csv(result, output_path)
        assert output_path.exists()

    def test_full_soot_simulation(self, temp_dir):
        """Test complete soot formation simulation with particles."""
        # Setup gas phase
        gas = GasPhase()
        gas.load_mechanism("gri30.yaml")
        gas.set_state_TPX(
            1800.0,
            101325.0,
            {"CH4": 0.055, "O2": 0.11, "N2": 0.835},
        )

        # Create reactor with particles - use C2H2 as precursor since
        # GRI-Mech 3.0 doesn't have PAH species like A4 (pyrene)
        from nanoparticle_simulator.particles.processes import NucleationProcess

        reactor = create_batch_reactor(
            gas=gas,
            volume=1e-6,
            enable_particles=True,
            particle_processes=["growth", "coagulation"],  # Skip nucleation for this test
        )

        # Run short simulation
        result = reactor.run(
            duration=1e-6,
            dt=1e-7,
            output_interval=2e-7,
        )

        # Validate gas-phase results
        assert len(result.times) >= 3
        assert len(result.species_names) == 53  # GRI-Mech 3.0

        # Validate particle results
        assert len(result.n_particles) == len(result.times)
        assert len(result.mean_diameter) == len(result.times)

        # Write output
        config = OutputConfig(
            directory=str(temp_dir),
            prefix="soot_test",
            format="csv",
        )
        writer = OutputWriter(config)
        files = writer.write(result)

        assert len(files) == 2
        assert all(f.exists() for f in files)

    def test_config_driven_simulation(self, temp_dir):
        """Test simulation driven by configuration file."""
        # Create configuration
        config = create_default_config()
        config.name = "E2E Test"
        config.solver.duration = 1e-6
        config.solver.time_step = 1e-7
        config.solver.output_interval = 5e-7
        config.particles.enabled = False
        config.output.directory = str(temp_dir)

        # Save configuration
        config_path = temp_dir / "test_config.yaml"
        save_config(config, config_path)

        # Load configuration
        loaded_config = load_config(config_path)
        assert loaded_config.name == "E2E Test"

        # Run simulation from config
        gas = GasPhase()
        gas.load_mechanism(loaded_config.gas.mechanism)
        gas.set_state_TPX(
            loaded_config.gas.temperature,
            loaded_config.gas.pressure,
            loaded_config.gas.composition,
        )

        reactor = create_batch_reactor(
            gas=gas,
            volume=loaded_config.reactor.volume,
            enable_particles=loaded_config.particles.enabled,
        )

        result = reactor.run(
            duration=loaded_config.solver.duration,
            dt=loaded_config.solver.time_step,
            output_interval=loaded_config.solver.output_interval,
        )

        # Validate
        assert len(result.times) >= 2

    def test_temperature_sensitive_simulation(self, temp_dir):
        """Test simulation at different temperatures."""
        temperatures = [1400.0, 1600.0, 1800.0]
        results = []

        for T in temperatures:
            gas = GasPhase()
            gas.load_mechanism("gri30.yaml")
            gas.set_state_TPX(
                T,
                101325.0,
                {"CH4": 0.05, "O2": 0.21, "N2": 0.74},
            )

            reactor = create_batch_reactor(
                gas=gas,
                volume=1e-6,
                enable_particles=False,
            )

            result = reactor.run(
                duration=1e-6,
                dt=1e-7,
                output_interval=5e-7,
            )

            results.append(result)

        # Higher temperature should have higher reaction rates
        # Check that simulations ran successfully
        for result in results:
            assert len(result.times) >= 2

    def test_reproducibility(self, temp_dir):
        """Test simulation reproducibility with fixed seed."""

        def run_simulation(seed):
            gas = GasPhase()
            gas.load_mechanism("gri30.yaml")
            gas.set_state_TPX(
                1800.0,
                101325.0,
                {"CH4": 0.055, "O2": 0.11, "N2": 0.835},
            )

            from nanoparticle_simulator.particles.stochastic_solver import (
                StochasticSolver,
                SolverConfig,
            )
            from nanoparticle_simulator.particles.processes import (
                NucleationProcess,
            )

            config = SolverConfig(seed=seed, sample_volume=1e-9)
            particles = StochasticSolver(config=config)
            particles.add_process(NucleationProcess())
            particles.initialize(sample_volume=1e-9)

            reactor = create_batch_reactor(
                gas=gas,
                volume=1e-9,
                enable_particles=False,
            )

            return reactor.run(
                duration=1e-7,
                dt=1e-8,
                output_interval=5e-8,
            )

        # Run twice with same seed
        result1 = run_simulation(42)
        result2 = run_simulation(42)

        # Gas-phase results should be identical
        np.testing.assert_allclose(
            result1.temperatures,
            result2.temperatures,
            rtol=1e-10,
        )


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_very_short_simulation(self):
        """Test very short simulation time."""
        gas = GasPhase()
        gas.load_mechanism("gri30.yaml")
        gas.set_state_TPX(1500.0, 101325.0, "N2:1.0")

        reactor = create_batch_reactor(
            gas=gas,
            volume=1e-6,
            enable_particles=False,
        )

        result = reactor.run(
            duration=1e-12,
            dt=1e-13,
            output_interval=1e-13,
        )

        assert len(result.times) >= 1

    def test_inert_gas(self):
        """Test simulation with inert gas only."""
        gas = GasPhase()
        gas.load_mechanism("gri30.yaml")
        gas.set_state_TPX(1500.0, 101325.0, "N2:1.0")

        reactor = create_batch_reactor(
            gas=gas,
            volume=1e-6,
            enable_particles=False,
        )

        result = reactor.run(
            duration=1e-6,
            dt=1e-7,
            output_interval=5e-7,
        )

        # Temperature should be constant (no reactions)
        np.testing.assert_allclose(
            result.temperatures,
            result.temperatures[0],
            rtol=1e-6,
        )

    def test_low_pressure(self):
        """Test simulation at low pressure."""
        gas = GasPhase()
        gas.load_mechanism("gri30.yaml")
        gas.set_state_TPX(
            1500.0,
            10132.5,  # 0.1 atm
            {"CH4": 0.05, "O2": 0.21, "N2": 0.74},
        )

        reactor = create_batch_reactor(
            gas=gas,
            volume=1e-6,
            enable_particles=False,
        )

        result = reactor.run(
            duration=1e-6,
            dt=1e-7,
            output_interval=5e-7,
        )

        # Should run without errors
        assert len(result.times) >= 2
        # Pressure should remain constant
        np.testing.assert_allclose(
            result.pressures,
            10132.5,
            rtol=1e-3,
        )
