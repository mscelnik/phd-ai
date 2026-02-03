"""Command-line entry point for running the soot & nanotube simulations."""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

from .io import SimulationConfig
from .simulation import run_simulation


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="sootsim",
        description="Run a coupled gas-phase and particle population simulation.",
    )
    parser.add_argument(
        "-c",
        "--config",
        type=Path,
        required=True,
        help="Path to YAML run configuration",
    )
    parsed = parser.parse_args(argv)
    config = SimulationConfig.load(parsed.config)
    result = run_simulation(config)
    print(
        f"Simulation '{result.config.name}' finished. Results written to {result.config.output_folder / result.config.name}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
