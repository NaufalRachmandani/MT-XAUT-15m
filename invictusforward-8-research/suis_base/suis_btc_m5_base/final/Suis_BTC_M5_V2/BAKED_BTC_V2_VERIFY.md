# Suis BTC M5 V2 Verification

Validation uses `Exness-MT5Real25 / 184000633`, `BTCUSDc`, deposit `1000 USC`, `M5`, `Model=4`, `ExecutionMode=20`, `ExpertParameters=` empty.

| Variant | HQ | Net | Profit % | PF | Trades | WR | Bal DD Max | Eq DD Max | Max DD Any | Largest Loss | Max Cons Loss | Bars | Ticks |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| V1 baseline | 100% real ticks | 8359.44 | 835.94% | 1.57 | 254 | 70.87% | 2 936.16000000 (39.03492212%) | 3 366.05000000 (43.51549845%) | 43.52% | -620.94 | 6 (-349.99000000) | 38294 | 12522820 |
| V2 baked | 100% real ticks | 9667.00 | 966.70% | 1.97 | 192 | 74.48% | 1 534.05000000 (21.16447740%) | 1 750.53000000 (24.15113759%) | 29.28% | -623.38 | 3 (-1 303.33000000) | 38294 | 12522820 |

## Notes
- V2 is baked from `v2_block_h9_nozone_r155`.
- V2 blocks the loss-heavy hour 9 and disables the sell zone engine from V1.
- Queue variants increased trade count but were rejected because either profit fell below V1 or Max DD Any exceeded V1.
