# Invictus Forward-8 V6 Jun2025 Archive Boost

Authority: native MT5 Strategy Tester `.htm` reports. Python was used only for orchestration, parsing, and this report.

Safety: generated tester configs use `AllowLiveTrading=0`, `Visual=0`, `ShutdownTerminal=1`, local agents only, and sound events disabled in `[Events]`.

Selected research candidate: `v6_profit_balanced`, saved as `sets/InvictusForward8_V6_selected_profit_balanced_not_live.set`. This is not live-ready; it is the best next manual backtest candidate.

## Decision

- Best archive net winner: `v6_archive_balanced` on USD Real38 Jun2025-Now, net `20,540.08`, PF `2.14`, DD `28.63%`.
- Best 2026 profit winner: `v6_archive_profit_push`, but it is rejected as robust archive learner because Jun-Dec 2025 is negative.
- Best compromise: `v6_profit_balanced`. It improves V5 max on full USD archive net and DD, while keeping cent 2026 profit high enough for further testing.
- Live decision: `not live-ready`. Jun-Dec 2025 only barely passes PF (`1.01`) and has large DD (`63.77%`), so this still needs another risk layer before real cent deployment.

## USD Real38 Proxy, 1000 USD, XAUUSD, 1:2000

| Variant | Jun-Dec 2025 Net/PF/DD | 2026 YTD Net/PF/DD | Jun2025-Now Net/PF/DD | Full largest loss | History | Verdict |
| --- | ---: | ---: | ---: | ---: | --- | --- |
| V5 max | -57.18 / 0.99 / 87.19% | 22,744.79 / 2.63 / 24.14% | 17,946.58 / 1.76 / 28.51% | -3,741.15 | 100% real ticks | baseline favorite; high DD/largest loss |
| V6 H13+RB guard | -53.87 / 0.99 / 60.34% | 14,438.05 / 3.43 / 14.32% | 12,892.34 / 2.05 / 14.15% | -644.31 | 100% real ticks | risk reduced, profit too low |
| V6 archive-balanced | 776.14 / 1.09 / 54.17% | 13,108.63 / 3.11 / 14.24% | 20,540.08 / 2.14 / 28.63% | -1,242.59 | 100% real ticks | best archive net, lower cent profit |
| V6 profit-push | -344.95 / 0.96 / 77.28% | 25,425.28 / 3.89 / 13.02% | 15,002.48 / 2.12 / 17.39% | -759.36 | 100% real ticks | 2026 winner, Jun-Dec fails |
| V6 archive-strict | 742.37 / 1.10 / 54.23% | 9,879.72 / 2.54 / 27.13% | 16,123.27 / 1.89 / 27.42% | -1,219.58 | 100% real ticks | positive archive, weaker 2026 |
| V6 profit-balanced | 62.61 / 1.01 / 63.77% | 19,691.66 / 3.30 / 16.61% | 19,701.34 / 2.21 / 16.61% | -1,265.60 | 100% real ticks | selected compromise, not live-ready |

## Cent Confirmation, 1000 USC, XAUUSDc, 1:2000

| Variant | May OOS Net/PF/DD | Last Month Net/PF/DD | 2026 YTD Net/PF/DD | YTD largest loss | History | Verdict |
| --- | ---: | ---: | ---: | ---: | --- | --- |
| V5 max | 1,022.00 / no loss / 14.31% | 2,562.40 / 8.01 / 13.80% | 19,839.91 / 2.52 / 28.60% | -3,732.50 | 100% real ticks | cent profit leader, DD/largest loss high |
| V6 archive-balanced | 805.40 / no loss / 13.61% | 1,792.80 / 5.90 / 14.66% | 10,916.11 / 2.85 / 14.11% | -671.20 | 100% real ticks | safer but profit lower |
| V6 profit-push | 1,378.20 / no loss / 17.21% | 3,799.62 / 8.67 / 17.06% | 18,157.26 / 3.39 / 17.52% | -902.60 | 100% real ticks | best V6 cent profit, archive Jun-Dec negative |
| V6 profit-balanced | 1,126.60 / no loss / 17.47% | 2,587.42 / 6.23 / 17.20% | 15,865.94 / 2.99 / 17.47% | -1,041.40 | 100% real ticks | selected V6 research balance |

## What Changed From V5

- Added V6 archive hour controls for trend H07/H08/H13/H16 and range-bounce H01/H17.
- Selected V6 compromise blocks trend H13, blocks range-bounce H01/H17, scales H07 to `0.8`, H08 to `0.6`, H16 to `0.4`, and keeps H13 multiplier at `1.0` because it is hard-blocked.
- Order comments changed to `IF8V6A_TR`, `IF8V6A_RB`, and `IF8V6A_DC` for cleaner diagnosis by module.
- OnTester CSV output now includes V6 archive guard inputs.

## Files

- Source: `invictusforward-8-research/invictus8_v6_jun2025_archive_boost/source/v6archive/InvictusForward-8-V6ArchiveBoost.mq5`
- Selected set: `invictusforward-8-research/invictus8_v6_jun2025_archive_boost/sets/InvictusForward8_V6_selected_profit_balanced_not_live.set`
- Compiled EX5 copy: `invictusforward-8-research/invictus8_v6_jun2025_archive_boost/reports/InvictusForward8_V6AB_V6Archive_InvictusForward-8-V6ArchiveBoost.ex5`
- Results JSON: `invictusforward-8-research/invictus8_v6_jun2025_archive_boost/reports/results.json`
- Comparison JSON: `invictusforward-8-research/invictus8_v6_jun2025_archive_boost/reports/comparison.json`
