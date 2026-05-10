# Trade-Level Analysis: Suis_BTC_v1_base_base_BTCUSDm_recent_2m_20260308_20260508.htm

## Summary
- Report net profit: `-16.35 Balance Drawdown Absolute`
- Reconstructed closed trades: `111`
- Reconstructed net: `-15.36`
- Win rate: `54.05%`
- Profit factor: `0.94`
- Unmatched exits: `0`
- Max price/PnL match error: `0.0089`

## Worst Engines
| engine | trades | net | win_rate | PF | avg | largest_loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| BO | 26 | -54.76 | 42.31% | 0.53 | -2.11 | -14.02 |
| RV | 14 | -16.29 | 35.71% | 0.45 | -1.16 | -6.76 |
| PB | 71 | 55.69 | 61.97% | 1.42 | 0.78 | -10.90 |

## Best Engines
| engine | trades | net | win_rate | PF | avg | largest_loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| PB | 71 | 55.69 | 61.97% | 1.42 | 0.78 | -10.90 |
| RV | 14 | -16.29 | 35.71% | 0.45 | -1.16 | -6.76 |
| BO | 26 | -54.76 | 42.31% | 0.53 | -2.11 | -14.02 |

## Worst Engine x Regime
| engine | regime_tag | trades | net | win_rate | PF | avg | largest_loss |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| BO |  | 26 | -54.76 | 42.31% | 0.53 | -2.11 | -14.02 |
| RV |  | 14 | -16.29 | 35.71% | 0.45 | -1.16 | -6.76 |
| PB |  | 71 | 55.69 | 61.97% | 1.42 | 0.78 | -10.90 |

## Worst Engine x Entry Hour
| engine | entry_hour | trades | net | win_rate | PF | avg | largest_loss |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| BO | 8 | 3 | -17.56 | 33.33% | 0.21 | -5.85 | -12.29 |
| PB | 2 | 5 | -12.53 | 20.00% | 0.10 | -2.51 | -6.72 |
| PB | 11 | 4 | -7.64 | 25.00% | 0.41 | -1.91 | -6.49 |
| PB | 21 | 3 | -5.76 | 33.33% | 0.29 | -1.92 | -4.07 |
| PB | 0 | 4 | -5.74 | 75.00% | 0.41 | -1.44 | -9.65 |
| PB | 16 | 3 | -5.17 | 33.33% | 0.67 | -1.72 | -9.57 |
| PB | 15 | 4 | -4.74 | 50.00% | 0.66 | -1.19 | -10.90 |
| RV | 8 | 3 | -1.95 | 33.33% | 0.65 | -0.65 | -3.17 |
| PB | 20 | 3 | -0.81 | 33.33% | 0.89 | -0.27 | -4.16 |
| PB | 9 | 5 | -0.24 | 60.00% | 0.98 | -0.05 | -6.14 |
| BO | 0 | 4 | 1.71 | 50.00% | 1.10 | 0.43 | -12.57 |
| PB | 7 | 3 | 4.26 | 100.00% | 0.00 | 1.42 | 0.00 |

## Worst Months
| entry_month | trades | net | win_rate | PF | avg | largest_loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2026-03 | 111 | -15.36 | 54.05% | 0.94 | -0.14 | -14.02 |

## Worst Loss Clusters
| start | end | count | pnl | buy_losses | sell_losses | engines |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| 2026-03-23 21:30:00 | 2026-03-24 13:40:28 | 5 | -28.42 | 5 | 0 | BO:1, PB:4 |
| 2026-03-20 11:15:00 | 2026-03-20 21:18:29 | 5 | -26.44 | 2 | 3 | PB:4, RV:1 |
| 2026-03-08 09:45:00 | 2026-03-08 11:41:37 | 3 | -10.53 | 2 | 1 | BO:1, PB:1, RV:1 |

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
