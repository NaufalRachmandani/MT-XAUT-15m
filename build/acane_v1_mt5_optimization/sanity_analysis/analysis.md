# Trade-Level Analysis: AcaneM1_v1_sanity_20260501_20260510_d100_lev12000_delay100_model4_20260501_20260510.htm

## Summary
- Report net profit: `-30.17 Balance Drawdown Absolute`
- Reconstructed closed trades: `164`
- Reconstructed net: `-26.75`
- Win rate: `52.44%`
- Profit factor: `0.83`
- Unmatched exits: `0`
- Max price/PnL match error: `3.4848`

## Worst Engines
| engine | trades | net | win_rate | PF | avg | largest_loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| TPL | 156 | -23.25 | 52.56% | 0.85 | -0.15 | -3.27 |
| CBK | 8 | -3.50 | 50.00% | 0.51 | -0.44 | -2.58 |

## Best Engines
| engine | trades | net | win_rate | PF | avg | largest_loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| CBK | 8 | -3.50 | 50.00% | 0.51 | -0.44 | -2.58 |
| TPL | 156 | -23.25 | 52.56% | 0.85 | -0.15 | -3.27 |

## Worst Engine x Regime
| engine | regime_tag | trades | net | win_rate | PF | avg | largest_loss |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| TPL |  | 156 | -23.25 | 52.56% | 0.85 | -0.15 | -3.27 |
| CBK | RG | 2 | -1.79 | 50.00% | 0.31 | -0.90 | -2.58 |
| CBK | WG | 6 | -1.71 | 50.00% | 0.63 | -0.28 | -1.87 |

## Worst Engine x Entry Hour
| engine | entry_hour | trades | net | win_rate | PF | avg | largest_loss |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| TPL | 15 | 9 | -11.72 | 33.33% | 0.27 | -1.30 | -2.80 |
| TPL | 2 | 8 | -9.59 | 37.50% | 0.11 | -1.20 | -2.65 |
| TPL | 0 | 8 | -5.66 | 25.00% | 0.53 | -0.71 | -2.84 |
| TPL | 6 | 7 | -5.60 | 42.86% | 0.32 | -0.80 | -3.27 |
| CBK | 1 | 3 | -3.95 | 33.33% | 0.11 | -1.32 | -2.58 |
| TPL | 19 | 7 | -3.35 | 28.57% | 0.46 | -0.48 | -1.81 |
| TPL | 20 | 5 | -2.01 | 40.00% | 0.51 | -0.40 | -1.72 |
| TPL | 14 | 11 | -1.02 | 63.64% | 0.91 | -0.09 | -2.89 |
| TPL | 7 | 13 | -0.92 | 61.54% | 0.93 | -0.07 | -2.88 |
| TPL | 8 | 13 | -0.87 | 46.15% | 0.95 | -0.07 | -2.85 |
| TPL | 23 | 4 | -0.86 | 50.00% | 0.68 | -0.21 | -1.44 |
| TPL | 13 | 3 | -0.81 | 66.67% | 0.70 | -0.27 | -2.74 |

## Worst Months
| entry_month | trades | net | win_rate | PF | avg | largest_loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2026-05 | 164 | -26.75 | 52.44% | 0.83 | -0.16 | -3.27 |

## Worst Loss Clusters
| start | end | count | pnl | buy_losses | sell_losses | engines |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| 2026-05-06 01:48:00 | 2026-05-06 14:41:50 | 18 | -39.01 | 18 | 0 | CBK:1, TPL:17 |
| 2026-05-05 03:52:01 | 2026-05-05 15:10:44 | 15 | -36.40 | 14 | 1 | CBK:1, TPL:14 |
| 2026-05-01 01:43:00 | 2026-05-01 11:08:27 | 10 | -19.03 | 3 | 7 | CBK:1, TPL:9 |
| 2026-05-06 19:51:00 | 2026-05-07 00:17:00 | 11 | -17.75 | 11 | 0 | TPL:11 |
| 2026-05-04 00:13:00 | 2026-05-04 05:54:00 | 8 | -15.88 | 1 | 7 | CBK:1, TPL:7 |
| 2026-05-01 15:37:00 | 2026-05-01 17:03:40 | 6 | -14.67 | 6 | 0 | TPL:6 |
| 2026-05-08 02:29:00 | 2026-05-08 06:05:32 | 4 | -10.78 | 4 | 0 | TPL:4 |
| 2026-05-05 19:32:00 | 2026-05-05 20:55:33 | 5 | -5.67 | 0 | 5 | TPL:5 |

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
