"""
Reactor module for coupled gas-particle simulations.

This module provides reactor models that couple gas-phase chemistry
with particle population dynamics using operator splitting.

References:
    M.S. Celnik et al., "Coupling a stochastic soot population balance to
    gas-phase chemistry using operator splitting", Combustion and Flame 148 (2007)

    M.S. Celnik et al., "A predictor-corrector algorithm for the coupling
    of stiff ODEs to a particle population balance", J. Comput. Phys. 228 (2009)
"""

from nanoparticle_simulator.reactor.base import ReactorBase
from nanoparticle_simulator.reactor.batch import BatchReactor
from nanoparticle_simulator.reactor.splitting import (
    OperatorSplitter,
    StrangSplitter,
    PredictorCorrector,
)
from nanoparticle_simulator.reactor.ode_solver import ODESolver

__all__ = [
    "ReactorBase",
    "BatchReactor",
    "OperatorSplitter",
    "StrangSplitter",
    "PredictorCorrector",
    "ODESolver",
]
