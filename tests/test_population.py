from sootsim.population import MonteCarloPopulation


def test_population_step_creates_snapshots() -> None:
    population = MonteCarloPopulation(
        initial_particles=2, nucleation_coefficient=0.0
    )
    snapshots = population.simulate([0.5, 0.5, 0.5], [0.0, 0.01, 0.02], dt=0.01)
    assert len(snapshots) == 3
    assert all(snapshot.count >= 0 for snapshot in snapshots)
    for snapshot in snapshots:
        assert snapshot.mean_mass >= 0.0
        assert snapshot.median_mass >= 0.0
