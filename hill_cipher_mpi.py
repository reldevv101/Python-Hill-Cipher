"""Convenient entry point for Hill Cipher MPI runs from the project folder."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent / "src"))

from matrix_benchmark.hill_cipher.mpi_cli import main


if __name__ == "__main__":
    main()
