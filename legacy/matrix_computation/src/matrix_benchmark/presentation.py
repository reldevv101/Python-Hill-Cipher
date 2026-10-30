"""Console formatting helpers for benchmark output."""

from __future__ import annotations

import sys
from collections.abc import Callable

from .sequential import Matrix


def print_title(title: str) -> None:
    line = "=" * 60
    print(line)
    print(f" {title}")
    print(line)


def print_matrix(matrix: Matrix, label: str) -> None:
    """Print a numeric matrix in a readable console format."""
    print(f"\n{label}")
    for row in matrix:
        values = ", ".join(f"{value:9.3f}" for value in row)
        print(f"  [{values}]")


def make_progress_reporter(label: str) -> Callable[[int, int], None]:
    """Create a carriage-return progress bar for a known number of rows."""
    last_percent = -1

    def report(completed: int, total: int) -> None:
        nonlocal last_percent
        percent = int(completed * 100 / total) if total else 100
        if percent == last_percent and completed != total:
            return
        last_percent = percent
        filled = percent * 24 // 100
        bar = "#" * filled + "-" * (24 - filled)
        print(f"\r{label:<18} [{bar}] {percent:3d}%", end="", flush=True)
        if completed == total:
            print()

    return report
