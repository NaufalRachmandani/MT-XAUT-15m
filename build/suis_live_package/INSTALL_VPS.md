# Suis M5 VPS Install

Package ini berisi dua EA aktif:

- `SuisM5_v1.ex5`: stable profile.
- `SuisM5_v2.ex5`: aggressive frequency profile.

Cara pasang:

1. Buka MT5 di VPS.
2. `File > Open Data Folder`.
3. Masuk ke `MQL5/Experts/`.
4. Buat folder `Suis` jika belum ada.
5. Copy `SuisM5_v1.ex5` dan `SuisM5_v2.ex5` ke `MQL5/Experts/Suis/`.
6. Hapus EA lama/iterasi lama jika masih ada supaya Navigator tidak membingungkan.
7. Di Navigator MT5, klik kanan `Expert Advisors`, lalu pilih `Refresh`.
8. Attach EA yang ingin dipakai ke chart `XAUUSDc,M5`.

Rekomendasi:

- Pakai `SuisM5_v2` kalau prioritasnya aggressive TF5m / frequency / profit tinggi.
- Pakai `SuisM5_v1` kalau prioritasnya lebih stabil.

Tidak perlu preset `.set`. Semua setting dikunci di dalam `.ex5`.
