# v5 20x Summary

Champion: iterasi 15 `low_balance_b`
Guardrail: net profit > 0, PF >= 1.03, trades >= 350, equity DD <= 95%

| Iter | Name | Lev | Accepted | Net Profit | PF | WR | Trades | Eq DD | Buy PnL | Sell PnL | SW PnL | Trend TP/SL | Takeaway |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| 01 | baseline_v4_clone | 1:100 | yes | 197.42 | 1.08 | 52.01% | 771 | 90.51% | 113.57 | 8.75 | 75.10 | 90/262 | Baseline champion awal. |
| 02 | leverage_1_50 | 1:50 | no | -56.01 | 0.91 | 54.59% | 392 | 82.46% | -67.86 | -18.99 | 30.84 | 25/68 | Ditolak: profit berubah negatif. |
| 03 | leverage_1_75 | 1:75 | no | 194.96 | 1.08 | 51.87% | 802 | 88.90% | 95.45 | 47.15 | 52.36 | 91/275 | Promising: risk turun dan profit tetap dekat champion. |
| 04 | slow_compound_a | 1:100 | no | 195.77 | 1.08 | 51.67% | 780 | 90.25% | 119.38 | 1.55 | 74.84 | 90/270 | Promising: risk turun dan profit tetap dekat champion. |
| 05 | slow_compound_b | 1:100 | no | 195.77 | 1.08 | 51.67% | 780 | 90.25% | 119.38 | 1.55 | 74.84 | 90/270 | Promising: risk turun dan profit tetap dekat champion. |
| 06 | position_caps_a | 1:100 | no | -81.86 | 0.93 | 51.29% | 349 | 96.31% | -107.18 | -1.03 | 26.35 | 38/121 | Ditolak: profit berubah negatif. |
| 07 | position_caps_b | 1:100 | no | -81.86 | 0.93 | 51.29% | 349 | 96.31% | -107.18 | -1.03 | 26.35 | 38/121 | Ditolak: profit berubah negatif. |
| 08 | daily_caps_a | 1:100 | no | 141.77 | 1.07 | 50.58% | 686 | 87.91% | 82.90 | 40.97 | 17.90 | 81/233 | Netral: ada perbaikan lokal, tapi belum cukup kuat untuk mengganti champion. |
| 09 | daily_caps_b | 1:100 | yes | 215.49 | 1.10 | 50.77% | 717 | 75.89% | 184.18 | -3.63 | 34.94 | 85/241 | Dibawa ke baseline berikutnya. |
| 10 | buy_filter_a | 1:100 | yes | 279.66 | 1.11 | 52.59% | 793 | 73.24% | 248.38 | -1.71 | 32.99 | 89/255 | Dibawa ke baseline berikutnya. |
| 11 | buy_filter_b | 1:100 | no | 210.02 | 1.06 | 50.62% | 800 | 80.63% | 313.95 | -95.97 | -7.96 | 88/243 | Netral: ada perbaikan lokal, tapi belum cukup kuat untuk mengganti champion. |
| 12 | sell_filter_a | 1:100 | yes | 290.69 | 1.12 | 52.17% | 782 | 69.38% | 260.67 | 10.86 | 19.16 | 91/254 | Dibawa ke baseline berikutnya. |
| 13 | sell_filter_b | 1:100 | no | 289.75 | 1.12 | 52.80% | 767 | 71.08% | 163.97 | 90.64 | 35.14 | 85/240 | Promising: sisi sell terlihat lebih bersih tanpa merusak total edge. |
| 14 | low_balance_a | 1:100 | yes | 289.87 | 1.16 | 51.41% | 710 | 60.10% | 272.03 | 24.00 | -6.16 | 83/229 | Dibawa ke baseline berikutnya. |
| 15 | low_balance_b | 1:100 | yes | 278.04 | 1.20 | 52.08% | 672 | 54.24% | 258.64 | 7.41 | 11.99 | 78/222 | Dibawa ke baseline berikutnya. |
| 16 | combo_core | 1:50 | no | -44.96 | 0.82 | 53.49% | 258 | 67.86% | -26.21 | -24.06 | 5.31 | 8/37 | Ditolak: profit berubah negatif. |
| 17 | combo_core_buy | 1:50 | no | -44.96 | 0.82 | 53.49% | 258 | 67.86% | -26.21 | -24.06 | 5.31 | 8/37 | Ditolak: profit berubah negatif. |
| 18 | combo_core_sell | 1:50 | no | -44.96 | 0.82 | 53.49% | 258 | 67.86% | -26.21 | -24.06 | 5.31 | 8/37 | Ditolak: profit berubah negatif. |
| 19 | combo_balanced | 1:75 | no | -65.51 | 0.78 | 54.71% | 223 | 81.78% | -40.03 | -34.51 | 9.03 | 8/39 | Ditolak: profit berubah negatif. |
| 20 | champion_challenge | 1:50 | no | 127.32 | 1.15 | 51.75% | 400 | 70.94% | 6.00 | 115.86 | 5.46 | 46/132 | Netral: ada perbaikan lokal, tapi belum cukup kuat untuk mengganti champion. |
