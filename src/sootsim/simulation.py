"""Orchestrate chemistry and particle population models into a full run."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from .chemistry import GasPhaseTrajectory, Reaction, integrate_gas_phase
from .io import SimulationConfig, PopulationConfig
from .population import MonteCarloPopulation, PopulationSnapshot


@dataclass
class SimulationResult:
    config: SimulationConfig
    gas_phase: GasPhaseTrajectory
    snapshots: list[PopulationSnapshot]


def _default_reactions() -> list[Reaction]:
    return [
        Reaction(
            name="C2H2_pyrolysis",
            rate_constant=2.1,
            reactants={"C2H2": 1},
            products={"C": 1, "H2": 1},
        ),
        Reaction(
            name="oxidation",
            rate_constant=1.6,
            reactants={"C": 1, "O2": 0.5},
            products={"CO": 1},
        ),
        Reaction(
            name="acetylene_combustion",
            rate_constant=0.9,
            reactants={"C2H2": 1, "O2": 1},
            products={"CO": 2, "H2": 1},
        ),
    ]


def run_simulation(config: SimulationConfig) -> SimulationResult:
    reactions = _default_reactions()
    gas_phase = integrate_gas_phase(
        config.initial_species,
        reactions,
        t_span=(0.0, config.time_end),
        steps=config.time_steps,
    )
    acetylene_profile = gas_phase.concentrations.get(
        "C2H2", [0.0] * len(gas_phase.time)
    )
    population_sim = MonteCarloPopulation(
        initial_particles=config.population.initial_particles,
        nucleation_coefficient=config.population.nucleation_coefficient,
        growth_coefficient=config.population.growth_coefficient,
        coagulation_probability=config.population.coagulation_probability,
        oxidation_fraction=config.population.oxidation_fraction,
    )
    snapshots = population_sim.simulate(
        acetylene_profile, gas_phase.time, config.population.dt
    )
    outputs_path = config.output_folder / config.name
    outputs_path.mkdir(parents=True, exist_ok=True)
    _write_gas_phase(outputs_path / "gas_phase.csv", gas_phase)
    _write_population(outputs_path / "population.csv", snapshots)
    return SimulationResult(
        config=config, gas_phase=gas_phase, snapshots=snapshots
    )


def _write_gas_phase(path: Path, trajectory: GasPhaseTrajectory) -> None:
    header = ["time"] + list(trajectory.species)
    rows = []
    for idx, time in enumerate(trajectory.time):
        row = [f"{time:.5f}"] + [
            f"{trajectory.concentrations[name][idx]:.6f}"
            for name in trajectory.species
        ]
        rows.append(row)
    _write_csv(path, header, rows)


def _write_population(
    path: Path, snapshots: Iterable[PopulationSnapshot]
) -> None:
    header = ["time", "particle_count", "mean_mass", "median_mass"]
    rows = [
        [
            f"{s.time:.5f}",
            str(s.count),
            f"{s.mean_mass:.6f}",
            f"{s.median_mass:.6f}",
        ]
        for s in snapshots
    ]
    _write_csv(path, header, rows)


def _write_csv(
    path: Path, header: Iterable[str], rows: Iterable[Iterable[str]]
) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        handle.write(",".join(header))
        handle.write("\n")
        for row in rows:
            handle.write(",".join(row))
            handle.write("\n")
