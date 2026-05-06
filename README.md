# Suis M5

Repository ini sekarang memakai naming baru yang lebih stabil:

- `SuisM5_v1`: stable profile.
- `SuisM5_v2`: aggressive frequency profile.

Internal source sekarang memakai prefix generik `SUIS_`, supaya versi berikutnya tetap mudah dibaca tanpa nama historis yang membingungkan.

## Live Files

- [SuisM5_v1.mq5](</Users/naufalrachmandani/Hobby/MT5 XAU 15m/mt5/SuisM5_v1.mq5>)
- [SuisM5_v2.mq5](</Users/naufalrachmandani/Hobby/MT5 XAU 15m/mt5/SuisM5_v2.mq5>)
- [SuisM5_v1.ex5](</Users/naufalrachmandani/Hobby/MT5 XAU 15m/build/suis_live_package/MQL5/Experts/Suis/SuisM5_v1.ex5>)
- [SuisM5_v2.ex5](</Users/naufalrachmandani/Hobby/MT5 XAU 15m/build/suis_live_package/MQL5/Experts/Suis/SuisM5_v2.ex5>)
- [suis_live_package.zip](</Users/naufalrachmandani/Hobby/MT5 XAU 15m/build/suis_live_package.zip>)

Copy file `.ex5` ke `MQL5/Experts/Suis/` di VPS. Tidak perlu preset `.set`.

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
