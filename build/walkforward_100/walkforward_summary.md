# Walk-Forward Regime Matrix

Setup: `XAUUSDc`, `M15`, monthly windows from `2025.01.01` to `2026.04.15`, `Deposit 100 USD`, `Leverage 1:100`, `Every tick`.

## Aggregate Version Summary

| Version | Positive Windows | Avg Net | Median Net | Avg PF | Avg WR | Avg EqDD | Worst EqDD | Best Net Wins | Best PF Wins | Best Recovery Wins |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| v1 | 11/16 | 52.52 | 25.66 | 1.49 | 48.37% | 50.11% | 75.75% | 5 | 7 | 7 |
| v4 | 12/16 | 121.42 | 67.71 | 1.27 | 51.85% | 60.00% | 82.24% | 6 | 3 | 2 |
| v5 | 11/16 | 56.36 | 66.88 | 1.44 | 51.53% | 50.97% | 83.63% | 5 | 6 | 7 |

## Window Winners

| Window | Period | Best Net | Best PF | Best Recovery Proxy |
| --- | --- | --- | --- | --- |
| 2025-01 | 2025.01.01 - 2025.01.31 | v4 (301.52) | v5 (2.89) | v5 (2.63) |
| 2025-02 | 2025.02.01 - 2025.02.28 | v4 (441.28) | v5 (2.55) | v5 (4.29) |
| 2025-03 | 2025.03.01 - 2025.03.31 | v1 (242.71) | v1 (3.11) | v1 (2.95) |
| 2025-04 | 2025.04.01 - 2025.04.30 | v4 (134.45) | v5 (1.56) | v5 (1.55) |
| 2025-05 | 2025.05.01 - 2025.05.31 | v4 (287.00) | v4 (1.91) | v4 (2.84) |
| 2025-06 | 2025.06.01 - 2025.06.30 | v1 (71.60) | v1 (1.61) | v1 (0.77) |
| 2025-07 | 2025.07.01 - 2025.07.31 | v5 (147.58) | v5 (2.04) | v5 (2.33) |
| 2025-08 | 2025.08.01 - 2025.08.31 | v1 (53.00) | v1 (1.79) | v1 (0.96) |
| 2025-09 | 2025.09.01 - 2025.09.30 | v1 (150.78) | v1 (2.25) | v1 (1.55) |
| 2025-10 | 2025.10.01 - 2025.10.31 | v1 (10.39) | v1 (1.07) | v1 (0.14) |
| 2025-11 | 2025.11.01 - 2025.11.30 | v4 (459.80) | v1 (3.48) | v1 (3.49) |
| 2025-12 | 2025.12.01 - 2025.12.31 | v5 (116.02) | v5 (1.83) | v5 (1.35) |
| 2026-01 | 2026.01.01 - 2026.01.31 | v5 (-16.86) | v4 (0.95) | v4 (-0.08) |
| 2026-02 | 2026.02.01 - 2026.02.28 | v5 (31.93) | v1 (1.30) | v1 (0.42) |
| 2026-03 | 2026.03.01 - 2026.03.31 | v4 (145.78) | v4 (1.48) | v5 (1.16) |
| 2026-04 | 2026.04.01 - 2026.04.15 | v5 (55.02) | v5 (1.65) | v5 (1.02) |

## Regime Takeaways

- `Recent-leader` by monthly net profit is `v5` over the recent windows set (`2025-11` onward).
- `Robust-leader` by recovery-style consistency is `v1`.
- `Absolute-leader` by number of monthly net-profit wins is `v4`.
- `Best Recovery Proxy` uses `net profit / equity drawdown absolute` as a simple walk-forward robustness measure on the same 100 USD account base.

## Files
- [walkforward_results.json](/Users/naufalrachmandani/Hobby/MT5 XAU 15m/build/walkforward_100/walkforward_results.json)
- [walkforward_results.csv](/Users/naufalrachmandani/Hobby/MT5 XAU 15m/build/walkforward_100/walkforward_results.csv)
- [walkforward_winners.csv](/Users/naufalrachmandani/Hobby/MT5 XAU 15m/build/walkforward_100/walkforward_winners.csv)
- [walkforward_version_summary.csv](/Users/naufalrachmandani/Hobby/MT5 XAU 15m/build/walkforward_100/walkforward_version_summary.csv)
- [walkforward_matrix.csv](/Users/naufalrachmandani/Hobby/MT5 XAU 15m/build/walkforward_100/walkforward_matrix.csv)
