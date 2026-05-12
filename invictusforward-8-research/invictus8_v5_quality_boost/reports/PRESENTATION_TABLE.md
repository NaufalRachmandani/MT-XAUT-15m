# Invictus Forward-8 Version Comparison

Scope valid untuk keputusan tuning: native MT5 Strategy Tester `.htm`, `XAUUSDc`, `USC`, `M15`, deposit `1000 USC`, leverage `1:2000`, 2026 only, real ticks. Python hanya dipakai untuk parse dan merapikan report.

Catatan kualitas data: hasil manual `XAUUSD` standard account periode `2025.01.01-2026.05.10` hanya `70%` history quality, jadi dipakai sebagai proxy check saja, bukan dasar keputusan tuning.

## Main Evolution Table

| Version | Role | Net Profit | ROI on 1000 | PF | Trades | Win Rate | Equity DD | Largest Loss | Max CL | History | Verdict |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| Base | Original ZIP | 802.11 | 80.21% | 1.11 | 298 | 68.12% | 52.85% | -153.52 | 7 | 100% real ticks | Rejected: profit kecil dan DD ekstrem. |
| V1 | First tuned | 3,024.49 | 302.45% | 1.58 | 237 | 75.53% | 32.88% | -199.70 | 5 | 100% real ticks | Baseline awal; profit naik, DD masih tinggi. |
| V2 | Profit-first native optimizer | 5,480.48 | 548.05% | 1.31 | 513 | 76.61% | 40.43% | -499.50 | 6 | 100% real ticks | Rejected: OOS May gagal dan largest loss membesar. |
| V2Live | Risk-adjusted optimizer | 2,255.75 | 225.58% | 1.69 | 190 | 75.26% | 28.33% | -149.90 | 7 | 100% real ticks | Rejected: lebih defensif dari V2, tapi belum paling kuat. |
| V3 | April guard reference | 3,291.08 | 329.11% | 3.06 | 158 | 80.38% | 12.73% | -124.90 | 3 | 100% real ticks | Best low-risk baseline sejauh ini. |
| V4 | Profit boost | 16,322.03 | 1632.20% | 3.31 | 167 | 81.44% | 28.63% | -849.10 | 3 | 100% real ticks | Profit besar, tetapi loss size/DD belum layak live kecil. |
| V5 Safe | Quality/profit scaled | 9,701.49 | 970.15% | 3.10 | 165 | 81.21% | 22.14% | -416.50 | 3 | 100% real ticks | Risk candidate terbaik: profit tinggi dengan DD lebih rendah dari V4. |
| V5 High | High-profit scaled | 18,771.29 | 1877.13% | 2.55 | 169 | 81.07% | 26.87% | -3,110.40 | 3 | 100% real ticks | Profit tinggi, largest loss terlalu besar. |
| V5 Max | Max-profit scaled | 19,839.91 | 1983.99% | 2.52 | 169 | 81.07% | 28.60% | -3,732.50 | 3 | 100% real ticks | Profit winner, not live-ready karena largest loss ekstrem. |

## Key Candidate Window Matrix

Format cell: `net profit / equity DD / profit factor`. Semua dari native MT5 report pada `XAUUSDc` 1000 USC.

| Version | Mar validation | Apr validation | May OOS | Last month | YTD 2026 |
|---|---:|---:|---:|---:|---:|
| V3 Reference | - | - | - | 598.82 / DD 12.51% / PF 4.41 | 3,291.08 / DD 12.73% / PF 3.06 |
| V4 Profit Boost | 1,399.70 / DD 16.68% / PF 3.24 | 717.83 / DD 26.07% / PF 1.99 | 579.60 / DD 13.11% / PF no loss | 1,542.14 / DD 14.60% / PF 5.46 | 16,322.03 / DD 28.63% / PF 3.31 |
| V5 Safe | 1,034.90 / DD 26.28% / PF 2.80 | 588.67 / DD 18.97% / PF 2.26 | 562.90 / DD 10.49% / PF no loss | 1,459.98 / DD 9.99% / PF 7.59 | 9,701.49 / DD 22.14% / PF 3.10 |
| V5 High | 1,649.50 / DD 38.36% / PF 2.77 | 790.49 / DD 31.09% / PF 2.00 | 795.80 / DD 13.68% / PF no loss | 2,337.20 / DD 14.72% / PF 6.98 | 18,771.29 / DD 26.87% / PF 2.55 |
| V5 Max | 1,651.90 / DD 42.43% / PF 2.53 | 819.39 / DD 30.27% / PF 2.06 | 1,022.00 / DD 14.31% / PF no loss | 2,562.40 / DD 13.80% / PF 8.01 | 19,839.91 / DD 28.60% / PF 2.52 |

