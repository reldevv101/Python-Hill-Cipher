"""Write benchmark runs to a CSV file for later analysis and reporting."""

from __future__ import annotations

import csv
from collections.abc import Mapping
from pathlib import Path

CSV_FIELDS = (
    "timestamp",
    "size",
    "seed",
    "mode",
    "workers",
    "sequential_seconds",
    "parallel_seconds",
    "speedup",
    "checksum",
    "result_match",
)


def append_benchmark_result(path: Path, result: Mapping[str, object]) -> None:
    """Append one benchmark result and create the CSV header when needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    write_header = not path.exists() or path.stat().st_size == 0

    with path.open("a", newline="", encoding="utf-8") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=CSV_FIELDS)
        if write_header:
            writer.writeheader()
        writer.writerow({field: result.get(field, "") for field in CSV_FIELDS})
