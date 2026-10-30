# Menjalankan MPI pada Dua Komputer Windows

Panduan ini menggunakan satu komputer sebagai **master** yang menjalankan
perintah `mpiexec`, dan satu komputer sebagai **worker**. Aplikasi matrix
benchmark yang sama akan dijalankan sebagai proses MPI pada keduanya.

## 1. Siapkan kedua komputer

Di master dan worker, lakukan hal yang sama:

1. Hubungkan keduanya ke jaringan lokal yang sama.
2. Pasang versi Python, Microsoft MPI (MS-MPI), dan `mpi4py` yang sama.
3. Letakkan salinan project pada path yang sama, misalnya:

   ```text
   C:\MPI\Python Matrix Computation
   ```

4. Buka PowerShell dan verifikasi:

   ```powershell
   mpiexec -n 2 py -3 -m mpi4py.bench helloworld
   ```

Perintah verifikasi tersebut dilakukan lokal pada masing-masing komputer.

## 2. Tentukan master dan worker

Pilih satu komputer untuk menjalankan perintah `mpiexec`. Komputer inilah yang
disebut **master**. Master membuat matriks awal, membagi pekerjaan, dan
menampilkan hasil akhir. Komputer kedua disebut **worker**; ia hanya
mengerjakan baris matriks yang diterimanya dari master.

Untuk praktik proyek ini, gunakan komputer yang sekarang Anda pakai sebagai
master. Dari pengujian sebelumnya, namanya adalah:

```text
DESKTOP-KMSGI0H
```

Jadi pengaturannya adalah:

| Peran | Komputer | Tugas |
| --- | --- | --- |
| Master | `DESKTOP-KMSGI0H` | Menjalankan `mpiexec` dan menampilkan hasil |
| Worker | Komputer kedua | Menerima dan menghitung bagian matriks |

## 3. Catat nama worker

Di komputer kedua saja, buka PowerShell lalu jalankan:

```powershell
hostname
```

Misalnya keluarannya adalah `LAB-PC-02`. Maka `LAB-PC-02` adalah nama worker.
Dari master, pastikan worker dapat ditemukan di jaringan:

```powershell
ping LAB-PC-02
```

## 4. Uji dua komputer

Di **master** (`DESKTOP-KMSGI0H`), buka PowerShell pada folder project. Jika
nama worker adalah `LAB-PC-02`, jalankan:

```powershell
mpiexec /hosts 2 DESKTOP-KMSGI0H 1 LAB-PC-02 1 /wdir "C:\MPI\Python Matrix Computation" py -3 -m mpi4py.bench helloworld
```

Jika berhasil, keluaran akan menyebut dua proses dengan nama komputer yang
berbeda. Baru kemudian jalankan benchmark:

```powershell
mpiexec /hosts 2 DESKTOP-KMSGI0H 1 LAB-PC-02 1 /wdir "C:\MPI\Python Matrix Computation" py -3 mpi_benchmark.py --size 250 --seed 7
```

Baris `Komputer proses` pada hasil benchmark harus memuat nama master dan
worker. Checksum juga harus sama dengan benchmark sequential untuk `size` dan
`seed` yang sama.

## Jika proses worker tidak dapat dimulai

Jangan mengubah kode terlebih dahulu. Periksa bahwa:

- nama worker dapat diping dari master;
- MS-MPI dan `mpi4py` sudah dipasang pada kedua komputer;
- path project yang dipakai pada `/wdir` benar dan tersedia di worker;
- Windows meminta atau memblokir izin jaringan/firewall untuk MS-MPI.

MS-MPI mendukung daftar host melalui `/hosts`, dan opsi `/wdir` menentukan
folder kerja proses yang dijalankan. Lihat dokumentasi
[mpiexec Microsoft](https://learn.microsoft.com/en-us/powershell/high-performance-computing/mpiexec?view=hpc19-ps)
untuk parameter tambahan.
