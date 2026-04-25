# v11 Split M5 Backtest

Setup: `XAUUSDc`, `M5`, `Deposit 100 USD`, `Leverage 1:100`, `Every tick`. Recent window = `2026.04.01-2026.04.25`.

Final profile: `v11 split M5 readable-score`.

## Combined Tester

`InvictusCombinedM5_v11.default_2026.set`

| Window | Net Profit | Trades | Win Rate | Profit Factor | EqDD |
| --- | ---: | ---: | ---: | ---: | ---: |
| 2026.04.01-2026.04.25 | 40.25% | 25 | 64.00% | 3.12 | 7.30% |
| 2026 YTD | 558.51% | 155 | 58.06% | 2.70 | 17.71% |

## Direction Split

| Bot | Recent Net | Recent Trades | Recent PF | 2026 Net | 2026 Trades | 2026 PF | 2026 EqDD |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| bull-only | 39.97% | 23 | 3.63 | 269.58% | 127 | 2.37 | 17.72% |
| bear-only | 11.95% | 15 | 1.79 | 68.37% | 87 | 1.50 | 32.25% |

Catatan: `combined tester` bukan penjumlahan hasil bull-only dan bear-only. Combined tester memakai satu equity curve, sehingga compounding dan exposure management berbeda dari backtest terpisah.

## Readable Trade Notes

Comment trade sekarang memuat dua bentuk sekaligus:

- Marker internal pendek agar EA tetap bisa mengelola exit/add-on: `ZB`, `BE`, `AB`, `WG`, `RG`.
- Label manusia agar mudah dibaca di MT5 mobile/history: `BUY_ZONE`, `SELL_BREAK`, `BUY_ADDON`.

Contoh: `S11|SELL_BREAK|BE|S72|B|RG|BR` berarti bear bot v11 masuk SELL dari bearish breakout, score 72, grade B, strong-regime, dan breakout.

## Exit Management Update

- Bull-only dan combined tester memakai `time_strict`: `V10_TimeCloseProfitOnly=false`, `V10_MaxHoldBars=24`, `V10_ZoneMaxHoldBars=12`, `V10_AddOnMaxHoldBars=8`.
- Bear-only tetap memakai exit default karena split validation menunjukkan `time_strict` menurunkan bear YTD dari `+60.73%` ke `+45.32%`.
- TP manager / partial close tetap default `false`. Exit matrix menunjukkan partial/trailing menambah jumlah trade, tetapi menurunkan total profit.
- Log exit sekarang memakai label jelas seperti `MOVE_SL_TO_BE`, `TIME_CLOSE`, `TP1_RUNNER_SET`, `TRAIL_SL`, `FAST_FAIL_CLOSE`, dan `WEAK_SELL_QUICK_EXIT`.

## Bear Safety Update

`safe_break_quality` menjadi default Bear:

- `V10_MinTradeScore=64`
- `V10_MinBreakATR=0.05`
- `V10_WeakSellMinBreakATR=0.08`
- `V10_MinBodyRatio=0.46`
- `V10_WeakSellMinBodyRatio=0.50`

Efek terhadap Bear YTD: `+68.37%`, `87` trades, PF `1.50`, EqDD `32.25%`.
