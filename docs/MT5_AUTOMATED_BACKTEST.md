# MT5 Automated Backtest on macOS via Wine

Panduan ini menjelaskan cara menjalankan backtest MetaTrader 5 secara programatik, tanpa klik manual di UI, dengan pola yang sama seperti yang dipakai di project ini.

## Gambaran Alur

1. Siapkan file EA `.mq5`.
2. Compile EA dengan `metaeditor64.exe`.
3. Copy hasil `.ex5` ke folder `MQL5/Experts/...`.
4. Buat file `.ini` untuk Strategy Tester.
5. Jalankan `terminal64.exe /config:...`.
6. Tunggu report `.htm` selesai dibuat.
7. Parse report untuk ambil metrik backtest.

## Environment yang Dipakai di Project Ini

- Workspace project:
  `/Users/naufalrachmandani/Hobby/MT5 XAU 15m`
- Wine prefix MT5:
  `/Users/naufalrachmandani/Library/Application Support/net.metaquotes.wine.metatrader5`
- Wine binary:
  `/Applications/MetaTrader 5.app/Contents/SharedSupport/wine/bin/wine64`
- MetaEditor:
  `C:\Program Files\MetaTrader 5\metaeditor64.exe`
- Terminal MT5:
  `C:\Program Files\MetaTrader 5\terminal64.exe`
- Build folder yang nyaman untuk compile:
  `/Users/naufalrachmandani/Library/Application Support/net.metaquotes.wine.metatrader5/drive_c/MT5Build`
- Folder Experts MT5:
  `/Users/naufalrachmandani/Library/Application Support/net.metaquotes.wine.metatrader5/drive_c/Program Files/MetaTrader 5/MQL5/Experts/Invictus`
- Folder report MT5:
  `/Users/naufalrachmandani/Library/Application Support/net.metaquotes.wine.metatrader5/drive_c/Program Files/MetaTrader 5/Reports`

## Struktur Minimal

Contoh file yang dibutuhkan:

- Source EA:
  `mt5/InvictusForward1M15_v5.mq5`
- Config backtest:
  `mt5/InvictusForward1M15_v5.backtest.ini`
- Script runner:
  `tools/iterate_v5.py`
  `tools/compare_versions_6m_100.py`

## Langkah 1: Compile EA

Contoh command:

```bash
WINEPREFIX="/Users/naufalrachmandani/Library/Application Support/net.metaquotes.wine.metatrader5" \
WINEDEBUG=-all \
"/Applications/MetaTrader 5.app/Contents/SharedSupport/wine/bin/wine64" \
"C:\\Program Files\\MetaTrader 5\\metaeditor64.exe" \
"/compile:C:\\MT5Build\\InvictusForward1M15_v5.mq5" \
"/log:C:\\MT5Build\\InvictusForward1M15_v5.compile.log"
```

Catatan penting:

- Di Wine, exit code compile bisa `1` walaupun compile sukses.
- Jangan hanya percaya exit code proses.
- Selalu baca file log compile dan cek ada string `0 errors`.

Contoh cek log:

```bash
python3 - <<'PY'
from pathlib import Path
log = Path("/Users/naufalrachmandani/Library/Application Support/net.metaquotes.wine.metatrader5/drive_c/MT5Build/InvictusForward1M15_v5.compile.log")
text = log.read_bytes().decode("utf-16le", errors="ignore")
print(text.splitlines()[-1])
print("ok" if "0 errors" in text else "compile failed")
PY
```

## Langkah 2: Copy `.ex5` ke Folder Experts

Contoh:

```bash
cp \
"/Users/naufalrachmandani/Library/Application Support/net.metaquotes.wine.metatrader5/drive_c/MT5Build/InvictusForward1M15_v5.ex5" \
"/Users/naufalrachmandani/Library/Application Support/net.metaquotes.wine.metatrader5/drive_c/Program Files/MetaTrader 5/MQL5/Experts/Invictus/InvictusForward1M15_v5.ex5"
```

## Langkah 3: Buat File Config Tester

Contoh isi `.ini`:

```ini
[Common]
Login=257385275
Server=Exness-MT5Real36
ProxyEnable=0
KeepPrivate=1
NewsEnable=1
CertInstall=1

[Experts]
AllowLiveTrading=0
AllowDllImport=0
Enabled=1
Account=0
Profile=0

[Tester]
Expert=Invictus\InvictusForward1M15_v5.ex5
Symbol=XAUUSDc
Period=M15
Login=257385275
Model=0
ExecutionMode=0
Optimization=0
FromDate=2025.01.01
ToDate=2026.04.15
ForwardMode=0
Report=\Reports\InvictusForward1M15_v5_XAUUSDc_M15_2025_2026
ReplaceReport=1
ShutdownTerminal=1
Deposit=100
Currency=USD
Leverage=1:100
UseLocal=1
UseRemote=0
UseCloud=0
Visual=0
```

