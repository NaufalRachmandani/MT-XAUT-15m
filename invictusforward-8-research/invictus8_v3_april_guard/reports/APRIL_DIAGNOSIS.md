# April Failure Diagnosis

Source of truth: native MT5 Strategy Tester `.htm` reports. Local runs use `AllowLiveTrading=0`; this experiment does not enable live Algo Trading.

## April Validation Table

| Variant/Expert | Window | Net | PF | Trades | Win Rate | Eq DD | Largest Loss | Max Consecutive Losses | History |
| --- | --- | ---: | ---: | ---: | ---: | --- | ---: | --- | --- |
| V1 | Validate Apr | -180.67 | 0.72 | 47 | 51.06% | 356.74900000 (30.85847257%) | -50.00 | 5 (-216.40000000) | 100% real ticks |
| V2Live | Validate Apr | -169.60 | 0.71 | 40 | 47.50% | 300.24900000 (27.03360462%) | -50.00 | 7 (-195.86980000) | 100% real ticks |
| Trend only, V2 rules | Validate Apr | -166.13 | 0.68 | 32 | 46.88% | 306.84900000 (26.89957087%) | -50.00 | 5 (-156.80000000) | 100% real ticks |
| RangeBounce only | Validate Apr | -30.07 | 0.39 | 5 | 40.00% | 71.26980000 (7.03274127%) | -20.80 | 2 (-39.06980000) | 100% real ticks |
| DropCatcher only | Validate Apr | 26.60 | 2.41 | 3 | 66.67% | 46.30000000 (4.55753519%) | -18.90 | 1 (-18.90000000) | 100% real ticks |
| Pending fill-hour guard only | Validate Apr | 334.15 | 2.04 | 39 | 74.36% | 143.50000000 (11.37669055%) | -50.00 | 3 (-63.86980000) | 100% real ticks |
| Trend score +10 only | Validate Apr | -80.14 | 0.58 | 18 | 55.56% | 104.06980000 (10.40281887%) | -48.90 | 3 (-87.96980000) | 100% real ticks |
| V3 default April guard | Validate Apr | -90.64 | 0.45 | 14 | 50.00% | 126.76980000 (12.67191124%) | -48.90 | 3 (-87.96980000) | 100% real ticks |
| V3 default + IMP only | Validate Apr | -90.64 | 0.45 | 14 | 50.00% | 126.76980000 (12.67191124%) | -48.90 | 3 (-87.96980000) | 100% real ticks |
| V3 micro-risk | Validate Apr | -66.24 | 0.53 | 14 | 50.00% | 102.06980000 (10.20595940%) | -24.50 | 3 (-63.56980000) | 100% real ticks |

## April Loss By Variant And Module

| Variant/Expert | Module | Trades | Net | Losses |
| --- | --- | ---: | ---: | ---: |
| DropCatcher only | DropCatcher | 3 | 26.60 | 1 |
| Pending fill-hour guard only | RangeBounce | 5 | -29.50 | 3 |
| Pending fill-hour guard only | DropCatcher | 3 | 26.60 | 1 |
| Pending fill-hour guard only | Trend | 31 | 339.90 | 6 |
| RangeBounce only | RangeBounce | 5 | -29.50 | 3 |
| Trend only, V2 rules | Trend | 32 | -161.00 | 17 |
| Trend score +10 only | Trend | 10 | -76.10 | 4 |
| Trend score +10 only | RangeBounce | 5 | -29.50 | 3 |
| Trend score +10 only | DropCatcher | 3 | 26.60 | 1 |
| V1 | Trend | 37 | -199.80 | 19 |
| V1 | RangeBounce | 7 | -1.20 | 3 |
| V1 | DropCatcher | 3 | 26.60 | 1 |
| V2Live | Trend | 32 | -161.00 | 17 |
| V2Live | RangeBounce | 5 | -29.50 | 3 |
| V2Live | DropCatcher | 3 | 26.60 | 1 |
| V3 default + IMP only | Trend | 6 | -86.60 | 3 |
| V3 default + IMP only | RangeBounce | 5 | -29.50 | 3 |
| V3 default + IMP only | DropCatcher | 3 | 26.60 | 1 |
| V3 default April guard | Trend | 6 | -86.60 | 3 |
| V3 default April guard | RangeBounce | 5 | -29.50 | 3 |
| V3 default April guard | DropCatcher | 3 | 26.60 | 1 |
| V3 micro-risk | Trend | 6 | -62.20 | 3 |
| V3 micro-risk | RangeBounce | 5 | -29.50 | 3 |
| V3 micro-risk | DropCatcher | 3 | 26.60 | 1 |

## Worst April Hours

| Variant/Expert | Hour | Trades | Net | Losses |
| --- | ---: | ---: | ---: | ---: |
| V1 | 0 | 9 | -175.20 | 7 |
| V2Live | 0 | 8 | -127.50 | 6 |
| Trend only, V2 rules | 0 | 8 | -127.50 | 6 |
| V2Live | 1 | 2 | -70.70 | 2 |
| V3 default April guard | 12 | 4 | -65.90 | 2 |
| V3 default + IMP only | 12 | 4 | -65.90 | 2 |
| Trend score +10 only | 12 | 5 | -62.20 | 2 |
| V1 | 10 | 2 | -50.00 | 2 |
| V2Live | 10 | 2 | -50.00 | 2 |
| Trend only, V2 rules | 10 | 2 | -50.00 | 2 |
| V1 | 1 | 1 | -49.90 | 1 |
| Trend only, V2 rules | 1 | 1 | -49.90 | 1 |
| V2Live | 9 | 3 | -46.70 | 2 |
| Trend only, V2 rules | 9 | 3 | -46.70 | 2 |
| V3 micro-risk | 12 | 4 | -41.50 | 2 |
| V2Live | 19 | 2 | -40.00 | 2 |
| Trend only, V2 rules | 19 | 2 | -40.00 | 2 |
| V2Live | 12 | 5 | -35.80 | 1 |
| Trend only, V2 rules | 12 | 5 | -35.80 | 1 |
| V1 | 12 | 6 | -32.10 | 1 |
| V1 | 23 | 1 | -25.00 | 1 |
| V2Live | 23 | 1 | -25.00 | 1 |
| Trend only, V2 rules | 23 | 1 | -25.00 | 1 |
| Trend score +10 only | 18 | 1 | -23.60 | 1 |
| V3 default April guard | 18 | 1 | -23.60 | 1 |
| V3 default + IMP only | 18 | 1 | -23.60 | 1 |
| V3 micro-risk | 18 | 1 | -23.60 | 1 |
| V1 | 19 | 3 | -23.40 | 2 |
| V1 | 22 | 1 | -23.30 | 1 |
| V2Live | 22 | 1 | -23.30 | 1 |
