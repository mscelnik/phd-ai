"""
Nano-Particulate Stochastic Modelling Package
Based on Dr. Matthew Celnik's PhD thesis (2008)

This package implements stochastic population balance models for simulating
nano-particulate formation, growth, and sintering using Gillespie's stochastic
simulation algorithm.
"""

__version__ = "0.1.0"
__author__ = "Based on Dr. Matthew Celnik's work"

from .population_balance import PopulationBalance
from .particle_system import ParticleSystem
from .events import ReactionEvent
from .utilities import convert_to_volume_fraction, calculate_particle_diameter

__all__ = [
    "PopulationBalance",
    "ParticleSystem",
    "ReactionEvent",
    "convert_to_volume_fraction",
    "calculate_particle_diameter",
]
