# Trade-Level Analysis: AcaneM1_v1_sanity_20260501_20260510_d100_lev12000_delay100_model4_20260501_20260510.htm

## Summary
- Report net profit: `-27.78 Balance Drawdown Absolute`
- Reconstructed closed trades: `52`
- Reconstructed net: `-27.78`
- Win rate: `44.23%`
- Profit factor: `0.56`
- Unmatched exits: `0`
- Max price/PnL match error: `2.9205`

## Worst Engines
| engine | trades | net | win_rate | PF | avg | largest_loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| IMP | 50 | -23.51 | 46.00% | 0.60 | -0.47 | -2.95 |
| CBK | 2 | -4.27 | 0.00% | 0.00 | -2.13 | -2.78 |

## Best Engines
| engine | trades | net | win_rate | PF | avg | largest_loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| CBK | 2 | -4.27 | 0.00% | 0.00 | -2.13 | -2.78 |
| IMP | 50 | -23.51 | 46.00% | 0.60 | -0.47 | -2.95 |

## Worst Engine x Regime
| engine | regime_tag | trades | net | win_rate | PF | avg | largest_loss |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| IMP |  | 50 | -23.51 | 46.00% | 0.60 | -0.47 | -2.95 |
| CBK | WG | 2 | -4.27 | 0.00% | 0.00 | -2.13 | -2.78 |

## Worst Engine x Entry Hour
| engine | entry_hour | trades | net | win_rate | PF | avg | largest_loss |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| IMP | 8 | 7 | -11.53 | 14.29% | 0.02 | -1.65 | -2.87 |
| IMP | 11 | 6 | -11.22 | 16.67% | 0.00 | -1.87 | -2.68 |
| IMP | 9 | 5 | -5.38 | 40.00% | 0.35 | -1.08 | -2.88 |
| IMP | 4 | 3 | -1.88 | 33.33% | 0.46 | -0.63 | -1.95 |
| IMP | 10 | 9 | 0.67 | 55.56% | 1.07 | 0.07 | -2.95 |
| IMP | 5 | 10 | 1.10 | 70.00% | 1.17 | 0.11 | -2.36 |
| IMP | 7 | 7 | 10.24 | 71.43% | 6.20 | 1.46 | -1.97 |

## Worst Months
| entry_month | trades | net | win_rate | PF | avg | largest_loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2026-05 | 52 | -27.78 | 44.23% | 0.56 | -0.53 | -2.95 |

## Worst Loss Clusters
| start | end | count | pnl | buy_losses | sell_losses | engines |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| 2026-05-06 04:08:00 | 2026-05-06 14:17:38 | 11 | -27.00 | 11 | 0 | IMP:11 |
| 2026-05-07 05:53:01 | 2026-05-07 11:49:26 | 5 | -12.18 | 5 | 0 | IMP:5 |
| 2026-05-08 11:28:00 | 2026-05-08 12:56:02 | 3 | -7.68 | 3 | 0 | CBK:1, IMP:2 |
| 2026-05-04 04:18:00 | 2026-05-04 08:31:00 | 5 | -7.60 | 1 | 4 | CBK:1, IMP:4 |
| 2026-05-01 10:54:00 | 2026-05-01 11:13:20 | 3 | -5.93 | 0 | 3 | IMP:3 |

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
