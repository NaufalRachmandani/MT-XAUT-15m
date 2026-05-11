# InvictusForward-8 Research

Date: 2026-05-10

## Scope

Source from `/Users/naufalrachmandani/Downloads/InvictusForward-8.zip` was extracted into `source/original/InvictusForward-8`.

The tuned branch is separate: `source/tuned/InvictusForward-8-Tuned`. Original files were not edited.

## Main Findings

Baseline Forward-8 already works on 2026 YTD, but the risk profile was too uneven:

- $100 YTD was profitable, but equity drawdown was near 48%.
- Last month was negative.
- Worst YTD hours were server hours 05, 10, 11, and 04.
- Last week losses came mostly from range bounce at hour 05 and Drop Catcher at hour 10.
- Standard-account $29 is not robust because 0.01 lot with a roughly $25 SL can risk most of the account in one trade. Leverage 1:2000 helps margin, not stop-loss size.

## Tuned Changes

`InvictusForward-8-Tuned` keeps the core SMC breakout, range bounce, and Drop Catcher logic intact. The changes are guardrails:

- Blocks trending/range entries during weak server hours: 04, 05, 10, 11.
- Blocks Drop Catcher during its leak hours: 00, 01, 10, 23.
- Reduces low-balance max trending exposure from 5 to 3 positions.
- Makes max range entries per range/day an input.
- Keeps every tester run on `Model=4` real ticks and `Leverage=1:2000`.

## Backtest Results

All rows below use `XAUUSD`, `M15`, `Model=4`, local real ticks, `ExecutionMode=100`, and `Leverage=1:2000`.

| Case | Baseline Net | Baseline PF | Baseline Eq DD | Tuned Net | Tuned PF | Tuned Eq DD | Note |
| --- | ---: | ---: | --- | ---: | ---: | --- | --- |
| d100 last week | 3.25 | 1.02 | 113.32 (82.13%) | 116.94 | 3.57 | 70.26 (24.46%) | Strong improvement |
| d100 last month | -102.28 | 0.72 | 301.82 (100.76%) | 162.17 | 1.48 | 211.66 (70.66%) | Improved, still high DD |
| d100 YTD 2026 | 621.04 | 1.27 | 587.07 (47.75%) | 1242.07 | 1.73 | 384.19 (27.24%) | Best validation window |
| d29 last week | -29.34 | 0.15 | 67.31 (100.51%) | -30.65 | 0.08 | 68.62 (102.46%) | Standard $29 still unsafe |
| d29 YTD 2026 | 624.22 | 1.28 | 587.07 (50.54%) | 1050.19 | 1.65 | 407.48 (31.90%) | Improved YTD, but not safe |

Detailed tuned reports are in `backtests/tuned_realticks_lev2000`.

## Cent Native 2026 Compare

The current decision set is the native MT5 cent-account run in `backtests/cent_native_2026_lev2000_compare`. It uses account `184000633`, server `Exness-MT5Real25`, symbol `XAUUSDc`, currency `USC`, period `M15`, `Model=4`, `ExecutionMode=100`, and `Leverage=1:2000`.

No 2025 result is used in this comparison. All 12 reports show `100% real ticks`; both Base and Tuned compile logs show `0 errors, 0 warnings`.

| Deposit | Window | Base Net/PF/Eq DD | Tuned Net/PF/Eq DD | Winner |
| ---: | --- | --- | --- | --- |
| 1000 USC | 2026 YTD | 802.11 / 1.11 / 52.85% | 3024.49 / 1.58 / 32.88% | Tuned |
| 1000 USC | Last Month | -150.98 / 0.81 / 41.91% | 259.80 / 1.42 / 29.07% | Tuned |
| 1000 USC | Last Week | 22.70 / 1.11 / 14.65% | 254.28 / 6.11 / 9.67% | Tuned |
| 20000 USC | 2026 YTD | 16601.34 / 1.15 / 44.27% | 55063.84 / 1.75 / 21.68% | Tuned |
| 20000 USC | Last Month | -6209.76 / 0.67 / 53.58% | 4584.48 / 1.35 / 32.25% | Tuned |
| 20000 USC | Last Week | 729.10 / 1.17 / 14.69% | 5176.18 / 5.52 / 10.93% | Tuned |

Use the Tuned cent variant as the next baseline, but do not treat the 1000 USC profile as conservative live risk. Its 2026 YTD equity drawdown is still 32.88%, so a micro-risk cent profile is still the next practical hardening step.

## Recommendation

Use `InvictusForward-8-Tuned` as the next research baseline for cent-account tests.

Do not run the current standard XAUUSD profile on a $29 account. For very small capital, use a cent account or create a dedicated micro-risk profile that disables range bounce below a minimum balance and avoids fixed $25 SL exposure.
