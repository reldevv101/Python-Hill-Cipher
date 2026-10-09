"""Tkinter desktop interface for local matrix benchmarks."""

from __future__ import annotations

import os
import queue
import random
import threading
import tkinter as tk
from tkinter import messagebox, ttk

from .parallel import timed_parallel_multiply
from .sequential import Matrix, matrix_checksum, timed_multiply


DISPLAY_LIMIT = 10


def make_matrix(size: int, rng: random.Random) -> Matrix:
    return [[rng.uniform(-10.0, 10.0) for _ in range(size)] for _ in range(size)]


class MatrixBenchmarkApp(tk.Tk):
    """A desktop UI that keeps expensive work off the Tkinter event loop."""

    def __init__(self) -> None:
        super().__init__()
        self.title("Matrix Computation Benchmark")
        self.minsize(900, 650)

        self.size_var = tk.StringVar(value="3")
        self.seed_var = tk.StringVar(value="7")
        self.mode_var = tk.StringVar(value="both")
        self.workers_var = tk.StringVar(value=str(min(4, os.cpu_count() or 1)))
        self.status_var = tk.StringVar(value="Siap dijalankan.")
        self.progress_var = tk.DoubleVar(value=0)
        self.sequential_var = tk.StringVar(value="-")
        self.parallel_var = tk.StringVar(value="-")
        self.speedup_var = tk.StringVar(value="-")
        self.checksum_var = tk.StringVar(value="-")
        self.queue: queue.Queue[tuple[str, object]] = queue.Queue()
        self.matrix_tables: dict[str, ttk.Treeview] = {}

        self._build_layout()
        self.after(50, self._process_messages)

    def _build_layout(self) -> None:
        outer = ttk.Frame(self, padding=16)
        outer.grid(sticky="nsew")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        outer.columnconfigure(0, weight=1)
        outer.rowconfigure(3, weight=1)

        ttk.Label(
            outer,
            text="MATRIX COMPUTATION BENCHMARK",
            font=("Segoe UI", 16, "bold"),
        ).grid(row=0, column=0, sticky="w")
        ttk.Label(
            outer,
            text="Sequential dan parallel pada satu komputer. Gunakan konsol untuk MPI dua komputer.",
        ).grid(row=1, column=0, sticky="w", pady=(2, 12))

        controls = ttk.LabelFrame(outer, text="Konfigurasi", padding=12)
        controls.grid(row=2, column=0, sticky="ew")
        for column in range(8):
            controls.columnconfigure(column, weight=1)

        self._add_field(controls, "Ukuran N", self.size_var, 0)
        self._add_field(controls, "Seed", self.seed_var, 2)
        self._add_combo(controls, "Mode", self.mode_var, ("sequential", "parallel", "both"), 4)
        self._add_field(controls, "Worker", self.workers_var, 6)

        self.start_button = ttk.Button(controls, text="Mulai Benchmark", command=self.start)
        self.start_button.grid(row=2, column=0, columnspan=4, sticky="ew", pady=(12, 0))
        ttk.Button(controls, text="Reset", command=self.reset).grid(
            row=2, column=4, columnspan=4, sticky="ew", pady=(12, 0), padx=(8, 0)
        )

        body = ttk.Frame(outer)
        body.grid(row=3, column=0, sticky="nsew", pady=(12, 0))
        body.columnconfigure(0, weight=1)
        body.rowconfigure(1, weight=1)

        results = ttk.LabelFrame(body, text="Hasil Benchmark", padding=12)
        results.grid(row=0, column=0, sticky="ew")
        self._add_result(results, "Sequential", self.sequential_var, 0)
        self._add_result(results, "Parallel", self.parallel_var, 1)
        self._add_result(results, "Speedup", self.speedup_var, 2)
        self._add_result(results, "Checksum", self.checksum_var, 3)

        matrices = ttk.LabelFrame(body, text="Matriks", padding=8)
        matrices.grid(row=1, column=0, sticky="nsew", pady=(12, 0))
        matrices.columnconfigure(0, weight=1)
        matrices.rowconfigure(0, weight=1)
        notebook = ttk.Notebook(matrices)
        notebook.grid(row=0, column=0, sticky="nsew")
        for label in ("Matriks A", "Matriks B", "Hasil A x B"):
            frame = ttk.Frame(notebook, padding=6)
            notebook.add(frame, text=label)
            table = ttk.Treeview(frame, show="headings", height=10)
            table.pack(fill="both", expand=True)
            self.matrix_tables[label] = table

        footer = ttk.Frame(outer)
        footer.grid(row=4, column=0, sticky="ew", pady=(12, 0))
        footer.columnconfigure(0, weight=1)
        ttk.Label(footer, textvariable=self.status_var).grid(row=0, column=0, sticky="w")
        ttk.Progressbar(footer, variable=self.progress_var, maximum=100).grid(
            row=1, column=0, sticky="ew", pady=(4, 0)
        )

    @staticmethod
    def _add_field(parent: ttk.Widget, label: str, variable: tk.StringVar, column: int) -> None:
        ttk.Label(parent, text=label).grid(row=0, column=column, columnspan=2, sticky="w")
        ttk.Entry(parent, textvariable=variable, width=12).grid(
            row=1, column=column, columnspan=2, sticky="ew", padx=(0, 8)
        )

    @staticmethod
    def _add_combo(
        parent: ttk.Widget,
        label: str,
        variable: tk.StringVar,
        values: tuple[str, ...],
        column: int,
    ) -> None:
        ttk.Label(parent, text=label).grid(row=0, column=column, columnspan=2, sticky="w")
        ttk.Combobox(parent, textvariable=variable, values=values, state="readonly").grid(
            row=1, column=column, columnspan=2, sticky="ew", padx=(0, 8)
        )

    @staticmethod
    def _add_result(parent: ttk.Widget, label: str, variable: tk.StringVar, column: int) -> None:
        parent.columnconfigure(column, weight=1)
        ttk.Label(parent, text=label).grid(row=0, column=column, sticky="w")
        ttk.Label(parent, textvariable=variable, font=("Segoe UI", 10, "bold")).grid(
            row=1, column=column, sticky="w", pady=(2, 0)
        )

    def start(self) -> None:
        try:
            size = int(self.size_var.get())
            seed = int(self.seed_var.get())
            workers = int(self.workers_var.get())
            if size <= 0 or workers <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Input tidak valid", "Ukuran dan worker harus bilangan bulat positif.")
            return

        self.start_button.configure(state="disabled")
        self.progress_var.set(0)
        self.status_var.set("Menyiapkan matriks...")
        thread = threading.Thread(
            target=self._run_benchmark,
            args=(size, seed, self.mode_var.get(), workers),
            daemon=True,
        )
        thread.start()

    def _run_benchmark(self, size: int, seed: int, mode: str, workers: int) -> None:
        try:
            rng = random.Random(seed)
            matrix_a = make_matrix(size, rng)
            matrix_b = make_matrix(size, rng)
            sequential_result: Matrix | None = None
            parallel_result: Matrix | None = None
            sequential_elapsed: float | None = None
            parallel_elapsed: float | None = None

            def progress(label: str, base: float, span: float):
                def update(completed: int, total: int) -> None:
                    percent = base + span * completed / total
                    self.queue.put(("progress", (label, percent)))

                return update

            if mode in ("sequential", "both"):
                sequential_result, sequential_elapsed = timed_multiply(
                    matrix_a, matrix_b, progress("Sequential", 0, 50 if mode == "both" else 100)
                )
            if mode in ("parallel", "both"):
                base = 50 if mode == "both" else 0
                span = 50 if mode == "both" else 100
                parallel_result, parallel_elapsed = timed_parallel_multiply(
                    matrix_a, matrix_b, workers, progress("Parallel", base, span)
                )

            if sequential_result is not None and parallel_result is not None:
                if sequential_result != parallel_result:
                    raise RuntimeError("Hasil parallel tidak sama dengan hasil sequential.")

            result = sequential_result if sequential_result is not None else parallel_result
            speedup = (
                sequential_elapsed / parallel_elapsed
                if sequential_elapsed is not None and parallel_elapsed is not None
                else None
            )
            self.queue.put(
                (
                    "done",
                    {
                        "size": size,
                        "matrix_a": matrix_a,
                        "matrix_b": matrix_b,
                        "result": result,
                        "sequential": sequential_elapsed,
                        "parallel": parallel_elapsed,
                        "speedup": speedup,
                        "checksum": matrix_checksum(result) if result is not None else 0.0,
                    },
                )
            )
        except Exception as error:  # noqa: BLE001 - surface background failures to the UI.
            self.queue.put(("error", str(error)))

    def _process_messages(self) -> None:
        try:
            while True:
                message, value = self.queue.get_nowait()
                if message == "progress":
                    label, percent = value  # type: ignore[misc]
                    self.progress_var.set(percent)
                    self.status_var.set(f"Menghitung: {label} ({percent:.0f}%)")
                elif message == "done":
                    self._show_result(value)  # type: ignore[arg-type]
                elif message == "error":
                    self.start_button.configure(state="normal")
                    self.status_var.set("Perhitungan gagal.")
                    messagebox.showerror("Benchmark gagal", str(value))
        except queue.Empty:
            pass
        self.after(50, self._process_messages)

    def _show_result(self, data: dict[str, object]) -> None:
        sequential = data["sequential"]
        parallel = data["parallel"]
        speedup = data["speedup"]
        self.sequential_var.set(f"{sequential:.6f} detik" if sequential is not None else "Tidak dijalankan")
        self.parallel_var.set(f"{parallel:.6f} detik" if parallel is not None else "Tidak dijalankan")
        self.speedup_var.set(f"{speedup:.2f}x" if speedup is not None else "-")
        self.checksum_var.set(f"{data['checksum']:.6f}")
        self.progress_var.set(100)
        self.status_var.set("Selesai. Hasil sequential dan parallel tervalidasi bila keduanya dijalankan.")
        self.start_button.configure(state="normal")

        if int(data["size"]) <= DISPLAY_LIMIT:
            self._populate_table("Matriks A", data["matrix_a"])  # type: ignore[arg-type]
            self._populate_table("Matriks B", data["matrix_b"])  # type: ignore[arg-type]
            self._populate_table("Hasil A x B", data["result"])  # type: ignore[arg-type]
        else:
            for label in self.matrix_tables:
                self._clear_table(label, f"Tidak ditampilkan: ukuran lebih dari {DISPLAY_LIMIT} x {DISPLAY_LIMIT}.")

    def _populate_table(self, label: str, matrix: Matrix) -> None:
        table = self.matrix_tables[label]
        table.delete(*table.get_children())
        columns = [f"C{index + 1}" for index in range(len(matrix[0]))]
        table.configure(columns=columns)
        for column in columns:
            table.heading(column, text=column)
            table.column(column, anchor="e", width=95, stretch=True)
        for row in matrix:
            table.insert("", "end", values=[f"{value:.3f}" for value in row])

    def _clear_table(self, label: str, message: str) -> None:
        table = self.matrix_tables[label]
        table.delete(*table.get_children())
        table.configure(columns=("message",))
        table.heading("message", text="Informasi")
        table.column("message", width=500, anchor="w")
        table.insert("", "end", values=(message,))

    def reset(self) -> None:
        self.size_var.set("3")
        self.seed_var.set("7")
        self.mode_var.set("both")
        self.workers_var.set(str(min(4, os.cpu_count() or 1)))
        self.sequential_var.set("-")
        self.parallel_var.set("-")
        self.speedup_var.set("-")
        self.checksum_var.set("-")
        self.progress_var.set(0)
        self.status_var.set("Siap dijalankan.")
        for label in self.matrix_tables:
            self._clear_table(label, "Belum ada hasil.")


def main() -> None:
    app = MatrixBenchmarkApp()
    app.reset()
    app.mainloop()
