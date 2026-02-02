"""
Utility functions for nano-particulate simulations
"""

import numpy as np
from typing import List, Tuple


def convert_to_volume_fraction(
    particle_diameters: np.ndarray, system_volume: float
) -> float:
    """
    Convert particle diameters to volume fraction.

    Parameters
    ----------
    particle_diameters : np.ndarray
        Array of particle diameters in meters
    system_volume : float
        System volume in cubic meters

    Returns
    -------
    float
        Volume fraction of particles
    """
    total_particle_volume = 0.0
    for diameter in particle_diameters:
        radius = diameter / 2.0
        volume = (4.0 / 3.0) * np.pi * (radius**3)
        total_particle_volume += volume

    volume_fraction = total_particle_volume / system_volume
    return volume_fraction


def calculate_particle_diameter(
    num_atoms: int, atom_mass: float = 12.0 / 6.02214076e23
) -> float:
    """
    Calculate particle diameter from number of atoms.

    Parameters
    ----------
    num_atoms : int
        Number of atoms in particle
    atom_mass : float
        Mass of a single atom in kg

    Returns
    -------
    float
        Particle diameter in meters
    """
    carbon_density = 2200.0  # kg/m³
    particle_mass = num_atoms * atom_mass
    particle_volume = particle_mass / carbon_density
    particle_radius = (3.0 * particle_volume / (4.0 * np.pi)) ** (1.0 / 3.0)
    return 2.0 * particle_radius


def calculate_brownian_velocity(
    temperature: float, particle_diameter: float, gas_viscosity: float = 1.81e-5
) -> float:
    """
    Calculate Brownian motion velocity using kinetic theory.

    Parameters
    ----------
    temperature : float
        Temperature in Kelvin
    particle_diameter : float
        Particle diameter in meters
    gas_viscosity : float
        Gas dynamic viscosity in Pa·s (default: air at 300K)

    Returns
    -------
    float
        Characteristic Brownian velocity in m/s
    """
    boltzmann = 1.380649e-23  # J/K
    particle_mass = 1.0e-26  # kg (approximate for small nanoparticles)

    # Diffusion coefficient from Stokes-Einstein
    diffusion = (
        boltzmann
        * temperature
        / (3.0 * np.pi * gas_viscosity * particle_diameter)
    )

    # Brownian velocity scale
    velocity = np.sqrt(diffusion * boltzmann * temperature / particle_mass)

    return velocity


def calculate_collision_frequency(
    num_particles: int,
    particle_diameter: float,
    temperature: float,
    system_volume: float,
) -> float:
    """
    Calculate binary collision frequency from kinetic theory.

    Parameters
    ----------
    num_particles : int
        Number of particles
    particle_diameter : float
        Average particle diameter in meters
    temperature : float
        Temperature in Kelvin
    system_volume : float
        System volume in cubic meters

    Returns
    -------
    float
        Collision frequency in 1/s
    """
    if num_particles < 2:
        return 0.0

    boltzmann = 1.380649e-23
    # Number density
    number_density = num_particles / system_volume

    # Brownian velocity
    velocity = calculate_brownian_velocity(temperature, particle_diameter)

    # Collision cross section
    collision_diameter = 2.0 * particle_diameter
    cross_section = np.pi * collision_diameter**2

    # Collision frequency
    frequency = number_density * velocity * cross_section * np.sqrt(2)

    return frequency


def format_size_metric(value: float) -> str:
    """
    Format a size metric with appropriate units.

    Parameters
    ----------
    value : float
        Value in meters

    Returns
    -------
    str
        Formatted string with appropriate units (nm, μm, etc.)
    """
    if value < 1e-9:
        return f"{value*1e12:.2f} pm"
    elif value < 1e-6:
        return f"{value*1e9:.2f} nm"
    elif value < 1e-3:
        return f"{value*1e6:.2f} μm"
    else:
        return f"{value*1e3:.2f} mm"
