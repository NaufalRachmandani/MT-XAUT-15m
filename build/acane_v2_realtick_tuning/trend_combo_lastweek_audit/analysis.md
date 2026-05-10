# Trade-Level Analysis: AcaneM1_v2t_trend_combo_lastweek_20260501_d29_delay50_real_ticks_20260501_20260509.htm

## Summary
- Report net profit: `-2.65 Balance Drawdown Absolute`
- Reconstructed closed trades: `11`
- Reconstructed net: `-2.65`
- Win rate: `36.36%`
- Profit factor: `0.43`
- Unmatched exits: `0`
- Max price/PnL match error: `1.1088`

## Worst Engines
| engine | trades | net | win_rate | PF | avg | largest_loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| MOM | 11 | -2.65 | 36.36% | 0.43 | -0.24 | -1.12 |

## Best Engines
| engine | trades | net | win_rate | PF | avg | largest_loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| MOM | 11 | -2.65 | 36.36% | 0.43 | -0.24 | -1.12 |

## Worst Engine x Regime
| engine | regime_tag | trades | net | win_rate | PF | avg | largest_loss |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| MOM | WG | 5 | -1.65 | 40.00% | 0.17 | -0.33 | -0.87 |
| MOM | RG | 6 | -1.00 | 33.33% | 0.62 | -0.17 | -1.12 |

## Worst Engine x Entry Hour
| engine | entry_hour | trades | net | win_rate | PF | avg | largest_loss |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| MOM | 0 | 5 | -2.08 | 40.00% | 0.26 | -0.42 | -1.12 |
| MOM | 1 | 4 | -0.43 | 25.00% | 0.69 | -0.11 | -0.70 |

## Worst Months
| entry_month | trades | net | win_rate | PF | avg | largest_loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2026-05 | 11 | -2.65 | 36.36% | 0.43 | -0.24 | -1.12 |

## Worst Loss Clusters
| start | end | count | pnl | buy_losses | sell_losses | engines |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| 2026-05-01 00:01:00 | 2026-05-01 02:05:46 | 7 | -4.63 | 2 | 5 | MOM:7 |

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
