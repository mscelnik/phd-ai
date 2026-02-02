# QUICKSTART Guide - Nano-Particulate Stochastic Model

Get up and running in 5 minutes!

## Table of Contents

1. [Installation](#installation)
2. [First Run](#first-run)
3. [Basic Usage](#basic-usage)
4. [Common Tasks](#common-tasks)
5. [Troubleshooting](#troubleshooting)

---

## Installation

### Step 1: Create Virtual Environment

On **Windows**:
```bash
python -m venv venv
venv\Scripts\activate
```

On **Linux/Mac**:
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- numpy (numerical computing)
- scipy (scientific functions)
- matplotlib (plotting)
- pytest (testing)

### Step 3: Verify Installation

```bash
pytest tests/ -v
```

You should see all tests pass (✓).

---

## First Run

### Run Example 1: Basic Particle Simulation

```bash
cd examples
python example_basic_simulation.py
```

**What happens:**
- Creates 20 particles through nucleation
- Grows particles for 100 steps
- Displays statistics
- Saves plot: `example1_particles.png`

**Expected output:**
```
======================================================================
Example 1: Basic Nano-Particle System Simulation
======================================================================

Creating particle system...
  Temperature: 1500 K
  Pressure: 101325 Pa
  Volume: 1e-06 m³

Simulating nucleation events...
  Created 20 particles

Simulating surface growth...

Particle system statistics:
  Number of particles: 20
  Mean diameter: 2.34 nm
  Total volume: 6.72e-23 m³

Generating visualization...
  Saved plot to: example1_particles.png
```

### Run Example 2: Gillespie Stochastic Simulation

```bash
python example_gillespie_simulation.py
```

**What happens:**
- Creates stochastic model with nucleation, growth, coagulation
- Runs 5000 Gillespie algorithm steps
- Tracks system evolution over time
- Generates 4-panel visualization

**Expected output:**
```
======================================================================
Example 2: Stochastic Population Balance Simulation
======================================================================

Creating population balance model...
  Initialized with 10 particles

Running Gillespie simulation...
  Simulation completed
  Final time: 1.000000e-03 s

Final system state:
  Particles: 45
  Mean diameter: 3.21 nm
  Total mass: 1.87e-19 kg

Generating visualization...
  Saved plot to: example2_gillespie_simulation.png
```

---

## Basic Usage

### Create a Particle System

```python
from src.particle_system import ParticleSystem

# Create system at high temperature
system = ParticleSystem(
    temperature=1500.0,  # Kelvin
    pressure=101325.0,   # Pascals (1 atm)
    volume=1.0e-6        # m³ (1 cm³)
)
```

**System parameters:**
- `temperature`: Affects reaction rates and Brownian motion (100-5000 K typical)
- `pressure`: Affects gas properties (atmospheric pressure typical)
- `volume`: Affects particle number density

### Add Particles

```python
# Create a single particle
system.add_particle(
    num_atoms=1000,      # Number of carbon atoms
    mass=1.0e-20,        # kg
    diameter=5.0e-9      # meters (5 nm)
)

# Or simulate nucleation (creates 1 nm particles)
system.perform_nucleation()
```

### Simulate Processes

```python
# Surface growth: molecule sticks to particle surface
system.perform_surface_growth(particle_index=0)

# Coagulation: two particles collide and merge
system.perform_coagulation()

# Sintering: reduce surface roughness at constant volume
system.perform_sintering(particle_index=0)
```

### Get Results

```python
# Get current state
state = system.get_system_state()
print(f"Particles: {state['num_particles']}")
print(f"Mean diameter: {state['mean_diameter']*1e9:.2f} nm")
print(f"Total volume: {state['total_volume']:.2e} m³")

# Get size distribution
diameters, counts = system.get_particle_size_distribution()
```

---

## Common Tasks

### Task 1: Simulate Nucleation-Only System

What: Create particles without growth or merging

```python
from src.particle_system import ParticleSystem

system = ParticleSystem(temperature=1500.0)

# Create 100 nucleation events
for i in range(100):
    system.perform_nucleation()

state = system.get_system_state()
print(f"Created {state['num_particles']} particles")
print(f"All diameter: {state['mean_diameter']*1e9:.2f} nm (should be ~1 nm)")
```

### Task 2: Study Temperature Effects on Sintering

What: Compare sintering rates at different temperatures

```python
from src.particle_system import ParticleSystem

for temp in [500, 1000, 1500, 2000]:
    ps = ParticleSystem(temperature=temp)
    ps.add_particle(num_atoms=1000, mass=1.0e-20, diameter=5.0e-9)

    sintering_rate = ps.sintering_propensity(0)
    print(f"T={temp}K: sintering_rate={sintering_rate:.2e}")
```

Expected: Higher temperature → faster sintering

### Task 3: Track Particle Growth Over Time

What: Simulate surface growth and track diameter evolution

```python
from src.particle_system import ParticleSystem
import numpy as np

system = ParticleSystem(temperature=1500.0)
system.perform_nucleation()

diameters = []
times = []

for step in range(1000):
    if step % 100 == 0:
        diameters.append(system.particles[0]['diameter'])
        times.append(step)

    system.perform_surface_growth(0)

# Plot
import matplotlib.pyplot as plt
plt.plot(times, np.array(diameters)*1e9, 'o-')
plt.xlabel('Step')
plt.ylabel('Diameter (nm)')
plt.show()
```

### Task 4: Run Gillespie Stochastic Simulation

What: Full stochastic simulation with multiple reactions

```python
from src.population_balance import PopulationBalance, ParticleProperty

# Create model
pb = PopulationBalance(max_time=1.0e-3, num_particles_initial=20)

# Initialize
properties = [
    ParticleProperty("diameter", 1.0e-9),
    ParticleProperty("mass", 1.0e-20),
]
pb.initialize_particles(properties)

# Add reactions
def nucleation_update(particles):
    if len(particles) < 1000:
        particles.append({"diameter": 1.0e-9, "mass": 1.0e-20})

pb.add_reaction_event(
    "nucleation",
    lambda p, t: 50.0,  # Rate
    lambda p, t: 50.0 * (1000 - len(p)),  # Propensity
    nucleation_update
)

# Simulate
pb.simulate(num_steps=10000)

# Results
print(f"Final particles: {pb.history['num_particles'][-1]}")
print(f"Final time: {pb.current_time:.2e} s")
```

### Task 5: Calculate Physical Properties

What: Use utility functions for physics calculations

```python
from src.utilities import (
    calculate_particle_diameter,
    calculate_brownian_velocity,
    calculate_collision_frequency,
    format_size_metric
)

# Convert atom count to diameter
diameter = calculate_particle_diameter(num_atoms=5000)
print(f"Diameter: {format_size_metric(diameter)}")

# Calculate Brownian motion
velocity = calculate_brownian_velocity(temperature=1500.0, particle_diameter=10.0e-9)
print(f"Brownian velocity: {velocity:.2e} m/s")

# Calculate collision frequency
freq = calculate_collision_frequency(
    num_particles=100,
    particle_diameter=10.0e-9,
    temperature=1500.0,
    system_volume=1.0e-6
)
print(f"Collision frequency: {freq:.2e} /s")
```

---

## Troubleshooting

### Problem: Import Error - "No module named 'src'"

**Solution**: Make sure you're running from the project root directory:
```bash
cd nano-stochastic-model  # Main project folder
python -c "from src.particle_system import ParticleSystem"
```

### Problem: Tests Fail with ModuleNotFoundError

**Solution**: Install in development mode:
```bash
pip install -e .
```

Then run tests:
```bash
pytest tests/ -v
```

### Problem: No plot displayed

**Solution**: Plots are saved to disk, not displayed. Check:
- `examples/example1_particles.png`
- `examples/example2_gillespie_simulation.png`

Or modify example to use interactive mode:
```python
import matplotlib.pyplot as plt
plt.ion()  # Interactive mode
plt.show()
```

### Problem: Simulation is too slow

**Solutions**:
1. Reduce `num_particles_initial` in PopulationBalance
2. Reduce `num_steps` in `simulate()` call
3. Reduce `max_time` parameter
4. Check system resources (RAM, CPU)

Example:
```python
# Fast simulation
pb = PopulationBalance(
    max_time=1.0e-5,  # Shorter time
    num_particles_initial=5  # Fewer particles
)
pb.simulate(num_steps=100)  # Fewer steps
```

### Problem: Memory issues with large populations

**Solutions**:
1. Don't store all particles in memory - use moment methods instead
2. Reduce particle count
3. Store only essential properties

```python
# Store only diameter and mass (not formation_time, etc.)
particle = {
    "id": len(particles),
    "diameter": diameter,
    "mass": mass,
}
```

### Problem: Need help with physics

**Resources**:
- Read docstrings: `help(ParticleSystem)` or `help(ParticleSystem.nucleation_propensity)`
- Check examples: `examples/` folder
- See README.md for theoretical background
- Original thesis and papers (see README references)

---

## Next Steps

### Learn More

1. **Read the README**: Full documentation and theory
2. **Review examples**: Practical demonstrations
3. **Check tests**: Usage patterns and edge cases
4. **Explore source code**: See implementation details

### Customize

Modify parameters:
```python
# Different temperature
system = ParticleSystem(temperature=2500.0)

# Custom propensity function
def my_nucleation_propensity(particles, time):
    return 100.0 * (time / 0.001)  # Increase over time
```

Extend with new reactions:
```python
def my_reaction_update(particles):
    # Custom logic here
    pass

pb.add_reaction_event(
    "my_reaction",
    rate_function=lambda p, t: 1.0,
    propensity_function=my_propensity,
    update_function=my_reaction_update
)
```

### Run Tests

```bash
# All tests
pytest tests/ -v

# Specific test
pytest tests/test_particle_system.py::TestParticleSystem::test_nucleation_event -v

# With coverage
pytest tests/ --cov=src
```

---

## Key Keyboard Shortcuts & Commands

| Command | Purpose |
|---------|---------|
| `python example_basic_simulation.py` | Run Example 1 |
| `python example_gillespie_simulation.py` | Run Example 2 |
| `pytest tests/ -v` | Run all tests |
| `python -m pytest tests/ --cov=src` | Run tests with coverage |
| `python -c "from src.particle_system import ParticleSystem"` | Test import |
| `venv\Scripts\activate` | Activate venv (Windows) |
| `source venv/bin/activate` | Activate venv (Linux/Mac) |

---

## Support

- 📖 **Documentation**: See README.md
- 🔍 **Examples**: Check `examples/` folder
- ✅ **Tests**: Review `tests/` for usage patterns
- 📚 **Theory**: See References section in README

**Happy Simulating!** 🚀

---

**Last Updated**: February 2026
**Version**: 0.1.0