Catatan:

- `ShutdownTerminal=1` penting agar terminal menutup sendiri setelah selesai.
- `Report=` sebaiknya unik per run supaya file tidak tertimpa tanpa sadar.
- `Visual=0` lebih stabil dan cepat untuk batch backtest.

## Langkah 4: Jalankan Backtest

Contoh command:

```bash
WINEPREFIX="/Users/naufalrachmandani/Library/Application Support/net.metaquotes.wine.metatrader5" \
WINEDEBUG=-all \
"/Applications/MetaTrader 5.app/Contents/SharedSupport/wine/bin/wine64" \
"C:\\Program Files\\MetaTrader 5\\terminal64.exe" \
"/config:C:\\MT5Build\\InvictusForward1M15_v5.backtest.ini"
```

Setelah command ini jalan, MT5 akan:

- membuka terminal
- memulai Strategy Tester
- menjalankan backtest
- menulis report HTML ke folder `Reports`
- menutup terminal jika `ShutdownTerminal=1`

## Langkah 5: Tunggu Sampai Report Jadi

Pola paling sederhana:

```python
import time
from pathlib import Path

report = Path("/Users/naufalrachmandani/Library/Application Support/net.metaquotes.wine.metatrader5/drive_c/Program Files/MetaTrader 5/Reports/InvictusForward1M15_v5_XAUUSDc_M15_2025_2026.htm")

for _ in range(180):
    if report.exists() and report.stat().st_size > 0:
        print("report ready")
        break
    time.sleep(2)
else:
    raise RuntimeError("report not generated")
```

## Langkah 6: Parse Report

Report MT5 default biasanya UTF-16LE. Jadi parsing sederhana bisa seperti ini:

```python
import re
from pathlib import Path

report = Path("/path/to/report.htm")
text = report.read_bytes().decode("utf-16le", errors="ignore")
plain = re.sub(r"<[^>]+>", " ", text).replace("\xa0", " ")
plain = re.sub(r"\s+", " ", plain)

def extract(label: str) -> str:
    m = re.search(re.escape(label) + r"\s*([^:]{1,90})", plain)
    if not m:
        raise RuntimeError(f"missing {label}")
    return m.group(1).strip()

print("Total Net Profit:", extract("Total Net Profit:"))
print("Profit Factor:", extract("Profit Factor:"))
print("Total Trades:", extract("Total Trades:"))
print("Equity Drawdown Maximal:", extract("Equity Drawdown Maximal:"))
```

## Langkah 7: Parse Tester Log untuk Diagnosis

Kalau EA menulis diagnostic line ke log, file tester log sangat berguna untuk tahu bottleneck entry.

Contoh path log:

`/Users/naufalrachmandani/Library/Application Support/net.metaquotes.wine.metatrader5/drive_c/Program Files/MetaTrader 5/Tester/logs/20260417.log`

Contoh baca 2 line terakhir untuk diagnosis:

```python
from pathlib import Path

log = Path("/Users/naufalrachmandani/Library/Application Support/net.metaquotes.wine.metatrader5/drive_c/Program Files/MetaTrader 5/Tester/logs/20260417.log")
text = log.read_bytes().decode("utf-16le", errors="ignore")

for prefix in ("IF1 diag trend:", "IF1 diag sideways:"):
    lines = [line for line in text.splitlines() if prefix in line]
    print(lines[-1] if lines else f"missing {prefix}")
```

Ini sangat membantu untuk melihat:

- berapa kali gagal di `bos`
- berapa kali gagal di `zone`
- berapa kali gagal di `score`
- berapa kali kena `dailyLoss`
- closed PnL per layer

## Masalah yang Sering Terjadi

### 1. Compile sukses tapi proses exit code `1`

Ini sering terjadi di Wine. Solusinya:

- jangan percaya exit code
- cek log compile
- validasi `0 errors`

### 2. `symbol not exist`

Biasanya simbol belum tersedia di broker/account aktif. Solusinya:

- buka MT5 manual sekali
- pastikan simbol ada di `Market Watch`
- gunakan nama simbol yang benar, misalnya di setup ini `XAUUSDc`, bukan `XAUUSD.s`

