"""Export generated matrices without adding a third-party dependency."""

from __future__ import annotations

import csv
from collections.abc import Mapping
from pathlib import Path
from xml.sax.saxutils import escape
from zipfile import ZIP_DEFLATED, ZipFile

from .sequential import Matrix


def export_matrices(
    destination: Path,
    matrix_a: Matrix,
    matrix_b: Matrix,
    result: Matrix,
    metadata: Mapping[str, object],
) -> list[Path]:
    """Export A, B, and A x B as either CSV files or one XLSX workbook.

    A CSV file cannot contain three independent matrices cleanly, so selecting
    ``example.csv`` creates ``example_A.csv``, ``example_B.csv``, and
    ``example_AxB.csv`` in the same folder.
    """

    extension = destination.suffix.lower()
    if extension == ".csv":
        return _export_csv_files(destination, matrix_a, matrix_b, result)
    if extension == ".xlsx":
        _export_xlsx(destination, matrix_a, matrix_b, result, metadata)
        return [destination]
    raise ValueError("Pilih format CSV (.csv) atau Excel (.xlsx).")


def _export_csv_files(destination: Path, matrix_a: Matrix, matrix_b: Matrix, result: Matrix) -> list[Path]:
    outputs = [
        (destination.with_name(f"{destination.stem}_A.csv"), matrix_a),
        (destination.with_name(f"{destination.stem}_B.csv"), matrix_b),
        (destination.with_name(f"{destination.stem}_AxB.csv"), result),
    ]
    for path, matrix in outputs:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", newline="", encoding="utf-8-sig") as file:
            writer = csv.writer(file)
            writer.writerow([f"C{index + 1}" for index in range(len(matrix[0]))])
            writer.writerows(matrix)
    return [path for path, _ in outputs]


def _export_xlsx(
    destination: Path,
    matrix_a: Matrix,
    matrix_b: Matrix,
    result: Matrix,
    metadata: Mapping[str, object],
) -> None:
    """Write a compact Excel workbook using the standard-library ZIP/XML APIs."""

    sheets = [
        ("Matriks A", _matrix_sheet_xml(matrix_a)),
        ("Matriks B", _matrix_sheet_xml(matrix_b)),
        ("Hasil A x B", _matrix_sheet_xml(result)),
        ("Informasi", _metadata_sheet_xml(metadata)),
    ]
    destination.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(destination, "w", compression=ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", _content_types_xml(len(sheets)))
        archive.writestr("_rels/.rels", _root_relationships_xml())
        archive.writestr("xl/workbook.xml", _workbook_xml([name for name, _ in sheets]))
        archive.writestr("xl/_rels/workbook.xml.rels", _workbook_relationships_xml(len(sheets)))
        for index, (_, sheet_xml) in enumerate(sheets, start=1):
            archive.writestr(f"xl/worksheets/sheet{index}.xml", sheet_xml)


def _matrix_sheet_xml(matrix: Matrix) -> str:
    headers = [f"C{index + 1}" for index in range(len(matrix[0]))]
    rows: list[list[object]] = [headers, *matrix]
    return _sheet_xml(rows)


def _metadata_sheet_xml(metadata: Mapping[str, object]) -> str:
    rows: list[list[object]] = [["Properti", "Nilai"]]
    rows.extend([[key, value] for key, value in metadata.items()])
    return _sheet_xml(rows)


def _sheet_xml(rows: list[list[object]]) -> str:
    xml_rows: list[str] = []
    for row_number, values in enumerate(rows, start=1):
        cells = "".join(
            _cell_xml(_cell_reference(column_number, row_number), value)
            for column_number, value in enumerate(values, start=1)
        )
        xml_rows.append(f'<row r="{row_number}">{cells}</row>')
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        f"<sheetData>{''.join(xml_rows)}</sheetData>"
        "</worksheet>"
    )


def _cell_xml(reference: str, value: object) -> str:
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return f'<c r="{reference}"><v>{value:.15g}</v></c>'
    return f'<c r="{reference}" t="inlineStr"><is><t>{escape(str(value))}</t></is></c>'


def _cell_reference(column: int, row: int) -> str:
    letters = ""
    while column:
        column, remainder = divmod(column - 1, 26)
        letters = chr(65 + remainder) + letters
    return f"{letters}{row}"


def _content_types_xml(sheet_count: int) -> str:
    sheets = "".join(
        f'<Override PartName="/xl/worksheets/sheet{index}.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
        for index in range(1, sheet_count + 1)
    )
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/xl/workbook.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
        f"{sheets}</Types>"
    )


def _root_relationships_xml() -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" '
        'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" '
        'Target="xl/workbook.xml"/>'
        "</Relationships>"
    )


def _workbook_xml(sheet_names: list[str]) -> str:
    sheets = "".join(
        f'<sheet name="{escape(name)}" sheetId="{index}" r:id="rId{index}"/>'
        for index, name in enumerate(sheet_names, start=1)
    )
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        f"<sheets>{sheets}</sheets></workbook>"
    )


def _workbook_relationships_xml(sheet_count: int) -> str:
    relationships = "".join(
        f'<Relationship Id="rId{index}" '
        'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" '
        f'Target="worksheets/sheet{index}.xml"/>'
        for index in range(1, sheet_count + 1)
    )
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        f"{relationships}</Relationships>"
    )
