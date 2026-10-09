# Matrix Computation Benchmark

Fondasi proyek untuk membandingkan kinerja komputasi matriks. Tahap ini berisi
perkalian matriks **sequential**, **parallel satu komputer**, dan fondasi
**distributed computing dengan MPI**. GUI belum dibuat.

Penjelasan konsep, algoritma, dan bahan laporan tersedia di
[docs/project-concepts.md](docs/project-concepts.md).

## Kebutuhan

- Python 3.10 atau lebih baru
- Tidak ada dependency pihak ketiga

## Menjalankan di konsol

1. Buka PowerShell.
2. Masuk ke folder proyek:

```powershell
cd "C:\Users\USER\Documents\Codex\Python Matrix Computation"
```

3. Jalankan salah satu perintah berikut.

### Sequential

Versi dasar: seluruh perkalian dikerjakan oleh satu proses.

```powershell
py -3 main.py --size 100 --mode sequential
```

### Parallel

Baris pada matriks kiri dibagi ke beberapa proses dalam satu komputer.

```powershell
py -3 main.py --size 250 --mode parallel --workers 4
```

### Perbandingan sequential dan parallel

Ini adalah perintah utama untuk benchmark. Program menjalankan kedua metode
dengan data yang sama, memeriksa kesamaan hasil, lalu menghitung speedup.

```powershell
py -3 main.py --size 250 --mode both --workers 4
```

Gunakan `--seed` yang sama saat membandingkan beberapa percobaan agar matriks
inputnya tetap sama:

```powershell
py -3 main.py --size 500 --seed 7 --mode both --workers 4
```

### Menampilkan hasil perkalian matriks

Untuk demonstrasi, gunakan matriks kecil dan tambahkan `--show-result`:

```powershell
py -3 main.py --size 3 --seed 7 --mode both --workers 2 --show-result
```

Matriks hasil `A x B` ditampilkan di konsol. Demi keterbacaan, ukuran maksimum
tampilan adalah `10 x 10` secara default. Ubah dengan `--display-limit` bila
diperlukan.

### Progress bar konsol

```powershell
py -3 main.py --size 250 --mode both --workers 4 --progress
```

Progress bar cocok untuk demonstrasi. Matikan `--progress` saat mencatat waktu
benchmark agar output terminal tidak memengaruhi pengukuran.

## Desktop GUI

Versi desktop menyediakan input ukuran, seed, mode, dan jumlah worker. GUI juga
menampilkan progress bar, waktu, checksum, speedup, serta tabel matriks `A`,
`B`, dan hasil `A x B` untuk ukuran sampai `10 x 10`.

Jalankan dari folder proyek:

```powershell
py -3 main_gui.py
```

Gunakan ukuran `3` sampai `10` ketika ingin menunjukkan seluruh matriks kepada
dosen. Untuk benchmark besar, GUI tetap menghitung hasil tetapi tidak merender
tabel matriks agar tampilan tetap responsif. Mode MPI dua komputer tetap
dijalankan dari konsol melalui `mpi_benchmark.py` karena membutuhkan pemilihan
host dan kredensial MS-MPI.

Opsi yang tersedia:

- `--size`: ukuran matriks persegi (default: `100`)
- `--seed`: seed pembangkit data agar hasil dapat diulang (default: `42`)
- `--mode`: `sequential`, `parallel`, atau `both` (default: `sequential`)
- `--workers`: jumlah proses untuk mode parallel
- `--save-csv`: lokasi file CSV untuk menyimpan hasil percobaan
- `--show-result`: menampilkan matriks hasil untuk ukuran kecil
- `--display-limit`: batas ukuran matriks yang boleh ditampilkan (default: `10`)
- `--progress`: menampilkan progress bar pada sequential dan parallel

Tampilkan bantuan singkat dari program kapan saja dengan:

```powershell
py -3 main.py --help
```

## Menyimpan hasil benchmark

Tambahkan `--save-csv` pada perintah benchmark untuk menyimpan satu hasil
percobaan. Jika file belum ada, program membuatnya beserta header. Jika sudah
ada, hasil baru ditambahkan sebagai baris berikutnya.

```powershell
py -3 main.py --size 500 --seed 7 --mode both --workers 4 --save-csv results\benchmark_results.csv
```

File CSV tersebut dapat dibuka langsung dengan Excel. Kolom yang dicatat:

- waktu percobaan, ukuran matriks, seed, mode, dan jumlah worker;
- waktu sequential dan parallel;
- speedup, checksum, serta status kesamaan hasil.

Untuk data laporan yang dapat dibandingkan, pertahankan `--size`, `--seed`,
dan `--workers` yang sama pada percobaan berulang. Jalankan mode `both` agar
kolom waktu dan speedup terisi lengkap.

