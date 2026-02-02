"""
Unit tests for ParticleEnsemble class.
"""

import pytest
import numpy as np
from nanoparticle_simulator.particles.particle import Particle
from nanoparticle_simulator.particles.ensemble import ParticleEnsemble

# FIXME: These tests are hanging. Add a fail-safe timeout mechanism to prevent infinite loops.


class TestParticleEnsemble:
    """Tests for ParticleEnsemble class."""

    @pytest.fixture
    def ensemble(self):
        """Create a test ensemble."""
        return ParticleEnsemble(
            sample_volume=1e-9,
            max_particles=100,
            min_particles=1,  # Low threshold to avoid doubling in tests
            seed=42,
        )

    def test_empty_ensemble(self, ensemble):
        """Test empty ensemble properties."""
        assert ensemble.n_particles == 0
        assert ensemble.total_mass == 0.0
        assert ensemble.number_density == 0.0
        assert ensemble.mean_diameter == 0.0

    def test_add_particle(self, ensemble):
        """Test adding particles."""
        p = Particle(n_carbon=100, n_hydrogen=50)
        ensemble.add_particle(p)

        assert ensemble.n_particles == 1
        assert ensemble.total_mass > 0

    def test_add_multiple_particles(self, ensemble):
        """Test adding multiple particles."""
        for i in range(10):
            p = Particle(n_carbon=100 + i * 10, n_hydrogen=50)
            ensemble.add_particle(p)

        assert ensemble.n_particles == 10

    def test_remove_particle(self, ensemble):
        """Test removing particles by index."""
        for i in range(5):
            p = Particle(n_carbon=100, n_hydrogen=50)
            ensemble.add_particle(p)

        removed = ensemble.remove_particle(2)

        assert ensemble.n_particles == 4
        assert removed.n_carbon == 100

    def test_select_random(self, ensemble):
        """Test random particle selection."""
        for i in range(10):
            p = Particle(n_carbon=100 * (i + 1), n_hydrogen=50)
            ensemble.add_particle(p)

        selected = ensemble.select_random()
        assert selected is not None
        assert ensemble.n_particles == 10  # Not removed

    def test_select_random_pair(self, ensemble):
        """Test random pair selection."""
        for i in range(10):
            p = Particle(n_carbon=100, n_hydrogen=50)
            ensemble.add_particle(p)

        pair = ensemble.select_random_pair()
        assert pair is not None
        idx1, idx2 = pair
        assert idx1 != idx2

    def test_select_random_pair_insufficient(self, ensemble):
        """Test pair selection with insufficient particles."""
        p = Particle(n_carbon=100, n_hydrogen=50)
        ensemble.add_particle(p)

        pair = ensemble.select_random_pair()
        assert pair is None

    def test_weighted_selection(self, ensemble):
        """Test weighted particle selection."""
        for i in range(5):
            p = Particle(n_carbon=100 * (i + 1), n_hydrogen=50)
            ensemble.add_particle(p)

        # Weight by carbon count
        weights = np.array([p.n_carbon for p in ensemble])
        result = ensemble.select_weighted(weights)

        assert result is not None
        idx, particle = result
        assert 0 <= idx < ensemble.n_particles

    def test_halving(self):
        """Test ensemble halving when max exceeded."""
        ensemble = ParticleEnsemble(
            sample_volume=1e-9,
            max_particles=20,
            min_particles=5,
            seed=42,
        )

        # Add particles to trigger halving
        for i in range(25):
            p = Particle(n_carbon=100, n_hydrogen=50)
            ensemble.add_particle(p)

        # Should have been halved
        assert ensemble.n_particles <= 20
        assert ensemble.statistical_weight > 1.0

    def test_doubling(self):
        """Test ensemble doubling when min not met."""
        ensemble = ParticleEnsemble(
            sample_volume=1e-9,
            max_particles=100,
            min_particles=10,
            seed=42,
        )

        # Add exactly 10 particles
        for i in range(10):
            p = Particle(n_carbon=100, n_hydrogen=50)
            ensemble.add_particle(p)

        assert ensemble.n_particles == 10
        assert ensemble.statistical_weight == 1.0

        # Remove one particle - this should trigger doubling
        ensemble.remove_particle(0)

        # After removal (9), doubling happens -> 18 particles, weight halved
        assert ensemble.n_particles == 18  # 9 * 2
        assert ensemble.statistical_weight == 0.5

    def test_statistics(self, ensemble):
        """Test ensemble statistics calculation."""
        for i in range(10):
            p = Particle(n_carbon=100 + i * 50, n_hydrogen=50)
            ensemble.add_particle(p)

        stats = ensemble.get_statistics()

        assert stats.n_particles == 10
        assert stats.total_mass > 0
        assert stats.mean_diameter > 0
        assert stats.mean_carbon > 0
        assert stats.number_density > 0

    def test_diameter_distribution(self, ensemble):
        """Test size distribution calculation."""
        for i in range(100):
            p = Particle(n_carbon=100 + i * 10, n_hydrogen=50)
            ensemble.add_particle(p)

        centers, counts = ensemble.diameter_distribution(bins=10)

        assert len(centers) == 10
        assert len(counts) == 10
        assert np.sum(counts) > 0

    def test_clear(self, ensemble):
        """Test clearing ensemble."""
        for i in range(10):
            p = Particle(n_carbon=100, n_hydrogen=50)
            ensemble.add_particle(p)

        ensemble.clear()

        assert ensemble.n_particles == 0
        assert ensemble.statistical_weight == 1.0

    def test_iteration(self, ensemble):
        """Test iterating over ensemble."""
        for i in range(5):
            p = Particle(n_carbon=100 * (i + 1), n_hydrogen=50)
            ensemble.add_particle(p)

        carbons = [p.n_carbon for p in ensemble]
        assert carbons == [100, 200, 300, 400, 500]

    def test_indexing(self, ensemble):
        """Test indexing into ensemble."""
        for i in range(5):
            p = Particle(n_carbon=100 * (i + 1), n_hydrogen=50)
            ensemble.add_particle(p)

        assert ensemble[0].n_carbon == 100
        assert ensemble[4].n_carbon == 500
        assert len(ensemble) == 5
