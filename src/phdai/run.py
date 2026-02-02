"""High-level runner that composes chemistry and particle modules.

This provides a simple operator-splitting loop: integrate chemistry, compute
nucleation rate, apply nucleation and coagulation for a timestep, and save
summary results.
"""

from __future__ import annotations

import os
import time
from typing import Dict, Any

import pandas as pd

from .chemistry import simple_consumption, estimate_nucleation_rate
from .particles import initialize_particles, nucleate, run_monte_carlo, size_distribution


def run_simulation(cfg: Dict[str, Any]) -> Dict[str, Any]:
    # unpack config with defaults
    t0 = cfg.get("t0", 0.0)
    tf = cfg.get("tf", 1.0)
    steps = cfg.get("steps", 10)
    C0 = cfg.get("C0", 1.0)
    k = cfg.get("k", 1.0)
    dt = (tf - t0) / steps

    # initialize particles
    particles = initialize_particles(cfg.get("n_seed", 10), size=cfg.get("seed_size", 1.0))

    results = []
    for i in range(steps):
        t_start = t0 + i * dt
        t_end = t_start + dt
        times, conc = simple_consumption((t_start, t_end), C0, k=k)
        C0 = float(conc[-1])
        # compute nucleation
        rate = estimate_nucleation_rate(C0, k_nuc=cfg.get("k_nuc", 1e-3))
        particles = nucleate(particles, rate, dt, seed_size=cfg.get("seed_size", 1.0))
        particles = run_monte_carlo(cfg.get("coag_steps", 5), particles, max_iters=cfg.get("max_iters", 1000))
        hist_counts, bin_edges = size_distribution(particles, bins=cfg.get("bins", 10))
        results.append(
            {
                "time": t_end,
                "C_precursor": C0,
                "n_particles": len(particles),
                "mean_size": float(sum(particles) / len(particles)),
            }
        )

    # save summary to outputs
    out_dir = cfg.get("out_dir", os.path.join("outputs", time.strftime("run_%Y%m%d_%H%M%S")))
    os.makedirs(out_dir, exist_ok=True)
    df = pd.DataFrame(results)
    out_csv = os.path.join(out_dir, "summary.csv")
    df.to_csv(out_csv, index=False)
    return {"out_dir": out_dir, "summary_csv": out_csv, "n_particles": len(particles)}
