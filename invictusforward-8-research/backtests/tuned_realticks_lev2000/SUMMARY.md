# InvictusForward-8 Tuned Backtests

All rows use `Model=4` / every tick based on real ticks and `Leverage=1:2000`.

| Case | Deposit | Window | Net | PF | Trades | WR | Eq DD | Largest Loss | History |
| --- | ---: | --- | ---: | ---: | ---: | ---: | --- | ---: | --- |
| d100_last_week | 100 USD | 2026.05.01 to 2026.05.10 | 116.94 | 3.57 | 10 | 80.00% | 70.26 (24.46%) | -24.94 | 100% real ticks |
| d100_last_month | 100 USD | 2026.04.10 to 2026.05.10 | 162.17 | 1.48 | 39 | 61.54% | 211.66 (70.66%) | -25.55 | 100% real ticks |
| d100_ytd_2026 | 100 USD | 2026.01.01 to 2026.05.10 | 1242.07 | 1.73 | 186 | 69.35% | 384.19 (27.24%) | -51.09 | 100% real ticks |
| d29_last_week | 29 USD | 2026.05.01 to 2026.05.10 | -30.65 | 0.08 | 3 | 33.33% | 68.62 (102.46%) | -20.54 | 100% real ticks |
| d29_ytd_2026 | 29 USD | 2026.01.01 to 2026.05.10 | 1050.19 | 1.65 | 175 | 67.43% | 407.48 (31.90%) | -51.09 | 100% real ticks |
