# v11 Split M5 Summary

Setup utama: `XAUUSDc`, `M5`, `Deposit 100 USD`, `Leverage 1:100`, `Every tick`.

`v11` memecah arsitektur menjadi tiga file:

- `InvictusBullM5_v11`: BUY-only untuk live chart bullish.
- `InvictusBearM5_v11`: SELL-only untuk live chart bearish.
- `InvictusCombinedM5_v11`: tester gabungan untuk mensimulasikan portfolio bull+bear dalam satu backtest.

## Champion Profile

Profil final yang dibekukan: `zone_loose`.

Perubahan utama dari `v10`:

- Risk dinaikkan ke `5.00%` base budget.
- `MaxPositions=6`, `WeakRegimeMaxPositions=2`.
- Score gate dilonggarkan ke `V10_MinTradeScore=68`.
- Break/body threshold dilonggarkan untuk `M5`.
- Zone retest dibuat lebih aktif: `ZoneLookback=8`, `ZoneMinBodyRatio=0.46`, `ZoneBreakATR=0.02`, `ZoneMidTouchATR=0.10`, `ZoneOvershootATR=0.35`, `ZoneRiskMultiplier=0.70`, `ZoneRR=1.20`.
- Cross-direction guard aktif antar bot: bull magic `2026042411`, bear magic `2026042412`.
- Comment trade tetap berisi engine, score, grade, dan tags: `B11|...`, `S11|...`, `C11|...`.

## Backtest Champion

`InvictusCombinedM5_v11.default_2026.set`

| Window | Net Profit | Trades | Win Rate | Profit Factor | EqDD |
| --- | ---: | ---: | ---: | ---: | ---: |
| 2026-only | +504.76% | 152 | 61.18% | 2.53 | 21.28% |
| 2025-current | +426.34% | 614 | 56.51% | 1.44 | 55.03% |
| Last 2W | +15.30% | 10 | 80.00% | 4.30 | 4.87% |

## Split Contribution Check

Profil `zone_loose` dijalankan sebagai bot terpisah untuk melihat kontribusi arah.

| Bot | Window | Net Profit | Trades | Win Rate | Profit Factor | EqDD |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Bull-only | 2026-only | +135.95% | 135 | 48.15% | 1.85 | 13.68% |
| Bull-only | Last 2W | +16.67% | 10 | 70.00% | 9.51 | 5.06% |
| Bear-only | 2026-only | +59.61% | 31 | 64.52% | 3.13 | 9.35% |
| Bear-only | Last 2W | -1.01% | 1 | 0.00% | 0.00 | 1.71% |

Catatan: hasil combined tidak sama dengan penjumlahan bull-only + bear-only karena compounding dan exposure portfolio berjalan dalam satu equity curve. Untuk backtest portfolio, gunakan `InvictusCombinedM5_v11`; untuk live split, attach `InvictusBullM5_v11` dan `InvictusBearM5_v11` di dua chart `XAUUSDc M5` terpisah.
