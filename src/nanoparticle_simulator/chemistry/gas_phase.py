"""
Gas-phase chemistry solver.

This module provides the main interface for gas-phase chemistry calculations
using Cantera as the backend. It handles thermodynamic state, reaction rates,
and species production.

References:
    GRI-Mech 3.0: http://combustion.berkeley.edu/gri-mech/version30/text30.html
    M.S. Celnik et al., "Coupling a stochastic soot population balance to
    gas-phase chemistry using operator splitting", Combustion and Flame 148 (2007)
"""

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import cantera as ct
import numpy as np
from numpy.typing import NDArray

from nanoparticle_simulator.chemistry.mechanism import Mechanism

logger = logging.getLogger(__name__)


@dataclass
class GasPhaseState:
    """
    State of the gas phase.

    Immutable snapshot of the gas-phase thermodynamic state.

    Attributes:
        T: Temperature in K
        P: Pressure in Pa
        Y: Mass fractions (n_species,)
        X: Mole fractions (n_species,)
        rho: Density in kg/m³
        mean_mw: Mean molecular weight in kg/mol
    """

    T: float
    P: float
    Y: NDArray[np.float64]
    X: NDArray[np.float64]
    rho: float
    mean_mw: float

    def copy(self) -> "GasPhaseState":
        """Return a copy of this state."""
        return GasPhaseState(
            T=self.T,
            P=self.P,
            Y=self.Y.copy(),
            X=self.X.copy(),
            rho=self.rho,
            mean_mw=self.mean_mw,
        )


