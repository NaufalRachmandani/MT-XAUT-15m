# AcaneM1_v1 MT5 Real-Tick Validation

Setup: `XAUUSD`, `M1`, account `265874264`, server `Exness-MT5Real38`, `Model=4` real ticks. Main acceptance uses `$100`, leverage `1:2000`, delay `100ms`.

| Case | Delay | Deposit | Net | PF | Trades | Win rate | Eq DD | Largest loss | History |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: | --- |
| last_week_20260501_20260510 | 100ms | 100 | -0.21 | 0.97 | 10 | 60.00% | 4.37 (4.26%) | -2.05 | 100% real ticks |
| last_month_20260410_20260510 | 100ms | 100 | -2.45 | 0.75 | 14 | 57.14% | 4.37 (4.35%) | -2.05 | 100% real ticks |
| ytd_2026 | 100ms | 100 | 12.91 | 1.15 | 149 | 64.43% | 18.41 (16.95%) | -2.73 | 100% real ticks |
| current_2025 | 100ms | 100 | 4.12 | 1.02 | 563 | 60.75% | 44.02 (35.09%) | -2.73 | 70% real ticks |
| stress_last_month_20260410_20260510 | 200ms | 100 | -2.92 | 0.72 | 14 | 57.14% | 4.75 (4.71%) | -2.46 | 100% real ticks |
| stress_ytd_2026 | 200ms | 100 | 9.54 | 1.11 | 149 | 64.43% | 20.61 (18.96%) | -2.72 | 100% real ticks |
| optional_29_ytd_2026 | 100ms | 29 | 7.03 | 1.11 | 118 | 63.56% | 13.10 (39.41%) | -2.73 | 100% real ticks |

Hard gate rows passing individually: `1/4`.
Live package should only be created after all acceptance rows and stress rows are reviewed.

Raw JSON: `matrix_results.json`.
