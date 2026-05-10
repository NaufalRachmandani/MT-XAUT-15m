#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from xml.etree import ElementTree

from analyze_mt5_report import iter_rows, parse_first_number, read_report


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "mt5" / "AcaneM1_v1.mq5"
OUT = ROOT / "build" / "acane_v1_mt5_optimization"

WINEPREFIX = Path.home() / "Library/Application Support/net.metaquotes.wine.metatrader5"
WINE = Path("/Applications/MetaTrader 5.app/Contents/SharedSupport/wine/bin/wine64")
METAEDITOR = r"C:\Program Files\MetaTrader 5\metaeditor64.exe"
TERMINAL = r"C:\Program Files\MetaTrader 5\terminal64.exe"
MT5_BUILD = WINEPREFIX / "drive_c" / "MT5Build"
MT5_ROOT = WINEPREFIX / "drive_c" / "Program Files" / "MetaTrader 5"
REPORTS = MT5_ROOT / "Reports"
EXPERTS = MT5_ROOT / "MQL5" / "Experts"
TESTER_PROFILES = MT5_ROOT / "MQL5" / "Profiles" / "Tester"

ACCOUNT = 265874264
SERVER = "Exness-MT5Real38"
SYMBOL = "XAUUSD"
PERIOD = "M1"
MODEL_REAL_TICKS = 4
BASE_DEPOSIT = 100
BASE_LEVERAGE = "1:2000"


@dataclass(frozen=True)
class BacktestCase:
    name: str
    from_date: str
    to_date: str
    deposit: int = BASE_DEPOSIT
    leverage: str = BASE_LEVERAGE
    delay_ms: int = 100
    model: int = MODEL_REAL_TICKS


def env() -> dict[str, str]:
    output = os.environ.copy()
    output["WINEPREFIX"] = str(WINEPREFIX)
    output["WINEDEBUG"] = "-all"
    return output


def win_build_path(filename: str) -> str:
    return rf"C:\MT5Build\{filename}"


def write_utf16(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"\xff\xfe" + text.encode("utf-16le"))


def compile_source() -> Path:
    if not SOURCE.exists():
        raise RuntimeError(f"missing source: {SOURCE}")
    MT5_BUILD.mkdir(parents=True, exist_ok=True)
    shutil.copy2(SOURCE, MT5_BUILD / SOURCE.name)
    compile_log = MT5_BUILD / "AcaneM1_v1.compile.log"
    subprocess.run(
        [str(WINE), METAEDITOR, f"/compile:{win_build_path(SOURCE.name)}", f"/log:{win_build_path(compile_log.name)}"],
        env=env(),
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        timeout=120,
    )
    text = compile_log.read_bytes().decode("utf-16le", errors="ignore") if compile_log.exists() else ""
    if "0 errors" not in text:
        raise RuntimeError(f"compile failed:\n{text[-3000:]}")
    ex5 = MT5_BUILD / "AcaneM1_v1.ex5"
    if not ex5.exists():
        raise RuntimeError(f"compiled ex5 missing: {ex5}")
    return ex5


def copy_lab_expert(ex5: Path) -> None:
    lab = EXPERTS / "AcaneLab"
    lab.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ex5, lab / "AcaneM1_v1.ex5")


def package_live_expert(ex5: Path) -> None:
    target = EXPERTS / "Acane"
    target.mkdir(parents=True, exist_ok=True)
    for path in target.glob("AcaneM1_*.ex5"):
        path.unlink()
    shutil.copy2(ex5, target / "AcaneM1_v1.ex5")


def set_line(name: str, value: object, start: object | None = None, step: object | None = None, stop: object | None = None, enabled: bool = False) -> str:
    if isinstance(value, str):
        return f"{name}={value}"
    if isinstance(value, bool):
        value_s = str(value).lower()
        start = value_s if start is None else str(start).lower()
        step = 0 if step is None else step
        stop = value_s if stop is None else str(stop).lower()
    else:
        value_s = str(value)
        start = value if start is None else start
        step = 0 if step is None else step
        stop = value if stop is None else stop
    flag = "Y" if enabled else "N"
    return f"{name}={value_s}||{start}||{step}||{stop}||{flag}"


