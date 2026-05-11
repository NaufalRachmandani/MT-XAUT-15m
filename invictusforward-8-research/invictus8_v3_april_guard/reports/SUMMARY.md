# Invictus Forward-8 V3 April Guard

V3 is an April-failure guard experiment, not a live deployment package.

Selected diagnostic variant: `Pending fill-hour guard only` (`pending_guard_only`).
Relative gate passed: `True`.
Strict live candidate: `False`.
Forward-demo set: `sets/InvictusForward8_V3Guard_selected_forward_demo_only.set`.

## Decision

V3 improved the relative April/V1 gate, but it is not yet a strict live candidate.

This is the first variant in this research run that materially fixes April. Treat it as a forward-demo candidate only, not a live local deployment while the VPS is already trading.

## Baseline Validation

| Variant/Expert | Window | Net | PF | Trades | Win Rate | Eq DD | Largest Loss | Max Consecutive Losses | History |
| --- | --- | ---: | ---: | ---: | ---: | --- | ---: | --- | --- |
| V1 | Validate Mar | 862.80 | 3.31 | 47 | 80.85% | 159.40000000 (12.64477233%) | -67.60 | 3 (-91.60000000) | 100% real ticks |
| V1 | Validate Apr | -180.67 | 0.72 | 47 | 51.06% | 356.74900000 (30.85847257%) | -50.00 | 5 (-216.40000000) | 100% real ticks |
| V1 | Validate May | 254.28 | 6.11 | 14 | 92.86% | 134.30000000 (9.67174264%) | -49.80 | 1 (-49.80000000) | 100% real ticks |
| V2Live | Validate Mar | 818.80 | 3.64 | 42 | 83.33% | 145.00000000 (11.06701267%) | -67.60 | 2 (-70.90000000) | 100% real ticks |
| V2Live | Validate Apr | -169.60 | 0.71 | 40 | 47.50% | 300.24900000 (27.03360462%) | -50.00 | 7 (-195.86980000) | 100% real ticks |
| V2Live | Validate May | 301.28 | 0.00 | 12 | 100.00% | 82.00000000 (6.29567628%) | 0.00 | 0 (0.00000000) | 100% real ticks |

## V3 Validation

| Variant/Expert | Window | Net | PF | Trades | Win Rate | Eq DD | Largest Loss | Max Consecutive Losses | History |
| --- | --- | ---: | ---: | ---: | ---: | --- | ---: | --- | --- |
| Trend only, V2 rules | Validate Mar | 482.70 | 2.95 | 32 | 84.38% | 145.00000000 (12.96958855%) | -65.50 | 1 (-65.50000000) | 100% real ticks |
| Trend only, V2 rules | Validate Apr | -166.13 | 0.68 | 32 | 46.88% | 306.84900000 (26.89957087%) | -50.00 | 5 (-156.80000000) | 100% real ticks |
| Trend only, V2 rules | Validate May | 293.48 | 0.00 | 11 | 100.00% | 82.00000000 (6.33360552%) | 0.00 | 0 (0.00000000) | 100% real ticks |
| RangeBounce only | Validate Mar | 129.00 | 7.26 | 6 | 83.33% | 28.90000000 (2.63493800%) | -20.60 | 1 (-20.60000000) | 100% real ticks |
| RangeBounce only | Validate Apr | -30.07 | 0.39 | 5 | 40.00% | 71.26980000 (7.03274127%) | -20.80 | 2 (-39.06980000) | 100% real ticks |
| RangeBounce only | Validate May | 7.80 | 0.00 | 1 | 100.00% | 8.90000000 (0.87538114%) | 0.00 | 0 (0.00000000) | 100% real ticks |
| DropCatcher only | Validate Mar | 112.70 | 6.93 | 4 | 75.00% | 64.80000000 (5.68321347%) | -19.00 | 1 (-19.00000000) | 100% real ticks |
| DropCatcher only | Validate Apr | 26.60 | 2.41 | 3 | 66.67% | 46.30000000 (4.55753519%) | -18.90 | 1 (-18.90000000) | 100% real ticks |
| DropCatcher only | Validate May | 0.00 | 0.00 | 0 | 0.00% | 0.00000000 (0.00000000%) | 0.00 | 0 (0.00000000) | 100% real ticks |
| Pending fill-hour guard only | Validate Mar | 683.90 | 3.80 | 37 | 83.78% | 145.00000000 (11.06701267%) | -67.60 | 2 (-70.90000000) | 100% real ticks |
| Pending fill-hour guard only | Validate Apr | 334.15 | 2.04 | 39 | 74.36% | 143.50000000 (11.37669055%) | -50.00 | 3 (-63.86980000) | 100% real ticks |
| Pending fill-hour guard only | Validate May | 271.20 | 0.00 | 11 | 100.00% | 82.00000000 (6.44451430%) | 0.00 | 0 (0.00000000) | 100% real ticks |
| Trend score +10 only | Validate Mar | 248.10 | 2.15 | 23 | 73.91% | 151.10000000 (12.10155374%) | -50.30 | 3 (-101.20000000) | 100% real ticks |
| Trend score +10 only | Validate Apr | -80.14 | 0.58 | 18 | 55.56% | 104.06980000 (10.40281887%) | -48.90 | 3 (-87.96980000) | 100% real ticks |
| Trend score +10 only | Validate May | 139.50 | 3.80 | 7 | 85.71% | 85.80000000 (7.00236677%) | -49.80 | 1 (-49.80000000) | 100% real ticks |
| V3 default April guard | Validate Mar | 291.70 | 2.69 | 22 | 77.27% | 151.10000000 (12.10155374%) | -50.30 | 3 (-101.20000000) | 100% real ticks |
| V3 default April guard | Validate Apr | -90.64 | 0.45 | 14 | 50.00% | 126.76980000 (12.67191124%) | -48.90 | 3 (-87.96980000) | 100% real ticks |
| V3 default April guard | Validate May | 63.60 | 2.28 | 5 | 80.00% | 85.80000000 (7.46476422%) | -49.80 | 1 (-49.80000000) | 100% real ticks |
| V3 default + IMP only | Validate Mar | 291.70 | 2.69 | 22 | 77.27% | 151.10000000 (12.10155374%) | -50.30 | 3 (-101.20000000) | 100% real ticks |
| V3 default + IMP only | Validate Apr | -90.64 | 0.45 | 14 | 50.00% | 126.76980000 (12.67191124%) | -48.90 | 3 (-87.96980000) | 100% real ticks |
| V3 default + IMP only | Validate May | 63.60 | 2.28 | 5 | 80.00% | 85.80000000 (7.46476422%) | -49.80 | 1 (-49.80000000) | 100% real ticks |
| V3 micro-risk | Validate Mar | 250.80 | 3.37 | 18 | 72.22% | 109.90000000 (9.03262924%) | -25.10 | 3 (-60.00000000) | 100% real ticks |
| V3 micro-risk | Validate Apr | -66.24 | 0.53 | 14 | 50.00% | 102.06980000 (10.20595940%) | -24.50 | 3 (-63.56980000) | 100% real ticks |
| V3 micro-risk | Validate May | 48.50 | 2.95 | 4 | 75.00% | 42.90000000 (3.93073117%) | -24.90 | 1 (-24.90000000) | 100% real ticks |

