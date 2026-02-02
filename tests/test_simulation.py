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


def test_gas_phase_solver_run():
    solver = GasPhaseChemistrySolver(["C2H2 + O2 -> CO2 + H2O"])
    y0 = [1.0]
    t_span = (0, 1)
    dt = 0.1
    t, y = solver.run(y0, t_span, dt)
    assert len(t) > 0
    assert y.shape[1] == len(t)


def test_particle_model_run():
    params = {"initial_count": 1000, "growth_rate": 0.01, "coagulation_rate": 0.005}
    model = ParticlePopulationBalanceModel(params)
    history = model.run(10)
    assert len(history) == 11


def test_operator_splitting_simulator_run(tmp_path):
    config = {
        "reactions": ["C2H2 + O2 -> CO2 + H2O"],
        "particles": {"initial_count": 1000, "growth_rate": 0.01, "coagulation_rate": 0.005},
        "simulation": {"time_steps": 10, "dt": 0.1},
    }
    sim = OperatorSplittingSimulator(config)
    initial_conditions = {"chemistry": [1.0]}
    initial_particles = {"count": 1000}
    chem_t, chem_y, particle_history = sim.run(initial_conditions, initial_particles)
    assert len(chem_t) > 0
    assert len(particle_history) == 11
