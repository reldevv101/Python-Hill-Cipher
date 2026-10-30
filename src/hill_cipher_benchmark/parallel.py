"""Single-computer multiprocessing for independent Hill Cipher blocks."""

from __future__ import annotations

import multiprocessing as mp
from collections.abc import Sequence
from time import perf_counter

from .alphabet import normalize_plaintext
from .blocks import split_blocks
from .core import transform_blocks
from .key import Key, inverse_key, validate_key

_worker_key: Key | None = None


def _initialize_worker(key: Key) -> None:
    """Install the validated key once in each spawned worker process."""

    global _worker_key
    _worker_key = key


def _transform_chunk(text: str) -> str:
    """Transform one even-length chunk in a worker process."""

    if _worker_key is None:
        raise RuntimeError("Kunci worker belum diinisialisasi.")
    return transform_blocks(text, _worker_key)


def _validate_workers(workers: int) -> None:
    if not isinstance(workers, int) or isinstance(workers, bool) or workers <= 0:
        raise ValueError("Jumlah worker harus berupa bilangan bulat positif.")


def _map_chunks(chunks: list[str], key: Key, workers: int) -> str:
    if not chunks:
        return ""
    active_workers = min(workers, len(chunks))
    with mp.Pool(
        processes=active_workers,
        initializer=_initialize_worker,
        initargs=(key,),
    ) as pool:
        return "".join(pool.map(_transform_chunk, chunks))


def parallel_encrypt(plaintext: str, key: Sequence[Sequence[int]], workers: int) -> str:
    """Encrypt plaintext by distributing its independent two-letter blocks.

    The normalization and odd-length X padding rules match ``core.encrypt``.
    Pool startup, task distribution, and result collection are included in the
    call's elapsed time when used through ``timed_parallel_encrypt``.
    """

    _validate_workers(workers)
    matrix = validate_key(key)
    text = normalize_plaintext(plaintext)
    if len(text) % 2:
        text += "X"
    return _map_chunks(split_blocks(text, workers), matrix, workers)


def parallel_decrypt(
    ciphertext: str,
    key: Sequence[Sequence[int]],
    workers: int,
    *,
    original_length: int | None = None,
) -> str:
    """Decrypt ciphertext in parallel, optionally removing known X padding."""

    _validate_workers(workers)
    if not isinstance(ciphertext, str):
        raise TypeError("Ciphertext harus berupa teks.")
    if any(character < "A" or character > "Z" for character in ciphertext):
        raise ValueError("Ciphertext harus berisi huruf kapital A-Z saja.")
    if len(ciphertext) % 2:
        raise ValueError("Panjang ciphertext harus genap.")
    if original_length is not None and (
        not isinstance(original_length, int)
        or isinstance(original_length, bool)
        or original_length < 0
        or original_length > len(ciphertext)
    ):
        raise ValueError("Panjang plaintext asli tidak valid untuk ciphertext ini.")

    inverse = inverse_key(key)
    plaintext = _map_chunks(split_blocks(ciphertext, workers), inverse, workers)
    return plaintext if original_length is None else plaintext[:original_length]


def timed_parallel_encrypt(
    plaintext: str,
    key: Sequence[Sequence[int]],
    workers: int,
) -> tuple[str, float]:
    """Encrypt in parallel and return the result with end-to-end elapsed time."""

    started_at = perf_counter()
    ciphertext = parallel_encrypt(plaintext, key, workers)
    return ciphertext, perf_counter() - started_at


def timed_parallel_decrypt(
    ciphertext: str,
    key: Sequence[Sequence[int]],
    workers: int,
    *,
    original_length: int | None = None,
) -> tuple[str, float]:
    """Decrypt in parallel and return the result with end-to-end elapsed time."""

    started_at = perf_counter()
    plaintext = parallel_decrypt(
        ciphertext,
        key,
        workers,
        original_length=original_length,
    )
    return plaintext, perf_counter() - started_at
