"""Convenient entry point for the Matrix Computation Benchmark."""

from pathlib import Path
import sys

# Enables `py main.py` before the project is installed as a package.
sys.path.insert(0, str(Path(__file__).parent / "src"))

from matrix_benchmark.cli import main


if __name__ == "__main__":
    main()
