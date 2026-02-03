"""Convenience wrapper around the `sootsim` console script so the repo can be executed as a script."""
import sys

from sootsim.cli import main

if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