## V4/V5 Probe Appendix

| Source | Variant | Net Profit | ROI on 1000 | PF | Trades | Win Rate | Equity DD | Largest Loss | Max CL |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| V4 | `v4_lot_200` | 16,322.03 | 1632.20% | 3.31 | 167 | 81.44% | 28.63% | -849.10 | 3 |
| V4 | `v4_aggressive_boost` | 15,156.73 | 1515.67% | 3.18 | 165 | 81.21% | 28.18% | -799.20 | 3 |
| V4 | `v4_balanced_boost` | 8,215.01 | 821.50% | 3.13 | 166 | 81.33% | 21.73% | -399.60 | 3 |
| V4 | `v4_lot_150` | 8,103.78 | 810.38% | 3.11 | 164 | 81.10% | 21.86% | -399.60 | 3 |
| V4 | `v3_reference` | 3,291.08 | 329.11% | 3.06 | 158 | 80.38% | 12.73% | -124.90 | 3 |
| V4 | `v4_ref_logic_fixed_lots` | 3,291.08 | 329.11% | 3.06 | 158 | 80.38% | 12.73% | -124.90 | 3 |
| V4 | `v4_rr_boost` | 3,043.18 | 304.32% | 2.91 | 156 | 80.13% | 13.19% | -124.90 | 3 |
| V5 | `v5_max_profit_scaled` | 19,839.91 | 1983.99% | 2.52 | 169 | 81.07% | 28.60% | -3,732.50 | 3 |
| V5 | `v5_high_profit_scaled` | 18,771.29 | 1877.13% | 2.55 | 169 | 81.07% | 26.87% | -3,110.40 | 3 |
| V5 | `v5_mid_profit_scaled` | 13,095.74 | 1309.57% | 3.24 | 166 | 81.33% | 24.79% | -555.40 | 3 |
| V5 | `v5_profit_scaled` | 9,701.49 | 970.15% | 3.10 | 165 | 81.21% | 22.14% | -416.50 | 3 |
| V5 | `v5_quality_scaled` | 6,045.18 | 604.52% | 3.04 | 165 | 81.21% | 17.63% | -254.50 | 3 |
| V5 | `v5_strong_rr_scaled` | 5,697.38 | 569.74% | 2.95 | 163 | 80.98% | 17.66% | -244.70 | 3 |
| V5 | `v5_leak_block_scaled` | 4,879.31 | 487.93% | 2.29 | 138 | 79.71% | 19.40% | -821.10 | 4 |
| V5 | `v3_reference` | 3,291.08 | 329.11% | 3.06 | 158 | 80.38% | 12.73% | -124.90 | 3 |

## Manual USD Proxy Check

| Setup | Period | History Quality | Net Profit | PF | Trades | Win Rate | Equity DD | Largest Loss | Decision Use |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| V5 manual on `XAUUSD`, 1000 USD, leverage 1:2000 | 2025.01.01-2026.05.10 | 70% | 692.64 USD | 1.35 | 280 | 59.29% | 18.14% | -26.23 | Proxy check only; not valid as 100% tick-learning source. |

## Presentation Talking Points

- `Base` ke `V1`: profit naik besar, tetapi drawdown masih tinggi untuk akun cent 1000 USC.
- `V2`: native optimization profit-first berhasil menaikkan profit YTD, tapi gagal sebagai live candidate karena OOS/May dan loss size memburuk.
- `V2Live`: lebih defensif dari V2, tetapi belum cukup kuat untuk dipilih.
- `V3`: baseline risk terbaik saat ini, dengan PF tinggi dan DD jauh lebih rendah.
- `V4`: profit melonjak, namun DD dan largest loss terlalu besar untuk 1000 USC.
- `V5 Safe`: kandidat kompromi terbaik sejauh ini: profit jauh di atas V3, DD lebih rendah dari V4, tapi tetap perlu validasi forward/manual.
- `V5 Max`: profit winner di YTD, tetapi bukan live-ready karena largest loss ekstrem.
- Standard-account `XAUUSD` ternyata tetap hanya 70% history quality pada test manual, jadi belum bisa dipakai untuk membuktikan performa pre-2026 secara valid.

## Suggested Slide Summary

Untuk presentasi singkat, pakai tiga kandidat akhir: `V3` sebagai low-risk baseline, `V5 Safe` sebagai kandidat realistis, dan `V5 Max` sebagai profit-ceiling/rejected-risk reference. Rekomendasi teknis saat ini: jangan live-kan V5 Max di 1000 USC; kalau mau lanjut eksperimen, fokus turunkan largest loss V5 Safe tanpa menghancurkan PF.
