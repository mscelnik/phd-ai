import pytest
import numpy as np
from src.gas_phase_solver import GasPhaseChemistrySolver


def test_reaction_rates():
    reaction_mechanism = {"reactions": [{"rate_constant": 1.0, "reactants": [0], "products": [1]}]}
    solver = GasPhaseChemistrySolver(reaction_mechanism)
    concentrations = np.array([1.0, 0.0])
    rates = solver.reaction_rates(0, concentrations)
    assert rates[0] == -1.0
    assert rates[1] == 1.0


def test_solve():
    reaction_mechanism = {"reactions": [{"rate_constant": 1.0, "reactants": [0], "products": [1]}]}
    solver = GasPhaseChemistrySolver(reaction_mechanism)
    initial_concentrations = [1.0, 0.0]
    t_span = (0, 10)
    t_eval = np.linspace(0, 10, 100)
    solution = solver.solve(initial_concentrations, t_span, t_eval)
    assert solution.success
