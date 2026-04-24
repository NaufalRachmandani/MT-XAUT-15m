# 2026 Active Versions Summary

Window:
- `2026.01.01 - 2026.04.25`
- `XAUUSDc`
- `Deposit 100 USD`
- `Leverage 1:100`
- `Every tick`

| Version | TF | Profit % | PF | EqDD |
| --- | --- | ---: | ---: | ---: |
| v6 | M15 | 58.96% | 1.17 | 29.17% |
| v8 | M15 | 32.84% | 2.06 | 8.99% |
| v10 | M5 | 318.57% | 2.93 | 9.26% |
| v11 combined | M5 | 504.76% | 2.53 | 21.28% |

## Reading

1. `v8`
   - best overall kalau targetnya risk-adjusted dan survivability
2. `v6`
   - paling agresif di jalur `M15`
   - profit lebih tinggi daripada `v8`, tapi DD juga jauh lebih besar
3. `v10`
   - jalur `M5` aktif
   - lebih seimbang daripada `v11` untuk DD 2026
   - champion terbaru memakai `base-style zone retest` yang lebih agresif pada sisi buy
   - DD 2026-only tetap sehat, tetapi ini sekarang jelas mode profit-first, bukan lagi mode paling rapi
4. `v11 combined`
   - profit leader untuk window 2026-only
   - arsitektur risetnya split bull-only + bear-only, dengan combined tester untuk portfolio backtest
   - DD lebih tinggi daripada `v10`, jadi ini mode agresif
