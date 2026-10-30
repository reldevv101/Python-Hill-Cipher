"""MPI processing of independent Hill Cipher blocks."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any

from .alphabet import normalize_plaintext
from .blocks import split_blocks
from .core import transform_blocks
from .key import Key, inverse_key, validate_key


def _import_mpi():
    try:
        from mpi4py import MPI
    except ImportError as error:
        raise RuntimeError(
            "mpi4py atau runtime MPI belum siap. Pasang runtime MPI, lalu jalankan "
            "`py -3 -m pip install mpi4py` terlebih dahulu."
        ) from error
    return MPI


def _prepare_encryption(
    plaintext: str | None,
    key: Sequence[Sequence[int]] | None,
) -> tuple[Key, str, None]:
    matrix = validate_key(key)  # type: ignore[arg-type]
    normalized = normalize_plaintext(plaintext)  # type: ignore[arg-type]
    if len(normalized) % 2:
        normalized += "X"
    return matrix, normalized, None


def _prepare_decryption(
    ciphertext: str | None,
    key: Sequence[Sequence[int]] | None,
    original_length: int | None,
) -> tuple[Key, str, int | None]:
    if not isinstance(ciphertext, str):
        raise TypeError("Ciphertext harus berupa teks pada rank 0.")
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
    return inverse_key(key), ciphertext, original_length  # type: ignore[arg-type]


def _distributed_transform(
    text: str | None,
    key: Sequence[Sequence[int]] | None,
    *,
    prepare: Callable[
        [str | None, Sequence[Sequence[int]] | None, int | None],
        tuple[Key, str, int | None],
    ],
    original_length: int | None = None,
    communicator: Any | None = None,
) -> tuple[str | None, float | None]:
    MPI = _import_mpi()
    comm = communicator if communicator is not None else MPI.COMM_WORLD
    rank = comm.Get_rank()
    process_count = comm.Get_size()

    control = None
    chunks = None
    if rank == 0:
        try:
            worker_key, prepared_text, trim_length = prepare(text, key, original_length)
            chunks = split_blocks(prepared_text, process_count)
            chunks.extend("" for _ in range(process_count - len(chunks)))
            control = (True, worker_key, trim_length, "")
        except (TypeError, ValueError) as error:
            control = (False, None, None, str(error))

    # Keep all ranks on the same path when root-side validation fails.
    comm.Barrier()
    started_at = MPI.Wtime()
    succeeded, worker_key, trim_length, error_message = comm.bcast(control, root=0)
    if not succeeded:
        raise ValueError(error_message)

    local_text = comm.scatter(chunks, root=0)
    local_result = transform_blocks(local_text, worker_key)
    result_chunks = comm.gather(local_result, root=0)
    elapsed_seconds = MPI.Wtime() - started_at

    if rank != 0:
        return None, None
    result = "".join(result_chunks)
    if trim_length is not None:
        result = result[:trim_length]
    return result, elapsed_seconds


def _prepare_encryption_call(text, key, _original_length):
    return _prepare_encryption(text, key)


def _prepare_decryption_call(text, key, original_length):
    return _prepare_decryption(text, key, original_length)


def distributed_encrypt(
    plaintext: str | None,
    key: Sequence[Sequence[int]] | None,
    *,
    communicator: Any | None = None,
) -> tuple[str | None, float | None]:
    """Encrypt on all ranks; only rank 0 supplies input and receives output.

    Elapsed time includes broadcasting the validated key, scattering prepared
    blocks, local transforms, and gathering the result. Root-side normalization
    and key validation happen before the timed communication section.
    """

    return _distributed_transform(
        plaintext,
        key,
        prepare=_prepare_encryption_call,
        communicator=communicator,
    )


def distributed_decrypt(
    ciphertext: str | None,
    key: Sequence[Sequence[int]] | None,
    *,
    original_length: int | None = None,
    communicator: Any | None = None,
) -> tuple[str | None, float | None]:
    """Decrypt on all ranks; only rank 0 supplies input and receives output."""

    return _distributed_transform(
        ciphertext,
        key,
        prepare=_prepare_decryption_call,
        original_length=original_length,
        communicator=communicator,
    )
