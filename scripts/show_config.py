"""Utility to dump one of the repository configs to stdout."""
from pathlib import Path


def main() -> None:
    config = Path("data/configs/acetylene_run.yaml")
    if not config.exists():
        raise SystemExit("Config file missing")
    print(config.read_text())


if __name__ == "__main__":
    main()
