import unittest

from matrix_benchmark.parallel import parallel_multiply, timed_parallel_multiply
from matrix_benchmark.sequential import multiply


class ParallelMultiplyTests(unittest.TestCase):
    def test_parallel_result_matches_sequential_result(self) -> None:
        left = [[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]]
        right = [[7.0, 8.0], [9.0, 10.0]]
        self.assertEqual(parallel_multiply(left, right, workers=2), multiply(left, right))

    def test_timed_parallel_multiply_returns_non_negative_time(self) -> None:
        result, elapsed = timed_parallel_multiply([[2.0]], [[4.0]], workers=1)
        self.assertEqual(result, [[8.0]])
        self.assertGreaterEqual(elapsed, 0.0)

    def test_rejects_invalid_worker_count(self) -> None:
        with self.assertRaises(ValueError):
            parallel_multiply([[1.0]], [[1.0]], workers=0)

    def test_parallel_reports_completed_rows(self) -> None:
        calls: list[tuple[int, int]] = []

        parallel_multiply(
            [[1.0], [2.0]],
            [[3.0]],
            workers=2,
            progress=lambda completed, total: calls.append((completed, total)),
        )

        self.assertEqual(calls[-1], (2, 2))
