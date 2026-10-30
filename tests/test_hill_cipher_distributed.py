"""Multi-rank integration tests for distributed Hill Cipher processing."""

from __future__ import annotations

import importlib.util
import shutil
import subprocess
import sys
import unittest
from textwrap import dedent


@unittest.skipUnless(
    importlib.util.find_spec("mpi4py") is not None and shutil.which("mpiexec") is not None,
    "mpi4py dan mpiexec diperlukan untuk tes MPI.",
)
class HillCipherDistributedTests(unittest.TestCase):
    def test_mpi_encrypt_decrypt_empty_chunks_and_input_error(self) -> None:
        script = dedent(
            """
            from mpi4py import MPI
            from matrix_benchmark.hill_cipher.distributed import distributed_decrypt, distributed_encrypt

            comm = MPI.COMM_WORLD
            rank = comm.Get_rank()
            plaintext = "Hello!" if rank == 0 else None
            key = ((3, 3), (2, 5)) if rank == 0 else None

            ciphertext, encryption_seconds = distributed_encrypt(plaintext, key)
            assert (ciphertext == "HIOZHN") if rank == 0 else (ciphertext is None)
            assert (encryption_seconds is not None) if rank == 0 else (encryption_seconds is None)

            recovered, decryption_seconds = distributed_decrypt(
                ciphertext,
                key,
                original_length=5 if rank == 0 else None,
            )
            assert (recovered == "HELLO") if rank == 0 else (recovered is None)
            assert (decryption_seconds is not None) if rank == 0 else (decryption_seconds is None)

            short_result, _ = distributed_encrypt(
                "AB" if rank == 0 else None,
                key,
            )
            assert (short_result == "DF") if rank == 0 else (short_result is None)

            invalid_key = ((2, 0), (0, 1)) if rank == 0 else None
            try:
                distributed_encrypt("TEST" if rank == 0 else None, invalid_key)
            except ValueError as error:
                assert "invers modulo 26" in str(error)
            else:
                raise AssertionError("Kunci tidak valid seharusnya ditolak pada semua rank.")
            """
        )
        completed = subprocess.run(
            [shutil.which("mpiexec") or "mpiexec", "-n", "4", sys.executable, "-c", script],
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)


if __name__ == "__main__":
    unittest.main()
