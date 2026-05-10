# Trade-Level Analysis: Suis_BTC_v1_runner_runner_BTCUSDm_2025_current_20250101_20260508.htm

## Summary
- Report net profit: `-32.47 Balance Drawdown Absolute`
- Reconstructed closed trades: `33`
- Reconstructed net: `-32.47`
- Win rate: `36.36%`
- Profit factor: `0.56`
- Unmatched exits: `0`
- Max price/PnL match error: `0.0087`

## Worst Engines
| engine | trades | net | win_rate | PF | avg | largest_loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| PB | 26 | -19.87 | 38.46% | 0.63 | -0.76 | -9.66 |
| BO | 4 | -9.38 | 25.00% | 0.36 | -2.35 | -7.27 |
| RV | 3 | -3.22 | 33.33% | 0.42 | -1.07 | -3.63 |

## Best Engines
| engine | trades | net | win_rate | PF | avg | largest_loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| RV | 3 | -3.22 | 33.33% | 0.42 | -1.07 | -3.63 |
| BO | 4 | -9.38 | 25.00% | 0.36 | -2.35 | -7.27 |
| PB | 26 | -19.87 | 38.46% | 0.63 | -0.76 | -9.66 |

## Worst Engine x Regime
| engine | regime_tag | trades | net | win_rate | PF | avg | largest_loss |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| PB |  | 26 | -19.87 | 38.46% | 0.63 | -0.76 | -9.66 |
| BO |  | 4 | -9.38 | 25.00% | 0.36 | -2.35 | -7.27 |
| RV |  | 3 | -3.22 | 33.33% | 0.42 | -1.07 | -3.63 |

## Worst Engine x Entry Hour
| engine | entry_hour | trades | net | win_rate | PF | avg | largest_loss |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| PB | 2 | 4 | -2.63 | 50.00% | 0.82 | -0.66 | -9.66 |

## Worst Months
| entry_month | trades | net | win_rate | PF | avg | largest_loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2025-01 | 33 | -32.47 | 36.36% | 0.56 | -0.98 | -9.66 |

## Worst Loss Clusters
| start | end | count | pnl | buy_losses | sell_losses | engines |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| 2025-01-03 02:15:00 | 2025-01-03 14:10:27 | 7 | -24.83 | 3 | 4 | PB:6, RV:1 |
| 2025-01-05 05:30:00 | 2025-01-05 12:11:04 | 3 | -8.25 | 3 | 0 | PB:2, RV:1 |
| 2025-01-04 22:45:00 | 2025-01-05 01:36:17 | 3 | -6.06 | 3 | 0 | PB:3 |
| 2025-01-04 12:15:00 | 2025-01-04 13:53:25 | 3 | -5.61 | 0 | 3 | PB:3 |

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
