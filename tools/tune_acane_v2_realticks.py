#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path

from analyze_mt5_report import iter_rows, parse_first_number, read_report


ROOT = Path(__file__).resolve().parents[1]
SRC_V2 = ROOT / "mt5" / "AcaneM1_v2.mq5"
SRC_V1_DEBUG = ROOT / "mt5" / "AcaneM1_v1_guarded_debug.mq5"
SRC_V1_DOWNLOAD = Path.home() / "Downloads" / "AcaneM1_v1_guarded.mq5"
OUT = ROOT / "build" / "acane_v2_realtick_tuning"

WINEPREFIX = Path.home() / "Library/Application Support/net.metaquotes.wine.metatrader5"
WINE = Path("/Applications/MetaTrader 5.app/Contents/SharedSupport/wine/bin/wine64")
METAEDITOR = r"C:\Program Files\MetaTrader 5\metaeditor64.exe"
TERMINAL = r"C:\Program Files\MetaTrader 5\terminal64.exe"
MT5_BUILD = WINEPREFIX / "drive_c" / "MT5Build"
EXPERTS_TUNE = WINEPREFIX / "drive_c" / "Program Files" / "MetaTrader 5" / "MQL5" / "Experts" / "AcaneTune"
REPORTS = WINEPREFIX / "drive_c" / "Program Files" / "MetaTrader 5" / "Reports"


@dataclass(frozen=True)
class Case:
    name: str
    from_date: str
    to_date: str


@dataclass(frozen=True)
class Variant:
    name: str
    source: Path = SRC_V2
    replacements: dict[str, object] = field(default_factory=dict)
    require_trend_regime: bool = False
    note: str = ""


def env() -> dict[str, str]:
    output = os.environ.copy()
    output["WINEPREFIX"] = str(WINEPREFIX)
    output["WINEDEBUG"] = "-all"
    return output


def win_build_path(filename: str) -> str:
    return rf"C:\MT5Build\{filename}"


def const_value(value: object) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, str):
        return json.dumps(value)
    if isinstance(value, float):
        return f"{value:.2f}"
    return str(value)


def replace_const(text: str, name: str, raw_value: object, optional: bool = False) -> str:
    value = const_value(raw_value)
    pattern = re.compile(rf"const\s+([A-Za-z0-9_]+)\s+{re.escape(name)}\s*=\s*[^;]+;")
    text, count = pattern.subn(lambda m: f"const {m.group(1):<6} {name} = {value};", text, count=1)
    if count != 1 and not optional:
        raise RuntimeError(f"failed to replace {name}")
    return text


def patch_source(variant: Variant, stem: str) -> str:
    text = variant.source.read_text()
    text = re.sub(r'#property version\s+"[^"]+"', '#property version   "2.10"', text, count=1)
    text = re.sub(r"// Acane M1.*", f"// {stem}: real-tick tuning candidate.", text, count=1)

    common = {
        "ACANE_LogEntries": False,
        "ACANE_LogStatus": False,
        "ACANE_DebugReasons": False,
        "ACANE_StatusEverySeconds": 300,
        "ACANE_DebugEverySeconds": 300,
    }
    replacements = {**common, **variant.replacements}
    for name, value in common.items():
        text = replace_const(text, name, value, optional=True)
    for name, value in variant.replacements.items():
        text = replace_const(text, name, value)

    if variant.require_trend_regime:
        text = text.replace(
            "bool buyReclaim = rates[0].low <= bandLower - atr * ACANE_MeanReversionTouchATR &&",
            "bool buyReclaim = regime == ACANE_BULL &&\n                        rates[0].low <= bandLower - atr * ACANE_MeanReversionTouchATR &&",
        )
        text = text.replace(
            "bool sellReject = rates[0].high >= bandUpper + atr * ACANE_MeanReversionTouchATR &&",
            "bool sellReject = regime == ACANE_BEAR &&\n                        rates[0].high >= bandUpper + atr * ACANE_MeanReversionTouchATR &&",
        )

    return text


