# Trade-Level Analysis: AcaneM1_v2_since_2023_d29_delay50ms_real_ticks_20230101_20260509.htm

## Summary
- Report net profit: `33 695.79 Balance Drawdown Absolute`
- Reconstructed closed trades: `2086`
- Reconstructed net: `33697.50`
- Win rate: `60.74%`
- Profit factor: `1.98`
- Unmatched exits: `0`
- Max price/PnL match error: `964.6461`

## Worst Engines
| engine | trades | net | win_rate | PF | avg | largest_loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| MRV | 2086 | 33697.50 | 60.74% | 1.98 | 16.15 | -627.01 |

## Best Engines
| engine | trades | net | win_rate | PF | avg | largest_loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| MRV | 2086 | 33697.50 | 60.74% | 1.98 | 16.15 | -627.01 |

## Worst Engine x Regime
| engine | regime_tag | trades | net | win_rate | PF | avg | largest_loss |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| MRV | RG | 620 | 15742.59 | 66.61% | 3.03 | 25.39 | -470.58 |
| MRV | WG | 1466 | 17954.91 | 58.25% | 1.67 | 12.25 | -627.01 |

## Worst Engine x Entry Hour
| engine | entry_hour | trades | net | win_rate | PF | avg | largest_loss |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| MRV | 3 | 124 | -1224.81 | 53.23% | 0.63 | -9.88 | -424.22 |
| MRV | 4 | 99 | -412.07 | 50.51% | 0.75 | -4.16 | -405.16 |
| MRV | 22 | 40 | -12.66 | 42.50% | 0.49 | -0.32 | -5.01 |
| MRV | 8 | 140 | 617.31 | 60.71% | 1.17 | 4.41 | -627.01 |
| MRV | 23 | 94 | 757.96 | 51.06% | 1.44 | 8.06 | -372.50 |
| MRV | 10 | 104 | 916.68 | 59.62% | 1.46 | 8.81 | -399.98 |
| MRV | 1 | 117 | 1051.55 | 59.83% | 1.52 | 8.99 | -470.58 |
| MRV | 12 | 112 | 1100.07 | 61.61% | 1.48 | 9.82 | -365.00 |
| MRV | 18 | 111 | 1131.20 | 52.25% | 1.56 | 10.19 | -327.36 |
| MRV | 0 | 131 | 1314.06 | 54.20% | 1.78 | 10.03 | -338.69 |
| MRV | 7 | 104 | 1384.93 | 59.62% | 1.97 | 13.32 | -326.95 |
| MRV | 17 | 110 | 1527.60 | 60.00% | 2.01 | 13.89 | -346.96 |

## Worst Months
| entry_month | trades | net | win_rate | PF | avg | largest_loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2024-08 | 194 | 10.88 | 58.25% | 1.54 | 0.06 | -0.53 |
| 2024-09 | 425 | 59.18 | 58.12% | 1.75 | 0.14 | -1.42 |
| 2024-10 | 559 | 324.56 | 56.35% | 1.70 | 0.58 | -5.31 |
| 2024-11 | 497 | 7251.10 | 67.20% | 2.67 | 14.59 | -115.92 |
| 2024-12 | 411 | 26051.78 | 62.77% | 1.88 | 63.39 | -627.01 |

## Worst Loss Clusters
| start | end | count | pnl | buy_losses | sell_losses | engines |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| 2024-12-22 23:06:39 | 2024-12-23 19:51:30 | 12 | -4645.84 | 7 | 5 | MRV:12 |
| 2024-12-24 00:17:04 | 2024-12-24 13:21:44 | 10 | -3515.09 | 6 | 4 | MRV:10 |
| 2024-12-20 10:02:01 | 2024-12-20 18:05:57 | 7 | -2324.44 | 4 | 3 | MRV:7 |
| 2024-12-12 00:07:22 | 2024-12-12 19:31:37 | 15 | -2205.59 | 10 | 5 | MRV:15 |
| 2024-12-19 03:27:59 | 2024-12-19 14:35:57 | 5 | -1419.89 | 4 | 1 | MRV:5 |
| 2024-12-12 23:34:35 | 2024-12-13 13:12:16 | 7 | -1287.71 | 5 | 2 | MRV:7 |
| 2024-12-18 06:14:05 | 2024-12-18 09:54:27 | 4 | -1211.85 | 3 | 1 | MRV:4 |
| 2024-12-16 23:24:37 | 2024-12-17 04:32:45 | 5 | -1094.93 | 3 | 2 | MRV:5 |
| 2024-12-09 23:39:15 | 2024-12-10 09:45:45 | 9 | -1086.54 | 5 | 4 | MRV:9 |
| 2024-12-05 01:11:25 | 2024-12-05 19:40:47 | 9 | -996.82 | 4 | 5 | MRV:9 |

## Files
- `trade_log.csv`: all reconstructed closed trades with original entry label.
- `top_losses.csv`: worst individual trades.
- `by_engine.csv`, `by_engine_hour.csv`, `by_engine_regime.csv`: leak maps.
- `loss_clusters.csv`: clustered losses within a 4-hour gap.

## Label Legend
- `BO` = `BUY_BREAK`
- `PB` = `BUY_PULLBACK`
- `ZB` = `BUY_ZONE`
- `IB` = `BUY_IMPULSE`
- `SB` = `BUY_COMP`
- `AB` = `BUY_ADDON`
- `BE` = `SELL_BREAK`
- `ZS` = `SELL_ZONE`
- `IS` = `SELL_IMPULSE`
- `SS` = `SELL_COMP`
- `AS` = `SELL_ADDON`
- `RG` = strong regime
- `WG` = weak regime
- `CH` = core hour
- `XH` = outside hour
- `X` = outside hour (truncated)
- `ZN` = zone retest
- `RT` = retest
- `RJ` = rejection
- `AD` = add-on
- `CT` = continuation
- `RC` = reclaim/continuation
