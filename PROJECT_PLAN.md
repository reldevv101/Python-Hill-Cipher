# PROJECT PLAN — Hill Cipher Benchmark

## Latar belakang

Proyek ini dikembangkan bertahap dari **Python Matrix Computation** menjadi aplikasi **Hill Cipher Benchmark**. Kode yang ada menjadi fondasi yang ditinjau dan dimanfaatkan secara selektif. Aplikasi akan mengenkripsi dan mendekripsi pesan dengan Hill Cipher, lalu membandingkan komputasi sequential, parallel pada satu komputer, dan distributed menggunakan MPI.

## Tujuan

- Membuat implementasi Hill Cipher sederhana yang benar dan dapat diuji ulang.
- Menggunakan sequential sebagai baseline, lalu membandingkannya dengan `multiprocessing` dan MPI.
- Mengukur waktu dengan kondisi yang setara serta melaporkan speedup, efisiensi, throughput, dan kebenaran hasil.
- Menyediakan hasil yang mudah ditinjau dan diekspor untuk demonstrasi serta laporan.
- Menetapkan novelty hanya setelah perbandingan jurnal dan arahan dosen; jangan membuat klaim keamanan yang tidak didukung.

## Ruang lingkup

### Fondasi kriptografi

- Implementasi awal memakai alfabet A–Z, pemetaan A=0 sampai Z=25, modulo 26, dan matriks kunci 2×2.
- Tentukan dan dokumentasikan satu kebijakan normalisasi plaintext (misalnya huruf besar saja, spasi/tanda baca dihapus) serta padding untuk pesan ganjil. Enkripsi dan dekripsi harus menerapkan kebijakan yang konsisten.
- Validasi ukuran dan isi kunci, serta pastikan matriks memiliki invers modulo 26. Untuk matriks 2×2, syaratnya `gcd(det(K), 26) = 1`.
- Dekripsi harus menghitung invers modular dengan benar. Uji bahwa hasil dekripsi sama dengan plaintext setelah normalisasi dan pelepasan padding yang memang ditambahkan.
- Perhitungan kriptografi menggunakan bilangan bulat dan aritmetika modular; fungsi perkalian matriks pecahan yang sudah ada tidak boleh dianggap sebagai implementasi Hill Cipher.

### Metode komputasi dan hasil

- Sequential menjadi baseline yang paling sederhana.
- Parallel membagi blok pesan yang independen ke worker `multiprocessing`.
- Distributed membagi blok Hill Cipher ke rank MPI, lalu menyusun kembali hasil dalam urutan aslinya.
- Semua metode memakai plaintext, kunci, ukuran blok, dan konfigurasi yang sama. Hasil ciphertext harus identik.
- Ukur enkripsi dan dekripsi secara terpisah. Catat panjang pesan, konfigurasi proses, waktu, validasi, speedup, efisiensi, dan throughput. Nyatakan dengan jelas apakah waktu mencakup overhead pembagian, komunikasi, dan penggabungan.
- Simpan hasil benchmark dalam CSV; pertahankan ekspor matriks A/B/A×B lama jika masih dibutuhkan untuk demonstrasi, tetapi jangan memaksakan bentuk ekspor itu ke data cipher.
- Antarmuka CLI lebih dahulu. GUI dapat diperbarui setelah alur inti dan benchmark stabil. Tidak termasuk login, database, atau GUI kompleks pada tahap awal.

## Audit awal repo: komponen yang ditemukan

Kode matrix computation lama dikelompokkan di `legacy/matrix_computation/`:
paket `src/matrix_benchmark/`, entry point matrix, tes, serta panduan lama.
Paket aktif Hill Cipher berada di `src/hill_cipher_benchmark/`, dengan tes
khusus di `tests/` dan entry point MPI `hill_cipher_mpi.py`. Berkas lama di
`results/` dipertahankan pada lokasi semula. Catatan audit awal di bagian ini
telah diselaraskan dengan susunan repository terbaru.

- **Berpotensi dipakai ulang setelah peninjauan:** pola timer, pelaporan CSV yang dapat dikonfigurasi, format presentasi, pola pembagian tugas/hasil dan pengaturan worker, serta kerangka CLI/GUI.
- **Perlu diadaptasi:** pembagian baris menjadi pembagian blok pesan; skema CSV; antarmuka; dokumentasi; dan integrasi MPI agar menerima input pesan/kunci secara konsisten.
- **Komponen baru:** normalisasi/pemetaan alfabet, validasi kunci, invers matriks modulo, enkripsi/dekripsi serial, pembagian blok Hill Cipher, orkestrasi parallel/distributed cipher, dan benchmark cipher.
- **Jangan digunakan sebagai pengganti:** operasi float pada perkalian matriks sekarang bukan aritmetika modular integer yang diperlukan Hill Cipher.

Audit ini hanya inventaris awal, bukan keputusan desain final. Periksa isi lengkap dan pemanggil setiap modul sebelum melakukan perubahan.

## Arsitektur sasaran (rancangan awal)

Pertahankan paket aktif di `src/hill_cipher_benchmark/` dan pisahkan domain
cipher dari kode matrix lama yang disimpan di `legacy/matrix_computation/`.
Modul aktif meliputi:

