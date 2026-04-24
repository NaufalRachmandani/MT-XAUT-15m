# MT XAU T 15m

Repository riset EA MT5 untuk `XAUUSDc`.

Workspace aktif sekarang sengaja dipersempit agar tidak penuh versi yang sudah tidak layak pakai. Varian lama yang gagal atau tidak lagi diprioritaskan dipensiunkan dari working tree dan tetap aman di Git history.

## Versi Aktif

- [InvictusForward1M15_v6.mq5](/Users/naufalrachmandani/Hobby/MT5%20XAU%2015m/mt5/InvictusForward1M15_v6.mq5)
- [InvictusForward1M15_v8.mq5](/Users/naufalrachmandani/Hobby/MT5%20XAU%2015m/mt5/InvictusForward1M15_v8.mq5)
- [InvictusForward1M15_v10.mq5](/Users/naufalrachmandani/Hobby/MT5%20XAU%2015m/mt5/InvictusForward1M15_v10.mq5)
- [InvictusBullM5_v11.mq5](/Users/naufalrachmandani/Hobby/MT5%20XAU%2015m/mt5/InvictusBullM5_v11.mq5)
- [InvictusBearM5_v11.mq5](/Users/naufalrachmandani/Hobby/MT5%20XAU%2015m/mt5/InvictusBearM5_v11.mq5)
- [InvictusCombinedM5_v11.mq5](/Users/naufalrachmandani/Hobby/MT5%20XAU%2015m/mt5/InvictusCombinedM5_v11.mq5)

## Mana yang Dipakai

- `v8` = pilihan utama `M15` untuk `2026-only`
  - profit lebih rendah, tapi DD paling sehat
  - cocok kalau prioritasnya survivability dan equity curve bersih
- `v6` = pilihan agresif `M15`
  - profit lebih tinggi dari `v8`
  - DD sekitar `30%`, jadi jelas lebih kasar
- `v10` = jalur utama `M5`
  - sekarang memakai arsitektur `base-style zone retest` yang diadaptasi ke `M5`
  - lebih agresif daripada `v8`
  - jadi kandidat `M5` utama kalau target utamanya profit dan trade count, bukan DD paling rendah
- `v11` = eksperimen utama split `M5`
  - `BullM5_v11` khusus BUY, `BearM5_v11` khusus SELL
  - `CombinedM5_v11` dipakai untuk backtest portfolio bull+bear
  - kandidat paling agresif saat ini untuk `2026-only`, tapi DD `2025-current` masih kasar

## Snapshot Ringkas

- `v6`
  - `2026-only`: `+58.96%`, `EqDD 29.17%`
  - `2025-current`: `+1662.44%`, `EqDD 29.88%`
- `v8`
  - `2026-only`: `+32.84%`, `EqDD 8.99%`
  - `2025-current`: `+200.21%`, `EqDD 17.45%`
- `v10`
  - `2026-only`: `+308.93%`, `EqDD 9.22%`
  - `2025-current`: `+307.79%`, `EqDD 50.74%`
  - live guard aktif: `MinTradeScore=72` dan quick-exit khusus weak/out-of-session base sell
- `v11 combined`
  - `2026-only`: `+504.76%`, `EqDD 21.28%`, `152 trades`
  - `2025-current`: `+426.34%`, `EqDD 55.03%`, `614 trades`
  - split live aktif: bull magic `2026042411`, bear magic `2026042412`

Ringkasan lintas-window ada di:
- [compare_active_windows_2025current_vs_2026only.md](/Users/naufalrachmandani/Hobby/MT5%20XAU%2015m/build/compare_active_windows_2025current_vs_2026only.md)
- [compare_2026_active_summary.md](/Users/naufalrachmandani/Hobby/MT5%20XAU%2015m/build/compare_2026_active_summary.md)
- [version_catalog.md](/Users/naufalrachmandani/Hobby/MT5%20XAU%2015m/build/version_catalog.md)

## Preset / Config

- `v6`
  - [InvictusForward1M15_v6.backtest.ini](/Users/naufalrachmandani/Hobby/MT5%20XAU%2015m/mt5/InvictusForward1M15_v6.backtest.ini)
  - [InvictusForward1M15_v6.default_2026.set](/Users/naufalrachmandani/Hobby/MT5%20XAU%2015m/mt5/InvictusForward1M15_v6.default_2026.set)
  - [InvictusForward1M15_v6.live_safe_5400usc.set](/Users/naufalrachmandani/Hobby/MT5%20XAU%2015m/mt5/InvictusForward1M15_v6.live_safe_5400usc.set)
- `v8`
  - [InvictusForward1M15_v8.backtest.ini](/Users/naufalrachmandani/Hobby/MT5%20XAU%2015m/mt5/InvictusForward1M15_v8.backtest.ini)
- `v10`
  - [InvictusForward1M15_v10.backtest.ini](/Users/naufalrachmandani/Hobby/MT5%20XAU%2015m/mt5/InvictusForward1M15_v10.backtest.ini)
  - [InvictusForward1M15_v10.default_2026.set](/Users/naufalrachmandani/Hobby/MT5%20XAU%2015m/mt5/InvictusForward1M15_v10.default_2026.set)
  - [InvictusForward1M15_v10.trim_2026.set](/Users/naufalrachmandani/Hobby/MT5%20XAU%2015m/mt5/InvictusForward1M15_v10.trim_2026.set)
- `v11`
  - [InvictusBullM5_v11.default_2026.set](/Users/naufalrachmandani/Hobby/MT5%20XAU%2015m/mt5/InvictusBullM5_v11.default_2026.set)
  - [InvictusBearM5_v11.default_2026.set](/Users/naufalrachmandani/Hobby/MT5%20XAU%2015m/mt5/InvictusBearM5_v11.default_2026.set)
  - [InvictusCombinedM5_v11.default_2026.set](/Users/naufalrachmandani/Hobby/MT5%20XAU%2015m/mt5/InvictusCombinedM5_v11.default_2026.set)

## Dokumentasi HTML

- [InvictusForward-1-Docs_v6.html](/Users/naufalrachmandani/Hobby/MT5%20XAU%2015m/build/InvictusForward-1-Docs_v6.html)
- [InvictusForward-1-Docs_v8.html](/Users/naufalrachmandani/Hobby/MT5%20XAU%2015m/build/InvictusForward-1-Docs_v8.html)
- [InvictusForward-1-Docs_v10.html](/Users/naufalrachmandani/Hobby/MT5%20XAU%2015m/build/InvictusForward-1-Docs_v10.html)
- [InvictusForward-1-Docs_v11.html](/Users/naufalrachmandani/Hobby/MT5%20XAU%2015m/build/InvictusForward-1-Docs_v11.html)

## Backtest Automation

- [MT5_AUTOMATED_BACKTEST.md](/Users/naufalrachmandani/Hobby/MT5%20XAU%2015m/docs/MT5_AUTOMATED_BACKTEST.md)

## Catatan

- Semua varian lama yang tidak lagi dipakai sengaja dihapus dari working tree untuk menjaga riset tetap fokus.
- Kalau suatu saat perlu melihat jalur lama, ambil dari Git history, bukan dari workspace aktif.
