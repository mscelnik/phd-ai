"""
Particle population balance module.

This module implements the stochastic Monte Carlo method for simulating
particle population dynamics, including nucleation, growth, coagulation,
and oxidation processes.

References:
    M.S. Celnik et al., "Coupling a stochastic soot population balance to
    gas-phase chemistry using operator splitting", Combustion and Flame 148 (2007)

    M.S. Celnik et al., "An aromatic site description of soot particles",
    Combustion and Flame 155 (2008)
"""

from nanoparticle_simulator.particles.particle import Particle
from nanoparticle_simulator.particles.ensemble import ParticleEnsemble
from nanoparticle_simulator.particles.processes import (
    NucleationProcess,
    GrowthProcess,
    CoagulationProcess,
    OxidationProcess,
)
from nanoparticle_simulator.particles.stochastic_solver import StochasticSolver

__all__ = [
    "Particle",
    "ParticleEnsemble",
    "NucleationProcess",
    "GrowthProcess",
    "CoagulationProcess",
    "OxidationProcess",
    "StochasticSolver",
]
