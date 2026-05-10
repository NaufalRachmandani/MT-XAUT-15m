# Trade-Level Analysis: AcaneM1_v2t_r07_reclaim_only_ytd_2026_d29_delay100_real_ticks_20260101_20260509.htm

## Summary
- Report net profit: `-4.74 Balance Drawdown Absolute`
- Reconstructed closed trades: `7`
- Reconstructed net: `-4.74`
- Win rate: `14.29%`
- Profit factor: `0.20`
- Unmatched exits: `0`
- Max price/PnL match error: `1.3661`

## Worst Engines
| engine | trades | net | win_rate | PF | avg | largest_loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| RCL | 7 | -4.74 | 14.29% | 0.20 | -0.68 | -1.38 |

## Best Engines
| engine | trades | net | win_rate | PF | avg | largest_loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| RCL | 7 | -4.74 | 14.29% | 0.20 | -0.68 | -1.38 |

## Worst Engine x Regime
| engine | regime_tag | trades | net | win_rate | PF | avg | largest_loss |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| RCL | RG | 7 | -4.74 | 14.29% | 0.20 | -0.68 | -1.38 |

## Worst Engine x Entry Hour
| engine | entry_hour | trades | net | win_rate | PF | avg | largest_loss |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| RCL | 4 | 4 | -3.50 | 0.00% | 0.00 | -0.88 | -1.21 |
| RCL | 0 | 3 | -1.24 | 33.33% | 0.50 | -0.41 | -1.38 |

## Worst Months
| entry_month | trades | net | win_rate | PF | avg | largest_loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2026-01 | 7 | -4.74 | 14.29% | 0.20 | -0.68 | -1.38 |

## Worst Loss Clusters
| start | end | count | pnl | buy_losses | sell_losses | engines |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| 2026-01-02 00:17:00 | 2026-01-02 04:45:07 | 4 | -4.45 | 4 | 0 | RCL:4 |

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
