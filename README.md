# Suis M5

Repository ini sekarang memakai naming baru yang lebih stabil:

- `SuisM5_v1`: stable profile.
- `SuisM5_v2`: aggressive frequency profile.
- `AcaneM1_v1_guarded`: Acane M1 aggressive guarded profile terbaru. Ini menggantikan nama lama `AcaneM1_v1_profit30`.

Internal source sekarang memakai prefix generik `SUIS_`, supaya versi berikutnya tetap mudah dibaca tanpa nama historis yang membingungkan.

## Live Files

- [SuisM5_v1.mq5](</Users/naufalrachmandani/Hobby/MT5 XAU 15m/mt5/SuisM5_v1.mq5>)
- [SuisM5_v2.mq5](</Users/naufalrachmandani/Hobby/MT5 XAU 15m/mt5/SuisM5_v2.mq5>)
- [AcaneM1_v1_guarded.mq5](</Users/naufalrachmandani/Hobby/MT5 XAU 15m/mt5/AcaneM1_v1_guarded.mq5>)
- [SuisM5_v1.ex5](</Users/naufalrachmandani/Hobby/MT5 XAU 15m/build/suis_live_package/MQL5/Experts/Suis/SuisM5_v1.ex5>)
- [SuisM5_v2.ex5](</Users/naufalrachmandani/Hobby/MT5 XAU 15m/build/suis_live_package/MQL5/Experts/Suis/SuisM5_v2.ex5>)
- [AcaneM1_v1_guarded.ex5](</Users/naufalrachmandani/Hobby/MT5 XAU 15m/build/acane_guarded_live_package/MQL5/Experts/Acane/AcaneM1_v1_guarded.ex5>)
- [suis_live_package.zip](</Users/naufalrachmandani/Hobby/MT5 XAU 15m/build/suis_live_package.zip>)
- [acane_guarded_live_package.zip](</Users/naufalrachmandani/Hobby/MT5 XAU 15m/build/acane_guarded_live_package.zip>)

Copy file `.ex5` ke folder sesuai package di VPS. Tidak perlu preset `.set`.

## Sanity Backtest Setelah Rename

Setup: `XAUUSDc`, `M5`, `Deposit 100 USD`, `Leverage 1:100`, mode `Every tick`, window `2026.01.01-2026.05.07`.

| EA | Net Profit | Trades | PF | EqDD |
| --- | ---: | ---: | ---: | ---: |
| `SuisM5_v1` | +5900.48% | 95 | 5.71 | 11.85% |
| `SuisM5_v2` | +22259.69% | 125 | 4.26 | 19.94% |

## Pilihan Live

- Gunakan `SuisM5_v2` jika prioritasnya aggressive TF5m, frequency lebih tinggi, dan profit tinggi.
- Gunakan `SuisM5_v1` jika ingin profile yang lebih konservatif/stabil.

`SuisM5_v2` sudah memakai base risk `30%`, daily max loss guard `30%`, profit harian tidak dibatasi, dan buy/sell frequency lebih tinggi dibanding v1.

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
- Max posisi turun dari `42` ke `12`; max same-side turun dari `28` ke `6`.
- Tambah open-risk cap total `12%` dan same-side `8%`.
- Tambah basket floating-loss stop `9%`; jika aktif, EA close posisi dan stop trading hari itu.
- Tambah cooldown `15` menit setelah `3` fast-loss beruntun.
- MRV diblok jika impulse ATR atau jarak EMA terlalu ekstrem, supaya tidak terus melawan candle yang sedang impulsif.

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

- [AcaneM1_v1_guarded.mq5](</Users/naufalrachmandani/Hobby/MT5 XAU 15m/mt5/AcaneM1_v1_guarded.mq5>)
- [AcaneM1_v1_guarded.ex5](</Users/naufalrachmandani/Hobby/MT5 XAU 15m/build/acane_guarded_live_package/MQL5/Experts/Acane/AcaneM1_v1_guarded.ex5>)
- [acane_guarded_live_package.zip](</Users/naufalrachmandani/Hobby/MT5 XAU 15m/build/acane_guarded_live_package.zip>)

Catatan risiko: build ini tetap agresif. Backtest sangat tinggi karena compounding dan leverage tinggi; itu bukan garansi live. Guard `15%` juga bukan garansi absolut jika ada slippage, gap, koneksi putus, atau close gagal.
