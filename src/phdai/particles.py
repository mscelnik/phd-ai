"""Particle population-balance Monte Carlo module (toy implementation).

Provides a simple stochastic coagulation/nucleation simulator with a
failsafe on iterations/time to comply with DEVGUIDE test limits.
"""

from __future__ import annotations

import random
from typing import List, Tuple

import numpy as np


def initialize_particles(n_seed: int, size: float = 1.0) -> List[float]:
    return [size for _ in range(n_seed)]


def coagulate_step(particles: List[float]) -> List[float]:
    """Pick two random particles and merge them (add volumes).

    Returns updated particle list.
    """
    if len(particles) < 2:
        return particles
    i, j = random.sample(range(len(particles)), 2)
    # merge by adding sizes (toy model)
    new_size = particles[i] + particles[j]
    # remove larger index first
    for idx in sorted([i, j], reverse=True):
        particles.pop(idx)
    particles.append(new_size)
    return particles


def run_monte_carlo(n_steps: int, particles: List[float], max_iters: int = 10000) -> List[float]:
    """Run a bounded number of coagulation steps.

    Args:
        n_steps: number of coagulation attempts
        particles: initial particle sizes list
        max_iters: absolute iteration cap (failsafe)

    Returns final particle sizes list
    """
    iters = 0
    for _ in range(n_steps):
        if iters >= max_iters:
            break
        particles = coagulate_step(particles)
        iters += 1
    return particles


def nucleate(particles: List[float], rate: float, dt: float, seed_size: float = 1.0) -> List[float]:
    """Create new particles based on nucleation rate and timestep dt.

    Uses Poisson draw.
    """
    mean_count = rate * dt
    n_new = np.random.poisson(mean_count)
    particles.extend([seed_size] * int(n_new))
    return particles


def size_distribution(particles: List[float], bins: int = 10) -> Tuple[np.ndarray, np.ndarray]:
    return np.histogram(particles, bins=bins)
