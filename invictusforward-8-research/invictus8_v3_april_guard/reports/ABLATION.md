# V3 Module Ablation And Guard Matrix

All rows below are native MT5 `.htm` validation runs on 1000 USC.

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

## Variant Gate Scores

| Variant | Relative Gate | Strict Live | Score | Aggregate Net | Min Net | Max Eq DD % | April Net | April PF | Fail Reasons |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Pending fill-hour guard only | True | False | 2719.94 | 1289.25 | 271.20 | 11.38 | 334.15 | 2.04 |  |
| DropCatcher only | False | False | 704.27 | 139.30 | 0.00 | 5.68 | 26.60 | 2.41 | May net <= 0 |
| RangeBounce only | False | False | 488.20 | 106.73 | -30.07 | 7.03 | -30.07 | 0.39 | April PF worse than V1 |
| Trend score +10 only | False | False | 488.03 | 307.46 | -80.14 | 12.10 | -80.14 | 0.58 | April PF worse than V1 |
| V3 micro-risk | False | False | 474.29 | 233.06 | -66.24 | 10.21 | -66.24 | 0.53 | April PF worse than V1 |
| V3 default April guard | False | False | 408.03 | 264.66 | -90.64 | 12.67 | -90.64 | 0.45 | April PF worse than V1 |
| V3 default + IMP only | False | False | 408.03 | 264.66 | -90.64 | 12.67 | -90.64 | 0.45 | April PF worse than V1 |
| Trend only, V2 rules | False | False | 384.68 | 610.05 | -166.13 | 26.90 | -166.13 | 0.68 | April PF worse than V1; Mar/May DD worse than V1 |
