"""Tests for multiprocessing Hill Cipher block processing."""

from __future__ import annotations

import unittest

from hill_cipher_benchmark import decrypt, encrypt
from hill_cipher_benchmark.parallel import (
    parallel_decrypt,
    parallel_encrypt,
    split_blocks,
    timed_parallel_decrypt,
    timed_parallel_encrypt,
)


class HillCipherParallelTests(unittest.TestCase):
    KEY = ((3, 3), (2, 5))

    def test_split_blocks_balances_work_and_preserves_order(self) -> None:
        chunks = split_blocks("ABCDEFGHIJ", 3)

        self.assertEqual(chunks, ["ABCD", "EFGH", "IJ"])
        self.assertEqual("".join(chunks), "ABCDEFGHIJ")

    def test_split_blocks_caps_chunks_at_available_blocks(self) -> None:
        self.assertEqual(split_blocks("ABCD", 5), ["AB", "CD"])

    def test_split_blocks_rejects_unaligned_input(self) -> None:
        with self.assertRaises(ValueError):
            split_blocks("ABC", 2)

    def test_parallel_encryption_matches_sequential(self) -> None:
        for plaintext, workers in (("HELP", 2), ("Hello, world!", 3), ("CAT", 8), ("", 2)):
            with self.subTest(plaintext=plaintext, workers=workers):
                self.assertEqual(
                    parallel_encrypt(plaintext, self.KEY, workers),
                    encrypt(plaintext, self.KEY),
                )

    def test_parallel_decryption_matches_sequential(self) -> None:
        plaintext = "Multiprocessing keeps every two-letter block in order."
        normalized_length = len("MULTIPROCESSINGKEEPSEVERYTWOLETTERBLOCKINORDER")
        ciphertext = encrypt(plaintext, self.KEY)

        self.assertEqual(
            parallel_decrypt(ciphertext, self.KEY, 4, original_length=normalized_length),
            decrypt(ciphertext, self.KEY, original_length=normalized_length),
        )

    def test_rejects_invalid_worker_count(self) -> None:
        for workers in (0, -1, 1.5, True):
            with self.subTest(workers=workers), self.assertRaises(ValueError):
                parallel_encrypt("HELP", self.KEY, workers)  # type: ignore[arg-type]

    def test_timed_functions_return_results_and_non_negative_durations(self) -> None:
        ciphertext, encryption_seconds = timed_parallel_encrypt("HELP", self.KEY, 2)
        plaintext, decryption_seconds = timed_parallel_decrypt(
            ciphertext,
            self.KEY,
            2,
            original_length=4,
        )

        self.assertEqual(ciphertext, "HIAT")
        self.assertEqual(plaintext, "HELP")
        self.assertGreaterEqual(encryption_seconds, 0.0)
        self.assertGreaterEqual(decryption_seconds, 0.0)


if __name__ == "__main__":
    unittest.main()
