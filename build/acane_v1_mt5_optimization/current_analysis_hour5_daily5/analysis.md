# Trade-Level Analysis: AcaneM1_v1_current_2025_d100_lev12000_delay100_model4_20250101_20260510.htm

## Summary
- Report net profit: `17.11 Balance Drawdown Absolute`
- Reconstructed closed trades: `545`
- Reconstructed net: `17.11`
- Win rate: `60.55%`
- Profit factor: `1.04`
- Unmatched exits: `0`
- Max price/PnL match error: `3.7026`

## Worst Engines
| engine | trades | net | win_rate | PF | avg | largest_loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| CBK | 10 | -4.64 | 40.00% | 0.49 | -0.46 | -2.81 |
| IMP | 535 | 21.75 | 60.93% | 1.06 | 0.04 | -3.74 |

## Best Engines
| engine | trades | net | win_rate | PF | avg | largest_loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| IMP | 535 | 21.75 | 60.93% | 1.06 | 0.04 | -3.74 |
| CBK | 10 | -4.64 | 40.00% | 0.49 | -0.46 | -2.81 |

## Worst Engine x Regime
| engine | regime_tag | trades | net | win_rate | PF | avg | largest_loss |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| CBK | WG | 10 | -4.64 | 40.00% | 0.49 | -0.46 | -2.81 |
| IMP |  | 535 | 21.75 | 60.93% | 1.06 | 0.04 | -3.74 |

## Worst Engine x Entry Hour
| engine | entry_hour | trades | net | win_rate | PF | avg | largest_loss |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| CBK | 5 | 10 | -4.64 | 40.00% | 0.49 | -0.46 | -2.81 |
| IMP | 5 | 535 | 21.75 | 60.93% | 1.06 | 0.04 | -3.74 |

## Worst Months
| entry_month | trades | net | win_rate | PF | avg | largest_loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2025-09 | 68 | -30.45 | 42.65% | 0.49 | -0.45 | -2.14 |
| 2025-07 | 43 | -3.44 | 55.81% | 0.89 | -0.08 | -2.62 |
| 2025-11 | 38 | -2.88 | 57.89% | 0.91 | -0.08 | -2.81 |
| 2025-06 | 32 | -1.01 | 65.62% | 0.95 | -0.03 | -2.44 |
| 2025-03 | 22 | -0.78 | 54.55% | 0.95 | -0.04 | -1.97 |
| 2025-08 | 4 | -0.56 | 50.00% | 0.78 | -0.14 | -1.64 |
| 2025-10 | 40 | -0.48 | 60.00% | 0.98 | -0.01 | -2.86 |
| 2025-02 | 27 | -0.16 | 62.96% | 0.99 | -0.01 | -2.04 |

## Worst Loss Clusters
| start | end | count | pnl | buy_losses | sell_losses | engines |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| 2026-01-28 05:20:00 | 2026-01-28 05:43:23 | 3 | -8.54 | 3 | 0 | IMP:3 |
| 2026-01-21 05:19:00 | 2026-01-21 05:54:25 | 3 | -8.34 | 3 | 0 | IMP:3 |
| 2025-07-15 05:25:01 | 2025-07-15 05:49:59 | 4 | -8.24 | 4 | 0 | IMP:4 |
| 2025-09-24 05:22:00 | 2025-09-24 05:56:08 | 6 | -7.83 | 6 | 0 | IMP:6 |
| 2025-06-24 05:06:00 | 2025-06-24 05:48:27 | 4 | -7.27 | 0 | 4 | IMP:4 |
| 2025-09-30 05:19:00 | 2025-09-30 06:04:36 | 4 | -6.33 | 4 | 0 | IMP:4 |
| 2025-03-28 05:08:00 | 2025-03-28 05:58:19 | 4 | -6.28 | 4 | 0 | IMP:4 |
| 2025-11-04 05:02:00 | 2025-11-04 05:24:48 | 3 | -6.19 | 0 | 3 | IMP:3 |
| 2025-09-01 05:21:00 | 2025-09-01 05:50:35 | 3 | -6.17 | 3 | 0 | IMP:3 |
| 2026-01-19 05:03:00 | 2026-01-19 05:59:00 | 4 | -5.95 | 4 | 0 | IMP:4 |

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
