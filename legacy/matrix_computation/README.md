# Legacy Matrix Computation Benchmark

Folder ini menyimpan aplikasi Matrix Computation Benchmark sebelum repository
difokuskan pada Hill Cipher. Kode, tes, dan panduan dipindahkan ke sini tanpa
mengubah isi programnya. Berkas lama di folder `results/` repository utama
dipertahankan pada lokasi semula.

## Menjalankan

Dari PowerShell, masuk ke folder ini:

```powershell
cd "C:\Users\USER\Documents\Codex\Python-Hill-Cipher\legacy\matrix_computation"
```

Jalankan benchmark sequential atau parallel:

```powershell
py -3 main.py --size 100 --mode sequential
py -3 main.py --size 250 --mode both --workers 4
```

Untuk GUI matrix lama:

```powershell
py -3 main_gui.py
```

Tes lama dapat dijalankan dari folder ini:

```powershell
$env:PYTHONPATH = "src"
py -3 -m unittest discover -s tests -v
```

Petunjuk konsep dan MPI lama ada di folder `docs/`. Entry point tersebut
disimpan untuk menjaga hasil kerja terdahulu dan tidak digunakan oleh aplikasi
Hill Cipher aktif.
