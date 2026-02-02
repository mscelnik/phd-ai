import sys
from src.simulation import SimulationConfig, OperatorSplittingSimulator


def main(config_path):
    config = SimulationConfig(config_path).config
    sim = OperatorSplittingSimulator(config)
    # Example initial conditions
    initial_conditions = {"chemistry": [1.0]}  # initial concentration
    initial_particles = {"count": config["particles"]["initial_count"]}
    chem_t, chem_y, particle_history = sim.run(initial_conditions, initial_particles)
    print("Simulation complete. Results saved to data/.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run_simulation.py <config_path>")
    else:
        main(sys.argv[1])
