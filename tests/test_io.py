from pathlib import Path

from sootsim.io import SimulationConfig


def test_config_loader(tmp_path: Path) -> None:
    config_yaml = tmp_path / "run.yaml"
    config_yaml.write_text(
        """
name: test-run
time_end: 0.1
time_steps: 5
initial_species:
  C2H2: 1.0
  O2: 2.0
output_folder: outputs
"""
    )
    config = SimulationConfig.load(config_yaml)
    assert config.name == "test-run"
    assert config.time_steps == 5
    assert config.output_folder.name == "outputs"
