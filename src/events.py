"""
Reaction Events for Particle System Simulation
"""

from dataclasses import dataclass
from typing import Callable


@dataclass
class ReactionEvent:
    """
    Represents a reaction event that can occur in the particle system.
    """

    name: str
    propensity_function: Callable
    reaction_function: Callable
    description: str = ""

    def __call__(self):
        """Execute the reaction."""
        return self.reaction_function()
