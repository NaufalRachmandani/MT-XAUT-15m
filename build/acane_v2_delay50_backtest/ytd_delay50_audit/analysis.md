# Trade-Level Analysis: AcaneM1_v2_ytd_2026_d29_delay50ms_real_ticks_20260101_20260509.htm

## Summary
- Report net profit: `-3.66 Balance Drawdown Absolute`
- Reconstructed closed trades: `28`
- Reconstructed net: `-3.66`
- Win rate: `50.00%`
- Profit factor: `0.42`
- Unmatched exits: `0`
- Max price/PnL match error: `0.8514`

## Worst Engines
| engine | trades | net | win_rate | PF | avg | largest_loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| MRV | 28 | -3.66 | 50.00% | 0.42 | -0.13 | -0.86 |

## Best Engines
| engine | trades | net | win_rate | PF | avg | largest_loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| MRV | 28 | -3.66 | 50.00% | 0.42 | -0.13 | -0.86 |

## Worst Engine x Regime
| engine | regime_tag | trades | net | win_rate | PF | avg | largest_loss |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| MRV | WG | 22 | -3.58 | 45.45% | 0.34 | -0.16 | -0.86 |
| MRV | RG | 6 | -0.08 | 66.67% | 0.91 | -0.01 | -0.59 |

## Worst Engine x Entry Hour
| engine | entry_hour | trades | net | win_rate | PF | avg | largest_loss |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| MRV | 6 | 3 | -1.43 | 0.00% | 0.00 | -0.48 | -0.86 |
| MRV | 4 | 3 | -1.13 | 0.00% | 0.00 | -0.38 | -0.63 |
| MRV | 7 | 9 | 0.13 | 66.67% | 1.10 | 0.01 | -0.86 |

## Worst Months
| entry_month | trades | net | win_rate | PF | avg | largest_loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2026-01 | 28 | -3.66 | 50.00% | 0.42 | -0.13 | -0.86 |

## Worst Loss Clusters
| start | end | count | pnl | buy_losses | sell_losses | engines |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| 2026-01-05 04:24:59 | 2026-01-05 07:40:55 | 5 | -2.26 | 1 | 4 | MRV:5 |
| 2026-01-02 04:24:20 | 2026-01-02 12:09:01 | 6 | -2.20 | 5 | 1 | MRV:6 |

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
