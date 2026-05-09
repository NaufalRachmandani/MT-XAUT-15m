# AcaneM1 v2.10 VPS Install

Copy `MQL5/Experts/Acane/AcaneM1_v2.ex5` ke folder data MetaTrader 5.

Setup chart:

- Account: `265874264`
- Server: `Exness-MT5Real38`
- Symbol: `XAUUSD`
- Timeframe: `M1`
- Attach EA: `AcaneM1_v2`
- Algo Trading: ON hanya untuk proses attach/migration yang benar
- Jangan jalankan v1 dan v2 bersamaan di account/symbol yang sama
- Setelah attach, lakukan migration/sync ke MQL5 VPS

Validasi setelah migration:

- Tab `Experts` harus menampilkan `ACANE PROFILE v2.10 REALTICK MRV RG`.
- Line tersebut harus menampilkan `account=265874264 accountLeverage=2000`.
- VPS Details harus menampilkan `1 charts, 1 experts`.
- Setelah migration berhasil, local MT5 boleh ditutup agar tidak double-run.

Catatan saldo:

- Backtest final memakai deposit `$29`, leverage `1:2000`, real ticks, dan delay `50ms`.
- Versi ini jauh lebih selektif daripada build sebelumnya. Itu sengaja untuk menghindari overtrade seperti Jumat 2026.05.08.
