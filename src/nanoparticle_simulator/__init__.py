"""
Nanoparticle Simulator
======================

A comprehensive numerical modelling package for soot and carbon nanotube formation.

This package implements a coupled gas-phase chemistry and stochastic population
balance model for simulating nano-particle formation in combustion systems.

The solver uses an operator splitting algorithm to couple:
1. Gas-phase chemistry solver (using Cantera for detailed kinetics)
2. Particle population balance model (stochastic Markov-chain Monte Carlo)

References
----------
Based on the PhD thesis:
    M.S. Celnik, "On the numerical modelling of soot and carbon nanotubes",
    University of Cambridge, 2008.

Key papers:
    - Celnik et al., Combustion and Flame 148 (2007) 158-176
    - Celnik et al., Journal of Computational Physics 228 (2009) 2758-2769
    - Celnik et al., Combustion and Flame 155 (2008) 161-180
"""

from nanoparticle_simulator.version import __version__

__author__ = "Matthew Celnik"
__email__ = "msc37@cam.ac.uk"
__all__ = ["__version__"]
