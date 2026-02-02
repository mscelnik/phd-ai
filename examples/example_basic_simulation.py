"""
Example 1: Basic particle system simulation
Demonstrates fundamental nano-particle formation and growth
"""

import sys

sys.path.insert(0, "..")

from src.particle_system import ParticleSystem
import matplotlib.pyplot as plt
import numpy as np


def main():
    """Run basic particle system simulation."""

    print("=" * 70)
    print("Example 1: Basic Nano-Particle System Simulation")
    print("=" * 70)
    print()

    # Create system
    print("Creating particle system...")
    system = ParticleSystem(
        temperature=1500.0, pressure=101325.0, volume=1.0e-6  # K  # Pa  # m³
    )
    print(f"  Temperature: {system.temperature} K")
    print(f"  Pressure: {system.pressure} Pa")
    print(f"  Volume: {system.volume:.2e} m³")
    print()

    # Simulate nucleation events
    print("Simulating nucleation events...")
    for i in range(20):
        system.perform_nucleation()
    print(f"  Created {len(system.particles)} particles")
    print()

    # Simulate growth
    print("Simulating surface growth...")
    for step in range(100):
        for i in range(len(system.particles)):
            if np.random.random() < 0.5:  # 50% chance of growth
                system.perform_surface_growth(i)

    print(f"  After growth: {len(system.particles)} particles")
    print()

    # Show statistics
    print("Particle system statistics:")
    state = system.get_system_state()
    print(f"  Number of particles: {state['num_particles']}")
    print(f"  Mean diameter: {state['mean_diameter']*1e9:.2f} nm")
    print(f"  Total volume: {state['total_volume']:.2e} m³")
    print()

    # Print particle details
    print("Particle details (first 5):")
    for i, p in enumerate(system.particles[:5]):
        print(
            f"  Particle {i}: diameter={p['diameter']*1e9:.2f} nm, "
            f"mass={p['mass']:.2e} kg, atoms={p['num_atoms']}"
        )
    print()

    # Visualize
    print("Generating visualization...")
    diameters_nm = np.array([p["diameter"] * 1e9 for p in system.particles])

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))

    # Histogram
    ax1.hist(diameters_nm, bins=20, edgecolor="black", alpha=0.7)
    ax1.set_xlabel("Particle Diameter (nm)")
    ax1.set_ylabel("Count")
    ax1.set_title("Particle Size Distribution")
    ax1.grid(True, alpha=0.3)

    # Scatter plot
    masses = np.array([p["mass"] * 1e20 for p in system.particles])
    ax2.scatter(diameters_nm, masses, alpha=0.6)
    ax2.set_xlabel("Particle Diameter (nm)")
    ax2.set_ylabel("Mass (×10⁻²⁰ kg)")
    ax2.set_title("Particle Mass vs Diameter")
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig("example1_particles.png", dpi=100)
    print("  Saved plot to: example1_particles.png")
    print()


if __name__ == "__main__":
    main()
