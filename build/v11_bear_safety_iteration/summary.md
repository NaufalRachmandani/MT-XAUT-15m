# v11 Bear Safety Iteration

Setup: `InvictusBearM5_v11`, `XAUUSDc`, `M5`, `Deposit 100 USD`, `Leverage 1:100`, `Every tick`.

| Rank | Iter | Preset | Recent Net | Recent Trades | Recent PF | YTD Net | YTD Trades | YTD PF | YTD EqDD |
| ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 9 | safe_break_quality | 11.95% | 15 | 1.79 | 68.37% | 87 | 1.50 | 32.25% |
| 2 | 8 | safe_zone_quality | 11.94% | 13 | 1.91 | 77.47% | 83 | 1.62 | 34.58% |
| 3 | 5 | safe_block_weak_zone | 10.39% | 12 | 1.80 | 60.05% | 79 | 1.47 | 34.45% |
| 4 | 1 | bear_current | 11.95% | 15 | 1.79 | 60.73% | 91 | 1.43 | 36.76% |
| 5 | 10 | safe_sell_time_strict_selective | 11.95% | 15 | 1.79 | 60.73% | 91 | 1.43 | 36.76% |
| 6 | 4 | safe_block_weak_addons | 11.55% | 13 | 1.88 | 58.92% | 85 | 1.44 | 36.73% |
| 7 | 6 | safe_strong_only | 4.91% | 7 | 1.56 | 43.85% | 62 | 1.41 | 34.47% |
| 8 | 7 | safe_no_addons | 13.91% | 12 | 2.21 | 65.08% | 78 | 1.50 | 39.41% |
| 9 | 3 | safe_weak_score76 | 11.19% | 11 | 1.91 | 45.67% | 75 | 1.38 | 38.29% |
| 10 | 2 | safe_weak_score72 | 10.39% | 12 | 1.80 | 42.17% | 80 | 1.34 | 38.60% |

## Final Decision

- `safe_break_quality` menjadi default Bear.
- Perubahan default: `V10_MinTradeScore=64`, `V10_MinBreakATR=0.05`, `V10_WeakSellMinBreakATR=0.08`, `V10_MinBodyRatio=0.46`, `V10_WeakSellMinBodyRatio=0.50`.
- Safe mode yang terlalu ketat tidak dipakai sebagai default karena memangkas profit dan tidak menurunkan DD cukup besar.
