# PhD AI Simulation Suite

This repository contains a Python implementation of the physical model simulations for nano-particle formation, including:

1. **Gas-phase chemistry solver**: Simulates reaction kinetics for gas-phase species.
2. **Particle population-balance model**: Models the dynamics of particle populations using stochastic methods.

## Features
- Human-readable input files (YAML).
- Outputs in CSV format for easy analysis.
- Modular and extensible design.
- Thorough unit and integration tests.

## Setup
1. Clone the repository:
   ```bash
   git clone <repository-url>
   ```
2. Navigate to the project directory:
   ```bash
   cd phd-ai
   ```
3. Set up the Python environment:
   ```bash
   make setup
   ```

## Usage
1. Prepare an input YAML file with the required parameters.
2. Run the simulation scripts (to be implemented).
3. View results in the `output/` directory.

## Testing
Run the following command to execute all tests:
```bash
make test
```
