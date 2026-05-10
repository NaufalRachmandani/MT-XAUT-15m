# Trade-Level Analysis: AcaneM1_v2t_r30_sell_rjt_9_12_ytd_2026_d29_delay100_real_ticks_20260101_20260509.htm

## Summary
- Report net profit: `-0.83 Balance Drawdown Absolute`
- Reconstructed closed trades: `115`
- Reconstructed net: `-0.83`
- Win rate: `60.00%`
- Profit factor: `0.98`
- Unmatched exits: `0`
- Max price/PnL match error: `1.8018`

## Worst Engines
| engine | trades | net | win_rate | PF | avg | largest_loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| RJT | 115 | -0.83 | 60.00% | 0.98 | -0.01 | -1.68 |

## Best Engines
| engine | trades | net | win_rate | PF | avg | largest_loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| RJT | 115 | -0.83 | 60.00% | 0.98 | -0.01 | -1.68 |

## Worst Engine x Regime
| engine | regime_tag | trades | net | win_rate | PF | avg | largest_loss |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| RJT | RG | 115 | -0.83 | 60.00% | 0.98 | -0.01 | -1.68 |

## Worst Engine x Entry Hour
| engine | entry_hour | trades | net | win_rate | PF | avg | largest_loss |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| RJT | 9 | 32 | -2.74 | 59.38% | 0.81 | -0.09 | -1.55 |
| RJT | 11 | 42 | -0.19 | 57.14% | 0.99 | -0.00 | -1.68 |
| RJT | 10 | 41 | 2.10 | 63.41% | 1.13 | 0.05 | -1.34 |

## Worst Months
| entry_month | trades | net | win_rate | PF | avg | largest_loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2026-02 | 9 | -3.47 | 22.22% | 0.46 | -0.39 | -1.23 |
| 2026-01 | 64 | -3.43 | 62.50% | 0.88 | -0.05 | -1.68 |
| 2026-04 | 30 | 0.29 | 60.00% | 1.02 | 0.01 | -1.43 |
| 2026-03 | 6 | 1.23 | 66.67% | 1.61 | 0.20 | -1.04 |
| 2026-05 | 6 | 4.55 | 83.33% | 6.11 | 0.76 | -0.89 |

## Worst Loss Clusters
| start | end | count | pnl | buy_losses | sell_losses | engines |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| 2026-01-19 10:37:00 | 2026-01-19 11:59:31 | 4 | -4.85 | 0 | 4 | RJT:4 |
| 2026-04-27 09:02:00 | 2026-04-27 11:52:26 | 4 | -3.43 | 0 | 4 | RJT:4 |
| 2026-01-14 09:54:00 | 2026-01-14 11:59:08 | 3 | -3.34 | 0 | 3 | RJT:3 |
| 2026-04-22 09:34:00 | 2026-04-22 09:51:02 | 3 | -3.10 | 0 | 3 | RJT:3 |
| 2026-01-08 09:23:00 | 2026-01-08 11:21:05 | 3 | -3.02 | 0 | 3 | RJT:3 |
| 2026-02-16 11:36:01 | 2026-02-16 11:52:37 | 3 | -2.85 | 0 | 3 | RJT:3 |
| 2026-02-18 09:51:00 | 2026-02-18 11:09:14 | 3 | -2.33 | 0 | 3 | RJT:3 |

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
