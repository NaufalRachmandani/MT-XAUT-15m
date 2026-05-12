# Invictus Forward-8 V5 Quality Boost

V5 is a quality-scaled profit experiment based on V4. It uses only native MT5 cent `XAUUSDc` 2026 real-tick confirmation in this run.

Safety: all generated native MT5 configs use `AllowLiveTrading=0`, `Visual=0`, and `ShutdownTerminal=1`.

Selected research variant: `v5_max_profit_scaled`.

## Results

| Account | Variant | Window | Deposit | Net | PF | Trades | WR | Eq DD | Largest Loss | History | Validation |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- | ---: | --- | --- |
| Cent confirmation | V3 reference | Cent Last Month | 1000 USC | 598.82 | 4.41 | 35 | 85.71% | 143.50000000 (12.50849008%) | -50.00 | 100% real ticks | OK |
| Cent confirmation | V3 reference | Cent 2026 YTD | 1000 USC | 3291.08 | 3.06 | 158 | 80.38% | 387.20000000 (12.72728325%) | -124.90 | 100% real ticks | OK |
| Cent confirmation | V5 high-profit scaled | Cent Last Month | 1000 USC | 2337.20 | 6.98 | 38 | 86.84% | 492.40000000 (14.72443125%) | -162.00 | 100% real ticks | OK |
| Cent confirmation | V5 high-profit scaled | Cent OOS May | 1000 USC | 795.80 | 0.00 | 11 | 100.00% | 246.20000000 (13.68157822%) | 0.00 | 100% real ticks | OK |
| Cent confirmation | V5 high-profit scaled | Cent Validate Apr | 1000 USC | 790.49 | 2.00 | 40 | 75.00% | 512.50000000 (31.09089424%) | -185.20 | 100% real ticks | OK |
| Cent confirmation | V5 high-profit scaled | Cent Validate Mar | 1000 USC | 1649.50 | 2.77 | 38 | 84.21% | 579.80000000 (38.35924578%) | -270.30 | 100% real ticks | OK |
| Cent confirmation | V5 high-profit scaled | Cent 2026 YTD | 1000 USC | 18771.29 | 2.55 | 169 | 81.07% | 7 265.80000000 (26.87345441%) | -3110.40 | 100% real ticks | OK |
| Cent confirmation | V5 leak-block scaled | Cent Last Month | 1000 USC | 947.78 | 3.50 | 27 | 85.19% | 471.80000000 (19.49924227%) | -273.70 | 100% real ticks | OK |
| Cent confirmation | V5 leak-block scaled | Cent 2026 YTD | 1000 USC | 4879.31 | 2.29 | 138 | 79.71% | 1 415.50000000 (19.40421719%) | -821.10 | 100% real ticks | OK |
| Cent confirmation | V5 max-profit scaled | Cent Last Month | 1000 USC | 2562.40 | 8.01 | 38 | 86.84% | 492.40000000 (13.79541434%) | -162.00 | 100% real ticks | OK |
| Cent confirmation | V5 max-profit scaled | Cent OOS May | 1000 USC | 1022.00 | 0.00 | 11 | 100.00% | 287.20000000 (14.30920233%) | 0.00 | 100% real ticks | OK |
| Cent confirmation | V5 max-profit scaled | Cent Validate Apr | 1000 USC | 819.39 | 2.06 | 40 | 75.00% | 512.50000000 (30.27183935%) | -185.20 | 100% real ticks | OK |
| Cent confirmation | V5 max-profit scaled | Cent Validate Mar | 1000 USC | 1651.90 | 2.53 | 38 | 84.21% | 652.40000000 (42.42700137%) | -315.40 | 100% real ticks | OK |
| Cent confirmation | V5 max-profit scaled | Cent 2026 YTD | 1000 USC | 19839.91 | 2.52 | 169 | 81.07% | 8 347.10000000 (28.59868081%) | -3732.50 | 100% real ticks | OK |
| Cent confirmation | V5 mid-profit scaled | Cent Last Month | 1000 USC | 1751.54 | 6.95 | 37 | 86.49% | 296.80000000 (22.53877763%) | -115.70 | 100% real ticks | OK |
| Cent confirmation | V5 mid-profit scaled | Cent 2026 YTD | 1000 USC | 13095.74 | 3.24 | 166 | 81.33% | 1 689.00000000 (24.79177915%) | -555.40 | 100% real ticks | OK |
| Cent confirmation | V5 profit-scaled | Cent Last Month | 1000 USC | 1459.98 | 7.59 | 37 | 86.49% | 246.20000000 (9.99317607%) | -92.50 | 100% real ticks | OK |
| Cent confirmation | V5 profit-scaled | Cent OOS May | 1000 USC | 562.90 | 0.00 | 11 | 100.00% | 164.20000000 (10.49134241%) | 0.00 | 100% real ticks | OK |
| Cent confirmation | V5 profit-scaled | Cent Validate Apr | 1000 USC | 588.67 | 2.26 | 40 | 75.00% | 273.60000000 (18.97007208%) | -97.90 | 100% real ticks | OK |
| Cent confirmation | V5 profit-scaled | Cent Validate Mar | 1000 USC | 1034.90 | 2.80 | 37 | 83.78% | 362.60000000 (26.28107560%) | -148.30 | 100% real ticks | OK |
| Cent confirmation | V5 profit-scaled | Cent 2026 YTD | 1000 USC | 9701.49 | 3.10 | 165 | 81.21% | 1 244.10000000 (22.14138695%) | -416.50 | 100% real ticks | OK |
| Cent confirmation | V5 quality-scaled | Cent Last Month | 1000 USC | 1071.88 | 6.40 | 35 | 85.71% | 188.50000000 (15.74663440%) | -69.50 | 100% real ticks | OK |
| Cent confirmation | V5 quality-scaled | Cent 2026 YTD | 1000 USC | 6045.18 | 3.04 | 165 | 81.21% | 738.70000000 (17.63101501%) | -254.50 | 100% real ticks | OK |
| Cent confirmation | V5 strong-RR scaled | Cent Last Month | 1000 USC | 1059.68 | 6.34 | 35 | 85.71% | 188.50000000 (15.74663440%) | -69.50 | 100% real ticks | OK |
| Cent confirmation | V5 strong-RR scaled | Cent 2026 YTD | 1000 USC | 5697.38 | 2.95 | 163 | 80.98% | 710.00000000 (17.66267661%) | -244.70 | 100% real ticks | OK |

