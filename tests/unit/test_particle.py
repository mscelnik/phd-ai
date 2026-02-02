"""
Unit tests for Particle class.
"""

import pytest
import numpy as np
from nanoparticle_simulator.particles.particle import (
    Particle,
    create_nascent_particle,
    C_MASS,
    H_MASS,
    AVOGADRO,
)


class TestParticle:
    """Tests for Particle class."""

    def test_particle_creation(self):
        """Test basic particle creation."""
        p = Particle(n_carbon=100, n_hydrogen=50)

        assert p.n_carbon == 100
        assert p.n_hydrogen == 50
        assert p.n_primary == 1
        assert p.is_valid

    def test_particle_mass(self):
        """Test particle mass calculation."""
        p = Particle(n_carbon=100, n_hydrogen=0)

        expected_mass = 100 * C_MASS / AVOGADRO
        assert p.mass == pytest.approx(expected_mass)

    def test_particle_with_hydrogen(self):
        """Test particle mass with hydrogen."""
        p = Particle(n_carbon=100, n_hydrogen=50)

        expected_mass = (100 * C_MASS + 50 * H_MASS) / AVOGADRO
        assert p.mass == pytest.approx(expected_mass)

    def test_particle_diameter(self):
        """Test diameter calculation."""
        p = Particle(n_carbon=1000, n_hydrogen=0)

        # Diameter should be positive and reasonable (nanometer scale)
        assert p.diameter > 0
        assert p.diameter < 1e-6  # Less than 1 micron

    def test_particle_surface_area(self):
        """Test surface area calculation."""
        p = Particle(n_carbon=1000, n_hydrogen=0)

        assert p.surface_area > 0
        # Surface area should scale with diameter squared
        d = p.diameter
        expected_sa = np.pi * d**2
        assert p.surface_area == pytest.approx(expected_sa, rel=0.1)

    def test_c_to_h_ratio(self):
        """Test C/H ratio calculation."""
        p = Particle(n_carbon=100, n_hydrogen=50)
        assert p.c_to_h_ratio == 2.0

        p_no_h = Particle(n_carbon=100, n_hydrogen=0)
        assert p_no_h.c_to_h_ratio == float("inf")

    def test_add_carbon(self):
        """Test adding carbon atoms."""
        p = Particle(n_carbon=100, n_hydrogen=50)
        p.add_carbon(10)

        assert p.n_carbon == 110

    def test_add_hydrogen(self):
        """Test adding hydrogen atoms."""
        p = Particle(n_carbon=100, n_hydrogen=50)
        p.add_hydrogen(5)

        assert p.n_hydrogen == 55

    def test_remove_carbon(self):
        """Test removing carbon atoms."""
        p = Particle(n_carbon=100, n_hydrogen=50)

        success = p.remove_carbon(10)
        assert success
        assert p.n_carbon == 90

        # Try to remove more than available
        success = p.remove_carbon(200)
        assert not success
        assert p.n_carbon == 90  # Unchanged

    def test_coagulation(self):
        """Test particle coagulation."""
        p1 = Particle(n_carbon=100, n_hydrogen=50, n_primary=1)
        p2 = Particle(n_carbon=200, n_hydrogen=100, n_primary=2)

        p_new = p1.coagulate(p2)

        assert p_new.n_carbon == 300
        assert p_new.n_hydrogen == 150
        assert p_new.n_primary == 3

    def test_particle_copy(self):
        """Test particle copying."""
        p = Particle(n_carbon=100, n_hydrogen=50, creation_time=1.0)
        p_copy = p.copy()

        assert p_copy.n_carbon == p.n_carbon
        assert p_copy.n_hydrogen == p.n_hydrogen
        assert p_copy.creation_time == p.creation_time

        # Modify original
        p.add_carbon(10)
        assert p_copy.n_carbon == 100  # Copy unchanged

    def test_invalid_particle(self):
        """Test validation of invalid particles."""
        with pytest.raises(ValueError):
            Particle(n_carbon=-10, n_hydrogen=0)

        with pytest.raises(ValueError):
            Particle(n_carbon=100, n_hydrogen=-5)

        with pytest.raises(ValueError):
            Particle(n_carbon=100, n_hydrogen=0, n_primary=0)


class TestNascentParticle:
    """Tests for nascent particle creation."""

    def test_create_nascent_particle(self):
        """Test nascent particle factory function."""
        p = create_nascent_particle(
            n_carbon=32,
            n_hydrogen=18,
            creation_time=0.001,
        )

        assert p.n_carbon == 32
        assert p.n_hydrogen == 18
        assert p.n_primary == 1
        assert p.active_sites == 2
        assert p.creation_time == 0.001
