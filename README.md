# Suis M5

Repository ini sekarang memakai naming baru yang lebih stabil:

- `SuisM5_v1`: satu-satunya Suis M5 aktif. File ini sudah ditiban dengan profil aggressive/frequency yang sebelumnya disebut `SuisM5_v2`.
- `AcaneM1_v1_guarded`: Acane M1 aggressive guarded profile terbaru. Ini menggantikan nama lama `AcaneM1_v1_profit30`.

Internal source sekarang memakai prefix generik `SUIS_`, supaya versi berikutnya tetap mudah dibaca tanpa nama historis yang membingungkan.

## Live Files

- [SuisM5_v1.mq5](</Users/naufalrachmandani/Hobby/MT5 XAU Bot/mt5/SuisM5_v1.mq5>)
- [AcaneM1_v1_guarded.mq5](</Users/naufalrachmandani/Hobby/MT5 XAU Bot/mt5/AcaneM1_v1_guarded.mq5>)
- [SuisM5_v1.ex5](</Users/naufalrachmandani/Hobby/MT5 XAU Bot/build/suis_live_package/MQL5/Experts/Suis/SuisM5_v1.ex5>)
- [AcaneM1_v1_guarded.ex5](</Users/naufalrachmandani/Hobby/MT5 XAU Bot/build/acane_guarded_live_package/MQL5/Experts/Acane/AcaneM1_v1_guarded.ex5>)
- [suis_live_package.zip](</Users/naufalrachmandani/Hobby/MT5 XAU Bot/build/suis_live_package.zip>)
- [acane_guarded_live_package.zip](</Users/naufalrachmandani/Hobby/MT5 XAU Bot/build/acane_guarded_live_package.zip>)

Copy file `.ex5` ke folder sesuai package di VPS. Tidak perlu preset `.set`.

## Suis M5 Snapshot

Suis sekarang hanya punya satu file aktif: `SuisM5_v1`. Secara isi, ini adalah profil aggressive/frequency yang sebelumnya disebut `SuisM5_v2`.

Setup terbaru yang lebih relevan untuk akun standar: `XAUUSDm`, `M5`, `Deposit 150 USD`, `Leverage 1:2000`, mode `Every tick`.

| EA | Net Profit | Trades | PF | EqDD |
| --- | ---: | ---: | ---: | ---: |
| `SuisM5_v1` 2026.01.01-2026.05.08 | +353.57% | 1132 | 1.09 | 58.21% |
| `SuisM5_v1` 2025.01.01-2026.05.08 | +567.49% | 4422 | 1.07 | 43.01% |

## Pilihan Live

- `AcaneM1_v1_guarded` lebih cocok jika latency VPS ke broker rendah, idealnya jauh di bawah `50 ms`.
- `SuisM5_v1` lebih tahan latency dibanding Acane M1 karena bekerja di `M5`, tetapi hasil `XAUUSDm` saat ini masih punya DD tinggi sehingga belum menjadi kandidat live utama tanpa retune.
- Untuk VPS dengan ping sekitar `180 ms`, jangan jalankan Acane M1 aggressive kecuali setelah pindah ke VPS latency rendah.

## Historical Acane M1 v1

Bagian ini hanya arsip eksperimen awal, bukan file live yang direkomendasikan sekarang. Engine final memakai Bollinger/RSI mean-reversion di candle M1 berjalan, dengan momentum/reclaim/compression dimatikan karena iterasi awal menunjukkan PF negatif.

Setup: `XAUUSDc`, `M1`, deposit `100 USD`, leverage `1:100`, mode `Every tick`.

| Window | Net Profit | Trades | Trades/day | PF | EqDD |
| --- | ---: | ---: | ---: | ---: | ---: |
| `2026.04.01-2026.05.07` | +92.70% | 217 | 6.0 | 1.43 | 15.21% |
| `2026.01.01-2026.05.07` | +3857.78% | 745 | 5.9 | 1.81 | 15.00% |
| `2025.01.01-2026.05.07` | +54.82% | 203 | 0.4 | 1.35 | 15.03% |
| `2023.01.01-2026.05.07` | +26.45% | 229 | 0.2 | 1.16 | 15.05% |

Catatan risiko: Acane final memakai RR `0.72R`, structural D1 price gate `>= 2500`, daily loss guard `15%`, account circuit `15%`, dan retry-close saat guard aktif. Jangan anggap batas 15% sebagai garansi absolut karena slippage, gap, spread, koneksi, atau close failure masih bisa membuat real loss melewati threshold.

## Acane M1 Guarded

