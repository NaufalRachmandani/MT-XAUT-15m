# Trade-Level Analysis: AcaneM1_v1_ytd_2026_d100_lev12000_delay100_model4_20260101_20260510.htm

## Summary
- Report net profit: `41.69 Balance Drawdown Absolute`
- Reconstructed closed trades: `147`
- Reconstructed net: `41.69`
- Win rate: `68.71%`
- Profit factor: `1.39`
- Unmatched exits: `0`
- Max price/PnL match error: `3.7026`

## Worst Engines
| engine | trades | net | win_rate | PF | avg | largest_loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| CBK | 3 | -0.77 | 66.67% | 0.57 | -0.26 | -1.78 |
| IMP | 144 | 42.46 | 68.75% | 1.40 | 0.29 | -3.74 |

## Best Engines
| engine | trades | net | win_rate | PF | avg | largest_loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| IMP | 144 | 42.46 | 68.75% | 1.40 | 0.29 | -3.74 |
| CBK | 3 | -0.77 | 66.67% | 0.57 | -0.26 | -1.78 |

## Worst Engine x Regime
| engine | regime_tag | trades | net | win_rate | PF | avg | largest_loss |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| CBK | WG | 3 | -0.77 | 66.67% | 0.57 | -0.26 | -1.78 |
| IMP |  | 144 | 42.46 | 68.75% | 1.40 | 0.29 | -3.74 |

## Worst Engine x Entry Hour
| engine | entry_hour | trades | net | win_rate | PF | avg | largest_loss |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| CBK | 5 | 3 | -0.77 | 66.67% | 0.57 | -0.26 | -1.78 |
| IMP | 5 | 144 | 42.46 | 68.75% | 1.40 | 0.29 | -3.74 |

## Worst Months
| entry_month | trades | net | win_rate | PF | avg | largest_loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2026-01 | 51 | -0.34 | 60.78% | 0.99 | -0.01 | -2.99 |
| 2026-03 | 36 | 0.78 | 63.89% | 1.02 | 0.02 | -3.18 |
| 2026-05 | 10 | 1.10 | 70.00% | 1.17 | 0.11 | -2.36 |
| 2026-04 | 8 | 9.06 | 87.50% | 6.09 | 1.13 | -1.78 |
| 2026-02 | 42 | 31.09 | 78.57% | 2.45 | 0.74 | -3.74 |

## Worst Loss Clusters
| start | end | count | pnl | buy_losses | sell_losses | engines |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| 2026-02-04 05:18:00 | 2026-02-04 05:51:12 | 4 | -8.95 | 4 | 0 | IMP:4 |
| 2026-01-28 05:20:00 | 2026-01-28 05:43:23 | 3 | -8.54 | 3 | 0 | IMP:3 |
| 2026-01-21 05:19:00 | 2026-01-21 05:54:25 | 3 | -8.34 | 3 | 0 | IMP:3 |
| 2026-01-19 05:03:00 | 2026-01-19 06:00:50 | 4 | -7.14 | 4 | 0 | IMP:4 |
| 2026-03-23 05:25:00 | 2026-03-23 05:53:20 | 3 | -5.85 | 0 | 3 | IMP:3 |

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
