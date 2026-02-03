Running the simulation
=======================

1. Create a virtualenv and install deps (see Makefile).
2. Edit or copy a YAML config from `data/configs/`.
3. Run `python -m sootsim --config path/to/config.yml` or `make setup` followed by `sootsim --config ...`.
4. Outputs live under the configured `output_folder/run_name` as CSV dumps.

Configuration options
---------------------

- `name`: unique identifier used to create the output subfolder.
- `time_end`: simulation horizon in seconds.
- `time_steps`: number of chemistry integration points.
- `initial_species`: dictionary of molar densities (mol/m^3) for the gas stage.
- `population`: overrides for the Monte Carlo particle model (dt, nucleation coefficient, etc.).
- `output_folder`: destination for CSV results (defaults to `outputs`).

The default mechanism is deliberately small to keep the solver stable in the limited runtime required for these tests.
