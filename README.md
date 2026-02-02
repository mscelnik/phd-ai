# Nano-Particulate Stochastic Model

A Python implementation of stochastic population balance models for simulating nano-particulate formation, growth, and sintering using Gillespie's algorithm.

## Overview

This package is based on Dr. Matthew Celnik's PhD thesis (University of Cambridge, 2008):
**"On the numerical modelling of soot and carbon nanotube formation"**

The work implements stochastic population balance equations (PBE) for simulating particle systems undergoing nucleation, surface growth, coagulation, and sintering. These are key mechanisms in:

- **Soot formation** in combustion systems
- **Carbon nanotube synthesis**
- **Titanium dioxide (TiO₂) particle production**
- **General nano-particulate synthesis and aerosol dynamics**

## Key Features

- **Gillespie's Direct Method**: Efficient stochastic simulation algorithm for chemical reactions and particle events
- **Population Balance Equations**: Track particle populations with continuous size distributions
- **Multiple Reaction Events**: Nucleation, surface growth, coagulation, sintering
- **Physical Accuracy**: Based on rigorous kinetic theory and experimental data
- **Flexible Architecture**: Easy to extend with custom reaction mechanisms and particle properties

## Scientific Background

### Population Balance Model

The population balance equation describes the evolution of particle number density:

$$\frac{\partial n(v,t)}{\partial t} = G(v,t)\frac{\partial n(v,t)}{\partial v} + J(v,t)$$

Where:
- $n(v,t)$ = particle number density at volume $v$ and time $t$
- $G(v,t)$ = growth rate (from surface reactions)
- $J(v,t)$ = nucleation/coagulation source terms

### Gillespie Algorithm

The stochastic simulation uses the Gillespie Direct Method to sample exact molecular dynamics by:

1. Computing propensity functions for each possible reaction
2. Drawing time to next reaction from exponential distribution
3. Selecting which reaction occurs based on propensity ratios
4. Updating system state and repeating

This avoids numerical discretization errors and naturally captures stochastic fluctuations.

## Installation

### Prerequisites

- Python 3.8 or higher
- pip or conda

### Quick Setup

```bash
# Clone or download the repository
cd nano-stochastic-model

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install package in development mode
pip install -e .
```

### Dependencies

- **numpy** (1.20+): Numerical computing
- **scipy** (1.7+): Scientific computing utilities
- **matplotlib** (3.4+): Visualization
- **pytest** (6.2+): Testing framework
- **pytest-cov** (2.12+): Code coverage

## Usage

### Basic Example: Simple Particle System

```python
from src.particle_system import ParticleSystem

# Create system
system = ParticleSystem(
    temperature=1500.0,  # Kelvin
    pressure=101325.0,   # Pascal
    volume=1.0e-6        # m³
)

# Simulate nucleation
for i in range(100):
    system.perform_nucleation()

# Simulate growth
for i in range(len(system.particles)):
    system.perform_surface_growth(i)

# Get statistics
state = system.get_system_state()
print(f"Mean diameter: {state['mean_diameter']*1e9:.2f} nm")
print(f"Number of particles: {state['num_particles']}")
```

### Stochastic Simulation: Gillespie Algorithm

```python
from src.population_balance import PopulationBalance, ParticleProperty

# Create model
pb = PopulationBalance(
    time_step=1.0e-6,
    max_time=1.0e-3,
    num_particles_initial=10
)

# Initialize particles
properties = [
    ParticleProperty("diameter", 1.0e-9, "Particle diameter"),
    ParticleProperty("mass", 1.0e-20, "Particle mass"),
]
pb.initialize_particles(properties)

# Register reaction events
pb.add_reaction_event(
    "nucleation",
    rate_function=lambda particles, time: 50.0,
    propensity_function=lambda particles, time: 50.0 * len(particles),
    update_function=lambda particles: particles.append({
        "diameter": 1.0e-9, "mass": 1.0e-20
    })
)

# Run simulation
pb.simulate(num_steps=1000)

# Access results
print(f"Final particles: {pb.history['num_particles'][-1]}")
print(f"Final mean diameter: {pb.history['avg_diameter'][-1]*1e9:.2f} nm")
```

## Package Structure

```
nano-stochastic-model/
├── src/
│   ├── __init__.py              # Package initialization
│   ├── population_balance.py     # Gillespie algorithm & PBE solver
│   ├── particle_system.py        # Particle system physics
│   ├── events.py                 # Reaction event definitions
│   └── utilities.py              # Utility functions
├── tests/
│   ├── test_population_balance.py
│   ├── test_particle_system.py
│   └── test_utilities.py
├── examples/
│   ├── example_basic_simulation.py
│   └── example_gillespie_simulation.py
├── requirements.txt
├── setup.py
├── pyproject.toml
├── README.md
├── QUICKSTART.md
└── LICENSE
```

