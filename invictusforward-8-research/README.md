# InvictusForward-8 Research Folder

Folder ini sengaja dibuat terpisah untuk riset `InvictusForward-8`.

## Struktur Aktif

- `source/original/InvictusForward-8`: Base/source original dari zip.
- `invictus8_v5_quality_boost`: V5 quality/profit boost reference.
- `invictus8_v6_jun2025_archive_boost`: V6 archive-aware balanced reference.
- `invictus8_v8_risk_certified`: versi terbaru/latest risk-certified stress attempt.
- `tools/run_invictus8_v5_quality_boost.py`: native MT5 runner/helper V5.
- `tools/run_invictus8_v8_risk_certified.py`: native MT5 runner/helper V8.

## Report Utama

- `invictus8_v5_quality_boost/reports/SUMMARY.md`
- `invictus8_v6_jun2025_archive_boost/reports/SUMMARY.md`
- `invictus8_v8_risk_certified/reports/SUMMARY.md`

## MT5 Native Rules

Setiap run riset harus tetap:

- `Model=4`
- `Leverage=1:2000`
- `UseLocal=1`
- `UseRemote=0`
- `UseCloud=0`
- `AllowLiveTrading=0`
- `Visual=0`
- `ShutdownTerminal=1`

Jangan pakai hasil 2025 cent yang history quality rendah untuk keputusan logic. Untuk archive/tick proxy, pisahkan label account dan symbol supaya hasil tidak tercampur dengan cent confirmation.
