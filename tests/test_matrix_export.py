"""Tests for matrix CSV and XLSX export."""

from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from matrix_benchmark.matrix_export import export_matrices


class MatrixExportTests(unittest.TestCase):
    def setUp(self) -> None:
        self.matrix_a = [[1.0, 2.0], [3.0, 4.0]]
        self.matrix_b = [[5.0, 6.0], [7.0, 8.0]]
        self.result = [[19.0, 22.0], [43.0, 50.0]]
        self.metadata = {"Seed": 7, "Checksum": 134.0}

    def test_csv_export_creates_one_file_per_matrix(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            outputs = export_matrices(
                Path(temporary_directory) / "hasil.csv",
                self.matrix_a,
                self.matrix_b,
                self.result,
                self.metadata,
            )

            self.assertEqual([path.name for path in outputs], ["hasil_A.csv", "hasil_B.csv", "hasil_AxB.csv"])
            with outputs[2].open(newline="", encoding="utf-8-sig") as file:
                self.assertEqual(list(csv.reader(file)), [["C1", "C2"], ["19.0", "22.0"], ["43.0", "50.0"]])

    def test_xlsx_export_contains_all_matrix_sheets(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            output = Path(temporary_directory) / "hasil.xlsx"
            export_matrices(output, self.matrix_a, self.matrix_b, self.result, self.metadata)

            with ZipFile(output) as workbook:
                self.assertIn("xl/worksheets/sheet1.xml", workbook.namelist())
                self.assertIn("xl/worksheets/sheet4.xml", workbook.namelist())
                workbook_xml = workbook.read("xl/workbook.xml").decode("utf-8")
                result_xml = workbook.read("xl/worksheets/sheet3.xml").decode("utf-8")

            self.assertIn('name="Matriks A"', workbook_xml)
            self.assertIn('name="Hasil A x B"', workbook_xml)
            self.assertIn("<v>50</v>", result_xml)


if __name__ == "__main__":
    unittest.main()