### 3. Report tidak muncul

Kemungkinan:

- terminal masih running
- config path salah
- EA path salah
- report name salah
- akun/symbol/testing context tidak valid

### 4. Backtest jalan tapi hasil `0 trades`

Biasanya bukan masalah MT5, tapi logika EA terlalu ketat atau filter entry tidak pernah lolos. Solusinya:

- tambahkan diagnostic counters di EA
- parse tester log
- cek layer mana yang memblokir entry

## Template Python Runner Sederhana

Kalau mau yang paling cepat diimplementasikan, struktur dasar runner seperti ini:

```python
from pathlib import Path
import os
import shutil
import subprocess
import time

ROOT = Path("/path/to/project")
WINEPREFIX = Path("/path/to/wineprefix")
WINE = "/Applications/MetaTrader 5.app/Contents/SharedSupport/wine/bin/wine64"
METAEDITOR = r"C:\Program Files\MetaTrader 5\metaeditor64.exe"
TERMINAL = r"C:\Program Files\MetaTrader 5\terminal64.exe"
MT5_BUILD = WINEPREFIX / "drive_c" / "MT5Build"
EXPERTS = WINEPREFIX / "drive_c" / "Program Files" / "MetaTrader 5" / "MQL5" / "Experts" / "Invictus"
REPORTS = WINEPREFIX / "drive_c" / "Program Files" / "MetaTrader 5" / "Reports"

env = os.environ.copy()
env["WINEPREFIX"] = str(WINEPREFIX)
env["WINEDEBUG"] = "-all"

source = ROOT / "mt5" / "MyEA.mq5"
build_src = MT5_BUILD / "MyEA.mq5"
compile_log = MT5_BUILD / "MyEA.compile.log"
ini = MT5_BUILD / "MyEA.backtest.ini"
report = REPORTS / "MyEA_report.htm"

shutil.copy2(source, build_src)

subprocess.run(
    [WINE, METAEDITOR, r"/compile:C:\MT5Build\MyEA.mq5", r"/log:C:\MT5Build\MyEA.compile.log"],
    env=env,
    check=False,
)

text = compile_log.read_bytes().decode("utf-16le", errors="ignore")
if "0 errors" not in text:
    raise RuntimeError("compile failed")

shutil.copy2(MT5_BUILD / "MyEA.ex5", EXPERTS / "MyEA.ex5")

ini.write_text("... isi config tester ...")

subprocess.run(
    [WINE, TERMINAL, r"/config:C:\MT5Build\MyEA.backtest.ini"],
    env=env,
    check=False,
)

for _ in range(180):
    if report.exists() and report.stat().st_size > 0:
        break
    time.sleep(2)
else:
    raise RuntimeError("report missing")
```

## Rekomendasi Praktis

- Buat `report` name unik untuk setiap iterasi.
- Simpan hasil JSON/Markdown summary per batch tuning.
- Tambahkan diagnostic counters di EA sejak awal.
- Batasi varian aktif supaya workflow tetap sederhana. Di project ini varian aktif yang dipertahankan sekarang hanya:
  `v1`, `v4`, dan `v5`.
- Jangan melakukan tuning buta hanya dari net profit; selalu lihat:
  `PF`, `recovery factor`, `equity drawdown`, `trade count`.

## File Referensi di Project Ini

- Runner 20 iterasi `v5`:
  [iterate_v5.py](/Users/naufalrachmandani/Hobby/MT5%20XAU%2015m/tools/iterate_v5.py)
- Runner compare versi aktif:
  [compare_versions_6m_100.py](/Users/naufalrachmandani/Hobby/MT5%20XAU%2015m/tools/compare_versions_6m_100.py)
- Runner walk-forward versi aktif:
  [walkforward_regime_matrix.py](/Users/naufalrachmandani/Hobby/MT5%20XAU%2015m/tools/walkforward_regime_matrix.py)
- Config backtest `v5`:
  [InvictusForward1M15_v5.backtest.ini](/Users/naufalrachmandani/Hobby/MT5%20XAU%2015m/mt5/InvictusForward1M15_v5.backtest.ini)
- EA `v5`:
  [InvictusForward1M15_v5.mq5](/Users/naufalrachmandani/Hobby/MT5%20XAU%2015m/mt5/InvictusForward1M15_v5.mq5)

Dengan setup ini, batch backtest bisa ditinggal jalan sendiri, lalu kamu tinggal baca report dan summary saat selesai.