## Variant Scores

| Variant | Gate | Score | Cent YTD Net/PF/DD% | Cent Last Month Net/PF/DD% | Fail Reasons |
| --- | --- | ---: | --- | --- | --- |
| V5 max-profit scaled | True | 22697.68 | 19839.9106 / 2.52 / 28.59868081 | 2562.402 / 8.01 / 13.79541434 |  |
| V5 high-profit scaled | True | 21297.89 | 18771.2898 / 2.55 / 26.87345441 | 2337.202 / 6.98 / 14.72443125 |  |
| V5 mid-profit scaled | False | 14551.06 | 13095.7422 / 3.24 / 24.79177915 | 1751.5416 / 6.95 / 22.53877763 | oos_may: cent confirmation not tested; validate_apr: cent confirmation not tested; validate_mar: cent confirmation not tested |
| V5 profit-scaled | True | 11148.84 | 9701.4892 / 3.1 / 22.14138695 | 1459.9812 / 7.59 / 9.99317607 |  |
| V5 quality-scaled | False | 6827.98 | 6045.1758 / 3.04 / 17.63101501 | 1071.8812 / 6.4 / 15.7466344 | oos_may: cent confirmation not tested; validate_apr: cent confirmation not tested; validate_mar: cent confirmation not tested |
| V5 strong-RR scaled | False | 6461.25 | 5697.3758 / 2.95 / 17.66267661 | 1059.6812 / 6.34 / 15.7466344 | oos_may: cent confirmation not tested; validate_apr: cent confirmation not tested; validate_mar: cent confirmation not tested |
| V5 leak-block scaled | False | 5327.92 | 4879.306 / 2.29 / 19.40421719 | 947.7812 / 3.5 / 19.49924227 | oos_may: cent confirmation not tested; validate_apr: cent confirmation not tested; validate_mar: cent confirmation not tested |

## Decision

`v5_max_profit_scaled` is the selected **profit research candidate**. It beats V4 lot +100% on 2026 YTD net profit while keeping YTD equity DD roughly flat, but it is **not live-ready** for 1000 USC because validation DD worsens in Mar/Apr/May and largest YTD loss is much larger than V4.

`v5_profit_scaled` is the safer V5 candidate. It gives lower profit than V4, but materially reduces YTD DD and largest loss.

Use V5 files for manual/native backtest research only, not live deployment.
