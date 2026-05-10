# Trade-Level Analysis: AcaneM1_v2_ytd_2026_d29_delay100ms_real_ticks_20260101_20260509.htm

## Summary
- Report net profit: `6.11 Balance Drawdown Absolute`
- Reconstructed closed trades: `130`
- Reconstructed net: `6.11`
- Win rate: `61.54%`
- Profit factor: `1.11`
- Unmatched exits: `0`
- Max price/PnL match error: `2.2869`

## Worst Engines
| engine | trades | net | win_rate | PF | avg | largest_loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| RJT | 130 | 6.11 | 61.54% | 1.11 | 0.05 | -1.82 |

## Best Engines
| engine | trades | net | win_rate | PF | avg | largest_loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| RJT | 130 | 6.11 | 61.54% | 1.11 | 0.05 | -1.82 |

## Worst Engine x Regime
| engine | regime_tag | trades | net | win_rate | PF | avg | largest_loss |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| RJT | RG | 130 | 6.11 | 61.54% | 1.11 | 0.05 | -1.82 |

## Worst Engine x Entry Hour
| engine | entry_hour | trades | net | win_rate | PF | avg | largest_loss |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| RJT | 10 | 69 | -1.22 | 57.97% | 0.96 | -0.02 | -1.74 |
| RJT | 11 | 61 | 7.33 | 65.57% | 1.29 | 0.12 | -1.82 |

## Worst Months
| entry_month | trades | net | win_rate | PF | avg | largest_loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2026-02 | 19 | -4.99 | 42.11% | 0.63 | -0.26 | -1.62 |
| 2026-03 | 12 | -0.29 | 66.67% | 0.92 | -0.02 | -1.46 |
| 2026-05 | 8 | 2.03 | 62.50% | 1.95 | 0.25 | -1.22 |
| 2026-01 | 59 | 3.65 | 67.80% | 1.16 | 0.06 | -1.68 |
| 2026-04 | 32 | 5.71 | 59.38% | 1.38 | 0.18 | -1.82 |

## Worst Loss Clusters
| start | end | count | pnl | buy_losses | sell_losses | engines |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| 2026-01-19 10:37:00 | 2026-01-19 11:59:31 | 4 | -4.85 | 0 | 4 | RJT:4 |
| 2026-02-16 11:36:01 | 2026-02-16 11:52:37 | 3 | -2.85 | 0 | 3 | RJT:3 |
| 2026-04-24 10:18:00 | 2026-04-24 10:48:10 | 3 | -2.83 | 0 | 3 | RJT:3 |

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
