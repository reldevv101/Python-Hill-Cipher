"""Entry point for the MPI distributed matrix benchmark."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent / "src"))

from matrix_benchmark.distributed import main


if __name__ == "__main__":
    main()