## Selected Variant Final Checks

| Variant/Expert | Window | Net | PF | Trades | Win Rate | Eq DD | Largest Loss | Max Consecutive Losses | History |
| --- | --- | ---: | ---: | ---: | ---: | --- | ---: | --- | --- |
| Pending fill-hour guard only | Train Jan-Apr | 2209.48 | 2.38 | 145 | 78.62% | 387.20000000 (12.72728325%) | -124.90 | 3 (-138.26980000) | 100% real ticks |
| Pending fill-hour guard only | OOS May | 271.20 | 0.00 | 11 | 100.00% | 82.00000000 (6.44451430%) | 0.00 | 0 (0.00000000) | 100% real ticks |
| Pending fill-hour guard only | Last Month | 598.82 | 4.41 | 35 | 85.71% | 143.50000000 (12.50849008%) | -50.00 | 2 (-68.90000000) | 100% real ticks |
| Pending fill-hour guard only | 2026 YTD | 3291.08 | 3.06 | 158 | 80.38% | 387.20000000 (12.72728325%) | -124.90 | 3 (-138.26980000) | 100% real ticks |
| Pending fill-hour guard only | Train Jan-Apr | 17988.92 | 2.00 | 180 | 78.89% | 3 358.60000000 (8.71558552%) | -630.40 | 6 (-2 656.82820000) | 100% real ticks |
| Pending fill-hour guard only | OOS May | 2713.20 | 5.36 | 13 | 92.31% | 1 656.70000000 (6.79814033%) | -622.10 | 1 (-622.10000000) | 100% real ticks |
| Pending fill-hour guard only | Last Month | 5525.97 | 2.25 | 47 | 80.85% | 3 422.50000000 (15.09683811%) | -626.40 | 2 (-1 249.30000000) | 100% real ticks |
| Pending fill-hour guard only | 2026 YTD | 21519.72 | 2.16 | 195 | 80.00% | 3 358.60000000 (8.71558552%) | -630.40 | 6 (-2 656.82820000) | 100% real ticks |

## Safety Note

All generated tester configs use `AllowLiveTrading=0`, `Visual=0`, and `ShutdownTerminal=1`. Do not attach these research builds to a live local chart while VPS trading is active.
