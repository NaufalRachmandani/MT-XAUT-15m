# V4 vs V5 Comparison

Native MT5 cent `XAUUSDc` reports only. Deposit `1000 USC`, leverage `1:2000`, model `Every tick based on real ticks`.

## Window Winners

| Window | Winner | Notes |
| --- | --- | --- |
| Mar validation | V5 max profit | V5 max profit: net 1651.90, DD 42.43%; V5 high profit: net 1649.50, DD 38.36%; V4 lot +100%: net 1399.70, DD 16.68%; V5 safer quality: net 1034.90, DD 26.28% |
| Apr validation | V5 max profit | V5 max profit: net 819.39, DD 30.27%; V5 high profit: net 790.49, DD 31.09%; V4 lot +100%: net 717.83, DD 26.07%; V5 safer quality: net 588.67, DD 18.97% |
| May OOS | V5 max profit | V5 max profit: net 1022.00, DD 14.31%; V5 high profit: net 795.80, DD 13.68%; V4 lot +100%: net 579.60, DD 13.11%; V5 safer quality: net 562.90, DD 10.49% |
| Last month | V5 max profit | V5 max profit: net 2562.40, DD 13.80%; V5 high profit: net 2337.20, DD 14.72%; V4 lot +100%: net 1542.14, DD 14.60%; V5 safer quality: net 1459.98, DD 9.99% |
| 2026 YTD | V5 max profit | V5 max profit: net 19839.91, DD 28.60%; V5 high profit: net 18771.29, DD 26.87%; V4 lot +100%: net 16322.03, DD 28.63%; V5 safer quality: net 9701.49, DD 22.14% |

## Key Metrics

| Variant | Window | Net | PF | Trades | WR | Eq DD | Largest Loss | Max CL | History |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| V4 lot +100% | Mar validation | 1399.70 | 3.24 | 37 | 83.78% | 16.68% | -180.20 | 2 | 100% real ticks |
| V4 lot +100% | Apr validation | 717.83 | 1.99 | 40 | 75.00% | 26.07% | -138.80 | 3 | 100% real ticks |
| V4 lot +100% | May OOS | 579.60 | no-loss | 11 | 100.00% | 13.11% | 0.00 | 0 | 100% real ticks |
| V4 lot +100% | Last month | 1542.14 | 5.46 | 37 | 86.49% | 14.60% | -124.90 | 2 | 100% real ticks |
| V4 lot +100% | 2026 YTD | 16322.03 | 3.31 | 167 | 81.44% | 28.63% | -849.10 | 3 | 100% real ticks |
| V5 safer quality | Mar validation | 1034.90 | 2.80 | 37 | 83.78% | 26.28% | -148.30 | 2 | 100% real ticks |
| V5 safer quality | Apr validation | 588.67 | 2.26 | 40 | 75.00% | 18.97% | -97.90 | 3 | 100% real ticks |
| V5 safer quality | May OOS | 562.90 | no-loss | 11 | 100.00% | 10.49% | 0.00 | 0 | 100% real ticks |
| V5 safer quality | Last month | 1459.98 | 7.59 | 37 | 86.49% | 9.99% | -92.50 | 2 | 100% real ticks |
| V5 safer quality | 2026 YTD | 9701.49 | 3.10 | 165 | 81.21% | 22.14% | -416.50 | 3 | 100% real ticks |
| V5 high profit | Mar validation | 1649.50 | 2.77 | 38 | 84.21% | 38.36% | -270.30 | 2 | 100% real ticks |
| V5 high profit | Apr validation | 790.49 | 2.00 | 40 | 75.00% | 31.09% | -185.20 | 3 | 100% real ticks |
| V5 high profit | May OOS | 795.80 | no-loss | 11 | 100.00% | 13.68% | 0.00 | 0 | 100% real ticks |
| V5 high profit | Last month | 2337.20 | 6.98 | 38 | 86.84% | 14.72% | -162.00 | 2 | 100% real ticks |
| V5 high profit | 2026 YTD | 18771.29 | 2.55 | 169 | 81.07% | 26.87% | -3110.40 | 3 | 100% real ticks |
| V5 max profit | Mar validation | 1651.90 | 2.53 | 38 | 84.21% | 42.43% | -315.40 | 2 | 100% real ticks |
| V5 max profit | Apr validation | 819.39 | 2.06 | 40 | 75.00% | 30.27% | -185.20 | 3 | 100% real ticks |
| V5 max profit | May OOS | 1022.00 | no-loss | 11 | 100.00% | 14.31% | 0.00 | 0 | 100% real ticks |
| V5 max profit | Last month | 2562.40 | 8.01 | 38 | 86.84% | 13.80% | -162.00 | 2 | 100% real ticks |
| V5 max profit | 2026 YTD | 19839.91 | 2.52 | 169 | 81.07% | 28.60% | -3732.50 | 3 | 100% real ticks |

## Decision

`v5_max_profit_scaled` is the profit winner: YTD net 19839.91 vs V4 16322.03 (+3517.89), with YTD equity DD 28.60% vs V4 28.63% (-0.03 pp).
It is not live-ready for 1000 USC because validation DD is worse than V4 in Mar/Apr/May and largest YTD loss worsens from -849.10 to -3732.50.
`v5_profit_scaled` is the safer V5 profile: YTD net 9701.49, YTD DD 22.14%, largest loss -416.50; it sacrifices profit versus V4 for smaller loss size.
Use the selected V5 set as a manual research/backtest candidate, not a live deployment set.
