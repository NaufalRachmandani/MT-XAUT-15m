# Suis BTC M5 V2 Verification

Validation uses `Exness-MT5Real25 / 184000633`, `BTCUSDc`, deposit `1000 USC`, `M5`, `Model=4`, `ExecutionMode=20`, `ExpertParameters=` empty.

| Variant | HQ | Net | Profit % | PF | Trades | WR | Bal DD Abs | Bal DD Max | Bal DD Rel | Eq DD Abs | Eq DD Max | Eq DD Rel | Max DD Any | Largest Loss | Max Cons Loss | Bars | Ticks |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | ---: | --- | --- | ---: | ---: | --- | ---: | ---: |
| V1 baseline | 100% real ticks | 8359.44 | 835.94% | 1.57 | 254 | 70.87% | 361.00 | 2 936.16000000 (39.03492212%) | 39.03492212% (2 936.16000000) | 369.76 | 3 366.05000000 (43.51549845%) | 43.51549845% (3 366.05000000) | 43.52% | -620.94 | 6 (-349.99000000) | 38294 | 12522820 |
| V2 previous baked | 100% real ticks | 10173.73 | 1017.37% | 2.00 | 193 | 74.09% | 199.79 | 1 506.80000000 (20.41576735%) | 20.41576735% (1 506.80000000) | 228.37 | 1 708.86000000 (23.15349627%) | 28.59578492% (598.77000000) | 28.60% | -623.38 | 3 (-1 303.33000000) | 38294 | 12522820 |
| V2 quantity baked | 100% real ticks | 14326.68 | 1432.67% | 2.09 | 266 | 74.44% | 200.07 | 876.67000000 (10.66812207%) | 20.00700000% (200.07000000) | 229.51 | 1 216.14000000 (13.09915544%) | 27.78681906% (671.01000000) | 27.79% | -620.94 | 6 (-676.21000000) | 38294 | 12522820 |

## Notes

- Current V2 is baked from `v2_qnty_r155_rr76_h17_zone`.
- Compared with the previous baked V2, net profit increased from `10173.73` to `14326.68` USC, trades increased from `193` to `266`, and Max DD Any decreased from `28.60%` to `27.79%`.
- `ExpertParameters=` remained empty in the verification run; defaults are inside the EX5.
