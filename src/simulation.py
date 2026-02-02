import yaml
import pandas as pd
import numpy as np


class SimulationConfig:
    def __init__(self, config_path):
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)


from src.chemistry import ReactionSystem
from src.particles import ParticlePopulation


class GasPhaseChemistrySolver:
    def __init__(self, reaction_set):
        self.system = ReactionSystem(reaction_set)

    def run(self, y0, t_span, dt):
        return self.system.run(y0, t_span, dt)


class ParticlePopulationBalanceModel:
    def __init__(self, params):
        self.model = ParticlePopulation(
            params["initial_count"],
            params.get("growth_rate", 0.01),
            params.get("coagulation_rate", 0.005),
        )

    def run(self, steps):
        return self.model.run(steps)


class OperatorSplittingSimulator:
    def __init__(self, config):
        self.gas_solver = GasPhaseChemistrySolver(config["reactions"])
        self.particle_model = ParticlePopulationBalanceModel(config["particles"])
        self.sim_config = config["simulation"]

    def run(self, initial_conditions, initial_particles):
        time_steps = self.sim_config["time_steps"]
        dt = self.sim_config["dt"]
        t_span = (0, time_steps * dt)

        # Chemistry initial conditions: vector of concentrations (example: [1.0])
        y0 = initial_conditions.get("chemistry", [1.0])
        chem_t, chem_y = self.gas_solver.run(y0, t_span, dt)

        # Particle initial count
        initial_count = initial_particles.get("count", self.particle_model.model.count)
        particle_history = self.particle_model.run(time_steps)

        # Output results to CSV
        pd.DataFrame({"time": chem_t, "chemistry": chem_y[0]}).to_csv("data/chemistry_output.csv", index=False)
        pd.DataFrame({"step": range(time_steps + 1), "particle_count": particle_history}).to_csv(
            "data/particle_output.csv", index=False
        )
        return chem_t, chem_y, particle_history
