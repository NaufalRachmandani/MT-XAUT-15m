# Friday 2026-05-08 Acane Audit

Account/server: `265874264` / `Exness-MT5Real38`
Symbol/timeframe: `XAUUSD` / `M1`
Leverage in tester reports: `1:2000`

## One-day backtest, Friday 2026-05-08

| EA | Deposit | Net | Trades | W/L | Win Rate | PF | Equity DD |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| v1 guarded debug | 29 | 2.26 | 28 | 16/12 | 57.14% | 1.70 | 2.67 (8.09%) |
| v2 | 29 | 5.72 | 22 | 13/8 | 59.09% | 2.36 | 2.57 (7.49%) |
| v1 guarded debug | 100 | 42.00 | 86 | 55/31 | 63.95% | 2.15 | 9.36 (8.08%) |
| v2 | 100 | 18.83 | 24 | 16/8 | 66.67% | 3.03 | 4.64 (4.16%) |
| v1 guarded debug | 200 | 91.41 | 85 | 55/30 | 64.71% | 2.18 | 20.21 (8.60%) |
| v2 | 200 | 45.43 | 24 | 16/8 | 66.67% | 3.11 | 11.47 (5.08%) |

## VPS terminal log reconstruction

The VPS terminal log after migration only shows 5 reconstructed closed trades for account `265874264` on Friday evening server time.

| Source | Closed | W/L | Net | Notes |
| --- | ---: | ---: | ---: | --- |
| local terminal log | 0 | 0/0 | 0.00 | no live closed XAUUSD trades found for account `265874264` |
| VPS terminal log | 5 | 0/5 | -8.97 | 3 unique `No money` failed entries |

Worst VPS reconstructed trades:
- `20:47:58`: buy `0.04`, `4724.425 -> 4723.974`, `-1.80`
- `20:50:02`: buy `0.04`, `4723.979 -> 4723.612`, `-1.47`
- `21:07:24`: sell `0.04`, `4724.708 -> 4724.937`, `-0.92`
- `21:31:07`: buy `0.04`, `4723.587 -> 4723.033`, `-2.22`
- `22:01:29`: buy `0.04`, `4723.484 -> 4722.843`, `-2.56`

Conclusion: the Friday strategy tester does not reproduce a 50% account drawdown. The VPS log does show a real all-loss streak after migration and repeated margin pressure (`No money`), but only for the trades visible in the local VPS logs. The larger mobile-history loss likely includes earlier trades not present in the local/VPS log snapshot, balance operations, or a different terminal/session history.
