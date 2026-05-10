# Trade-Level Analysis: AcaneM1_v2t_extreme_only_current_2025_d29_delay50_real_ticks_20250101_20260509.htm

## Summary
- Report net profit: `-0.98 Balance Drawdown Absolute`
- Reconstructed closed trades: `33`
- Reconstructed net: `-0.98`
- Win rate: `45.45%`
- Profit factor: `0.82`
- Unmatched exits: `0`
- Max price/PnL match error: `0.7326`

## Worst Engines
| engine | trades | net | win_rate | PF | avg | largest_loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| MRV | 33 | -0.98 | 45.45% | 0.82 | -0.03 | -0.70 |

## Best Engines
| engine | trades | net | win_rate | PF | avg | largest_loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| MRV | 33 | -0.98 | 45.45% | 0.82 | -0.03 | -0.70 |

## Worst Engine x Regime
| engine | regime_tag | trades | net | win_rate | PF | avg | largest_loss |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| MRV | WG | 19 | -1.42 | 36.84% | 0.64 | -0.07 | -0.70 |
| MRV | RG | 14 | 0.44 | 57.14% | 1.28 | 0.03 | -0.44 |

## Worst Engine x Entry Hour
| engine | entry_hour | trades | net | win_rate | PF | avg | largest_loss |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| MRV | 2 | 3 | -0.74 | 0.00% | 0.00 | -0.25 | -0.27 |
| MRV | 19 | 4 | -0.04 | 75.00% | 0.81 | -0.01 | -0.21 |
| MRV | 18 | 3 | 0.03 | 66.67% | 1.09 | 0.01 | -0.32 |
| MRV | 10 | 3 | 0.18 | 66.67% | 1.56 | 0.06 | -0.32 |

## Worst Months
| entry_month | trades | net | win_rate | PF | avg | largest_loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2025-09 | 5 | -1.46 | 0.00% | 0.00 | -0.29 | -0.70 |
| 2025-07 | 7 | -1.25 | 14.29% | 0.35 | -0.18 | -0.44 |
| 2025-08 | 3 | -0.86 | 33.33% | 0.05 | -0.29 | -0.54 |
| 2025-03 | 2 | -0.16 | 50.00% | 0.33 | -0.08 | -0.24 |
| 2025-04 | 1 | 0.04 | 100.00% | 0.00 | 0.04 | 0.00 |
| 2025-01 | 5 | 0.40 | 60.00% | 1.91 | 0.08 | -0.22 |
| 2025-05 | 1 | 0.74 | 100.00% | 0.00 | 0.74 | 0.00 |
| 2025-02 | 9 | 1.57 | 77.78% | 3.91 | 0.17 | -0.32 |

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
