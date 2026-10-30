"""Command-line interface for distributed Hill Cipher MPI runs."""

from __future__ import annotations

import argparse
from collections.abc import Sequence

from .distributed import _import_mpi, distributed_decrypt, distributed_encrypt
from .key import Key


def _parse_key(value: str) -> Key:
    try:
        entries = [int(part.strip()) for part in value.split(",")]
    except ValueError as error:
        raise argparse.ArgumentTypeError("Kunci harus berisi empat bilangan bulat dipisahkan koma.") from error
    if len(entries) != 4:
        raise argparse.ArgumentTypeError("Kunci harus berformat a,b,c,d untuk matriks 2 x 2.")
    return ((entries[0], entries[1]), (entries[2], entries[3]))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Enkripsi atau dekripsi Hill Cipher dengan proses MPI."
    )
    parser.add_argument("--action", choices=("encrypt", "decrypt"), required=True)
    parser.add_argument(
        "--text",
        required=True,
        help="Plaintext untuk encrypt atau ciphertext A-Z untuk decrypt.",
    )
    parser.add_argument(
        "--key",
        type=_parse_key,
        default=((3, 3), (2, 5)),
        help="Empat integer a,b,c,d untuk matriks [[a,b],[c,d]] (default: 3,3,2,5).",
    )
    parser.add_argument(
        "--original-length",
        type=int,
        help="Panjang plaintext setelah normalisasi; gunakan saat decrypt untuk membuang padding.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.original_length is not None and args.original_length < 0:
        parser.error("--original-length harus nol atau lebih.")
    if args.action == "encrypt" and args.original_length is not None:
        parser.error("--original-length hanya digunakan untuk action decrypt.")

    MPI = _import_mpi()
    communicator = MPI.COMM_WORLD
    rank = communicator.Get_rank()
    process_count = communicator.Get_size()
    root_text = args.text if rank == 0 else None
    root_key = args.key if rank == 0 else None

    if args.action == "encrypt":
        result, elapsed = distributed_encrypt(root_text, root_key, communicator=communicator)
        result_label = "Ciphertext"
    else:
        result, elapsed = distributed_decrypt(
            root_text,
            root_key,
            original_length=args.original_length if rank == 0 else None,
            communicator=communicator,
        )
        result_label = "Plaintext"

    if rank == 0:
        print("Hill Cipher MPI")
        print(f"Aksi          : {args.action}")
        print(f"Jumlah rank   : {process_count}")
        print(f"Waktu total   : {elapsed:.6f} detik")
        print(f"{result_label:<14}: {result}")


if __name__ == "__main__":
    main()
