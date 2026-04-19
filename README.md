# MT XAU T 15m

Repository riset dan iterasi EA MT5 untuk XAUUSD pada timeframe `M15`, dengan artefak source `.mq5`, preset `.set`, konfigurasi backtest `.ini`, dan catatan hasil backtest.

## Versi Aktif

- [InvictusForward1M15_v6.mq5](/Users/naufalrachmandani/Hobby/MT5%20XAU%2015m/mt5/InvictusForward1M15_v6.mq5)
- [InvictusForward1M15_v7.mq5](/Users/naufalrachmandani/Hobby/MT5%20XAU%2015m/mt5/InvictusForward1M15_v7.mq5)
- [InvictusForward1M15_v8.mq5](/Users/naufalrachmandani/Hobby/MT5%20XAU%2015m/mt5/InvictusForward1M15_v8.mq5)

## Mana yang Cocok untuk 2026

Ringkasan lengkap ada di [compare_2026_active_summary.md](/Users/naufalrachmandani/Hobby/MT5%20XAU%2015m/build/compare_2026_active_summary.md).

### Rekomendasi utama

- **`v8` = kandidat terbaik untuk market 2026**
  - `$100`: `+32.84%`, `PF 2.06`, `EqDD 8.99%`
  - `$10,000`: `+23.84%`, `PF 1.29`, `EqDD 13.91%`
  - Paling seimbang antara profit, PF, dan drawdown lintas ukuran akun.

- **`v6` = kandidat agresif untuk 2026**
  - `$100`: `+58.96%`, `EqDD 29.17%`
  - `$10,000`: `+74.48%`, `EqDD 29.90%`
  - Cocok kalau prioritas utama adalah profit lebih tinggi dan kamu siap menerima DD sekitar `30%`.

- **`v7` = fallback defensif**
  - `$100`: `+28.11%`, `EqDD 9.08%`
  - `$10,000`: `+19.43%`, `EqDD 16.97%`
  - Cocok kalau kamu ingin equity curve yang lebih tenang daripada `v6`.

### Tidak direkomendasikan sebagai versi utama 2026

- `v1`: terlalu lemah di akun kecil
- `v4`: tidak stabil lintas modal, bisa profit di akun kecil tapi rusak di akun besar
- `v5`: profit tinggi di akun kecil, tetapi tidak portable ke akun besar pada regime 2026

## Quick Start

### Backtest

- Gunakan file `.ini` di folder [mt5](/Users/naufalrachmandani/Hobby/MT5%20XAU%2015m/mt5)
- Panduan automasi ada di [MT5_AUTOMATED_BACKTEST.md](/Users/naufalrachmandani/Hobby/MT5%20XAU%2015m/docs/MT5_AUTOMATED_BACKTEST.md)

### Live / Demo preset untuk v6

- Preset default research: [InvictusForward1M15_v6.default_2026.set](/Users/naufalrachmandani/Hobby/MT5%20XAU%2015m/mt5/InvictusForward1M15_v6.default_2026.set)
- Preset aman live kecil/cent: [InvictusForward1M15_v6.live_safe_5400usc.set](/Users/naufalrachmandani/Hobby/MT5%20XAU%2015m/mt5/InvictusForward1M15_v6.live_safe_5400usc.set)

## Dokumentasi HTML

- [InvictusForward-1-Docs_v6.html](/Users/naufalrachmandani/Hobby/MT5%20XAU%2015m/build/InvictusForward-1-Docs_v6.html)
- [InvictusForward-1-Docs_v7.html](/Users/naufalrachmandani/Hobby/MT5%20XAU%2015m/build/InvictusForward-1-Docs_v7.html)
- [InvictusForward-1-Docs_v8.html](/Users/naufalrachmandani/Hobby/MT5%20XAU%2015m/build/InvictusForward-1-Docs_v8.html)

## Catatan

- Semua angka rekomendasi di atas mengacu pada window `2026.01.01 - 2026.04.15`, `XAUUSDc`, `M15`, mode `Every tick`.
- Jangan asumsikan versi terbaik di satu regime akan tetap terbaik di regime lain.
- Equity curve yang tampak mulus di screenshot atau graph saja tidak cukup untuk menyimpulkan bot bagus; tetap perlu lihat PF, DD, trade count, dan stabilitas lintas modal.
