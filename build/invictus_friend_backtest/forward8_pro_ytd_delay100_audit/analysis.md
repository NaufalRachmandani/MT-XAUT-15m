# Trade-Level Analysis: InvictusForward-8_pro_ytd_2026_d29_delay100_XAUUSD_M15_d29_USD_delay100_model4_20260101_20260509.htm

## Summary
- Report net profit: `624.22 Balance Drawdown Absolute`
- Reconstructed closed trades: `231`
- Reconstructed net: `632.77`
- Win rate: `58.01%`
- Profit factor: `1.29`
- Unmatched exits: `0`
- Max price/PnL match error: `79.1209`

## Worst Engines
| engine | trades | net | win_rate | PF | avg | largest_loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
|  | 231 | 632.77 | 58.01% | 1.29 | 2.74 | -49.95 |

## Best Engines
| engine | trades | net | win_rate | PF | avg | largest_loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
|  | 231 | 632.77 | 58.01% | 1.29 | 2.74 | -49.95 |

## Worst Engine x Regime
| engine | regime_tag | trades | net | win_rate | PF | avg | largest_loss |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
|  |  | 231 | 632.77 | 58.01% | 1.29 | 2.74 | -49.95 |

## Worst Engine x Entry Hour
| engine | entry_hour | trades | net | win_rate | PF | avg | largest_loss |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
|  | 5 | 20 | -198.91 | 30.00% | 0.34 | -9.95 | -25.04 |
|  | 10 | 9 | -130.13 | 33.33% | 0.08 | -14.46 | -25.09 |
|  | 11 | 10 | -108.39 | 30.00% | 0.33 | -10.84 | -25.24 |
|  | 4 | 10 | -55.55 | 40.00% | 0.55 | -5.55 | -25.19 |
|  | 1 | 8 | -20.62 | 50.00% | 0.80 | -2.58 | -49.69 |
|  | 23 | 6 | -2.16 | 66.67% | 0.95 | -0.36 | -24.98 |
|  | 20 | 3 | -1.61 | 66.67% | 0.91 | -0.54 | -17.56 |
|  | 0 | 27 | 8.02 | 44.44% | 1.02 | 0.30 | -49.82 |
|  | 17 | 4 | 10.05 | 75.00% | 1.69 | 2.51 | -14.51 |
|  | 12 | 24 | 11.20 | 62.50% | 1.05 | 0.47 | -25.21 |
|  | 9 | 14 | 27.15 | 64.29% | 1.22 | 1.94 | -25.06 |
|  | 2 | 3 | 39.67 | 66.67% | 4.87 | 13.22 | -10.24 |

## Worst Months
| entry_month | trades | net | win_rate | PF | avg | largest_loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2026-04 | 65 | -244.09 | 43.08% | 0.73 | -3.76 | -49.95 |
| 2026-05 | 14 | 3.25 | 50.00% | 1.02 | 0.23 | -24.94 |
| 2026-02 | 36 | 27.11 | 58.33% | 1.09 | 0.75 | -25.21 |
| 2026-01 | 64 | 413.92 | 70.31% | 1.97 | 6.47 | -25.16 |
| 2026-03 | 52 | 432.58 | 63.46% | 2.04 | 8.32 | -25.24 |

## Worst Loss Clusters
| start | end | count | pnl | buy_losses | sell_losses | engines |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| 2026-04-16 00:25:56 | 2026-04-16 13:54:17 | 3 | -147.03 | 3 | 0 | :3 |
| 2026-04-06 09:50:12 | 2026-04-06 12:23:03 | 5 | -125.09 | 5 | 0 | :5 |
| 2026-01-27 07:00:26 | 2026-01-27 14:05:41 | 4 | -95.40 | 4 | 0 | :4 |
| 2026-04-30 05:01:20 | 2026-04-30 06:51:39 | 4 | -90.34 | 0 | 4 | :4 |
| 2026-01-21 05:26:15 | 2026-01-21 07:03:20 | 3 | -75.19 | 3 | 0 | :3 |
| 2026-01-20 00:00:52 | 2026-01-20 04:35:34 | 3 | -75.00 | 0 | 3 | :3 |
| 2026-03-27 11:15:35 | 2026-03-27 14:03:16 | 3 | -73.56 | 0 | 3 | :3 |
| 2026-03-25 11:47:56 | 2026-03-25 12:30:49 | 3 | -72.59 | 3 | 0 | :3 |
| 2026-04-23 09:30:00 | 2026-04-23 11:52:38 | 3 | -71.94 | 0 | 3 | :3 |
| 2026-02-11 12:02:40 | 2026-02-11 12:41:09 | 3 | -71.34 | 3 | 0 | :3 |

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
