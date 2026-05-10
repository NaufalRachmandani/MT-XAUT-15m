# Trade-Level Analysis: AcaneM1_v2_friday_20260508_d29_delay50ms_real_ticks_20260508_20260509.htm

## Summary
- Report net profit: `-2.61 Balance Drawdown Absolute`
- Reconstructed closed trades: `8`
- Reconstructed net: `-2.61`
- Win rate: `25.00%`
- Profit factor: `0.24`
- Unmatched exits: `0`
- Max price/PnL match error: `1.1781`

## Worst Engines
| engine | trades | net | win_rate | PF | avg | largest_loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| MRV | 8 | -2.61 | 25.00% | 0.24 | -0.33 | -1.19 |

## Best Engines
| engine | trades | net | win_rate | PF | avg | largest_loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| MRV | 8 | -2.61 | 25.00% | 0.24 | -0.33 | -1.19 |

## Worst Engine x Regime
| engine | regime_tag | trades | net | win_rate | PF | avg | largest_loss |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| MRV | WG | 4 | -2.71 | 0.00% | 0.00 | -0.68 | -1.19 |
| MRV | RG | 4 | 0.10 | 50.00% | 1.14 | 0.03 | -0.63 |

## Worst Engine x Entry Hour
| engine | entry_hour | trades | net | win_rate | PF | avg | largest_loss |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |

## Worst Months
| entry_month | trades | net | win_rate | PF | avg | largest_loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2026-05 | 8 | -2.61 | 25.00% | 0.24 | -0.33 | -1.19 |

## Worst Loss Clusters
| start | end | count | pnl | buy_losses | sell_losses | engines |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| 2026-05-08 00:16:21 | 2026-05-08 07:03:14 | 6 | -3.43 | 4 | 2 | MRV:6 |

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
