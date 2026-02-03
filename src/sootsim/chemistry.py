"""Gas-phase chemistry solver with a small acetylene combustion mechanism."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping, Sequence

import numpy as np
from scipy.integrate import solve_ivp


@dataclass(frozen=True)
class Reaction:
    name: str
    rate_constant: float
    reactants: Mapping[str, int]
    products: Mapping[str, int]

    def rate(self, concentrations: Mapping[str, float]) -> float:
        """Mass-action rate using a simple deterministic rate law."""
        rate = self.rate_constant
        for species, stoich in self.reactants.items():
            conc = concentrations.get(species, 0.0)
            if conc <= 0.0:
                return 0.0
            rate *= conc**stoich
        return rate


def _collect_species(
    initial: Mapping[str, float], reactions: Iterable[Reaction]
) -> Sequence[str]:
    species = set(initial)
    for reaction in reactions:
        species.update(reaction.reactants)
        species.update(reaction.products)
    return tuple(sorted(species))


@dataclass
class GasPhaseTrajectory:
    time: np.ndarray
    species: Sequence[str]
    concentrations: Mapping[str, np.ndarray]

    def final_concentrations(self) -> Mapping[str, float]:
        return {name: arr[-1] for name, arr in self.concentrations.items()}


def integrate_gas_phase(
    initial_state: Mapping[str, float],
    reactions: Iterable[Reaction],
    t_span: tuple[float, float] = (0.0, 0.5),
    steps: int = 201,
) -> GasPhaseTrajectory:
    """Integrate a very small gas-phase mechanism with operator splitting-friendly output."""
    species = _collect_species(initial_state, reactions)
    y0 = np.array([initial_state.get(name, 0.0) for name in species])

    def derivative(t: float, y: np.ndarray) -> np.ndarray:
        concentrations = dict(zip(species, y))
        delta = {name: 0.0 for name in species}
        for reaction in reactions:
            r_rate = reaction.rate(concentrations)
            if r_rate == 0.0:
                continue
            for name, stoich in reaction.reactants.items():
                delta[name] -= stoich * r_rate
            for name, stoich in reaction.products.items():
                delta[name] += stoich * r_rate
        return np.array([delta[name] for name in species])

    t_eval = np.linspace(t_span[0], t_span[1], steps)
    solution = solve_ivp(
        derivative, t_span, y0, t_eval=t_eval, vectorized=False
    )
    concentrations = {name: solution.y[idx] for idx, name in enumerate(species)}
    return GasPhaseTrajectory(
        time=solution.t, species=species, concentrations=concentrations
    )
