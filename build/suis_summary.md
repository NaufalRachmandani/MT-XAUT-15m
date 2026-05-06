# Suis M5 Summary

Aktif sekarang:

- `SuisM5_v1`: stable profile.
- `SuisM5_v2`: aggressive frequency profile.

Source internal sudah memakai prefix generik `SUIS_`.

## Sanity Backtest Setelah Rename

Setup: `XAUUSDc`, `M5`, `Deposit 100 USD`, `Leverage 1:100`, mode `Every tick`, window `2026.01.01-2026.05.07`.

| EA | Net Profit | Trades | PF | EqDD |
| --- | ---: | ---: | ---: | ---: |
| `SuisM5_v1` | +5900.48% | 95 | 5.71 | 11.85% |
| `SuisM5_v2` | +22259.69% | 125 | 4.26 | 19.94% |

## Live Package

- `build/suis_live_package/MQL5/Experts/Suis/SuisM5_v1.ex5`
- `build/suis_live_package/MQL5/Experts/Suis/SuisM5_v2.ex5`
- `build/suis_live_package.zip`

Rekomendasi live saat ini: `SuisM5_v2`.
