# quick_results

Setup: `XAUUSD`, `M1`, deposit `$29`, leverage `1:2000`, `Model=4` real ticks, `ExecutionMode=50`.

| Variant | Case | Net | PF | Trades | WR | Eq DD | History | Note |
| --- | --- | ---: | ---: | ---: | ---: | --- | --- | --- |
| mrv_block_bad_s82_touch18 | lastweek_20260501 | 0.03 | 0.00 | 1 | 100.00% | 0.20 (0.69%) | 100% real ticks | extreme score with less band overshoot requirement |
| mrv_block_bad_rg | lastweek_20260501 | 0.03 | 0.00 | 1 | 100.00% | 0.20 (0.69%) | 100% real ticks | extreme MRV, leak hours blocked, regime must agree |
| mrv_block_bad_s78 | lastweek_20260501 | -0.27 | 0.00 | 1 | 0.00% | 0.27 (0.93%) | 100% real ticks | between strict and extreme MRV with leak hours blocked |
| mrv_block_bad_rg_s78 | lastweek_20260501 | -0.27 | 0.00 | 1 | 0.00% | 0.27 (0.93%) | 100% real ticks | moderately strict MRV, leak hours blocked, regime must agree |
| mrv_block_bad_s74 | lastweek_20260501 | -1.92 | 0.29 | 8 | 25.00% | 2.92 (9.83%) | 100% real ticks | strict MRV with leak hours blocked |
| mrv_block_bad_s70 | lastweek_20260501 | -3.08 | 0.19 | 9 | 11.11% | 3.57 (12.11%) | 100% real ticks | moderate MRV with leak hours blocked |
| mrv_block_bad_base | lastweek_20260501 | -3.12 | 0.59 | 25 | 32.00% | 3.57 (12.12%) | 100% real ticks | current MRV with audited leak hours blocked |
| mrv_block_bad_rg | ytd_2026 | 1.61 | 8.32 | 5 | 80.00% | 0.91 (3.08%) | 100% real ticks | extreme MRV, leak hours blocked, regime must agree |
| mrv_block_bad_s70 | ytd_2026 | -3.26 | 0.19 | 16 | 31.25% | 3.50 (11.97%) | 100% real ticks | moderate MRV with leak hours blocked |
| mrv_block_bad_rg_s78 | ytd_2026 | -3.38 | 0.01 | 7 | 14.29% | 3.38 (11.66%) | 100% real ticks | moderately strict MRV, leak hours blocked, regime must agree |
| mrv_block_bad_s78 | ytd_2026 | -3.43 | 0.01 | 8 | 12.50% | 3.43 (11.83%) | 100% real ticks | between strict and extreme MRV with leak hours blocked |
| mrv_block_bad_s74 | ytd_2026 | -3.49 | 0.34 | 18 | 27.78% | 3.49 (12.03%) | 100% real ticks | strict MRV with leak hours blocked |
| mrv_block_bad_base | ytd_2026 | -3.56 | 0.39 | 26 | 42.31% | 3.56 (12.28%) | 100% real ticks | current MRV with audited leak hours blocked |
| mrv_block_bad_s82_touch18 | ytd_2026 | -3.79 | 0.18 | 11 | 36.36% | 3.79 (13.07%) | 100% real ticks | extreme score with less band overshoot requirement |
