#!/usr/bin/env python3
"""CLI runner for the phd-ai simplified simulation."""
import argparse
import yaml
from pathlib import Path

from phdai.run import run_simulation


def main():
    p = argparse.ArgumentParser()
    p.add_argument("config", help="YAML config file")
    args = p.parse_args()
    cfg = yaml.safe_load(Path(args.config).read_text())
    out = run_simulation(cfg)
    print(f"Simulation finished. Outputs: {out}")


if __name__ == "__main__":
    main()
