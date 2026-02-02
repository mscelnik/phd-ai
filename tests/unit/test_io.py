"""
Unit tests for I/O module.
"""

import pytest
import tempfile
from pathlib import Path
import yaml
import json
import numpy as np

from nanoparticle_simulator.io.config import (
    SimulationConfig,
    GasPhaseConfig,
    ParticleConfig,
    load_config,
    save_config,
    create_default_config,
)
from nanoparticle_simulator.io.output import (
    OutputWriter,
    OutputConfig,
    write_csv,
)
from nanoparticle_simulator.reactor.base import SimulationResult


class TestConfig:
    """Tests for configuration handling."""

    def test_default_config(self):
        """Test default configuration creation."""
        config = create_default_config()

        assert config.name == "Soot Formation Simulation"
        assert config.gas.mechanism == "gri30.yaml"
        assert config.gas.temperature == 1500.0
        assert config.particles.enabled is True

    def test_save_load_yaml(self, temp_dir):
        """Test saving and loading YAML config."""
        config = create_default_config()
        config.name = "Test Config"

        filepath = temp_dir / "config.yaml"
        save_config(config, filepath)

        loaded = load_config(filepath)

        assert loaded.name == "Test Config"
        assert loaded.gas.mechanism == config.gas.mechanism
        assert loaded.gas.temperature == config.gas.temperature

    def test_save_load_json(self, temp_dir):
        """Test saving and loading JSON config."""
        config = create_default_config()
        config.name = "JSON Test"

        filepath = temp_dir / "config.json"
        save_config(config, filepath)

        loaded = load_config(filepath)

        assert loaded.name == "JSON Test"

    def test_load_nonexistent_file(self):
        """Test loading nonexistent file raises error."""
        with pytest.raises(FileNotFoundError):
            load_config("nonexistent_file.yaml")

    def test_config_to_dict(self):
        """Test converting config to dictionary."""
        config = create_default_config()
        data = config.to_dict()

        assert isinstance(data, dict)
        assert "gas" in data
        assert "particles" in data
        assert data["gas"]["mechanism"] == "gri30.yaml"


class TestOutputWriter:
    """Tests for output writing."""

    @pytest.fixture
    def sample_result(self):
        """Create sample simulation result."""
        n_times = 10
        n_species = 3

        return SimulationResult(
            times=np.linspace(0, 0.001, n_times),
            temperatures=np.linspace(1500, 1800, n_times),
            pressures=np.full(n_times, 101325.0),
            species=np.random.rand(n_times, n_species),
            species_names=["CH4", "O2", "N2"],
            n_particles=np.arange(n_times, dtype=np.int64),
            mean_diameter=np.linspace(1e-9, 10e-9, n_times),
            number_density=np.linspace(1e10, 1e12, n_times),
            total_mass=np.linspace(1e-6, 1e-4, n_times),
        )

    def test_write_csv(self, temp_dir, sample_result):
        """Test writing CSV output."""
        config = OutputConfig(
            directory=str(temp_dir),
            prefix="test",
            format="csv",
        )
        writer = OutputWriter(config)

        files = writer.write(sample_result)

        assert len(files) == 2  # gas + particles
        assert all(f.suffix == ".csv" for f in files)
        assert all(f.exists() for f in files)

    def test_write_excel(self, temp_dir, sample_result):
        """Test writing Excel output."""
        config = OutputConfig(
            directory=str(temp_dir),
            prefix="test",
            format="excel",
        )
        writer = OutputWriter(config)

        files = writer.write(sample_result)

        assert len(files) == 1
        assert files[0].suffix == ".xlsx"
        assert files[0].exists()

    def test_write_csv_convenience(self, temp_dir, sample_result):
        """Test convenience CSV writer function."""
        filepath = temp_dir / "output.csv"
        write_csv(sample_result, filepath)

        assert filepath.exists()

    def test_species_filter(self, temp_dir, sample_result):
        """Test species filtering in output."""
        config = OutputConfig(
            directory=str(temp_dir),
            prefix="test",
            format="csv",
            species_filter=["CH4", "O2"],
        )
        writer = OutputWriter(config)

        files = writer.write(sample_result)

        # Check that filtered species are in output
        import pandas as pd

        df = pd.read_csv(files[0])

        assert "Y_CH4" in df.columns
        assert "Y_O2" in df.columns
        assert "Y_N2" not in df.columns
