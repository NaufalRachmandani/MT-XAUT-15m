# InvictusForward-8 Fresh Backtests

All rows use account `265874264`, server `Exness-MT5Real38`, `XAUUSD M15`, `Model=4` / every tick based on real ticks, local agents only.

| Case | Deposit | Delay | Window | Net | PF | Trades | WR | EqDD | Largest Loss | History |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: | --- | ---: | --- |
| d100_delay100_2025_to_20260430_friend_window | 100 USD | 100ms | 2025.01.01 to 2026.04.30 | 24588.10 | 1.19 | 1191 | 70.11% | 15 918.41 (39.52%) | -1623.38 | 69% real ticks |
| d100_delay100_2025_current | 100 USD | 100ms | 2025.01.01 to 2026.05.10 | 20720.59 | 1.15 | 1213 | 69.83% | 20 637.74 (51.23%) | -1623.38 | 70% real ticks |
| d100_delay100_2026_ytd | 100 USD | 100ms | 2026.01.01 to 2026.05.10 | 621.04 | 1.27 | 234 | 58.12% | 587.07 (47.75%) | -49.95 | 100% real ticks |
| d100_delay100_last_month | 100 USD | 100ms | 2026.04.10 to 2026.05.10 | -102.28 | 0.72 | 30 | 43.33% | 301.82 (100.76%) | -25.55 | 100% real ticks |
| d100_delay100_last_week | 100 USD | 100ms | 2026.05.01 to 2026.05.10 | 3.25 | 1.02 | 14 | 50.00% | 113.32 (82.13%) | -24.94 | 100% real ticks |
| d100_delay200_2026_ytd | 100 USD | 200ms | 2026.01.01 to 2026.05.10 | 622.52 | 1.29 | 234 | 58.97% | 594.71 (48.03%) | -49.95 | 100% real ticks |
| d100_delay200_last_week | 100 USD | 200ms | 2026.05.01 to 2026.05.10 | 20.46 | 1.15 | 15 | 53.33% | 98.31 (70.40%) | -24.94 | 100% real ticks |
| d29_delay100_2026_ytd_sanity | 29 USD | 100ms | 2026.01.01 to 2026.05.10 | 624.22 | 1.28 | 231 | 58.01% | 587.07 (50.54%) | -49.95 | 100% real ticks |
| d29_delay100_last_week_sanity | 29 USD | 100ms | 2026.05.01 to 2026.05.10 | -29.34 | 0.15 | 5 | 40.00% | 67.31 (100.51%) | -20.54 | 100% real ticks |
