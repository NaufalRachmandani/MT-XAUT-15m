# V2Live Trade Diagnosis

Diagnosis uses closed trades reconstructed from native MT5 `.htm` deal tables. Focus below is V2Live deposit 1000.

## By Module

| Module | Trades | Net | Losses |
| --- | ---: | ---: | ---: |
| DropCatcher | 27 | 411.00 | 7 |
| RangeBounce | 31 | 489.50 | 5 |
| Trend | 363 | 3355.80 | 94 |

## Worst Entry Hours

| Hour | Trades | Net | Losses |
| ---: | ---: | ---: | ---: |
| 10 | 4 | -501.40 | 4 |
| 19 | 20 | -367.90 | 11 |
| 22 | 3 | -279.60 | 3 |
| 1 | 10 | -229.10 | 3 |
| 20 | 4 | -199.80 | 4 |
| 23 | 17 | -118.20 | 5 |
| 0 | 52 | -109.50 | 19 |
| 2 | 3 | -31.80 | 3 |
| 11 | 2 | 23.60 | 0 |
| 17 | 6 | 68.40 | 0 |
| 5 | 5 | 93.50 | 0 |
| 16 | 3 | 135.10 | 0 |

## Largest Losses

| Window | Time Hour | Module | Profit | Comment |
| --- | ---: | --- | ---: | --- |
| train_2026_jan_apr | 15 | Trend | -149.90 | IF8V2L_TR S:85 IMP |
| ytd_2026 | 15 | Trend | -149.90 | IF8V2L_TR S:85 IMP |
| train_2026_jan_apr | 1 | Trend | -149.70 | IF8V2L_TR S:85 IMP |
| ytd_2026 | 1 | Trend | -149.70 | IF8V2L_TR S:85 IMP |
| train_2026_jan_apr | 0 | Trend | -149.60 | IF8V2L_TR S:85 IMP |
| ytd_2026 | 0 | Trend | -149.60 | IF8V2L_TR S:85 IMP |
| train_2026_jan_apr | 10 | Trend | -125.80 | IF8V2L_TR S:85 IMP |
| ytd_2026 | 10 | Trend | -125.80 | IF8V2L_TR S:85 IMP |
| train_2026_jan_apr | 0 | Trend | -125.60 | IF8V2L_TR S:85 IMP |
| ytd_2026 | 0 | Trend | -125.60 | IF8V2L_TR S:85 IMP |
| train_2026_jan_apr | 0 | Trend | -125.50 | IF8V2L_TR S:95 IMP |
| ytd_2026 | 0 | Trend | -125.50 | IF8V2L_TR S:95 IMP |
| train_2026_jan_apr | 23 | Trend | -125.10 | IF8V2L_TR S:85 COR |
| ytd_2026 | 23 | Trend | -125.10 | IF8V2L_TR S:85 COR |
| train_2026_jan_apr | 10 | Trend | -124.90 | IF8V2L_TR S:85 IMP |
| ytd_2026 | 10 | Trend | -124.90 | IF8V2L_TR S:85 IMP |
| train_2026_jan_apr | 12 | Trend | -122.40 | IF8V2L_TR S:95 IMP |
| ytd_2026 | 12 | Trend | -122.40 | IF8V2L_TR S:95 IMP |
| train_2026_jan_apr | 22 | Trend | -116.50 | IF8V2L_TR S:85 COR |
| train_2026_jan_apr | 19 | Trend | -116.50 | IF8V2L_TR S:85 COR |