def default_inputs() -> dict[str, object]:
    return {
        "AC_Magic": 2026051001,
        "AC_RiskPercent": 2.0,
        "AC_CoreRiskMultiplier": 1.0,
        "AC_WeakRiskMultiplier": 0.45,
        "AC_MaxLotCap": 0.06,
        "AC_MaxPositions": 3,
        "AC_MaxSameSidePositions": 2,
        "AC_MinBarsBetweenEntries": 1,
        "AC_BlockOppositeDirection": True,
        "AC_MaxSpreadUsd": 0.85,
        "AC_DeviationPoints": 80,
        "AC_EnableBuys": True,
        "AC_EnableSells": True,
        "AC_EnableDailyGuard": True,
        "AC_DailyMaxLossPct": 5.0,
        "AC_DailyMaxLossUsd": 5.0,
        "AC_CloseOnDailyStop": True,
        "AC_EnableEquityCircuit": True,
        "AC_MaxEquityDrawdownPct": 19.0,
        "AC_CloseOnCircuitStop": True,
        "AC_MaxOpenRiskPct": 12.0,
        "AC_BasketLossStopPct": 10.0,
        "AC_LossCooldownBars": 8,
        "AC_UseSessionFilter": True,
        "AC_SessionStartHour": 4,
        "AC_SessionEndHour": 15,
        "AC_BlockEntryHours": "",
        "AC_HourPreset": 8,
        "AC_EnableStructuralPriceGate": True,
        "AC_MinD1CloseForTrading": 2500.0,
        "AC_UseH1TrendGuard": True,
        "AC_H1Fast": 18,
        "AC_H1Slow": 54,
        "AC_EMAFast": 9,
        "AC_EMASlow": 34,
        "AC_M5Fast": 12,
        "AC_M5Slow": 36,
        "AC_M15Fast": 12,
        "AC_M15Slow": 36,
        "AC_ATRPeriod": 14,
        "AC_RSIPeriod": 9,
        "AC_ADXPeriod": 14,
        "AC_BBandsPeriod": 20,
        "AC_BBandsDeviation": 2.0,
        "AC_EnableTrendPullback": False,
        "AC_EnableImpulseContinuation": True,
        "AC_EnableCompressionBreakout": True,
        "AC_EnableMeanReversion": True,
        "AC_ImpulseLookback": 6,
        "AC_ImpulseMinBreakATR": 0.06,
        "AC_BreakLookback": 12,
        "AC_CompressionLookback": 8,
        "AC_MinATRUsd": 0.22,
        "AC_MaxATRUsd": 6.0,
        "AC_MinBodyRatio": 0.32,
        "AC_StrongBodyRatio": 0.52,
        "AC_MinBreakATR": 0.08,
        "AC_StrongBreakATR": 0.20,
        "AC_CompressionMaxATR": 1.55,
        "AC_PullbackTouchATR": 0.30,
        "AC_MaxEmaDistanceATR": 1.45,
        "AC_TrendADXMin": 16.0,
        "AC_SidewaysADXMax": 18.0,
        "AC_StrongADX": 25.0,
        "AC_RequirePullbackMomentum": True,
        "AC_MinScore": 70,
        "AC_StrongScore": 100,
        "AC_MinSLUsd": 0.65,
        "AC_MaxSLUsd": 2.00,
        "AC_ATRStopMult": 0.70,
        "AC_StopBufferATR": 0.12,
        "AC_TrendRR": 1.15,
        "AC_ImpulseRR": 0.95,
        "AC_BreakoutRR": 1.35,
        "AC_MeanReversionRR": 0.82,
        "AC_MeanReversionRSILow": 31.0,
        "AC_MeanReversionRSIHigh": 69.0,
        "AC_MeanReversionTouchATR": 0.14,
        "AC_BreakevenR": 0.50,
        "AC_BreakevenLockUsd": 0.05,
        "AC_TrailStartR": 0.80,
        "AC_TrailATR": 0.45,
        "AC_MaxHoldBars": 14,
        "AC_WeakMaxHoldBars": 8,
        "AC_CloseOnRegimeFlip": False,
        "AC_TesterMinTrades": 250,
        "AC_TesterMaxDDPct": 20.0,
        "AC_LogEntries": False,
        "AC_LogStatus": False,
        "AC_StatusEveryBars": 30,
    }


