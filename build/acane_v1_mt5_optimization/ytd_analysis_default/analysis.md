# Trade-Level Analysis: AcaneM1_v1_ytd_2026_d100_lev12000_delay100_model4_20260101_20260510.htm

## Summary
- Report net profit: `-8.98 Balance Drawdown Absolute`
- Reconstructed closed trades: `358`
- Reconstructed net: `-8.98`
- Win rate: `59.78%`
- Profit factor: `0.97`
- Unmatched exits: `0`
- Max price/PnL match error: `4.6332`

## Worst Engines
| engine | trades | net | win_rate | PF | avg | largest_loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| CBK | 13 | -9.49 | 53.85% | 0.44 | -0.73 | -3.40 |
| IMP | 345 | 0.51 | 60.00% | 1.00 | 0.00 | -4.68 |

## Best Engines
| engine | trades | net | win_rate | PF | avg | largest_loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| IMP | 345 | 0.51 | 60.00% | 1.00 | 0.00 | -4.68 |
| CBK | 13 | -9.49 | 53.85% | 0.44 | -0.73 | -3.40 |

## Worst Engine x Regime
| engine | regime_tag | trades | net | win_rate | PF | avg | largest_loss |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| CBK | WG | 13 | -9.49 | 53.85% | 0.44 | -0.73 | -3.40 |
| IMP |  | 345 | 0.51 | 60.00% | 1.00 | 0.00 | -4.68 |

## Worst Engine x Entry Hour
| engine | entry_hour | trades | net | win_rate | PF | avg | largest_loss |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| IMP | 10 | 109 | -33.59 | 51.38% | 0.73 | -0.31 | -4.68 |
| IMP | 7 | 92 | -8.34 | 56.52% | 0.91 | -0.09 | -3.05 |
| CBK | 7 | 3 | -5.42 | 33.33% | 0.07 | -1.81 | -2.96 |
| CBK | 10 | 7 | -3.30 | 57.14% | 0.64 | -0.47 | -3.40 |
| CBK | 5 | 3 | -0.77 | 66.67% | 0.57 | -0.26 | -1.78 |
| IMP | 5 | 144 | 42.44 | 68.75% | 1.40 | 0.29 | -3.74 |

## Worst Months
| entry_month | trades | net | win_rate | PF | avg | largest_loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2026-04 | 58 | -26.79 | 50.00% | 0.62 | -0.46 | -4.68 |
| 2026-01 | 114 | -7.51 | 60.53% | 0.92 | -0.07 | -2.99 |
| 2026-03 | 90 | 0.23 | 60.00% | 1.00 | 0.00 | -3.40 |
| 2026-05 | 26 | 12.01 | 65.38% | 1.67 | 0.46 | -2.95 |
| 2026-02 | 70 | 13.08 | 64.29% | 1.20 | 0.19 | -3.74 |

## Worst Loss Clusters
| start | end | count | pnl | buy_losses | sell_losses | engines |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| 2026-01-27 05:51:00 | 2026-01-27 10:18:00 | 6 | -16.30 | 6 | 0 | IMP:6 |
| 2026-01-12 05:27:00 | 2026-01-12 11:00:01 | 8 | -14.58 | 8 | 0 | IMP:8 |
| 2026-01-28 05:20:00 | 2026-01-28 07:50:10 | 5 | -14.22 | 5 | 0 | IMP:5 |
| 2026-03-16 05:32:00 | 2026-03-16 07:29:24 | 4 | -11.41 | 0 | 4 | IMP:4 |
| 2026-03-18 10:03:00 | 2026-03-18 10:58:16 | 5 | -11.06 | 0 | 5 | IMP:5 |
| 2026-04-14 07:40:00 | 2026-04-14 10:54:40 | 4 | -10.70 | 4 | 0 | CBK:2, IMP:2 |
| 2026-02-23 07:52:00 | 2026-02-23 10:39:33 | 4 | -10.66 | 4 | 0 | CBK:1, IMP:3 |
| 2026-03-19 05:12:00 | 2026-03-19 10:18:38 | 4 | -10.41 | 0 | 4 | IMP:4 |
| 2026-04-09 10:02:00 | 2026-04-09 10:51:31 | 4 | -10.35 | 4 | 0 | IMP:4 |
| 2026-05-06 05:10:01 | 2026-05-06 10:55:18 | 4 | -9.42 | 4 | 0 | IMP:4 |

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
