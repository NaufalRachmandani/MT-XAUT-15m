# Trade-Level Analysis: AcaneM1_v2_current_2025_d29_delay100ms_real_ticks_20250101_20260509.htm

## Summary
- Report net profit: `-14.34 Balance Drawdown Absolute`
- Reconstructed closed trades: `252`
- Reconstructed net: `-14.34`
- Win rate: `54.37%`
- Profit factor: `0.83`
- Unmatched exits: `0`
- Max price/PnL match error: `1.1881`

## Worst Engines
| engine | trades | net | win_rate | PF | avg | largest_loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| RJT | 252 | -14.34 | 54.37% | 0.83 | -0.06 | -1.20 |

## Best Engines
| engine | trades | net | win_rate | PF | avg | largest_loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| RJT | 252 | -14.34 | 54.37% | 0.83 | -0.06 | -1.20 |

## Worst Engine x Regime
| engine | regime_tag | trades | net | win_rate | PF | avg | largest_loss |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| RJT | RG | 252 | -14.34 | 54.37% | 0.83 | -0.06 | -1.20 |

## Worst Engine x Entry Hour
| engine | entry_hour | trades | net | win_rate | PF | avg | largest_loss |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| RJT | 11 | 98 | -13.50 | 48.98% | 0.63 | -0.14 | -0.97 |
| RJT | 10 | 154 | -0.84 | 57.79% | 0.98 | -0.01 | -1.20 |

## Worst Months
| entry_month | trades | net | win_rate | PF | avg | largest_loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2025-05 | 49 | -8.20 | 44.90% | 0.63 | -0.17 | -1.20 |
| 2025-02 | 49 | -7.96 | 48.98% | 0.53 | -0.16 | -0.74 |
| 2025-01 | 49 | -3.58 | 53.06% | 0.77 | -0.07 | -0.76 |
| 2025-06 | 26 | -2.53 | 57.69% | 0.73 | -0.10 | -1.01 |
| 2025-03 | 47 | 1.11 | 61.70% | 1.08 | 0.02 | -0.92 |
| 2025-04 | 32 | 6.82 | 65.62% | 1.77 | 0.21 | -1.08 |

## Worst Loss Clusters
| start | end | count | pnl | buy_losses | sell_losses | engines |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| 2025-05-27 10:00:00 | 2025-05-27 11:46:36 | 4 | -3.73 | 0 | 4 | RJT:4 |
| 2025-01-21 10:01:00 | 2025-01-21 11:19:38 | 5 | -3.19 | 0 | 5 | RJT:5 |
| 2025-05-13 10:11:00 | 2025-05-13 11:12:42 | 4 | -3.16 | 0 | 4 | RJT:4 |
| 2025-01-13 10:29:00 | 2025-01-13 11:46:37 | 4 | -2.90 | 0 | 4 | RJT:4 |
| 2025-01-14 10:02:00 | 2025-01-14 11:25:38 | 4 | -2.83 | 0 | 4 | RJT:4 |
| 2025-05-28 10:53:00 | 2025-05-28 11:39:19 | 4 | -2.79 | 0 | 4 | RJT:4 |
| 2025-04-29 10:24:00 | 2025-04-29 11:45:38 | 3 | -2.59 | 0 | 3 | RJT:3 |
| 2025-05-01 10:06:00 | 2025-05-01 11:34:21 | 3 | -2.59 | 0 | 3 | RJT:3 |
| 2025-03-10 11:08:00 | 2025-03-10 11:37:26 | 3 | -2.51 | 0 | 3 | RJT:3 |
| 2025-06-09 10:25:01 | 2025-06-09 10:39:34 | 3 | -2.50 | 0 | 3 | RJT:3 |

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
