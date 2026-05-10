# Acane Guarded Debug Throttle Package

Copy `MQL5/Experts/Acane/AcaneM1_v1_guarded_debug_throttle.ex5` ke folder data MetaTrader 5.

Setup chart:
- Account: `265874264`, server `Exness-MT5Real38`
- Symbol: `XAUUSD`
- Timeframe: `M1`
- Attach EA: `AcaneM1_v1_guarded_debug_throttle`
- Algo Trading: ON
- Setelah attach, lakukan migration/sync ke MQL5 VPS.

Validasi setelah migration:
- Buka tab `Experts`.
- Pastikan muncul log `ACANE PROFILE v1.05 GUARDED DEBUG THROTTLE`.
- Pastikan VPS Details menampilkan `1 charts, 1 experts`.

Perbedaan utama dari build debug agresif:
- `MaxPositions`: `12` -> `1`
- `MaxSameSidePositions`: `4` -> `1`
- `MinSecondsBetweenEntries`: `3` -> `180`
- `DailyMaxLossPct`: `15` -> `6`
- `AccountCircuit`: `15` -> `8`
- `MaxOpenRiskPct`: `12` -> `4`
- `BasketLossStopPct`: `9` -> `3`
- `FastLossCooldownAfter`: `2` -> `1`
- `FastLossCooldownSeconds`: `900` -> `3600`
- `BlockEntryHours`: `2,3,5,11,20`

Catatan risiko: build ini tetap agresif pada sinyal yang diterima karena `RiskPercent` dan `MeanReversionRiskMultiplier` tetap seperti debug build. Perubahan utamanya adalah mencegah stacking loss beruntun dan memblok jam yang bocor di backtest 2026.
