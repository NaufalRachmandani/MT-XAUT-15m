#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import time
import zipfile
from dataclasses import dataclass
from pathlib import Path

from analyze_mt5_report import parse_first_number, parse_report_metrics, read_report


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "mt5" / "AcaneM1_v1.mq5"
OUT = ROOT / "build" / "acane_m1_iteration"
PACKAGE = ROOT / "build" / "acane_live_package"

WINEPREFIX = Path.home() / "Library/Application Support/net.metaquotes.wine.metatrader5"
WINE = Path("/Applications/MetaTrader 5.app/Contents/SharedSupport/wine/bin/wine64")
METAEDITOR = r"C:\Program Files\MetaTrader 5\metaeditor64.exe"
TERMINAL = r"C:\Program Files\MetaTrader 5\terminal64.exe"
MT5_BUILD = WINEPREFIX / "drive_c" / "MT5Build"
EXPERTS = WINEPREFIX / "drive_c" / "Program Files" / "MetaTrader 5" / "MQL5" / "Experts" / "Acane"
REPORTS = WINEPREFIX / "drive_c" / "Program Files" / "MetaTrader 5" / "Reports"


@dataclass(frozen=True)
class Variant:
    name: str
    replacements: dict[str, object]
    note: str


def const_value(value: object) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, str):
        return json.dumps(value)
    if isinstance(value, float):
        return f"{value:.2f}"
    return str(value)


def patch_source(text: str, stem: str, replacements: dict[str, object]) -> str:
    text = re.sub(r'#property version\s+"[^"]+"', '#property version   "1.00"', text, count=1)
    text = text.replace("AcaneM1_v1", stem)
    for name, raw_value in replacements.items():
        value = const_value(raw_value)
        pattern = re.compile(rf"const\s+([A-Za-z0-9_]+)\s+{re.escape(name)}\s*=\s*[^;]+;")
        text, count = pattern.subn(lambda m: f"const {m.group(1):<6} {name} = {value};", text, count=1)
        if count != 1:
            raise RuntimeError(f"failed to replace {name}")
    return text


def env() -> dict[str, str]:
    output = os.environ.copy()
    output["WINEPREFIX"] = str(WINEPREFIX)
    output["WINEDEBUG"] = "-all"
    return output


def win_build_path(filename: str) -> str:
    return rf"C:\MT5Build\{filename}"


