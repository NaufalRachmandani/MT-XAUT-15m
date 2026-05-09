# AcaneM1 v2 delay 50ms backtest

Setup: `XAUUSD`, `M1`, account `265874264` on `Exness-MT5Real38`, deposit `$29`, leverage `1:2000`, `Model=4` real ticks.

| Window | Delay | Net | PF | Trades | Win rate | Eq DD | History |
| --- | ---: | ---: | ---: | ---: | ---: | --- | --- |
| final_current_2025 | 50ms | 2.96 | 4.22 | 18 | 77.78% | 1.20 (3.85%) | 70% real ticks |
| final_friday_20260508 | 50ms | 0.00 | 0.00 | 0 | 0.00% | 0.00 (0.00%) | 100% real ticks |
| final_lastweek_20260501 | 50ms | 0.03 | 0.00 | 1 | 100.00% | 0.20 (0.69%) | 100% real ticks |
| final_ytd_2026 | 50ms | 1.61 | 8.32 | 5 | 80.00% | 0.91 (3.08%) | 100% real ticks |

Raw results are in `delay50_results.json`.
