import pytest
from src.particle_balance_model import ParticlePopulationBalanceModel


def test_initial_population():
    initial_population = [10, 20, 30]
    model = ParticlePopulationBalanceModel(initial_population, None, None)
    assert (model.population == initial_population).all()


def test_simulation():
    initial_population = [10, 20, 30]
    model = ParticlePopulationBalanceModel(initial_population, None, None)
    model.simulate(steps=10)
    # Placeholder assertion until coagulation/fragmentation logic is implemented
    assert True
