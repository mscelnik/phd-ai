"""
Unit tests for population balance model
"""

import pytest
import numpy as np
from src.population_balance import PopulationBalance, ParticleProperty


class TestPopulationBalance:
    """Test PopulationBalance class."""

    def test_initialization(self):
        """Test PopulationBalance initialization."""
        pb = PopulationBalance(
            time_step=1.0e-6, max_time=1.0, num_particles_initial=100
        )

        assert pb.time_step == 1.0e-6
        assert pb.max_time == 1.0
        assert pb.num_particles_initial == 100
        assert pb.current_time == 0.0
        assert len(pb.particles) == 0
        assert len(pb.reaction_events) == 0

    def test_particle_initialization(self):
        """Test particle population initialization."""
        pb = PopulationBalance(num_particles_initial=50)

        properties = [
            ParticleProperty("diameter", 1.0e-9, "Particle diameter"),
            ParticleProperty("mass", 1.0e-20, "Particle mass"),
        ]
        pb.initialize_particles(properties)

        assert len(pb.particles) == 50
        for particle in pb.particles:
            assert "id" in particle
            assert "diameter" in particle
            assert "mass" in particle
            assert particle["diameter"] == 1.0e-9

    def test_add_reaction_event(self):
        """Test adding reaction events."""
        pb = PopulationBalance()

        def dummy_rate(particles, time):
            return 1.0

        def dummy_propensity(particles, time):
            return len(particles)

        def dummy_update(particles):
            pass

        pb.add_reaction_event(
            "test_reaction", dummy_rate, dummy_propensity, dummy_update
        )

        assert len(pb.reaction_events) == 1
        assert pb.reaction_events[0]["name"] == "test_reaction"

    def test_propensity_calculation(self):
        """Test propensity calculation."""
        pb = PopulationBalance(num_particles_initial=10)

        properties = [ParticleProperty("diameter", 1.0e-9)]
        pb.initialize_particles(properties)

        def propensity1(particles, time):
            return len(particles) * 0.5

        def propensity2(particles, time):
            return 2.0

        pb.add_reaction_event(
            "reaction1",
            lambda p, t: propensity1(p, t),
            propensity1,
            lambda p: None,
        )
        pb.add_reaction_event(
            "reaction2",
            lambda p, t: propensity2(p, t),
            propensity2,
            lambda p: None,
        )

        propensities, total = pb.calculate_propensities()

        assert len(propensities) == 2
        assert propensities[0] == 5.0  # 10 * 0.5
        assert propensities[1] == 2.0
        assert total == 7.0

    def test_edge_case_zero_particles(self):
        """Test handling of system with zero particles."""
        pb = PopulationBalance(num_particles_initial=0)
        properties = [ParticleProperty("diameter", 1.0e-9)]
        pb.initialize_particles(properties)

        assert len(pb.particles) == 0

        propensities, total = pb.calculate_propensities()
        assert total == 0.0

    def test_gillespie_step_with_no_propensity(self):
        """Test Gillespie step when no reactions can occur."""
        pb = PopulationBalance()
        properties = [ParticleProperty("diameter", 1.0e-9)]
        pb.initialize_particles(properties)

        # Add reaction with zero propensity
        def zero_propensity(particles, time):
            return 0.0

        pb.add_reaction_event(
            "zero_reaction", lambda p, t: 0.0, zero_propensity, lambda p: None
        )

        result = pb.gillespie_step()
        assert result is False

    def test_get_statistics(self):
        """Test getting population statistics."""
        pb = PopulationBalance(num_particles_initial=100)
        properties = [
            ParticleProperty("diameter", 2.0e-9),
            ParticleProperty("mass", 5.0e-20),
        ]
        pb.initialize_particles(properties)

        stats = pb.get_statistics()

        assert "diameter" in stats
        assert "mass" in stats
        assert stats["diameter"]["mean"] == 2.0e-9
        assert stats["mass"]["mean"] == 5.0e-20

    def test_history_storage(self):
        """Test history tracking."""
        pb = PopulationBalance(max_time=0.001, num_particles_initial=5)
        properties = [ParticleProperty("diameter", 1.0e-9)]
        pb.initialize_particles(properties)

        pb._store_history()

        assert len(pb.history["time"]) == 1
        assert len(pb.history["num_particles"]) == 1
        assert pb.history["num_particles"][0] == 5


class TestParticleDistribution:
    """Test particle distribution calculations."""

    def test_get_particle_distribution(self):
        """Test getting particle size distribution."""
        pb = PopulationBalance(num_particles_initial=100)
        properties = [ParticleProperty("diameter", 1.0e-9)]
        pb.initialize_particles(properties)

        # Add some variation to diameters
        for i, particle in enumerate(pb.particles):
            particle["diameter"] = 1.0e-9 * (1.0 + i / 100.0)

        bins, histogram = pb.get_particle_distribution("diameter", num_bins=10)

        assert len(bins) == 11  # num_bins + 1
        assert len(histogram) == 10
        assert np.sum(histogram) == 100


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
