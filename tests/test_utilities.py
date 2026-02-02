"""
Unit tests for utility functions
"""

import pytest
import numpy as np
from src.utilities import (
    convert_to_volume_fraction,
    calculate_particle_diameter,
    calculate_brownian_velocity,
    calculate_collision_frequency,
    format_size_metric,
)


class TestVolumeConversion:
    """Test volume conversion functions."""

    def test_convert_to_volume_fraction_empty(self):
        """Test volume fraction with no particles."""
        diameters = np.array([])
        volume_fraction = convert_to_volume_fraction(
            diameters, system_volume=1.0e-6
        )

        assert volume_fraction == 0.0

    def test_convert_to_volume_fraction_single_particle(self):
        """Test volume fraction with single particle."""
        diameter = 10.0e-9  # 10 nm
        system_volume = 1.0e-6

        diameters = np.array([diameter])
        volume_fraction = convert_to_volume_fraction(diameters, system_volume)

        # Calculate expected
        radius = diameter / 2.0
        particle_volume = (4.0 / 3.0) * np.pi * (radius**3)
        expected_fraction = particle_volume / system_volume

        assert np.isclose(volume_fraction, expected_fraction, rtol=1e-10)

    def test_convert_to_volume_fraction_multiple_particles(self):
        """Test volume fraction with multiple particles."""
        diameters = np.array([10.0e-9, 20.0e-9, 15.0e-9])
        system_volume = 1.0e-6

        volume_fraction = convert_to_volume_fraction(diameters, system_volume)

        # Should be between 0 and 1
        assert 0.0 <= volume_fraction <= 1.0


class TestParticleDiameter:
    """Test particle diameter calculation."""

    def test_calculate_particle_diameter(self):
        """Test diameter calculation from atom count."""
        num_atoms = 1000
        diameter = calculate_particle_diameter(num_atoms)

        assert diameter > 0.0
        assert diameter < 100.0e-9  # Should be less than 100 nm

    def test_diameter_increases_with_atoms(self):
        """Test that diameter increases with atom count."""
        diameter_100 = calculate_particle_diameter(100)
        diameter_1000 = calculate_particle_diameter(1000)
        diameter_10000 = calculate_particle_diameter(10000)

        assert diameter_100 < diameter_1000 < diameter_10000


class TestBrownianVelocity:
    """Test Brownian motion calculations."""

    def test_calculate_brownian_velocity(self):
        """Test Brownian velocity calculation."""
        velocity = calculate_brownian_velocity(
            temperature=300.0, particle_diameter=10.0e-9
        )

        assert velocity > 0.0

    def test_velocity_increases_with_temperature(self):
        """Test that velocity increases with temperature."""
        velocity_cold = calculate_brownian_velocity(
            temperature=100.0, particle_diameter=10.0e-9
        )
        velocity_hot = calculate_brownian_velocity(
            temperature=1000.0, particle_diameter=10.0e-9
        )

        assert velocity_hot > velocity_cold

    def test_velocity_decreases_with_diameter(self):
        """Test that velocity decreases with particle diameter."""
        velocity_small = calculate_brownian_velocity(
            temperature=300.0, particle_diameter=1.0e-9
        )
        velocity_large = calculate_brownian_velocity(
            temperature=300.0, particle_diameter=100.0e-9
        )

        assert velocity_small > velocity_large


class TestCollisionFrequency:
    """Test collision frequency calculations."""

    def test_collision_frequency_empty_system(self):
        """Test collision frequency with no particles."""
        frequency = calculate_collision_frequency(
            num_particles=0,
            particle_diameter=10.0e-9,
            temperature=300.0,
            system_volume=1.0e-6,
        )

        assert frequency == 0.0

    def test_collision_frequency_single_particle(self):
        """Test collision frequency with one particle."""
        frequency = calculate_collision_frequency(
            num_particles=1,
            particle_diameter=10.0e-9,
            temperature=300.0,
            system_volume=1.0e-6,
        )

        assert frequency == 0.0

    def test_collision_frequency_increases_with_particles(self):
        """Test that collision frequency increases with particle count."""
        freq_10 = calculate_collision_frequency(
            num_particles=10,
            particle_diameter=10.0e-9,
            temperature=300.0,
            system_volume=1.0e-6,
        )
        freq_100 = calculate_collision_frequency(
            num_particles=100,
            particle_diameter=10.0e-9,
            temperature=300.0,
            system_volume=1.0e-6,
        )

        assert freq_100 > freq_10

    def test_collision_frequency_increases_with_temperature(self):
        """Test that collision frequency increases with temperature."""
        freq_cold = calculate_collision_frequency(
            num_particles=100,
            particle_diameter=10.0e-9,
            temperature=100.0,
            system_volume=1.0e-6,
        )
        freq_hot = calculate_collision_frequency(
            num_particles=100,
            particle_diameter=10.0e-9,
            temperature=1000.0,
            system_volume=1.0e-6,
        )

        assert freq_hot > freq_cold


class TestFormatSizeMetric:
    """Test size metric formatting."""

    def test_format_picometers(self):
        """Test formatting of picometer scale."""
        result = format_size_metric(1.0e-12)
        assert "pm" in result

    def test_format_nanometers(self):
        """Test formatting of nanometer scale."""
        result = format_size_metric(1.0e-9)
        assert "nm" in result

    def test_format_micrometers(self):
        """Test formatting of micrometer scale."""
        result = format_size_metric(1.0e-6)
        assert "μm" in result

    def test_format_millimeters(self):
        """Test formatting of millimeter scale."""
        result = format_size_metric(1.0e-3)
        assert "mm" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
