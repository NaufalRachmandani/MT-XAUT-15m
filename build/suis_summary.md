# Suis M5 Summary

Aktif sekarang:

- `SuisM5_v1`: satu-satunya Suis M5 aktif. File ini sudah ditiban dengan profil aggressive/frequency yang sebelumnya disebut `SuisM5_v2`.

Source internal sudah memakai prefix generik `SUIS_`.

## Snapshot Backtest

Setup terbaru yang lebih relevan untuk akun standar: `XAUUSDm`, `M5`, `Deposit 150 USD`, `Leverage 1:2000`, mode `Every tick`.

| EA | Net Profit | Trades | PF | EqDD |
| --- | ---: | ---: | ---: | ---: |
| `SuisM5_v1` 2026.01.01-2026.05.08 | +353.57% | 1132 | 1.09 | 58.21% |
| `SuisM5_v1` 2025.01.01-2026.05.08 | +567.49% | 4422 | 1.07 | 43.01% |

## Live Package

- `build/suis_live_package/MQL5/Experts/Suis/SuisM5_v1.ex5`
- `build/suis_live_package.zip`

Rekomendasi saat ini: Suis hanya dipertahankan sebagai fallback M5 yang lebih tahan latency daripada Acane M1, tetapi perlu retune lagi sebelum live serius di `XAUUSDm`.
