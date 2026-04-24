# v10 Summary

Current official `v10` source:
- `/Users/naufalrachmandani/Hobby/MT5 XAU 15m/mt5/InvictusForward1M15_v10.mq5`
- timeframe: `M5`
- role: `dual-engine M5`

## Current Main Verify

Official `v10` sekarang memakai:
- sell engine `v9-style` yang tetap fokus pada regime bearish `2026`
- buy engine `hybrid breakout + pullback reclaim`
- `base-style zone retest` yang mengambil reclaim ke midpoint candle body dan menambah frequency di sisi buy
- `buy-only add-on engine` yang tetap aktif jika trade buy utama sudah profit dan trend masih searah
- anti-chop gate berbasis `EMA hold + side flips`
- tuning champion saat ini:
  - `BuyRiskMultiplier = 0.60`
  - `WeakBuyRiskMultiplier = 0.22`
  - `MaxPositions = 5`
  - `EnableZoneRetestEngine = true`
  - `ZoneAllowWeakRegime = true`
  - `ZoneUseCoreHours = false`
  - `ZoneLookback = 11`
  - `ZoneMinBodyRatio = 0.54`
  - `ZoneBreakATR = 0.04`
  - `ZoneRiskMultiplier = 0.60`
  - `ZoneRR = 1.40`
  - `EnableAddOnEngine = true`
  - `EnableBuyAddOns = true`
  - `EnableSellAddOns = false`
  - `AddOnMinProgressR = 0.80`
  - `AddOnMinBodyRatio = 0.58`
  - `AddOnRiskMultiplier = 0.35`
  - `AddOnRR = 1.10`
  - `AddOnMaxHoldBars = 12`
  - `CloseOnRegimeFlip = false`
  - `ChopLookbackBars = 10`
  - `MaxEmaFlips = 3`
  - `HoldBars = 2`
  - `HoldBufferATR = 0.05`

Hasil official champion saat ini:
- `2025-current`: `+307.79%`, `PF 1.50`, `WR 56.95%`, `Trades 446`, `EqDD 50.74%`
- `2026-only`: `+308.93%`, `PF 2.73`, `WR 61.98%`, `Trades 121`, `EqDD 9.22%`
- `recent 2m (2026.02.22 - 2026.04.22)`: `+142.52%`, `PF 3.61`, `WR 71.70%`, `Trades 53`, `Trades/week 6.29`, `EqDD 9.19%`
- `recent 1m (2026.03.22 - 2026.04.22)`: `+58.28%`, `PF 4.71`, `WR 79.17%`, `Trades 24`, `Trades/week 5.42`, `EqDD 9.16%`

## Zone-Retest Round 1

Target ronde ini: ambil ide `base` dan `invictus-ea-explorer.html`, lalu adaptasi ke `M5` agar trade count naik tanpa jatuh menjadi mixed-regime noise.

Hasil 10 preset ada di [v10_zone_m5_round1/summary.md](/Users/naufalrachmandani/Hobby/MT5%20XAU%2015m/build/v10_zone_m5_round1/summary.md).

Top hasilnya:
- `zone_buyheavy`: `recent 2m +142.52%`, `53 trades`, `2026-only +318.57%`
- `zone_dual_hold`: `recent 2m +127.29%`, `53 trades`, `2026-only +312.90%`
- `zone_push`: `recent 2m +133.81%`, `54 trades`, `2026-only +295.90%`

Validasi full-window `2025-current`:
- `control`: `+218.17%`, `PF 1.60`, `Trades 352`, `EqDD 32.92%`
- `zone_buyheavy`: `+305.71%`, `PF 1.52`, `Trades 447`, `EqDD 50.80%`
- `zone_mid`: `+228.46%`, `PF 1.57`, `Trades 400`, `EqDD 38.96%`
- `zone_soft`: `+185.87%`, `PF 1.44`, `Trades 453`, `EqDD 47.40%`
- `zone_dual_hold`: `+168.74%`, `PF 1.40`, `Trades 454`, `EqDD 54.14%`
- `zone_push`: `+116.54%`, `PF 1.26`, `Trades 487`, `EqDD 64.82%`

Kesimpulan ronde ini:
- `zone_buyheavy` adalah champion profit-first
- `zone_mid` adalah candidate terbaik untuk jalur **DD-trim** dari arsitektur yang sama: profit masih jauh di atas control, tetapi DD lebih rendah daripada `zone_buyheavy`
- `zone_push` memang paling banyak trade, tapi DD dan kualitas full-window memburuk terlalu jauh
- `zone_dual_hold` kuat di `2026-only`, tapi kalah bersih dari `buyheavy`
- karena kamu minta prioritas sekarang adalah target profit dan quantity, `zone_buyheavy` dipromosikan ke `v10` official
- preset pendamping juga saya siapkan:
  - [InvictusForward1M15_v10.default_2026.set](/Users/naufalrachmandani/Hobby/MT5%20XAU%2015m/mt5/InvictusForward1M15_v10.default_2026.set) = profit-first / aggressive
  - [InvictusForward1M15_v10.trim_2026.set](/Users/naufalrachmandani/Hobby/MT5%20XAU%2015m/mt5/InvictusForward1M15_v10.trim_2026.set) = DD-trim companion

