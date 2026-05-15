# Suis BTC M5 V2 Frontier

Cent account validation: `Exness-MT5Real25 / 184000633`, `BTCUSDc`, deposit `1000 USC`, `M5`, `Model=4`, `ExecutionMode=20`, `ExpertParameters=` empty.

## Baked Champion

| Variant | HQ | Net | Profit % | PF | Trades | WR | Bal DD Abs | Bal DD Max | Bal DD Rel | Eq DD Abs | Eq DD Max | Eq DD Rel | Max DD Any | Largest Loss | Max Cons Loss | Bars | Ticks |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | ---: | --- | --- | ---: | ---: | --- | ---: | ---: |
| v2_qnty_r155_rr76_h17_zone | 100% real ticks | 14326.68 | 1432.67% | 2.09 | 266 | 74.44% | 200.07 | 876.67000000 (10.66812207%) | 20.00700000% (200.07000000) | 229.51 | 1 216.14000000 (13.09915544%) | 27.78681906% (671.01000000) | 27.79% | -620.94 | 6 (-676.21000000) | 38294 | 12522820 |

## Relevant Frontier

| Variant | Net | Profit % | PF | Trades | WR | Max DD Any | Largest Loss | Verdict |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| v2_queue_push_nozone_r34 | 16629.42 | 1662.94% | 1.57 | 493 | 71.60% | 62.18% | -956.39 | More profit, rejected for DD. |
| v2_queue_push_nozone_r40 | 15707.46 | 1570.75% | 1.52 | 504 | 72.02% | 67.12% | -956.39 | More trades, rejected for DD. |
| v2_qnty_r155_rr76_h17_zone | 14326.68 | 1432.67% | 2.09 | 266 | 74.44% | 27.79% | -620.94 | Baked champion. |
| v2_qnty_r15_rr78_h17_zone | 13928.60 | 1392.86% | 2.08 | 265 | 74.72% | 27.28% | -620.94 | Slightly lower DD, lower net. |
| v2_qnty_r145_rr76_h17_zone | 13756.90 | 1375.69% | 2.08 | 261 | 73.95% | 26.76% | -620.94 | Lower DD, lower net. |
| v2_mt5opt_r15_rr76_score42 | 10173.73 | 1017.37% | 2.00 | 193 | 74.09% | 28.60% | -623.38 | Previous baked V2. |
| v2_queue_h5_6_15_16_17_nozone_r16_peak35 | 3100.88 | 310.09% | 1.29 | 552 | 72.28% | 27.00% | -256.99 | High quantity, profit quality too low. |

## Notes

- The accepted upgrade was not a full queue/flood approach. Queue variants created far more trades but collapsed PF and net profit.
- The clean improvement came from allowing sell hour `17`, enabling zone retest, and moving risk from `15.0` to `15.5`.
- Final baked EX5 was rerun as a normal native backtest, not as an optimization row.
