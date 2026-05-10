# Trade-Level Analysis: AcaneM1_v2t_mom_strict_lastweek_20260501_d29_delay50_real_ticks_20260501_20260509.htm

## Summary
- Report net profit: `-2.71 Balance Drawdown Absolute`
- Reconstructed closed trades: `6`
- Reconstructed net: `-2.71`
- Win rate: `50.00%`
- Profit factor: `0.14`
- Unmatched exits: `0`
- Max price/PnL match error: `1.2672`

## Worst Engines
| engine | trades | net | win_rate | PF | avg | largest_loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| MOM | 6 | -2.71 | 50.00% | 0.14 | -0.45 | -1.28 |

## Best Engines
| engine | trades | net | win_rate | PF | avg | largest_loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| MOM | 6 | -2.71 | 50.00% | 0.14 | -0.45 | -1.28 |

## Worst Engine x Regime
| engine | regime_tag | trades | net | win_rate | PF | avg | largest_loss |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| MOM | RG | 3 | -1.88 | 33.33% | 0.06 | -0.63 | -1.28 |
| MOM | WG | 3 | -0.83 | 66.67% | 0.28 | -0.28 | -1.16 |

## Worst Engine x Entry Hour
| engine | entry_hour | trades | net | win_rate | PF | avg | largest_loss |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| MOM | 0 | 5 | -3.02 | 40.00% | 0.04 | -0.60 | -1.28 |

## Worst Months
| entry_month | trades | net | win_rate | PF | avg | largest_loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2026-05 | 6 | -2.71 | 50.00% | 0.14 | -0.45 | -1.28 |

## Worst Loss Clusters
| start | end | count | pnl | buy_losses | sell_losses | engines |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| 2026-05-01 00:01:00 | 2026-05-01 00:33:13 | 3 | -3.15 | 0 | 3 | MOM:3 |

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
