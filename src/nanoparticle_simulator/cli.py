#!/usr/bin/env python
"""
Command-line interface for nanoparticle simulator.

Usage:
    nanoparticle-sim run config.yaml
    nanoparticle-sim validate config.yaml
    nanoparticle-sim example --output example_config.yaml
"""

import argparse
import logging
import sys
from pathlib import Path

from nanoparticle_simulator.io.config import (
    SimulationConfig,
    load_config,
    save_config,
    create_default_config,
)
from nanoparticle_simulator.utils.logging_config import setup_logging


def main() -> int:
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description="Nanoparticle formation simulator",
        prog="nanoparticle-sim",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose output",
    )
    parser.add_argument(
        "--log-file",
        type=str,
        help="Log file path",
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Run command
    run_parser = subparsers.add_parser("run", help="Run a simulation")
    run_parser.add_argument(
        "config",
        type=str,
        help="Configuration file (YAML or JSON)",
    )
    run_parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="Output directory (overrides config)",
    )

    # Validate command
    validate_parser = subparsers.add_parser(
        "validate",
        help="Validate a configuration file",
    )
    validate_parser.add_argument(
        "config",
        type=str,
        help="Configuration file to validate",
    )

    # Example command
    example_parser = subparsers.add_parser(
        "example",
        help="Generate example configuration",
    )
    example_parser.add_argument(
        "-o",
        "--output",
        type=str,
        default="example_config.yaml",
        help="Output file path",
    )

    args = parser.parse_args()

    # Setup logging
    level = logging.DEBUG if args.verbose else logging.INFO
    setup_logging(level=level, log_file=args.log_file)
    logger = logging.getLogger(__name__)

    if args.command is None:
        parser.print_help()
        return 0

    if args.command == "run":
        return run_simulation(args.config, args.output)
    elif args.command == "validate":
        return validate_config(args.config)
    elif args.command == "example":
        return generate_example(args.output)

    return 0


def run_simulation(config_path: str, output_dir: str | None = None) -> int:
    """
    Run a simulation from configuration file.

    Args:
        config_path: Path to configuration file
        output_dir: Optional output directory override

    Returns:
        Exit code (0 for success)
    """
    logger = logging.getLogger(__name__)

    try:
        # Load configuration
        config = load_config(config_path)
        logger.info(f"Running simulation: {config.name}")

        if output_dir is not None:
            config.output.directory = output_dir

        # Import here to avoid circular imports and slow startup
        from nanoparticle_simulator.chemistry.gas_phase import GasPhase
        from nanoparticle_simulator.reactor.batch import create_batch_reactor
        from nanoparticle_simulator.io.output import OutputWriter, OutputConfig

        # Setup gas phase
        gas = GasPhase()
        gas.load_mechanism(config.gas.mechanism)
        gas.set_state_TPX(
            config.gas.temperature,
            config.gas.pressure,
            config.gas.composition,
        )

        # Determine particle processes
        processes = []
        if config.particles.enabled:
            if config.particles.nucleation_enabled:
                processes.append("nucleation")
            if config.particles.growth_enabled:
                processes.append("growth")
            if config.particles.coagulation_enabled:
                processes.append("coagulation")
            if config.particles.oxidation_enabled:
                processes.append("oxidation")

        # Create reactor
        reactor = create_batch_reactor(
            gas=gas,
            volume=config.reactor.volume,
            enable_particles=config.particles.enabled,
            particle_processes=processes if processes else None,
        )

        # Run simulation
        logger.info(
            f"Starting simulation: duration={config.solver.duration:.2e} s, " f"dt={config.solver.time_step:.2e} s"
        )

        result = reactor.run(
            duration=config.solver.duration,
            dt=config.solver.time_step,
            output_interval=config.solver.output_interval,
        )

        # Write output
        output_config = OutputConfig(
            directory=config.output.directory,
            prefix=config.output.prefix,
            format=config.output.format,
            species_filter=config.output.species_filter,
        )
        writer = OutputWriter(output_config)
        files = writer.write(result)

        logger.info(f"Simulation complete. Output written to: {files}")
        return 0

    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        return 1
    except Exception as e:
        logger.exception(f"Simulation failed: {e}")
        return 1


def validate_config(config_path: str) -> int:
    """
    Validate a configuration file.

    Args:
        config_path: Path to configuration file

    Returns:
        Exit code (0 for valid)
    """
    logger = logging.getLogger(__name__)

    try:
        config = load_config(config_path)
        logger.info(f"Configuration valid: {config.name}")

        # Print summary
        print(f"\nConfiguration: {config.name}")
        print(f"  Description: {config.description}")
        print(f"\nGas Phase:")
        print(f"  Mechanism: {config.gas.mechanism}")
        print(f"  Temperature: {config.gas.temperature} K")
        print(f"  Pressure: {config.gas.pressure} Pa")
        print(f"\nParticles: {'Enabled' if config.particles.enabled else 'Disabled'}")
        print(f"\nSolver:")
        print(f"  Duration: {config.solver.duration} s")
        print(f"  Time step: {config.solver.time_step} s")

        return 0

    except Exception as e:
        logger.error(f"Configuration invalid: {e}")
        return 1


def generate_example(output_path: str) -> int:
    """
    Generate an example configuration file.

    Args:
        output_path: Output file path

    Returns:
        Exit code (0 for success)
    """
    logger = logging.getLogger(__name__)

    try:
        config = create_default_config()
        config.name = "Example Soot Formation Simulation"
        config.description = "Example configuration for methane/air combustion with soot formation"

        save_config(config, output_path)
        logger.info(f"Example configuration written to: {output_path}")
        return 0

    except Exception as e:
        logger.error(f"Failed to generate example: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
