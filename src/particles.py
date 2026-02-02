import numpy as np


class ParticlePopulation:
    def __init__(self, initial_count, growth_rate, coagulation_rate):
        self.count = initial_count
        self.growth_rate = growth_rate
        self.coagulation_rate = coagulation_rate

    def step(self):
        # Simple stochastic growth and coagulation
        growth = np.random.poisson(self.growth_rate * self.count)
        coagulation = np.random.poisson(self.coagulation_rate * self.count)
        self.count += growth - coagulation
        return self.count

    def run(self, steps):
        history = [self.count]
        for _ in range(steps):
            history.append(self.step())
        return history
