# v11 Exit Iteration

Setup: `InvictusCombinedM5_v11`, `XAUUSDc`, `M5`, `Deposit 100 USD`, `Leverage 1:100`, `Every tick`.

| Rank | Iter | Preset | Recent Net | Recent Trades | Recent PF | YTD Net | YTD Trades | YTD PF | YTD EqDD |
| ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 8 | time_strict | 40.25% | 25 | 3.12 | 558.51% | 155 | 2.70 | 17.71% |
| 2 | 1 | exit_control | 41.36% | 25 | 3.00 | 505.95% | 154 | 2.46 | 21.28% |
| 3 | 6 | be_early | 41.36% | 25 | 3.00 | 505.95% | 154 | 2.46 | 21.28% |
| 4 | 7 | be_late | 41.36% | 25 | 3.00 | 505.95% | 154 | 2.46 | 21.28% |
| 5 | 9 | regime_flip | 37.26% | 25 | 2.80 | 488.11% | 154 | 2.41 | 21.28% |
| 6 | 4 | tp_late_runner | 39.79% | 31 | 2.93 | 469.33% | 185 | 2.41 | 18.98% |
| 7 | 2 | tp_default | 36.11% | 36 | 2.78 | 425.32% | 228 | 2.36 | 10.24% |
| 8 | 10 | adaptive_combo | 23.65% | 36 | 2.21 | 329.20% | 236 | 2.19 | 10.24% |
| 9 | 3 | tp_quick_scalp | 23.13% | 38 | 2.27 | 257.33% | 237 | 2.18 | 10.25% |
| 10 | 5 | tp_heavy_partial | 23.63% | 39 | 2.67 | 223.96% | 238 | 2.30 | 10.20% |

## Final Decision

- `time_strict` dipakai untuk `InvictusBullM5_v11` dan `InvictusCombinedM5_v11`.
- `InvictusBearM5_v11` tetap memakai exit default. Split validation menunjukkan bear YTD turun dari `+60.73%` ke `+45.32%` jika `time_strict` dipaksa.
- TP manager / partial close tetap nonaktif karena semua varian TP manager menurunkan profit walau trade count naik.
