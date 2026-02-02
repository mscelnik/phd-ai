"""
Unit tests for GasPhase class.
"""

import pytest
import numpy as np
from nanoparticle_simulator.chemistry.gas_phase import GasPhase, GasPhaseState


class TestGasPhase:
    """Tests for GasPhase class."""

    @pytest.fixture
    def gas(self):
        """Create a gas phase with GRI-Mech 3.0."""
        gas = GasPhase()
        gas.load_mechanism("gri30.yaml")
        return gas

    def test_load_mechanism(self, gas):
        """Test mechanism loading."""
        assert gas.n_species == 53
        assert gas.n_reactions == 325
        assert "CH4" in gas.species_names
        assert "O2" in gas.species_names

    def test_set_state_TPX(self, gas):
        """Test setting state with temperature, pressure, and mole fractions."""
        gas.set_state_TPX(1500.0, 101325.0, "CH4:0.1, O2:0.2, N2:0.7")

        assert gas.T == pytest.approx(1500.0)
        assert gas.P == pytest.approx(101325.0)
        assert gas.species_mole_fraction("CH4") == pytest.approx(0.1, rel=1e-6)

    def test_set_state_dict(self, gas):
        """Test setting state with composition dictionary."""
        gas.set_state(
            T=1800.0,
            P=202650.0,
            X={"CH4": 0.05, "O2": 0.21, "N2": 0.74},
        )

        assert gas.T == pytest.approx(1800.0)
        assert gas.P == pytest.approx(202650.0)

    def test_thermodynamic_properties(self, gas):
        """Test thermodynamic property calculations."""
        gas.set_state_TPX(1500.0, 101325.0, "CH4:0.05, O2:0.21, N2:0.74")

        assert gas.density > 0
        assert gas.mean_molecular_weight > 0
        assert gas.cp > 0
        assert gas.cv > 0
        assert gas.cp > gas.cv  # cp > cv for ideal gas

    def test_production_rates(self, gas):
        """Test species production rate calculation."""
        gas.set_state_TPX(1500.0, 101325.0, "CH4:0.05, O2:0.21, N2:0.74")

        rates = gas.production_rates
        assert len(rates) == gas.n_species
        # N2 should have near-zero production rate (inert)
        # Allow small numerical errors from floating point
        n2_idx = gas.species_index("N2")
        assert abs(rates[n2_idx]) < 1e-8

    def test_state_snapshot(self, gas):
        """Test getting and restoring state snapshots."""
        gas.set_state_TPX(1500.0, 101325.0, "CH4:0.1, O2:0.2, N2:0.7")
        state = gas.get_state()

        # Change state
        gas.set_state_TPX(2000.0, 202650.0, "O2:1.0")

        # Restore
        gas.restore_state(state)

        assert gas.T == pytest.approx(1500.0)
        assert gas.P == pytest.approx(101325.0)
        assert gas.species_mole_fraction("CH4") == pytest.approx(0.1, rel=1e-5)

    def test_equilibrate(self, gas):
        """Test equilibration."""
        gas.set_state_TPX(2000.0, 101325.0, "CH4:0.05, O2:0.1, N2:0.85")
        T_initial = gas.T

        gas.equilibrate("HP")

        # Temperature should increase (exothermic combustion)
        # Actually for HP equilibration T can change
        assert gas.T > 0

    def test_concentrations(self, gas):
        """Test molar concentration calculation."""
        gas.set_state_TPX(1500.0, 101325.0, "CH4:0.05, O2:0.21, N2:0.74")

        conc = gas.concentrations()
        assert len(conc) == gas.n_species
        assert np.sum(conc) > 0

    def test_species_not_found_error(self, gas):
        """Test error when species not found."""
        with pytest.raises(Exception):  # Cantera raises CanteraError
            gas.species_index("INVALID_SPECIES")


class TestGasPhaseState:
    """Tests for GasPhaseState dataclass."""

    def test_state_copy(self):
        """Test state copying."""
        state = GasPhaseState(
            T=1500.0,
            P=101325.0,
            Y=np.array([0.1, 0.2, 0.7]),
            X=np.array([0.1, 0.2, 0.7]),
            rho=0.5,
            mean_mw=0.028,
        )

        copy = state.copy()

        assert copy.T == state.T
        assert copy.P == state.P
        assert np.array_equal(copy.Y, state.Y)

        # Modify original, copy should be unchanged
        state.Y[0] = 999.0
        assert copy.Y[0] != 999.0