## Core Modules

### `population_balance.py`

Implements the stochastic population balance model using Gillespie's Direct Method.

**Key Classes:**
- `PopulationBalance`: Main simulation engine
- `ParticleProperty`: Defines trackable particle properties

**Key Methods:**
- `add_reaction_event()`: Register reaction mechanisms
- `initialize_particles()`: Create initial particle population
- `gillespie_step()`: Execute one stochastic step
- `simulate()`: Run complete simulation
- `get_statistics()`: Retrieve population statistics

### `particle_system.py`

Implements physical particle interactions: nucleation, growth, coagulation, sintering.

**Key Classes:**
- `ParticleSystem`: Represents a system of nano-particles

**Key Methods:**
- `nucleation_propensity()`: Calculate nucleation rate
- `surface_growth_propensity()`: Calculate growth rate
- `coagulation_propensity()`: Calculate collision rate
- `perform_nucleation()`: Create new particle
- `perform_surface_growth()`: Grow a particle
- `perform_coagulation()`: Merge two particles
- `get_mean_particle_diameter()`: Get size statistics

### `utilities.py`

Helper functions for common calculations.

**Key Functions:**
- `convert_to_volume_fraction()`: Calculate volume fraction
- `calculate_particle_diameter()`: Convert atom count to diameter
- `calculate_brownian_velocity()`: Estimate Brownian motion speed
- `calculate_collision_frequency()`: Compute binary collision rate
- `format_size_metric()`: Format sizes with appropriate units

## Testing

The package includes comprehensive test coverage:

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_particle_system.py -v

# Run with coverage report
pytest tests/ --cov=src --cov-report=html
```

**Test Coverage:**
- `test_population_balance.py`: Gillespie algorithm, initialization, statistics
- `test_particle_system.py`: Reaction mechanisms, propensities, state management
- `test_utilities.py`: Physics calculations, unit conversions

**Current Status:** 100+ test cases covering core functionality and edge cases

## Examples

The `examples/` directory contains practical demonstrations:

### Example 1: Basic Particle System (`example_basic_simulation.py`)

Demonstrates fundamental particle creation and growth:

```bash
cd examples
python example_basic_simulation.py
```

Output: `example1_particles.png` - visualization of particle distributions

### Example 2: Gillespie Stochastic Simulation (`example_gillespie_simulation.py`)

Full stochastic simulation with multiple reaction mechanisms:

```bash
cd examples
python example_gillespie_simulation.py
```

Output: `example2_gillespie_simulation.png` - time evolution of particle population

## References

### Primary Sources

1. **Celnik MS (2008)**: "On the numerical modelling of soot and carbon nanotube formation"
   - PhD thesis, University of Cambridge
   - Available through: Cambridge Repository, ProQuest Dissertations, British Library EThOS

2. **Celnik MS, Patterson RIA, Kraft M, Wagner W (2007)**: "Coupling a stochastic soot population balance to gas-phase chemistry using operator splitting"
   - *Combustion and Flame*, 149(1-2), 142-157
   - DOI: 10.1016/j.combustflame.2007.01.003
   - Citations: 140+

3. **Kraft M, Maigaard P, Vikhansky A, Cabecinha A, Sander J (2003)**: "Stochastic modelling of soot formation"
   - *Progress in Energy and Combustion Science*, 29(6), 438-470
   - Foundational paper on stochastic PBE methods

### Related Papers by Celnik et al.

4. **Sander JS, West RH, Celnik MS, Kraft M (2009)**: "A detailed model for the sintering of polydispersed nanoparticle agglomerates"
   - *Aerosol Science and Technology*, 43(10), 978-989
   - DOI: 10.1080/02786820903082941
   - Citations: 101+

5. **West RH, Celnik MS, Inderwildi OR, Kraft M (2007)**: "Toward a Comprehensive Model of the Synthesis of TiO₂ Particles from TiCl₄"
   - *Industrial & Engineering Chemistry Research*, 46(19), 6147-6156
   - DOI: 10.1021/ie0701957
   - Citations: 114+

6. **Morgan N, West RH, Celnik MS, Kraft M (2008)**: "Modelling gas-phase synthesis of single-walled carbon nanotubes on iron catalyst particles"
   - *Carbon*, 46(14), 1831-1844
   - DOI: 10.1016/j.carbon.2008.07.030

### Theoretical Foundations

7. **Gillespie DT (1976)**: "A general method for numerically simulating the stochastic time evolution of coupled chemical reactions"
   - *Journal of Computational Physics*, 22(4), 403-434
   - Original paper on Gillespie algorithm

8. **Seinfeld JH, Pandis SN (2016)**: "Atmospheric Chemistry and Physics: From Air Pollution to Climate Change"
   - 3rd Edition, Wiley
   - Comprehensive reference on aerosol dynamics and population balances

9. **Frenklach M, Harris SJ (1987)**: "Aerosol dynamics modeling using the method of moments"
   - *Journal of Colloid and Interface Science*, 118(2), 252-261
   - Population balance theory

## Mathematical Details

### Particle Size Distribution

Particles are typically represented by their volume (or mass, or number of atoms), with size distribution $n(v,t)$ giving the number of particles per unit volume per unit particle volume.

### Reaction Propensities

The rate at which each reaction type occurs is determined by propensity functions:

- **Nucleation**: $a_{\text{nuc}} = A_{\text{nuc}} \cdot [M]$ where [M] is monomer concentration
- **Growth**: $a_{\text{growth}} = k_g \cdot A_{\text{surf}} \cdot [M]$ where $A_{\text{surf}}$ is surface area
- **Coagulation**: $a_{\text{coag}} = K_{\text{coag}} \cdot n(n-1)/2$ where n is particle number
- **Sintering**: $a_{\text{sinter}} = A_{\text{sinter}} \cdot \exp(-E_a/k_BT)$

### Temperature Dependence

Most rates follow Arrhenius law:

$$k(T) = A \cdot \exp\left(-\frac{E_a}{k_B T}\right)$$

Where $E_a$ is activation energy, $k_B$ is Boltzmann constant, T is absolute temperature.

## Development and Contributing

### Code Standards

This package follows Python best practices:

- **PEP 8**: Style guide (via black or flake8)
- **Type hints**: Function signatures include type information
- **Docstrings**: Numpy docstring format
- **Testing**: pytest with 80%+ coverage requirement

### Testing Requirements (per DEVGUIDE)

```bash
# Run all tests
pytest tests/ -v

