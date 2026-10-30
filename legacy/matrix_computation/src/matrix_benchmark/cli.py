"""Command-line entry point for the sequential benchmark."""

from __future__ import annotations

import argparse
from datetime import datetime
import os
import random
from pathlib import Path

from .parallel import timed_parallel_multiply
from .presentation import make_progress_reporter, print_matrix, print_title
from .reporting import append_benchmark_result
from .sequential import matrix_checksum, timed_multiply


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Benchmark perkalian matriks sequential dan parallel."
    )
    parser.add_argument(
        "--size", type=int, default=100,
        help="Ukuran matriks persegi N x N (default: 100).",
    )
    parser.add_argument(
        "--seed", type=int, default=42,
        help="Seed untuk data acak yang dapat diulang (default: 42).",
    )
    parser.add_argument(
        "--mode", choices=("sequential", "parallel", "both"), default="sequential",
        help="Metode yang diuji (default: sequential).",
    )
    parser.add_argument(
        "--workers", type=int, default=os.cpu_count() or 1,
        help="Jumlah proses untuk mode parallel (default: jumlah CPU).",
    )
    parser.add_argument(
        "--save-csv",
        type=Path,
        help="Simpan hasil percobaan sebagai satu baris CSV pada path ini.",
    )
    parser.add_argument(
        "--show-result",
        action="store_true",
        help="Tampilkan matriks hasil. Disarankan hanya untuk ukuran kecil.",
    )
    parser.add_argument(
        "--display-limit",
        type=int,
        default=10,
        help="Ukuran maksimum untuk --show-result (default: 10).",
    )
    parser.add_argument(
        "--progress",
        action="store_true",
        help="Tampilkan progress bar selama perhitungan.",
    )
    return parser


def make_matrix(size: int, rng: random.Random) -> list[list[float]]:
    return [[rng.uniform(-10.0, 10.0) for _ in range(size)] for _ in range(size)]


def main() -> None:
    args = build_parser().parse_args()
    if args.size <= 0:
        raise SystemExit("--size harus berupa bilangan bulat positif.")
    if args.workers <= 0:
        raise SystemExit("--workers harus berupa bilangan bulat positif.")
    if args.display_limit <= 0:
        raise SystemExit("--display-limit harus berupa bilangan bulat positif.")
    if args.show_result and args.size > args.display_limit:
        raise SystemExit(
            "Ukuran matriks terlalu besar untuk ditampilkan. "
            "Naikkan --display-limit atau gunakan --size yang lebih kecil."
        )

    rng = random.Random(args.seed)
    matrix_a = make_matrix(args.size, rng)
    matrix_b = make_matrix(args.size, rng)
    print_title("MATRIX COMPUTATION BENCHMARK")
    print("Konfigurasi")
    print(f"  Ukuran matriks : {args.size} x {args.size}")
    print(f"  Seed           : {args.seed}")
    print(f"  Mode           : {args.mode}")

    sequential_result: list[list[float]] | None = None
    sequential_elapsed: float | None = None
    parallel_result: list[list[float]] | None = None
    parallel_elapsed: float | None = None
    speedup: float | None = None
    if args.mode in ("sequential", "both"):
        progress = make_progress_reporter("Sequential") if args.progress else None
        sequential_result, sequential_elapsed = timed_multiply(matrix_a, matrix_b, progress)
        print("\nHasil sequential")
        print(f"  Waktu    : {sequential_elapsed:.6f} detik")
        print(f"  Checksum : {matrix_checksum(sequential_result):.6f}")

    if args.mode in ("parallel", "both"):
        progress = make_progress_reporter("Parallel") if args.progress else None
        parallel_result, parallel_elapsed = timed_parallel_multiply(
            matrix_a, matrix_b, args.workers, progress
        )
        print("\nHasil parallel")
        print(f"  Proses   : {args.workers}")
        print(f"  Waktu    : {parallel_elapsed:.6f} detik")
        print(f"  Checksum : {matrix_checksum(parallel_result):.6f}")
        if sequential_result is not None and sequential_elapsed is not None:
            if parallel_result != sequential_result:
                raise RuntimeError("Hasil parallel tidak sama dengan hasil sequential.")
            speedup = sequential_elapsed / parallel_elapsed
            print(f"  Validasi : hasil sama")
            print(f"  Speedup  : {speedup:.2f}x")

    if args.show_result:
        result_to_show = sequential_result if sequential_result is not None else parallel_result
        if result_to_show is not None:
            print_matrix(result_to_show, "Matriks hasil (A x B)")

    if args.save_csv is not None:
        result = sequential_result if sequential_result is not None else parallel_result
        checksum = matrix_checksum(result) if result is not None else ""
        append_benchmark_result(
            args.save_csv,
            {
                "timestamp": datetime.now().astimezone().isoformat(timespec="seconds"),
                "size": args.size,
                "seed": args.seed,
                "mode": args.mode,
                "workers": args.workers if args.mode != "sequential" else 1,
                "sequential_seconds": (
                    f"{sequential_elapsed:.6f}" if sequential_elapsed is not None else ""
                ),
                "parallel_seconds": (
                    f"{parallel_elapsed:.6f}" if parallel_elapsed is not None else ""
                ),
                "speedup": f"{speedup:.6f}" if speedup is not None else "",
                "checksum": f"{checksum:.6f}" if isinstance(checksum, float) else checksum,
                "result_match": (
                    "yes" if args.mode == "both" else "not_checked"
                ),
            },
        )
        print(f"\nHasil disimpan ke: {args.save_csv}")


if __name__ == "__main__":
    main()
