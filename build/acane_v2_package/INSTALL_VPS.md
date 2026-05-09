# AcaneM1 v2 VPS Install

Copy `MQL5/Experts/Acane/AcaneM1_v2.ex5` ke folder data MetaTrader 5.

Setup chart:
- Account: `265874264`
- Server: `Exness-MT5Real38`
- Symbol: `XAUUSD`
- Timeframe: `M1`
- Attach EA: `AcaneM1_v2`
- Algo Trading: ON
- Jangan jalankan `AcaneM1_v2` bersamaan dengan `AcaneM1_v1_guarded_debug` pada symbol/akun yang sama.
- Setelah attach, lakukan migration/sync ke MQL5 VPS.

Validasi setelah migration:
- Tab `Experts` harus menampilkan `ACANE PROFILE v2 BALANCED FAST`.
- Pastikan line tersebut juga menampilkan `account=265874264 accountLeverage=2000`.
- VPS Details harus menampilkan `1 charts, 1 experts`.

Catatan saldo:
- Pastikan account live memang memakai leverage `1:2000`.
- Dengan leverage `1:2000`, backtest deposit `$29` bisa membuka posisi dan aktif trading.
- Jika report/tester terbaca `1:100`, hasilnya bisa berbeda jauh dan saldo kecil bisa tidak cukup margin.
