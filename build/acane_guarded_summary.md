# Acane M1 Guarded

`AcaneM1_v1_guarded` adalah file live Acane terbaru. Ini menggantikan nama lama `AcaneM1_v1_profit30`, karena build sekarang bukan guard 30% lagi.

## Live Files

- Source: `mt5/AcaneM1_v1_guarded.mq5`
- EX5: `build/acane_guarded_live_package/MQL5/Experts/Acane/AcaneM1_v1_guarded.ex5`
- Package: `build/acane_guarded_live_package.zip`

## Current Guarded Profile

- Timeframe: `M1`
- Engine aktif: Bollinger/RSI mean-reversion pada candle berjalan.
- Risk nominal: `30%` per signal, tetapi dibatasi open-risk cap.
- Daily max loss: `15%`
- Account circuit: `15%`
- Max positions: `12`
- Max same-side positions: `4`
- Total open-risk cap: `12%`
- Same-side open-risk cap: `8%`
- Basket floating-loss stop: `9%`
- Fast-loss cooldown: `2` fast losses -> cooldown `15` menit.
- MRV impulse block: hindari entry mean-reversion saat impulse ATR/EMA distance terlalu ekstrem.

## Audit Live Loss 2026-05-08

Pola loss live terjadi karena build lama `v1.02 PROFIT30` masih aktif:

- EA membuka banyak posisi `MRV` mean-reversion buy dalam hitungan detik ketika harga belum benar-benar reversal.
- Build lama memakai `risk=30`, `maxPos=42`, `sameSide=28`, dan jeda entry `1` detik.
- Guard 30% baru aktif setelah drawdown sudah melewati threshold karena banyak posisi terbuka/tertutup hampir bersamaan.
- Local terminal sempat `Algo Trading` off, tetapi log menunjukkan ada session/VPS lain yang tetap mengirim order.

## Latest Standard Tuning Snapshot

Setup: `XAUUSDm`, `M1`, Standard account context, deposit `150 USD`, mode `Every tick`.

| Profile | Window | Net Profit | Trades | PF | Win Rate | Max EqDD |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| old guarded `v1.03` | 2026.01.01-2026.05.08 | +1165254.02% | 1941 | 1.69 | 60.95% | 7.29% |
| old guarded `v1.03` | 2025.01.01-2026.05.08 | +2027.26% | 927 | 1.51 | 59.55% | 15.01% |
| current `v1.04` | 2026.01.01-2026.05.08 | +1184409.69% | 1858 | 1.76 | 61.89% | 7.53% |
| current `v1.04` | 2025.01.01-2026.05.08 | +15410874.16% | 7959 | 1.76 | 57.29% | 3.18% |

Perubahan `v1.04`: max same-side positions `6 -> 4`, fast-loss cooldown trigger `3 -> 2`. Ini dipilih karena meningkatkan robustness 2025-current tanpa memangkas profit 2026.

## Previous Pro Snapshot

Setup `150 USD`: `XAUUSD`, `M1`, Pro account context, deposit `150 USD`, leverage `1:2000`, model `Every tick`.

| Window | Net Profit | Trades | Trades/day | PF | Max EqDD |
| --- | ---: | ---: | ---: | ---: | ---: |
| 2026.05.07-2026.05.08 | +16.41% | 27 | 27.0 | 2.60 | 4.71% |
| 2026.01.01-2026.05.08 | +3599296.33% | 3653 | 28.5 | 1.55 | 6.38% |

Setup `300 USD`: `XAUUSD`, `M1`, Pro account context, deposit `300 USD`, leverage `1:2000`, model `Every tick`.

| Window | Net Profit | Trades | Trades/day | PF | Max EqDD |
| --- | ---: | ---: | ---: | ---: | ---: |
| 2026.05.07-2026.05.08 | +11.60% | 17 | 17.0 | 3.06 | 3.02% |
| 2026.01.01-2026.05.08 | +2148908.70% | 4201 | 32.8 | 1.49 | 8.83% |
| 2025.01.01-2026.05.08 | +12936930.45% | 11797 | 23.8 | 1.83 | 1.61% |
| 2023.01.01-2026.05.08 | +15893310.40% | 15165 | 12.4 | 1.86 | 1.30% |

## Forward-Test Read

Build ini adalah kandidat pengganti raw profit30. Jangan jalankan raw `v1.02 PROFIT30` lagi di VPS. Setelah copy file `.ex5` baru, attach ke chart gold `M1` dan pastikan Experts log menampilkan:

`ACANE LOCKED PROFILE v1.04 GUARDED`

Catatan risiko: guard `15%` bukan garansi absolut. Slippage, gap, spread melebar, koneksi putus, atau close failure masih bisa membuat real loss melewati threshold.
