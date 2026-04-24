# MT XAU v11

Repository ini sekarang difokuskan ke satu versi aktif: `v11` split engine untuk `XAUUSDc` timeframe `M5`.

Versi lama `v1` sampai `v10` dan cache iterasinya sudah dipindahkan ke Git history. Jika perlu mengambil ulang data lama, gunakan commit sebelum cleanup: `546f3b6`.

## File Aktif

- [InvictusBullM5_v11.mq5](/Users/naufalrachmandani/Hobby/MT5%20XAU%2015m/mt5/InvictusBullM5_v11.mq5): BUY-only engine.
- [InvictusBearM5_v11.mq5](/Users/naufalrachmandani/Hobby/MT5%20XAU%2015m/mt5/InvictusBearM5_v11.mq5): SELL-only engine.
- [InvictusCombinedM5_v11.mq5](/Users/naufalrachmandani/Hobby/MT5%20XAU%2015m/mt5/InvictusCombinedM5_v11.mq5): combined tester untuk backtest portfolio.

## Preset

- [InvictusBullM5_v11.default_2026.set](/Users/naufalrachmandani/Hobby/MT5%20XAU%2015m/mt5/InvictusBullM5_v11.default_2026.set)
- [InvictusBearM5_v11.default_2026.set](/Users/naufalrachmandani/Hobby/MT5%20XAU%2015m/mt5/InvictusBearM5_v11.default_2026.set)
- [InvictusCombinedM5_v11.default_2026.set](/Users/naufalrachmandani/Hobby/MT5%20XAU%2015m/mt5/InvictusCombinedM5_v11.default_2026.set)

## Dokumentasi

- [InvictusForward-1-Docs_v11.html](/Users/naufalrachmandani/Hobby/MT5%20XAU%2015m/build/InvictusForward-1-Docs_v11.html)
- [v11_summary.md](/Users/naufalrachmandani/Hobby/MT5%20XAU%2015m/build/v11_summary.md)
- [v11_split_m5/summary.md](/Users/naufalrachmandani/Hobby/MT5%20XAU%2015m/build/v11_split_m5/summary.md)

## Backtest Snapshot

Setup: `XAUUSDc`, `M5`, `Deposit 100 USD`, `Leverage 1:100`, mode `Every tick`.

| Bot | Window | Net Profit | Trades | Win Rate | PF | EqDD |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Combined tester | 2026-only | +504.76% | 152 | 61.18% | 2.53 | 21.28% |
| Combined tester | 2025-current | +426.34% | 614 | 56.51% | 1.44 | 55.03% |
| Bull-only | 2026-only | +135.95% | 135 | 48.15% | 1.85 | 13.68% |
| Bear-only | 2026-only | +59.61% | 31 | 64.52% | 3.13 | 9.35% |

## Live Setup

MT5 hanya bisa attach satu EA per chart. Untuk live split:

1. Buka chart pertama: `XAUUSDc`, timeframe `M5`, attach `InvictusBullM5_v11`.
2. Buka chart kedua: `XAUUSDc`, timeframe `M5`, attach `InvictusBearM5_v11`.
3. Pastikan `Algo Trading` ON.
4. Gunakan default input/preset kecuali memang sedang eksperimen.

`InvictusCombinedM5_v11` sebaiknya dipakai untuk backtest portfolio, bukan setup live utama.

## Automation

- [MT5_AUTOMATED_BACKTEST.md](/Users/naufalrachmandani/Hobby/MT5%20XAU%2015m/docs/MT5_AUTOMATED_BACKTEST.md)
- [backtest_v11_split.py](/Users/naufalrachmandani/Hobby/MT5%20XAU%2015m/tools/backtest_v11_split.py)
