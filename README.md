# Invictus Forward-8 Research

Repository ini sekarang difokuskan untuk riset `InvictusForward-8` saja. Artefak bot lain, build lama, dan eksperimen Forward-8 yang bukan jalur utama sudah dibersihkan dari workspace.

## Kept Scope

- `Base`: source original dari zip di `invictusforward-8-research/source/original/InvictusForward-8`.
- `V5`: quality/profit boost reference di `invictusforward-8-research/invictus8_v5_quality_boost`.
- `V6`: archive-aware balanced reference di `invictusforward-8-research/invictus8_v6_jun2025_archive_boost`.
- `Latest / V8`: risk-certified stress attempt di `invictusforward-8-research/invictus8_v8_risk_certified`.

## Current Recommendation

V8/latest belum live-ready untuk `1000 USC`. V6 masih baseline paling masuk akal untuk riset lanjutan karena profit tetap kuat dengan drawdown lebih terkendali dibanding V5 max/raw. V8 berguna sebagai bukti stress-risk dan kandidat micro-risk, bukan sebagai set live final.

Key reports:

- `invictusforward-8-research/invictus8_v5_quality_boost/reports/SUMMARY.md`
- `invictusforward-8-research/invictus8_v6_jun2025_archive_boost/reports/SUMMARY.md`
- `invictusforward-8-research/invictus8_v8_risk_certified/reports/SUMMARY.md`

## Safety Notes

- Native MT5 Strategy Tester `.htm` tetap menjadi source of truth.
- Python hanya dipakai untuk orchestration, parsing, dan ringkasan.
- Local MT5 research configs harus tetap memakai `AllowLiveTrading=0`, `UseRemote=0`, `UseCloud=0`, dan sound events off.
- Jangan menyalakan local Algo Trading saat VPS live masih menjalankan EA.
