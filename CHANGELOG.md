# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-01-01

### Added
- Initial release of the nanoparticle formation simulator
- Gas-phase chemistry module with Cantera integration
- Particle population balance with stochastic Monte Carlo solver
- Nucleation, growth, coagulation, and oxidation processes
- Batch reactor model with operator splitting
- Strang splitting and predictor-corrector coupling algorithms
- YAML/JSON configuration file support
- CSV and Excel output formats
- Command-line interface
- Comprehensive test suite (unit, integration, end-to-end)
- Full documentation

### Technical Details
- Python 3.10+ support
- Cantera 3.2.0 for gas-phase chemistry
- GRI-Mech 3.0 as default mechanism (53 species, 325 reactions)
- BDF integrator for stiff chemistry ODE system
- Statistical weight doubling/halving for ensemble size control
