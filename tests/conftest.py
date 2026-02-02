"""
Test configuration for pytest.

Provides fixtures and utilities for testing.
"""

import pytest
import numpy as np
from pathlib import Path
import tempfile
import shutil


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test outputs."""
    dirpath = tempfile.mkdtemp()
    yield Path(dirpath)
    shutil.rmtree(dirpath)


@pytest.fixture
def sample_config_dict():
    """Return a sample configuration dictionary."""
    return {
        "name": "Test Simulation",
        "description": "Test configuration",
        "gas": {
            "mechanism": "gri30.yaml",
            "temperature": 1500.0,
            "pressure": 101325.0,
            "composition": {"CH4": 0.05, "O2": 0.21, "N2": 0.74},
        },
        "particles": {
            "enabled": True,
            "max_particles": 1000,
            "min_particles": 100,
        },
        "solver": {
            "duration": 0.001,
            "time_step": 1e-6,
        },
        "output": {
            "directory": "test_output",
            "format": "csv",
        },
    }


@pytest.fixture
def rng():
    """Return a seeded random number generator."""
    return np.random.default_rng(42)