- `alphabet.py`: alfabet dan normalisasi/padding.
- `key.py`: validasi matriks dan invers modular.
- `core.py`: transformasi blok sequential, enkripsi, dan dekripsi.
- `parallel.py`: pembagian blok pesan dan penggabungan hasil `multiprocessing`.
- `distributed.py`: orkestrasi MPI atas blok pesan.
- `mpi_cli.py`: entry point konsol untuk operasi MPI.
- `benchmark.py` dan `reporting.py`: modul yang direncanakan untuk pengukuran dan keluaran CSV.
- Entry point CLI terlebih dahulu; GUI dan ekspor hasil diperbarui pada fase tersendiri.

Kode matrix computation dipindahkan tanpa mengubah isi file ke folder arsip.
Entry point dan tes lamanya tetap tersedia di sana selama dibutuhkan. File hasil
di `results/` tidak dipindah atau ditulis ulang.

## Fase pengerjaan

### Fase 0 — Audit dan baseline

- Petakan seluruh file, API publik, alur CLI/GUI, hasil yang telah tersimpan, dan tes.
- Jalankan pemeriksaan yang sesuai dan catat baseline; jangan mengubah kode aplikasi.
- Identifikasi risiko kompatibilitas, dependensi MPI, serta data lama yang harus dipertahankan.

### Fase 1 — Hill Cipher sequential

- Tetapkan spesifikasi alfabet, normalisasi, padding, format kunci, dan perilaku pesan kosong.
- Implementasikan operasi modular integer, validasi kunci, enkripsi, dan dekripsi sequential.
- Tambahkan tes unit untuk vektor contoh yang diketahui, batas/pesan ganjil, karakter yang dinormalisasi, kunci valid/tidak valid, serta round-trip.

### Fase 2 — Parallel lokal

- Bagi pekerjaan pada batas blok agar setiap blok dapat dihitung mandiri.
- Jaga urutan keluaran dan hindari overhead yang tidak perlu.
- Bandingkan ciphertext dan plaintext hasil parallel dengan sequential untuk berbagai jumlah worker dan ukuran pesan.
- Ukur overhead proses dan jangan mengklaim parallel lebih cepat untuk semua ukuran.

### Fase 3 — Distributed MPI

- Distribusikan konfigurasi dan blok secara konsisten, hitung bagian lokal, lalu kumpulkan hasil berurutan.
- Tangani jumlah rank yang lebih besar daripada jumlah blok dan kegagalan/dependensi MPI dengan jelas.
- Verifikasi hasil MPI identik dengan sequential; dokumentasikan eksperimen lokal dan, jika tersedia, multi-komputer.

### Fase 4 — Benchmark, pelaporan, dan antarmuka

- Jalankan enkripsi dan dekripsi sebagai pengukuran terpisah; gunakan input/configuration identik dan beberapa pengulangan.
- Simpan data mentah yang cukup untuk menghitung ringkasan dan grafik kemudian. Pisahkan waktu komputasi inti dari waktu end-to-end jika memungkinkan.
- Perbarui CLI, CSV, README, dan panduan. Setelah stabil, putuskan adaptasi GUI dan ekspor yang berguna.

### Fase 5 — Perbandingan jurnal dan seleksi novelty

- Buat tabel literatur: algoritma/varian, alfabet/modulo, ukuran dan pembentukan kunci, model komputasi, dataset, metrik, serta keterbatasan.
- Cocokkan opsi pengembangan dengan celah yang terverifikasi dan arahan dosen.
- Pilih paling banyak satu atau dua opsi realistis, tulis pertanyaan eksperimen dan kriteria sukses sebelum implementasi.
- Ubah scope/arsitektur hanya setelah keputusan novelty terdokumentasi.

### Fase 6 — Evaluasi dan laporan

- Ulangi eksperimen dengan seed/input dan lingkungan yang dicatat; rangkum variasi, bukan hanya satu angka tercepat.
- Sajikan tabel/grafik waktu, speedup, efisiensi, throughput, serta validasi hasil.
- Batasi kesimpulan pada bukti performa dan sifat implementasi yang benar-benar diuji.

## Rencana eksperimen

- **Kebenaran fungsional:** vektor plaintext/kunci/ciphertext yang terdokumentasi; round-trip setelah normalisasi; kesetaraan sequential, multiprocessing, dan MPI.
- **Variasi beban:** beberapa panjang pesan, termasuk pesan kecil dan besar, panjang ganjil, serta kasus pendek/kosong sesuai kebijakan spesifikasi.
- **Variasi komputasi:** sequential, beberapa jumlah worker lokal, dan beberapa jumlah rank MPI bila tersedia.
- **Variabel terkendali:** pesan, kunci, ukuran blok, aturan preprocessing, versi Python/dependensi, perangkat keras, dan konfigurasi yang sama di antara metode.
- **Metrik:** waktu enkripsi dan dekripsi secara terpisah; waktu inti dan end-to-end bila dapat dipisahkan; speedup terhadap sequential; efisiensi `speedup / jumlah worker` (jelaskan definisi worker untuk MPI); throughput dalam simbol atau byte per detik; dan status kesamaan hasil.
- **Pengulangan:** lakukan beberapa run per konfigurasi, laporkan nilai representatif dan variasi. Pemanasan, urutan metode, dan overhead startup perlu dicatat agar interpretasi adil.
- **Eksperimen modulo/alfabet:** hanya setelah spesifikasi pemetaan simbol dan operasi modular yang benar disepakati; perlakukan sebagai kandidat penelitian, bukan asumsi peningkatan keamanan.

