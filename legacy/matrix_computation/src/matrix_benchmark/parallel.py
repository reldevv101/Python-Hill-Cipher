"""Single-computer parallel matrix multiplication using multiprocessing."""

from __future__ import annotations

import multiprocessing as mp
from collections.abc import Callable
from time import perf_counter

from .sequential import Matrix, _validate_matrices

_right_columns: list[tuple[float, ...]] = []


def _set_right_columns(right_columns: list[tuple[float, ...]]) -> None:
    """Store read-only input once in every worker process."""
    global _right_columns
    _right_columns = right_columns


def _multiply_rows(rows: list[list[float]]) -> Matrix:
    """Multiply one chunk of left-matrix rows in a worker process."""
    return [
        [sum(a * b for a, b in zip(left_row, right_column)) for right_column in _right_columns]
        for left_row in rows
    ]


def _split_rows(matrix: Matrix, chunks: int) -> list[Matrix]:
    chunk_size = max(1, (len(matrix) + chunks - 1) // chunks)
    return [matrix[index : index + chunk_size] for index in range(0, len(matrix), chunk_size)]


def parallel_multiply(
    left: Matrix,
    right: Matrix,
    workers: int,
    progress: Callable[[int, int], None] | None = None,
) -> Matrix:
    """Return `left x right` by dividing left-matrix rows among processes."""
    _validate_matrices(left, right)
    if workers <= 0:
        raise ValueError("Jumlah worker harus berupa bilangan bulat positif.")

    active_workers = min(workers, len(left))
    right_columns = [tuple(column) for column in zip(*right)]
    row_chunks = _split_rows(left, active_workers)

    # Windows uses spawn: worker functions must remain at module level.
    with mp.Pool(
        processes=active_workers,
        initializer=_set_right_columns,
        initargs=(right_columns,),
    ) as pool:
        result_chunks: list[Matrix] = []
        completed_rows = 0
        for chunk, result_chunk in zip(row_chunks, pool.imap(_multiply_rows, row_chunks)):
            result_chunks.append(result_chunk)
            completed_rows += len(chunk)
            if progress is not None:
                progress(completed_rows, len(left))

    return [row for chunk in result_chunks for row in chunk]


def timed_parallel_multiply(
    left: Matrix,
    right: Matrix,
    workers: int,
    progress: Callable[[int, int], None] | None = None,
) -> tuple[Matrix, float]:
    """Multiply in parallel and return the result with elapsed seconds."""
    started_at = perf_counter()
    result = parallel_multiply(left, right, workers, progress)
    return result, perf_counter() - started_at
