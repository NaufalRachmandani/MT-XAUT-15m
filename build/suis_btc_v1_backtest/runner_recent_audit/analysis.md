# Trade-Level Analysis: Suis_BTC_v1_runner_runner_BTCUSDm_recent_2m_20260308_20260508.htm

## Summary
- Report net profit: `-14.18 Balance Drawdown Absolute`
- Reconstructed closed trades: `106`
- Reconstructed net: `-13.33`
- Win rate: `56.60%`
- Profit factor: `0.95`
- Unmatched exits: `0`
- Max price/PnL match error: `0.0097`

## Worst Engines
| engine | trades | net | win_rate | PF | avg | largest_loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| BO | 23 | -19.82 | 52.17% | 0.77 | -0.86 | -14.02 |
| RV | 14 | -14.76 | 42.86% | 0.43 | -1.05 | -6.76 |
| PB | 69 | 21.25 | 60.87% | 1.16 | 0.31 | -10.90 |

## Best Engines
| engine | trades | net | win_rate | PF | avg | largest_loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| PB | 69 | 21.25 | 60.87% | 1.16 | 0.31 | -10.90 |
| RV | 14 | -14.76 | 42.86% | 0.43 | -1.05 | -6.76 |
| BO | 23 | -19.82 | 52.17% | 0.77 | -0.86 | -14.02 |

## Worst Engine x Regime
| engine | regime_tag | trades | net | win_rate | PF | avg | largest_loss |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| BO |  | 23 | -19.82 | 52.17% | 0.77 | -0.86 | -14.02 |
| RV |  | 14 | -14.76 | 42.86% | 0.43 | -1.05 | -6.76 |
| PB |  | 69 | 21.25 | 60.87% | 1.16 | 0.31 | -10.90 |

## Worst Engine x Entry Hour
| engine | entry_hour | trades | net | win_rate | PF | avg | largest_loss |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| PB | 16 | 3 | -12.13 | 33.33% | 0.23 | -4.04 | -9.57 |
| PB | 2 | 4 | -11.89 | 25.00% | 0.01 | -2.97 | -6.72 |
| PB | 11 | 5 | -11.03 | 20.00% | 0.37 | -2.21 | -6.49 |
| PB | 15 | 4 | -7.69 | 50.00% | 0.45 | -1.92 | -10.90 |
| PB | 13 | 3 | -6.62 | 33.33% | 0.29 | -2.21 | -5.49 |
| PB | 0 | 4 | -4.89 | 75.00% | 0.49 | -1.22 | -9.65 |
| PB | 17 | 4 | 3.94 | 100.00% | 0.00 | 0.98 | 0.00 |
| PB | 20 | 4 | 4.12 | 50.00% | 1.37 | 1.03 | -6.95 |
| PB | 9 | 5 | 5.04 | 60.00% | 1.87 | 1.01 | -3.80 |
| PB | 7 | 4 | 5.91 | 100.00% | 0.00 | 1.48 | 0.00 |
| PB | 22 | 3 | 8.47 | 66.67% | 3.51 | 2.82 | -3.37 |
| PB | 4 | 5 | 13.13 | 60.00% | 2.42 | 2.63 | -5.91 |

## Worst Months
| entry_month | trades | net | win_rate | PF | avg | largest_loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2026-03 | 106 | -13.33 | 56.60% | 0.95 | -0.13 | -14.02 |

## Worst Loss Clusters
| start | end | count | pnl | buy_losses | sell_losses | engines |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| 2026-03-10 09:30:00 | 2026-03-10 13:34:42 | 3 | -22.32 | 3 | 0 | BO:1, PB:2 |
| 2026-03-20 16:45:00 | 2026-03-20 21:18:29 | 3 | -15.52 | 0 | 3 | PB:3 |
| 2026-03-24 01:30:00 | 2026-03-24 13:15:00 | 4 | -15.15 | 4 | 0 | BO:1, PB:3 |
| 2026-03-08 09:45:00 | 2026-03-08 11:41:37 | 3 | -14.34 | 2 | 1 | BO:1, PB:1, RV:1 |

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