## Score Layer & Trade Notes

`v10` sekarang punya layer `score + grade + tags + note` di setiap signal. Setelah live review `2026.04.24`, score tidak lagi netral penuh:

- order comment MT5 sekarang compact, misalnya `Inv|PB|S90|A|RG|CH|BX`
- log `Experts` sekarang menulis note yang lebih panjang, misalnya engine, score, grade, tags, RR, SL/TP, dan alasan singkat trade
- current engine codes:
  - `BE` = bearish engine
  - `PB` = bullish pullback reclaim
  - `BO` = bullish breakout
  - `SB` = bullish sub-engine

Ronde score-behavior pertama dan livefix week-check sudah diuji. Kesimpulannya:

- score layer **berhasil** sebagai observability / audit layer
- live loss `BE S68 WG XH` menunjukkan score rendah tidak boleh lagi ikut masuk di live default
- default official sekarang memakai:
  - `V10_MinTradeScore = 72`
  - `V10_ScoreRRBonus = 0.00`
  - `V10_ScoreRiskBonus = 1.00`
- tambahan guard:
  - `V10_WeakOutsideSellQuickExit = true`
  - `V10_WeakOutsideSellExitBars = 6`
- validasi forced-parameter terbaru:
  - `2026.04.20 - 2026.04.25`: `0 trades` pada tester; artinya trade live `2026.04.24 09:30` tidak tereplikasi oleh default forced-parameter
  - `2026.04.10 - 2026.04.25`: `+12.50%`, `PF 4.08`, `WR 75.00%`, `Trades 8`, `EqDD 4.65%`
  - `2026.01.01 - 2026.04.25`: `+308.93%`, `PF 2.73`, `WR 61.98%`, `Trades 121`, `EqDD 9.22%`

Artinya `v10` sekarang tetap agresif, tetapi score `R` seperti `S68` tidak lagi boleh masuk pada default live.

## Recent 2M Check

Saya juga rerun `v10` untuk window recent yang lebih relevan ke workflow `M5`:
- `2026.02.22 - 2026.04.22`
- `XAUUSDc`
- `M5`
- `Deposit 100 USD`
- `Leverage 1:100`

Baseline official terbaru:
- `+96.02%`
- `PF 3.67`
- `WR 70.45%`
- `44 trades`
- `5.13 trades/week`
- `EqDD 9.45%`

Kesimpulan pentingnya:
- mixed-regime unlock yang saya uji memang bisa mendorong `10-39 trades/week`, tetapi hampir semuanya menghancurkan expectancy; itu membuktikan bottleneck-nya bukan “kurang agresif”, melainkan mixed regime yang terlalu noisy
- continuation sub-engine bull/bear juga sudah diuji. Hasil terbaiknya hanya menaikkan flow ke sekitar `6.7 trades/week`, tetapi full-window jadi lebih buruk
- solusi yang akhirnya menang adalah **buy-only add-on engine**:
  - tidak membuka sinyal baru di mixed regime
  - hanya menambah posisi buy saat trade utama sudah dalam profit dan trend masih searah
  - versi final `buyonly_soft` memberi uplift recent dan tetap menjaga `2025-current` di atas official lama
- ringkasan eksperimen quantity ada di:
  - [v10_tradecount_round1/summary.md](/Users/naufalrachmandani/Hobby/MT5%20XAU%2015m/build/v10_tradecount_round1/summary.md)
  - [v10_tradecount_round2/summary.md](/Users/naufalrachmandani/Hobby/MT5%20XAU%2015m/build/v10_tradecount_round2/summary.md)
  - [v10_tradecount_round3/summary.md](/Users/naufalrachmandani/Hobby/MT5%20XAU%2015m/build/v10_tradecount_round3/summary.md)

Implikasi praktis:
- `v10` official tetap menjaga quality, tetapi sekarang tidak lagi seterlalu ketat seperti sebelumnya
- quantity naik dari `36 -> 44 trades` pada recent 2 bulan tanpa membuka mixed-regime noise
- improvement ini datang dari stacking winner, bukan dari memperbanyak sinyal jelek

## TP Manager / Partial Runner

`v10` sekarang juga punya `staged TP manager`, tetapi default official tetap `off`.

