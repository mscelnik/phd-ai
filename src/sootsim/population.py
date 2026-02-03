"""Lightweight Monte Carlo population-balance model for soot kernels."""
from __future__ import annotations

from dataclasses import dataclass, field
from statistics import mean, median
from typing import Iterable

import numpy as np


@dataclass
class Particle:
    id: int
    creation_time: float
    mass: float
    carbon_atoms: int


@dataclass
class PopulationSnapshot:
    time: float
    count: int
    mean_mass: float
    median_mass: float


class MonteCarloPopulation:
    def __init__(
        self,
        initial_particles: int = 4,
        nucleation_coefficient: float = 0.8,
        growth_coefficient: float = 1e-4,
        coagulation_probability: float = 0.2,
        oxidation_fraction: float = 0.01,
        rng: np.random.Generator | None = None,
    ) -> None:
        self.rng = rng or np.random.default_rng()
        self.particles: list[Particle] = []
        self._next_id = 1
        self.nucleation_coefficient = nucleation_coefficient
        self.growth_coefficient = growth_coefficient
        self.coagulation_probability = coagulation_probability
        self.oxidation_fraction = oxidation_fraction
        for _ in range(initial_particles):
            self._nucleate(0.0)

    def _nucleate(self, time: float) -> None:
        particle = Particle(
            id=self._next_id,
            creation_time=time,
            mass=1.0,
            carbon_atoms=6,
        )
        self._next_id += 1
        self.particles.append(particle)

    def _coagulate(self) -> None:
        if len(self.particles) < 2:
            return
        if self.rng.random() > self.coagulation_probability:
            return
        indices = self.rng.choice(len(self.particles), size=2, replace=False)
        first = self.particles[max(indices)]
        second = self.particles[min(indices)]
        first.mass += second.mass
        first.carbon_atoms += second.carbon_atoms
        self.particles.remove(second)

    def _grow(self, acetylene: float, dt: float) -> None:
        for particle in self.particles:
            increment = acetylene * self.growth_coefficient * dt
            particle.mass += increment
            particle.carbon_atoms += int(max(1, increment * 10))

    def _oxidize(self, dt: float) -> None:
        for particle in list(self.particles):
            particle.mass *= 1 - self.oxidation_fraction * dt
            if particle.mass < 0.5:
                self.particles.remove(particle)

    def step(self, acetylene: float, time: float, dt: float) -> None:
        nucleation_rate = min(acetylene * self.nucleation_coefficient, 1.0)
        if self.rng.random() < nucleation_rate * dt:
            self._nucleate(time)
        self._grow(acetylene, dt)
        self._coagulate()
        self._oxidize(dt)

    def simulate(
        self,
        acetylene_values: Iterable[float],
        times: Iterable[float],
        dt: float,
    ) -> list[PopulationSnapshot]:
        snapshots: list[PopulationSnapshot] = []
        for time, acetylene in zip(times, acetylene_values):
            self.step(acetylene, time, dt)
            snapshots.append(self.snapshot(time))
        return snapshots

    def snapshot(self, time: float) -> PopulationSnapshot:
        if not self.particles:
            return PopulationSnapshot(
                time=time, count=0, mean_mass=0.0, median_mass=0.0
            )
        masses = [p.mass for p in self.particles]
        return PopulationSnapshot(
            time=time,
            count=len(self.particles),
            mean_mass=mean(masses),
            median_mass=median(masses),
        )
