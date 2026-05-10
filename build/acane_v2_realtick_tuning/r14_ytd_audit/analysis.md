# Trade-Level Analysis: AcaneM1_v2t_r14_hybrid_more_tp_ytd_2026_d29_delay100_real_ticks_20260101_20260509.htm

## Summary
- Report net profit: `-4.48 Balance Drawdown Absolute`
- Reconstructed closed trades: `8`
- Reconstructed net: `-4.48`
- Win rate: `25.00%`
- Profit factor: `0.28`
- Unmatched exits: `0`
- Max price/PnL match error: `1.6137`

## Worst Engines
| engine | trades | net | win_rate | PF | avg | largest_loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| RCL | 6 | -3.84 | 16.67% | 0.30 | -0.64 | -1.38 |
| MOM | 2 | -0.64 | 50.00% | 0.18 | -0.32 | -0.78 |

## Best Engines
| engine | trades | net | win_rate | PF | avg | largest_loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| MOM | 2 | -0.64 | 50.00% | 0.18 | -0.32 | -0.78 |
| RCL | 6 | -3.84 | 16.67% | 0.30 | -0.64 | -1.38 |

## Worst Engine x Regime
| engine | regime_tag | trades | net | win_rate | PF | avg | largest_loss |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| RCL | RG | 6 | -3.84 | 16.67% | 0.30 | -0.64 | -1.38 |
| MOM | RG | 2 | -0.64 | 50.00% | 0.18 | -0.32 | -0.78 |

## Worst Engine x Entry Hour
| engine | entry_hour | trades | net | win_rate | PF | avg | largest_loss |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| RCL | 4 | 3 | -2.96 | 0.00% | 0.00 | -0.99 | -1.27 |
| RCL | 0 | 3 | -0.88 | 33.33% | 0.65 | -0.29 | -1.38 |

## Worst Months
| entry_month | trades | net | win_rate | PF | avg | largest_loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2026-01 | 8 | -4.48 | 25.00% | 0.28 | -0.56 | -1.38 |

## Worst Loss Clusters
| start | end | count | pnl | buy_losses | sell_losses | engines |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| 2026-01-02 00:17:00 | 2026-01-02 04:45:07 | 4 | -4.56 | 4 | 0 | MOM:1, RCL:3 |

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
