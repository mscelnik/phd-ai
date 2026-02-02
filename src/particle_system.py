"""
Particle System for Nano-Particulate Simulations

Implements a concrete particle system for soot and nano-particulate formation
with specific reaction mechanisms: nucleation, surface growth, coagulation.
"""

import numpy as np
from typing import List, Dict, Tuple
import logging

logger = logging.getLogger(__name__)


class ParticleSystem:
    """
    Represents a system of nano-particles undergoing nucleation, growth, and coagulation.
    """

    # Constants
    BOLTZMANN_CONSTANT = 1.380649e-23  # J/K
    AVOGADRO_NUMBER = 6.02214076e23

    def __init__(
        self,
        temperature: float = 1500.0,
        pressure: float = 101325.0,
        volume: float = 1.0e-6,
    ):
        """
        Initialize particle system.

        Parameters
        ----------
        temperature : float
            System temperature in Kelvin
        pressure : float
            System pressure in Pascals
        volume : float
            System volume in cubic meters
        """
        self.temperature = temperature
        self.pressure = pressure
        self.volume = volume

        self.particles: List[Dict] = []
        self.time = 0.0

        logger.info(
            f"Initialized ParticleSystem: T={temperature}K, "
            f"P={pressure}Pa, V={volume}m³"
        )

    def add_particle(
        self,
        num_atoms: int,
        mass: float,
        diameter: float,
        formation_time: float = 0.0,
    ) -> None:
        """
        Add a particle to the system.

        Parameters
        ----------
        num_atoms : int
            Number of atoms in the particle
        mass : float
            Particle mass in kg
        diameter : float
            Particle diameter in meters
        formation_time : float
            Time when particle was formed
        """
        particle = {
            "id": len(self.particles),
            "num_atoms": num_atoms,
            "mass": mass,
            "diameter": diameter,
            "formation_time": formation_time,
            "radius": diameter / 2.0,
        }
        self.particles.append(particle)

    def nucleation_propensity(self, precursor_concentration: float) -> float:
        """
        Calculate nucleation propensity (formation rate of new particles).

        Parameters
        ----------
        precursor_concentration : float
            Precursor gas concentration (mol/m³)

        Returns
        -------
        float
            Nucleation rate
        """
        if precursor_concentration < 0:
            return 0.0

        # Arrhenius-type nucleation rate
        nucleation_coefficient = 1.0e-6
        activation_energy = 50000.0  # J/mol
        rate = (
            nucleation_coefficient
            * precursor_concentration
            * np.exp(
                -activation_energy
                / (self.temperature * self.BOLTZMANN_CONSTANT)
            )
        )

        return rate

    def surface_growth_propensity(
        self, precursor_concentration: float, particle_index: int
    ) -> float:
        """
        Calculate surface growth propensity for a specific particle.

        Parameters
        ----------
        precursor_concentration : float
            Precursor gas concentration (mol/m³)
        particle_index : int
            Index of the particle

        Returns
        -------
        float
            Surface growth rate
        """
        if particle_index >= len(self.particles) or precursor_concentration < 0:
            return 0.0

        particle = self.particles[particle_index]
        surface_area = 4 * np.pi * (particle["radius"] ** 2)

        # Growth rate proportional to surface area and concentration
        growth_coefficient = 1.0e-8
        rate = growth_coefficient * surface_area * precursor_concentration

        return rate

    def coagulation_propensity(self) -> float:
        """
        Calculate coagulation (collision) propensity.

        Returns
        -------
        float
            Coagulation rate
        """
        if len(self.particles) < 2:
            return 0.0

        # Collision frequency based on Brownian motion
        # Simplified: proportional to particle count squared
        collision_coefficient = 1.0e-10
        rate = (
            collision_coefficient
            * (len(self.particles) * (len(self.particles) - 1))
            / 2
        )

        return rate

    def sintering_propensity(self, particle_index: int) -> float:
        """
        Calculate sintering (coalescence) propensity for agglomerate particles.

        Parameters
        ----------
        particle_index : int
            Index of the particle

        Returns
        -------
        float
            Sintering rate
        """
        if particle_index >= len(self.particles):
            return 0.0

        particle = self.particles[particle_index]
        activation_energy = 100000.0  # J/mol
        sintering_coefficient = 1.0e-12

        # Temperature dependent sintering
        rate = sintering_coefficient * np.exp(
            -activation_energy / (self.BOLTZMANN_CONSTANT * self.temperature)
        )

        return rate

    def perform_nucleation(self) -> None:
        """Create a new particle through nucleation."""
        diameter = 1.0e-9  # 1 nanometer
        mass = self._diameter_to_mass(diameter)
        num_atoms = int(mass / (12.0 / self.AVOGADRO_NUMBER))  # Assuming carbon

        self.add_particle(num_atoms, mass, diameter, self.time)
        logger.debug(f"Nucleation event: new particle created")

    def perform_surface_growth(self, particle_index: int) -> None:
        """
        Add atoms to particle surface (growth).

        Parameters
        ----------
        particle_index : int
            Index of particle to grow
        """
        if particle_index >= len(self.particles):
            return

        particle = self.particles[particle_index]
        diameter_increase = 0.1e-9  # Increase by 0.1 nm

        particle["diameter"] += diameter_increase
        particle["radius"] = particle["diameter"] / 2.0
        particle["num_atoms"] += 1
        particle["mass"] = self._diameter_to_mass(particle["diameter"])

        logger.debug(
            f"Surface growth: particle {particle_index} grown to {particle['diameter']*1e9:.2f}nm"
        )

    def perform_coagulation(self) -> None:
        """
        Combine two particles through coagulation.
        """
        if len(self.particles) < 2:
            return

        # Select two random particles
        idx1, idx2 = np.random.choice(
            len(self.particles), size=2, replace=False
        )
        p1 = self.particles[idx1]
        p2 = self.particles[idx2]

        # Conserve mass and atoms
        combined_mass = p1["mass"] + p2["mass"]
        combined_atoms = p1["num_atoms"] + p2["num_atoms"]
        combined_diameter = self._mass_to_diameter(combined_mass)

        # Update first particle with combined properties
        p1["mass"] = combined_mass
        p1["num_atoms"] = combined_atoms
        p1["diameter"] = combined_diameter
        p1["radius"] = combined_diameter / 2.0

        # Remove second particle
        self.particles.pop(max(idx1, idx2))
        if idx1 > idx2:
            self.particles.pop(idx2)

        logger.debug(
            f"Coagulation: particles merged to {combined_diameter*1e9:.2f}nm"
        )

    def perform_sintering(self, particle_index: int) -> None:
        """
        Sinter a particle (reduce surface area at constant volume).

        Parameters
        ----------
        particle_index : int
            Index of particle to sinter
        """
        if particle_index >= len(self.particles):
            return

        particle = self.particles[particle_index]
        # Sintering reduces effective particle size slightly (surface roughness reduction)
        particle["diameter"] *= 0.98

        logger.debug(f"Sintering: particle {particle_index} sintered")

    def _diameter_to_mass(self, diameter: float) -> float:
        """
        Convert particle diameter to mass (assumes spherical particle, density of carbon).

        Parameters
        ----------
        diameter : float
            Particle diameter in meters

        Returns
        -------
        float
            Particle mass in kg
        """
        carbon_density = 2200.0  # kg/m³ (amorphous carbon)
        radius = diameter / 2.0
        volume = (4.0 / 3.0) * np.pi * (radius**3)
        mass = carbon_density * volume
        return mass

    def _mass_to_diameter(self, mass: float) -> float:
        """
        Convert particle mass to diameter (assumes spherical particle, density of carbon).

        Parameters
        ----------
        mass : float
            Particle mass in kg

        Returns
        -------
        float
            Particle diameter in meters
        """
        carbon_density = 2200.0  # kg/m³
        volume = mass / carbon_density
        radius = (3.0 * volume / (4.0 * np.pi)) ** (1.0 / 3.0)
        diameter = 2.0 * radius
        return diameter

    def get_particle_size_distribution(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Get current particle size distribution.

        Returns
        -------
        diameters : np.ndarray
            Particle diameters in meters
        counts : np.ndarray
            Count of particles at each diameter
        """
        diameters = np.array([p["diameter"] for p in self.particles])
        return diameters, np.ones_like(diameters)

    def get_mean_particle_diameter(self) -> float:
        """
        Calculate mean particle diameter.

        Returns
        -------
        float
            Mean diameter in meters
        """
        if len(self.particles) == 0:
            return 0.0
        return np.mean([p["diameter"] for p in self.particles])

    def get_total_particle_volume(self) -> float:
        """
        Calculate total particle volume.

        Returns
        -------
        float
            Total volume in cubic meters
        """
        total_volume = 0.0
        for particle in self.particles:
            radius = particle["radius"]
            volume = (4.0 / 3.0) * np.pi * (radius**3)
            total_volume += volume
        return total_volume

    def get_system_state(self) -> Dict:
        """
        Get current system state as dictionary.

        Returns
        -------
        dict
            System state including time, number of particles, mean diameter, total volume
        """
        return {
            "time": self.time,
            "num_particles": len(self.particles),
            "mean_diameter": self.get_mean_particle_diameter(),
            "total_volume": self.get_total_particle_volume(),
            "temperature": self.temperature,
            "pressure": self.pressure,
        }
