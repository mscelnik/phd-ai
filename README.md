# PhD AI Simulation Suite

This repository contains a Python implementation of the physical model simulator for nano-particle formation (soot and carbon nanotubes), based on the original work from the University of Cambridge CoMo group.

## Structure
- `src/`: Python source code
- `tests/`: Unit and integration tests
- `data/`: Input data files
- `refs/`: Reference papers, thesis, and source material
- `scripts/`: Run scripts

## Setup
1. Create and activate a Python virtual environment:
   ```sh
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. Run tests:
   ```sh
   make test
   ```
3. Run simulation:
   ```sh
   python scripts/run_simulation.py src/input_schema.yaml
   ```

## Input/Output
- Input: YAML or JSON config files (see `src/input_schema.yaml`)
- Output: Human-readable CSV/Excel files (to be implemented)

## References
All relevant papers, thesis, and code sources are stored in `refs/`. See below for a list of included sources.

## Documentation
- Code is documented inline.
- Sphinx documentation can be generated (to be set up).

## License
MIT
