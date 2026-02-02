"""
Unit tests for particle system
"""

import pytest
import numpy as np
from src.particle_system import ParticleSystem


class TestParticleSystem:
    """Test ParticleSystem class."""

    def test_initialization(self):
        """Test ParticleSystem initialization."""
        ps = ParticleSystem(
            temperature=1500.0, pressure=101325.0, volume=1.0e-6
        )

        assert ps.temperature == 1500.0
        assert ps.pressure == 101325.0
        assert ps.volume == 1.0e-6
        assert len(ps.particles) == 0

    def test_add_particle(self):
        """Test adding particles to the system."""
        ps = ParticleSystem()

        ps.add_particle(num_atoms=1000, mass=1.0e-20, diameter=5.0e-9)

        assert len(ps.particles) == 1
        assert ps.particles[0]["num_atoms"] == 1000
        assert ps.particles[0]["mass"] == 1.0e-20
        assert ps.particles[0]["diameter"] == 5.0e-9

    def test_nucleation_propensity(self):
        """Test nucleation propensity calculation."""
        ps = ParticleSystem(temperature=1500.0)

        # Test with positive concentration
        propensity = ps.nucleation_propensity(precursor_concentration=1000.0)
        assert propensity > 0.0

        # Test with zero concentration
        propensity_zero = ps.nucleation_propensity(precursor_concentration=0.0)
        assert propensity_zero == 0.0

        # Test with negative concentration (should be zero)
        propensity_neg = ps.nucleation_propensity(
            precursor_concentration=-100.0
        )
        assert propensity_neg == 0.0

    def test_surface_growth_propensity(self):
        """Test surface growth propensity."""
        ps = ParticleSystem()
        ps.add_particle(num_atoms=1000, mass=1.0e-20, diameter=5.0e-9)

        propensity = ps.surface_growth_propensity(
            precursor_concentration=1000.0, particle_index=0
        )
        assert propensity > 0.0

        # Test with non-existent particle
        propensity_invalid = ps.surface_growth_propensity(
            precursor_concentration=1000.0, particle_index=999
        )
        assert propensity_invalid == 0.0

    def test_coagulation_propensity(self):
        """Test coagulation propensity."""
        ps = ParticleSystem()

        # No particles
        propensity_empty = ps.coagulation_propensity()
        assert propensity_empty == 0.0

        # One particle (no collision possible)
        ps.add_particle(num_atoms=1000, mass=1.0e-20, diameter=5.0e-9)
        propensity_one = ps.coagulation_propensity()
        assert propensity_one == 0.0

        # Two particles
        ps.add_particle(num_atoms=1000, mass=1.0e-20, diameter=5.0e-9)
        propensity_two = ps.coagulation_propensity()
        assert propensity_two > 0.0

    def test_sintering_propensity(self):
        """Test sintering propensity."""
        ps = ParticleSystem(temperature=1500.0)
        ps.add_particle(num_atoms=1000, mass=1.0e-20, diameter=5.0e-9)

        propensity = ps.sintering_propensity(particle_index=0)
        assert propensity > 0.0

        # Temperature effect: higher temp should have higher sintering rate
        ps_hot = ParticleSystem(temperature=2000.0)
        ps_hot.add_particle(num_atoms=1000, mass=1.0e-20, diameter=5.0e-9)
        propensity_hot = ps_hot.sintering_propensity(particle_index=0)
        assert propensity_hot > propensity

    def test_nucleation_event(self):
        """Test nucleation event."""
        ps = ParticleSystem()
        assert len(ps.particles) == 0

        ps.perform_nucleation()

        assert len(ps.particles) == 1
        assert ps.particles[0]["diameter"] == 1.0e-9

    def test_surface_growth_event(self):
        """Test surface growth event."""
        ps = ParticleSystem()
        ps.add_particle(num_atoms=1000, mass=1.0e-20, diameter=5.0e-9)

        initial_diameter = ps.particles[0]["diameter"]
        ps.perform_surface_growth(particle_index=0)
        final_diameter = ps.particles[0]["diameter"]

        assert final_diameter > initial_diameter
        assert ps.particles[0]["num_atoms"] > 1000

    def test_coagulation_event(self):
        """Test coagulation event."""
        ps = ParticleSystem()
        ps.add_particle(num_atoms=1000, mass=1.0e-20, diameter=5.0e-9)
        ps.add_particle(num_atoms=1000, mass=1.0e-20, diameter=5.0e-9)

        initial_count = len(ps.particles)
        ps.perform_coagulation()
        final_count = len(ps.particles)

        assert final_count == initial_count - 1
        assert ps.particles[0]["num_atoms"] == 2000

    def test_diameter_to_mass_conversion(self):
        """Test diameter to mass conversion."""
        ps = ParticleSystem()

        diameter = 10.0e-9  # 10 nm
        mass = ps._diameter_to_mass(diameter)

        assert mass > 0.0

        # Verify inverse relationship
        diameter_back = ps._mass_to_diameter(mass)
        assert np.isclose(diameter, diameter_back, rtol=1e-10)

    def test_get_mean_particle_diameter(self):
        """Test getting mean particle diameter."""
        ps = ParticleSystem()

        # Empty system
        assert ps.get_mean_particle_diameter() == 0.0

        # Single particle
        ps.add_particle(num_atoms=1000, mass=1.0e-20, diameter=5.0e-9)
        assert ps.get_mean_particle_diameter() == 5.0e-9

        # Multiple particles
        ps.add_particle(num_atoms=1000, mass=1.0e-20, diameter=10.0e-9)
        mean_diameter = ps.get_mean_particle_diameter()
        assert np.isclose(mean_diameter, 7.5e-9)

    def test_get_total_particle_volume(self):
        """Test total particle volume calculation."""
        ps = ParticleSystem()

        # Empty system
        assert ps.get_total_particle_volume() == 0.0

        # Single particle
        ps.add_particle(num_atoms=1000, mass=1.0e-20, diameter=10.0e-9)
        volume = ps.get_total_particle_volume()

        expected_volume = (4.0 / 3.0) * np.pi * (5.0e-9) ** 3
        assert np.isclose(volume, expected_volume, rtol=1e-10)

    def test_get_system_state(self):
        """Test getting system state."""
        ps = ParticleSystem(temperature=1500.0, pressure=101325.0)
        ps.time = 0.5
        ps.add_particle(num_atoms=1000, mass=1.0e-20, diameter=5.0e-9)

        state = ps.get_system_state()

        assert state["time"] == 0.5
        assert state["num_particles"] == 1
        assert state["temperature"] == 1500.0
        assert state["pressure"] == 101325.0


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_particle_system_with_extreme_values(self):
        """Test with extreme temperature and pressure values."""
        # Very hot system
        ps_hot = ParticleSystem(temperature=5000.0)
        sintering_hot = ps_hot.sintering_propensity(0)

        # Very cold system
        ps_cold = ParticleSystem(temperature=100.0)
        ps_cold.add_particle(num_atoms=1000, mass=1.0e-20, diameter=5.0e-9)
        sintering_cold = ps_cold.sintering_propensity(0)

        # Hot should have higher sintering rate
        assert sintering_hot > sintering_cold

    def test_particle_system_with_zero_volume(self):
        """Test system with very small volume."""
        ps = ParticleSystem(volume=1.0e-15)

        # Should still initialize without error
        assert ps.volume == 1.0e-15


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
