# Trade-Level Analysis: Suis_BTC_v1_base_base_BTCUSDm_2026_ytd_20260101_20260508.htm

## Summary
- Report net profit: `-6.66 Balance Drawdown Absolute`
- Reconstructed closed trades: `83`
- Reconstructed net: `-5.10`
- Win rate: `49.40%`
- Profit factor: `0.97`
- Unmatched exits: `0`
- Max price/PnL match error: `0.0092`

## Worst Engines
| engine | trades | net | win_rate | PF | avg | largest_loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| BO | 21 | -10.54 | 42.86% | 0.85 | -0.50 | -9.98 |
| PB | 55 | 2.71 | 50.91% | 1.03 | 0.05 | -8.16 |
| RV | 7 | 2.73 | 57.14% | 1.23 | 0.39 | -4.87 |

## Best Engines
| engine | trades | net | win_rate | PF | avg | largest_loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| RV | 7 | 2.73 | 57.14% | 1.23 | 0.39 | -4.87 |
| PB | 55 | 2.71 | 50.91% | 1.03 | 0.05 | -8.16 |
| BO | 21 | -10.54 | 42.86% | 0.85 | -0.50 | -9.98 |

## Worst Engine x Regime
| engine | regime_tag | trades | net | win_rate | PF | avg | largest_loss |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| BO |  | 21 | -10.54 | 42.86% | 0.85 | -0.50 | -9.98 |
| PB |  | 55 | 2.71 | 50.91% | 1.03 | 0.05 | -8.16 |
| RV |  | 7 | 2.73 | 57.14% | 1.23 | 0.39 | -4.87 |

## Worst Engine x Entry Hour
| engine | entry_hour | trades | net | win_rate | PF | avg | largest_loss |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| BO | 14 | 4 | -27.01 | 0.00% | 0.00 | -6.75 | -9.98 |
| PB | 12 | 3 | -8.77 | 0.00% | 0.00 | -2.92 | -3.72 |
| PB | 6 | 3 | -6.32 | 33.33% | 0.14 | -2.11 | -3.68 |
| PB | 1 | 4 | -6.15 | 25.00% | 0.58 | -1.54 | -6.24 |
| PB | 0 | 6 | -5.43 | 16.67% | 0.64 | -0.90 | -4.91 |
| PB | 11 | 3 | -4.74 | 33.33% | 0.14 | -1.58 | -2.94 |
| PB | 4 | 3 | 0.41 | 66.67% | 1.05 | 0.14 | -8.16 |
| PB | 17 | 3 | 2.18 | 66.67% | 1.80 | 0.73 | -2.72 |
| PB | 9 | 3 | 3.55 | 100.00% | 0.00 | 1.18 | 0.00 |
| PB | 8 | 3 | 5.32 | 66.67% | 2.70 | 1.77 | -3.13 |
| PB | 21 | 4 | 10.59 | 100.00% | 0.00 | 2.65 | 0.00 |

## Worst Months
| entry_month | trades | net | win_rate | PF | avg | largest_loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2026-01 | 83 | -5.10 | 49.40% | 0.97 | -0.06 | -9.98 |

## Worst Loss Clusters
| start | end | count | pnl | buy_losses | sell_losses | engines |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| 2026-01-09 07:00:00 | 2026-01-09 15:26:42 | 4 | -22.75 | 1 | 3 | BO:1, PB:3 |
| 2026-01-04 04:45:00 | 2026-01-04 12:44:36 | 3 | -13.28 | 3 | 0 | BO:2, PB:1 |

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
