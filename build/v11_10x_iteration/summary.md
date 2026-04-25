# v11 10x Iteration

Setup: `XAUUSDc`, `M5`, `Deposit 100 USD`, `Leverage 1:100`, `Every tick`.

Catatan: tabel ini adalah ranking iterasi untuk memilih preset. Validasi final setelah comment marker dibuat readable dan tetap kompatibel dengan internal EA ada di `build/v11_final_backtest.json`.

| Side | Rank | Iter | Preset | Recent Net | Recent Trades | Recent PF | YTD Net | YTD Trades | YTD PF | YTD EqDD |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| bull | 1 | 1 | bull_control | 41.08% | 23 | 3.44 | 239.10% | 126 | 2.09 | 21.18% |
| bull | 2 | 2 | bull_score62 | 41.08% | 23 | 3.44 | 239.10% | 126 | 2.09 | 21.18% |
| bull | 3 | 6 | bull_addon_dense | 33.78% | 27 | 2.59 | 231.43% | 159 | 1.93 | 17.24% |
| bull | 4 | 5 | bull_sub_loose | 29.52% | 31 | 2.15 | 139.34% | 174 | 1.52 | 21.14% |
| bull | 5 | 4 | bull_zone_dense | 18.15% | 25 | 1.64 | 172.85% | 139 | 1.68 | 15.45% |
| bull | 6 | 3 | bull_session_open | -2.84% | 42 | 0.95 | 70.18% | 245 | 1.12 | 48.51% |
| bull | 7 | 10 | bull_fast_scalp | -15.35% | 56 | 0.73 | 80.78% | 281 | 1.15 | 46.08% |
| bull | 8 | 9 | bull_trend_push | -4.70% | 42 | 0.94 | 63.11% | 250 | 1.07 | 62.88% |
| bull | 9 | 8 | bull_tp_dense | -16.77% | 63 | 0.69 | 12.78% | 390 | 1.03 | 42.18% |
| bull | 10 | 7 | bull_dense_mix | -38.70% | 75 | 0.54 | 9.40% | 410 | 1.01 | 70.72% |
| bear | 1 | 7 | bear_dense_mix | 16.14% | 8 | 5.73 | 66.86% | 84 | 1.54 | 36.76% |
| bear | 2 | 8 | bear_tp_dense | 13.00% | 9 | 8.22 | 57.74% | 95 | 1.74 | 31.85% |
| bear | 3 | 3 | bear_session_open | 15.48% | 5 | 9.60 | 84.16% | 55 | 1.98 | 35.28% |
| bear | 4 | 9 | bear_trend_push | 25.81% | 5 | 9.60 | 81.98% | 56 | 1.58 | 49.26% |
| bear | 5 | 4 | bear_zone_dense | 1.02% | 1 | 0.00 | 76.09% | 34 | 2.63 | 13.32% |
| bear | 6 | 10 | bear_fast_scalp | 5.69% | 5 | 2.37 | 35.46% | 58 | 1.41 | 39.57% |
| bear | 7 | 6 | bear_addon_dense | 0.00% | 0 | 0.00 | 79.70% | 30 | 3.47 | 13.33% |
| bear | 8 | 1 | bear_control | 0.00% | 0 | 0.00 | 77.54% | 26 | 3.39 | 13.27% |
| bear | 9 | 2 | bear_score62 | 0.00% | 0 | 0.00 | 77.54% | 26 | 3.39 | 13.27% |
| bear | 10 | 5 | bear_sub_loose | -0.46% | 2 | 0.67 | 58.22% | 39 | 2.24 | 14.51% |

## Final Pick

- Bull memakai `bull_control`, karena varian yang lebih ramai trade menurunkan PF dan memperlebar drawdown.
- Bear memakai `bear_dense_mix`, lalu source default bear disesuaikan agar SELL lebih aktif.
- Setelah exit matrix diterapkan, validasi final source default: bull recent 23 trade, bear recent 15 trade, combined recent 25 trade; combined 2026 YTD `+558.51%` dengan `155` trade.