OPT_RANGES: dict[str, tuple[object, object, object]] = {
    "AC_RiskPercent": (1.0, 0.5, 4.0),
    "AC_CoreRiskMultiplier": (0.65, 0.15, 1.25),
    "AC_WeakRiskMultiplier": (0.15, 0.15, 0.75),
    "AC_MaxLotCap": (0.02, 0.01, 0.12),
    "AC_MaxPositions": (1, 1, 5),
    "AC_MaxSameSidePositions": (1, 1, 3),
    "AC_MinBarsBetweenEntries": (0, 1, 4),
    "AC_MaxSpreadUsd": (0.45, 0.10, 1.05),
    "AC_DailyMaxLossPct": (3.0, 1.0, 10.0),
    "AC_DailyMaxLossUsd": (3.0, 1.0, 12.0),
    "AC_MaxOpenRiskPct": (6.0, 2.0, 16.0),
    "AC_BasketLossStopPct": (5.0, 1.5, 13.0),
    "AC_LossCooldownBars": (3, 3, 18),
    "AC_UseSessionFilter": (False, 0, True),
    "AC_SessionStartHour": (0, 2, 14),
    "AC_SessionEndHour": (12, 2, 23),
    "AC_HourPreset": (0, 1, 9),
    "AC_EMAFast": (5, 2, 15),
    "AC_EMASlow": (21, 5, 61),
    "AC_M5Fast": (8, 2, 20),
    "AC_M5Slow": (24, 6, 60),
    "AC_M15Fast": (8, 2, 20),
    "AC_M15Slow": (24, 6, 72),
    "AC_UseH1TrendGuard": (False, 0, True),
    "AC_H1Fast": (12, 3, 30),
    "AC_H1Slow": (36, 6, 96),
    "AC_RSIPeriod": (6, 1, 14),
    "AC_ADXPeriod": (8, 2, 20),
    "AC_EnableTrendPullback": (False, 0, True),
    "AC_EnableImpulseContinuation": (False, 0, True),
    "AC_ImpulseLookback": (3, 1, 12),
    "AC_ImpulseMinBreakATR": (0.00, 0.03, 0.18),
    "AC_BreakLookback": (5, 2, 20),
    "AC_CompressionLookback": (4, 2, 14),
    "AC_MinATRUsd": (0.16, 0.04, 0.40),
    "AC_MaxATRUsd": (3.0, 0.75, 8.0),
    "AC_MinBodyRatio": (0.20, 0.06, 0.56),
    "AC_MinBreakATR": (0.02, 0.04, 0.22),
    "AC_StrongBreakATR": (0.08, 0.04, 0.34),
    "AC_CompressionMaxATR": (0.80, 0.20, 2.40),
    "AC_PullbackTouchATR": (0.10, 0.08, 0.58),
    "AC_MaxEmaDistanceATR": (0.75, 0.25, 2.25),
    "AC_TrendADXMin": (10.0, 2.0, 26.0),
    "AC_SidewaysADXMax": (12.0, 2.0, 28.0),
    "AC_RequirePullbackMomentum": (False, 0, True),
    "AC_MinScore": (58, 4, 86),
    "AC_StrongScore": (78, 4, 102),
    "AC_MinSLUsd": (0.55, 0.15, 1.30),
    "AC_MaxSLUsd": (1.30, 0.30, 4.00),
    "AC_ATRStopMult": (0.45, 0.15, 1.50),
    "AC_TrendRR": (0.75, 0.15, 1.80),
    "AC_ImpulseRR": (0.55, 0.15, 1.45),
    "AC_BreakoutRR": (0.85, 0.20, 2.20),
    "AC_MeanReversionRR": (0.45, 0.10, 1.20),
    "AC_MeanReversionRSILow": (22.0, 3.0, 42.0),
    "AC_MeanReversionRSIHigh": (58.0, 3.0, 78.0),
    "AC_MeanReversionTouchATR": (0.00, 0.06, 0.36),
    "AC_BreakevenR": (0.30, 0.10, 1.00),
    "AC_TrailStartR": (0.55, 0.15, 1.45),
    "AC_TrailATR": (0.25, 0.10, 0.95),
    "AC_MaxHoldBars": (6, 4, 32),
    "AC_WeakMaxHoldBars": (3, 3, 20),
}