def compile_variant(variant: Variant) -> str:
    stem = f"AcaneM1_v2t_{variant.name}"
    MT5_BUILD.mkdir(parents=True, exist_ok=True)
    EXPERTS_TUNE.mkdir(parents=True, exist_ok=True)
    source_path = MT5_BUILD / f"{stem}.mq5"
    source_path.write_text(patch_source(variant, stem))
    compile_log = MT5_BUILD / f"{stem}.compile.log"
    subprocess.run(
        [
            str(WINE),
            METAEDITOR,
            f"/compile:{win_build_path(source_path.name)}",
            f"/log:{win_build_path(compile_log.name)}",
        ],
        env=env(),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    log_text = compile_log.read_bytes().decode("utf-16le", errors="ignore") if compile_log.exists() else ""
    if "0 errors" not in log_text:
        raise RuntimeError(f"compile failed for {stem}: {log_text[-2000:]}")
    ex5 = MT5_BUILD / f"{stem}.ex5"
    if not ex5.exists():
        raise RuntimeError(f"missing compiled ex5 for {stem}")
    shutil.copy2(ex5, EXPERTS_TUNE / ex5.name)
    return stem


def report_stem(stem: str, case: Case) -> str:
    start = case.from_date.replace(".", "")
    end = case.to_date.replace(".", "")
    return f"{stem}_{case.name}_d29_delay50_real_ticks_{start}_{end}"


def write_ini(stem: str, case: Case) -> Path:
    name = report_stem(stem, case)
    config = f"""[Common]
Login=265874264
Server=Exness-MT5Real38
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
Expert=AcaneTune\\{stem}.ex5
Symbol=XAUUSD
Period=M1
Login=265874264
Model=4
ExecutionMode=50
Optimization=0
FromDate={case.from_date}
ToDate={case.to_date}
ForwardMode=0
Report=\\Reports\\{name}
ReplaceReport=1
ShutdownTerminal=1
Deposit=29
Currency=USD
Leverage=1:2000
UseLocal=1
UseRemote=0
UseCloud=0
Visual=0
"""
    ini = MT5_BUILD / f"{name}.ini"
    ini.write_bytes(b"\xff\xfe" + config.encode("utf-16le"))
    return ini


def cell(text: str, label: str, default: str = "") -> str:
    for row in iter_rows(text):
        for index, value in enumerate(row[:-1]):
            if value == label:
                return row[index + 1]
    return default


def pct_in(value: str) -> float:
    match = re.search(r"\(([-\d.]+)%\)", value)
    return float(match.group(1)) if match else 0.0


def dd_pct(value: str) -> float:
    return pct_in(value)


def parse_report(report: Path, variant: Variant, stem: str, case: Case) -> dict[str, object]:
    text = read_report(report)
    profit_trades = cell(text, "Profit Trades (% of total):")
    loss_trades = cell(text, "Loss Trades (% of total):")
    eqdd = cell(text, "Equity Drawdown Maximal:")
    baldd = cell(text, "Balance Drawdown Maximal:")
    return {
        "variant": variant.name,
        "stem": stem,
        "case": case.name,
        "from": case.from_date,
        "to": case.to_date,
        "note": variant.note,
        "net": parse_first_number(cell(text, "Total Net Profit:")),
        "pf": parse_first_number(cell(text, "Profit Factor:")),
        "trades": int(parse_first_number(cell(text, "Total Trades:"))),
        "wins": int(parse_first_number(profit_trades)),
        "losses": int(parse_first_number(loss_trades)),
        "win_rate": pct_in(profit_trades),
        "eqdd": eqdd,
        "eqdd_pct": dd_pct(eqdd),
        "baldd": baldd,
        "history_quality": cell(text, "History Quality:"),
        "largest_loss": parse_first_number(cell(text, "Largest loss trade:")),
        "avg_loss": parse_first_number(cell(text, "Average loss trade:")),
        "report": str(OUT / f"{report_stem(stem, case)}.htm"),
    }


def run_case(stem: str, variant: Variant, case: Case, timeout: int) -> dict[str, object]:
    name = report_stem(stem, case)
    report = REPORTS / f"{name}.htm"
    for old in REPORTS.glob(f"{name}*"):
        if old.is_file():
            old.unlink()
    ini = write_ini(stem, case)
    subprocess.run(
        [str(WINE), TERMINAL, f"/config:{win_build_path(ini.name)}"],
        env=env(),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
        timeout=timeout,
    )
    for _ in range(180):
        if report.exists() and report.stat().st_size > 0:
            break
        time.sleep(1)
    if not report.exists() or report.stat().st_size == 0:
        raise RuntimeError(f"report missing: {report}")
    OUT.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ini, OUT / ini.name)
    for artifact in REPORTS.glob(f"{name}*"):
        if artifact.is_file():
            shutil.copy2(artifact, OUT / artifact.name)
    return parse_report(report, variant, stem, case)


