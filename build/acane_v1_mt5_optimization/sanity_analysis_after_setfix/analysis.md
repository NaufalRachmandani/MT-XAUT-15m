# Trade-Level Analysis: AcaneM1_v1_sanity_20260501_20260510_d100_lev12000_delay100_model4_20260501_20260510.htm

## Summary
- Report net profit: `-15.04 Balance Drawdown Absolute`
- Reconstructed closed trades: `44`
- Reconstructed net: `-15.04`
- Win rate: `45.45%`
- Profit factor: `0.70`
- Unmatched exits: `0`
- Max price/PnL match error: `3.8115`

## Worst Engines
| engine | trades | net | win_rate | PF | avg | largest_loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| TPL | 42 | -14.34 | 45.24% | 0.70 | -0.34 | -2.89 |
| CBK | 2 | -0.70 | 50.00% | 0.53 | -0.35 | -1.49 |

## Best Engines
| engine | trades | net | win_rate | PF | avg | largest_loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| CBK | 2 | -0.70 | 50.00% | 0.53 | -0.35 | -1.49 |
| TPL | 42 | -14.34 | 45.24% | 0.70 | -0.34 | -2.89 |

## Worst Engine x Regime
| engine | regime_tag | trades | net | win_rate | PF | avg | largest_loss |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| TPL |  | 42 | -14.34 | 45.24% | 0.70 | -0.34 | -2.89 |
| CBK | WG | 1 | -1.49 | 0.00% | 0.00 | -1.49 | -1.49 |
| CBK | RG | 1 | 0.79 | 100.00% | 0.00 | 0.79 | 0.00 |

## Worst Engine x Entry Hour
| engine | entry_hour | trades | net | win_rate | PF | avg | largest_loss |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| TPL | 7 | 8 | -11.56 | 25.00% | 0.23 | -1.44 | -2.73 |
| TPL | 11 | 8 | -6.42 | 37.50% | 0.49 | -0.80 | -2.81 |
| TPL | 8 | 6 | -3.52 | 33.33% | 0.60 | -0.59 | -2.37 |
| TPL | 9 | 6 | 2.53 | 50.00% | 1.88 | 0.42 | -2.83 |
| TPL | 4 | 5 | 2.84 | 60.00% | 1.80 | 0.57 | -2.19 |
| TPL | 5 | 3 | 3.23 | 100.00% | 0.00 | 1.08 | 0.00 |
| TPL | 10 | 4 | 4.21 | 75.00% | 422.00 | 1.05 | -0.01 |

## Worst Months
| entry_month | trades | net | win_rate | PF | avg | largest_loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2026-05 | 44 | -15.04 | 45.45% | 0.70 | -0.34 | -2.89 |

## Worst Loss Clusters
| start | end | count | pnl | buy_losses | sell_losses | engines |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| 2026-05-06 04:36:00 | 2026-05-06 14:41:50 | 10 | -20.08 | 10 | 0 | TPL:10 |
| 2026-05-07 07:35:00 | 2026-05-07 07:52:59 | 4 | -10.37 | 4 | 0 | TPL:4 |
| 2026-05-08 11:17:00 | 2026-05-08 11:30:19 | 4 | -9.84 | 4 | 0 | TPL:4 |
| 2026-05-04 08:24:00 | 2026-05-04 08:39:22 | 3 | -6.79 | 0 | 3 | TPL:3 |

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