def write_set(name: str, optimize: bool, overrides: dict[str, object] | None = None) -> Path:
    values = default_inputs()
    if overrides:
        values.update(overrides)
    lines = [
        "; AcaneM1_v1 generated set",
        "; Base: XAUUSD M1, account 265874264, Exness-MT5Real38, deposit 100 USD, leverage 1:2000, Model=4, delay100",
    ]
    for key, value in values.items():
        if optimize and key in OPT_RANGES:
            start, step, stop = OPT_RANGES[key]
            lines.append(set_line(key, value, start, step, stop, True))
        else:
            lines.append(set_line(key, value, enabled=False))
    path = TESTER_PROFILES / name
    write_utf16(path, "\r\n".join(lines) + "\r\n")
    shutil.copy2(path, OUT / name)
    return path


def report_stem(prefix: str, case: BacktestCase) -> str:
    start = case.from_date.replace(".", "")
    end = case.to_date.replace(".", "")
    return f"{prefix}_{case.name}_d{case.deposit}_lev{case.leverage.replace(':', '')}_delay{case.delay_ms}_model{case.model}_{start}_{end}"


def tester_common() -> str:
    return f"""[Common]
Login={ACCOUNT}
Server={SERVER}
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
"""


def write_backtest_ini(case: BacktestCase, set_file: str) -> tuple[Path, str]:
    name = report_stem("AcaneM1_v1", case)
    config = tester_common() + f"""
[Tester]
Expert=AcaneLab\\AcaneM1_v1.ex5
ExpertParameters={set_file}
Symbol={SYMBOL}
Period={PERIOD}
Login={ACCOUNT}
Model={case.model}
ExecutionMode={case.delay_ms}
Optimization=0
FromDate={case.from_date}
ToDate={case.to_date}
ForwardMode=0
Report=\\Reports\\{name}
ReplaceReport=1
ShutdownTerminal=1
Deposit={case.deposit}
Currency=USD
Leverage={case.leverage}
UseLocal=1
UseRemote=0
UseCloud=0
Visual=0
"""
    path = MT5_BUILD / f"{name}.ini"
    write_utf16(path, config)
    shutil.copy2(path, OUT / path.name)
    return path, name


def write_optimization_ini(set_file: str) -> tuple[Path, str]:
    name = "AcaneM1_v1_genetic_2025_forward_20260101_20260510_d100_delay100_model4"
    config = tester_common() + f"""
[Tester]
Expert=AcaneLab\\AcaneM1_v1.ex5
ExpertParameters={set_file}
Symbol={SYMBOL}
Period={PERIOD}
Login={ACCOUNT}
Model={MODEL_REAL_TICKS}
ExecutionMode=100
Optimization=2
OptimizationCriterion=6
FromDate=2025.01.01
ToDate=2026.05.10
ForwardMode=4
ForwardDate=2026.01.01
Report=\\Reports\\{name}
ReplaceReport=1
ShutdownTerminal=1
Deposit={BASE_DEPOSIT}
Currency=USD
Leverage={BASE_LEVERAGE}
UseLocal=1
UseRemote=0
UseCloud=0
Visual=0
"""
    path = MT5_BUILD / f"{name}.ini"
    write_utf16(path, config)
    shutil.copy2(path, OUT / path.name)
    return path, name


def run_terminal(ini: Path, timeout: int) -> bool:
    try:
        subprocess.run(
            [str(WINE), TERMINAL, f"/config:{win_build_path(ini.name)}"],
            env=env(),
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=timeout,
        )
        return True
    except subprocess.TimeoutExpired:
        return False


def wait_report(stem: str, suffix: str = ".htm", seconds: int = 180) -> Path:
    report = REPORTS / f"{stem}{suffix}"
    for _ in range(seconds):
        if report.exists() and report.stat().st_size > 0:
            return report
        time.sleep(1)
    raise RuntimeError(f"report missing: {report}")


