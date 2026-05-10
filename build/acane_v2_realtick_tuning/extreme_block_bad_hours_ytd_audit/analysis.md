# Trade-Level Analysis: AcaneM1_v2t_extreme_block_bad_hours_ytd_2026_d29_delay50_real_ticks_20260101_20260509.htm

## Summary
- Report net profit: `1.19 Balance Drawdown Absolute`
- Reconstructed closed trades: `9`
- Reconstructed net: `1.19`
- Win rate: `66.67%`
- Profit factor: `1.96`
- Unmatched exits: `0`
- Max price/PnL match error: `1.1385`

## Worst Engines
| engine | trades | net | win_rate | PF | avg | largest_loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| MRV | 9 | 1.19 | 66.67% | 1.96 | 0.13 | -0.61 |

## Best Engines
| engine | trades | net | win_rate | PF | avg | largest_loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| MRV | 9 | 1.19 | 66.67% | 1.96 | 0.13 | -0.61 |

## Worst Engine x Regime
| engine | regime_tag | trades | net | win_rate | PF | avg | largest_loss |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| MRV | WG | 4 | -0.42 | 50.00% | 0.59 | -0.10 | -0.61 |
| MRV | RG | 5 | 1.61 | 80.00% | 8.32 | 0.32 | -0.22 |

## Worst Engine x Entry Hour
| engine | entry_hour | trades | net | win_rate | PF | avg | largest_loss |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |

## Worst Months
| entry_month | trades | net | win_rate | PF | avg | largest_loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2026-03 | 3 | -0.52 | 33.33% | 0.37 | -0.17 | -0.61 |
| 2026-05 | 1 | 0.03 | 100.00% | 0.00 | 0.03 | 0.00 |
| 2026-01 | 1 | 0.04 | 100.00% | 0.00 | 0.04 | 0.00 |
| 2026-04 | 4 | 1.64 | 75.00% | 5.00 | 0.41 | -0.41 |

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
