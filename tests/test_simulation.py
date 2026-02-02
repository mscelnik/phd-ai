import pytest
from src.simulation import (
    SimulationConfig,
    GasPhaseChemistrySolver,
    ParticlePopulationBalanceModel,
    OperatorSplittingSimulator,
)


def test_simulation_config_load():
    config = SimulationConfig("src/input_schema.yaml")
    assert "reactions" in config.config
    assert "particles" in config.config


def test_gas_phase_solver_init():
    solver = GasPhaseChemistrySolver(["C2H2 + O2 -> CO2 + H2O"])
    assert solver.reaction_set


def test_particle_model_init():
    model = ParticlePopulationBalanceModel({"initial_count": 1000})
    assert model.params["initial_count"] == 1000


def test_operator_splitting_simulator_init():
    config = {"reactions": ["C2H2 + O2 -> CO2 + H2O"], "particles": {"initial_count": 1000}}
    sim = OperatorSplittingSimulator(config)
    assert sim.gas_solver
    assert sim.particle_model
