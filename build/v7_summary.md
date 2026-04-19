# v7 Summary

Window: `2026.01.01 - 2026.04.15`, `XAUUSDc`, `M15`, `Deposit 100 USD`, `Leverage 1:100`, `Every tick`.

## Goal

- Start from `base`, not from `v6`.
- Improve `2026-only` behavior.
- Target drawdown `< 15%`.
- Try to push profit toward `100%`.

## Baseline vs Champion

| Variant | Net Profit | Profit % | PF | Win Rate | Trades | EqDD |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| base recovered as v7 baseline | -84.67 | -84.67% | 0.79 | 37.04% | 54 | 95.97% |
| v7 seed after first structural patch | 1.91 | 1.91% | 1.19 | 45.65% | 46 | 5.42% |
| v7 final champion (`r180_manage`) | 28.11 | 28.11% | 1.79 | 60.56% | 71 | 9.08% |

## What Actually Worked

- Move from base sizing to risk-based sizing.
- Reduce trend stop from fixed `$25` to dynamic clamp `$12-$28`.
- Re-open trend hour `11`.
- Lower buy score gate from `75` to `70`.
- Enable pending manager.
- Enable breakeven manager.
- Raise trend risk to `1.80%` and sideways risk to `0.60%`.

## What Did Not Work Cleanly

- `market-only` trend execution: trade count and win rate rose, but expectancy collapsed.
- Removing high-score impulsive buy requirement: profit collapsed.
- Pushing risk to `2.00% / 0.70%`: profit stalled while PF deteriorated.
- Aggressive sell unlocks: no clean uplift.

## Key Diagnosis

- Base was not just “too risky”; it was also too rigid for `2026-only`.
- The biggest recoverable issue was buy path quality plus trade lifecycle management.
- Even after improvements, `v7` champion still earns most of its edge from the buy side.
- Target `100%` profit with `DD < 15%` was **not** reached on the current base-derived architecture.

## Champion Settings

- `V7_TrendRiskPercent = 1.80`
- `V7_SidewaysRiskPercent = 0.60`
- `IF1_SCORE_BUY_MIN_OVERRIDE = 70`
- `IF1TrendToxicHoursOverride = {3, 7, 8, 9, 10, 17}`
- `V7_ENABLE_PENDING_MANAGER = true`
- `V7_ENABLE_BREAKEVEN_MANAGER = true`
- `IF1_SIDEWAYS_ADX_THRESHOLD_OVERRIDE = 28`

## Supporting Files

- `build/v7_round1/summary.md`
- `build/v7_round2/summary.md`
- `build/v7_round3/summary.md`
- `build/v7_round4/summary.md`
- `build/v7_champion_analysis/analysis.md`
