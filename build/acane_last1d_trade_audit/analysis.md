# Trade-Level Analysis: AcaneM1_v1_guarded_XAUUSDm_standard_last1d_livecheck_14982_20260507_20260508.htm

## Summary
- Report net profit: `26.66 Balance Drawdown Absolute`
- Reconstructed closed trades: `26`
- Reconstructed net: `26.66`
- Win rate: `69.23%`
- Profit factor: `2.63`
- Unmatched exits: `0`
- Max price/PnL match error: `4.6035`

## Worst Engines
| engine | trades | net | win_rate | PF | avg | largest_loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| MRV | 26 | 26.66 | 69.23% | 2.63 | 1.03 | -4.65 |

## Best Engines
| engine | trades | net | win_rate | PF | avg | largest_loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| MRV | 26 | 26.66 | 69.23% | 2.63 | 1.03 | -4.65 |

## Worst Engine x Regime
| engine | regime_tag | trades | net | win_rate | PF | avg | largest_loss |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| MRV | RG | 8 | 7.45 | 75.00% | 3.92 | 0.93 | -1.41 |
| MRV | WG | 18 | 19.21 | 66.67% | 2.40 | 1.07 | -4.65 |

## Worst Engine x Entry Hour
| engine | entry_hour | trades | net | win_rate | PF | avg | largest_loss |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| MRV | 1 | 5 | 0.12 | 60.00% | 1.02 | 0.02 | -4.65 |
| MRV | 0 | 4 | 0.36 | 50.00% | 1.12 | 0.09 | -1.73 |
| MRV | 17 | 4 | 6.93 | 75.00% | 5.91 | 1.73 | -1.41 |

## Worst Months
| entry_month | trades | net | win_rate | PF | avg | largest_loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2026-05 | 26 | 26.66 | 69.23% | 2.63 | 1.03 | -4.65 |

## Worst Loss Clusters
| start | end | count | pnl | buy_losses | sell_losses | engines |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| 2026-05-07 00:33:45 | 2026-05-07 01:06:25 | 4 | -10.18 | 2 | 2 | MRV:4 |

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