Yang sudah diimplementasikan di source:
- `TP1` partial close pada `V10_TP1R`
- sisa posisi di-extend ke `RunnerRR`
- setelah profit lanjut, `SL` bisa ditarik dengan `ATR trail`
- state posisi disimpan per-ticket dan sekarang dibersihkan pada `OnInit/OnDeinit` supaya tidak bocor antar backtest

Validasi bersih yang sudah saya dapat:
- `control_off_fix` pada `2026-only`: `+180.63%`, `PF 3.12`, `WR 62.50%`, `EqDD 9.56%`
- `tp_base_fix` pada `2026-only`: `+153.88%`, `PF 2.94`, `WR 76.56%`, `EqDD 13.07%`
- `tp_base` pada `2025-11`: `+4.32%`, `PF 1.19`, `EqDD 21.18%`
- `control_off` pada `2025-11`: `+5.77%`, `PF 1.25`, `EqDD 20.98%`

Kesimpulannya:
- TP manager **berfungsi**: partial close dan runner memang hidup
- tetapi pada validasi yang sudah bersih, dia **menaikkan win rate** sambil **menurunkan net profit / PF**
- karena itu saya tidak mempromosikan TP manager sebagai default official
- input tetap saya simpan di source dan preset supaya nanti bisa dipakai lagi untuk ronde trend-engine berikutnya

## DD Readout

- DD `2025-current` **bukan** karena satu bulan merah saja.
- Dari analisis report penuh di [/Users/naufalrachmandani/Hobby/MT5 XAU 15m/build/v10_dd_analysis/analysis.md](/Users/naufalrachmandani/Hobby/MT5%20XAU%2015m/build/v10_dd_analysis/analysis.md):
  - peak balance kecil tercapai pada `2025-04-08 16:06:38`
  - trough balance DD terjadi pada `2025-12-17 10:34:28`
  - max balance DD span = `43.59`
- Artinya problem utamanya adalah **periode underwater panjang dari April sampai Desember 2025**, bukan sekadar Desember 2025 yang sedikit merah.
- Source kebocoran yang paling jelas:
  - `long` fast-fail adalah sumber utama DD
  - `long` holding `<=30m` = `-51.51`
  - `long` holding `30-60m` = `-16.83`
  - sebaliknya `long` holding `1-3h` = `+70.34`
  - `short` overall justru positif `+33.05`
- Jam entry long yang paling merusak:
  - `07`, `10`, `17`
- Jam exit loss terburuk:
  - `long` exit `08`, `11`, `10`
  - `short` exit `13`
- Implikasi praktis:
  - DD tinggi di `v10` current lebih cocok dibedah sebagai **masalah buy yang cepat invalid / terlalu dini**, bukan masalah sell global.

## DD Repair Candidate

Trade-level what-if menunjukkan jalur repair yang paling kuat bukan di sell, melainkan di `fast-fail long`:

- `block all long bad hours 07/08/10/12/13/14/17`: net `+115.04`, DD abs `30.03`, DD pct `13.96%`
- `block BULL PB bad hours 07/08/10/12/13/14/17`: net `+107.68`, DD abs `30.85`, DD pct `14.85%`
- `remove long <=30m`: net `+102.37`, DD abs `19.67`, DD pct `9.72%`
- `halve loss on long <=30m`: net `+109.51`, DD abs `25.22`, DD pct `12.04%`

Interpretasinya:

- penyebab terbesar underwater April-Desember adalah `long` yang masuk di jam buy yang secara historis memang lemah
- fix yang tervalidasi paling bersih saat ini adalah `buy core-hour whitelist`
- hook `fast-fail guard` tetap disimpan di source untuk ronde berikutnya, tetapi belum mengalahkan `core-hours only`

Winner yang sekarang dibekukan:

- `V10_UseBuyCoreHours = true`
- buy hanya aktif di jam inti yang historis sehat
- sell engine tetap tidak diutak-atik

Detail kandidat ada di [repair_candidates.md](/Users/naufalrachmandani/Hobby/MT5%20XAU%2015m/build/v10_dd_analysis/repair_candidates.md).

## Research Outcome

- `v10` dibuat karena `v9` terlalu spesifik ke regime bearish/mixed `2026`.
- Ronde pertama merombak buy dan sell sekaligus:
  - hasilnya gagal; `control` masih `2025-current -55.80%`
  - kesimpulan: mengganti dua sisi sekaligus membuat diagnosis kabur
- Ronde kedua mengunci sell kembali ke pola `v9`, lalu hanya mencari uplift di buy:
  - `control_hybrid`: `2025-current -3.97%`, `2026-only +117.95%`
  - ini membuktikan arsitektur gabungan memang lebih sehat daripada ronde pertama
