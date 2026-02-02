from phdai.particles import initialize_particles, nucleate, run_monte_carlo


def test_particle_seed_and_nucleation():
    particles = initialize_particles(3, size=1.0)
    assert len(particles) == 3
    particles = nucleate(particles, rate=10.0, dt=0.01, seed_size=1.0)
    # with mean 0.1 new particles, it's possible to be same, but should not error
    assert isinstance(particles, list)
    particles2 = run_monte_carlo(2, particles.copy(), max_iters=100)
    assert isinstance(particles2, list)
