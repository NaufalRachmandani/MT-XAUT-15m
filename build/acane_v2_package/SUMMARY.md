# AcaneM1 v2.10 Summary

Final build: `AcaneM1_v2`
Profile: real-tick filtered MRV scalper for `XAUUSD,M1`.

This package is tuned against the stricter tester setup:

- Account/server: `265874264` / `Exness-MT5Real38`
- Deposit: `$29`
- Leverage: `1:2000`
- Model: `4` / every tick based on real ticks
- Execution delay: `50ms`

Core changes versus the previous v2:

- MRV entries are only allowed on stronger extremes: RSI `30/70`, Bollinger deviation `2.25`, band overshoot `0.28 ATR`.
- MRV entries must agree with the detected M1/M5 regime.
- Blocked entry hours: `1,2,3,16,17,23`.
- Max positions remain capped at `2`, same-side positions at `1`.
- Daily loss guard remains `10%`; account circuit remains `12%`.
- Status/debug spam is disabled for VPS use.

## Final Validation

All rows below use `Model=4` real ticks and `ExecutionMode=50`.

| Window | Net | PF | Trades | Win Rate | Eq DD | History |
| --- | ---: | ---: | ---: | ---: | --- | --- |
| 2026.05.08-2026.05.09 | 0.00 | 0.00 | 0 | 0.00% | 0.00 (0.00%) | 100% real ticks |
| 2026.05.01-2026.05.09 | 0.03 | 0.00 | 1 | 100.00% | 0.20 (0.69%) | 100% real ticks |
| 2026.01.01-2026.05.09 | 1.61 | 8.32 | 5 | 80.00% | 0.91 (3.08%) | 100% real ticks |
| 2025.01.01-2026.05.09 | 2.96 | 4.22 | 18 | 77.78% | 1.20 (3.85%) | 70% real ticks |

Context only: the 2023-current test is positive (`+3.48`, PF `4.03`, 21 trades), but history quality is only `28% real ticks`, so it should not be used as the main proof.

Decision: use `AcaneM1_v2.ex5` only if accepting lower frequency while forward-testing. This version intentionally avoids the Friday 2026.05.08 overtrading pattern from the previous EA.