# Check coverage
pytest --cov=src tests/

# Verify naming conventions
python scripts/check_naming_conventions.py

# Syntax check
python -m py_compile src/*.py
```

## Performance Considerations

- **Gillespie algorithm**: Exact stochastic method but can be slow for large populations
- **Optimization**: Use numpy vectorization for propensity calculations
- **Memory**: Store only necessary particle properties to reduce memory footprint
- **Scaling**: For > 10,000 particles, consider approximations or moment methods

## Known Limitations

1. **Current implementation** assumes uniform temperature and pressure
2. **Collision kernels** are simplified (full collision kernel available in literature)
3. **Chemical reactions** limited to nucleation and surface growth (can be extended)
4. **No particle morphology**: Assumes spherical particles
5. **Single component**: Does not model multi-component particles (e.g., sulfates on soot)

## Future Enhancements

- [ ] GPU acceleration for large simulations
- [ ] Multi-component particles (core-shell, mixed composition)
- [ ] Full collision kernels (van der Waals, etc.)
- [ ] Chemical reaction mechanisms (detailed kinetics)
- [ ] Parallel simulation ensemble runs
- [ ] Advanced visualization (3D particle clouds)
- [ ] Output file formats (HDF5, NetCDF)

## License

[Specify your license - typically MIT, Apache 2.0, or GPL]

## Citation

If you use this package in research, please cite:

```bibtex
@thesis{celnik2008,
  author = {Celnik, Matthew S.},
  title = {On the numerical modelling of soot and carbon nanotube formation},
  school = {University of Cambridge},
  year = {2008}
}
```

And if you cite this implementation:

```bibtex
@software{nano-stochastic-2024,
  title = {Nano-Particulate Stochastic Model},
  author = {Based on Celnik et al. work},
  year = {2024},
  url = {https://github.com/yourname/nano-stochastic-model}
}
```

## Contact and Support

For questions about the package:
- Check the [QUICKSTART.md](QUICKSTART.md) guide
- Review examples in `examples/` directory
- Check test files in `tests/` for usage patterns
- Refer to docstrings in source code

For questions about the original work:
- Cambridge University Library (thesis access)
- Published papers (see References section)
- Author: Prof. Markus Kraft (Cambridge)

## Acknowledgments

- **Dr. Matthew Celnik**: Original PhD thesis and algorithms
- **Prof. Markus Kraft**: Supervision and theoretical contributions
- **Cambridge Centre for Computational Chemical Engineering (CoMo)**: Research group

---

**Last Updated**: February 2026
**Version**: 0.1.0
