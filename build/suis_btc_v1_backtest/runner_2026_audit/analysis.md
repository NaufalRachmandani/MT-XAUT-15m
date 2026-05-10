# Trade-Level Analysis: Suis_BTC_v1_runner_runner_BTCUSDm_2026_ytd_20260101_20260508.htm

## Summary
- Report net profit: `4.00 Balance Drawdown Absolute`
- Reconstructed closed trades: `73`
- Reconstructed net: `5.56`
- Win rate: `54.79%`
- Profit factor: `1.03`
- Unmatched exits: `0`
- Max price/PnL match error: `0.0095`

## Worst Engines
| engine | trades | net | win_rate | PF | avg | largest_loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| BO | 15 | -19.24 | 46.67% | 0.69 | -1.28 | -13.76 |
| RV | 8 | 4.82 | 75.00% | 1.64 | 0.60 | -4.87 |
| PB | 50 | 19.98 | 54.00% | 1.20 | 0.40 | -7.70 |

## Best Engines
| engine | trades | net | win_rate | PF | avg | largest_loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| PB | 50 | 19.98 | 54.00% | 1.20 | 0.40 | -7.70 |
| RV | 8 | 4.82 | 75.00% | 1.64 | 0.60 | -4.87 |
| BO | 15 | -19.24 | 46.67% | 0.69 | -1.28 | -13.76 |

## Worst Engine x Regime
| engine | regime_tag | trades | net | win_rate | PF | avg | largest_loss |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| BO |  | 15 | -19.24 | 46.67% | 0.69 | -1.28 | -13.76 |
| RV |  | 8 | 4.82 | 75.00% | 1.64 | 0.60 | -4.87 |
| PB |  | 50 | 19.98 | 54.00% | 1.20 | 0.40 | -7.70 |

## Worst Engine x Entry Hour
| engine | entry_hour | trades | net | win_rate | PF | avg | largest_loss |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| BO | 14 | 3 | -20.48 | 0.00% | 0.00 | -6.83 | -9.98 |
| PB | 0 | 5 | -19.09 | 0.00% | 0.00 | -3.82 | -4.91 |
| PB | 6 | 3 | -6.88 | 33.33% | 0.06 | -2.29 | -3.68 |
| PB | 21 | 5 | -0.04 | 80.00% | 0.99 | -0.01 | -7.70 |
| PB | 16 | 3 | 0.61 | 66.67% | 1.21 | 0.20 | -2.87 |
| PB | 8 | 3 | 3.82 | 66.67% | 1.61 | 1.27 | -6.26 |
| PB | 9 | 3 | 4.83 | 100.00% | 0.00 | 1.61 | 0.00 |
| PB | 15 | 3 | 10.98 | 66.67% | 3.94 | 3.66 | -3.74 |
| PB | 17 | 3 | 13.21 | 66.67% | 5.86 | 4.40 | -2.72 |

## Worst Months
| entry_month | trades | net | win_rate | PF | avg | largest_loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2026-01 | 73 | 5.56 | 54.79% | 1.03 | 0.08 | -13.76 |

## Worst Loss Clusters
| start | end | count | pnl | buy_losses | sell_losses | engines |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| 2026-01-04 04:45:00 | 2026-01-04 12:44:36 | 3 | -21.28 | 3 | 0 | BO:2, PB:1 |
| 2026-01-09 11:00:00 | 2026-01-09 15:26:42 | 3 | -20.27 | 0 | 3 | BO:1, PB:2 |

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