## Distributed computing dengan MPI

Mode MPI dijalankan melalui file terpisah, `mpi_benchmark.py`. Rank 0 menjadi
master: ia membuat matriks, membagikan baris matriks kiri kepada setiap proses,
kemudian menggabungkan hasil dari seluruh worker. Pengukuran waktu mencakup
distribusi data, perhitungan lokal, dan penggabungan hasil.

### Setup awal di Windows

Lakukan setup yang sama pada setiap komputer yang akan dipakai:

1. Pasang satu runtime MPI untuk Windows. Proyek ini ditujukan untuk Microsoft
   MPI (MS-MPI); setelah instalasi, `mpiexec` harus dapat dijalankan dari
   PowerShell.
2. Pasang binding Python MPI:

   ```powershell
   py -3 -m pip install mpi4py
   ```

3. Verifikasi MPI secara lokal dahulu:

   ```powershell
   mpiexec -n 2 py -3 -m mpi4py.bench helloworld
   ```

Dokumentasi `mpi4py` menyatakan bahwa wheel Windows memerlukan runtime Intel
MPI atau Microsoft MPI. Lihat [panduan instalasi mpi4py](https://mpi4py.readthedocs.io/en/stable/install.html)
dan [referensi mpiexec Microsoft](https://learn.microsoft.com/en-us/powershell/high-performance-computing/mpiexec?view=hpc19-ps).

### Menjalankan benchmark MPI pada satu komputer

Setelah setup berhasil, jalankan dua proses:

```powershell
mpiexec -n 2 py -3 mpi_benchmark.py --size 250 --seed 7
```

Checksum hasil MPI harus sama dengan checksum pada benchmark sequential untuk
`--size` dan `--seed` yang sama. Setelah uji lokal ini berhasil, tahap berikutnya
adalah mengonfigurasi dua komputer di jaringan yang sama sebagai master dan worker.
Ikuti panduan rinci di [docs/distributed-two-computers.md](docs/distributed-two-computers.md).

Program membuat dua matriks acak berukuran `N x N`, menghitung hasil `A x B`,
lalu menampilkan waktu komputasi serta checksum hasil. Pada mode `both`,
program memastikan hasil parallel sama dengan sequential dan menampilkan
speedup. Checksum juga berguna saat kelak membandingkan dengan MPI/distributed.

### Membaca hasil

Contoh bentuk keluaran mode `both`:

```text
============================================================
 MATRIX COMPUTATION BENCHMARK
============================================================
Konfigurasi
  Ukuran matriks : 250 x 250
  Seed           : 7
  Mode           : both

Hasil sequential
  Waktu    : 0.xxxxxx detik
  Checksum : nilai-yang-sama

Hasil parallel
  Proses   : 4
  Waktu    : 0.xxxxxx detik
  Checksum : nilai-yang-sama
  Validasi : hasil sama
  Speedup  : x.xx
```

- **Waktu sequential**: waktu satu proses menyelesaikan perkalian.
- **Waktu parallel**: waktu saat pekerjaan dibagi ke sejumlah `worker`.
- **Checksum**: harus sama pada kedua metode. Ini menunjukkan hasil
  perhitungannya konsisten.
- **Speedup**: `waktu sequential / waktu parallel`. Nilai di atas `1.00x`
  berarti parallel lebih cepat; nilai di bawah `1.00x` berarti overhead proses
  masih lebih besar daripada keuntungan parallelisme.

Untuk ukuran kecil, parallel sering lebih lambat karena biaya membuat proses
dan mengirim data. Karena itu, uji beberapa ukuran matriks sebelum menarik
kesimpulan.

## Menjalankan tes otomatis

Tes otomatis memeriksa rumus perkalian, validasi input, dan kesamaan hasil
parallel dengan sequential. Jalankan dari folder proyek:

```powershell
$env:PYTHONPATH = "src"
py -3 -m unittest discover -s tests -v
```

Hasil yang diharapkan di bagian akhir adalah:

```text
Ran ... tests in ...
OK
```

## Catatan untuk pencatatan benchmark

Saat mulai membuat laporan, catat minimal: ukuran matriks, seed, jumlah worker,
waktu sequential, waktu parallel, dan speedup. Jalankan setiap konfigurasi
lebih dari sekali karena waktu dapat berubah akibat aktivitas komputer lain.

## Struktur

```text
main.py               entry point praktis
main_gui.py           entry point desktop GUI
mpi_benchmark.py      entry point benchmark MPI
src/matrix_benchmark/ kode aplikasi
tests/                pengujian dasar
README.md             cara memakai proyek
pyproject.toml        metadata dan instalasi opsional
```
