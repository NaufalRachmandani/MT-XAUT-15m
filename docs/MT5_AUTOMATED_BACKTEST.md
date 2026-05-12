# MT5 Automated Backtest For Invictus Forward-8

Panduan ini hanya untuk riset lokal `InvictusForward-8`. Jangan gunakan flow ini untuk menjalankan live trading lokal saat VPS masih aktif.

## Safety Defaults

Setiap `.ini` tester yang dibuat otomatis wajib memakai:

```ini
[Experts]
AllowLiveTrading=0

[Tester]
Model=4
Visual=0
UseLocal=1
UseRemote=0
UseCloud=0
ShutdownTerminal=1
```

Tambahkan juga blok event sound off jika menjalankan terminal lewat `/config`:

```ini
[Events]
Enable=0
ConnectEnable=0
DisconnectEnable=0
Expert AdvisorEnable=0
Testing FinishedEnable=0
```

## Active Research Folders

- Base: `invictusforward-8-research/source/original/InvictusForward-8`
- V5: `invictusforward-8-research/invictus8_v5_quality_boost`
- V6: `invictusforward-8-research/invictus8_v6_jun2025_archive_boost`
- Latest/V8: `invictusforward-8-research/invictus8_v8_risk_certified`

## Runners

```bash
python3 invictusforward-8-research/tools/run_invictus8_v5_quality_boost.py
python3 invictusforward-8-research/tools/run_invictus8_v8_risk_certified.py
```

## Validation

- Compile log harus berisi `0 errors`.
- Native MT5 `.htm` adalah source of truth.
- Python parsing hanya boleh merapikan hasil dari report native.
- Jangan mencampur hasil cent `XAUUSDc/USC` dengan proxy USD `XAUUSD/USD` tanpa label eksplisit.
