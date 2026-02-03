import numpy as np

from sootsim.chemistry import Reaction, integrate_gas_phase


def test_reaction_rate_requires_present_species() -> None:
    reaction = Reaction(
        name="a",
        rate_constant=1.0,
        reactants={"A": 1},
        products={"B": 1},
    )
    assert reaction.rate({"A": 2.0}) > 0.0
    assert reaction.rate({}) == 0.0


def test_gas_phase_integration_reduces_precursors() -> None:
    initial = {"C2H2": 1.5, "O2": 2.0, "CO": 0.0}
    reactions = [
        Reaction(
            name="comb",
            rate_constant=1.0,
            reactants={"C2H2": 1, "O2": 1},
            products={"CO": 2},
        ),
    ]
    result = integrate_gas_phase(initial, reactions, t_span=(0.0, 0.1), steps=5)
    assert "C2H2" in result.species
    assert result.concentrations["C2H2"][-1] <= initial["C2H2"]
    assert result.concentrations["CO"][-1] >= 0.0
    assert np.all(result.time >= 0.0)
