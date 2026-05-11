# Trade-Level Analysis: InvictusForward-8-Tuned_d29_last_week_XAUUSD_M15_d29_USD_lev2000_delay100_model4_20260501_20260510.htm

## Summary
- Report net profit: `-30.65 Balance Drawdown Absolute`
- Reconstructed closed trades: `3`
- Reconstructed net: `-30.65`
- Win rate: `33.33%`
- Profit factor: `0.08`
- Unmatched exits: `0`
- Max price/PnL match error: `20.3346`

## Worst Engines
| engine | trades | net | win_rate | PF | avg | largest_loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
|  | 3 | -30.65 | 33.33% | 0.08 | -10.22 | -20.54 |

## Best Engines
| engine | trades | net | win_rate | PF | avg | largest_loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
|  | 3 | -30.65 | 33.33% | 0.08 | -10.22 | -20.54 |

## Worst Engine x Regime
| engine | regime_tag | trades | net | win_rate | PF | avg | largest_loss |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
|  |  | 3 | -30.65 | 33.33% | 0.08 | -10.22 | -20.54 |

## Worst Engine x Entry Hour
| engine | entry_hour | trades | net | win_rate | PF | avg | largest_loss |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |

## Worst Months
| entry_month | trades | net | win_rate | PF | avg | largest_loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2026-05 | 3 | -30.65 | 33.33% | 0.08 | -10.22 | -20.54 |

## Worst Loss Clusters
| start | end | count | pnl | buy_losses | sell_losses | engines |
| --- | --- | ---: | ---: | ---: | ---: | --- |

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
