# 2026 Active Versions Summary

Window: `2026.01.01 - 2026.04.15`, `XAUUSDc`, `M15`, `Every tick`.

## Deposit 100 USD

Source: [/Users/naufalrachmandani/Hobby/MT5 XAU 15m/build/compare_2026_only_active_100/compare_summary.md](/Users/naufalrachmandani/Hobby/MT5%20XAU%2015m/build/compare_2026_only_active_100/compare_summary.md)

| Version | Profit % | PF | Win Rate | Trades | EqDD |
| --- | ---: | ---: | ---: | ---: | ---: |
| v1 | -56.19% | 0.55 | 38.89% | 36 | 90.92% |
| v4 | 131.60% | 1.10 | 47.00% | 417 | 89.76% |
| v5 | 145.47% | 1.22 | 49.23% | 323 | 85.98% |
| v6 | 58.96% | 1.17 | 53.01% | 498 | 29.17% |
| v7 | 28.11% | 1.79 | 60.56% | 71 | 9.08% |
| v8 | 32.84% | 2.06 | 58.90% | 73 | 8.99% |

## Deposit 10,000 USD

Source: [/Users/naufalrachmandani/Hobby/MT5 XAU 15m/build/compare_2026_only_active_10000/compare_summary.md](/Users/naufalrachmandani/Hobby/MT5%20XAU%2015m/build/compare_2026_only_active_10000/compare_summary.md)

| Version | Profit % | PF | Win Rate | Trades | EqDD |
| --- | ---: | ---: | ---: | ---: | ---: |
| v1 | 13.92% | 1.15 | 45.05% | 111 | 17.78% |
| v4 | -53.88% | 0.91 | 47.58% | 559 | 87.45% |
| v5 | -2.36% | 1.00 | 50.98% | 457 | 78.10% |
| v6 | 74.48% | 1.21 | 53.99% | 489 | 29.90% |
| v7 | 19.43% | 1.22 | 55.88% | 238 | 16.97% |
| v8 | 23.84% | 1.29 | 55.88% | 238 | 13.91% |

## Practical Ranking for 2026

1. `v8` = best overall candidate for 2026.
   - Best risk-adjusted profile on both deposits.
   - DD stays under `9%` on `$100` and under `15%` on `$10,000`.
   - PF is the highest in small account tests and strongest among deployable variants in larger-account tests.

2. `v6` = aggressive but still viable.
   - Much higher profit than `v8` on larger capital.
   - DD around `30%`, so this is materially riskier.
   - Best fit only if profit priority is clearly above survivability.

3. `v7` = defensive fallback.
   - Very clean DD profile.
   - Lower profit than `v8`.
   - Useful as a conservative reference or if you want the calmest equity curve from the `base` lineage.

4. `v1`, `v4`, `v5` = not suitable as 2026 primary versions.
   - `v1` is too weak on small capital.
   - `v4` and `v5` are unstable across account sizes and can flip from very profitable to unacceptable.

## v8 Cross-Scale Refinement

Source: [/Users/naufalrachmandani/Hobby/MT5 XAU 15m/build/v8_round4_cross_scale/summary.md](/Users/naufalrachmandani/Hobby/MT5%20XAU%2015m/build/v8_round4_cross_scale/summary.md)

The final `v8` tweak that survived cross-scale validation was:
- keep bearish regime detection at `ADX >= 28` with H4 close/high lookback `3`
- keep bearish buy score floor at `95`
- reduce bearish-regime buy risk from `0.15x` to `0.10x`

This was better than the prior `v8` control on both deposits without breaking DD constraints.
