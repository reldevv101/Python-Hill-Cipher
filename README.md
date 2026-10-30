# Hill Cipher Benchmark

Proyek ini mengembangkan aplikasi pembelajaran dan benchmark Hill Cipher.
Implementasi menggunakan alfabet A–Z dan aritmetika integer modulo 26, lalu
membandingkan pemrosesan sequential, multiprocessing pada satu komputer, dan
MPI. Hill Cipher adalah cipher klasik yang dapat dipelajari dan diukur dalam
proyek ini; cipher ini **bukan metode enkripsi modern yang aman**.

## Status fitur

| Fitur | Status |
| --- | --- |
| Enkripsi/dekripsi sequential | Modul inti tersedia |
| Enkripsi/dekripsi multiprocessing | Modul tersedia |
| Enkripsi/dekripsi MPI | CLI konsol tersedia |
| Perbandingan benchmark dan ekspor CSV khusus Hill Cipher | Belum dibuat |
| GUI Hill Cipher | Belum dibuat |

Kode matrix computation lama disimpan di `legacy/matrix_computation/` dan tidak
menjadi bagian dari aplikasi Hill Cipher. `results/` tetap berisi hasil matriks
lama dan dipertahankan di lokasi semula. Gunakan `hill_cipher_mpi.py` untuk
menjalankan Hill Cipher melalui MPI.

## Aturan Hill Cipher saat ini

- Alfabet hanya `A` sampai `Z`, dengan pemetaan `A=0`, …, `Z=25`.
- Plaintext diubah ke huruf kapital; karakter selain huruf ASCII A–Z dibuang.
- Teks diproses per dua huruf sebagai vektor kolom dan dikalikan dengan kunci
  2×2. Setiap nilai hasil direduksi modulo 26.
- Panjang plaintext ganjil ditambah `X`. Padding hanya dapat dibuang saat
  dekripsi jika panjang plaintext setelah normalisasi diketahui.
- Kunci terdiri dari empat integer 0–25 dan harus invertibel modulo 26, yaitu
  `gcd(determinan, 26) = 1`.

Normalisasi ini menghilangkan kapitalisasi asli, spasi, tanda baca, angka, dan
karakter di luar A–Z. Hasil dekripsi adalah teks yang sudah dinormalisasi.

## Persyaratan

- Python 3.10 atau lebih baru.
- Sequential dan multiprocessing menggunakan pustaka standar Python.
- MPI memerlukan Microsoft MPI (MS-MPI) serta `mpi4py` pada setiap komputer
  yang menjalankan rank.

Untuk menyiapkan binding MPI melalui Python launcher:

```powershell
py -3 -m pip install mpi4py
```

Pastikan `mpiexec` tersedia dan uji instalasi MPI lokal:

```powershell
mpiexec -n 2 py -3 -m mpi4py.bench helloworld
```

## Menjalankan Hill Cipher MPI

Buka PowerShell pada folder proyek:

```powershell
cd "C:\Users\USER\Documents\Codex\Python-Hill-Cipher"
```

Enkripsi contoh dengan empat rank:

```powershell
mpiexec -n 4 py -3 hill_cipher_mpi.py --action encrypt --text "Hello!" --key 3,3,2,5
```

Keluaran ciphertext untuk contoh tersebut adalah `HIOZHN`. `--key 3,3,2,5`
mewakili matriks kunci `[[3, 3], [2, 5]]`. Jika tidak ditulis, kunci contoh
tersebut menjadi nilai default.

Dekripsi dan hilangkan padding menggunakan panjang teks ternormalisasi:

```powershell
mpiexec -n 4 py -3 hill_cipher_mpi.py --action decrypt --text HIOZHN --key 3,3,2,5 --original-length 5
```

Hasilnya `HELLO`. Gunakan `--original-length` hanya saat dekripsi. Nilainya
adalah jumlah huruf A–Z setelah normalisasi, bukan panjang teks sebelum spasi
dan tanda baca dibuang. Tanpa nilai itu, padding `X` dipertahankan karena tidak
selalu dapat dibedakan dari huruf X yang memang ada di akhir pesan.

Untuk menjalankan pada dua komputer, kedua komputer harus memiliki salinan
proyek pada path kerja yang sesuai, versi Python, MS-MPI, dan `mpi4py` yang
tersedia. Format perintah MS-MPI:

```powershell
mpiexec /hosts 2 NAMA_MASTER 1 NAMA_WORKER 1 /wdir "C:\MPI\Python-Hill-Cipher" py -3 hill_cipher_mpi.py --action encrypt --text "Hello!" --key 3,3,2,5
```

Ganti nama komputer dan path sesuai konfigurasi Anda. Pengujian MPI yang telah
dilakukan pada proyek ini menggunakan beberapa rank pada satu komputer;
pengujian Hill Cipher lintas dua komputer masih perlu dilakukan.

Waktu MPI saat ini mencakup broadcast kunci, scatter blok yang telah disiapkan,
perhitungan lokal, dan pengumpulan hasil. Normalisasi teks, validasi kunci,
serta persiapan pembagian blok dilakukan sebelum pengukuran. Karena itu,
bandingkan waktu ini dengan metode lain setelah batas pengukurannya disamakan.

## Pemanggilan modul sequential dan multiprocessing

Modul inti dapat dipanggil langsung dari Python. Contoh berikut membandingkan
ciphertext sequential dan multiprocessing:

```powershell
$env:PYTHONPATH = "src"
py -3 -c "from hill_cipher_benchmark import encrypt; from hill_cipher_benchmark.parallel import parallel_encrypt; key=((3,3),(2,5)); print('Sequential:', encrypt('Hello!', key)); print('Parallel:', parallel_encrypt('Hello!', key, workers=2))"
```

Kedua metode seharusnya menghasilkan `HIOZHN`. Fungsi `decrypt` dan
`parallel_decrypt` juga tersedia di `hill_cipher_benchmark` dan
`hill_cipher_benchmark.parallel`. Antarmuka konsol untuk menjalankan dan
membandingkan ketiga metode dalam satu benchmark akan ditambahkan pada tahap
berikutnya.

## Tes otomatis

Jalankan tes dari folder proyek:

```powershell
$env:PYTHONPATH = "src"
py -3 -m unittest discover -s tests -v
```

Tes MPI memerlukan `mpi4py` dan `mpiexec`. Tes tersebut melewati pemeriksaan
MPI jika dependensi atau runtime tidak tersedia.

## Berkas hasil dan komponen lama

Isi `results/` yang sudah ada adalah keluaran benchmark matriks lama. File itu
tidak berisi hasil Hill Cipher. Pencatatan benchmark Hill Cipher ke CSV dan
ekspor hasil enkripsi/dekripsi belum diterapkan.

Kode lama dikelompokkan terpisah agar fokus repository tetap pada Hill Cipher.
Untuk menjalankan matrix benchmark lama, buka folder arsip dan ikuti README
arsip tersebut. Berkas hasil yang ada tetap berada di `results/`.

```text
hill_cipher_mpi.py                  entry point Hill Cipher MPI
src/hill_cipher_benchmark/          algoritma sequential, parallel, dan MPI
tests/                              tes Hill Cipher
legacy/matrix_computation/          kode, tes, dan dokumentasi matrix lama
results/                            hasil matrix lama, dipertahankan
```
