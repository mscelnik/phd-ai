"""
Population Balance Model for Nano-Particulates

Implements stochastic population balance equations using Gillespie's algorithm
for simulating particle formation, growth, coagulation, and sintering.

Based on:
- Celnik MS (2008): "On the numerical modelling of soot and carbon nanotube formation"
- Kraft et al. (2007): "Coupling a stochastic soot population balance to gas-phase chemistry"
"""

import numpy as np
from dataclasses import dataclass
from typing import List, Callable, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


@dataclass
class ParticleProperty:
    """Represents a property of a particle (e.g., number of atoms, diameter)."""

    name: str
    initial_value: float
    description: str = ""


class PopulationBalance:
    """
    Stochastic Population Balance Model using Gillespie's Direct Method.

    This implements the stochastic simulation algorithm for particle systems,
    allowing efficient simulation of nano-particulate formation and evolution.
    """

    def __init__(
        self,
        time_step: float = 1.0e-6,
        max_time: float = 1.0,
        num_particles_initial: int = 100,
    ):
        """
        Initialize the population balance model.

        Parameters
        ----------
        time_step : float
            Initial time step for the simulation (seconds)
        max_time : float
            Maximum simulation time (seconds)
        num_particles_initial : int
            Number of initial particles in the system
        """
        self.time_step = time_step
        self.max_time = max_time
        self.num_particles_initial = num_particles_initial

        self.current_time = 0.0
        self.particles = []  # List of particle states
        self.reaction_events = []  # List of reaction event functions
        self.history = {
            "time": [],
            "num_particles": [],
            "avg_diameter": [],
            "total_mass": [],
        }

        logger.info(
            f"Initialized PopulationBalance: max_time={max_time}s, "
            f"initial_particles={num_particles_initial}"
        )

    def add_reaction_event(
        self,
        name: str,
        rate_function: Callable,
        propensity_function: Callable,
        update_function: Callable,
    ) -> None:
        """
        Register a reaction event for the model.

        Parameters
        ----------
        name : str
            Name of the reaction (e.g., "nucleation", "coagulation")
        rate_function : Callable
            Function that calculates the reaction rate given state
        propensity_function : Callable
            Gillespie propensity function (hazard rate)
        update_function : Callable
            Function that updates particle state after event
        """
        event = {
            "name": name,
            "rate_function": rate_function,
            "propensity_function": propensity_function,
            "update_function": update_function,
        }
        self.reaction_events.append(event)
        logger.debug(f"Added reaction event: {name}")

    def initialize_particles(
        self, particle_properties: List[ParticleProperty]
    ) -> None:
        """
        Initialize particle population.

        Parameters
        ----------
        particle_properties : List[ParticleProperty]
            List of particle properties to track
        """
        self.particles = []
        self.particle_properties = particle_properties

        for i in range(self.num_particles_initial):
            particle = {
                prop.name: prop.initial_value for prop in particle_properties
            }
            particle["id"] = i
            self.particles.append(particle)

        logger.info(f"Initialized {len(self.particles)} particles")

    def calculate_propensities(self) -> Tuple[np.ndarray, float]:
        """
        Calculate propensity functions for all reaction events.

        Returns
        -------
        propensities : np.ndarray
            Array of propensity values for each reaction
        total_propensity : float
            Sum of all propensities
        """
        propensities = np.zeros(len(self.reaction_events))

        for i, event in enumerate(self.reaction_events):
            propensities[i] = event["propensity_function"](
                self.particles, self.current_time
            )

        total_propensity = np.sum(propensities)
        return propensities, total_propensity

    def gillespie_step(self) -> bool:
        """
        Execute one Gillespie algorithm step.

        Returns
        -------
        bool
            True if reaction occurred, False if time exceeded max_time
        """
        propensities, total_propensity = self.calculate_propensities()

        if total_propensity <= 0:
            logger.debug("No propensity: simulation may have ended")
            return False

        # Calculate time to next reaction
        tau = -np.log(np.random.rand()) / total_propensity
        self.current_time += tau

        if self.current_time > self.max_time:
            self.current_time = self.max_time
            return False

        # Select which reaction occurs
        if np.sum(propensities) > 0:
            probabilities = propensities / np.sum(propensities)
            reaction_index = np.random.choice(
                len(self.reaction_events), p=probabilities
            )

            # Execute the reaction
            event = self.reaction_events[reaction_index]
            event["update_function"](self.particles)

        return True

    def simulate(self, num_steps: Optional[int] = None) -> None:
        """
        Run the stochastic simulation.

        Parameters
        ----------
        num_steps : Optional[int]
            Maximum number of Gillespie steps. If None, runs until max_time.
        """
        logger.info(f"Starting simulation: max_time={self.max_time}s")

        step_count = 0
        while self.current_time < self.max_time:
            if num_steps is not None and step_count >= num_steps:
                break

            if not self.gillespie_step():
                break

            step_count += 1

            # Store history every 100 steps
            if step_count % 100 == 0:
                self._store_history()

        self._store_history()  # Final state
        logger.info(
            f"Simulation complete: {step_count} steps, final_time={self.current_time}s"
        )

    def _store_history(self) -> None:
        """Store current state in history."""
        self.history["time"].append(self.current_time)
        self.history["num_particles"].append(len(self.particles))

        if len(self.particles) > 0:
            avg_diameter = np.mean(
                [p.get("diameter", 1.0) for p in self.particles]
            )
            total_mass = np.sum([p.get("mass", 1.0) for p in self.particles])
        else:
            avg_diameter = 0.0
            total_mass = 0.0

        self.history["avg_diameter"].append(avg_diameter)
        self.history["total_mass"].append(total_mass)

    def get_particle_distribution(
        self, property_name: str, num_bins: int = 50
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Get histogram distribution of a particle property.

        Parameters
        ----------
        property_name : str
            Name of the property to histogram
        num_bins : int
            Number of histogram bins

        Returns
        -------
        bins : np.ndarray
            Bin edges
        histogram : np.ndarray
            Histogram counts
        """
        values = [p.get(property_name, 0) for p in self.particles]
        histogram, bins = np.histogram(values, bins=num_bins)
        return bins, histogram

    def get_statistics(self) -> dict:
        """
        Get summary statistics of current particle population.

        Returns
        -------
        dict
            Dictionary with statistics (mean, std, min, max for each tracked property)
        """
        if len(self.particles) == 0:
            return {}

        stats = {}
        for prop in self.particle_properties:
            values = np.array([p.get(prop.name, 0) for p in self.particles])
            stats[prop.name] = {
                "mean": float(np.mean(values)),
                "std": float(np.std(values)),
                "min": float(np.min(values)),
                "max": float(np.max(values)),
            }

        return stats
