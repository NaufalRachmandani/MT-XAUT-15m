# Acane v1 Small Balance Tuning

Account/server: `265874264` / `Exness-MT5Real38`
Symbol/timeframe: `XAUUSD` / `M1`
Tester model: Every tick

## Deposit 29, 2026.01.01 - 2026.05.09

All tested variants produced `0` trades. With the current risk formula and broker lot constraints, balance around `$29` generally falls below the minimum tradable lot. If live still shows `0.03`/`0.04` lots, those trades were likely opened before the withdrawal or while equity/baseline was much higher.

## Deposit 200, 2026.05.01 - 2026.05.09

| Variant | Trades | W/L | Win Rate | PF | Net | Eq DD |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| current debug | 62 | 42/20 | 67.74% | 2.30 | 70.41 | 14.05 (5.55%) |
| throttle | 38 | 29/9 | 76.32% | 5.28 | 61.65 | 12.22 (5.96%) |
| strict quality | 12 | 6/6 | 50.00% | 1.59 | 6.68 | 11.62 (5.46%) |
| fast quality | 11 | 4/7 | 36.36% | 0.87 | -2.12 | 14.02 (6.79%) |

## Deposit 200, 2026.01.01 - 2026.05.09

| Variant | Trades | W/L | Win Rate | PF | Net | Eq DD |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| current debug | 3757 | 2213/1544 | 58.90% | 1.62 | 6,594,331.85 | 406,700.00 (8.90%) |
| throttle | 828 | 663/165 | 80.07% | 5.39 | 997,998.37 | 47,565.43 (5.87%) |

Decision: `AcaneM1_v1_guarded_debug_throttle` is the best candidate from this pass. It keeps the MRV entry logic and aggressive risk multiplier, but prevents rapid same-side stacking, adds long cooldown after the first fast loss, lowers account guards, and blocks the worst leak-map hours.
