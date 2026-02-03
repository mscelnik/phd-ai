from pathlib import Path

from sootsim.io import PopulationConfig, SimulationConfig
from sootsim.simulation import run_simulation


def test_run_simulation_writes_csv(tmp_path: Path) -> None:
    config = SimulationConfig(
        name="integration",
        time_end=0.1,
        time_steps=10,
        initial_species={"C2H2": 1.0, "O2": 0.5},
        output_folder=tmp_path,
        population=PopulationConfig(dt=0.01, initial_particles=2),
    )
    result = run_simulation(config)
    target = config.output_folder / config.name
    assert (target / "gas_phase.csv").exists()
    assert (target / "population.csv").exists()
    assert result.snapshots[-1].time <= config.time_end
