# v11 Split M5 Summary

Setup utama: `XAUUSDc`, `M5`, `Deposit 100 USD`, `Leverage 1:100`, `Every tick`.

`v11` memecah arsitektur menjadi tiga file:

- `InvictusBullM5_v11`: BUY-only untuk live chart bullish.
- `InvictusBearM5_v11`: SELL-only untuk live chart bearish.
- `InvictusCombinedM5_v11`: tester gabungan untuk mensimulasikan portfolio bull+bear dalam satu backtest.

## Champion Profile

Profil final yang dibekukan: `v11 split M5 readable-score`.

Perubahan utama:

- Risk dinaikkan ke `5.00%` base budget.
- Bull engine dipertahankan dari profil terbaik karena profit, PF, dan win rate masih paling stabil.
- Bear engine dituning ulang dari 10 iterasi dan memakai profil `bear_dense_mix` agar SELL tidak terlalu pasif di window April 2026.
- Bear safety iteration memilih `safe_break_quality`: SELL breakout dibuat lebih selektif untuk menurunkan DD tanpa mematikan aktivitas sell.
- `MaxPositions=6` untuk bull/combined dan `MaxPositions=8` untuk bear dense.
- Score gate utama: bull/combined `68`, bear dense `60`.
- Zone retest dan breakout M5 tetap menjadi mesin utama, ditambah compression/add-on untuk memperbanyak entry saat momentum valid.
- Exit matrix 10 preset memilih `time_strict` untuk bull dan combined; bear tetap default karena `time_strict` menurunkan performa SELL.
- Daily Guard `balanced_guard` aktif sebagai default: daily loss cap 8%, profit lock +12% dengan 4% giveback, dan cooldown 180 menit setelah 3 loss beruntun.
- Cross-direction guard aktif antar bot: bull magic `2026042411`, bear magic `2026042412`.
- Comment trade sekarang lebih readable tetapi tetap kompatibel dengan marker internal: contoh `B11|BUY_ZONE|ZB|S76|B|WG|ZN`.

## Backtest Champion

`InvictusCombinedM5_v11.default_2026.set`

| Window | Net Profit | Trades | Win Rate | Profit Factor | EqDD |
| --- | ---: | ---: | ---: | ---: | ---: |
| 2026 YTD | +677.97% | 146 | 60.96% | 2.98 | 17.74% |
| 2026.04.10-2026.04.25 | +10.43% | 12 | 50.00% | 2.22 | 7.30% |

## Split Contribution Check

Profil final dijalankan sebagai bot terpisah untuk melihat kontribusi arah. Ini lebih dekat dengan setup live karena MT5 attach `InvictusBullM5_v11` dan `InvictusBearM5_v11` di dua chart terpisah.

| Bot | Window | Net Profit | Trades | Win Rate | Profit Factor | EqDD |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Bull-only | 2026 YTD | +335.28% | 118 | 60.17% | 2.82 | 17.71% |
| Bull-only | 2026.04.10-2026.04.25 | +10.23% | 10 | 50.00% | 2.84 | 4.87% |
| Bear-only | 2026 YTD | +19.02% | 73 | 50.68% | 1.16 | 32.20% |
| Bear-only | 2026.04.10-2026.04.25 | +12.28% | 13 | 61.54% | 1.91 | 12.60% |

Catatan: hasil combined tidak sama dengan penjumlahan bull-only + bear-only karena compounding dan exposure portfolio berjalan dalam satu equity curve. Untuk backtest portfolio, gunakan `InvictusCombinedM5_v11`; untuk live split, attach `InvictusBullM5_v11` dan `InvictusBearM5_v11` di dua chart `XAUUSDc M5` terpisah.

## 10x Iteration Takeaway

