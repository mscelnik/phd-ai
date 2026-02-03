"""Configuration loading helpers for the simulation models."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

import yaml


@dataclass
class PopulationConfig:
    dt: float = 0.002
    initial_particles: int = 6
    nucleation_coefficient: float = 0.8
    growth_coefficient: float = 1e-4
    coagulation_probability: float = 0.25
    oxidation_fraction: float = 0.01


@dataclass
class SimulationConfig:
    name: str
    time_end: float
    time_steps: int
    initial_species: Mapping[str, float]
    output_folder: Path
    population: PopulationConfig

    @classmethod
    def load(cls, path: Path) -> "SimulationConfig":
        raw = yaml.safe_load(path.read_text())
        pop_raw = raw.get("population", {})
        population = PopulationConfig(
            **{**PopulationConfig().__dict__, **pop_raw}
        )
        return cls(
            name=raw["name"],
            time_end=float(raw.get("time_end", 0.5)),
            time_steps=int(raw.get("time_steps", 201)),
            initial_species=raw.get("initial_species", {}),
            output_folder=Path(raw.get("output_folder", "outputs")),
            population=population,
        )
