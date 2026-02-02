"""Simple gas-phase chemistry module.

This module provides a minimal ODE-based chemistry solver to model a single
precursor (e.g. acetylene) consumption with a simple rate law. It is
intentionally simple for testing and demonstration.
"""

from __future__ import annotations

import numpy as np
from scipy.integrate import solve_ivp


def simple_consumption(t_span, C0, k=1.0):
    """Integrate dC/dt = -k * C over t_span.

    Args:
        t_span: tuple (t0, tf)
        C0: initial concentration (float)
        k: rate constant

    Returns:
        times, concentrations arrays
    """

    def rhs(t, y):
        return [-k * y[0]]

    sol = solve_ivp(rhs, t_span, [C0], t_eval=np.linspace(t_span[0], t_span[1], 50))
    return sol.t, sol.y[0]


def estimate_nucleation_rate(C_acetylene, k_nuc=1e-3):
    """Estimate particle nucleation rate from precursor concentration.

    This is a toy model: nucleation rate proportional to concentration.
    """
    return k_nuc * C_acetylene