def write_outputs(results: list[dict[str, object]], filename: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{filename}.json").write_text(json.dumps(results, indent=2) + "\n")
    lines = [
        f"# {filename}",
        "",
        "Setup: `XAUUSD`, `M1`, deposit `$29`, leverage `1:2000`, `Model=4` real ticks, `ExecutionMode=50`.",
        "",
        "| Variant | Case | Net | PF | Trades | WR | Eq DD | History | Note |",
        "| --- | --- | ---: | ---: | ---: | ---: | --- | --- | --- |",
    ]
    for row in sorted(results, key=lambda r: (str(r["case"]), -float(r["net"]))):
        lines.append(
            "| {variant} | {case} | {net:.2f} | {pf:.2f} | {trades} | {win_rate:.2f}% | {eqdd} | {history_quality} | {note} |".format(
                **row
            )
        )
    (OUT / f"{filename}.md").write_text("\n".join(lines) + "\n")


VARIANTS = [
    Variant("v2_live", note="current deployed v2"),
    Variant("v1_old", source=SRC_V1_DEBUG, note="old guarded debug baseline"),
    Variant("v1_download", source=SRC_V1_DOWNLOAD, note="exact file from Downloads"),
    Variant(
        "trend_only",
        require_trend_regime=True,
        replacements={"ACANE_BlockEntryHours": ""},
        note="MRV only when M1/M5 trend agrees",
    ),
    Variant(
        "strict_mrv",
        replacements={
            "ACANE_MinScore": 74,
            "ACANE_StrongScore": 82,
            "ACANE_MeanReversionRSILow": 35.0,
            "ACANE_MeanReversionRSIHigh": 65.0,
            "ACANE_MeanReversionTouchATR": 0.18,
            "ACANE_MrvMaxImpulseATR": 0.75,
            "ACANE_MrvMaxEmaDistanceATR": 0.85,
            "ACANE_BlockEntryHours": "",
        },
        note="deeper BB/RSI rejection",
    ),
    Variant(
        "strict_trend",
        require_trend_regime=True,
        replacements={
            "ACANE_MinScore": 74,
            "ACANE_StrongScore": 82,
            "ACANE_MeanReversionRSILow": 35.0,
            "ACANE_MeanReversionRSIHigh": 65.0,
            "ACANE_MeanReversionTouchATR": 0.18,
            "ACANE_MrvMaxImpulseATR": 0.75,
            "ACANE_MrvMaxEmaDistanceATR": 0.85,
            "ACANE_BlockEntryHours": "",
        },
        note="strict MRV plus trend regime",
    ),
    Variant(
        "soft_exit",
        replacements={
            "ACANE_FastLossR": 0.55,
            "ACANE_BreakevenR": 0.34,
            "ACANE_TrailStartR": 0.70,
            "ACANE_MaxHoldSeconds": 180,
            "ACANE_BlockEntryHours": "",
        },
        note="less 6-second noise cutting",
    ),
    Variant(
        "strict_soft",
        replacements={
            "ACANE_MinScore": 74,
            "ACANE_StrongScore": 82,
            "ACANE_MeanReversionRSILow": 35.0,
            "ACANE_MeanReversionRSIHigh": 65.0,
            "ACANE_MeanReversionTouchATR": 0.18,
            "ACANE_MrvMaxImpulseATR": 0.75,
            "ACANE_MrvMaxEmaDistanceATR": 0.85,
            "ACANE_FastLossR": 0.55,
            "ACANE_BreakevenR": 0.34,
            "ACANE_TrailStartR": 0.70,
            "ACANE_MaxHoldSeconds": 180,
            "ACANE_BlockEntryHours": "",
        },
        note="strict signal with softer exits",
    ),
    Variant(
        "session_13_19",
        replacements={
            "ACANE_UseSessionFilter": True,
            "ACANE_SessionStartHour": 13,
            "ACANE_SessionEndHour": 19,
            "ACANE_BlockEntryHours": "",
        },
        note="avoid Asia/current leak hours",
    ),
    Variant(
        "session_soft",
        replacements={
            "ACANE_UseSessionFilter": True,
            "ACANE_SessionStartHour": 13,
            "ACANE_SessionEndHour": 19,
            "ACANE_BlockEntryHours": "",
            "ACANE_FastLossR": 0.55,
            "ACANE_BreakevenR": 0.34,
            "ACANE_TrailStartR": 0.70,
            "ACANE_MaxHoldSeconds": 180,
        },
        note="session filter plus softer exits",
    ),
    Variant(
        "tight_spread",
        replacements={
            "ACANE_MaxSpreadUsd": 0.35,
            "ACANE_BlockEntryHours": "",
        },
        note="avoid wide tick execution",
    ),
    Variant(
        "block_leaks",
        replacements={
            "ACANE_BlockEntryHours": "0,1,2,3,4,5,6,8,10,11,12,20,22,23",
        },
        note="block observed leak hours, leave 7/9/13-19/21",
    ),
    Variant(
        "extreme_only",
        replacements={
            "ACANE_MinScore": 82,
            "ACANE_StrongScore": 86,
            "ACANE_MeanReversionRSILow": 30.0,
            "ACANE_MeanReversionRSIHigh": 70.0,
            "ACANE_MeanReversionTouchATR": 0.28,
            "ACANE_BBandsDeviation": 2.25,
            "ACANE_BlockEntryHours": "",
        },
        note="only very stretched reversals",
    ),
    Variant(
        "extreme_rg_only",
        require_trend_regime=True,
        replacements={
            "ACANE_MinScore": 82,
            "ACANE_StrongScore": 86,
            "ACANE_MeanReversionRSILow": 30.0,
            "ACANE_MeanReversionRSIHigh": 70.0,
            "ACANE_MeanReversionTouchATR": 0.28,
            "ACANE_BBandsDeviation": 2.25,
            "ACANE_BlockEntryHours": "",
        },
        note="extreme MRV only when regime agrees",
    ),
    Variant(
        "extreme_buy_only",
        replacements={
            "ACANE_EnableSells": False,
            "ACANE_MinScore": 82,
            "ACANE_StrongScore": 86,
            "ACANE_MeanReversionRSILow": 30.0,
            "ACANE_MeanReversionRSIHigh": 70.0,
            "ACANE_MeanReversionTouchATR": 0.28,
            "ACANE_BBandsDeviation": 2.25,
            "ACANE_BlockEntryHours": "",
        },
        note="extreme MRV buys only",
    ),
    Variant(
        "extreme_session_9_21",
        replacements={
            "ACANE_MinScore": 82,
            "ACANE_StrongScore": 86,
            "ACANE_MeanReversionRSILow": 30.0,
            "ACANE_MeanReversionRSIHigh": 70.0,
            "ACANE_MeanReversionTouchATR": 0.28,
            "ACANE_BBandsDeviation": 2.25,
            "ACANE_UseSessionFilter": True,
            "ACANE_SessionStartHour": 9,
            "ACANE_SessionEndHour": 21,
            "ACANE_BlockEntryHours": "",
        },
        note="extreme MRV during server hours 9-20",
    ),
    Variant(
        "extreme_session_9_16",
        replacements={
            "ACANE_MinScore": 82,
            "ACANE_StrongScore": 86,
            "ACANE_MeanReversionRSILow": 30.0,
            "ACANE_MeanReversionRSIHigh": 70.0,
            "ACANE_MeanReversionTouchATR": 0.28,
            "ACANE_BBandsDeviation": 2.25,
            "ACANE_UseSessionFilter": True,
            "ACANE_SessionStartHour": 9,
            "ACANE_SessionEndHour": 16,
            "ACANE_BlockEntryHours": "",
        },
        note="extreme MRV during server hours 9-15",
    ),
    Variant(
        "extreme_block_bad_hours",
        replacements={
            "ACANE_MinScore": 82,
            "ACANE_StrongScore": 86,
            "ACANE_MeanReversionRSILow": 30.0,
            "ACANE_MeanReversionRSIHigh": 70.0,
            "ACANE_MeanReversionTouchATR": 0.28,
            "ACANE_BBandsDeviation": 2.25,
            "ACANE_BlockEntryHours": "1,2,3,16,17,23",
        },
        note="extreme MRV blocks audited leak hours",
    ),
    Variant(
        "mrv_block_bad_base",
        replacements={
            "ACANE_BlockEntryHours": "1,2,3,16,17,23",
        },
        note="current MRV with audited leak hours blocked",
    ),
    Variant(
        "mrv_block_bad_s70",
        replacements={
            "ACANE_MinScore": 70,
            "ACANE_StrongScore": 80,
            "ACANE_MeanReversionRSILow": 36.0,
            "ACANE_MeanReversionRSIHigh": 64.0,
            "ACANE_MeanReversionTouchATR": 0.14,
            "ACANE_BBandsDeviation": 2.05,
            "ACANE_BlockEntryHours": "1,2,3,16,17,23",
        },
        note="moderate MRV with leak hours blocked",
    ),
    Variant(
        "mrv_block_bad_s74",
        replacements={
            "ACANE_MinScore": 74,
            "ACANE_StrongScore": 82,
            "ACANE_MeanReversionRSILow": 35.0,
            "ACANE_MeanReversionRSIHigh": 65.0,
            "ACANE_MeanReversionTouchATR": 0.18,
            "ACANE_MrvMaxImpulseATR": 0.75,
            "ACANE_MrvMaxEmaDistanceATR": 0.85,
            "ACANE_BBandsDeviation": 2.10,
            "ACANE_BlockEntryHours": "1,2,3,16,17,23",
        },
        note="strict MRV with leak hours blocked",
    ),
    Variant(
        "mrv_block_bad_s78",
        replacements={
            "ACANE_MinScore": 78,
            "ACANE_StrongScore": 84,
            "ACANE_MeanReversionRSILow": 32.0,
            "ACANE_MeanReversionRSIHigh": 68.0,
            "ACANE_MeanReversionTouchATR": 0.22,
            "ACANE_MrvMaxImpulseATR": 0.90,
            "ACANE_MrvMaxEmaDistanceATR": 1.00,
            "ACANE_BBandsDeviation": 2.15,
            "ACANE_BlockEntryHours": "1,2,3,16,17,23",
        },
        note="between strict and extreme MRV with leak hours blocked",
    ),
    Variant(
        "mrv_block_bad_s82_touch18",
        replacements={
            "ACANE_MinScore": 82,
            "ACANE_StrongScore": 86,
            "ACANE_MeanReversionRSILow": 30.0,
            "ACANE_MeanReversionRSIHigh": 70.0,
            "ACANE_MeanReversionTouchATR": 0.18,
            "ACANE_BBandsDeviation": 2.15,
            "ACANE_BlockEntryHours": "1,2,3,16,17,23",
        },
        note="extreme score with less band overshoot requirement",
    ),
    Variant(
        "mrv_block_bad_rg",
        require_trend_regime=True,
        replacements={
            "ACANE_MinScore": 82,
            "ACANE_StrongScore": 86,
            "ACANE_MeanReversionRSILow": 30.0,
            "ACANE_MeanReversionRSIHigh": 70.0,
            "ACANE_MeanReversionTouchATR": 0.28,
            "ACANE_BBandsDeviation": 2.25,
            "ACANE_BlockEntryHours": "1,2,3,16,17,23",
        },
        note="extreme MRV, leak hours blocked, regime must agree",
    ),
    Variant(
        "mrv_block_bad_rg_s78",
        require_trend_regime=True,
        replacements={
            "ACANE_MinScore": 78,
            "ACANE_StrongScore": 84,
            "ACANE_MeanReversionRSILow": 32.0,
            "ACANE_MeanReversionRSIHigh": 68.0,
            "ACANE_MeanReversionTouchATR": 0.22,
            "ACANE_MrvMaxImpulseATR": 0.90,
            "ACANE_MrvMaxEmaDistanceATR": 1.00,
            "ACANE_BBandsDeviation": 2.15,
            "ACANE_BlockEntryHours": "1,2,3,16,17,23",
        },
        note="moderately strict MRV, leak hours blocked, regime must agree",
    ),
    Variant(
        "extreme_block_rollover",
        replacements={
            "ACANE_MinScore": 82,
            "ACANE_StrongScore": 86,
            "ACANE_MeanReversionRSILow": 30.0,
            "ACANE_MeanReversionRSIHigh": 70.0,
            "ACANE_MeanReversionTouchATR": 0.28,
            "ACANE_BBandsDeviation": 2.25,
            "ACANE_BlockEntryHours": "0,1,2,3,23",
        },
        note="extreme MRV avoids rollover/early leak hours",
    ),
    Variant(
        "extreme_hold",
        replacements={
            "ACANE_MinScore": 82,
            "ACANE_StrongScore": 86,
            "ACANE_MeanReversionRSILow": 30.0,
            "ACANE_MeanReversionRSIHigh": 70.0,
            "ACANE_MeanReversionTouchATR": 0.28,
            "ACANE_BBandsDeviation": 2.25,
            "ACANE_MeanReversionRR": 0.84,
            "ACANE_FastLossR": 0.65,
            "ACANE_BreakevenR": 0.42,
            "ACANE_TrailStartR": 0.78,
            "ACANE_MaxHoldSeconds": 240,
            "ACANE_BlockEntryHours": "",
        },
        note="extreme MRV with less tick-noise cutting",
    ),
    Variant(
        "extreme_tight_spread",
        replacements={
            "ACANE_MaxSpreadUsd": 0.35,
            "ACANE_MinScore": 82,
            "ACANE_StrongScore": 86,
            "ACANE_MeanReversionRSILow": 30.0,
            "ACANE_MeanReversionRSIHigh": 70.0,
            "ACANE_MeanReversionTouchATR": 0.28,
            "ACANE_BBandsDeviation": 2.25,
            "ACANE_BlockEntryHours": "",
        },
        note="extreme MRV with tighter spread filter",
    ),
    Variant(
        "v1_download_extreme",
        source=SRC_V1_DOWNLOAD,
        replacements={
            "ACANE_MaxPositions": 2,
            "ACANE_MaxSameSidePositions": 1,
            "ACANE_MinSecondsBetweenEntries": 60,
            "ACANE_DailyMaxLossPct": 10.0,
            "ACANE_MaxAccountDrawdownPct": 12.0,
            "ACANE_MaxOpenRiskPct": 8.0,
            "ACANE_MaxSameSideOpenRiskPct": 6.0,
            "ACANE_BasketLossStopPct": 6.0,
            "ACANE_FastLossCooldownAfter": 1,
            "ACANE_FastLossCooldownSeconds": 1800,
            "ACANE_MinScore": 82,
            "ACANE_StrongScore": 86,
            "ACANE_MeanReversionRSILow": 30.0,
            "ACANE_MeanReversionRSIHigh": 70.0,
            "ACANE_MeanReversionTouchATR": 0.28,
            "ACANE_BBandsDeviation": 2.25,
            "ACANE_BlockEntryHours": "",
        },
        note="Downloads v1 with v2 guard plus extreme MRV",
    ),
    Variant(
        "v1_download_extreme_session",
        source=SRC_V1_DOWNLOAD,
        replacements={
            "ACANE_MaxPositions": 2,
            "ACANE_MaxSameSidePositions": 1,
            "ACANE_MinSecondsBetweenEntries": 60,
            "ACANE_DailyMaxLossPct": 10.0,
            "ACANE_MaxAccountDrawdownPct": 12.0,
            "ACANE_MaxOpenRiskPct": 8.0,
            "ACANE_MaxSameSideOpenRiskPct": 6.0,
            "ACANE_BasketLossStopPct": 6.0,
            "ACANE_FastLossCooldownAfter": 1,
            "ACANE_FastLossCooldownSeconds": 1800,
            "ACANE_MinScore": 82,
            "ACANE_StrongScore": 86,
            "ACANE_MeanReversionRSILow": 30.0,
            "ACANE_MeanReversionRSIHigh": 70.0,
            "ACANE_MeanReversionTouchATR": 0.28,
            "ACANE_BBandsDeviation": 2.25,
            "ACANE_UseSessionFilter": True,
            "ACANE_SessionStartHour": 9,
            "ACANE_SessionEndHour": 21,
            "ACANE_BlockEntryHours": "",
        },
        note="Downloads v1 extreme during server hours 9-20",
    ),
    Variant(
        "mom_only",
        replacements={
            "ACANE_EnableMeanReversionEngine": False,
            "ACANE_EnableMomentumEngine": True,
            "ACANE_EnableReclaimEngine": False,
            "ACANE_EnableCompressionEngine": False,
            "ACANE_CoreRiskMultiplier": 0.12,
            "ACANE_WeakRiskMultiplier": 0.06,
            "ACANE_MinScore": 70,
            "ACANE_StrongScore": 80,
            "ACANE_TakeProfitR": 0.62,
            "ACANE_FastLossR": 0.55,
            "ACANE_BreakevenR": 0.34,
            "ACANE_TrailStartR": 0.70,
            "ACANE_MaxHoldSeconds": 180,
            "ACANE_BlockEntryHours": "",
        },
        note="trend-following breakouts only",
    ),
    Variant(
        "mom_strict",
        replacements={
            "ACANE_EnableMeanReversionEngine": False,
            "ACANE_EnableMomentumEngine": True,
            "ACANE_EnableReclaimEngine": False,
            "ACANE_EnableCompressionEngine": False,
            "ACANE_CoreRiskMultiplier": 0.12,
            "ACANE_WeakRiskMultiplier": 0.00,
            "ACANE_MinScore": 78,
            "ACANE_StrongScore": 82,
            "ACANE_TakeProfitR": 0.72,
            "ACANE_FastLossR": 0.65,
            "ACANE_BreakevenR": 0.42,
            "ACANE_TrailStartR": 0.78,
            "ACANE_MaxHoldSeconds": 240,
            "ACANE_BlockEntryHours": "",
        },
        note="strong-score momentum only",
    ),
    Variant(
        "reclaim_only",
        replacements={
            "ACANE_EnableMeanReversionEngine": False,
            "ACANE_EnableMomentumEngine": False,
            "ACANE_EnableReclaimEngine": True,
            "ACANE_EnableCompressionEngine": False,
            "ACANE_CoreRiskMultiplier": 0.12,
            "ACANE_WeakRiskMultiplier": 0.06,
            "ACANE_MinScore": 70,
            "ACANE_StrongScore": 80,
            "ACANE_TakeProfitR": 0.62,
            "ACANE_FastLossR": 0.55,
            "ACANE_BreakevenR": 0.34,
            "ACANE_TrailStartR": 0.70,
            "ACANE_MaxHoldSeconds": 180,
            "ACANE_BlockEntryHours": "",
        },
        note="EMA reclaim/reject continuation only",
    ),
    Variant(
        "comp_only",
        replacements={
            "ACANE_EnableMeanReversionEngine": False,
            "ACANE_EnableMomentumEngine": False,
            "ACANE_EnableReclaimEngine": False,
            "ACANE_EnableCompressionEngine": True,
            "ACANE_CoreRiskMultiplier": 0.12,
            "ACANE_WeakRiskMultiplier": 0.06,
            "ACANE_MinScore": 70,
            "ACANE_StrongScore": 80,
            "ACANE_TakeProfitR": 0.62,
            "ACANE_FastLossR": 0.55,
            "ACANE_BreakevenR": 0.34,
            "ACANE_TrailStartR": 0.70,
            "ACANE_MaxHoldSeconds": 180,
            "ACANE_BlockEntryHours": "",
        },
        note="compression breakout only",
    ),
    Variant(
        "trend_combo",
        replacements={
            "ACANE_EnableMeanReversionEngine": False,
            "ACANE_EnableMomentumEngine": True,
            "ACANE_EnableReclaimEngine": True,
            "ACANE_EnableCompressionEngine": True,
            "ACANE_CoreRiskMultiplier": 0.12,
            "ACANE_WeakRiskMultiplier": 0.04,
            "ACANE_MinScore": 74,
            "ACANE_StrongScore": 82,
            "ACANE_TakeProfitR": 0.68,
            "ACANE_FastLossR": 0.60,
            "ACANE_BreakevenR": 0.40,
            "ACANE_TrailStartR": 0.78,
            "ACANE_MaxHoldSeconds": 240,
            "ACANE_BlockEntryHours": "",
        },
        note="all trend engines, no MRV",
    ),
    Variant(
        "hybrid_extreme_mom",
        replacements={
            "ACANE_EnableMeanReversionEngine": True,
            "ACANE_EnableMomentumEngine": True,
            "ACANE_EnableReclaimEngine": False,
            "ACANE_EnableCompressionEngine": False,
            "ACANE_CoreRiskMultiplier": 0.12,
            "ACANE_WeakRiskMultiplier": 0.00,
            "ACANE_MinScore": 78,
            "ACANE_StrongScore": 84,
            "ACANE_MeanReversionRSILow": 30.0,
            "ACANE_MeanReversionRSIHigh": 70.0,
            "ACANE_MeanReversionTouchATR": 0.28,
            "ACANE_BBandsDeviation": 2.25,
            "ACANE_TakeProfitR": 0.72,
            "ACANE_FastLossR": 0.65,
            "ACANE_BreakevenR": 0.42,
            "ACANE_TrailStartR": 0.78,
            "ACANE_MaxHoldSeconds": 240,
            "ACANE_BlockEntryHours": "",
        },
        note="strong momentum plus extreme MRV",
    ),
    Variant(
        "mom_ny",
        replacements={
            "ACANE_EnableMeanReversionEngine": False,
            "ACANE_EnableMomentumEngine": True,
            "ACANE_EnableReclaimEngine": True,
            "ACANE_EnableCompressionEngine": False,
            "ACANE_CoreRiskMultiplier": 0.12,
            "ACANE_WeakRiskMultiplier": 0.00,
            "ACANE_MinScore": 76,
            "ACANE_StrongScore": 82,
            "ACANE_TakeProfitR": 0.72,
            "ACANE_FastLossR": 0.65,
            "ACANE_BreakevenR": 0.42,
            "ACANE_TrailStartR": 0.78,
            "ACANE_MaxHoldSeconds": 240,
            "ACANE_UseSessionFilter": True,
            "ACANE_SessionStartHour": 12,
            "ACANE_SessionEndHour": 20,
            "ACANE_BlockEntryHours": "",
        },
        note="trend engines during active London/NY hours",
    ),
    Variant(
        "trend_block_0_2",
        replacements={
            "ACANE_EnableMeanReversionEngine": False,
            "ACANE_EnableMomentumEngine": True,
            "ACANE_EnableReclaimEngine": True,
            "ACANE_EnableCompressionEngine": True,
            "ACANE_CoreRiskMultiplier": 0.12,
            "ACANE_WeakRiskMultiplier": 0.04,
            "ACANE_MinScore": 74,
            "ACANE_StrongScore": 82,
            "ACANE_TakeProfitR": 0.68,
            "ACANE_FastLossR": 0.60,
            "ACANE_BreakevenR": 0.40,
            "ACANE_TrailStartR": 0.78,
            "ACANE_MaxHoldSeconds": 240,
            "ACANE_BlockEntryHours": "0,1,2",
        },
        note="trend combo but block leak hours 0-2",
    ),
    Variant(
        "mom_strict_block0",
        replacements={
            "ACANE_EnableMeanReversionEngine": False,
            "ACANE_EnableMomentumEngine": True,
            "ACANE_EnableReclaimEngine": False,
            "ACANE_EnableCompressionEngine": False,
            "ACANE_CoreRiskMultiplier": 0.12,
            "ACANE_WeakRiskMultiplier": 0.00,
            "ACANE_MinScore": 78,
            "ACANE_StrongScore": 82,
            "ACANE_TakeProfitR": 0.72,
            "ACANE_FastLossR": 0.65,
            "ACANE_BreakevenR": 0.42,
            "ACANE_TrailStartR": 0.78,
            "ACANE_MaxHoldSeconds": 240,
            "ACANE_BlockEntryHours": "0,1,2",
        },
        note="strict momentum, no server hours 0-2",
    ),
    Variant(
        "trend_hour23",
        replacements={
            "ACANE_EnableMeanReversionEngine": False,
            "ACANE_EnableMomentumEngine": True,
            "ACANE_EnableReclaimEngine": True,
            "ACANE_EnableCompressionEngine": True,
            "ACANE_CoreRiskMultiplier": 0.12,
            "ACANE_WeakRiskMultiplier": 0.04,
            "ACANE_MinScore": 74,
            "ACANE_StrongScore": 82,
            "ACANE_TakeProfitR": 0.68,
            "ACANE_FastLossR": 0.60,
            "ACANE_BreakevenR": 0.40,
            "ACANE_TrailStartR": 0.78,
            "ACANE_MaxHoldSeconds": 240,
            "ACANE_UseSessionFilter": True,
            "ACANE_SessionStartHour": 23,
            "ACANE_SessionEndHour": 0,
            "ACANE_BlockEntryHours": "",
        },
        note="trend combo only server hour 23",
    ),
    Variant(
        "mom_hour23",
        replacements={
            "ACANE_EnableMeanReversionEngine": False,
            "ACANE_EnableMomentumEngine": True,
            "ACANE_EnableReclaimEngine": False,
            "ACANE_EnableCompressionEngine": False,
            "ACANE_CoreRiskMultiplier": 0.12,
            "ACANE_WeakRiskMultiplier": 0.00,
            "ACANE_MinScore": 78,
            "ACANE_StrongScore": 82,
            "ACANE_TakeProfitR": 0.72,
            "ACANE_FastLossR": 0.65,
            "ACANE_BreakevenR": 0.42,
            "ACANE_TrailStartR": 0.78,
            "ACANE_MaxHoldSeconds": 240,
            "ACANE_UseSessionFilter": True,
            "ACANE_SessionStartHour": 23,
            "ACANE_SessionEndHour": 0,
            "ACANE_BlockEntryHours": "",
        },
        note="strict momentum only server hour 23",
    ),
    Variant(
        "trend_hour23_s92",
        replacements={
            "ACANE_EnableMeanReversionEngine": False,
            "ACANE_EnableMomentumEngine": True,
            "ACANE_EnableReclaimEngine": True,
            "ACANE_EnableCompressionEngine": True,
            "ACANE_CoreRiskMultiplier": 0.12,
            "ACANE_WeakRiskMultiplier": 0.00,
            "ACANE_MinScore": 92,
            "ACANE_StrongScore": 92,
            "ACANE_TakeProfitR": 0.72,
            "ACANE_FastLossR": 0.65,
            "ACANE_BreakevenR": 0.42,
            "ACANE_TrailStartR": 0.78,
            "ACANE_MaxHoldSeconds": 240,
            "ACANE_UseSessionFilter": True,
            "ACANE_SessionStartHour": 23,
            "ACANE_SessionEndHour": 0,
            "ACANE_BlockEntryHours": "",
        },
        note="hour 23 trend, score >=92 only",
    ),
    Variant(
        "trend_hour23_s92_hold",
        replacements={
            "ACANE_EnableMeanReversionEngine": False,
            "ACANE_EnableMomentumEngine": True,
            "ACANE_EnableReclaimEngine": True,
            "ACANE_EnableCompressionEngine": True,
            "ACANE_CoreRiskMultiplier": 0.12,
            "ACANE_WeakRiskMultiplier": 0.00,
            "ACANE_MinScore": 92,
            "ACANE_StrongScore": 92,
            "ACANE_TakeProfitR": 0.84,
            "ACANE_FastLossR": 0.95,
            "ACANE_BreakevenR": 0.55,
            "ACANE_TrailStartR": 0.95,
            "ACANE_MaxHoldSeconds": 360,
            "ACANE_UseSessionFilter": True,
            "ACANE_SessionStartHour": 23,
            "ACANE_SessionEndHour": 0,
            "ACANE_BlockEntryHours": "",
        },
        note="hour 23 score >=92 with looser exits",
    ),
    Variant(
        "mom_hour23_s92",
        replacements={
            "ACANE_EnableMeanReversionEngine": False,
            "ACANE_EnableMomentumEngine": True,
            "ACANE_EnableReclaimEngine": False,
            "ACANE_EnableCompressionEngine": False,
            "ACANE_CoreRiskMultiplier": 0.12,
            "ACANE_WeakRiskMultiplier": 0.00,
            "ACANE_MinScore": 92,
            "ACANE_StrongScore": 92,
            "ACANE_TakeProfitR": 0.72,
            "ACANE_FastLossR": 0.65,
            "ACANE_BreakevenR": 0.42,
            "ACANE_TrailStartR": 0.78,
            "ACANE_MaxHoldSeconds": 240,
            "ACANE_UseSessionFilter": True,
            "ACANE_SessionStartHour": 23,
            "ACANE_SessionEndHour": 0,
            "ACANE_BlockEntryHours": "",
        },
        note="hour 23 momentum, score >=92 only",
    ),
]


CASES_QUICK = [
    Case("lastweek_20260501", "2026.05.01", "2026.05.09"),
    Case("ytd_2026", "2026.01.01", "2026.05.09"),
]

CASES_FULL = [
    Case("lastweek_20260501", "2026.05.01", "2026.05.09"),
    Case("ytd_2026", "2026.01.01", "2026.05.09"),
    Case("current_2025", "2025.01.01", "2026.05.09"),
]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", choices=["quick", "full"], default="quick")
    parser.add_argument("--variants", nargs="*", help="variant names to run")
    args = parser.parse_args()

    selected = [v for v in VARIANTS if not args.variants or v.name in set(args.variants)]
    if args.variants and len(selected) != len(args.variants):
        found = {v.name for v in selected}
        missing = [name for name in args.variants if name not in found]
        raise SystemExit(f"unknown variants: {missing}")

    cases = CASES_QUICK if args.stage == "quick" else CASES_FULL
    results: list[dict[str, object]] = []
    for variant in selected:
        print(f"compile {variant.name}", flush=True)
        stem = compile_variant(variant)
        for case in cases:
            print(f"run {variant.name} {case.name}", flush=True)
            result = run_case(stem, variant, case, timeout=1200)
            print(
                f"done {variant.name} {case.name} net={result['net']:.2f} pf={result['pf']:.2f} trades={result['trades']}",
                flush=True,
            )
            results.append(result)
            write_outputs(results, f"{args.stage}_results_partial")
    write_outputs(results, f"{args.stage}_results")
    print(OUT / f"{args.stage}_results.md")


if __name__ == "__main__":
    main()
