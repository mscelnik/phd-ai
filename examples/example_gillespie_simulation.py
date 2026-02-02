"""
Example 2: Stochastic simulation with Gillespie algorithm
Demonstrates the population balance model with stochastic events
"""

import sys

sys.path.insert(0, "..")

from src.population_balance import PopulationBalance, ParticleProperty
import matplotlib.pyplot as plt
import numpy as np


def nucleation_event(particles):
    """Add a new particle."""
    if len(particles) < 1000:  # Prevent unlimited growth
        particles.append(
            {
                "id": len(particles),
                "diameter": 1.0e-9,
                "mass": 1.0e-21,
            }
        )


def growth_event(particles):
    """Grow a random particle."""
    if len(particles) > 0:
        idx = np.random.randint(0, len(particles))
        particles[idx]["diameter"] *= 1.02
        particles[idx]["mass"] *= 1.02**3


def coagulation_event(particles):
    """Coagulate two random particles."""
    if len(particles) >= 2:
        idx1, idx2 = np.random.choice(len(particles), size=2, replace=False)
        p1, p2 = particles[idx1], particles[idx2]

        combined_diameter = (p1["diameter"] ** 3 + p2["diameter"] ** 3) ** (
            1 / 3
        )
        p1["diameter"] = combined_diameter
        p1["mass"] = p1["mass"] + p2["mass"]

        particles.pop(max(idx1, idx2))
        if idx1 > idx2:
            particles.pop(idx2)


def main():
    """Run stochastic simulation."""

    print("=" * 70)
    print("Example 2: Stochastic Population Balance Simulation")
    print("=" * 70)
    print()

    # Create model
    print("Creating population balance model...")
    pb = PopulationBalance(
        time_step=1.0e-6, max_time=1.0e-3, num_particles_initial=10
    )

    # Initialize particles
    properties = [
        ParticleProperty("diameter", 1.0e-9, "Particle diameter"),
        ParticleProperty("mass", 1.0e-21, "Particle mass"),
    ]
    pb.initialize_particles(properties)
    print(f"  Initialized with {pb.num_particles_initial} particles")
    print()

    # Register events
    print("Registering reaction events...")

    def nucleation_propensity(particles, time):
        return max(0, 50 - len(particles)) * 1e3

    def growth_propensity(particles, time):
        return len(particles) * 100

    def coagulation_propensity(particles, time):
        n = len(particles)
        return n * (n - 1) / 2 * 1e-2 if n > 1 else 0

    pb.add_reaction_event(
        "nucleation",
        lambda p, t: nucleation_propensity(p, t),
        nucleation_propensity,
        nucleation_event,
    )

    pb.add_reaction_event(
        "growth",
        lambda p, t: growth_propensity(p, t),
        growth_propensity,
        growth_event,
    )

    pb.add_reaction_event(
        "coagulation",
        lambda p, t: coagulation_propensity(p, t),
        coagulation_propensity,
        coagulation_event,
    )

    print(f"  Registered {len(pb.reaction_events)} reaction events")
    print()

    # Run simulation
    print("Running Gillespie simulation...")
    pb.simulate(num_steps=5000)
    print(f"  Simulation completed")
    print(f"  Final time: {pb.current_time:.6e} s")
    print(f"  Number of steps: {len(pb.history['time'])}")
    print()

    # Results
    print("Final system state:")
    print(f"  Particles: {pb.history['num_particles'][-1]}")
    print(f"  Mean diameter: {pb.history['avg_diameter'][-1]*1e9:.2f} nm")
    print(f"  Total mass: {pb.history['total_mass'][-1]:.2e} kg")
    print()

    # Visualize
    print("Generating visualization...")
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))

    times = np.array(pb.history["time"]) * 1e3  # Convert to ms

    # Particle count
    axes[0, 0].plot(times, pb.history["num_particles"], "b-", linewidth=2)
    axes[0, 0].set_xlabel("Time (ms)")
    axes[0, 0].set_ylabel("Number of Particles")
    axes[0, 0].set_title("Particle Population Evolution")
    axes[0, 0].grid(True, alpha=0.3)

    # Mean diameter
    mean_diameters_nm = np.array(pb.history["avg_diameter"]) * 1e9
    axes[0, 1].plot(times, mean_diameters_nm, "g-", linewidth=2)
    axes[0, 1].set_xlabel("Time (ms)")
    axes[0, 1].set_ylabel("Mean Diameter (nm)")
    axes[0, 1].set_title("Mean Particle Size Evolution")
    axes[0, 1].grid(True, alpha=0.3)

    # Total mass
    axes[1, 0].plot(times, pb.history["total_mass"], "r-", linewidth=2)
    axes[1, 0].set_xlabel("Time (ms)")
    axes[1, 0].set_ylabel("Total Mass (kg)")
    axes[1, 0].set_title("Total Particle Mass Evolution")
    axes[1, 0].grid(True, alpha=0.3)

    # Final size distribution
    if len(pb.particles) > 0:
        diameters_nm = np.array([p["diameter"] * 1e9 for p in pb.particles])
        axes[1, 1].hist(diameters_nm, bins=20, edgecolor="black", alpha=0.7)
        axes[1, 1].set_xlabel("Particle Diameter (nm)")
        axes[1, 1].set_ylabel("Count")
        axes[1, 1].set_title("Final Particle Size Distribution")
        axes[1, 1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig("example2_gillespie_simulation.png", dpi=100)
    print("  Saved plot to: example2_gillespie_simulation.png")
    print()


if __name__ == "__main__":
    main()