def compile_source(stem: str, source_text: str) -> Path:
    MT5_BUILD.mkdir(parents=True, exist_ok=True)
    EXPERTS.mkdir(parents=True, exist_ok=True)
    build_src = MT5_BUILD / f"{stem}.mq5"
    build_src.write_text(source_text)
    compile_log = MT5_BUILD / f"{stem}.compile.log"
    subprocess.run(
        [
            str(WINE),
            METAEDITOR,
            f"/compile:{win_build_path(stem + '.mq5')}",
            f"/log:{win_build_path(stem + '.compile.log')}",
        ],
        env=env(),
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    log_text = compile_log.read_bytes().decode("utf-16le", errors="ignore") if compile_log.exists() else ""
    if "0 errors" not in log_text:
        raise RuntimeError(f"compile failed for {stem}: {log_text[-1600:]}")
    ex5 = MT5_BUILD / f"{stem}.ex5"
    if not ex5.exists():
        raise RuntimeError(f"missing compiled ex5 for {stem}")
    target = EXPERTS / f"{stem}.ex5"
    shutil.copy2(ex5, target)
    return target


def write_tester_ini(stem: str, report_name: str, from_date: str, to_date: str, deposit: int, leverage: str) -> Path:
    ini = MT5_BUILD / f"{report_name}.ini"
    config = f"""[Common]
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
Expert=Acane\\{stem}.ex5
Symbol=XAUUSDc
Period=M1
Login=257385275
Model=0
ExecutionMode=0
Optimization=0
FromDate={from_date}
ToDate={to_date}
ForwardMode=0
Report=\\Reports\\{report_name}
ReplaceReport=1
ShutdownTerminal=1
Deposit={deposit}
Currency=USD
Leverage={leverage}
UseLocal=1
UseRemote=0
UseCloud=0
Visual=0
"""
    ini.write_bytes(b"\xff\xfe" + config.encode("utf-16le"))
    return ini


def dd_percent(value: str) -> float:
    match = re.search(r"\(([-\d.]+)%\)", value)
    return float(match.group(1)) if match else 0.0


def run_backtest(stem: str, variant: str, window: str, from_date: str, to_date: str, deposit: int, leverage: str, timeout: int) -> dict[str, object]:
    report_name = f"{stem}_{variant}_{window}_{from_date.replace('.', '')}_{to_date.replace('.', '')}"
    report = REPORTS / f"{report_name}.htm"
    if report.exists():
        report.unlink()
    ini = write_tester_ini(stem, report_name, from_date, to_date, deposit, leverage)
    subprocess.run(
        [str(WINE), TERMINAL, f"/config:{win_build_path(ini.name)}"],
        env=env(),
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        timeout=timeout,
    )
    for _ in range(90):
        if report.exists() and report.stat().st_size > 0:
            break
        time.sleep(1)
    if not report.exists() or report.stat().st_size == 0:
        raise RuntimeError(f"report missing: {report}")
    report_text = read_report(report)
    metrics = parse_report_metrics(report_text)
    plain = re.sub(r"<[^>]+>", " ", report_text).replace("\xa0", " ")
    plain = re.sub(r"\s+", " ", plain)
    bars_match = re.search(r"\bBars:\s*([\d ]+)", plain)
    period_match = re.search(r"\bPeriod:\s*([^I]{1,80})", plain)
    bars = int(bars_match.group(1).replace(" ", "")) if bars_match else 0
    period = period_match.group(1).strip() if period_match else ""
    if bars <= 0 or not period.startswith("M1"):
        raise RuntimeError(f"invalid MT5 report ({period=}, {bars=}): {report}")
    net = parse_first_number(metrics.get("Total Net Profit:", ""))
    trades = int(parse_first_number(metrics.get("Total Trades:", "")))
    pf = parse_first_number(metrics.get("Profit Factor:", ""))
    eqdd = metrics.get("Equity Drawdown Maximal:", "")
    baldd = metrics.get("Balance Drawdown Maximal:", "")
    return {
        "window": window,
        "from": from_date,
        "to": to_date,
        "report": str(report),
        "net": net,
        "net_pct": net / deposit * 100.0,
        "trades": trades,
        "trades_per_day": trades / max(1.0, days_between(from_date, to_date)),
        "profit_factor": pf,
        "equity_dd": eqdd,
        "equity_dd_pct": dd_percent(eqdd),
        "balance_dd": baldd,
        "balance_dd_pct": dd_percent(baldd),
        "metrics": metrics,
    }


def days_between(from_date: str, to_date: str) -> float:
    start = time.strptime(from_date, "%Y.%m.%d")
    end = time.strptime(to_date, "%Y.%m.%d")
    return max(1.0, (time.mktime(end) - time.mktime(start)) / 86400.0)


VARIANTS = [
    Variant("acane_base", {}, "baseline aggressive M1 micro scalper"),
    Variant(
        "acane_swarm",
        {
            "ACANE_MaxPositions": 30,
            "ACANE_MaxSameSidePositions": 22,
            "ACANE_MinSecondsBetweenEntries": 2,
            "ACANE_MaxHoldSeconds": 60,
            "ACANE_MicroCloseProfitSeconds": 6,
            "ACANE_CoreRiskMultiplier": 0.24,
            "ACANE_WeakRiskMultiplier": 0.08,
            "ACANE_TakeProfitR": 0.32,
            "ACANE_ScalpProfitUsd": 0.20,
            "ACANE_MinSLUsd": 0.75,
            "ACANE_MaxSLUsd": 2.60,
            "ACANE_ATRStopMult": 0.50,
            "ACANE_MinScore": 52,
        },
        "maximum frequency swarm with smaller per-position risk",
    ),
    Variant(
        "acane_hyper",
        {
            "ACANE_MaxPositions": 45,
            "ACANE_MaxSameSidePositions": 34,
            "ACANE_MinSecondsBetweenEntries": 1,
            "ACANE_MaxHoldSeconds": 45,
            "ACANE_MicroCloseProfitSeconds": 4,
            "ACANE_CoreRiskMultiplier": 0.18,
            "ACANE_WeakRiskMultiplier": 0.06,
            "ACANE_TakeProfitR": 0.24,
            "ACANE_ScalpProfitUsd": 0.14,
            "ACANE_MinSLUsd": 0.65,
            "ACANE_MaxSLUsd": 2.10,
            "ACANE_ATRStopMult": 0.44,
            "ACANE_MinScore": 47,
            "ACANE_MaxSpreadUsd": 1.20,
        },
        "very high turnover stress test",
    ),
    Variant(
        "acane_strong_scaled",
        {
            "ACANE_MaxPositions": 16,
            "ACANE_MaxSameSidePositions": 10,
            "ACANE_MinSecondsBetweenEntries": 4,
            "ACANE_CoreRiskMultiplier": 0.55,
            "ACANE_WeakRiskMultiplier": 0.00,
            "ACANE_MinScore": 70,
            "ACANE_TakeProfitR": 0.52,
            "ACANE_MaxHoldSeconds": 75,
        },
        "fewer but much larger high-score entries",
    ),
    Variant(
        "acane_loose_score",
        {
            "ACANE_MaxPositions": 34,
            "ACANE_MaxSameSidePositions": 26,
            "ACANE_MinSecondsBetweenEntries": 2,
            "ACANE_CoreRiskMultiplier": 0.28,
            "ACANE_WeakRiskMultiplier": 0.10,
            "ACANE_MinScore": 45,
            "ACANE_MinBodyRatio": 0.24,
            "ACANE_MinBreakATR": 0.00,
            "ACANE_StrongBreakATR": 0.02,
            "ACANE_TakeProfitR": 0.26,
            "ACANE_ScalpProfitUsd": 0.16,
            "ACANE_MaxHoldSeconds": 55,
        },
        "looser score gates for daily trade-count ceiling",
    ),
    Variant(
        "acane_fast_tp",
        {
            "ACANE_MaxPositions": 26,
            "ACANE_MaxSameSidePositions": 18,
            "ACANE_MinSecondsBetweenEntries": 2,
            "ACANE_CoreRiskMultiplier": 0.32,
            "ACANE_WeakRiskMultiplier": 0.10,
            "ACANE_TakeProfitR": 0.22,
            "ACANE_ScalpProfitUsd": 0.12,
            "ACANE_MicroCloseProfitSeconds": 3,
            "ACANE_MaxHoldSeconds": 36,
            "ACANE_FastLossR": 0.42,
            "ACANE_MinScore": 51,
        },
        "small targets and very fast forced exit",
    ),
    Variant(
        "acane_wider_hold",
        {
            "ACANE_MaxPositions": 24,
            "ACANE_MaxSameSidePositions": 16,
            "ACANE_MinSecondsBetweenEntries": 3,
            "ACANE_CoreRiskMultiplier": 0.34,
            "ACANE_WeakRiskMultiplier": 0.12,
            "ACANE_MinSLUsd": 1.20,
            "ACANE_MaxSLUsd": 4.60,
            "ACANE_ATRStopMult": 0.75,
            "ACANE_TakeProfitR": 0.42,
            "ACANE_MaxHoldSeconds": 150,
            "ACANE_FastLossR": 0.72,
            "ACANE_MinScore": 54,
        },
        "let M1 winners breathe slightly longer",
    ),
    Variant(
        "acane_buy_only",
        {
            "ACANE_EnableSells": False,
            "ACANE_MaxPositions": 28,
            "ACANE_MaxSameSidePositions": 24,
            "ACANE_MinSecondsBetweenEntries": 2,
            "ACANE_CoreRiskMultiplier": 0.34,
            "ACANE_WeakRiskMultiplier": 0.12,
            "ACANE_MinScore": 50,
            "ACANE_TakeProfitR": 0.28,
            "ACANE_ScalpProfitUsd": 0.16,
        },
        "bullish-only aggressive profile",
    ),
    Variant(
        "acane_sell_only",
        {
            "ACANE_EnableBuys": False,
            "ACANE_MaxPositions": 28,
            "ACANE_MaxSameSidePositions": 24,
            "ACANE_MinSecondsBetweenEntries": 2,
            "ACANE_CoreRiskMultiplier": 0.30,
            "ACANE_WeakRiskMultiplier": 0.10,
            "ACANE_MinScore": 50,
            "ACANE_TakeProfitR": 0.28,
            "ACANE_ScalpProfitUsd": 0.16,
        },
        "bearish-only aggressive profile",
    ),
    Variant(
        "acane_strict_spread",
        {
            "ACANE_MaxSpreadUsd": 0.75,
            "ACANE_MaxPositions": 24,
            "ACANE_MaxSameSidePositions": 18,
            "ACANE_MinSecondsBetweenEntries": 2,
            "ACANE_CoreRiskMultiplier": 0.34,
            "ACANE_WeakRiskMultiplier": 0.12,
            "ACANE_MinScore": 50,
            "ACANE_TakeProfitR": 0.30,
        },
        "frequency plus tighter transaction-cost filter",
    ),
    Variant(
        "acane_mom_rr08",
        {
            "ACANE_EnableReclaimEngine": False,
            "ACANE_EnableCompressionEngine": False,
            "ACANE_MaxPositions": 24,
            "ACANE_MaxSameSidePositions": 18,
            "ACANE_MinSecondsBetweenEntries": 2,
            "ACANE_CoreRiskMultiplier": 0.30,
            "ACANE_WeakRiskMultiplier": 0.08,
            "ACANE_MinScore": 58,
            "ACANE_TakeProfitR": 0.82,
            "ACANE_ScalpProfitUsd": 0.38,
            "ACANE_MicroCloseProfitSeconds": 999,
            "ACANE_MaxHoldSeconds": 90,
            "ACANE_FastLossR": 0.28,
            "ACANE_BreakevenR": 0.18,
            "ACANE_TrailStartR": 0.30,
            "ACANE_BlockEntryHours": "0,1,3,23",
        },
        "momentum-only, cut losses faster, block first leak-map hours",
    ),
    Variant(
        "acane_mom_rr10",
        {
            "ACANE_EnableReclaimEngine": False,
            "ACANE_EnableCompressionEngine": False,
            "ACANE_MaxPositions": 20,
            "ACANE_MaxSameSidePositions": 14,
            "ACANE_MinSecondsBetweenEntries": 3,
            "ACANE_CoreRiskMultiplier": 0.34,
            "ACANE_WeakRiskMultiplier": 0.06,
            "ACANE_MinScore": 62,
            "ACANE_TakeProfitR": 1.00,
            "ACANE_ScalpProfitUsd": 0.45,
            "ACANE_MicroCloseProfitSeconds": 999,
            "ACANE_MaxHoldSeconds": 120,
            "ACANE_FastLossR": 0.25,
            "ACANE_BreakevenR": 0.22,
            "ACANE_TrailStartR": 0.40,
            "ACANE_BlockEntryHours": "0,1,3,23",
        },
        "momentum-only RR 1.0 with fast loss cap",
    ),
    Variant(
        "acane_regime_rr08",
        {
            "ACANE_EnableReclaimEngine": False,
            "ACANE_EnableCompressionEngine": True,
            "ACANE_MaxPositions": 26,
            "ACANE_MaxSameSidePositions": 18,
            "ACANE_MinSecondsBetweenEntries": 2,
            "ACANE_CoreRiskMultiplier": 0.26,
            "ACANE_WeakRiskMultiplier": 0.00,
            "ACANE_MinScore": 64,
            "ACANE_TakeProfitR": 0.80,
            "ACANE_ScalpProfitUsd": 0.34,
            "ACANE_MicroCloseProfitSeconds": 999,
            "ACANE_MaxHoldSeconds": 100,
            "ACANE_FastLossR": 0.28,
            "ACANE_BlockEntryHours": "0,1,3,23",
        },
        "strong-score regime momentum plus compression only",
    ),
    Variant(
        "acane_rcl_hour2",
        {
            "ACANE_EnableMomentumEngine": False,
            "ACANE_EnableCompressionEngine": False,
            "ACANE_UseSessionFilter": True,
            "ACANE_SessionStartHour": 2,
            "ACANE_SessionEndHour": 3,
            "ACANE_MaxPositions": 18,
            "ACANE_MaxSameSidePositions": 14,
            "ACANE_MinSecondsBetweenEntries": 2,
            "ACANE_CoreRiskMultiplier": 0.24,
            "ACANE_WeakRiskMultiplier": 0.08,
            "ACANE_MinScore": 52,
            "ACANE_TakeProfitR": 0.70,
            "ACANE_ScalpProfitUsd": 0.28,
            "ACANE_MicroCloseProfitSeconds": 999,
            "ACANE_MaxHoldSeconds": 90,
            "ACANE_FastLossR": 0.30,
        },
        "isolates the only profitable RCL hour from first leak map",
    ),
    Variant(
        "acane_mom_open_rr07",
        {
            "ACANE_EnableReclaimEngine": False,
            "ACANE_EnableCompressionEngine": False,
            "ACANE_MaxPositions": 30,
            "ACANE_MaxSameSidePositions": 22,
            "ACANE_MinSecondsBetweenEntries": 2,
            "ACANE_CoreRiskMultiplier": 0.24,
            "ACANE_WeakRiskMultiplier": 0.08,
            "ACANE_MinScore": 54,
            "ACANE_TakeProfitR": 0.72,
            "ACANE_ScalpProfitUsd": 0.32,
            "ACANE_MicroCloseProfitSeconds": 999,
            "ACANE_MaxHoldSeconds": 80,
            "ACANE_FastLossR": 0.25,
            "ACANE_BreakevenR": 0.18,
        },
        "momentum-only open hours to check if hour block is overfit",
    ),
    Variant(
        "acane_mr_only",
        {
            "ACANE_EnableMomentumEngine": False,
            "ACANE_EnableReclaimEngine": False,
            "ACANE_EnableCompressionEngine": False,
            "ACANE_MaxPositions": 24,
            "ACANE_MaxSameSidePositions": 16,
            "ACANE_MinSecondsBetweenEntries": 3,
            "ACANE_CoreRiskMultiplier": 0.00,
            "ACANE_WeakRiskMultiplier": 0.00,
            "ACANE_MeanReversionRiskMultiplier": 0.18,
            "ACANE_MeanReversionRR": 0.72,
            "ACANE_MeanReversionRSILow": 38.0,
            "ACANE_MeanReversionRSIHigh": 62.0,
            "ACANE_MicroCloseProfitSeconds": 999,
            "ACANE_MaxHoldSeconds": 120,
            "ACANE_FastLossR": 0.30,
            "ACANE_BreakevenR": 0.22,
            "ACANE_TrailStartR": 0.40,
            "ACANE_MinScore": 56,
        },
        "Bollinger/RSI mean-reversion only",
    ),
    Variant(
        "acane_mr_swarm",
        {
            "ACANE_EnableMomentumEngine": False,
            "ACANE_EnableReclaimEngine": False,
            "ACANE_EnableCompressionEngine": False,
            "ACANE_MaxPositions": 36,
            "ACANE_MaxSameSidePositions": 24,
            "ACANE_MinSecondsBetweenEntries": 2,
            "ACANE_MeanReversionRiskMultiplier": 0.12,
            "ACANE_MeanReversionRR": 0.58,
            "ACANE_MeanReversionRSILow": 42.0,
            "ACANE_MeanReversionRSIHigh": 58.0,
            "ACANE_MicroCloseProfitSeconds": 999,
            "ACANE_MaxHoldSeconds": 75,
            "ACANE_FastLossR": 0.24,
            "ACANE_BreakevenR": 0.18,
            "ACANE_MinScore": 52,
        },
        "looser mean-reversion swarm for trade count",
    ),
    Variant(
        "acane_mr_trend_hybrid",
        {
            "ACANE_EnableMomentumEngine": True,
            "ACANE_EnableReclaimEngine": False,
            "ACANE_EnableCompressionEngine": False,
            "ACANE_MaxPositions": 30,
            "ACANE_MaxSameSidePositions": 20,
            "ACANE_MinSecondsBetweenEntries": 2,
            "ACANE_CoreRiskMultiplier": 0.22,
            "ACANE_WeakRiskMultiplier": 0.06,
            "ACANE_MeanReversionRiskMultiplier": 0.12,
            "ACANE_TakeProfitR": 0.78,
            "ACANE_MeanReversionRR": 0.62,
            "ACANE_MeanReversionRSILow": 40.0,
            "ACANE_MeanReversionRSIHigh": 60.0,
            "ACANE_MicroCloseProfitSeconds": 999,
            "ACANE_MaxHoldSeconds": 90,
            "ACANE_FastLossR": 0.24,
            "ACANE_MinScore": 52,
        },
        "trend momentum plus mean-reversion, no reclaim/compression leaks",
    ),
    Variant(
        "acane_mr_strict_spread",
        {
            "ACANE_EnableMomentumEngine": False,
            "ACANE_EnableReclaimEngine": False,
            "ACANE_EnableCompressionEngine": False,
            "ACANE_MaxSpreadUsd": 0.75,
            "ACANE_MaxPositions": 28,
            "ACANE_MaxSameSidePositions": 18,
            "ACANE_MinSecondsBetweenEntries": 2,
            "ACANE_MeanReversionRiskMultiplier": 0.16,
            "ACANE_MeanReversionRR": 0.72,
            "ACANE_MeanReversionRSILow": 40.0,
            "ACANE_MeanReversionRSIHigh": 60.0,
            "ACANE_MicroCloseProfitSeconds": 999,
            "ACANE_MaxHoldSeconds": 90,
            "ACANE_FastLossR": 0.24,
            "ACANE_MinScore": 54,
        },
        "mean-reversion with tighter spread filter",
    ),
    Variant(
        "acane_mr_hours_13_20",
        {
            "ACANE_EnableMomentumEngine": False,
            "ACANE_EnableReclaimEngine": False,
            "ACANE_EnableCompressionEngine": False,
            "ACANE_UseSessionFilter": True,
            "ACANE_SessionStartHour": 13,
            "ACANE_SessionEndHour": 20,
            "ACANE_MaxPositions": 30,
            "ACANE_MaxSameSidePositions": 20,
            "ACANE_MinSecondsBetweenEntries": 2,
            "ACANE_MeanReversionRiskMultiplier": 0.18,
            "ACANE_MeanReversionRR": 0.72,
            "ACANE_MeanReversionRSILow": 40.0,
            "ACANE_MeanReversionRSIHigh": 60.0,
            "ACANE_MicroCloseProfitSeconds": 999,
            "ACANE_MaxHoldSeconds": 95,
            "ACANE_FastLossR": 0.24,
            "ACANE_MinScore": 52,
        },
        "mean-reversion only in first profitable hour cluster from leak map",
    ),
    Variant(
        "acane_mr_hours_12_15",
        {
            "ACANE_EnableMomentumEngine": False,
            "ACANE_EnableReclaimEngine": False,
            "ACANE_EnableCompressionEngine": False,
            "ACANE_UseSessionFilter": True,
            "ACANE_SessionStartHour": 12,
            "ACANE_SessionEndHour": 15,
            "ACANE_MaxPositions": 30,
            "ACANE_MaxSameSidePositions": 20,
            "ACANE_MinSecondsBetweenEntries": 2,
            "ACANE_MeanReversionRiskMultiplier": 0.18,
            "ACANE_MeanReversionRR": 0.72,
            "ACANE_MeanReversionRSILow": 40.0,
            "ACANE_MeanReversionRSIHigh": 60.0,
            "ACANE_MicroCloseProfitSeconds": 999,
            "ACANE_MaxHoldSeconds": 95,
            "ACANE_FastLossR": 0.24,
            "ACANE_MinScore": 52,
        },
        "mean-reversion around noon/london-us overlap candidate",
    ),
    Variant(
        "acane_mr_hours_7_20",
        {
            "ACANE_EnableMomentumEngine": False,
            "ACANE_EnableReclaimEngine": False,
            "ACANE_EnableCompressionEngine": False,
            "ACANE_UseSessionFilter": True,
            "ACANE_SessionStartHour": 7,
            "ACANE_SessionEndHour": 20,
            "ACANE_BlockEntryHours": "9,11,12,18",
            "ACANE_MaxPositions": 30,
            "ACANE_MaxSameSidePositions": 20,
            "ACANE_MinSecondsBetweenEntries": 2,
            "ACANE_MeanReversionRiskMultiplier": 0.16,
            "ACANE_MeanReversionRR": 0.78,
            "ACANE_MeanReversionRSILow": 40.0,
            "ACANE_MeanReversionRSIHigh": 60.0,
            "ACANE_MicroCloseProfitSeconds": 999,
            "ACANE_MaxHoldSeconds": 110,
            "ACANE_FastLossR": 0.24,
            "ACANE_MinScore": 52,
        },
        "wider MR session but block worst MR hours",
    ),
    Variant(
        "acane_mr_hours_13_20_scaled",
        {
            "ACANE_EnableMomentumEngine": False,
            "ACANE_EnableReclaimEngine": False,
            "ACANE_EnableCompressionEngine": False,
            "ACANE_UseSessionFilter": True,
            "ACANE_SessionStartHour": 13,
            "ACANE_SessionEndHour": 20,
            "ACANE_MaxPositions": 36,
            "ACANE_MaxSameSidePositions": 24,
            "ACANE_MinSecondsBetweenEntries": 1,
            "ACANE_MeanReversionRiskMultiplier": 0.28,
            "ACANE_MeanReversionRR": 0.74,
            "ACANE_MeanReversionRSILow": 42.0,
            "ACANE_MeanReversionRSIHigh": 58.0,
            "ACANE_MicroCloseProfitSeconds": 999,
            "ACANE_MaxHoldSeconds": 90,
            "ACANE_FastLossR": 0.22,
            "ACANE_MinScore": 50,
        },
        "scaled version of profitable MR session candidate",
    ),
    Variant(
        "acane_mr_robust_hours",
        {
            "ACANE_EnableMomentumEngine": False,
            "ACANE_EnableReclaimEngine": False,
            "ACANE_EnableCompressionEngine": False,
            "ACANE_MaxPositions": 36,
            "ACANE_MaxSameSidePositions": 24,
            "ACANE_MinSecondsBetweenEntries": 2,
            "ACANE_MeanReversionRiskMultiplier": 0.12,
            "ACANE_MeanReversionRR": 0.58,
            "ACANE_MeanReversionRSILow": 42.0,
            "ACANE_MeanReversionRSIHigh": 58.0,
            "ACANE_MicroCloseProfitSeconds": 999,
            "ACANE_MaxHoldSeconds": 75,
            "ACANE_FastLossR": 0.24,
            "ACANE_BreakevenR": 0.18,
            "ACANE_MinScore": 52,
            "ACANE_BlockEntryHours": "0,2,3,4,6,7,8,9,12,16,18,19,20,21,23",
        },
        "only hours positive in both 2026 and 2025-current leak maps",
    ),
    Variant(
        "acane_regime_gate_2500",
        {
            "ACANE_EnableStructuralPriceGate": True,
            "ACANE_MinD1CloseForTrading": 2500.00,
        },
        "skip low-price D1 regime that caused 2024 Apr-Aug failures",
    ),
    Variant(
        "acane_regime_gate_2600",
        {
            "ACANE_EnableStructuralPriceGate": True,
            "ACANE_MinD1CloseForTrading": 2600.00,
        },
        "stricter structural D1 price gate",
    ),
    Variant(
        "acane_gate2500_account30",
        {
            "ACANE_EnableStructuralPriceGate": True,
            "ACANE_MinD1CloseForTrading": 2500.00,
            "ACANE_MaxAccountDrawdownPct": 30.00,
        },
        "structural gate plus account DD circuit at 30%",
    ),
    Variant(
        "acane_gate2500_daily15",
        {
            "ACANE_EnableStructuralPriceGate": True,
            "ACANE_MinD1CloseForTrading": 2500.00,
            "ACANE_DailyMaxLossPct": 15.00,
        },
        "structural gate plus tighter daily stop",
    ),
    Variant(
        "acane_gate2500_weekly20",
        {
            "ACANE_EnableStructuralPriceGate": True,
            "ACANE_MinD1CloseForTrading": 2500.00,
            "ACANE_EnableWeeklyGuard": True,
            "ACANE_WeeklyMaxLossPct": 20.00,
            "ACANE_WeeklyMaxGivebackPct": 25.00,
        },
        "structural gate plus weekly loss/giveback stop",
    ),
    Variant(
        "acane_gate2500_monthly25",
        {
            "ACANE_EnableStructuralPriceGate": True,
            "ACANE_MinD1CloseForTrading": 2500.00,
            "ACANE_EnableMonthlyGuard": True,
            "ACANE_MonthlyMaxLossPct": 25.00,
            "ACANE_MonthlyMaxGivebackPct": 25.00,
        },
        "structural gate plus monthly loss/giveback stop",
    ),
    Variant(
        "acane_gate2500_guard_stack",
        {
            "ACANE_EnableStructuralPriceGate": True,
            "ACANE_MinD1CloseForTrading": 2500.00,
            "ACANE_DailyMaxLossPct": 18.00,
            "ACANE_EnableWeeklyGuard": True,
            "ACANE_WeeklyMaxLossPct": 22.00,
            "ACANE_WeeklyMaxGivebackPct": 24.00,
            "ACANE_EnableMonthlyGuard": True,
            "ACANE_MonthlyMaxLossPct": 28.00,
            "ACANE_MonthlyMaxGivebackPct": 28.00,
            "ACANE_MaxAccountDrawdownPct": 35.00,
        },
        "stacked structural, daily, weekly, monthly, and account guards",
    ),
    Variant(
        "acane_gate2500_guard_hours",
        {
            "ACANE_EnableStructuralPriceGate": True,
            "ACANE_MinD1CloseForTrading": 2500.00,
            "ACANE_DailyMaxLossPct": 18.00,
            "ACANE_EnableWeeklyGuard": True,
            "ACANE_WeeklyMaxLossPct": 22.00,
            "ACANE_WeeklyMaxGivebackPct": 24.00,
            "ACANE_EnableMonthlyGuard": True,
            "ACANE_MonthlyMaxLossPct": 28.00,
            "ACANE_MonthlyMaxGivebackPct": 28.00,
            "ACANE_MaxAccountDrawdownPct": 35.00,
            "ACANE_BlockEntryHours": "8,23",
        },
        "guard stack plus recurring bad hours from 2026 Feb",
    ),
    Variant(
        "acane_gate2500_guard_stack30",
        {
            "ACANE_EnableStructuralPriceGate": True,
            "ACANE_MinD1CloseForTrading": 2500.00,
            "ACANE_DailyMaxLossPct": 16.00,
            "ACANE_EnableWeeklyGuard": True,
            "ACANE_WeeklyMaxLossPct": 18.00,
            "ACANE_WeeklyMaxGivebackPct": 20.00,
            "ACANE_EnableMonthlyGuard": True,
            "ACANE_MonthlyMaxLossPct": 24.00,
            "ACANE_MonthlyMaxGivebackPct": 24.00,
            "ACANE_MaxAccountDrawdownPct": 30.00,
        },
        "tighter stacked guards targeting sub-30% DD without early account stop",
    ),
    Variant(
        "acane_gate2500_guard_tight",
        {
            "ACANE_EnableStructuralPriceGate": True,
            "ACANE_MinD1CloseForTrading": 2500.00,
            "ACANE_DailyMaxLossPct": 12.00,
            "ACANE_EnableWeeklyGuard": True,
            "ACANE_WeeklyMaxLossPct": 15.00,
            "ACANE_WeeklyMaxGivebackPct": 18.00,
            "ACANE_EnableMonthlyGuard": True,
            "ACANE_MonthlyMaxLossPct": 20.00,
            "ACANE_MonthlyMaxGivebackPct": 20.00,
            "ACANE_MaxAccountDrawdownPct": 30.00,
        },
        "strict risk brakes for DD control stress test",
    ),
    Variant(
        "acane_gate2600_guard_stack30",
        {
            "ACANE_EnableStructuralPriceGate": True,
            "ACANE_MinD1CloseForTrading": 2600.00,
            "ACANE_DailyMaxLossPct": 16.00,
            "ACANE_EnableWeeklyGuard": True,
            "ACANE_WeeklyMaxLossPct": 18.00,
            "ACANE_WeeklyMaxGivebackPct": 20.00,
            "ACANE_EnableMonthlyGuard": True,
            "ACANE_MonthlyMaxLossPct": 24.00,
            "ACANE_MonthlyMaxGivebackPct": 24.00,
            "ACANE_MaxAccountDrawdownPct": 30.00,
        },
        "stricter D1 price gate plus sub-30 guard stack",
    ),
    Variant(
        "acane_gate2800_guard_stack30",
        {
            "ACANE_EnableStructuralPriceGate": True,
            "ACANE_MinD1CloseForTrading": 2800.00,
            "ACANE_DailyMaxLossPct": 16.00,
            "ACANE_EnableWeeklyGuard": True,
            "ACANE_WeeklyMaxLossPct": 18.00,
            "ACANE_WeeklyMaxGivebackPct": 20.00,
            "ACANE_EnableMonthlyGuard": True,
            "ACANE_MonthlyMaxLossPct": 24.00,
            "ACANE_MonthlyMaxGivebackPct": 24.00,
            "ACANE_MaxAccountDrawdownPct": 30.00,
        },
        "high-price-only D1 regime plus sub-30 guard stack",
    ),
    Variant(
        "acane_profit_stack_risk016",
        {
            "ACANE_EnableStructuralPriceGate": True,
            "ACANE_MinD1CloseForTrading": 2500.00,
            "ACANE_MeanReversionRiskMultiplier": 0.16,
            "ACANE_MaxPositions": 42,
            "ACANE_MaxSameSidePositions": 28,
            "ACANE_MinSecondsBetweenEntries": 1,
            "ACANE_DailyMaxLossPct": 22.00,
            "ACANE_EnableWeeklyGuard": True,
            "ACANE_WeeklyMaxLossPct": 28.00,
            "ACANE_WeeklyMaxGivebackPct": 32.00,
            "ACANE_EnableMonthlyGuard": True,
            "ACANE_MonthlyMaxLossPct": 38.00,
            "ACANE_MonthlyMaxGivebackPct": 38.00,
            "ACANE_MaxAccountDrawdownPct": 55.00,
        },
        "profit-focused guard stack with higher MR risk and looser circuit",
    ),
    Variant(
        "acane_profit_stack_risk020",
        {
            "ACANE_EnableStructuralPriceGate": True,
            "ACANE_MinD1CloseForTrading": 2500.00,
            "ACANE_MeanReversionRiskMultiplier": 0.20,
            "ACANE_MaxPositions": 48,
            "ACANE_MaxSameSidePositions": 32,
            "ACANE_MinSecondsBetweenEntries": 1,
            "ACANE_DailyMaxLossPct": 26.00,
            "ACANE_EnableWeeklyGuard": True,
            "ACANE_WeeklyMaxLossPct": 35.00,
            "ACANE_WeeklyMaxGivebackPct": 40.00,
            "ACANE_EnableMonthlyGuard": True,
            "ACANE_MonthlyMaxLossPct": 50.00,
            "ACANE_MonthlyMaxGivebackPct": 50.00,
            "ACANE_MaxAccountDrawdownPct": 70.00,
        },
        "more aggressive profit-first stack; DD allowed to expand",
    ),
    Variant(
        "acane_profit_loose_rsi",
        {
            "ACANE_EnableStructuralPriceGate": True,
            "ACANE_MinD1CloseForTrading": 2500.00,
            "ACANE_MeanReversionRiskMultiplier": 0.15,
            "ACANE_MeanReversionRSILow": 45.00,
            "ACANE_MeanReversionRSIHigh": 55.00,
            "ACANE_MaxPositions": 48,
            "ACANE_MaxSameSidePositions": 32,
            "ACANE_MinSecondsBetweenEntries": 1,
            "ACANE_DailyMaxLossPct": 24.00,
            "ACANE_EnableWeeklyGuard": True,
            "ACANE_WeeklyMaxLossPct": 32.00,
            "ACANE_WeeklyMaxGivebackPct": 38.00,
            "ACANE_EnableMonthlyGuard": True,
            "ACANE_MonthlyMaxLossPct": 45.00,
            "ACANE_MonthlyMaxGivebackPct": 45.00,
            "ACANE_MaxAccountDrawdownPct": 65.00,
        },
        "profit-first variant with looser RSI mean-reversion trigger",
    ),
    Variant(
        "acane_profit_rr072",
        {
            "ACANE_EnableStructuralPriceGate": True,
            "ACANE_MinD1CloseForTrading": 2500.00,
            "ACANE_MeanReversionRiskMultiplier": 0.16,
            "ACANE_MeanReversionRR": 0.72,
            "ACANE_MaxPositions": 42,
            "ACANE_MaxSameSidePositions": 28,
            "ACANE_MinSecondsBetweenEntries": 1,
            "ACANE_MaxHoldSeconds": 100,
            "ACANE_DailyMaxLossPct": 22.00,
            "ACANE_EnableWeeklyGuard": True,
            "ACANE_WeeklyMaxLossPct": 30.00,
            "ACANE_WeeklyMaxGivebackPct": 35.00,
            "ACANE_EnableMonthlyGuard": True,
            "ACANE_MonthlyMaxLossPct": 45.00,
            "ACANE_MonthlyMaxGivebackPct": 45.00,
            "ACANE_MaxAccountDrawdownPct": 65.00,
        },
        "higher RR target to improve average win while staying high frequency",
    ),
    Variant(
        "acane_profit_raw_scaled",
        {
            "ACANE_EnableStructuralPriceGate": True,
            "ACANE_MinD1CloseForTrading": 2500.00,
            "ACANE_MeanReversionRiskMultiplier": 0.18,
            "ACANE_MaxPositions": 54,
            "ACANE_MaxSameSidePositions": 36,
            "ACANE_MinSecondsBetweenEntries": 1,
            "ACANE_DailyMaxLossPct": 30.00,
            "ACANE_EnableWeeklyGuard": False,
            "ACANE_EnableMonthlyGuard": False,
            "ACANE_MaxAccountDrawdownPct": 80.00,
        },
        "raw profit scaling with only structural gate, daily guard, and loose circuit",
    ),
    Variant(
        "acane_profit_account30_risk014",
        {
            "ACANE_EnableStructuralPriceGate": True,
            "ACANE_MinD1CloseForTrading": 2500.00,
            "ACANE_MeanReversionRiskMultiplier": 0.14,
            "ACANE_MaxPositions": 42,
            "ACANE_MaxSameSidePositions": 28,
            "ACANE_MinSecondsBetweenEntries": 1,
            "ACANE_DailyMaxLossPct": 30.00,
            "ACANE_EnableWeeklyGuard": False,
            "ACANE_EnableMonthlyGuard": False,
            "ACANE_MaxAccountDrawdownPct": 30.00,
        },
        "profit champion family: account30 circuit plus slightly higher risk",
    ),
    Variant(
        "acane_profit_account30_risk016",
        {
            "ACANE_EnableStructuralPriceGate": True,
            "ACANE_MinD1CloseForTrading": 2500.00,
            "ACANE_MeanReversionRiskMultiplier": 0.16,
            "ACANE_MaxPositions": 48,
            "ACANE_MaxSameSidePositions": 32,
            "ACANE_MinSecondsBetweenEntries": 1,
            "ACANE_DailyMaxLossPct": 30.00,
            "ACANE_EnableWeeklyGuard": False,
            "ACANE_EnableMonthlyGuard": False,
            "ACANE_MaxAccountDrawdownPct": 30.00,
        },
        "account30 with stronger size/frequency",
    ),
    Variant(
        "acane_profit_account30_rr072",
        {
            "ACANE_EnableStructuralPriceGate": True,
            "ACANE_MinD1CloseForTrading": 2500.00,
            "ACANE_MeanReversionRiskMultiplier": 0.12,
            "ACANE_MeanReversionRR": 0.72,
            "ACANE_MaxHoldSeconds": 100,
            "ACANE_MaxPositions": 42,
            "ACANE_MaxSameSidePositions": 28,
            "ACANE_MinSecondsBetweenEntries": 1,
            "ACANE_DailyMaxLossPct": 30.00,
            "ACANE_EnableWeeklyGuard": False,
            "ACANE_EnableMonthlyGuard": False,
            "ACANE_MaxAccountDrawdownPct": 30.00,
        },
        "account30 plus higher RR target",
    ),
    Variant(
        "acane_profit_account40_risk014",
        {
            "ACANE_EnableStructuralPriceGate": True,
            "ACANE_MinD1CloseForTrading": 2500.00,
            "ACANE_MeanReversionRiskMultiplier": 0.14,
            "ACANE_MaxPositions": 42,
            "ACANE_MaxSameSidePositions": 28,
            "ACANE_MinSecondsBetweenEntries": 1,
            "ACANE_DailyMaxLossPct": 30.00,
            "ACANE_EnableWeeklyGuard": False,
            "ACANE_EnableMonthlyGuard": False,
            "ACANE_MaxAccountDrawdownPct": 40.00,
        },
        "looser account circuit to let compounding continue",
    ),
    Variant(
        "acane_profit_account45_rr072",
        {
            "ACANE_EnableStructuralPriceGate": True,
            "ACANE_MinD1CloseForTrading": 2500.00,
            "ACANE_MeanReversionRiskMultiplier": 0.14,
            "ACANE_MeanReversionRR": 0.72,
            "ACANE_MaxHoldSeconds": 100,
            "ACANE_MaxPositions": 48,
            "ACANE_MaxSameSidePositions": 32,
            "ACANE_MinSecondsBetweenEntries": 1,
            "ACANE_DailyMaxLossPct": 30.00,
            "ACANE_EnableWeeklyGuard": False,
            "ACANE_EnableMonthlyGuard": False,
            "ACANE_MaxAccountDrawdownPct": 45.00,
        },
        "looser account circuit plus higher RR and larger size",
    ),
    Variant(
        "acane_profit_monthly30_rr072",
        {
            "ACANE_EnableStructuralPriceGate": True,
            "ACANE_MinD1CloseForTrading": 2500.00,
            "ACANE_MeanReversionRiskMultiplier": 0.12,
            "ACANE_MeanReversionRR": 0.72,
            "ACANE_MaxHoldSeconds": 100,
            "ACANE_MaxPositions": 42,
            "ACANE_MaxSameSidePositions": 28,
            "ACANE_MinSecondsBetweenEntries": 1,
            "ACANE_DailyMaxLossPct": 30.00,
            "ACANE_EnableWeeklyGuard": False,
            "ACANE_EnableMonthlyGuard": True,
            "ACANE_MonthlyMaxLossPct": 30.00,
            "ACANE_MonthlyMaxGivebackPct": 30.00,
            "ACANE_EnableEquityCircuit": False,
        },
        "RR0.72 profit profile with monthly-reset 30% guard instead of permanent account stop",
    ),
    Variant(
        "acane_profit_monthly40_rr072",
        {
            "ACANE_EnableStructuralPriceGate": True,
            "ACANE_MinD1CloseForTrading": 2500.00,
            "ACANE_MeanReversionRiskMultiplier": 0.12,
            "ACANE_MeanReversionRR": 0.72,
            "ACANE_MaxHoldSeconds": 100,
            "ACANE_MaxPositions": 42,
            "ACANE_MaxSameSidePositions": 28,
            "ACANE_MinSecondsBetweenEntries": 1,
            "ACANE_DailyMaxLossPct": 30.00,
            "ACANE_EnableWeeklyGuard": False,
            "ACANE_EnableMonthlyGuard": True,
            "ACANE_MonthlyMaxLossPct": 40.00,
            "ACANE_MonthlyMaxGivebackPct": 45.00,
            "ACANE_EnableEquityCircuit": False,
        },
        "looser monthly-reset guard for max long-window profit",
    ),
    Variant(
        "acane_profit_monthly30_risk014_rr072",
        {
            "ACANE_EnableStructuralPriceGate": True,
            "ACANE_MinD1CloseForTrading": 2500.00,
            "ACANE_MeanReversionRiskMultiplier": 0.14,
            "ACANE_MeanReversionRR": 0.72,
            "ACANE_MaxHoldSeconds": 100,
            "ACANE_MaxPositions": 48,
            "ACANE_MaxSameSidePositions": 32,
            "ACANE_MinSecondsBetweenEntries": 1,
            "ACANE_DailyMaxLossPct": 30.00,
            "ACANE_EnableWeeklyGuard": False,
            "ACANE_EnableMonthlyGuard": True,
            "ACANE_MonthlyMaxLossPct": 30.00,
            "ACANE_MonthlyMaxGivebackPct": 30.00,
            "ACANE_EnableEquityCircuit": False,
        },
        "monthly-reset guard plus larger size",
    ),
    Variant(
        "acane_profit_account30_rr080",
        {
            "ACANE_EnableStructuralPriceGate": True,
            "ACANE_MinD1CloseForTrading": 2500.00,
            "ACANE_MeanReversionRiskMultiplier": 0.12,
            "ACANE_MeanReversionRR": 0.80,
            "ACANE_MaxHoldSeconds": 120,
            "ACANE_MaxPositions": 42,
            "ACANE_MaxSameSidePositions": 28,
            "ACANE_MinSecondsBetweenEntries": 1,
            "ACANE_DailyMaxLossPct": 30.00,
            "ACANE_EnableWeeklyGuard": False,
            "ACANE_EnableMonthlyGuard": False,
            "ACANE_MaxAccountDrawdownPct": 30.00,
        },
        "account30 champion family with RR 0.80",
    ),
    Variant(
        "acane_profit_account30_rr090",
        {
            "ACANE_EnableStructuralPriceGate": True,
            "ACANE_MinD1CloseForTrading": 2500.00,
            "ACANE_MeanReversionRiskMultiplier": 0.12,
            "ACANE_MeanReversionRR": 0.90,
            "ACANE_MaxHoldSeconds": 150,
            "ACANE_MaxPositions": 42,
            "ACANE_MaxSameSidePositions": 28,
            "ACANE_MinSecondsBetweenEntries": 1,
            "ACANE_DailyMaxLossPct": 30.00,
            "ACANE_EnableWeeklyGuard": False,
            "ACANE_EnableMonthlyGuard": False,
            "ACANE_MaxAccountDrawdownPct": 30.00,
        },
        "account30 champion family with RR 0.90",
    ),
    Variant(
        "acane_profit_account30_fastloss018",
        {
            "ACANE_EnableStructuralPriceGate": True,
            "ACANE_MinD1CloseForTrading": 2500.00,
            "ACANE_MeanReversionRiskMultiplier": 0.12,
            "ACANE_MeanReversionRR": 0.72,
            "ACANE_FastLossR": 0.18,
            "ACANE_MaxHoldSeconds": 100,
            "ACANE_MaxPositions": 42,
            "ACANE_MaxSameSidePositions": 28,
            "ACANE_MinSecondsBetweenEntries": 1,
            "ACANE_DailyMaxLossPct": 30.00,
            "ACANE_EnableWeeklyGuard": False,
            "ACANE_EnableMonthlyGuard": False,
            "ACANE_MaxAccountDrawdownPct": 30.00,
        },
        "account30 RR0.72 with faster cut-loss",
    ),
    Variant(
        "acane_profit_account30_hold150",
        {
            "ACANE_EnableStructuralPriceGate": True,
            "ACANE_MinD1CloseForTrading": 2500.00,
            "ACANE_MeanReversionRiskMultiplier": 0.12,
            "ACANE_MeanReversionRR": 0.72,
            "ACANE_MaxHoldSeconds": 150,
            "ACANE_MaxPositions": 42,
            "ACANE_MaxSameSidePositions": 28,
            "ACANE_MinSecondsBetweenEntries": 1,
            "ACANE_DailyMaxLossPct": 30.00,
            "ACANE_EnableWeeklyGuard": False,
            "ACANE_EnableMonthlyGuard": False,
            "ACANE_MaxAccountDrawdownPct": 30.00,
        },
        "account30 RR0.72 with longer hold",
    ),
    Variant(
        "acane_profit_account30_rsi44",
        {
            "ACANE_EnableStructuralPriceGate": True,
            "ACANE_MinD1CloseForTrading": 2500.00,
            "ACANE_MeanReversionRiskMultiplier": 0.12,
            "ACANE_MeanReversionRR": 0.72,
            "ACANE_MeanReversionRSILow": 44.00,
            "ACANE_MeanReversionRSIHigh": 56.00,
            "ACANE_MaxHoldSeconds": 100,
            "ACANE_MaxPositions": 42,
            "ACANE_MaxSameSidePositions": 28,
            "ACANE_MinSecondsBetweenEntries": 1,
            "ACANE_DailyMaxLossPct": 30.00,
            "ACANE_EnableWeeklyGuard": False,
            "ACANE_EnableMonthlyGuard": False,
            "ACANE_MaxAccountDrawdownPct": 30.00,
        },
        "account30 RR0.72 with looser RSI trigger",
    ),
    Variant(
        "acane_profit_account30_rsi40",
        {
            "ACANE_EnableStructuralPriceGate": True,
            "ACANE_MinD1CloseForTrading": 2500.00,
            "ACANE_MeanReversionRiskMultiplier": 0.12,
            "ACANE_MeanReversionRR": 0.72,
            "ACANE_MeanReversionRSILow": 40.00,
            "ACANE_MeanReversionRSIHigh": 60.00,
            "ACANE_MaxHoldSeconds": 100,
            "ACANE_MaxPositions": 42,
            "ACANE_MaxSameSidePositions": 28,
            "ACANE_MinSecondsBetweenEntries": 1,
            "ACANE_DailyMaxLossPct": 30.00,
            "ACANE_EnableWeeklyGuard": False,
            "ACANE_EnableMonthlyGuard": False,
            "ACANE_MaxAccountDrawdownPct": 30.00,
        },
        "account30 RR0.72 with stricter RSI trigger",
    ),
    Variant(
        "acane_profit_account30_bb18",
        {
            "ACANE_EnableStructuralPriceGate": True,
            "ACANE_MinD1CloseForTrading": 2500.00,
            "ACANE_BBandsDeviation": 1.80,
            "ACANE_MeanReversionRiskMultiplier": 0.12,
            "ACANE_MeanReversionRR": 0.72,
            "ACANE_MaxHoldSeconds": 100,
            "ACANE_MaxPositions": 42,
            "ACANE_MaxSameSidePositions": 28,
            "ACANE_MinSecondsBetweenEntries": 1,
            "ACANE_DailyMaxLossPct": 30.00,
            "ACANE_EnableWeeklyGuard": False,
            "ACANE_EnableMonthlyGuard": False,
            "ACANE_MaxAccountDrawdownPct": 30.00,
        },
        "account30 RR0.72 with tighter Bollinger band",
    ),
    Variant(
        "acane_profit_account30_bb22",
        {
            "ACANE_EnableStructuralPriceGate": True,
            "ACANE_MinD1CloseForTrading": 2500.00,
            "ACANE_BBandsDeviation": 2.20,
            "ACANE_MeanReversionRiskMultiplier": 0.12,
            "ACANE_MeanReversionRR": 0.72,
            "ACANE_MaxHoldSeconds": 100,
            "ACANE_MaxPositions": 42,
            "ACANE_MaxSameSidePositions": 28,
            "ACANE_MinSecondsBetweenEntries": 1,
            "ACANE_DailyMaxLossPct": 30.00,
            "ACANE_EnableWeeklyGuard": False,
            "ACANE_EnableMonthlyGuard": False,
            "ACANE_MaxAccountDrawdownPct": 30.00,
        },
        "account30 RR0.72 with wider Bollinger band",
    ),
    Variant(
        "acane_profit_account30_nocooldown",
        {
            "ACANE_EnableStructuralPriceGate": True,
            "ACANE_MinD1CloseForTrading": 2500.00,
            "ACANE_MeanReversionRiskMultiplier": 0.12,
            "ACANE_MeanReversionRR": 0.72,
            "ACANE_MaxHoldSeconds": 100,
            "ACANE_MaxPositions": 54,
            "ACANE_MaxSameSidePositions": 36,
            "ACANE_MinSecondsBetweenEntries": 0,
            "ACANE_DailyMaxLossPct": 30.00,
            "ACANE_EnableWeeklyGuard": False,
            "ACANE_EnableMonthlyGuard": False,
            "ACANE_MaxAccountDrawdownPct": 30.00,
        },
        "account30 RR0.72 with no entry cooldown and higher position cap",
    ),
]


def score_result(result: dict[str, object]) -> float:
    net_pct = float(result["net_pct"])
    trades = float(result["trades"])
    eqdd = float(result["equity_dd_pct"])
    if trades < 50:
        return net_pct - 20000.0
    if net_pct <= 0:
        return net_pct - eqdd * 100.0
    return net_pct + min(trades, 4000.0) * 2.0 - eqdd * 120.0


def run_iteration(args: argparse.Namespace) -> dict[str, object]:
    OUT.mkdir(parents=True, exist_ok=True)
    source_text = SOURCE.read_text()
    results: list[dict[str, object]] = []

    windows = [("quick", args.from_date, args.to_date)]
    variants = [variant for variant in VARIANTS if not args.filter or re.search(args.filter, variant.name)]
    for variant in variants:
        stem = f"AcaneM1_v1_{variant.name}"
        print(f"==> compile {variant.name}")
        patched = patch_source(source_text, stem, variant.replacements)
        compile_source(stem, patched)
        try:
            row = {
                "variant": variant.name,
                "note": variant.note,
                "replacements": variant.replacements,
                "runs": [],
            }
            for window, from_date, to_date in windows:
                print(f"    backtest {variant.name} {window} {from_date}-{to_date}")
                run = run_backtest(stem, variant.name, window, from_date, to_date, args.deposit, args.leverage, args.timeout)
                row["runs"].append(run)
            row["score"] = score_result(row["runs"][0])
            results.append(row)
        except Exception as exc:
            results.append(
                {
                    "variant": variant.name,
                    "note": variant.note,
                    "replacements": variant.replacements,
                    "error": str(exc),
                    "runs": [],
                    "score": -1e12,
                }
            )

    results.sort(key=lambda row: float(row.get("score", -1e12)), reverse=True)
    payload = {
        "from": args.from_date,
        "to": args.to_date,
        "deposit": args.deposit,
        "leverage": args.leverage,
        "results": results,
    }
    (OUT / "results.json").write_text(json.dumps(payload, indent=2))
    write_summary(payload)
    return payload


def write_summary(payload: dict[str, object]) -> None:
    lines = [
        "# Acane M1 Iteration",
        "",
        f"Window: `{payload['from']}` to `{payload['to']}`, deposit `{payload['deposit']}`, leverage `{payload['leverage']}`.",
        "",
        "| Rank | Variant | Net % | Trades | Trades/day | PF | EqDD | Note |",
        "| ---: | --- | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for rank, row in enumerate(payload["results"], 1):
        runs = row.get("runs", [])
        if not runs:
            lines.append(f"| {rank} | `{row['variant']}` | ERR | ERR | ERR | ERR | ERR | {row.get('error', '')} |")
            continue
        run = runs[0]
        lines.append(
            f"| {rank} | `{row['variant']}` | {run['net_pct']:.2f}% | {run['trades']} | "
            f"{run['trades_per_day']:.1f} | {run['profit_factor']:.2f} | {run['equity_dd_pct']:.2f}% | {row['note']} |"
        )
    (OUT / "summary.md").write_text("\n".join(lines) + "\n")


def package_current() -> None:
    stem = "AcaneM1_v1"
    ex5 = compile_source(stem, SOURCE.read_text())
    package_experts = PACKAGE / "MQL5" / "Experts" / "Acane"
    if PACKAGE.exists():
        shutil.rmtree(PACKAGE)
    package_experts.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ex5, package_experts / ex5.name)
    install = PACKAGE / "INSTALL_VPS.md"
    install.write_text(
        "# Acane Live Package\n\n"
        "Copy `MQL5/Experts/Acane/AcaneM1_v1.ex5` ke folder data MetaTrader 5 di VPS.\n\n"
        "Setup chart:\n"
        "- Symbol: `XAUUSDc`\n"
        "- Timeframe: `M1`\n"
        "- Attach EA: `AcaneM1_v1`\n"
        "- Algo Trading: ON\n"
        "- Tidak perlu preset `.set`; default sudah dikunci di source.\n\n"
        "Catatan risiko: profile ini agresif dan memakai daily loss guard 15% + account circuit 15%. "
        "Forward test kecil tetap wajib sebelum scale-up.\n"
    )
    zip_path = ROOT / "build" / "acane_live_package.zip"
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in PACKAGE.rglob("*"):
            archive.write(path, path.relative_to(PACKAGE.parent))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--from-date", default="2026.04.01")
    parser.add_argument("--to-date", default="2026.05.07")
    parser.add_argument("--deposit", type=int, default=100)
    parser.add_argument("--leverage", default="100")
    parser.add_argument("--timeout", type=int, default=600)
    parser.add_argument("--filter", default="")
    parser.add_argument("--package", action="store_true")
    args = parser.parse_args()
    if args.package:
        package_current()
        return
    run_iteration(args)


if __name__ == "__main__":
    main()
