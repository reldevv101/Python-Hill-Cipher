# Konsep dan Algoritma Proyek

Dokumen ini menjelaskan konsep yang digunakan oleh program *Matrix Computation
Benchmark*. Isinya dapat dijadikan dasar untuk bagian metode atau pembahasan
pada laporan tugas.

## Tujuan program

Program membandingkan waktu perkalian dua matriks persegi dengan tiga cara:

1. **Sequential**: seluruh perhitungan berjalan dalam satu proses.
2. **Parallel**: beberapa proses pada satu komputer bekerja bersamaan.
3. **Distributed MPI**: beberapa proses dapat bekerja pada komputer berbeda
   dan saling berkomunikasi melalui jaringan.

Setiap percobaan memakai matriks acak yang sama ketika `size` dan `seed` sama.
Dengan demikian perbedaan waktu berasal dari metode komputasi, bukan perbedaan
data input.

## Perkalian matriks

Jika matriks `A` berukuran `m x n` dan `B` berukuran `n x p`, hasil perkalian
`C = A x B` berukuran `m x p`. Nilai pada baris `i`, kolom `j` dihitung dengan:

```text
C[i][j] = jumlah dari A[i][k] x B[k][j], untuk setiap k dari 0 sampai n - 1
```

Contoh:

```text
A = [1  2]      B = [5  6]      C = A x B = [19  22]
    [3  4]          [7  8]                  [43  50]
```

Nilai `C[0][0]` adalah `(1 x 5) + (2 x 7) = 19`. Untuk matriks persegi
`N x N`, algoritma dasar membutuhkan kira-kira `N³` operasi.

## Metode sequential

Satu proses membaca setiap baris matriks `A`, lalu menghitung hasil terhadap
setiap kolom `B`. Program melakukan transpose `B` terlebih dahulu agar kolom
`B` dapat diakses sebagai baris Python yang berurutan. Sequential digunakan
sebagai baseline untuk menghitung speedup.

## Metode parallel pada satu komputer

Metode parallel memakai `multiprocessing` Python. Baris `A` dibagi menjadi
beberapa kelompok. Setiap worker process menghitung satu kelompok baris,
kemudian proses utama menggabungkan hasil sesuai urutan semula.

```text
Proses utama
  ├─ worker 1: baris A bagian 1
  ├─ worker 2: baris A bagian 2
  └─ worker n: baris A bagian n
                 ↓
          gabungkan menjadi C
```

Setiap baris hasil bersifat independen sehingga pembagian per baris sesuai
untuk parallelisme. Untuk matriks kecil, parallel dapat lebih lambat karena
biaya membuat proses dan mengirim data antarproses.

## Metode distributed MPI

MPI (*Message Passing Interface*) digunakan untuk proses dengan memori
terpisah, termasuk pada dua komputer. Dalam proyek ini:

1. Rank 0/master membuat matriks `A` dan `B`.
2. Master melakukan broadcast kolom `B` ke seluruh proses.
3. Master membagi baris `A` dengan scatter.
4. Setiap rank menghitung bagian barisnya.
5. Master menggabungkan bagian hasil dengan gather.

```text
Master (rank 0) → broadcast B dan scatter A → worker/rank lain
Master (rank 0) ←────── gather hasil C ────── worker/rank lain
```

Waktu MPI mencakup distribusi data, perhitungan lokal, dan penggabungan hasil.
Karena komunikasi jaringan, ukuran kecil dapat lebih lambat daripada sequential.

## Checksum dan hasil matriks

Checksum adalah jumlah seluruh elemen matriks hasil `C`:

```text
checksum = jumlah seluruh C[i][j]
```

Untuk `size` dan `seed` sama, checksum sequential, parallel, dan MPI harus
sama. Ini adalah validasi cepat, tetapi bukan bukti matematis sempurna karena
dua matriks berbeda secara teori dapat mempunyai jumlah yang sama. Saat
demonstrasi, tampilkan juga hasil matriks kecil:

```powershell
py -3 main.py --size 3 --seed 7 --mode both --workers 2 --show-result
```

Ukuran tampilan dibatasi sampai `10 x 10` secara default agar konsol tidak
penuh. Ubah batas dengan `--display-limit` bila diperlukan.

## Progress bar konsol

Opsi `--progress` menunjukkan kemajuan perhitungan. Pada sequential, kemajuan
berdasarkan jumlah baris `A` selesai. Pada parallel, kemajuan bertambah ketika
hasil kelompok baris dari worker diterima.

```powershell
py -3 main.py --size 100 --mode both --workers 4 --progress
```

Progress bar berguna saat demonstrasi. Matikan saat mencatat benchmark resmi
karena output terminal menambah sedikit overhead waktu.

## Antarmuka grafis

GUI dibuat dengan Tkinter, pustaka antarmuka desktop bawaan Python sehingga
tidak memerlukan dependency tambahan. GUI tidak menghitung ulang dengan
algoritma berbeda; ia memanggil fungsi sequential dan parallel yang sama dengan
versi konsol. Perhitungan dijalankan pada background thread agar antarmuka tetap
responsif dan progress bar dapat diperbarui.

Tiga tabel pada GUI memiliki fungsi berikut:

- **Matriks A**: input pertama yang dibangkitkan dari seed.
- **Matriks B**: input kedua yang dibangkitkan dari seed.
- **Hasil A x B**: hasil perkalian yang dipakai untuk checksum dan validasi.

Tabel hanya ditampilkan untuk ukuran sampai `10 x 10`. Batas ini menjaga
tampilan tetap mudah dibaca; benchmark matriks besar tetap dapat dijalankan.
Distribusi MPI dua komputer tetap dipertahankan melalui konsol karena proses
peluncuran membutuhkan nama host dan kredensial jaringan.

## Mengukur performa

Program memakai `perf_counter()` untuk sequential/parallel dan `MPI.Wtime()`
untuk MPI. Speedup dihitung dengan:

```text
speedup = waktu sequential / waktu parallel
```

- `speedup > 1`: parallel lebih cepat.
- `speedup = 1`: performa setara.
- `speedup < 1`: overhead lebih besar daripada manfaat parallelisme.

Untuk laporan yang adil, gunakan seed sama, jalankan setiap konfigurasi
beberapa kali, lalu catat ukuran matriks, worker/proses, waktu, checksum, dan
speedup.
