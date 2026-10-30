import csv
import tempfile
import unittest
from pathlib import Path

from matrix_benchmark.reporting import CSV_FIELDS, append_benchmark_result


class ReportingTests(unittest.TestCase):
    def test_appends_rows_and_writes_header_once(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            output_path = Path(temporary_directory) / "results" / "benchmark.csv"
            append_benchmark_result(output_path, {"size": 100, "mode": "both"})
            append_benchmark_result(output_path, {"size": 200, "mode": "parallel"})

            with output_path.open(newline="", encoding="utf-8") as input_file:
                rows = list(csv.DictReader(input_file))

            self.assertEqual(tuple(rows[0].keys()), CSV_FIELDS)
            self.assertEqual(len(rows), 2)
            self.assertEqual(rows[0]["size"], "100")
            self.assertEqual(rows[1]["mode"], "parallel")
