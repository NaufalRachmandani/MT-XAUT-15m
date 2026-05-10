# Trade-Level Analysis: AcaneM1_v2t_trend_combo_ytd_2026_d29_delay50_real_ticks_20260101_20260509.htm

## Summary
- Report net profit: `0.67 Balance Drawdown Absolute`
- Reconstructed closed trades: `15`
- Reconstructed net: `0.67`
- Win rate: `60.00%`
- Profit factor: `1.15`
- Unmatched exits: `0`
- Max price/PnL match error: `1.0494`

## Worst Engines
| engine | trades | net | win_rate | PF | avg | largest_loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| MOM | 15 | 0.67 | 60.00% | 1.15 | 0.04 | -0.99 |

## Best Engines
| engine | trades | net | win_rate | PF | avg | largest_loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| MOM | 15 | 0.67 | 60.00% | 1.15 | 0.04 | -0.99 |

## Worst Engine x Regime
| engine | regime_tag | trades | net | win_rate | PF | avg | largest_loss |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| MOM | RG | 12 | -1.11 | 50.00% | 0.76 | -0.09 | -0.99 |
| MOM | WG | 3 | 1.78 | 100.00% | 0.00 | 0.59 | 0.00 |

## Worst Engine x Entry Hour
| engine | entry_hour | trades | net | win_rate | PF | avg | largest_loss |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| MOM | 0 | 3 | -1.72 | 33.33% | 0.02 | -0.57 | -0.91 |
| MOM | 23 | 10 | 3.76 | 80.00% | 3.61 | 0.38 | -0.85 |

## Worst Months
| entry_month | trades | net | win_rate | PF | avg | largest_loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2026-01 | 15 | 0.67 | 60.00% | 1.15 | 0.04 | -0.99 |

## Worst Loss Clusters
| start | end | count | pnl | buy_losses | sell_losses | engines |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| 2026-01-01 23:12:26 | 2026-01-02 01:02:27 | 6 | -4.56 | 6 | 0 | MOM:6 |

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