class GasPhase:
    """
    Gas-phase chemistry interface.

    Provides methods for computing thermodynamic properties, reaction rates,
    and species production rates. Uses Cantera as the computational backend.

    Example:
        >>> gas = GasPhase()
        >>> gas.load_mechanism("gri30.yaml")
        >>> gas.set_state(T=1500.0, P=101325.0, X={"CH4": 0.1, "O2": 0.2, "N2": 0.7})
        >>> rates = gas.production_rates
    """

    def __init__(
        self,
        mechanism: Optional[Mechanism | str | Path] = None,
    ) -> None:
        """
        Initialize gas-phase chemistry.

        Args:
            mechanism: Mechanism object, file path, or built-in name
        """
        self._mechanism: Optional[Mechanism] = None
        self._gas: Optional[ct.Solution] = None

        if mechanism is not None:
            if isinstance(mechanism, Mechanism):
                self._mechanism = mechanism
                self._gas = mechanism.ct_solution
            else:
                self.load_mechanism(mechanism)

    @property
    def mechanism(self) -> Optional[Mechanism]:
        """Return the loaded mechanism."""
        return self._mechanism

    @property
    def n_species(self) -> int:
        """Return number of species."""
        return self._gas.n_species if self._gas is not None else 0

    @property
    def n_reactions(self) -> int:
        """Return number of reactions."""
        return self._gas.n_reactions if self._gas is not None else 0

    @property
    def species_names(self) -> list[str]:
        """Return list of species names."""
        return list(self._gas.species_names) if self._gas is not None else []

    @property
    def T(self) -> float:
        """Return temperature in K."""
        if self._gas is None:
            raise RuntimeError("No mechanism loaded")
        return self._gas.T

    @property
    def P(self) -> float:
        """Return pressure in Pa."""
        if self._gas is None:
            raise RuntimeError("No mechanism loaded")
        return self._gas.P

    @property
    def Y(self) -> NDArray[np.float64]:
        """Return mass fractions."""
        if self._gas is None:
            raise RuntimeError("No mechanism loaded")
        return np.array(self._gas.Y)

    @property
    def X(self) -> NDArray[np.float64]:
        """Return mole fractions."""
        if self._gas is None:
            raise RuntimeError("No mechanism loaded")
        return np.array(self._gas.X)

    @property
    def density(self) -> float:
        """Return density in kg/m³."""
        if self._gas is None:
            raise RuntimeError("No mechanism loaded")
        return self._gas.density

    @property
    def mean_molecular_weight(self) -> float:
        """Return mean molecular weight in kg/mol."""
        if self._gas is None:
            raise RuntimeError("No mechanism loaded")
        return self._gas.mean_molecular_weight / 1000.0  # g/mol -> kg/mol

    @property
    def cp(self) -> float:
        """Return specific heat at constant pressure in J/(kg·K)."""
        if self._gas is None:
            raise RuntimeError("No mechanism loaded")
        return self._gas.cp_mass

    @property
    def cv(self) -> float:
        """Return specific heat at constant volume in J/(kg·K)."""
        if self._gas is None:
            raise RuntimeError("No mechanism loaded")
        return self._gas.cv_mass

    @property
    def enthalpy(self) -> float:
        """Return specific enthalpy in J/kg."""
        if self._gas is None:
            raise RuntimeError("No mechanism loaded")
        return self._gas.enthalpy_mass

    @property
    def internal_energy(self) -> float:
        """Return specific internal energy in J/kg."""
        if self._gas is None:
            raise RuntimeError("No mechanism loaded")
        return self._gas.int_energy_mass

    @property
    def production_rates(self) -> NDArray[np.float64]:
        """
        Return species production rates in kmol/(m³·s).

        These are the net rates of production of each species due to
        all gas-phase reactions.
        """
        if self._gas is None:
            raise RuntimeError("No mechanism loaded")
        return np.array(self._gas.net_production_rates)

    @property
    def production_rates_mass(self) -> NDArray[np.float64]:
        """
        Return species production rates in kg/(m³·s).

        Mass-based production rates for each species.
        """
        if self._gas is None:
            raise RuntimeError("No mechanism loaded")
        # Convert kmol/(m³·s) to kg/(m³·s)
        mw = np.array(self._gas.molecular_weights) / 1000.0  # kg/mol
        return self.production_rates * mw * 1000.0  # kmol -> mol

    @property
    def heat_release_rate(self) -> float:
        """
        Return volumetric heat release rate in W/m³.

        Positive values indicate exothermic reactions.
        """
        if self._gas is None:
            raise RuntimeError("No mechanism loaded")
        return -np.sum(self.production_rates * np.array(self._gas.partial_molar_enthalpies))

    def load_mechanism(self, source: str | Path) -> None:
        """
        Load a chemical mechanism.

        Args:
            source: Path to mechanism file or built-in name (e.g., 'gri30.yaml')
        """
        self._mechanism = Mechanism(name=str(source))
        self._mechanism.load(Path(source))
        self._gas = self._mechanism.ct_solution
        logger.info(f"Loaded mechanism with {self.n_species} species " f"and {self.n_reactions} reactions")

    def set_state(
        self,
        T: Optional[float] = None,
        P: Optional[float] = None,
        X: Optional[dict[str, float] | NDArray[np.float64] | str] = None,
        Y: Optional[dict[str, float] | NDArray[np.float64]] = None,
    ) -> None:
        """
        Set the thermodynamic state of the gas.

        Args:
            T: Temperature in K
            P: Pressure in Pa
            X: Mole fractions (dict, array, or string like "CH4:0.1, O2:0.2, N2:0.7")
            Y: Mass fractions (dict or array)

        Raises:
            RuntimeError: If no mechanism is loaded
            ValueError: If both X and Y are specified
        """
        if self._gas is None:
            raise RuntimeError("No mechanism loaded")

        if X is not None and Y is not None:
            raise ValueError("Cannot specify both X and Y")

        # Set composition first
        if X is not None:
            if isinstance(X, str):
                self._gas.X = X
            elif isinstance(X, dict):
                self._gas.X = X
            else:
                self._gas.X = np.asarray(X)
        elif Y is not None:
            if isinstance(Y, dict):
                self._gas.Y = Y
            else:
                self._gas.Y = np.asarray(Y)

        # Set T and P
        if T is not None and P is not None:
            self._gas.TP = T, P
        elif T is not None:
            self._gas.TP = T, self._gas.P
        elif P is not None:
            self._gas.TP = self._gas.T, P

    def set_state_TPY(self, T: float, P: float, Y: dict[str, float] | NDArray[np.float64]) -> None:
        """
        Set state using temperature, pressure, and mass fractions.

        Args:
            T: Temperature in K
            P: Pressure in Pa
            Y: Mass fractions
        """
        if self._gas is None:
            raise RuntimeError("No mechanism loaded")
        if isinstance(Y, dict):
            self._gas.TPY = T, P, Y
        else:
            self._gas.TPY = T, P, np.asarray(Y)

    def set_state_TPX(
        self,
        T: float,
        P: float,
        X: dict[str, float] | NDArray[np.float64] | str,
    ) -> None:
        """
        Set state using temperature, pressure, and mole fractions.

        Args:
            T: Temperature in K
            P: Pressure in Pa
            X: Mole fractions
        """
        if self._gas is None:
            raise RuntimeError("No mechanism loaded")
        if isinstance(X, (dict, str)):
            self._gas.TPX = T, P, X
        else:
            self._gas.TPX = T, P, np.asarray(X)

    def get_state(self) -> GasPhaseState:
        """
        Get current thermodynamic state.

        Returns:
            Snapshot of current gas-phase state
        """
        if self._gas is None:
            raise RuntimeError("No mechanism loaded")
        return GasPhaseState(
            T=self.T,
            P=self.P,
            Y=self.Y,
            X=self.X,
            rho=self.density,
            mean_mw=self.mean_molecular_weight,
        )

    def restore_state(self, state: GasPhaseState) -> None:
        """
        Restore gas to a previous state.

        Args:
            state: State to restore
        """
        self.set_state_TPY(state.T, state.P, state.Y)

    def species_index(self, name: str) -> int:
        """
        Get index of a species by name.

        Args:
            name: Species name

        Returns:
            Species index
        """
        if self._gas is None:
            raise RuntimeError("No mechanism loaded")
        return self._gas.species_index(name)

    def species_mass_fraction(self, name: str) -> float:
        """
        Get mass fraction of a species.

        Args:
            name: Species name

        Returns:
            Mass fraction
        """
        idx = self.species_index(name)
        return self.Y[idx]

    def species_mole_fraction(self, name: str) -> float:
        """
        Get mole fraction of a species.

        Args:
            name: Species name

        Returns:
            Mole fraction
        """
        idx = self.species_index(name)
        return self.X[idx]

    def species_concentration(self, name: str) -> float:
        """
        Get molar concentration of a species in kmol/m³.

        Args:
            name: Species name

        Returns:
            Concentration in kmol/m³

        Raises:
            KeyError: If species not found in mechanism
        """
        if self._gas is None:
            raise RuntimeError("No mechanism loaded")
        try:
            idx = self.species_index(name)
            return self._gas.concentrations[idx]
        except Exception as e:
            raise KeyError(f"Species '{name}' not found in mechanism") from e

    def concentrations(self) -> NDArray[np.float64]:
        """
        Get molar concentrations of all species in kmol/m³.

        Returns:
            Array of concentrations
        """
        if self._gas is None:
            raise RuntimeError("No mechanism loaded")
        return np.array(self._gas.concentrations)

    def equilibrate(self, XY: str = "TP") -> None:
        """
        Equilibrate the gas mixture.

        Args:
            XY: Two-character string indicating which properties to hold fixed
                (e.g., 'TP', 'HP', 'SP', 'UV')
        """
        if self._gas is None:
            raise RuntimeError("No mechanism loaded")
        self._gas.equilibrate(XY)

    def forward_rates(self) -> NDArray[np.float64]:
        """
        Get forward reaction rates in kmol/(m³·s).

        Returns:
            Array of forward rates for each reaction
        """
        if self._gas is None:
            raise RuntimeError("No mechanism loaded")
        return np.array(self._gas.forward_rates_of_progress)

    def reverse_rates(self) -> NDArray[np.float64]:
        """
        Get reverse reaction rates in kmol/(m³·s).

        Returns:
            Array of reverse rates for each reaction
        """
        if self._gas is None:
            raise RuntimeError("No mechanism loaded")
        return np.array(self._gas.reverse_rates_of_progress)

    def net_rates(self) -> NDArray[np.float64]:
        """
        Get net reaction rates in kmol/(m³·s).

        Returns:
            Array of net rates for each reaction
        """
        if self._gas is None:
            raise RuntimeError("No mechanism loaded")
        return np.array(self._gas.net_rates_of_progress)

    def __repr__(self) -> str:
        if self._mechanism is not None:
            return f"GasPhase({self._mechanism.name}, " f"T={self.T:.1f} K, P={self.P:.0f} Pa)"
        return "GasPhase(no mechanism loaded)"