`AcaneM1_v1_guarded` adalah file live Acane terbaru. Ini menggantikan nama lama `AcaneM1_v1_profit30`, karena build sekarang bukan guard 30% lagi. Perubahan ini dibuat setelah audit forward test Pro account 2026-05-08, ketika raw profit30 melakukan stacking mean-reversion buy berulang dan baru berhenti setelah account drawdown melewati 30%.

Penyebab loss live yang ditemukan:

- Raw profile terlalu agresif: `risk=30`, `maxPos=42`, `sameSide=28`, dan entry tiap `1` detik.
- Sinyal yang rugi adalah `MRV` mean-reversion, bukan trend continuation. Saat harga lanjut bergerak satu arah, EA membuka posisi searah berulang.
- Guard 30% tidak bisa menjadi batas absolut karena beberapa posisi bisa floating/close bersamaan, sehingga real drawdown bisa overshoot.
- Local MT5 sempat `Algo Trading` off, tetapi log menunjukkan ada session/VPS lain yang tetap mengirim order. Jadi masalahnya bukan chart lokal, tapi live instance yang masih menjalankan build raw.

Perubahan live build terbaru:

- Daily loss guard dan account circuit turun dari `30%` ke `15%`.
- Max posisi turun dari `42` ke `12`; max same-side turun dari `28` ke `4`.
- Tambah open-risk cap total `12%` dan same-side `8%`.
- Tambah basket floating-loss stop `9%`; jika aktif, EA close posisi dan stop trading hari itu.
- Tambah cooldown `15` menit setelah `2` fast-loss beruntun.
- MRV diblok jika impulse ATR atau jarak EMA terlalu ekstrem, supaya tidak terus melawan candle yang sedang impulsif.

Tuning terbaru `v1.04` pada Standard account `XAUUSDm`, deposit `150 USD`, mode `Every tick`:

| Profile | Window | Net Profit | Trades | PF | Win Rate | EqDD |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| old guarded `v1.03` | `2026.01.01-2026.05.08` | +1165254.02% | 1941 | 1.69 | 60.95% | 7.29% |
| old guarded `v1.03` | `2025.01.01-2026.05.08` | +2027.26% | 927 | 1.51 | 59.55% | 15.01% |
| current `v1.04` | `2026.01.01-2026.05.08` | +1184409.69% | 1858 | 1.76 | 61.89% | 7.53% |
| current `v1.04` | `2025.01.01-2026.05.08` | +15410874.16% | 7959 | 1.76 | 57.29% | 3.18% |

Setup test `150 USD`: `XAUUSD`, `M1`, account Pro context, deposit `150 USD`, leverage `1:2000`, mode `Every tick`.

| Window | Net Profit | Trades | Trades/day | PF | EqDD |
| --- | ---: | ---: | ---: | ---: | ---: |
| `2026.05.07-2026.05.08` | +16.41% | 27 | 27.0 | 2.60 | 4.71% |
| `2026.01.01-2026.05.08` | +3599296.33% | 3653 | 28.5 | 1.55 | 6.38% |

Setup test `300 USD`: `XAUUSD`, `M1`, account Pro context, deposit `300 USD`, leverage `1:2000`, mode `Every tick`.

| Window | Net Profit | Trades | Trades/day | PF | EqDD |
| --- | ---: | ---: | ---: | ---: | ---: |
| `2026.05.07-2026.05.08` | +11.60% | 17 | 17.0 | 3.06 | 3.02% |
| `2026.01.01-2026.05.08` | +2148908.70% | 4201 | 32.8 | 1.49 | 8.83% |
| `2025.01.01-2026.05.08` | +12936930.45% | 11797 | 23.8 | 1.83 | 1.61% |
| `2023.01.01-2026.05.08` | +15893310.40% | 15165 | 12.4 | 1.86 | 1.30% |

Live file:

- [AcaneM1_v1_guarded.mq5](</Users/naufalrachmandani/Hobby/MT5 XAU Bot/mt5/AcaneM1_v1_guarded.mq5>)
- [AcaneM1_v1_guarded.ex5](</Users/naufalrachmandani/Hobby/MT5 XAU Bot/build/acane_guarded_live_package/MQL5/Experts/Acane/AcaneM1_v1_guarded.ex5>)
- [acane_guarded_live_package.zip](</Users/naufalrachmandani/Hobby/MT5 XAU Bot/build/acane_guarded_live_package.zip>)

Catatan risiko: build ini tetap agresif. Backtest sangat tinggi karena compounding dan leverage tinggi; itu bukan garansi live. Guard `15%` juga bukan garansi absolut jika ada slippage, gap, koneksi putus, atau close gagal.
