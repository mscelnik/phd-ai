"""
Operator splitting algorithms.

Implements various operator splitting schemes for coupling the
gas-phase ODE system with the stochastic particle solver.

References:
    M.S. Celnik et al., "Coupling a stochastic soot population balance to
    gas-phase chemistry using operator splitting", Combustion and Flame 148 (2007)

    M.S. Celnik et al., "A predictor-corrector algorithm for the coupling
    of stiff ODEs to a particle population balance", J. Comput. Phys. 228 (2009)

    G. Strang, "On the construction and comparison of difference schemes",
    SIAM J. Numer. Anal. 5 (1968)
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
from enum import Enum, auto

import numpy as np
from numpy.typing import NDArray

from nanoparticle_simulator.chemistry.gas_phase import GasPhase, GasPhaseState
from nanoparticle_simulator.particles.stochastic_solver import StochasticSolver
from nanoparticle_simulator.reactor.ode_solver import ODESolver

logger = logging.getLogger(__name__)


class SplittingType(Enum):
    """Types of operator splitting."""

    LIE = auto()  # First-order Lie splitting
    STRANG = auto()  # Second-order Strang splitting
    PREDICTOR = auto()  # Predictor-corrector


@dataclass
class SplittingConfig:
    """
    Configuration for operator splitting.

    Attributes:
        splitting_type: Type of splitting scheme
        substeps: Number of substeps per main step
        rtol: Relative tolerance for corrector
        max_corrector_iters: Maximum corrector iterations
        corrector_tol: Convergence tolerance for corrector
    """

    splitting_type: SplittingType = SplittingType.STRANG
    substeps: int = 1
    rtol: float = 1e-4
    max_corrector_iters: int = 3
    corrector_tol: float = 1e-3


class OperatorSplitter(ABC):
    """
    Abstract base class for operator splitting algorithms.

    Operator splitting decouples the gas-phase chemistry from
    the particle population balance, allowing each to be solved
    with appropriate numerical methods.
    """

    def __init__(
        self,
        gas: GasPhase,
        ode_solver: ODESolver,
        particle_solver: Optional[StochasticSolver] = None,
    ) -> None:
        """
        Initialize operator splitter.

        Args:
            gas: Gas-phase chemistry
            ode_solver: ODE solver for gas phase
            particle_solver: Stochastic solver for particles
        """
        self._gas = gas
        self._ode = ode_solver
        self._particles = particle_solver

    @property
    def gas(self) -> GasPhase:
        """Return gas-phase interface."""
        return self._gas

    @property
    def ode_solver(self) -> ODESolver:
        """Return ODE solver."""
        return self._ode

    @property
    def particle_solver(self) -> Optional[StochasticSolver]:
        """Return particle solver."""
        return self._particles

    @abstractmethod
    def step(self, dt: float) -> None:
        """
        Advance coupled system by time dt.

        Args:
            dt: Time step (s)
        """
        ...

    def _advance_gas(self, dt: float) -> None:
        """
        Advance gas-phase chemistry.

        Args:
            dt: Time step (s)
        """
        self._ode.step(dt)

    def _advance_particles(self, dt: float) -> None:
        """
        Advance particle population.

        Args:
            dt: Time step (s)
        """
        if self._particles is not None:
            self._particles.step(self._gas, dt)

    def _update_gas_sources(self) -> None:
        """Update gas-phase source terms from particles."""
        if self._particles is not None:
            sources = self._particles.get_source_terms(self._gas)
            self._ode.set_particle_sources(sources)
        else:
            self._ode.clear_particle_sources()


class LieSplitter(OperatorSplitter):
    """
    First-order Lie (sequential) splitting.

    Solves the gas-phase and particle systems sequentially:
    1. Advance gas phase from t to t+dt
    2. Advance particles from t to t+dt

    This is first-order accurate in time.
    """

    def step(self, dt: float) -> None:
        """
        Advance using Lie splitting.

        Args:
            dt: Time step (s)
        """
        # Update source terms
        self._update_gas_sources()

        # Step 1: Gas phase
        self._advance_gas(dt)

        # Step 2: Particles
        self._advance_particles(dt)


class StrangSplitter(OperatorSplitter):
    """
    Second-order Strang (symmetric) splitting.

    Solves the systems in a symmetric pattern:
    1. Advance gas phase from t to t+dt/2
    2. Advance particles from t to t+dt
    3. Advance gas phase from t+dt/2 to t+dt

    This is second-order accurate in time.

    Reference:
        G. Strang, "On the construction and comparison of difference schemes",
        SIAM J. Numer. Anal. 5 (1968)
    """

    def step(self, dt: float) -> None:
        """
        Advance using Strang splitting.

        Args:
            dt: Time step (s)
        """
        # Update source terms
        self._update_gas_sources()

        # Step 1: Half step gas phase
        self._advance_gas(0.5 * dt)

        # Step 2: Full step particles
        self._advance_particles(dt)

        # Update sources after particle step
        self._update_gas_sources()

        # Step 3: Half step gas phase
        self._advance_gas(0.5 * dt)


class PredictorCorrector(OperatorSplitter):
    """
    Predictor-corrector splitting algorithm.

    Uses a predictor step to estimate the gas-phase evolution,
    then corrects based on actual particle source terms.

    This improves accuracy for highly coupled problems where
    the particle source terms significantly affect the gas phase.

    Reference:
        M.S. Celnik et al., "A predictor-corrector algorithm for the coupling
        of stiff ODEs to a particle population balance", J. Comput. Phys. 228 (2009)
    """

    def __init__(
        self,
        gas: GasPhase,
        ode_solver: ODESolver,
        particle_solver: Optional[StochasticSolver] = None,
        config: Optional[SplittingConfig] = None,
    ) -> None:
        """
        Initialize predictor-corrector.

        Args:
            gas: Gas-phase chemistry
            ode_solver: ODE solver for gas phase
            particle_solver: Stochastic solver for particles
            config: Splitting configuration
        """
        super().__init__(gas, ode_solver, particle_solver)
        self._config = config or SplittingConfig()

    def step(self, dt: float) -> None:
        """
        Advance using predictor-corrector.

        Algorithm:
        1. Predict: Advance gas phase using current source terms
        2. Advance particles with predicted gas state
        3. Correct: Re-advance gas phase with updated sources
        4. Iterate until convergence (optional)

        Args:
            dt: Time step (s)
        """
        # Save initial state
        initial_state = self._gas.get_state()

        # Update initial source terms
        self._update_gas_sources()

        # Predictor: Advance gas phase
        self._advance_gas(dt)
        predicted_state = self._gas.get_state()

        # Advance particles with predicted gas state
        self._advance_particles(dt)

        # Update source terms based on particle evolution
        self._update_gas_sources()

        # Corrector iteration
        for i in range(self._config.max_corrector_iters):
            # Restore initial state
            self._gas.restore_state(initial_state)

            # Correct: Re-advance gas phase with updated sources
            self._advance_gas(dt)
            corrected_state = self._gas.get_state()

            # Check convergence
            if self._check_convergence(predicted_state, corrected_state):
                logger.debug(f"Corrector converged in {i+1} iterations")
                break

            predicted_state = corrected_state

    def _check_convergence(self, state1: GasPhaseState, state2: GasPhaseState) -> bool:
        """
        Check if corrector has converged.

        Args:
            state1: Previous state
            state2: Current state

        Returns:
            True if converged
        """
        # Temperature convergence
        T_err = abs(state2.T - state1.T) / max(state1.T, 1.0)
        if T_err > self._config.corrector_tol:
            return False

        # Species convergence
        Y_err = np.max(np.abs(state2.Y - state1.Y))
        if Y_err > self._config.corrector_tol:
            return False

        return True


def create_splitter(
    splitting_type: SplittingType,
    gas: GasPhase,
    ode_solver: ODESolver,
    particle_solver: Optional[StochasticSolver] = None,
    config: Optional[SplittingConfig] = None,
) -> OperatorSplitter:
    """
    Factory function to create an operator splitter.

    Args:
        splitting_type: Type of splitting scheme
        gas: Gas-phase chemistry
        ode_solver: ODE solver for gas phase
        particle_solver: Stochastic solver for particles
        config: Splitting configuration

    Returns:
        Appropriate operator splitter

    Raises:
        ValueError: If unknown splitting type
    """
    if splitting_type == SplittingType.LIE:
        return LieSplitter(gas, ode_solver, particle_solver)
    elif splitting_type == SplittingType.STRANG:
        return StrangSplitter(gas, ode_solver, particle_solver)
    elif splitting_type == SplittingType.PREDICTOR:
        return PredictorCorrector(gas, ode_solver, particle_solver, config)
    else:
        raise ValueError(f"Unknown splitting type: {splitting_type}")
