# v8 Summary

Window resmi riset: `2026.01.01 - 2026.04.15`, `XAUUSDc`, `M15`, `Deposit 100 USD`, `Leverage 1:100`, mode `Every tick`.

## Champion

- Source final: [/Users/naufalrachmandani/Hobby/MT5 XAU 15m/mt5/InvictusForward1M15_v8.mq5](/Users/naufalrachmandani/Hobby/MT5%20XAU%2015m/mt5/InvictusForward1M15_v8.mq5)
- HTML final: [/Users/naufalrachmandani/Hobby/MT5 XAU 15m/build/InvictusForward-1-Docs_v8.html](/Users/naufalrachmandani/Hobby/MT5%20XAU%2015m/build/InvictusForward-1-Docs_v8.html)
- Validating report: [/Users/naufalrachmandani/Library/Application Support/net.metaquotes.wine.metatrader5/drive_c/Program Files/MetaTrader 5/Reports/InvictusForward1M15_v8_round4_buyrisk010_XAUUSDc_M15_20260101_20260415.htm](</Users/naufalrachmandani/Library/Application Support/net.metaquotes.wine.metatrader5/drive_c/Program Files/MetaTrader 5/Reports/InvictusForward1M15_v8_round4_buyrisk010_XAUUSDc_M15_20260101_20260415.htm>)

## Metrics

- Net profit: `32.84` atau `+32.84%`
- Profit factor: `2.06`
- Win rate: `58.90%`
- Total trades: `73`
- Max balance DD: `6.97%`
- Max equity DD: `8.99%`

## Champion Logic

- Tambah mode `bearish regime` berbasis `bias bearish H4 + ADX H4 >= 28 + breakdown close/high lookback 3 candle H4`
- Saat bearish regime aktif, `buy` dipersempit ke `score >= 95`
- Risk `buy` saat bearish regime diturunkan ke `0.10x`, jadi buy tidak dimatikan total tetapi tetap sangat kecil
- Sideways layer dimatikan saat bearish regime aktif
- Semua improvement `v7` tetap dipertahankan: risk-based sizing, cooldown `1 bar`, `pending manager`, `breakeven manager`, toxic hours `{3,7,8,9,10,17}`, dynamic trend SL

## Apa yang Ternyata Tidak Membantu

- Melarang buy total saat bearish regime memang membantu, tetapi tidak sebaik menyisakan sedikit buy participation
- Menambah sell risk tidak memberi perubahan berarti
- Memperdalam lookback bearish ke `5` candle justru menurunkan hasil
- Risk uplift di atas champion bisa menaikkan profit nominal tipis, tetapi PF turun dan DD naik

## Takeaway

`v8` bukan profit leader absolut, tetapi ini peningkatan bersih di atas `v7`: profit naik dari `+28.11%` ke `+32.84%`, PF naik dari `1.79` ke `2.06`, dan max equity DD turun tipis dari `9.08%` ke `8.99%`.
