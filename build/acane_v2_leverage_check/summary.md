# AcaneM1 v2 Leverage Check

Account/server: `265874264` / `Exness-MT5Real38`
Symbol/timeframe: `XAUUSD` / `M1`
Tester model: Every tick

Earlier package smoke tests reported `1:100` leverage, which made deposit `$29` look unusable. Rerunning with `Leverage=1:2000` produced reports that explicitly show `1:2000`.

| Window | Deposit | Requested Leverage | Report Leverage | Net | Trades | W/L | Win Rate | PF | Equity DD |
| --- | ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| 2026.05.01 - 2026.05.09 | 29 | 1:2000 | 1:2000 | 58.85 | 157 | 110/45 | 70.06% | 3.67 | 4.83 (5.76%) |
| 2026.05.01 - 2026.05.09 | 30 | 1:2000 | 1:2000 | 58.85 | 157 | 110/45 | 70.06% | 3.67 | 4.83 (5.69%) |
| 2026.05.01 - 2026.05.09 | 40 | 1:2000 | 1:2000 | 75.35 | 161 | 113/46 | 70.19% | 3.69 | 4.64 (4.29%) |
| 2026.05.01 - 2026.05.09 | 50 | 1:2000 | 1:2000 | 88.75 | 163 | 114/47 | 69.94% | 3.44 | 6.83 (5.30%) |
| 2026.05.01 - 2026.05.09 | 100 | 1:2000 | 1:2000 | 220.39 | 163 | 116/47 | 71.17% | 3.61 | 16.33 (5.54%) |
| 2026.01.01 - 2026.05.09 | 29 | 1:2000 | 1:2000 | 13,623,408.54 | 2,438 | 1,843/595 | 75.59% | 4.63 | 92,820.00 (2.17%) |

Conclusion: deposit `$29` can open positions if the live account is really running at `1:2000`. A `$100` top-up is not needed for margin feasibility, but it is still more robust for live slippage and execution differences.
