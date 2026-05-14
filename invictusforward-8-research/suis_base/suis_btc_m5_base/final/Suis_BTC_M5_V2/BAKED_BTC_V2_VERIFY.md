# Suis BTC M5 V2 Verification

Validation uses `Exness-MT5Real25 / 184000633`, `BTCUSDc`, deposit `1000 USC`, `M5`, `Model=4`, `ExecutionMode=20`, `ExpertParameters=` empty.

| Variant | HQ | Net | Profit % | PF | Trades | WR | Bal DD Max | Eq DD Max | Max DD Any | Largest Loss | Max Cons Loss | Bars | Ticks |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| V1 baseline | 100% real ticks | 8359.44 | 835.94% | 1.57 | 254 | 70.87% | 2 936.16000000 (39.03492212%) | 3 366.05000000 (43.51549845%) | 43.52% | -620.94 | 6 (-349.99000000) | 38294 | 12522820 |
| V2 previous baked | 100% real ticks | 9667.00 | 966.70% | 1.97 | 192 | 74.48% | 1 534.05000000 (21.16447740%) | 1 750.53000000 (24.15113759%) | 29.28% | -623.38 | 3 (-1 303.33000000) | 38294 | 12522820 |
| V2 MT5-opt baked | 100% real ticks | 10173.73 | 1017.37% | 2.00 | 193 | 74.09% | 1 506.80000000 (20.41576735%) | 1 708.86000000 (23.15349627%) | 28.60% | -623.38 | 3 (-1 303.33000000) | 38294 | 12522820 |

## Notes
- Current V2 is baked from `v2_mt5opt_r15_rr76_score42` after native MT5 optimization and normal no-set rerun.
- Compared with the previous V2 baked build, net profit increased from `9667.00` to `10173.73` USC while Max DD Any decreased from `29.28%` to `28.60%`.
- `ExpertParameters=` remained empty in the verification run; defaults are inside the EX5.
