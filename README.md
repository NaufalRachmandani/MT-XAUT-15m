# MT XAU v11

Repository ini sekarang difokuskan ke satu versi aktif: `v11` split engine untuk `XAUUSDc` timeframe `M5`.

Versi lama `v1` sampai `v10` dan cache iterasinya sudah dipindahkan ke Git history. Jika perlu mengambil ulang data lama, gunakan commit sebelum cleanup: `546f3b6`.

## File Aktif

- [InvictusBullM5_v11.mq5](/Users/naufalrachmandani/Hobby/MT5%20XAU%2015m/mt5/InvictusBullM5_v11.mq5): BUY-only engine.
- [InvictusBearM5_v11.mq5](/Users/naufalrachmandani/Hobby/MT5%20XAU%2015m/mt5/InvictusBearM5_v11.mq5): SELL-only engine.
- [InvictusCombinedM5_v11.mq5](/Users/naufalrachmandani/Hobby/MT5%20XAU%2015m/mt5/InvictusCombinedM5_v11.mq5): combined tester untuk backtest portfolio.

## Preset

- [InvictusBullM5_v11.default_2026.set](/Users/naufalrachmandani/Hobby/MT5%20XAU%2015m/mt5/InvictusBullM5_v11.default_2026.set)
- [InvictusBearM5_v11.default_2026.set](/Users/naufalrachmandani/Hobby/MT5%20XAU%2015m/mt5/InvictusBearM5_v11.default_2026.set)
- [InvictusCombinedM5_v11.default_2026.set](/Users/naufalrachmandani/Hobby/MT5%20XAU%2015m/mt5/InvictusCombinedM5_v11.default_2026.set)

## Dokumentasi

- [InvictusForward-1-Docs_v11.html](/Users/naufalrachmandani/Hobby/MT5%20XAU%2015m/build/InvictusForward-1-Docs_v11.html)
- [v11_summary.md](/Users/naufalrachmandani/Hobby/MT5%20XAU%2015m/build/v11_summary.md)
- [v11_split_m5/summary.md](/Users/naufalrachmandani/Hobby/MT5%20XAU%2015m/build/v11_split_m5/summary.md)

## Backtest Snapshot

Setup: `XAUUSDc`, `M5`, `Deposit 100 USD`, `Leverage 1:100`, mode `Every tick`.

| Bot | Window | Net Profit | Trades | Win Rate | PF | EqDD |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Combined tester | 2026 YTD | +677.97% | 146 | 60.96% | 2.98 | 17.74% |
| Combined tester | 2026.04.10-2026.04.25 | +10.43% | 12 | 50.00% | 2.22 | 7.30% |
| Bull-only | 2026 YTD | +335.28% | 118 | 60.17% | 2.82 | 17.71% |
| Bull-only | 2026.04.10-2026.04.25 | +10.23% | 10 | 50.00% | 2.84 | 4.87% |
| Bear-only | 2026 YTD | +19.02% | 73 | 50.68% | 1.16 | 32.20% |
| Bear-only | 2026.04.10-2026.04.25 | +12.28% | 13 | 61.54% | 1.91 | 12.60% |

Catatan: untuk live split, jumlah trade aktual berasal dari `Bull-only + Bear-only`. Combined tester tetap dipakai sebagai portfolio proxy karena satu equity curve lebih dekat untuk membaca DD total.

## Market Regime Study

Monthly matrix dari `2023.01` sampai `2026.04` menunjukkan v11 sangat regime-specific:

| Year | Base Sum Monthly Net | Guard Sum Monthly Net | Base Red Months | Guard Red Months | Base Worst DD | Guard Worst DD |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2023 | -19.37 | -26.86 | 7 | 7 | 29.43% | 26.03% |
| 2024 | -72.19 | -75.08 | 7 | 7 | 36.43% | 32.35% |
| 2025 | -69.03 | -57.20 | 8 | 8 | 42.83% | 39.38% |
| 2026 | +249.43 | +285.16 | 0 | 0 | 26.03% | 20.23% |

Interpretasi: `v11` cocok untuk 2026 expansion regime, tetapi tidak otomatis robust untuk 2023-2025. Daily Guard mengurangi DD dan membantu 2025/2026, tetapi belum mengubah hostile months menjadi edge positif.

## Daily Guard Default

Default sekarang memakai `balanced_guard`:

- `V11_EnableDailyGuard=true`
- `V11_DailyMaxLossPct=8.00`
- `V11_DailyProfitLockStartPct=12.00`
- `V11_DailyMaxGivebackPct=4.00`
- `V11_MaxConsecutiveLosses=3`
- `V11_LossCooldownMinutes=180`
- `V11_DailyClosePositionsOnStop=false`

Ini adalah entry guard, bukan hard liquidation guard. Jika daily loss menyentuh limit, EA berhenti membuka entry baru sampai hari berikutnya. Posisi aktif tidak dipaksa close karena varian close-on-stop menurunkan hasil backtest.

