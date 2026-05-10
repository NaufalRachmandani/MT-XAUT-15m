# quick_d29_delay100_partial

Setup: `XAUUSD`, `M1`, deposit `$29`, leverage `1:2000`, `Model=4` real ticks, `ExecutionMode=100`.

| Variant | Case | Net | PF | Trades | WR | Eq DD | Delay | History | Note |
| --- | --- | ---: | ---: | ---: | ---: | --- | ---: | --- | --- |
| r33_sell_rjt_10_only | friday_20260508 | 0.00 | 0.00 | 0 | 0.00% | 0.00 (0.00%) | 100 | 100% real ticks | sell-only RJT in YTD-positive hour 10 |
| r34_sell_rjt_10_12 | friday_20260508 | 0.00 | 0.00 | 0 | 0.00% | 0.00 (0.00%) | 100 | 100% real ticks | sell-only RJT in YTD-best hours 10-11 |
| r35_sell_rjt_10_only_tp | friday_20260508 | 0.00 | 0.00 | 0 | 0.00% | 0.00 (0.00%) | 100 | 100% real ticks | hour-10 RJT with larger target |
| r36_sell_rjt_10_12_tp | friday_20260508 | 0.00 | 0.00 | 0 | 0.00% | 0.00 (0.00%) | 100 | 100% real ticks | hours 10-11 RJT with larger target |
| r34_sell_rjt_10_12 | lastweek_20260501 | -0.20 | 0.94 | 6 | 50.00% | 2.31 (7.97%) | 100 | 100% real ticks | sell-only RJT in YTD-best hours 10-11 |
| r36_sell_rjt_10_12_tp | lastweek_20260501 | -1.48 | 0.66 | 6 | 50.00% | 2.71 (9.34%) | 100 | 100% real ticks | hours 10-11 RJT with larger target |
| r33_sell_rjt_10_only | lastweek_20260501 | -2.11 | 0.00 | 2 | 0.00% | 2.11 (7.28%) | 100 | 100% real ticks | sell-only RJT in YTD-positive hour 10 |
| r35_sell_rjt_10_only_tp | lastweek_20260501 | -2.51 | 0.00 | 2 | 0.00% | 2.51 (8.66%) | 100 | 100% real ticks | hour-10 RJT with larger target |
| r36_sell_rjt_10_12_tp | ytd_2026 | 4.99 | 1.07 | 140 | 62.86% | 21.88 (47.81%) | 100 | 100% real ticks | hours 10-11 RJT with larger target |
| r34_sell_rjt_10_12 | ytd_2026 | 4.80 | 1.08 | 123 | 60.98% | 16.03 (41.57%) | 100 | 100% real ticks | sell-only RJT in YTD-best hours 10-11 |
| r33_sell_rjt_10_only | ytd_2026 | -2.47 | 0.92 | 58 | 56.90% | 7.55 (22.15%) | 100 | 100% real ticks | sell-only RJT in YTD-positive hour 10 |
| r35_sell_rjt_10_only_tp | ytd_2026 | -5.41 | 0.85 | 68 | 57.35% | 10.76 (31.32%) | 100 | 100% real ticks | hour-10 RJT with larger target |