def cell(text: str, label: str, default: str = "") -> str:
    for row in iter_rows(text):
        for index, value in enumerate(row[:-1]):
            if value == label:
                return row[index + 1]
    return default


def pct_in(value: str) -> float:
    match = re.search(r"\(([-\d.]+)%\)", value)
    return float(match.group(1)) if match else 0.0


def parse_backtest_report(path: Path, case: BacktestCase) -> dict[str, object]:
    text = read_report(path)
    profit_trades = cell(text, "Profit Trades (% of total):")
    loss_trades = cell(text, "Loss Trades (% of total):")
    eqdd = cell(text, "Equity Drawdown Maximal:")
    return {
        "case": case.name,
        "from": case.from_date,
        "to": case.to_date,
        "deposit": case.deposit,
        "leverage": cell(text, "Leverage:", case.leverage),
        "model": case.model,
        "delay_ms": case.delay_ms,
        "history_quality": cell(text, "History Quality:"),
        "net": parse_first_number(cell(text, "Total Net Profit:")),
        "pf": parse_first_number(cell(text, "Profit Factor:")),
        "trades": int(parse_first_number(cell(text, "Total Trades:"))),
        "win_rate": pct_in(profit_trades),
        "loss_rate": pct_in(loss_trades),
        "eqdd": eqdd,
        "eqdd_pct": pct_in(eqdd),
        "largest_loss": parse_first_number(cell(text, "Largest loss trade:")),
        "avg_loss": parse_first_number(cell(text, "Average loss trade:")),
        "max_consecutive_losses": cell(text, "Maximum consecutive losses ($):"),
        "report": str(OUT / path.name),
    }


def copy_report_artifacts(stem: str) -> list[Path]:
    copied: list[Path] = []
    for path in REPORTS.glob(f"{stem}*"):
        if path.is_file():
            target = OUT / path.name
            shutil.copy2(path, target)
            copied.append(target)
    return copied


def run_backtest(case: BacktestCase, set_file: str, timeout: int) -> dict[str, object]:
    ini, stem = write_backtest_ini(case, set_file)
    for old in REPORTS.glob(f"{stem}*"):
        if old.is_file():
            old.unlink()
    completed = run_terminal(ini, timeout)
    if not completed:
        raise TimeoutError(f"MT5 did not finish {ini.name} within {timeout}s")
    report = wait_report(stem)
    copy_report_artifacts(stem)
    return parse_backtest_report(report, case)


def parse_optimization_xml(path: Path) -> list[dict[str, object]]:
    raw = path.read_bytes()
    text = raw.decode("utf-16le", errors="ignore") if raw.startswith(b"\xff\xfe") else raw.decode(errors="ignore")
    rows: list[dict[str, object]] = []
    try:
        root = ElementTree.fromstring(text)
    except ElementTree.ParseError:
        return rows
    for row in root.iter():
        if row.tag.lower().endswith("row") or row.tag.lower().endswith("pass"):
            data = {child.tag: (child.text or "") for child in list(row)}
            if data:
                rows.append(data)
    return rows


