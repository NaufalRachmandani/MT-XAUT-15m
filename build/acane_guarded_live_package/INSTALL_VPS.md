# Acane Guarded Live Package

Copy `MQL5/Experts/Acane/AcaneM1_v1_guarded.ex5` ke folder data MetaTrader 5 di VPS.

Setup chart:
- Symbol: pakai symbol gold yang aktif di akun, misalnya `XAUUSD`, `XAUUSDm`, atau `XAUUSDc` sesuai Market Watch.
- Timeframe: `M1`
- Attach EA: `AcaneM1_v1_guarded`
- Algo Trading: ON
- Jangan jalankan bersamaan dengan build Acane lama pada symbol/akun yang sama.

Validasi setelah attach:
- Buka tab `Experts`.
- Pastikan muncul log `ACANE LOCKED PROFILE v1.03 GUARDED`.
- Jika masih muncul `v1.02 PROFIT30` atau `AcaneM1_v1_profit30`, berarti VPS masih memakai file lama.

Catatan risiko: profile ini tetap agresif, tetapi build terbaru memakai daily loss guard `15%`, account circuit `15%`, open-risk cap `12%`, same-side cap `8%`, basket stop `9%`, dan cooldown setelah fast-loss beruntun. Batas ini bukan garansi absolut karena slippage, gap, spread, koneksi, atau close failure bisa membuat loss melewati angka guard.
