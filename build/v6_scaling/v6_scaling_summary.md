# v6 Fixed-Fractional Scaling Check

Tujuan: membandingkan perilaku `v6` pada modal kecil dan besar dengan setup yang sama, untuk melihat apakah fixed-fractional sizing membuat hasil lebih invariant terhadap ukuran akun.

## recent_6m

Period: `2025.10.18 - 2026.04.15`, `XAUUSDc`, `M15`, `Leverage 1:100`, `Every tick`.

| Deposit | Net Profit | Profit % | PF | Win Rate | Trades | Balance DD | Equity DD |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 100 | 34.01 | 34.01% | 1.09 | 51.16% | 1204 | 28.76% | 29.73% |
| 10000 | 3299.95 | 33.00% | 1.08 | 50.24% | 1258 | 35.89% | 36.98% |

- Trade count delta: `54` trades.
- Profit %% delta: `-1.01` percentage points.
- PF delta: `-0.01`.
- Equity DD delta: `7.25` percentage points.

## from_2025

Period: `2025.01.01 - 2026.04.15`, `XAUUSDc`, `M15`, `Leverage 1:100`, `Every tick`.

| Deposit | Net Profit | Profit % | PF | Win Rate | Trades | Balance DD | Equity DD |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 100 | 304.48 | 304.48% | 1.14 | 49.97% | 3062 | 36.12% | 37.08% |
| 10000 | 32085.62 | 320.86% | 1.14 | 49.65% | 3013 | 35.91% | 36.99% |

- Trade count delta: `-49` trades.
- Profit %% delta: `16.38` percentage points.
- PF delta: `0.00`.
- Equity DD delta: `-0.09` percentage points.

## Files
- [v6_scaling_results.json](/Users/naufalrachmandani/Hobby/MT5 XAU 15m/build/v6_scaling/v6_scaling_results.json)
- [v6_scaling_results.csv](/Users/naufalrachmandani/Hobby/MT5 XAU 15m/build/v6_scaling/v6_scaling_results.csv)
