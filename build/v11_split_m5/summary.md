# v11 Split M5 Backtest

Setup: `XAUUSDc`, `M5`, `Deposit 100 USD`, `Leverage 1:100`, `Every tick`.

Final profile: `zone_loose`.

## Combined Tester

`InvictusCombinedM5_v11.default_2026.set`

| Window | Net Profit | Trades | Win Rate | Profit Factor | EqDD |
| --- | ---: | ---: | ---: | ---: | ---: |
| Last 2W | 15.30% | 10 | 80.00% | 4.30 | 4.87% |
| 2026 YTD | 504.76% | 152 | 61.18% | 2.53 | 21.28% |
| 2025-Current | 426.34% | 614 | 56.51% | 1.44 | 55.03% |

## Direction Split

| Bot | Last 2W Net | Last 2W Trades | 2026 Net | 2026 Trades | 2026 PF | 2026 EqDD | 2025-Current Net | 2025-Current Trades | 2025-Current EqDD |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| bull-only | 16.67% | 10 | 135.95% | 135 | 1.85 | 13.68% | 74.95% | 567 | 46.82% |
| bear-only | -1.01% | 1 | 59.61% | 31 | 3.13 | 9.35% | 20.01% | 126 | 36.10% |

Catatan: `combined tester` bukan penjumlahan hasil bull-only dan bear-only. Combined tester memakai satu equity curve, sehingga compounding dan exposure management berbeda dari backtest terpisah.