## Kandidat novelty — ditunda sampai perbandingan jurnal

Opsi untuk ditelaah, bukan komitmen fitur:

1. Membandingkan alfabet/modulo yang didefinisikan secara eksplisit (contoh alfabet diperluas atau representasi byte) dengan evaluasi kebenaran dan performa. Modulo lebih besar tidak otomatis meningkatkan keamanan.
2. Variasi ukuran matriks kunci, jika literatur dan batas waktu mendukung analisis yang bermakna.
3. Skema kunci dinamis per blok/pesan, hanya jika aturan pembangkitan, sinkronisasi dekripsi, distribusi kunci, dan analisis keamanan dapat dijelaskan dengan bertanggung jawab.
4. Evaluasi strategi pembagian kerja atau ambang ukuran pesan pada sequential, parallel, dan MPI.

Tidak menyebut Hill Cipher atau varian sederhana ini sebagai kriptografi modern yang aman. Novelty harus dibandingkan dengan sumber jurnal yang dapat diverifikasi dan klaimnya proporsional.

## Rencana pengujian

- Unit test pemetaan alfabet, preprocessing/padding, operasi modular, determinan, invers matriks, enkripsi/dekripsi, dan kasus input invalid.
- Tes integrasi kesetaraan sequential dan parallel serta urutan blok; tes MPI dapat dilewati secara eksplisit bila runtime tidak tersedia, tetapi harus dijalankan pada lingkungan MPI sebelum klaim keberhasilan distribusi.
- Tes benchmark memastikan kolom konfigurasi/metrik tercatat, kesalahan metode tidak disamarkan, dan pengukuran tidak mencampur data dari konfigurasi berbeda.
- Pertahankan tes lama selama tahap transisi. Hapus atau ganti hanya setelah penggunaannya dipetakan, perilaku yang relevan tercakup tes baru, dan keputusan migrasi didokumentasikan.
- Jalankan seluruh tes yang relevan setelah setiap fase; jangan menambahkan perubahan aplikasi di luar fase yang sedang disetujui.

## Aturan pelestarian dan implementasi bertahap

1. Sebelum mengedit, tinjau status Git dan baca file yang terkait; jangan mengasumsikan repo bersih atau menimpa pekerjaan pengguna.
2. Jangan menghapus, mengganti nama, atau menulis ulang massal kode, dokumentasi, tes, maupun berkas `results/` yang ada tanpa kebutuhan yang jelas dan perubahan bertahap.
3. Tambahkan logika Hill Cipher dalam modul yang terpisah pada tahap awal; pertahankan API lama sampai strategi migrasi dinilai dan tes membuktikan transisi aman.
4. Kerjakan satu fase pada satu waktu dalam perubahan kecil yang dapat ditinjau. Sebelum tiap fase, jelaskan file yang akan diubah dan kriteria selesai; setelahnya, laporkan perubahan dan validasi.
5. Jangan mulai implementasi aplikasi sebagai bagian dari audit awal atau hanya karena rencana ini dibuat. Mulai implementasi setelah audit dan rencana fase ditinjau/diarahkan pengguna.
6. Jangan menyimpulkan keamanan dari ukuran modulo, kecepatan, atau kerumitan kunci saja. Klaim novelty menunggu kajian jurnal.
7. Jangan mengubah file hasil yang dihasilkan pengguna; tulis eksperimen baru ke nama/path keluaran baru yang disepakati.

## Kriteria selesai

- [ ] Hill Cipher A–Z modulo 26 dengan kunci 2×2 tervalidasi, enkripsi/dekripsi round-trip, dan perilaku normalisasi/padding terdokumentasi.
- [ ] Sequential, multiprocessing, dan MPI menghasilkan ciphertext identik dan memulihkan plaintext yang sama.
- [ ] Benchmark enkripsi/dekripsi dapat diulang; konfigurasi, waktu, validasi, speedup, efisiensi, dan throughput dilaporkan dengan definisi yang jelas.
- [ ] Pengujian otomatis mencakup fungsi inti, input invalid, kesetaraan metode, dan pencatatan hasil; uji MPI dilakukan pada lingkungan yang mendukungnya.
- [ ] README dan panduan menjelaskan setup, penggunaan, batas pengukuran, serta interpretasi hasil.
- [ ] Novelty (bila dipilih) didukung perbandingan jurnal, batasan, dan eksperimen yang terukur; jika belum didukung, tetap ditunda.
- [ ] Komponen lama yang dipertahankan atau dipensiunkan tercatat dan seluruh perubahan tetap bertahap serta dapat ditinjau.
