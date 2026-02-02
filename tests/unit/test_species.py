"""
Unit tests for Species class.
"""

import pytest
from nanoparticle_simulator.chemistry.species import Species


class TestSpecies:
    """Tests for Species class."""

    def test_species_creation(self):
        """Test basic species creation."""
        species = Species(name="CH4", mw=16.043e-3)

        assert species.name == "CH4"
        assert species.mw == pytest.approx(16.043e-3)
        assert species.molar_mass == pytest.approx(16.043e-3)

    def test_species_with_thermodynamics(self):
        """Test species with thermodynamic properties."""
        species = Species(
            name="H2O",
            mw=18.015e-3,
            h_formation=-241826.0,
            s_formation=188.835,
        )

        assert species.h_formation == pytest.approx(-241826.0)
        assert species.s_formation == pytest.approx(188.835)

    def test_species_equality(self):
        """Test species equality based on name."""
        s1 = Species(name="O2", mw=32.0e-3)
        s2 = Species(name="O2", mw=32.0e-3)
        s3 = Species(name="N2", mw=28.0e-3)

        assert s1 == s2
        assert s1 != s3

    def test_species_hash(self):
        """Test species hashing for use in sets/dicts."""
        s1 = Species(name="O2", mw=32.0e-3)
        s2 = Species(name="O2", mw=32.0e-3)

        species_set = {s1, s2}
        assert len(species_set) == 1

    def test_species_repr(self):
        """Test species string representation."""
        species = Species(name="CO2", mw=44.01e-3)
        repr_str = repr(species)

        assert "CO2" in repr_str
        assert "0.0440" in repr_str
