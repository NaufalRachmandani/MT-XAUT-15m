# Trade-Level Analysis: AcaneM1_v2t_extreme_block_bad_hours_current_2025_d29_delay50_real_ticks_20250101_20260509.htm

## Summary
- Report net profit: `3.59 Balance Drawdown Absolute`
- Reconstructed closed trades: `40`
- Reconstructed net: `3.59`
- Win rate: `62.50%`
- Profit factor: `1.86`
- Unmatched exits: `0`
- Max price/PnL match error: `1.1385`

## Worst Engines
| engine | trades | net | win_rate | PF | avg | largest_loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| MRV | 40 | 3.59 | 62.50% | 1.86 | 0.09 | -0.61 |

## Best Engines
| engine | trades | net | win_rate | PF | avg | largest_loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| MRV | 40 | 3.59 | 62.50% | 1.86 | 0.09 | -0.61 |

## Worst Engine x Regime
| engine | regime_tag | trades | net | win_rate | PF | avg | largest_loss |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| MRV | WG | 22 | 0.63 | 50.00% | 1.19 | 0.03 | -0.61 |
| MRV | RG | 18 | 2.96 | 77.78% | 4.22 | 0.16 | -0.25 |

## Worst Engine x Entry Hour
| engine | entry_hour | trades | net | win_rate | PF | avg | largest_loss |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| MRV | 13 | 3 | -0.60 | 0.00% | 0.00 | -0.20 | -0.36 |
| MRV | 18 | 5 | -0.36 | 60.00% | 0.51 | -0.07 | -0.41 |
| MRV | 12 | 4 | -0.08 | 50.00% | 0.89 | -0.02 | -0.54 |
| MRV | 19 | 4 | -0.04 | 75.00% | 0.81 | -0.01 | -0.21 |
| MRV | 10 | 3 | 0.18 | 66.67% | 1.56 | 0.06 | -0.32 |
| MRV | 6 | 3 | 1.76 | 66.67% | 0.00 | 0.59 | 0.00 |

## Worst Months
| entry_month | trades | net | win_rate | PF | avg | largest_loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2026-03 | 3 | -0.52 | 33.33% | 0.37 | -0.17 | -0.61 |
| 2025-08 | 2 | -0.49 | 50.00% | 0.09 | -0.25 | -0.54 |
| 2025-09 | 3 | -0.46 | 0.00% | 0.00 | -0.15 | -0.25 |
| 2025-12 | 2 | -0.27 | 50.00% | 0.25 | -0.14 | -0.36 |
| 2025-03 | 2 | -0.16 | 50.00% | 0.33 | -0.08 | -0.24 |
| 2026-05 | 1 | 0.03 | 100.00% | 0.00 | 0.03 | 0.00 |
| 2026-01 | 1 | 0.04 | 100.00% | 0.00 | 0.04 | 0.00 |
| 2025-07 | 2 | 0.34 | 50.00% | 2.06 | 0.17 | -0.32 |

## Worst Loss Clusters
| start | end | count | pnl | buy_losses | sell_losses | engines |
| --- | --- | ---: | ---: | ---: | ---: | --- |

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
