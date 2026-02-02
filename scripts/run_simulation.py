import sys
from src.simulation import SimulationConfig, OperatorSplittingSimulator


def main(config_path):
    config = SimulationConfig(config_path).config
    sim = OperatorSplittingSimulator(config)
    # Placeholder: initial conditions and particles
    initial_conditions = {}
    initial_particles = {}
    sim.run(initial_conditions, initial_particles)
    print("Simulation complete.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run_simulation.py <config_path>")
    else:
        main(sys.argv[1])
