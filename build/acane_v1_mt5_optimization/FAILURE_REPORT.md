# AcaneM1_v1 Rebuild Failure Report

Date: 2026-05-10

Setup used for acceptance:
- Expert: `AcaneLab\AcaneM1_v1.ex5`
- Symbol/TF: `XAUUSD`, `M1`
- Account/server: `265874264`, `Exness-MT5Real38`
- Deposit/leverage: `$100`, `1:2000`
- Model/delay: `Model=4` real ticks, `ExecutionMode=100ms`

Final default candidate:
- Hour preset: server hour `5` only
- Main engine: impulse continuation, with H1 trend guard
- Daily guard: `5%` / `$5`
- Stop profile: `MinSL=0.65`, `MaxSL=2.00`, `ATRStop=0.70`, `ImpulseRR=0.95`

Acceptance matrix:

| Case | Result | Gate |
| --- | ---: | --- |
| Last week 2026.05.01-2026.05.10 | `-0.21`, PF `0.97`, EqDD `4.26%`, 10 trades | Fail: not positive |
| Last month 2026.04.10-2026.05.10 | `-2.45`, PF `0.75`, EqDD `4.35%`, 14 trades | Fail: negative |
| 2026 YTD | `+12.91`, PF `1.15`, EqDD `16.95%`, 149 trades | Pass |
| 2025-current | `+4.12`, PF `1.02`, EqDD `35.09%`, 563 trades, history quality `70% real ticks` | Fail: DD too high |
| Last month stress delay 200ms | `-2.92`, PF `0.72`, EqDD `4.71%` | Fail: negative |
| YTD stress delay 200ms | `+9.54`, PF `1.11`, EqDD `18.96%` | Pass |

Decision:
- Do not package to live `MQL5/Experts/Acane`.
- Do not remove the current live `AcaneM1_v2.ex5`.
- Continue optimization only from the native MT5 runner or another strategy redesign. The current rebuilt source compiles and is suitable for optimization, but the default candidate is not live-ready.

Main technical reasons:
- The high-frequency variants produced unacceptable drawdown at `$100`.
- The safer hour-5-only variant can pass YTD drawdown but fails recent month and 2025-current stability.
- The drawdown is dominated by clustered impulse losses during one server-hour window; daily guard and tighter stops reduce DD but also remove enough edge to make recent windows negative.
