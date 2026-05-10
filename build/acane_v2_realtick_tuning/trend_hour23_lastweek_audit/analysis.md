# Trade-Level Analysis: AcaneM1_v2t_trend_hour23_lastweek_20260501_d29_delay50_real_ticks_20260501_20260509.htm

## Summary
- Report net profit: `-2.15 Balance Drawdown Absolute`
- Reconstructed closed trades: `8`
- Reconstructed net: `-2.15`
- Win rate: `25.00%`
- Profit factor: `0.32`
- Unmatched exits: `0`
- Max price/PnL match error: `0.7722`

## Worst Engines
| engine | trades | net | win_rate | PF | avg | largest_loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| MOM | 8 | -2.15 | 25.00% | 0.32 | -0.27 | -0.76 |

## Best Engines
| engine | trades | net | win_rate | PF | avg | largest_loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| MOM | 8 | -2.15 | 25.00% | 0.32 | -0.27 | -0.76 |

## Worst Engine x Regime
| engine | regime_tag | trades | net | win_rate | PF | avg | largest_loss |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| MOM | RG | 2 | -1.31 | 0.00% | 0.00 | -0.66 | -0.76 |
| MOM | WG | 6 | -0.84 | 33.33% | 0.55 | -0.14 | -0.64 |

## Worst Engine x Entry Hour
| engine | entry_hour | trades | net | win_rate | PF | avg | largest_loss |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| MOM | 23 | 8 | -2.15 | 25.00% | 0.32 | -0.27 | -0.76 |

## Worst Months
| entry_month | trades | net | win_rate | PF | avg | largest_loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2026-05 | 8 | -2.15 | 25.00% | 0.32 | -0.27 | -0.76 |

## Worst Loss Clusters
| start | end | count | pnl | buy_losses | sell_losses | engines |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| 2026-05-03 23:02:01 | 2026-05-03 23:33:19 | 3 | -1.30 | 2 | 1 | MOM:3 |

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