- Bull: `bull_control` tetap menang. Varian yang memaksa trade lebih banyak memang naik jumlah trade, tetapi menurunkan PF dan membuat drawdown terlalu mudah bocor.
- Bear: `bear_dense_mix` dipilih. Ini menaikkan aktivitas SELL di April 2026 dari hampir tidak ada trade menjadi 15 trade pada validasi final, dengan PF masih positif.
- Bear safety: `safe_break_quality` dipilih setelah 10 preset lanjutan. Ini menurunkan EqDD Bear YTD dari `36.76%` ke `32.25%` dan menaikkan net dari `+60.73%` ke `+68.37%`.
- Fokus berikutnya kalau ingin agresif lagi: tambah sub-engine baru, bukan sekadar melonggarkan score gate. Iterasi bull yang terlalu longgar membuktikan quantity tanpa edge cepat merusak equity curve.

## Exit Matrix Takeaway

- Preset terbaik: `time_strict`.
- Combined YTD naik dari `+505.95%` ke `+558.51%`; EqDD turun dari `21.28%` ke `17.71%`.
- Bull-only YTD naik dari `+239.10%` ke `+269.58%`; EqDD turun dari `21.18%` ke `17.72%`.
- Bear-only tidak memakai `time_strict` karena sell memburuk pada validasi split.
- TP manager / partial close tetap nonaktif karena semua varian partial/trailing di matrix exit menurunkan total profit.

## Diagnostic / Observation

- `V11_LogRejectedSignals=true` akan mencetak `V11 REJECT` untuk kandidat yang score-nya dekat threshold.
- `V11_LogStatusOnNewBar=true` akan mencetak status periodik: regime, posisi aktif, spread, equity, dan apakah bar tersebut entry.
- Diagnostic run Bear recent mencatat `15` entry, `1` exit action, dan `0` reject dekat threshold. Artinya filter terbaru tidak sedang membuang banyak kandidat high-score; bottleneck berikutnya bukan score gate saja, tetapi struktur setup yang terbentuk sebelum scoring.

## Monthly Regime Study

Monthly matrix `2023.01` sampai `2026.04` menunjukkan v11 cocok untuk 2026, tetapi tidak robust penuh untuk 2023-2025.

| Year | Base Net | Guard Net | Base Red Months | Guard Red Months | Base Worst DD | Guard Worst DD |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2023 | -19.37 | -26.86 | 7 | 7 | 29.43% | 26.03% |
| 2024 | -72.19 | -75.08 | 7 | 7 | 36.43% | 32.35% |
| 2025 | -69.03 | -57.20 | 8 | 8 | 42.83% | 39.38% |
| 2026 | +249.43 | +285.16 | 0 | 0 | 26.03% | 20.23% |

Keputusan: `balanced_guard` dipakai karena meningkatkan current regime dan menurunkan worst DD, tetapi hostile-regime fix berikutnya harus berupa entry/regime filter baru, bukan risk guard saja.

## Weekend Technical Research

Branch `codex/v11-technical-improvement` menambahkan engine opsional `Impulse Pullback` dengan marker `BUY_IMPULSE` / `SELL_IMPULSE`.

Hasil 11 kandidat combined tester:

| Rank | Preset | Recent | YTD | Decision |
| ---: | --- | ---: | ---: | --- |
| 1 | `control` | +40.25%, 25 trades, PF 3.12, DD 7.30% | +558.51%, 155 trades, PF 2.70, DD 17.71% | Tetap default |
| 2 | `sell_runner` | +40.25%, 25 trades, PF 3.12, DD 7.30% | +547.94%, 155 trades, PF 2.68, DD 17.73% | Dekat, tapi kalah |
| 3 | `sell_aggressive` | +35.07%, 32 trades, PF 2.60, DD 5.45% | +485.94%, 201 trades, PF 2.33, DD 17.69% | Trade naik, expectancy turun |
| 11 | `both_soft_scalp` | +19.19%, 36 trades, PF 1.85, DD 7.56% | +297.42%, 218 trades, PF 2.04, DD 16.70% | Quantity tinggi, profit turun tajam |

Keputusan: `V11_EnableImpulsePullbackEngine=false` tetap default. Engine disimpan untuk riset/diagnostic, bukan untuk live default.
