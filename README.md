# Nanoparticle Formation Simulator

A Python package for simulating nanoparticle (soot and carbon nanotube) formation in combustion systems, combining detailed gas-phase chemistry with stochastic particle population balance modeling.

## Overview

This simulator recreates the numerical methods from Matthew Celnik's PhD thesis on soot and CNT formation, originally implemented in Fortran 77/90 and C++. The code couples:

- **Gas-phase chemistry**: Detailed chemical kinetics using Cantera
- **Particle population balance**: Stochastic Monte Carlo method for particle dynamics
- **Operator splitting**: Efficient coupling of the two solvers

## Features

- Detailed gas-phase chemistry with GRI-Mech 3.0 (53 species, 325 reactions)
- Stochastic particle model with nucleation, growth, coagulation, and oxidation
- Strang splitting and predictor-corrector coupling algorithms
- Human-readable YAML/JSON configuration files
- CSV and Excel output formats
- Comprehensive test suite

## Installation

### Prerequisites

- Python 3.10 or higher
- Cantera 3.2.0 or higher

### Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/phd-ai.git
cd phd-ai

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install the package
pip install -e ".[dev]"
```

Or using the Makefile:

```bash
make setup
```

## Quick Start

### Command Line Interface

```bash
# Generate an example configuration file
nanoparticle-sim example --output my_config.yaml

# Validate a configuration file
nanoparticle-sim validate my_config.yaml

# Run a simulation
nanoparticle-sim run my_config.yaml
```

### Python API

```python
from nanoparticle_simulator.chemistry.gas_phase import GasPhase
from nanoparticle_simulator.reactor.batch import create_batch_reactor
from nanoparticle_simulator.io.output import write_csv

# Set up gas-phase chemistry
gas = GasPhase()
gas.load_mechanism("gri30.yaml")
gas.set_state_TPX(
    1800.0,              # Temperature (K)
    101325.0,            # Pressure (Pa)
    {"CH4": 0.055, "O2": 0.11, "N2": 0.835}  # Mole fractions
)

# Create reactor with particle modeling
reactor = create_batch_reactor(
    gas=gas,
    volume=1e-6,         # 1 cm³
    enable_particles=True,
    particle_processes=["nucleation", "growth", "coagulation", "oxidation"],
)

# Run simulation
result = reactor.run(
    duration=0.005,      # 5 ms
    dt=1e-6,             # 1 μs time step
    output_interval=1e-4, # 100 μs output interval
)

# Save results
write_csv(result, "output/simulation_results.csv")
```

## Configuration

Simulations are configured using YAML files:

```yaml
name: "Soot Formation Simulation"

gas:
  mechanism: "gri30.yaml"
  temperature: 1800.0      # K
  pressure: 101325.0       # Pa
  composition:
    CH4: 0.055
    O2: 0.11
    N2: 0.835

particles:
  enabled: true
  nucleation_enabled: true
  growth_enabled: true
  coagulation_enabled: true
  oxidation_enabled: true

reactor:
  reactor_type: "batch"
  volume: 1.0e-6           # m³
  constant_pressure: true
  splitting_type: "strang"

solver:
  duration: 0.005          # s
  time_step: 1.0e-6        # s
  output_interval: 1.0e-4  # s

output:
  directory: "output"
  format: "csv"
```

See [examples/soot_formation.yaml](examples/soot_formation.yaml) for a complete example.

## Project Structure

```
phd-ai/
├── src/nanoparticle_simulator/
│   ├── chemistry/        # Gas-phase chemistry (Cantera interface)
│   ├── particles/        # Particle population balance
│   ├── reactor/          # Reactor models and operator splitting
│   ├── io/               # Configuration and output handling
│   └── utils/            # Utilities and constants
├── tests/
│   ├── unit/             # Unit tests
│   ├── integration/      # Integration tests
│   └── e2e/              # End-to-end tests
├── examples/             # Example configuration files
├── data/                 # Reaction mechanisms and data
└── output/               # Simulation output (generated)
```

## Scientific Background

### Particle Model

The particle model uses a detailed description tracking:
- Carbon atom count (particle size)
- Hydrogen atom count (composition)
- Primary particle count (aggregation)
- Active surface sites (aromatic site model)

### Processes

1. **Nucleation**: Formation of nascent particles from PAH precursors (pyrene dimerization)
2. **Surface Growth**: HACA mechanism (H-abstraction, C₂H₂-addition)
3. **Coagulation**: Free-molecular collision kernel
4. **Oxidation**: Attack by O₂ and OH radicals

### Operator Splitting

The code implements:
- **Strang splitting**: Second-order accurate symmetric splitting
- **Predictor-corrector**: Improved accuracy for strongly coupled systems

## Testing

```bash
# Run all tests
make test

# Run with coverage
pytest --cov=nanoparticle_simulator tests/

# Run specific test categories
pytest tests/unit/
pytest tests/integration/
pytest tests/e2e/
```

## References

1. M.S. Celnik, "Modelling soot formation in turbulent flames", PhD Thesis, University of Cambridge, 2007.

2. M.S. Celnik, M. Sander, A. Raj, R.H. West, M. Kraft, "Modelling soot formation in a premixed flame using an aromatic-site soot model and an improved rate constant for soot mass growth", Combustion and Flame 155 (2008) 161-180.

3. M.S. Celnik, A. Raj, R. West, R. Patterson, M. Kraft, "A statistical approach to develop a detailed soot growth model using PAH characteristics", Combustion and Flame 155 (2008) 161-180.

4. M. Sander, R.I.A. Patterson, A. Braumann, A. Raj, M. Kraft, "Developing the PAH-PP soot particle model using process informatics and uncertainty propagation", Proceedings of the Combustion Institute 33 (2011) 675-683.

5. G.P. Smith et al., "GRI-Mech 3.0", http://combustion.berkeley.edu/gri-mech/version30/text30.html

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Original PhD research conducted at the University of Cambridge
- Computational Modelling Group (CoMoGroup)
- Cantera developers for the excellent chemistry toolkit
