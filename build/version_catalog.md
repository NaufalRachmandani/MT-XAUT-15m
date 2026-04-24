# Version Catalog

Catalog aktif sekarang sengaja dipersempit ke empat jalur yang masih layak dipakai:
- `v6`
- `v8`
- `v10`
- `v11`

Varian lama seperti `v1`, `v4`, `v5`, `v7`, dan `v9` dipensiunkan dari working tree agar riset tidak terus bercabang ke jalur yang sudah tidak diprioritaskan.

Semua angka di bawah memakai:
- `XAUUSDc`
- mode `Every tick`
- `Deposit 100 USD`
- `Leverage 1:100`

| Version | Role | TF | 2026-only Profit % | 2026-only PF | 2026-only EqDD | 2025-current Profit % | 2025-current PF | 2025-current EqDD |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| v6 | aggressive M15 | M15 | 58.96% | 1.17 | 29.17% | 1662.44% | 1.22 | 29.88% |
| v8 | risk-adjusted M15 | M15 | 32.84% | 2.06 | 8.99% | 200.21% | 1.33 | 17.45% |
| v10 | aggressive zone-retest M5 | M5 | 318.57% | 2.93 | 9.26% | 305.71% | 1.52 | 50.80% |
| v11 combined | split bull/bear M5 | M5 | 504.76% | 2.53 | 21.28% | 426.34% | 1.44 | 55.03% |

## Practical Reading

- `v6`
  - paling agresif di jalur `M15`
  - cocok kalau target utamanya profit dan kamu siap DD sekitar `30%`
- `v8`
  - versi `M15` paling bersih
  - cocok kalau prioritasnya survivability dan PF yang sehat
- `v10`
  - jalur `M5` utama
  - lebih seimbang daripada `v11` dari sisi DD 2026
  - sekarang juga full-window `2025-current` naik keras, tetapi trade-off-nya DD ikut melonjak
  - cocok kalau target utamanya profit agresif `M5`, bukan equity curve paling bersih
- `v11 combined`
  - profit leader untuk `2026-only`
  - memakai split bull-only + bear-only, dengan combined tester untuk validasi portfolio
  - cocok untuk riset/live agresif, bukan untuk mode DD rendah

## Current Recommendation

- untuk `2026-only`
  - `v8` jika mau paling stabil
  - `v6` jika mau agresif di `M15`
  - `v10` jika mau `M5` agresif dengan DD lebih rendah daripada `v11`
  - `v11` jika mau profit leader `M5` dan siap DD lebih besar
- untuk `2025-current`
  - `v6` tetap profit leader
  - `v8` paling tenang
  - `v10/v11` profit tinggi, tetapi full-window DD jauh lebih kasar daripada `v6/v8`
