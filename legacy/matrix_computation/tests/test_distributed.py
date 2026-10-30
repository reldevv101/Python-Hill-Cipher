import unittest

from matrix_benchmark.distributed import split_rows_for_processes


class DistributedHelperTests(unittest.TestCase):
    def test_split_rows_preserves_order_and_balances_chunks(self) -> None:
        matrix = [[float(value)] for value in range(5)]

        chunks = split_rows_for_processes(matrix, process_count=3)

        self.assertEqual([len(chunk) for chunk in chunks], [2, 2, 1])
        self.assertEqual([row for chunk in chunks for row in chunk], matrix)

    def test_split_rows_creates_empty_chunks_when_processes_exceed_rows(self) -> None:
        chunks = split_rows_for_processes([[1.0]], process_count=3)

        self.assertEqual(chunks, [[[1.0]], [], []])

    def test_split_rows_rejects_invalid_process_count(self) -> None:
        with self.assertRaises(ValueError):
            split_rows_for_processes([[1.0]], process_count=0)
