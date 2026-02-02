"""
Configuration file handling.

Reads and writes simulation configuration in YAML/JSON format.
"""

import json
import logging
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional, Any, Union

import yaml

logger = logging.getLogger(__name__)


@dataclass
class GasPhaseConfig:
    """
    Gas-phase configuration.

    Attributes:
        mechanism: Mechanism file path or name
        temperature: Initial temperature (K)
        pressure: Initial pressure (Pa)
        composition: Initial composition (mole fractions)
    """

    mechanism: str = "gri30.yaml"
    temperature: float = 1500.0
    pressure: float = 101325.0
    composition: dict[str, float] = field(
        default_factory=lambda: {
            "CH4": 0.05,
            "O2": 0.21,
            "N2": 0.74,
        }
    )


@dataclass
class ParticleConfig:
    """
    Particle solver configuration.

    Attributes:
        enabled: Enable particle solver
        max_particles: Maximum particles in ensemble
        min_particles: Minimum particles before doubling
        nucleation_enabled: Enable nucleation
        growth_enabled: Enable surface growth
        coagulation_enabled: Enable coagulation
        oxidation_enabled: Enable oxidation
        precursor_species: Nucleation precursor species name
    """

    enabled: bool = True
    max_particles: int = 4096
    min_particles: int = 512
    nucleation_enabled: bool = True
    growth_enabled: bool = True
    coagulation_enabled: bool = True
    oxidation_enabled: bool = True
    precursor_species: str = "A4"


@dataclass
class ReactorConfig:
    """
    Reactor configuration.

    Attributes:
        reactor_type: Type of reactor ("batch", "plug_flow", etc.)
        volume: Reactor volume (m³)
        constant_pressure: Constant pressure (True) or volume (False)
        energy_enabled: Solve energy equation
        splitting_type: Operator splitting ("strang", "lie", "predictor")
    """

    reactor_type: str = "batch"
    volume: float = 1.0e-6
    constant_pressure: bool = True
    energy_enabled: bool = True
    splitting_type: str = "strang"


@dataclass
class SolverConfig:
    """
    Solver configuration.

    Attributes:
        duration: Simulation duration (s)
        time_step: Integration time step (s)
        output_interval: Output interval (s)
        integrator: ODE integrator ("bdf", "radau", "lsoda")
        rtol: Relative tolerance
        atol: Absolute tolerance
        random_seed: Random seed for reproducibility
    """

    duration: float = 0.001
    time_step: float = 1e-6
    output_interval: float = 1e-5
    integrator: str = "bdf"
    rtol: float = 1e-6
    atol: float = 1e-12
    random_seed: Optional[int] = None


@dataclass
class OutputConfig:
    """
    Output configuration.

    Attributes:
        directory: Output directory
        prefix: Output file prefix
        format: Output format ("csv", "excel", "both")
        save_states: Save full reactor states
        species_filter: List of species to output (None for all)
    """

    directory: str = "output"
    prefix: str = "simulation"
    format: str = "csv"
    save_states: bool = False
    species_filter: Optional[list[str]] = None


@dataclass
class SimulationConfig:
    """
    Complete simulation configuration.

    Combines all configuration sections.
    """

    name: str = "Soot Formation Simulation"
    description: str = ""
    gas: GasPhaseConfig = field(default_factory=GasPhaseConfig)
    particles: ParticleConfig = field(default_factory=ParticleConfig)
    reactor: ReactorConfig = field(default_factory=ReactorConfig)
    solver: SolverConfig = field(default_factory=SolverConfig)
    output: OutputConfig = field(default_factory=OutputConfig)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


def load_config(filepath: Union[str, Path]) -> SimulationConfig:
    """
    Load configuration from YAML or JSON file.

    Args:
        filepath: Path to configuration file

    Returns:
        Simulation configuration

    Raises:
        FileNotFoundError: If file does not exist
        ValueError: If file format is not supported
    """
    filepath = Path(filepath)

    if not filepath.exists():
        raise FileNotFoundError(f"Configuration file not found: {filepath}")

    with open(filepath, "r") as f:
        if filepath.suffix in [".yaml", ".yml"]:
            data = yaml.safe_load(f)
        elif filepath.suffix == ".json":
            data = json.load(f)
        else:
            raise ValueError(f"Unsupported file format: {filepath.suffix}")

    logger.info(f"Loaded configuration from {filepath}")
    return _dict_to_config(data)


def save_config(config: SimulationConfig, filepath: Union[str, Path]) -> None:
    """
    Save configuration to YAML or JSON file.

    Args:
        config: Simulation configuration
        filepath: Output file path
    """
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)

    data = config.to_dict()

    with open(filepath, "w") as f:
        if filepath.suffix in [".yaml", ".yml"]:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        elif filepath.suffix == ".json":
            json.dump(data, f, indent=2)
        else:
            raise ValueError(f"Unsupported file format: {filepath.suffix}")

    logger.info(f"Saved configuration to {filepath}")


def _dict_to_config(data: dict[str, Any]) -> SimulationConfig:
    """
    Convert dictionary to SimulationConfig.

    Args:
        data: Configuration dictionary

    Returns:
        Simulation configuration
    """
    gas_data = data.get("gas", {})
    particles_data = data.get("particles", {})
    reactor_data = data.get("reactor", {})
    solver_data = data.get("solver", {})
    output_data = data.get("output", {})

    return SimulationConfig(
        name=data.get("name", "Simulation"),
        description=data.get("description", ""),
        gas=GasPhaseConfig(**gas_data),
        particles=ParticleConfig(**particles_data),
        reactor=ReactorConfig(**reactor_data),
        solver=SolverConfig(**solver_data),
        output=OutputConfig(**output_data),
    )


def create_default_config() -> SimulationConfig:
    """
    Create default configuration.

    Returns:
        Default simulation configuration
    """
    return SimulationConfig()
