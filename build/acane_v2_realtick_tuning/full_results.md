# full_results

Setup: `XAUUSD`, `M1`, deposit `$29`, leverage `1:2000`, `Model=4` real ticks, `ExecutionMode=50`.

| Variant | Case | Net | PF | Trades | WR | Eq DD | History | Note |
| --- | --- | ---: | ---: | ---: | ---: | --- | --- | --- |
| mrv_block_bad_rg | current_2025 | 2.96 | 4.22 | 18 | 77.78% | 1.20 (3.85%) | 70% real ticks | extreme MRV, leak hours blocked, regime must agree |
| mrv_block_bad_rg | lastweek_20260501 | 0.03 | 0.00 | 1 | 100.00% | 0.20 (0.69%) | 100% real ticks | extreme MRV, leak hours blocked, regime must agree |
| mrv_block_bad_rg | ytd_2026 | 1.61 | 8.32 | 5 | 80.00% | 0.91 (3.08%) | 100% real ticks | extreme MRV, leak hours blocked, regime must agree |
