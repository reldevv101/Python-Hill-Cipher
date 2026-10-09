"""Entry point for the desktop version of Matrix Computation Benchmark."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent / "src"))

from matrix_benchmark.gui import main


if __name__ == "__main__":
    main()
