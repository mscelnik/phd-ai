"""
Output writing utilities.

Writes simulation results to CSV and Excel files.
"""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Union

import numpy as np
import pandas as pd
from numpy.typing import NDArray

from nanoparticle_simulator.reactor.base import SimulationResult

logger = logging.getLogger(__name__)


@dataclass
class OutputConfig:
    """
    Output writer configuration.

    Attributes:
        directory: Output directory
        prefix: File name prefix
        format: Output format ("csv", "excel", "both")
        species_filter: List of species to include (None for all)
        time_units: Time units for output ("s", "ms", "us")
        diameter_units: Diameter units ("m", "nm", "um")
    """

    directory: str = "output"
    prefix: str = "simulation"
    format: str = "csv"
    species_filter: Optional[list[str]] = None
    time_units: str = "ms"
    diameter_units: str = "nm"


class OutputWriter:
    """
    Writer for simulation output.

    Writes simulation results to CSV and/or Excel files with
    configurable formatting and units.

    Example:
        >>> writer = OutputWriter(config=OutputConfig(directory="output"))
        >>> writer.write(result)
    """

    # Unit conversion factors
    TIME_FACTORS = {"s": 1.0, "ms": 1e3, "us": 1e6}
    DIAMETER_FACTORS = {"m": 1.0, "nm": 1e9, "um": 1e6}

    def __init__(self, config: Optional[OutputConfig] = None) -> None:
        """
        Initialize output writer.

        Args:
            config: Output configuration
        """
        self._config = config or OutputConfig()
        self._output_dir = Path(self._config.directory)
        self._output_dir.mkdir(parents=True, exist_ok=True)

    @property
    def output_dir(self) -> Path:
        """Return output directory."""
        return self._output_dir

    def write(self, result: SimulationResult, suffix: str = "") -> list[Path]:
        """
        Write simulation results to file(s).

        Args:
            result: Simulation results
            suffix: Optional suffix for filename

        Returns:
            List of written file paths
        """
        written_files = []

        # Convert to DataFrames
        df_gas = self._create_gas_dataframe(result)
        df_particles = self._create_particle_dataframe(result)

        # Determine output format
        if self._config.format in ["csv", "both"]:
            # Write CSV files
            gas_path = self._output_dir / f"{self._config.prefix}_gas{suffix}.csv"
            df_gas.to_csv(gas_path, index=False)
            written_files.append(gas_path)
            logger.info(f"Wrote gas-phase results to {gas_path}")

            if not df_particles.empty:
                particle_path = self._output_dir / f"{self._config.prefix}_particles{suffix}.csv"
                df_particles.to_csv(particle_path, index=False)
                written_files.append(particle_path)
                logger.info(f"Wrote particle results to {particle_path}")

        if self._config.format in ["excel", "both"]:
            # Write Excel file with multiple sheets
            excel_path = self._output_dir / f"{self._config.prefix}{suffix}.xlsx"
            with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
                df_gas.to_excel(writer, sheet_name="Gas Phase", index=False)
                if not df_particles.empty:
                    df_particles.to_excel(writer, sheet_name="Particles", index=False)
            written_files.append(excel_path)
            logger.info(f"Wrote results to {excel_path}")

        return written_files

    def _create_gas_dataframe(self, result: SimulationResult) -> pd.DataFrame:
        """
        Create DataFrame for gas-phase results.

        Args:
            result: Simulation results

        Returns:
            Gas-phase DataFrame
        """
        time_factor = self.TIME_FACTORS.get(self._config.time_units, 1.0)
        time_label = f"Time ({self._config.time_units})"

        data = {
            time_label: result.times * time_factor,
            "Temperature (K)": result.temperatures,
            "Pressure (Pa)": result.pressures,
        }

        # Add species mass fractions
        species_filter = self._config.species_filter
        for i, name in enumerate(result.species_names):
            if species_filter is None or name in species_filter:
                data[f"Y_{name}"] = result.species[:, i]

        return pd.DataFrame(data)

    def _create_particle_dataframe(self, result: SimulationResult) -> pd.DataFrame:
        """
        Create DataFrame for particle results.

        Args:
            result: Simulation results

        Returns:
            Particle DataFrame
        """
        if len(result.n_particles) == 0:
            return pd.DataFrame()

        time_factor = self.TIME_FACTORS.get(self._config.time_units, 1.0)
        time_label = f"Time ({self._config.time_units})"

        diam_factor = self.DIAMETER_FACTORS.get(self._config.diameter_units, 1.0)
        diam_label = f"Mean Diameter ({self._config.diameter_units})"

        data = {
            time_label: result.times * time_factor,
            "N_particles": result.n_particles,
            diam_label: result.mean_diameter * diam_factor,
            "Number Density (#/m³)": result.number_density,
            "Mass Concentration (kg/m³)": result.total_mass,
        }

        return pd.DataFrame(data)


def write_csv(
    result: SimulationResult,
    filepath: Union[str, Path],
    species_filter: Optional[list[str]] = None,
) -> None:
    """
    Write simulation results to CSV file.

    Convenience function for simple CSV output.

    Args:
        result: Simulation results
        filepath: Output file path
        species_filter: Species to include (None for all)
    """
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)

    # Create combined DataFrame
    data = {
        "Time (s)": result.times,
        "Temperature (K)": result.temperatures,
        "Pressure (Pa)": result.pressures,
    }

    # Add species
    for i, name in enumerate(result.species_names):
        if species_filter is None or name in species_filter:
            data[f"Y_{name}"] = result.species[:, i]

    # Add particle data
    if len(result.n_particles) > 0:
        data["N_particles"] = result.n_particles
        data["Mean_Diameter (m)"] = result.mean_diameter
        data["Number_Density (#/m³)"] = result.number_density

    df = pd.DataFrame(data)
    df.to_csv(filepath, index=False)
    logger.info(f"Wrote results to {filepath}")


def write_excel(
    result: SimulationResult,
    filepath: Union[str, Path],
    species_filter: Optional[list[str]] = None,
) -> None:
    """
    Write simulation results to Excel file.

    Creates a workbook with separate sheets for gas-phase
    and particle results.

    Args:
        result: Simulation results
        filepath: Output file path
        species_filter: Species to include (None for all)
    """
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)

    # Gas-phase sheet
    gas_data = {
        "Time (s)": result.times,
        "Temperature (K)": result.temperatures,
        "Pressure (Pa)": result.pressures,
    }
    for i, name in enumerate(result.species_names):
        if species_filter is None or name in species_filter:
            gas_data[f"Y_{name}"] = result.species[:, i]

    df_gas = pd.DataFrame(gas_data)

    # Particle sheet
    if len(result.n_particles) > 0:
        particle_data = {
            "Time (s)": result.times,
            "N_particles": result.n_particles,
            "Mean_Diameter (nm)": result.mean_diameter * 1e9,
            "Number_Density (#/m³)": result.number_density,
            "Mass_Concentration (kg/m³)": result.total_mass,
        }
        df_particles = pd.DataFrame(particle_data)
    else:
        df_particles = pd.DataFrame()

    # Write to Excel
    with pd.ExcelWriter(filepath, engine="openpyxl") as writer:
        df_gas.to_excel(writer, sheet_name="Gas Phase", index=False)
        if not df_particles.empty:
            df_particles.to_excel(writer, sheet_name="Particles", index=False)

    logger.info(f"Wrote results to {filepath}")
