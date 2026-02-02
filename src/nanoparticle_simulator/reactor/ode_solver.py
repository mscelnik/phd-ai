"""
ODE solver for gas-phase chemistry.

Provides integration methods for the stiff ODE system arising
from detailed chemical kinetics.
"""

import logging
from dataclasses import dataclass
from typing import Optional, Callable
from enum import Enum, auto

import numpy as np
from numpy.typing import NDArray
from scipy.integrate import solve_ivp

from nanoparticle_simulator.chemistry.gas_phase import GasPhase

logger = logging.getLogger(__name__)


class IntegratorType(Enum):
    """Available ODE integrators."""

    BDF = auto()  # Backward Differentiation Formula (stiff)
    RADAU = auto()  # Implicit Runge-Kutta (stiff)
    LSODA = auto()  # Automatic stiff/non-stiff switching
    RK45 = auto()  # Explicit Runge-Kutta (non-stiff)
    RK23 = auto()  # Explicit Runge-Kutta (non-stiff)


@dataclass
class ODEConfig:
    """
    Configuration for ODE solver.

    Attributes:
        integrator: Type of integrator
        rtol: Relative tolerance
        atol: Absolute tolerance
        max_steps: Maximum integration steps
        first_step: Initial step size (None for automatic)
    """

    integrator: IntegratorType = IntegratorType.BDF
    rtol: float = 1e-6
    atol: float = 1e-12
    max_steps: int = 10000
    first_step: Optional[float] = None


class ODESolver:
    """
    ODE solver for gas-phase chemistry integration.

    Wraps scipy's solve_ivp with appropriate settings for
    stiff chemical kinetics.

    Example:
        >>> solver = ODESolver(gas)
        >>> solver.integrate(dt=1e-4)
    """

    def __init__(
        self,
        gas: GasPhase,
        config: Optional[ODEConfig] = None,
        energy_enabled: bool = True,
        constant_pressure: bool = True,
    ) -> None:
        """
        Initialize ODE solver.

        Args:
            gas: Gas-phase chemistry
            config: Solver configuration
            energy_enabled: Whether to solve energy equation
            constant_pressure: Constant pressure (True) or volume (False)
        """
        self._gas = gas
        self._config = config or ODEConfig()
        self._energy_enabled = energy_enabled
        self._constant_pressure = constant_pressure

        # Source terms from particle processes
        self._particle_sources: dict[str, float] = {}

    @property
    def gas(self) -> GasPhase:
        """Return gas-phase interface."""
        return self._gas

    def set_particle_sources(self, sources: dict[str, float]) -> None:
        """
        Set source terms from particle processes.

        Args:
            sources: Species source terms (mol/m³/s)
        """
        self._particle_sources = sources.copy()

    def clear_particle_sources(self) -> None:
        """Clear particle source terms."""
        self._particle_sources.clear()

    def _get_state_vector(self) -> NDArray[np.float64]:
        """
        Get current state as vector.

        Returns:
            State vector [Y1, Y2, ..., Yn, T] or [Y1, Y2, ..., Yn]
        """
        Y = self._gas.Y
        if self._energy_enabled:
            return np.append(Y, self._gas.T)
        return Y

    def _set_state_from_vector(self, y: NDArray[np.float64]) -> None:
        """
        Set gas state from vector.

        Args:
            y: State vector
        """
        if self._energy_enabled:
            Y = y[:-1]
            T = y[-1]
            if self._constant_pressure:
                self._gas.set_state(T=T, Y=Y)
            else:
                self._gas.set_state(T=T, Y=Y)
        else:
            self._gas.set_state(Y=y)

    def _rhs(self, t: float, y: NDArray[np.float64]) -> NDArray[np.float64]:
        """
        Compute right-hand side of ODE system.

        For constant pressure reactor:
        dY_k/dt = (W_k * omega_dot_k) / rho
        dT/dt = -sum(h_k * omega_dot_k) / (rho * cp)

        Args:
            t: Time (not used, but required by solve_ivp)
            y: State vector

        Returns:
            Time derivatives
        """
        self._set_state_from_vector(y)

        n_species = self._gas.n_species
        rho = self._gas.density
        Y = self._gas.Y

        # Get molar production rates (kmol/m³/s)
        omega_dot = self._gas.production_rates

        # Add particle source terms
        for name, rate in self._particle_sources.items():
            try:
                idx = self._gas.species_index(name)
                omega_dot[idx] += rate / 1000.0  # mol -> kmol
            except (ValueError, KeyError):
                pass

        # Molecular weights (kg/kmol)
        if self._gas._gas is not None:
            W = np.array(self._gas._gas.molecular_weights)
        else:
            W = np.ones(n_species)

        # Mass production rates (kg/m³/s)
        omega_mass = omega_dot * W

        # Species equations: dY_k/dt = omega_mass_k / rho
        dYdt = omega_mass / rho

        if self._energy_enabled:
            # Energy equation
            if self._gas._gas is not None:
                h = np.array(self._gas._gas.partial_molar_enthalpies)  # J/kmol
            else:
                h = np.zeros(n_species)

            cp = self._gas.cp

            # Heat release: -sum(h_k * omega_k) / (rho * cp)
            q_dot = -np.dot(h, omega_dot)
            dTdt = q_dot / (rho * cp)

            return np.append(dYdt, dTdt)

        return dYdt

    def integrate(
        self,
        dt: float,
        t_eval: Optional[NDArray[np.float64]] = None,
    ) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
        """
        Integrate the ODE system for time dt.

        Args:
            dt: Integration time (s)
            t_eval: Times at which to store solution (optional)

        Returns:
            Tuple of (times, solution array)
        """
        y0 = self._get_state_vector()

        # Select integrator
        method_map = {
            IntegratorType.BDF: "BDF",
            IntegratorType.RADAU: "Radau",
            IntegratorType.LSODA: "LSODA",
            IntegratorType.RK45: "RK45",
            IntegratorType.RK23: "RK23",
        }
        method = method_map[self._config.integrator]

        # Integrate
        result = solve_ivp(
            self._rhs,
            (0.0, dt),
            y0,
            method=method,
            t_eval=t_eval,
            rtol=self._config.rtol,
            atol=self._config.atol,
            max_step=dt,  # Don't exceed the target time step
        )

        if not result.success:
            logger.warning(f"ODE integration warning: {result.message}")

        # Update gas to final state
        self._set_state_from_vector(result.y[:, -1])

        return result.t, result.y

    def step(self, dt: float) -> None:
        """
        Advance gas phase by time dt.

        Simple interface that just advances the state.

        Args:
            dt: Time step (s)
        """
        self.integrate(dt)

    def __repr__(self) -> str:
        return f"ODESolver({self._config.integrator.name}, " f"rtol={self._config.rtol:.0e})"
