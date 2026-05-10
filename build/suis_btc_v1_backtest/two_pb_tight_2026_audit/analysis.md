# Trade-Level Analysis: Suis_BTC_v1_two_pb_tight_two_pb_tight_BTCUSDm_2026_ytd_20260101_20260508.htm

## Summary
- Report net profit: `-15.30 Balance Drawdown Absolute`
- Reconstructed closed trades: `132`
- Reconstructed net: `-14.87`
- Win rate: `65.91%`
- Profit factor: `0.89`
- Unmatched exits: `0`
- Max price/PnL match error: `0.0081`

## Worst Engines
| engine | trades | net | win_rate | PF | avg | largest_loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| PB | 132 | -14.87 | 65.91% | 0.89 | -0.11 | -3.87 |

## Best Engines
| engine | trades | net | win_rate | PF | avg | largest_loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| PB | 132 | -14.87 | 65.91% | 0.89 | -0.11 | -3.87 |

## Worst Engine x Regime
| engine | regime_tag | trades | net | win_rate | PF | avg | largest_loss |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| PB |  | 132 | -14.87 | 65.91% | 0.89 | -0.11 | -3.87 |

## Worst Engine x Entry Hour
| engine | entry_hour | trades | net | win_rate | PF | avg | largest_loss |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| PB | 0 | 9 | -12.96 | 44.44% | 0.19 | -1.44 | -3.87 |
| PB | 1 | 8 | -10.89 | 50.00% | 0.29 | -1.36 | -3.84 |
| PB | 18 | 6 | -8.51 | 50.00% | 0.26 | -1.42 | -3.83 |
| PB | 23 | 4 | -8.00 | 25.00% | 0.30 | -2.00 | -3.83 |
| PB | 11 | 5 | -3.42 | 60.00% | 0.38 | -0.68 | -3.32 |
| PB | 2 | 5 | -2.60 | 60.00% | 0.56 | -0.52 | -3.82 |
| PB | 17 | 6 | -2.12 | 50.00% | 0.72 | -0.35 | -3.81 |
| PB | 5 | 3 | -1.39 | 66.67% | 0.53 | -0.46 | -2.98 |
| PB | 21 | 8 | -0.74 | 75.00% | 0.89 | -0.09 | -3.61 |
| PB | 7 | 3 | -0.12 | 66.67% | 0.94 | -0.04 | -2.03 |
| PB | 12 | 9 | 0.05 | 77.78% | 1.01 | 0.01 | -2.67 |
| PB | 15 | 7 | 0.27 | 42.86% | 1.04 | 0.04 | -3.85 |

## Worst Months
| entry_month | trades | net | win_rate | PF | avg | largest_loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2026-01 | 132 | -14.87 | 65.91% | 0.89 | -0.11 | -3.87 |

## Worst Loss Clusters
| start | end | count | pnl | buy_losses | sell_losses | engines |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| 2026-01-27 12:00:00 | 2026-01-27 18:55:36 | 4 | -11.75 | 0 | 4 | PB:4 |
| 2026-01-14 18:30:00 | 2026-01-14 23:31:36 | 3 | -11.07 | 3 | 0 | PB:3 |
| 2026-01-14 01:15:00 | 2026-01-14 11:19:26 | 3 | -10.45 | 3 | 0 | PB:3 |

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
