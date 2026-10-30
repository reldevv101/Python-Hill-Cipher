"""MPI-based matrix multiplication for distributed-memory processes."""

from __future__ import annotations

import argparse
import random
from collections.abc import Sequence

from .sequential import Matrix, _validate_matrices, matrix_checksum
from .presentation import print_matrix, print_title


def _import_mpi():
    try:
        from mpi4py import MPI
    except ImportError as error:
        raise RuntimeError(
            "mpi4py atau runtime MPI belum siap. Pasang runtime MPI, lalu jalankan "
            "`py -3 -m pip install mpi4py` terlebih dahulu."
        ) from error
    return MPI


def split_rows_for_processes(matrix: Matrix, process_count: int) -> list[Matrix]:
    """Split rows into near-equal chunks, including empty chunks when needed."""
    if process_count <= 0:
        raise ValueError("Jumlah proses harus berupa bilangan bulat positif.")

    base_size, remainder = divmod(len(matrix), process_count)
    chunks: list[Matrix] = []
    start = 0
    for process_index in range(process_count):
        end = start + base_size + (1 if process_index < remainder else 0)
        chunks.append(matrix[start:end])
        start = end
    return chunks


def _multiply_rows(rows: Matrix, right_columns: Sequence[tuple[float, ...]]) -> Matrix:
    return [
        [sum(a * b for a, b in zip(left_row, right_column)) for right_column in right_columns]
        for left_row in rows
    ]


def distributed_multiply(left: Matrix | None, right: Matrix | None):
    """Multiply matrices through the current MPI communicator.

    Only rank 0 supplies the input matrices and receives the final matrix.
    Other ranks return ``None`` after contributing their assigned rows.
    """
    MPI = _import_mpi()
    communicator = MPI.COMM_WORLD
    rank = communicator.Get_rank()
    process_count = communicator.Get_size()

    if rank == 0:
        if left is None or right is None:
            raise ValueError("Rank 0 harus menyediakan kedua matriks.")
        _validate_matrices(left, right)
        right_columns = [tuple(column) for column in zip(*right)]
        row_chunks = split_rows_for_processes(left, process_count)
    else:
        right_columns = None
        row_chunks = None

    communicator.Barrier()
    started_at = MPI.Wtime()
    right_columns = communicator.bcast(right_columns, root=0)
    local_rows = communicator.scatter(row_chunks, root=0)
    local_result = _multiply_rows(local_rows, right_columns)
    result_chunks = communicator.gather(local_result, root=0)
    elapsed_seconds = MPI.Wtime() - started_at

    if rank != 0:
        return None, None
    return [row for chunk in result_chunks for row in chunk], elapsed_seconds


def _make_matrix(size: int, rng: random.Random) -> Matrix:
    return [[rng.uniform(-10.0, 10.0) for _ in range(size)] for _ in range(size)]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Benchmark perkalian matriks distributed menggunakan MPI."
    )
    parser.add_argument("--size", type=int, default=100, help="Ukuran N pada matriks N x N.")
    parser.add_argument("--seed", type=int, default=42, help="Seed data acak.")
    parser.add_argument(
        "--show-result",
        action="store_true",
        help="Tampilkan matriks hasil. Disarankan hanya untuk ukuran kecil.",
    )
    parser.add_argument(
        "--display-limit", type=int, default=10,
        help="Ukuran maksimum untuk --show-result (default: 10).",
    )
    return parser


def main() -> None:
    try:
        MPI = _import_mpi()
    except RuntimeError as error:
        raise SystemExit(error) from error

    args = build_parser().parse_args()
    if args.size <= 0:
        raise SystemExit("--size harus berupa bilangan bulat positif.")
    if args.display_limit <= 0:
        raise SystemExit("--display-limit harus berupa bilangan bulat positif.")
    if args.show_result and args.size > args.display_limit:
        raise SystemExit(
            "Ukuran matriks terlalu besar untuk ditampilkan. "
            "Naikkan --display-limit atau gunakan --size yang lebih kecil."
        )

    communicator = MPI.COMM_WORLD
    rank = communicator.Get_rank()
    if rank == 0:
        rng = random.Random(args.seed)
        left = _make_matrix(args.size, rng)
        right = _make_matrix(args.size, rng)
    else:
        left = None
        right = None

    result, elapsed_seconds = distributed_multiply(left, right)
    process_hosts = communicator.gather(MPI.Get_processor_name(), root=0)
    if rank == 0 and result is not None and elapsed_seconds is not None:
        print_title("MATRIX COMPUTATION BENCHMARK (DISTRIBUTED MPI)")
        print("Konfigurasi")
        print(f"  Ukuran matriks : {args.size} x {args.size}")
        print(f"  Jumlah proses  : {communicator.Get_size()}")
        print(f"  Seed           : {args.seed}")
        print("\nHasil distributed")
        print(f"  Waktu total    : {elapsed_seconds:.6f} detik")
        print(f"  Checksum       : {matrix_checksum(result):.6f}")
        print(f"  Komputer proses: {', '.join(dict.fromkeys(process_hosts))}")
        if args.show_result:
            print_matrix(result, "Matriks hasil (A x B)")
