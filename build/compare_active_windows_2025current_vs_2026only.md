# Active Versions: 2025-Current vs 2026-Only / $100

Setup:
- `XAUUSDc`
- `Deposit 100 USD`
- `Leverage 1:100`
- `Every tick`

| Version | TF | 2026 Profit % | 2026 PF | 2026 EqDD | 2025-Current Profit % | 2025-Current PF | 2025-Current EqDD |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| v6 | M15 | 58.96% | 1.17 | 29.17% | 1662.44% | 1.22 | 29.88% |
| v8 | M15 | 32.84% | 2.06 | 8.99% | 200.21% | 1.33 | 17.45% |
| v10 | M5 | 318.57% | 2.93 | 9.26% | 305.71% | 1.52 | 50.80% |
| v11 combined | M5 | 504.76% | 2.53 | 21.28% | 426.34% | 1.44 | 55.03% |

## Practical Takeaway

- `v6`
  - profit-led `M15`
  - paling cocok kalau DD `~30%` masih bisa diterima
- `v8`
  - risk-adjusted leader
  - paling cocok kalau target utamanya stabilitas
- `v10`
  - jalur `M5` aktif
  - sekarang memakai `base-style zone retest` yang lebih agresif, plus buy-side risk yang lebih besar
  - paling menarik kalau targetmu profit `M5` tinggi dan trade count lebih banyak, dengan konsekuensi full-window DD yang jauh lebih kasar
- `v11 combined`
  - profit leader untuk `2026-only`
  - cocok untuk menguji konsep bull-only + bear-only split
  - bukan risk-adjusted leader karena `2025-current` DD masih tinggi
