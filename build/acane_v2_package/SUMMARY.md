# AcaneM1 v2 Summary

Final build: `AcaneM1_v2`
Profile: balanced aggressive MRV with anti-stack controls.

Core changes versus `AcaneM1_v1_guarded_debug`:
- `MaxPositions`: `12` -> `2`
- `MaxSameSidePositions`: `4` -> `1`
- `MinSecondsBetweenEntries`: `3` -> `60`
- `DailyMaxLossPct`: `15` -> `10`
- `AccountCircuit`: `15` -> `12`
- `MaxOpenRiskPct`: `12` -> `8`
- `BasketLossStopPct`: `9` -> `6`
- `FastLossCooldownAfter`: `2` -> `1`
- `FastLossCooldownSeconds`: `900` -> `1800`
- `BlockEntryHours`: `2,5,11,20`
- Min-lot fallback enabled with max min-lot risk `7%`

## Final smoke tests

| Window | Deposit | Net | Trades | W/L | Win Rate | PF | Equity DD |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 2026.05.01 - 2026.05.09 | 50 | 45.19 | 91 | 69/20 | 75.82% | 6.35 | 2.84 (4.87%) |
| 2026.05.01 - 2026.05.09 | 200 | 111.90 | 54 | 42/12 | 77.78% | 5.36 | 14.08 (6.73%) |

## Leverage re-check

The initial package smoke tests were generated while MT5 reported `1:100` leverage. A follow-up run forced/reported `1:2000`, matching the live account setting.

| Window | Deposit | Report Leverage | Net | Trades | W/L | Win Rate | PF | Equity DD |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | --- |
| 2026.05.01 - 2026.05.09 | 29 | 1:2000 | 58.85 | 157 | 110/45 | 70.06% | 3.67 | 4.83 (5.76%) |
| 2026.05.01 - 2026.05.09 | 50 | 1:2000 | 88.75 | 163 | 114/47 | 69.94% | 3.44 | 6.83 (5.30%) |
| 2026.05.01 - 2026.05.09 | 100 | 1:2000 | 220.39 | 163 | 116/47 | 71.17% | 3.61 | 16.33 (5.54%) |
| 2026.01.01 - 2026.05.09 | 29 | 1:2000 | 13,623,408.54 | 2,438 | 1,843/595 | 75.59% | 4.63 | 92,820.00 (2.17%) |

## Validation backtests

| Variant | Window | Deposit | Net | Trades | W/L | Win Rate | PF | Equity DD |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| v1 current debug | 2026.01.01 - 2026.05.09 | 200 | 6,594,331.85 | 3,757 | 2,213/1,544 | 58.90% | 1.62 | 406,700.00 (8.90%) |
| v2 balanced fast | 2026.01.01 - 2026.05.09 | 200 | 7,618,728.94 | 1,588 | 1,228/360 | 77.33% | 4.74 | 67,460.00 (1.01%) |
| v2 stack2 no-hour | 2026.01.01 - 2026.05.09 | 200 | 10,465,095.53 | 1,854 | 1,422/432 | 76.70% | 4.49 | 80,820.00 (0.84%) |

Decision: use `v2 balanced fast`. The no-hour variant had higher YTD profit, but it reopens hours that previously appeared in the leak map. The final v2 is a better first VPS candidate because it keeps high profit while reducing repeated same-side loss clusters.

Practical note: `$29` is possible if the live account is truly `1:2000`, but it is still a very small buffer. Top-up to `$100` is not required just to open positions, but it gives more room for slippage, spread spikes, and VPS/live execution differences.
