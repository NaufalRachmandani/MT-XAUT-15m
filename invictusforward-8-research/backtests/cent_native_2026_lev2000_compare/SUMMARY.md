# Forward-8 Cent Native MT5 Compare

Source of truth: native MT5 Strategy Tester `.htm` reports generated through `terminal64.exe /config`.

Setup: account `184000633` on `Exness-MT5Real25`, `XAUUSDc` `M15`, currency `USC`, leverage `1:2000`, `Model=4`, `ExecutionMode=100`, `UseLocal=1`, `UseRemote=0`, `UseCloud=0`.

All windows are 2026+ only. No 2025 result is used for tuning decisions.

## All Runs

| Expert | Deposit | Window | Net | PF | Trades | WR | Eq DD | Balance DD | Largest Loss | History | Validation |
| --- | ---: | --- | ---: | ---: | ---: | ---: | --- | --- | ---: | --- | --- |
| Base | 1000 USC | 2026 YTD | 802.11 | 1.11 | 298 | 68.12% | 1 826.88460000 (52.84909320%) | 1 706.68460000 (50.88513261%) | -153.52 | 100% real ticks | OK |
| Tuned | 1000 USC | 2026 YTD | 3024.49 | 1.58 | 237 | 75.53% | 1 466.93360000 (32.88139800%) | 1 316.73360000 (30.45113429%) | -199.70 | 100% real ticks | OK |
| Base | 1000 USC | Last Month | -150.98 | 0.81 | 55 | 49.09% | 555.39800000 (41.90668403%) | 515.09800000 (39.90159582%) | -51.14 | 100% real ticks | OK |
| Tuned | 1000 USC | Last Month | 259.80 | 1.42 | 51 | 72.55% | 385.29800000 (29.07205561%) | 336.39800000 (26.05876364%) | -51.14 | 100% real ticks | OK |
| Base | 1000 USC | Last Week | 22.70 | 1.11 | 19 | 63.16% | 165.80000000 (14.64793710%) | 93.70000000 (8.40886655%) | -50.00 | 100% real ticks | OK |
| Tuned | 1000 USC | Last Week | 254.28 | 6.11 | 14 | 92.86% | 134.30000000 (9.67174264%) | 49.80000000 (3.81878061%) | -49.80 | 100% real ticks | OK |
| Base | 20000 USC | 2026 YTD | 16601.34 | 1.15 | 278 | 68.71% | 27 595.08780000 (44.27013065%) | 25 840.28780000 (42.41172751%) | -2172.70 | 100% real ticks | OK |
| Tuned | 20000 USC | 2026 YTD | 55063.84 | 1.75 | 233 | 76.39% | 16 154.67980000 (21.67703477%) | 15 481.77980000 (20.92477421%) | -2372.40 | 100% real ticks | OK |
| Base | 20000 USC | Last Month | -6209.76 | 0.67 | 65 | 56.92% | 14 334.43720000 (53.57510810%) | 13 426.13720000 (51.65353487%) | -1173.80 | 100% real ticks | OK |
| Tuned | 20000 USC | Last Month | 4584.48 | 1.35 | 56 | 75.00% | 8 629.67880000 (32.25351425%) | 7 808.17880000 (30.03991616%) | -1173.80 | 100% real ticks | OK |
| Base | 20000 USC | Last Week | 729.10 | 1.17 | 23 | 69.57% | 3 374.40000000 (14.69129729%) | 1 965.40000000 (8.67638165%) | -1048.80 | 100% real ticks | OK |
| Tuned | 20000 USC | Last Week | 5176.18 | 5.52 | 16 | 93.75% | 3 089.10000000 (10.92895711%) | 1 144.60000000 (4.34865582%) | -1144.60 | 100% real ticks | OK |

## Base vs Tuned

| Deposit | Window | Base Net/PF/DD | Tuned Net/PF/DD | Winner | Note |
| ---: | --- | --- | --- | --- | --- |
| 1000 USC | 2026 YTD | 802.11 / 1.11 / 1 826.88460000 (52.84909320%) | 3024.49 / 1.58 / 1 466.93360000 (32.88139800%) | Tuned |  |
| 1000 USC | Last Month | -150.98 / 0.81 / 555.39800000 (41.90668403%) | 259.80 / 1.42 / 385.29800000 (29.07205561%) | Tuned |  |
| 1000 USC | Last Week | 22.70 / 1.11 / 165.80000000 (14.64793710%) | 254.28 / 6.11 / 134.30000000 (9.67174264%) | Tuned |  |
| 20000 USC | 2026 YTD | 16601.34 / 1.15 / 27 595.08780000 (44.27013065%) | 55063.84 / 1.75 / 16 154.67980000 (21.67703477%) | Tuned |  |
| 20000 USC | Last Month | -6209.76 / 0.67 / 14 334.43720000 (53.57510810%) | 4584.48 / 1.35 / 8 629.67880000 (32.25351425%) | Tuned |  |
| 20000 USC | Last Week | 729.10 / 1.17 / 3 374.40000000 (14.69129729%) | 5176.18 / 5.52 / 3 089.10000000 (10.92895711%) | Tuned |  |

## Recommendation

Tuned at 1000 USC passes the configured drawdown screen, but the YTD drawdown is still aggressive; use it as the next cent baseline, not as a conservative live profile.
