#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))

from analyze_mt5_report import iter_rows, parse_first_number, read_report  # noqa: E402


EXP_ROOT = Path(__file__).resolve().parent
SOURCE = EXP_ROOT / "final" / "Suis_BTC_M5_V2" / "source" / "Suis_BTC_M5_V2.mq5"
OUT_ROOT = EXP_ROOT / "mt5_optimization" / "suis_btc_m5_v2"
CONFIG_DIR = EXP_ROOT / "configs" / "suis_btc_m5_v2_mt5opt"

WINEPREFIX = Path.home() / "Library/Application Support/net.metaquotes.wine.metatrader5"
WINE = Path("/Applications/MetaTrader 5.app/Contents/SharedSupport/wine/bin/wine64")
METAEDITOR_WIN = r"C:\Program Files\MetaTrader 5\MetaEditor64.exe"
TERMINAL_WIN = r"C:\MT5PortableSuis\terminal64.exe"
PORTABLE = WINEPREFIX / "drive_c" / "MT5PortableSuis"
BUILD = WINEPREFIX / "drive_c" / "MT5Build"
BUILD_DIR = BUILD / "Suis_BTC_M5_V2_MT5Opt"
REPORTS = PORTABLE / "Reports"
TESTER_PROFILE = PORTABLE / "MQL5" / "Profiles" / "Tester"
OPT_EXPERT = PORTABLE / "MQL5" / "Experts" / "Suis_BTC_M5_V2_MT5Opt" / "Suis_BTC_M5_V2_MT5Opt.ex5"

ACCOUNT = {
    "name": "cent25",
    "login": "184000633",
    "server": "Exness-MT5Real25",
    "symbol": "BTCUSDc",
    "deposit": "1000",
    "currency": "USC",
    "leverage": "1:2000",
}

FROM_DATE = "2026.01.01"
TO_DATE = "2026.05.14"
PERIOD = "M5"
MODEL = 4
EXECUTION_MODE_MS = 20

BASELINE_V2 = {
    "net": 9667.00,
    "profit_pct": 966.70,
    "pf": 1.97,
    "trades": 192,
    "max_dd_any_pct": 29.28281391,
}

OPT_PARAMS = {
    "V10_RiskPercent": {"value": 15.5, "start": 14.5, "step": 0.5, "stop": 17.0, "type": "double"},
    "V11_MaxLotCap": {"value": 23.25, "start": 21.0, "step": 2.25, "stop": 27.75, "type": "double"},
    "V10_SellRR": {"value": 0.70, "start": 0.66, "step": 0.04, "stop": 0.78, "type": "double"},
    "V10_MinTradeScore": {"value": 38, "start": 36, "step": 2, "stop": 42, "type": "int"},
}


def win_path(path: Path) -> str:
    drive = WINEPREFIX / "drive_c"
    raw = str(path)
    if not raw.startswith(str(drive)):
        raise ValueError(f"path is outside drive_c: {path}")
    return "C:" + raw[len(str(drive)) :].replace("/", "\\")


def write_utf16(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"\xff\xfe" + text.encode("utf-16le"))


def patch_optimizer_source() -> Path:
    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)
    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    source = SOURCE.read_text(encoding="utf-8")
    source = re.sub(r'#property version\s+".*?"', '#property version   "2.10"', source)
    source = re.sub(
        r'#property description\s+".*?"',
        '#property description "Suis_BTC_M5_V2 MT5 optimizer temporary build"',
        source,
    )
    source = re.sub(
        r"// Suis BTC M5 V2 baked no-set build:.*",
        "// Suis BTC M5 V2 MT5 optimizer temporary build. Do not migrate this EX5.",
        source,
    )
    for name, spec in OPT_PARAMS.items():
        mql_type = "int" if spec["type"] == "int" else "double"
        pattern = re.compile(
            rf"^(\s*)const\s+{mql_type}\s+{re.escape(name)}\s*=\s*(.*?);",
            flags=re.M,
        )
        replacement = rf"\1input {mql_type} {name} = {spec['value']};"
        source, count = pattern.subn(replacement, source)
        if count != 1:
            raise RuntimeError(f"failed to expose optimizer input {name}: count={count}")
    path = BUILD_DIR / "Suis_BTC_M5_V2_MT5Opt.mq5"
    path.write_text(source, encoding="utf-8")
    return path


def compile_optimizer() -> None:
    source_path = patch_optimizer_source()
    log_path = BUILD_DIR / "compile.log"
    subprocess.run(
        [
            str(WINE),
            METAEDITOR_WIN,
            f"/compile:{win_path(source_path)}",
            f"/log:{win_path(log_path)}",
        ],
        env={**os.environ, "WINEPREFIX": str(WINEPREFIX)},
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        timeout=120,
    )
    log_text = log_path.read_bytes().decode("utf-16le", errors="ignore")
    if "Result: 0 errors, 0 warnings" not in log_text and " 0 error(s), 0 warning(s)" not in log_text:
        raise RuntimeError(f"compile failed\n{log_text}")
    ex5 = BUILD_DIR / "Suis_BTC_M5_V2_MT5Opt.ex5"
    if not ex5.exists():
        raise RuntimeError("missing optimizer EX5")
    OPT_EXPERT.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ex5, OPT_EXPERT)


