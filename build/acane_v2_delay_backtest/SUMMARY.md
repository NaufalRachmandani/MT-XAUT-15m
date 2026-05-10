# AcaneM1 v2 delay backtest

Setup: `XAUUSD`, `M1`, account `265874264` on `Exness-MT5Real38`, deposit `$29`, leverage `1:2000`, `Model=4` real ticks.

| Window | Delay | Net | PF | Trades | Win rate | Eq DD | History |
| --- | ---: | ---: | ---: | ---: | ---: | --- | --- |
| current_2025 | 100ms | -14.36 | 0.85 | 274 | 55.11% | 18.91 (56.36%) | 70% real ticks |
| friday_20260508 | 100ms | 0.00 | 0.00 | 0 | 0.00% | 0.00 (0.00%) | 100% real ticks |
| recent_20260501 | 100ms | -0.20 | 0.94 | 6 | 50.00% | 2.31 (7.97%) | 100% real ticks |
| recent_20260501_d100 | 100ms | -0.67 | 0.92 | 12 | 41.67% | 4.69 (4.56%) | 100% real ticks |
| recent_20260501_stress | 200ms | -0.13 | 0.96 | 6 | 50.00% | 2.31 (7.97%) | 100% real ticks |
| ytd_2026 | 100ms | 6.11 | 1.11 | 130 | 61.54% | 14.11 (37.14%) | 100% real ticks |
| ytd_2026_d100 | 100ms | -4.01 | 0.98 | 280 | 53.93% | 28.92 (26.33%) | 100% real ticks |
| ytd_2026_stress | 200ms | 11.48 | 1.17 | 151 | 61.59% | 11.95 (32.90%) | 100% real ticks |

Raw results are in `delay_results.json`.
