# Suis M5 VPS Install

Package ini berisi satu EA aktif:

- `SuisM5_v1.ex5`: profil aggressive/frequency yang sebelumnya disebut `SuisM5_v2`.

Cara pasang:

1. Buka MT5 di VPS.
2. `File > Open Data Folder`.
3. Masuk ke `MQL5/Experts/`.
4. Buat folder `Suis` jika belum ada.
5. Copy `SuisM5_v1.ex5` ke `MQL5/Experts/Suis/`.
6. Hapus EA lama/iterasi lama jika masih ada supaya Navigator tidak membingungkan.
7. Di Navigator MT5, klik kanan `Expert Advisors`, lalu pilih `Refresh`.
8. Attach EA ke chart gold `M5`, misalnya `XAUUSDm,M5` untuk akun Standard atau `XAUUSDc,M5` untuk Cent.

Rekomendasi:

- Suis lebih tahan latency dibanding Acane M1, tetapi snapshot `XAUUSDm` terakhir masih punya drawdown tinggi. Jangan anggap ini kandidat utama tanpa retune lanjutan.

Tidak perlu preset `.set`. Semua setting dikunci di dalam `.ex5`.