def set_line(name: str, spec: dict[str, Any]) -> str:
    return f"{name}={spec['value']}||{spec['start']}||{spec['step']}||{spec['stop']}||Y"


def write_set() -> Path:
    lines = [
        "; Suis BTC M5 V2 MT5 built-in optimization",
        "; Temporary optimizer set. Final EX5 must be baked and rerun with ExpertParameters empty.",
    ]
    for name, spec in OPT_PARAMS.items():
        lines.append(set_line(name, spec))
    path = TESTER_PROFILE / "Suis_BTC_M5_V2_MT5Opt_risk_rr_score.set"
    write_utf16(path, "\r\n".join(lines) + "\r\n")
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, CONFIG_DIR / path.name)
    return path


def report_stem() -> str:
    return (
        f"SUIS_BTC_M5_V2_MT5OPT_risk_rr_score_{ACCOUNT['name']}_ytd2026_"
        f"{ACCOUNT['symbol']}_d{ACCOUNT['deposit']}{ACCOUNT['currency']}_{PERIOD}_model{MODEL}_"
        f"exec{EXECUTION_MODE_MS}ms_realticks_{FROM_DATE.replace('.', '')}_{TO_DATE.replace('.', '')}"
    )


def write_ini(set_path: Path) -> Path:
    stem = report_stem()
    lines = [
        "[Common]",
        f"Login={ACCOUNT['login']}",
        f"Server={ACCOUNT['server']}",
        "ProxyEnable=0",
        "KeepPrivate=1",
        "NewsEnable=0",
        "CertInstall=1",
        "",
        "[Events]",
        "Enable=0",
        "ConnectEnable=0",
        "DisconnectEnable=0",
        "Email NotifyEnable=0",
        "TimeoutEnable=0",
        "OkEnable=0",
        "NewsEnable=0",
        "Expert AdvisorEnable=0",
        "AlertEnable=0",
        "RequoteEnable=0",
        "Trailing StopEnable=0",
        "Testing FinishedEnable=0",
        "",
        "[Experts]",
        "AllowLiveTrading=0",
        "AllowDllImport=0",
        "Enabled=1",
        "Account=0",
        "Profile=0",
        "",
        "[Tester]",
        r"Expert=Suis_BTC_M5_V2_MT5Opt\Suis_BTC_M5_V2_MT5Opt.ex5",
        f"ExpertParameters={set_path.name}",
        f"Symbol={ACCOUNT['symbol']}",
        f"Period={PERIOD}",
        f"Login={ACCOUNT['login']}",
        f"Model={MODEL}",
        f"ExecutionMode={EXECUTION_MODE_MS}",
        "Optimization=1",
        "OptimizationCriterion=0",
        f"FromDate={FROM_DATE}",
        f"ToDate={TO_DATE}",
        "ForwardMode=0",
        rf"Report=\Reports\{stem}",
        "ReplaceReport=1",
        "ShutdownTerminal=1",
        f"Deposit={ACCOUNT['deposit']}",
        f"Currency={ACCOUNT['currency']}",
        f"Leverage={ACCOUNT['leverage']}",
        "UseLocal=1",
        "UseRemote=0",
        "UseCloud=0",
        "Visual=0",
        "",
    ]
    path = BUILD / f"{stem}.ini"
    write_utf16(path, "\r\n".join(lines))
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, CONFIG_DIR / path.name)
    return path


def xml_rows(path: Path) -> list[dict[str, Any]]:
    ns = {"ss": "urn:schemas-microsoft-com:office:spreadsheet"}
    root = ET.parse(path).getroot()
    table = root.find(".//ss:Worksheet/ss:Table", ns)
    if table is None:
        return []
    raw_rows: list[list[str]] = []
    for row in table.findall("ss:Row", ns):
        values = []
        for cell in row.findall("ss:Cell", ns):
            data = cell.find("ss:Data", ns)
            values.append(data.text if data is not None and data.text is not None else "")
        if values:
            raw_rows.append(values)
    if not raw_rows:
        return []
    headers = raw_rows[0]
    parsed = []
    for values in raw_rows[1:]:
        item = {headers[i]: values[i] if i < len(values) else "" for i in range(len(headers))}
        for key in ["Result", "Profit", "Expected Payoff", "Profit Factor", "Recovery Factor", "Sharpe Ratio", "Equity DD %", "Trades"]:
            if key in item:
                try:
                    item[key] = float(str(item[key]).replace(" ", ""))
                except ValueError:
                    item[key] = 0.0
        parsed.append(item)
    return parsed