- Sweep buy yang terlalu terbuka tetap gagal:
  - `balanced_guard`: `2025-current -19.95%`
  - `bearish_anchor`: `2025-current -46.87%`
  - `bull_open`: November tetap terlalu bocor
- Inspirasi paling berguna dari riset TradingView justru bukan indikator baru, tetapi:
  - `anti-chop / slope gate`
  - `ATR-based volatility gate`
  - `partial/managed winner logic`
- Dari situ saya turunkan anti-chop filter berbasis `EMA hold + side flips`, dan ini jadi uplift terbesar:
  - `2025-current` naik dari `+0.53%` ke `+49.66%`
  - `2026-only` naik dari `+103.74%` ke `+115.15%`
  - `2026-only EqDD` turun dari `33.82%` ke `19.88%`
- Ronde DD terbaru menunjukkan langkah yang lebih kuat lagi:
  - `buy core-hour whitelist`
  - `2025-current` naik dari `+49.66%` ke `+199.87%`
  - `2026-only` naik dari `+115.15%` ke `+180.61%`
  - `2026-only EqDD` turun dari `19.88%` ke `9.56%`
  - `apr-dec 2025` masih sedikit merah, tetapi loss-nya turun besar dari `-25.63%` ke `-10.93%`
- Ronde quantity terbaru menambahkan layer yang benar-benar menang:
  - `buy-only add-on engine`
  - pada batch candidate, `2025-current` sempat naik lagi dari `+199.87%` ke `+217.80%`
  - `recent 2m` naik dari `+88.02%` ke `+96.02%`
  - `2026-only` tetap kuat di `+182.52%`
  - setelah preset champion dipaksa lewat `ExpertParameters`, official rerun stabil di `+145.06%` untuk full-window tahap itu
- Ronde terbaru berbasis `base + explorer` kemudian membuka jalur yang lebih agresif lagi:
  - `zone retest engine`
  - `zone_buyheavy` akhirnya mengangkat `recent 2m` ke `+142.52%`
  - `2026-only` naik ke `+318.57%`
  - `2025-current` ikut naik ke `+305.71%`
  - trade-off-nya: `2025-current EqDD` melonjak ke `50.80%`
- Insight paling penting:
  - membuka buy lebih lebar memang bisa membantu profit, tetapi harus tetap lewat struktur yang jelas; mixed-regime unlock mentah tetap merusak full-window
  - `fast-fail guard` saja tidak cukup
  - uplift yang paling bersih sebelumnya datang dari **membatasi buy ke jam yang memang punya expectancy sehat**
  - uplift terbaru datang dari **base-style zone retest + buy-heavy risk**, bukan dari mixed-regime unlock

## Borrow Check: v4/v5 -> v10

Saya juga cek langsung apakah “cara berpikir” `v4/v5` pada bulan bullish `2025-04` dan `2025-05` bisa dicangkok ke `v10`.

Yang diuji:
- `strong bull` boleh melebar ke luar `buy session`
- `strong bull` boleh keluar dari `buy core hours`
- di luar `core hours`, buy dibatasi ke `pullback-only`
- strong-bull buy risk dinaikkan sedikit

Ringkasan hasilnya ada di [v10_bull_borrow_narrow/summary.md](/Users/naufalrachmandani/Hobby/MT5%20XAU%2015m/build/v10_bull_borrow_narrow/summary.md).

Kesimpulannya tegas:
- graft itu memang bisa memperbaiki `2025-04` dari `-8.70%` menjadi sekitar `+6%` sampai `+8%`
- tetapi semua varian yang selesai tetap kalah dari `v10` official pada `2025-current` dan `2026-only`
- jadi perilaku profit `v4/v5` di April-Mei **bukan** sesuatu yang bisa dipinjam secara tipis ke `v10`; profit mereka tetap sangat terkait dengan arsitektur dan exposure lama

## Practical Conclusion

- `v10` sekarang berhasil jadi **engine gabungan bullish + bearish M5** yang benar-benar layak diperhitungkan.
- Dibanding `v9`:
  - `2026-only`: profit jauh lebih tinggi (`+318.57%` vs `+98.18%`), dengan DD tetap lebih rendah (`9.26%` vs `19.59%`)
  - `2025-current`: profit jauh lebih tinggi (`+305.71%` vs `+17.21%`), tetapi DD juga lebih kasar (`50.80%` vs `58.50%` masih tetap lebih baik, tetapi tidak lagi “bersih”)
- Jadi posisi `v10` sekarang:
  - sudah **mengalahkan `v9`** sebagai jalur `M5` utama
  - untuk `M5`, dia sekarang paling menarik jika target utamanya profit agresif dan trade count lebih tinggi
