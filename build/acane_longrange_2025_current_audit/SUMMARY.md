# Acane Long-Range Audit

Account/server: `265874264` / `Exness-MT5Real38`
Symbol/timeframe: `XAUUSD` / `M1`
Window: `2025.01.01 - 2026.05.09`
Deposit: `29`
Leverage in tester reports: `1:2000`

| EA | Net | Trades | W/L | Win Rate | PF | Equity DD |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| v1 guarded debug | -3.21 | 65 | 26/39 | 40.00% | 0.65 | 4.62 (15.19%) |
| v2 | 52,335,762.74 | 9,339 | 6,852/2,487 | 73.37% | 4.60 | 92,820.00 (0.22%) |

## v1 holes

The v1 long-range small-balance run is not robust. It loses in early 2025 and then effectively does not recover because the lot/risk constraints keep it from participating enough.

Worst v1 hours:
- `07`: 5 trades, net `-0.97`, PF `0.03`
- `19`: 3 trades, net `-0.69`, PF `0.00`
- `18`: 3 trades, net `-0.58`, PF `0.06`
- `13`: 1 trade, net `-0.53`, PF `0.00`
- `11`: 5 trades, net `-0.50`, PF `0.28`

Worst v1 days:
- `2025-01-02`: 54 trades, net `-1.87`, WR `42.6%`, PF `0.76`
- `2025-01-03`: 7 trades, net `-1.10`, WR `14.3%`, PF `0.04`
- `2025-01-01`: 4 trades, net `-0.24`, WR `50.0%`, PF `0.48`

## v2 holes

v2 is positive by month and hour in this run, but still has negative individual days. These are the weak spots to monitor in forward testing:

- `2025-08-06`: 29 trades, net `-19,500.00`, WR `58.6%`, PF `0.69`
- `2025-09-24`: 19 trades, net `-15,220.00`, WR `52.6%`, PF `0.66`
- `2025-07-27`: 1 trade, net `-10,740.00`
- `2025-08-31`: 2 trades, net `-9,120.00`
- `2026-04-12`: 1 trade, net `-7,980.00`

Decision: v2 is materially better than v1 in this broader audit, but the forward test should still watch for clustered negative days rather than only checking total profit.
