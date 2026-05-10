# Trade-Level Analysis: AcaneM1_v1_guarded_debug_v1_old_2025_current_d29_lev12000_20250101_20260509.htm

## Summary
- Report net profit: `-3.21 Balance Drawdown Absolute`
- Reconstructed closed trades: `65`
- Reconstructed net: `-3.21`
- Win rate: `40.00%`
- Profit factor: `0.65`
- Unmatched exits: `0`
- Max price/PnL match error: `0.6732`

## Worst Engines
| engine | trades | net | win_rate | PF | avg | largest_loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| MRV | 65 | -3.21 | 40.00% | 0.65 | -0.05 | -0.53 |

## Best Engines
| engine | trades | net | win_rate | PF | avg | largest_loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| MRV | 65 | -3.21 | 40.00% | 0.65 | -0.05 | -0.53 |

## Worst Engine x Regime
| engine | regime_tag | trades | net | win_rate | PF | avg | largest_loss |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| MRV | RG | 22 | -2.31 | 36.36% | 0.32 | -0.10 | -0.39 |
| MRV | WG | 43 | -0.90 | 41.86% | 0.85 | -0.02 | -0.53 |

## Worst Engine x Entry Hour
| engine | entry_hour | trades | net | win_rate | PF | avg | largest_loss |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| MRV | 7 | 5 | -0.97 | 20.00% | 0.03 | -0.19 | -0.33 |
| MRV | 19 | 3 | -0.69 | 0.00% | 0.00 | -0.23 | -0.24 |
| MRV | 18 | 3 | -0.58 | 33.33% | 0.06 | -0.19 | -0.39 |
| MRV | 11 | 5 | -0.50 | 40.00% | 0.28 | -0.10 | -0.24 |
| MRV | 0 | 3 | -0.48 | 33.33% | 0.08 | -0.16 | -0.30 |
| MRV | 10 | 3 | -0.39 | 33.33% | 0.09 | -0.13 | -0.22 |
| MRV | 23 | 8 | -0.19 | 50.00% | 0.79 | -0.02 | -0.24 |
| MRV | 17 | 6 | 0.20 | 50.00% | 1.29 | 0.03 | -0.24 |
| MRV | 1 | 10 | 0.38 | 60.00% | 1.61 | 0.04 | -0.23 |
| MRV | 9 | 3 | 0.42 | 66.67% | 2.56 | 0.14 | -0.27 |
| MRV | 12 | 5 | 0.86 | 60.00% | 2.79 | 0.17 | -0.25 |

## Worst Months
| entry_month | trades | net | win_rate | PF | avg | largest_loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2025-01 | 65 | -3.21 | 40.00% | 0.65 | -0.05 | -0.53 |

## Worst Loss Clusters
| start | end | count | pnl | buy_losses | sell_losses | engines |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| 2025-01-02 03:24:38 | 2025-01-03 01:58:44 | 37 | -8.84 | 21 | 16 | MRV:37 |

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