def run_optimization(timeout: int) -> dict[str, object]:
    set_path = write_set("AcaneM1_v1_genetic.set", optimize=True)
    ini, stem = write_optimization_ini(set_path.name)
    for old in REPORTS.glob(f"{stem}*"):
        if old.is_file():
            old.unlink()
    completed = run_terminal(ini, timeout)
    artifacts = copy_report_artifacts(stem)
    xml_rows = []
    for artifact in artifacts:
        if artifact.suffix.lower() == ".xml":
            xml_rows.extend(parse_optimization_xml(artifact))
    summary = {
        "stem": stem,
        "set": str(OUT / set_path.name),
        "ini": str(OUT / ini.name),
        "artifacts": [str(path) for path in artifacts],
        "parsed_xml_rows": len(xml_rows),
        "completed_before_timeout": completed,
        "note": "MT5 native genetic optimization, ForwardDate=2026.01.01, local agents only, cloud/remote disabled.",
    }
    (OUT / "optimization_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    return summary


def matrix_cases() -> list[BacktestCase]:
    return [
        BacktestCase("last_week_20260501_20260510", "2026.05.01", "2026.05.10", delay_ms=100),
        BacktestCase("last_month_20260410_20260510", "2026.04.10", "2026.05.10", delay_ms=100),
        BacktestCase("ytd_2026", "2026.01.01", "2026.05.10", delay_ms=100),
        BacktestCase("current_2025", "2025.01.01", "2026.05.10", delay_ms=100),
        BacktestCase("stress_last_month_20260410_20260510", "2026.04.10", "2026.05.10", delay_ms=200),
        BacktestCase("stress_ytd_2026", "2026.01.01", "2026.05.10", delay_ms=200),
        BacktestCase("optional_29_ytd_2026", "2026.01.01", "2026.05.10", deposit=29, delay_ms=100),
    ]


def write_matrix_summary(results: list[dict[str, object]]) -> None:
    lines = [
        "# AcaneM1_v1 MT5 Real-Tick Validation",
        "",
        "Setup: `XAUUSD`, `M1`, account `265874264`, server `Exness-MT5Real38`, `Model=4` real ticks. Main acceptance uses `$100`, leverage `1:2000`, delay `100ms`.",
        "",
        "| Case | Delay | Deposit | Net | PF | Trades | Win rate | Eq DD | Largest loss | History |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: | --- |",
    ]
    for row in results:
        lines.append(
            "| {case} | {delay_ms}ms | {deposit} | {net:.2f} | {pf:.2f} | {trades} | {win_rate:.2f}% | {eqdd} | {largest_loss:.2f} | {history_quality} |".format(
                **row
            )
        )
    hard_pass = [
        row
        for row in results
        if row["deposit"] == BASE_DEPOSIT
        and row["delay_ms"] == 100
        and str(row["case"]) in {"last_week_20260501_20260510", "last_month_20260410_20260510", "ytd_2026", "current_2025"}
        and float(row["net"]) > 0
        and float(row["eqdd_pct"]) < 20.0
        and int(row["trades"]) > 0
    ]
    lines.extend(
        [
            "",
            f"Hard gate rows passing individually: `{len(hard_pass)}/4`.",
            "Live package should only be created after all acceptance rows and stress rows are reviewed.",
            "",
            "Raw JSON: `matrix_results.json`.",
        ]
    )
    (OUT / "SUMMARY.md").write_text("\n".join(lines) + "\n")
    (OUT / "matrix_results.json").write_text(json.dumps(results, indent=2) + "\n")


def prepare() -> Path:
    OUT.mkdir(parents=True, exist_ok=True)
    ex5 = compile_source()
    copy_lab_expert(ex5)
    return ex5


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["compile", "sanity", "matrix", "optimize", "package-live"], default="sanity")
    parser.add_argument("--timeout", type=int, default=1800)
    args = parser.parse_args()

    ex5 = prepare()
    fixed_set = write_set("AcaneM1_v1_default.set", optimize=False)

    if args.mode == "compile":
        print(f"compiled {ex5}")
        return

    if args.mode == "package-live":
        package_live_expert(ex5)
        print(EXPERTS / "Acane" / "AcaneM1_v1.ex5")
        return

    if args.mode == "optimize":
        summary = run_optimization(args.timeout)
        print(json.dumps(summary, indent=2))
        return

    if args.mode == "matrix":
        results = []
        for case in matrix_cases():
            print(f"running {case.name} deposit={case.deposit} delay={case.delay_ms}ms model={case.model}", flush=True)
            row = run_backtest(case, fixed_set.name, args.timeout)
            print(f"done {case.name}: net={row['net']:.2f} pf={row['pf']:.2f} trades={row['trades']} eqdd={row['eqdd']}", flush=True)
            results.append(row)
        write_matrix_summary(results)
        print(OUT / "SUMMARY.md")
        return

    sanity = BacktestCase("sanity_20260501_20260510", "2026.05.01", "2026.05.10", delay_ms=100)
    row = run_backtest(sanity, fixed_set.name, args.timeout)
    print(json.dumps(row, indent=2))


if __name__ == "__main__":
    main()