## Weekend Technical Research

Setelah baseline v11 dipush, branch `codex/v11-technical-improvement` menambahkan engine eksperimental `Impulse Pullback`:

- Marker comment: `BUY_IMPULSE` / `SELL_IMPULSE`, internal marker `IB` / `IS`.
- Default tetap `V11_EnableImpulsePullbackEngine=false`.
- Hasil 11 kandidat di combined tester menunjukkan control sebelum Daily Guard masih menang atas impulse variants: `+558.51%` YTD, 155 trades, PF `2.70`, EqDD `17.71%`.
- Kandidat terbaik impulse hanya mendekati control, bukan mengalahkan: `sell_runner` `+547.94%` YTD dengan trade count sama; `sell_aggressive` menaikkan trades ke 201 tetapi net turun ke `+485.94%`.

Keputusan: engine ini disimpan sebagai opsi riset/diagnostic, bukan default live.

## Log dan Comment

Comment trade sekarang dibuat lebih mudah dibaca tanpa merusak marker internal EA.

Contoh comment lama yang membingungkan: `B11|ZB|S76|B|WG|ZN`.

Contoh comment baru: `B11|BUY_ZONE|ZB|S76|B|WG|ZN`.

Kode penting:

- `BUY_ZONE` / `SELL_ZONE`: entry dari retest area harga.
- `BUY_BREAK` / `SELL_BREAK`: entry breakout sesuai arah.
- `BUY_PULLBACK`: buy setelah pullback di trend bullish.
- `BUY_IMPULSE` / `SELL_IMPULSE`: engine riset impulse-pullback. Default nonaktif karena 11 kandidat belum mengalahkan control.
- `BUY_COMP` / `SELL_COMP`: breakout dari kompresi/range sempit.
- `BUY_ADDON` / `SELL_ADDON`: posisi tambahan ketika trade sebelumnya sudah bergerak benar.
- Untuk riset kenapa setup ditolak, ubah input `V11_LogRejectedSignals=true`. EA akan print `V11 REJECT` untuk kandidat yang score-nya dekat threshold.
- Untuk monitor ringkas di tab `Experts`, ubah `V11_LogStatusOnNewBar=true`. EA akan print regime, jumlah posisi, spread, equity, dan apakah bar itu entry.

## Exit Management

- Breakeven aktif: saat posisi bergerak `0.80R`, SL digeser ke area entry plus lock kecil `0.20`.
- TP manager / partial close masih default `false`. Hasil exit matrix menunjukkan partial/trailing menurunkan profit walau trade count naik.
- Bull-only dan combined tester memakai `time_strict`: posisi boleh ditutup saat melewati batas bar walau masih minus.
- Daily Guard sekarang aktif sebagai risk layer setelah exit matrix: combined 2026 YTD naik ke `+677.97%` dengan EqDD `17.74%`.
- Bear-only tidak memakai `time_strict` karena validasi split menunjukkan performa sell memburuk.
- Log exit sekarang lebih jelas: `MOVE_SL_TO_BE`, `TIME_CLOSE`, `TP1_RUNNER_SET`, `TRAIL_SL`, `FAST_FAIL_CLOSE`, dan `WEAK_SELL_QUICK_EXIT`.

## Bear Safety Update

Iterasi khusus Bear memilih `safe_break_quality`, bukan safe mode yang terlalu ketat. Default Bear sekarang memperketat kualitas SELL breakout:

- `V10_MinTradeScore=64`
- `V10_MinBreakATR=0.05`
- `V10_WeakSellMinBreakATR=0.08`
- `V10_MinBodyRatio=0.46`
- `V10_WeakSellMinBodyRatio=0.50`

Efek YTD Bear: net profit naik dari `+60.73%` ke `+68.37%`, PF naik dari `1.43` ke `1.50`, dan EqDD turun dari `36.76%` ke `32.25%`.

## Live Setup

MT5 hanya bisa attach satu EA per chart. Untuk live split:

1. Buka chart pertama: `XAUUSDc`, timeframe `M5`, attach `InvictusBullM5_v11`.
2. Buka chart kedua: `XAUUSDc`, timeframe `M5`, attach `InvictusBearM5_v11`.
3. Pastikan `Algo Trading` ON.
4. Gunakan default input/preset kecuali memang sedang eksperimen.

`InvictusCombinedM5_v11` sebaiknya dipakai untuk backtest portfolio, bukan setup live utama.

## Automation

- [MT5_AUTOMATED_BACKTEST.md](/Users/naufalrachmandani/Hobby/MT5%20XAU%2015m/docs/MT5_AUTOMATED_BACKTEST.md)
- [backtest_v11_split.py](/Users/naufalrachmandani/Hobby/MT5%20XAU%2015m/tools/backtest_v11_split.py)
