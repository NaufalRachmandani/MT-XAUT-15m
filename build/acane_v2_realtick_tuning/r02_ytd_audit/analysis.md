# Trade-Level Analysis: AcaneM1_v2t_r02_no_bad_hours_ytd_2026_d29_delay100_real_ticks_20260101_20260509.htm

## Summary
- Report net profit: `-4.55 Balance Drawdown Absolute`
- Reconstructed closed trades: `16`
- Reconstructed net: `-4.55`
- Win rate: `43.75%`
- Profit factor: `0.33`
- Unmatched exits: `0`
- Max price/PnL match error: `1.1979`

## Worst Engines
| engine | trades | net | win_rate | PF | avg | largest_loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| RCL | 9 | -2.49 | 44.44% | 0.30 | -0.28 | -1.21 |
| MOM | 7 | -2.06 | 42.86% | 0.36 | -0.29 | -1.14 |

## Best Engines
| engine | trades | net | win_rate | PF | avg | largest_loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| MOM | 7 | -2.06 | 42.86% | 0.36 | -0.29 | -1.14 |
| RCL | 9 | -2.49 | 44.44% | 0.30 | -0.28 | -1.21 |

## Worst Engine x Regime
| engine | regime_tag | trades | net | win_rate | PF | avg | largest_loss |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| RCL | RG | 9 | -2.49 | 44.44% | 0.30 | -0.28 | -1.21 |
| MOM | RG | 7 | -2.06 | 42.86% | 0.36 | -0.29 | -1.14 |

## Worst Engine x Entry Hour
| engine | entry_hour | trades | net | win_rate | PF | avg | largest_loss |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| RCL | 4 | 5 | -2.70 | 40.00% | 0.01 | -0.54 | -1.21 |
| RCL | 5 | 3 | -0.81 | 33.33% | 0.02 | -0.27 | -0.71 |
| MOM | 5 | 3 | -0.12 | 66.67% | 0.89 | -0.04 | -1.14 |

## Worst Months
| entry_month | trades | net | win_rate | PF | avg | largest_loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2026-01 | 16 | -4.55 | 43.75% | 0.33 | -0.28 | -1.21 |

## Worst Loss Clusters
| start | end | count | pnl | buy_losses | sell_losses | engines |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| 2026-01-02 04:00:00 | 2026-01-02 07:35:48 | 6 | -5.14 | 6 | 0 | MOM:4, RCL:2 |
| 2026-01-05 04:28:00 | 2026-01-05 05:05:02 | 3 | -1.63 | 3 | 0 | RCL:3 |

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