def markdown(rows: list[dict[str, Any]], xml_path: Path) -> str:
    lines = [
        "# Suis BTC M5 V2 MT5 Optimization",
        "",
        f"Native MT5 built-in optimization over `{ACCOUNT['symbol']}`, `{PERIOD}`, `Model={MODEL}`, `ExecutionMode={EXECUTION_MODE_MS}`, `{FROM_DATE}-{TO_DATE}`.",
        f"Raw optimizer XML: `{xml_path.name}`.",
        "",
        f"Baseline V2: net `{BASELINE_V2['net']:.2f}`, PF `{BASELINE_V2['pf']:.2f}`, trades `{BASELINE_V2['trades']}`, Max DD Any `{BASELINE_V2['max_dd_any_pct']:.2f}%`.",
        "",
        "| Rank | Profit | PF | Eq DD % | Trades | Risk | LotCap | SellRR | MinScore | Verdict |",
        "| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for i, row in enumerate(rows[:30], start=1):
        profit = float(row.get("Profit", 0.0))
        pf = float(row.get("Profit Factor", 0.0))
        eq_dd = float(row.get("Equity DD %", 0.0))
        trades = int(float(row.get("Trades", 0.0)))
        verdict = "rerun" if profit > BASELINE_V2["net"] and eq_dd <= 30.0 and trades >= 150 and pf >= 1.5 else "watch"
        lines.append(
            f"| {i} | {profit:.2f} | {pf:.2f} | {eq_dd:.2f}% | {trades} | "
            f"{row.get('V10_RiskPercent', '')} | {row.get('V11_MaxLotCap', '')} | {row.get('V10_SellRR', '')} | {row.get('V10_MinTradeScore', '')} | {verdict} |"
        )
    return "\n".join(lines) + "\n"


def run_optimizer(timeout: int, force: bool) -> dict[str, Any]:
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    stem = report_stem()
    xml_path = OUT_ROOT / f"{stem}.xml"
    results_json = OUT_ROOT / "mt5opt_results.json"
    if xml_path.exists() and results_json.exists() and not force:
        return {"xml": str(xml_path), "rows": json.loads(results_json.read_text(encoding="utf-8")), "cached": True}
    compile_optimizer()
    set_path = write_set()
    ini_path = write_ini(set_path)
    for old in REPORTS.glob(f"{stem}*"):
        if old.is_file():
            old.unlink()
    started = time.time()
    timed_out = False
    try:
        subprocess.run(
            [str(WINE), TERMINAL_WIN, "/portable", rf"/config:{win_path(ini_path)}"],
            env={**os.environ, "WINEPREFIX": str(WINEPREFIX)},
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        timed_out = True
    copied = []
    for report in REPORTS.glob(f"{stem}*"):
        if report.is_file():
            target = OUT_ROOT / report.name
            shutil.copy2(report, target)
            copied.append(target)
    if not xml_path.exists():
        raise RuntimeError(f"optimizer xml missing; timed_out={timed_out}; copied={[str(p) for p in copied]}")
    rows = xml_rows(xml_path)
    rows.sort(key=lambda row: (float(row.get("Profit", 0.0)), float(row.get("Profit Factor", 0.0))), reverse=True)
    results_json.write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")
    (OUT_ROOT / "MT5_OPTIMIZATION_SUMMARY.md").write_text(markdown(rows, xml_path), encoding="utf-8")
    shutil.copy2(BUILD_DIR / "Suis_BTC_M5_V2_MT5Opt.mq5", OUT_ROOT / "Suis_BTC_M5_V2_MT5Opt.mq5")
    shutil.copy2(BUILD_DIR / "compile.log", OUT_ROOT / "compile.log")
    shutil.copy2(ini_path, OUT_ROOT / ini_path.name)
    shutil.copy2(set_path, OUT_ROOT / set_path.name)
    return {"xml": str(xml_path), "rows": rows, "timed_out": timed_out, "elapsed_sec": time.time() - started, "cached": False}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--timeout", type=int, default=1800)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    result = run_optimizer(args.timeout, args.force)
    rows = result["rows"]
    print(json.dumps({"xml": result["xml"], "rows": len(rows), "elapsed_sec": result.get("elapsed_sec"), "cached": result.get("cached")}, indent=2))
    for row in rows[:10]:
        print(
            json.dumps(
                {
                    "profit": row.get("Profit"),
                    "pf": row.get("Profit Factor"),
                    "eq_dd_pct": row.get("Equity DD %"),
                    "trades": row.get("Trades"),
                    "risk": row.get("V10_RiskPercent"),
                    "lotcap": row.get("V11_MaxLotCap"),
                    "sell_rr": row.get("V10_SellRR"),
                    "score": row.get("V10_MinTradeScore"),
                },
                ensure_ascii=False,
            )
        )


if __name__ == "__main__":
    main()
