#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import difflib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from analyze_mt5_report import iter_rows, parse_first_number, read_report  # noqa: E402


RESEARCH = ROOT / "invictusforward-8-research"
EXP_ROOT = RESEARCH / "invictus8_v2_native_opt"
SRC_ROOT = EXP_ROOT / "source"
SETS_DIR = EXP_ROOT / "sets"
OPT_DIR = EXP_ROOT / "optimization"
CONF_DIR = EXP_ROOT / "confirmation"
REPORT_DIR = EXP_ROOT / "reports"

WINEPREFIX = Path.home() / "Library/Application Support/net.metaquotes.wine.metatrader5"
WINE = Path("/Applications/MetaTrader 5.app/Contents/SharedSupport/wine/bin/wine64")
TERMINAL = r"C:\Program Files\MetaTrader 5\terminal64.exe"
METAEDITOR = r"C:\Program Files\MetaTrader 5\metaeditor64.exe"
MT5_BUILD = WINEPREFIX / "drive_c" / "MT5Build"
REPORTS = WINEPREFIX / "drive_c" / "Program Files" / "MetaTrader 5" / "Reports"
EXPERTS = WINEPREFIX / "drive_c" / "Program Files" / "MetaTrader 5" / "MQL5" / "Experts"
PROFILES_TESTER = WINEPREFIX / "drive_c" / "Program Files" / "MetaTrader 5" / "MQL5" / "Profiles" / "Tester"
TESTER_CACHE = WINEPREFIX / "drive_c" / "Program Files" / "MetaTrader 5" / "Tester" / "cache"

LOGIN = "184000633"
SERVER = "Exness-MT5Real25"
SYMBOL = "XAUUSDc"
PERIOD = "M15"
CURRENCY = "USC"
LEVERAGE = "1:2000"
MODEL = 4
EXECUTION_MODE_MS = 100
OPT_PASS_CSV = "InvictusForward8_V2_optimization_passes.csv"
OOS_CANDIDATE_LIMIT = 200
OPT_COLUMNS = [
    "profit",
    "profit_factor",
    "trades",
    "equity_dd_pct",
    "balance_dd_pct",
    "recovery_factor",
    "BT_CompoundingPer",
    "BT_MaxLotCap",
    "Guard_BlockHour04",
    "Guard_BlockHour05",
    "Guard_BlockHour10",
    "Guard_BlockHour11",
    "Guard_DC_BlockHour00",
    "Guard_DC_BlockHour01",
    "Guard_DC_BlockHour10",
    "Guard_DC_BlockHour23",
    "Guard_MaxTrendPosLowBalance",
    "Guard_MaxTrendPosMidBalance",
    "Guard_MaxTrendPosHighBalance",
    "RangeBounce_LotMult",
    "RangeBounce_MaxBuy",
    "RangeBounce_MaxSell",
    "RangeBounce_EntryPct",
    "RangeBounce_MaxEntriesPerRange",
    "DropCatcher_BodyATR",
    "DropCatcher_MinBodyDlr",
    "DropCatcher_VolMult",
    "DropCatcher_MaxATR",
    "DropCatcher_SL_ATR",
    "DropCatcher_RR",
    "DropCatcher_LotMult",
    "DropCatcher_TrailATR",
    "SidewaysMinMethods",
    "MTF_H1_ADX_Max",
    "MTF_H4_ADX_Max",
    "PriceRange_ATRMult",
]


@dataclass(frozen=True)
class ExpertSpec:
    key: str
    label: str
    source_dir: Path
    source_file: str
    install_folder: str
    ex5_file: str


@dataclass(frozen=True)
class WindowSpec:
    key: str
    label: str
    from_date: str
    to_date: str


@dataclass(frozen=True)
class CaseSpec:
    expert: ExpertSpec
    window: WindowSpec
    deposit: int
    set_file: Path | None = None


EXPERTS_TO_RUN = [
    ExpertSpec(
        key="base",
        label="Base",
        source_dir=SRC_ROOT / "base",
        source_file="InvictusForward-8.mq5",
        install_folder="InvictusForward8_Base",
        ex5_file="InvictusForward-8.ex5",
    ),
    ExpertSpec(
        key="v1",
        label="V1",
        source_dir=SRC_ROOT / "v1",
        source_file="InvictusForward-8-Tuned.mq5",
        install_folder="InvictusForward8_V1",
        ex5_file="InvictusForward-8-Tuned.ex5",
    ),
    ExpertSpec(
        key="v2",
        label="V2",
        source_dir=SRC_ROOT / "v2",
        source_file="InvictusForward-8-V2.mq5",
        install_folder="InvictusForward8_V2",
        ex5_file="InvictusForward-8-V2.ex5",
    ),
]

TRAIN_WINDOW = WindowSpec("train_2026_jan_apr", "Train Jan-Apr", "2026.01.01", "2026.04.30")
WINDOWS = [
    TRAIN_WINDOW,
    WindowSpec("oos_may", "OOS May", "2026.05.01", "2026.05.10"),
    WindowSpec("last_month", "Last Month", "2026.04.10", "2026.05.10"),
    WindowSpec("ytd_2026", "2026 YTD", "2026.01.01", "2026.05.10"),
]
DEPOSITS = [1000, 20000]

V1_DEFAULTS: dict[str, object] = {
    "BT_RiskPercent": 3.0,
    "BT_UseFixedLot": False,
    "BT_FixedLot": 0.01,
    "BT_CompoundingPer": 500.0,
    "BT_MaxLotCap": 1.50,
    "BT_EnableSideways": True,
    "BT_MinSLDollar": 25.0,
    "BT_MaxSLDollar": 25.0,
    "EnableReversalClose": True,
    "SidewaysMinMethods": 4,
    "BB_Period": 20,
    "BB_Deviation": 2.0,
    "KC_ATRMultiplier": 1.5,
    "MTF_H1_ADX_Max": 25,
    "MTF_H4_ADX_Max": 22,
    "ATR_CompressionRatio": 0.65,
    "BBWidth_RelativeRatio": 0.70,
    "PriceRange_ATRMult": 2.3,
    "RangeBounce_LotMult": 0.25,
    "RangeBounce_MaxBuy": 2,
    "RangeBounce_MaxSell": 0,
    "RangeBounce_EntryPct": 0.25,
    "RangeBounce_MaxEntriesPerRange": 4,
    "Guard_EnableBadHourFilter": True,
    "Guard_BlockHour04": True,
    "Guard_BlockHour05": True,
    "Guard_BlockHour10": True,
    "Guard_BlockHour11": True,
    "Guard_EnableDropCatcherHourFilter": True,
    "Guard_DC_BlockHour00": True,
    "Guard_DC_BlockHour01": True,
    "Guard_DC_BlockHour10": True,
    "Guard_DC_BlockHour23": True,
    "Guard_MaxTrendPosLowBalance": 3,
    "Guard_MaxTrendPosMidBalance": 3,
    "Guard_MaxTrendPosHighBalance": 2,
    "EnableDropCatcher": True,
    "DropCatcher_BodyATR": 1.8,
    "DropCatcher_MinBodyDlr": 12.0,
    "DropCatcher_VolMult": 1.3,
    "DropCatcher_MaxATR": 15.0,
    "DropCatcher_SL_ATR": 2.0,
    "DropCatcher_RR": 3.0,
    "DropCatcher_LotMult": 0.25,
    "DropCatcher_TrailATR": 1.0,
}

PHASE1_RANGES: dict[str, tuple[object, object, object]] = {
    "BT_CompoundingPer": (300.0, 100.0, 1000.0),
    "BT_MaxLotCap": (0.50, 0.25, 2.00),
    "Guard_BlockHour04": (False, 0, True),
    "Guard_BlockHour05": (False, 0, True),
    "Guard_BlockHour10": (False, 0, True),
    "Guard_BlockHour11": (False, 0, True),
    "Guard_DC_BlockHour00": (False, 0, True),
    "Guard_DC_BlockHour01": (False, 0, True),
    "Guard_DC_BlockHour10": (False, 0, True),
    "Guard_DC_BlockHour23": (False, 0, True),
    "Guard_MaxTrendPosLowBalance": (2, 1, 5),
    "Guard_MaxTrendPosMidBalance": (2, 1, 5),
    "Guard_MaxTrendPosHighBalance": (1, 1, 4),
    "RangeBounce_LotMult": (0.10, 0.10, 0.50),
    "RangeBounce_MaxBuy": (0, 1, 3),
    "RangeBounce_MaxSell": (0, 1, 2),
    "RangeBounce_EntryPct": (0.15, 0.05, 0.35),
    "RangeBounce_MaxEntriesPerRange": (1, 1, 6),
    "DropCatcher_BodyATR": (1.4, 0.2, 2.4),
    "DropCatcher_MinBodyDlr": (8.0, 2.0, 18.0),
    "DropCatcher_VolMult": (1.0, 0.2, 1.8),
    "DropCatcher_MaxATR": (10.0, 2.0, 20.0),
    "DropCatcher_SL_ATR": (1.4, 0.2, 2.6),
    "DropCatcher_RR": (2.0, 0.5, 4.0),
    "DropCatcher_LotMult": (0.10, 0.10, 0.50),
    "DropCatcher_TrailATR": (0.6, 0.2, 1.4),
    "SidewaysMinMethods": (3, 1, 5),
    "MTF_H1_ADX_Max": (20, 5, 30),
    "MTF_H4_ADX_Max": (18, 4, 26),
    "PriceRange_ATRMult": (1.8, 0.2, 2.8),
}

PARAM_TYPES = {name: type(value) for name, value in V1_DEFAULTS.items()}


def env() -> dict[str, str]:
    output = os.environ.copy()
    output["WINEPREFIX"] = str(WINEPREFIX)
    output["WINEDEBUG"] = "-all"
    return output


def ensure_dirs() -> None:
    for directory in (EXP_ROOT, SETS_DIR, OPT_DIR, CONF_DIR, REPORT_DIR, MT5_BUILD, PROFILES_TESTER):
        directory.mkdir(parents=True, exist_ok=True)


def win_build_path(filename: str) -> str:
    return rf"C:\MT5Build\{filename}"


def decode_log(path: Path) -> str:
    data = path.read_bytes()
    for encoding in ("utf-16le", "utf-8"):
        text = data.decode(encoding, errors="ignore")
        if "Result:" in text or "error" in text.lower():
            return text
    return data.decode("utf-16le", errors="ignore")


def write_utf16(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"\xff\xfe" + text.encode("utf-16le"))


def set_value(value: object) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, float):
        return f"{value:.10g}"
    return str(value)


def cast_param(name: str, value: str) -> object:
    kind = PARAM_TYPES.get(name, str)
    if kind is bool:
        return value.strip().lower() in {"true", "1", "yes"}
    if kind is int:
        return int(float(value))
    if kind is float:
        return float(value)
    return value


def set_lines(values: dict[str, object], ranges: dict[str, tuple[object, object, object]] | None = None) -> list[str]:
    ranges = ranges or {}
    lines = [
        "; InvictusForward8 V2 native MT5 set",
        f"; Symbol={SYMBOL}, Period={PERIOD}, Currency={CURRENCY}, Leverage={LEVERAGE}, Model={MODEL}",
    ]
    for name, default in values.items():
        if name in ranges:
            start, step, stop = ranges[name]
            enabled = "Y"
        else:
            start, step, stop = default, 0, default
            enabled = "N"
        lines.append(
            f"{name}={set_value(default)}||{set_value(start)}||{set_value(step)}||{set_value(stop)}||{enabled}"
        )
    return lines


def write_set(name: str, values: dict[str, object], ranges: dict[str, tuple[object, object, object]] | None = None) -> Path:
    path = SETS_DIR / name
    text = "\r\n".join(set_lines(values, ranges)) + "\r\n"
    write_utf16(path, text)
    shutil.copy2(path, PROFILES_TESTER / name)
    return path


def compile_expert(expert: ExpertSpec) -> Path:
    if not expert.source_dir.exists():
        raise RuntimeError(f"source folder missing: {expert.source_dir}")
    build_dir = MT5_BUILD / expert.install_folder
    if build_dir.exists():
        shutil.rmtree(build_dir)
    shutil.copytree(expert.source_dir, build_dir)

    log = build_dir / f"{expert.install_folder}.compile.log"
    source = rf"C:\MT5Build\{expert.install_folder}\{expert.source_file}"
    log_win = rf"C:\MT5Build\{expert.install_folder}\{log.name}"
    subprocess.run(
        [str(WINE), METAEDITOR, f"/compile:{source}", f"/log:{log_win}"],
        env=env(),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
        timeout=180,
    )
    text = decode_log(log)
    destination = OPT_DIR / log.name if expert.key == "v2" else CONF_DIR / log.name
    shutil.copy2(log, destination)
    if "0 errors" not in text:
        raise RuntimeError(f"{expert.label} compile failed; see {destination}")

    ex5 = build_dir / expert.ex5_file
    if not ex5.exists():
        raise RuntimeError(f"compiled ex5 missing: {ex5}")
    target_dir = EXPERTS / expert.install_folder
    target_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ex5, target_dir / expert.ex5_file)
    shutil.copy2(ex5, (OPT_DIR if expert.key == "v2" else CONF_DIR) / f"{expert.install_folder}_{expert.ex5_file}")
    return ex5


def report_stem(case: CaseSpec) -> str:
    start = case.window.from_date.replace(".", "")
    end = case.window.to_date.replace(".", "")
    return (
        f"InvictusForward8_{case.expert.key}_{case.window.key}_d{case.deposit}USC_"
        f"{SYMBOL}_{PERIOD}_lev2000_delay{EXECUTION_MODE_MS}_model{MODEL}_{start}_{end}"
    )


def tester_ini(
    *,
    expert: ExpertSpec,
    stem: str,
    from_date: str,
    to_date: str,
    deposit: int,
    optimization: int,
    set_file: Path | None = None,
    forward_date: str | None = None,
) -> Path:
    lines = [
        "[Common]",
        f"Login={LOGIN}",
        f"Server={SERVER}",
        "ProxyEnable=0",
        "KeepPrivate=1",
        "NewsEnable=1",
        "CertInstall=1",
        "",
        "[Experts]",
        "AllowLiveTrading=0",
        "AllowDllImport=0",
        "Enabled=1",
        "Account=0",
        "Profile=0",
        "",
        "[Tester]",
        f"Expert={expert.install_folder}\\{expert.ex5_file}",
    ]
    if set_file is not None:
        lines.append(f"ExpertParameters={set_file.name}")
    lines.extend(
        [
            f"Symbol={SYMBOL}",
            f"Period={PERIOD}",
            f"Login={LOGIN}",
            f"Model={MODEL}",
            f"ExecutionMode={EXECUTION_MODE_MS}",
            f"Optimization={optimization}",
            "OptimizationCriterion=0",
            f"FromDate={from_date}",
            f"ToDate={to_date}",
        ]
    )
    if forward_date:
        lines.extend(["ForwardMode=4", f"ForwardDate={forward_date}"])
    else:
        lines.append("ForwardMode=0")
    lines.extend(
        [
            f"Report=\\Reports\\{stem}",
            "ReplaceReport=1",
            "ShutdownTerminal=1",
            f"Deposit={deposit}",
            f"Currency={CURRENCY}",
            f"Leverage={LEVERAGE}",
            "UseLocal=1",
            "UseRemote=0",
            "UseCloud=0",
            "Visual=0",
            "",
        ]
    )
    path = MT5_BUILD / f"{stem}.ini"
    write_utf16(path, "\n".join(lines))
    return path


def run_terminal_config(ini: Path, timeout: int) -> bool:
    try:
        subprocess.run(
            [str(WINE), TERMINAL, f"/config:{win_build_path(ini.name)}"],
            env=env(),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
            timeout=timeout,
        )
        return True
    except subprocess.TimeoutExpired:
        return False


def remove_old_reports(stem: str) -> None:
    for old in REPORTS.glob(f"{stem}*"):
        if old.is_file():
            old.unlink()


def copy_report_artifacts(stem: str, destination: Path) -> list[str]:
    destination.mkdir(parents=True, exist_ok=True)
    copied: list[str] = []
    for artifact in REPORTS.glob(f"{stem}*"):
        if artifact.is_file():
            target = destination / artifact.name
            shutil.copy2(artifact, target)
            copied.append(str(target))
    return copied


def load_existing_phase_outputs() -> list[dict[str, object]]:
    outputs: list[dict[str, object]] = []
    for phase in ("phase1", "phase2"):
        csv_paths = sorted(OPT_DIR.glob(f"{phase}_{OPT_PASS_CSV}"))
        if not csv_paths:
            continue
        rows = read_optimization_rows(csv_paths)
        for row in rows:
            row["phase"] = phase
        outputs.append(
            {
                "phase": phase,
                "completed_before_timeout": "reused",
                "set": str(SETS_DIR / f"InvictusForward8_V2_{phase}.set"),
                "ini": str(next(iter(sorted(OPT_DIR.glob(f"InvictusForward8_v2_{phase}_*.ini"))), "")),
                "csv_artifacts": [str(path) for path in csv_paths],
                "opt_artifacts": [str(path) for path in sorted(OPT_DIR.glob(f"{phase}_*.opt"))],
                "rows": rows,
            }
        )
    return outputs


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


def read_ini_settings(path: Path) -> dict[str, str]:
    text = path.read_bytes().decode("utf-16le", errors="ignore").lstrip("\ufeff")
    settings: dict[str, str] = {}
    for line in text.splitlines():
        if "=" not in line or line.lstrip().startswith(";"):
            continue
        key, value = line.split("=", 1)
        settings[key.strip()] = value.strip()
    return settings


def parse_report(report: Path, case: CaseSpec, ini: Path) -> dict[str, object]:
    text = read_report(report)
    profit_trades = cell(text, "Profit Trades (% of total):")
    loss_trades = cell(text, "Loss Trades (% of total):")
    row: dict[str, object] = {
        "expert_key": case.expert.key,
        "expert": case.expert.label,
        "window_key": case.window.key,
        "window": case.window.label,
        "from": case.window.from_date,
        "to": case.window.to_date,
        "deposit": case.deposit,
        "currency": cell(text, "Currency:", ""),
        "initial_deposit": parse_first_number(cell(text, "Initial Deposit:")),
        "account": LOGIN,
        "server": SERVER,
        "symbol": cell(text, "Symbol:", SYMBOL),
        "period": PERIOD,
        "period_report": cell(text, "Period:", ""),
        "leverage": cell(text, "Leverage:", LEVERAGE),
        "model": MODEL,
        "execution_mode_ms": EXECUTION_MODE_MS,
        "optimization": 0,
        "use_local": 1,
        "use_remote": 0,
        "use_cloud": 0,
        "history_quality": cell(text, "History Quality:"),
        "bars": int(parse_first_number(cell(text, "Bars:"))),
        "ticks": int(parse_first_number(cell(text, "Ticks:"))),
        "net": parse_first_number(cell(text, "Total Net Profit:")),
        "gross_profit": parse_first_number(cell(text, "Gross Profit:")),
        "gross_loss": parse_first_number(cell(text, "Gross Loss:")),
        "profit_factor": parse_first_number(cell(text, "Profit Factor:")),
        "expected_payoff": parse_first_number(cell(text, "Expected Payoff:")),
        "trades": int(parse_first_number(cell(text, "Total Trades:"))),
        "profit_trades": int(parse_first_number(profit_trades)),
        "loss_trades": int(parse_first_number(loss_trades)),
        "win_rate_pct": pct_in(profit_trades),
        "equity_dd": cell(text, "Equity Drawdown Maximal:"),
        "equity_dd_pct": dd_pct(cell(text, "Equity Drawdown Maximal:")),
        "balance_dd": cell(text, "Balance Drawdown Maximal:"),
        "balance_dd_pct": dd_pct(cell(text, "Balance Drawdown Maximal:")),
        "largest_loss": parse_first_number(cell(text, "Largest loss trade:")),
        "avg_loss": parse_first_number(cell(text, "Average loss trade:")),
        "max_consecutive_losses": cell(text, "Maximum consecutive losses ($):"),
        "on_tester": parse_first_number(cell(text, "OnTester result:")),
        "report": str(CONF_DIR / f"{report_stem(case)}.htm"),
        "ini": str(CONF_DIR / f"{report_stem(case)}.ini"),
        "set": str(case.set_file) if case.set_file else "",
        "ini_settings": read_ini_settings(ini),
    }
    row["validation_issues"] = validate_result(row)
    return row


def validate_result(row: dict[str, object]) -> list[str]:
    issues: list[str] = []
    settings = row.get("ini_settings", {})
    if row["symbol"] != SYMBOL:
        issues.append(f"symbol={row['symbol']}")
    if row["leverage"] != LEVERAGE:
        issues.append(f"leverage={row['leverage']}")
    if row["history_quality"] != "100% real ticks":
        issues.append(f"history={row['history_quality']}")
    if row["currency"] != CURRENCY:
        issues.append(f"currency={row['currency']}")
    if abs(float(row["initial_deposit"]) - float(row["deposit"])) > 0.01:
        issues.append(f"initial_deposit={row['initial_deposit']}")
    expected_ini = {
        "Symbol": SYMBOL,
        "Period": PERIOD,
        "Model": str(MODEL),
        "ExecutionMode": str(EXECUTION_MODE_MS),
        "Optimization": "0",
        "Deposit": str(row["deposit"]),
        "Currency": CURRENCY,
        "Leverage": LEVERAGE,
        "UseLocal": "1",
        "UseRemote": "0",
        "UseCloud": "0",
    }
    if isinstance(settings, dict):
        for key, expected in expected_ini.items():
            actual = settings.get(key)
            if actual != expected:
                issues.append(f"ini_{key}={actual}")
    else:
        issues.append("ini_settings=missing")
    return issues


def run_case(case: CaseSpec, timeout: int) -> dict[str, object]:
    stem = report_stem(case)
    remove_old_reports(stem)
    ini = tester_ini(
        expert=case.expert,
        stem=stem,
        from_date=case.window.from_date,
        to_date=case.window.to_date,
        deposit=case.deposit,
        optimization=0,
        set_file=case.set_file,
    )
    completed = run_terminal_config(ini, timeout)
    report = REPORTS / f"{stem}.htm"
    for _ in range(300):
        if report.exists() and report.stat().st_size > 0:
            break
        time.sleep(1)
    if not report.exists() or report.stat().st_size == 0:
        raise RuntimeError(f"report missing after {stem}; completed={completed}")
    shutil.copy2(ini, CONF_DIR / ini.name)
    copy_report_artifacts(stem, CONF_DIR)
    row = parse_report(report, case, ini)
    row["completed_before_timeout"] = completed
    return row


def find_optimization_csvs() -> list[Path]:
    return sorted(path for path in WINEPREFIX.rglob(OPT_PASS_CSV) if path.is_file())


def clear_optimization_csvs() -> None:
    for path in find_optimization_csvs():
        try:
            path.unlink()
        except OSError:
            pass


def read_optimization_rows(csv_paths: list[Path]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    seen: set[tuple[object, ...]] = set()
    for path in csv_paths:
        with path.open("r", encoding="utf-16", errors="ignore", newline="") as handle:
            reader = csv.reader(handle, delimiter=";")
            raw_rows = [[cell.strip() for cell in raw] for raw in reader if raw]
            if not raw_rows:
                continue
            header = raw_rows[0]
            has_header = "profit" in header and "profit_factor" in header
            fieldnames = header if has_header else OPT_COLUMNS
            data_rows = raw_rows[1:] if has_header else raw_rows
            for raw_values in data_rows:
                if len(raw_values) < 2:
                    continue
                raw = dict(zip(fieldnames, raw_values))
                if "profit" not in raw:
                    continue
                row: dict[str, object] = {"source_csv": str(path)}
                for key, value in raw.items():
                    if key is None:
                        continue
                    value = (value or "").strip()
                    if key in V1_DEFAULTS:
                        row[key] = cast_param(key, value)
                    else:
                        try:
                            row[key] = float(value)
                        except ValueError:
                            row[key] = value
                fingerprint = tuple(row.get(key) for key in V1_DEFAULTS)
                if fingerprint in seen:
                    continue
                seen.add(fingerprint)
                rows.append(row)
    return rows


def run_optimization_phase(
    *,
    name: str,
    values: dict[str, object],
    ranges: dict[str, tuple[object, object, object]],
    timeout: int,
) -> dict[str, object]:
    clear_optimization_csvs()
    set_file = write_set(f"InvictusForward8_V2_{name}.set", values, ranges)
    stem = f"InvictusForward8_v2_{name}_genetic_train_forward_d1000USC_{SYMBOL}_{PERIOD}_20260101_20260510"
    ini = tester_ini(
        expert=next(expert for expert in EXPERTS_TO_RUN if expert.key == "v2"),
        stem=stem,
        from_date="2026.01.01",
        to_date="2026.05.10",
        deposit=1000,
        optimization=2,
        set_file=set_file,
        forward_date="2026.05.01",
    )
    shutil.copy2(ini, OPT_DIR / ini.name)
    before_opt = {path: path.stat().st_mtime for path in TESTER_CACHE.glob("*.opt")}
    completed = run_terminal_config(ini, timeout)
    time.sleep(3)
    csv_paths = find_optimization_csvs()
    copied_csvs: list[str] = []
    for path in csv_paths:
        target = OPT_DIR / f"{name}_{path.name}"
        shutil.copy2(path, target)
        copied_csvs.append(str(target))
    opt_artifacts: list[str] = []
    for path in TESTER_CACHE.glob("*.opt"):
        if path not in before_opt or path.stat().st_mtime > before_opt.get(path, 0):
            target = OPT_DIR / f"{name}_{path.name}"
            shutil.copy2(path, target)
            opt_artifacts.append(str(target))
    rows = read_optimization_rows(csv_paths)
    for row in rows:
        row["phase"] = name
    return {
        "phase": name,
        "completed_before_timeout": completed,
        "set": str(set_file),
        "ini": str(OPT_DIR / ini.name),
        "csv_artifacts": copied_csvs,
        "opt_artifacts": opt_artifacts,
        "rows": rows,
    }


def top_profit_candidates(rows: list[dict[str, object]], limit: int) -> list[dict[str, object]]:
    viable = [
        row for row in rows
        if float(row.get("profit", 0.0)) > 0.0 and float(row.get("profit_factor", 0.0)) > 1.0
    ]
    viable.sort(key=lambda r: (float(r.get("profit", 0.0)), float(r.get("profit_factor", 0.0))), reverse=True)
    return viable[:limit]


def optimizer_candidate_pool(phase_outputs: list[dict[str, object]], limit: int) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for output in phase_outputs:
        rows.extend(output["rows"])
    viable = [
        row for row in rows
        if float(row.get("profit", 0.0)) > 0.0 and float(row.get("profit_factor", 0.0)) > 1.0
    ]
    rankings = [
        sorted(viable, key=lambda row: (float(row.get("profit", 0.0)), float(row.get("profit_factor", 0.0))), reverse=True),
        sorted(viable, key=lambda row: (float(row.get("profit_factor", 0.0)), float(row.get("profit", 0.0))), reverse=True),
        sorted(viable, key=lambda row: (float(row.get("equity_dd_pct", 999.0)), -float(row.get("profit", 0.0)))),
        sorted(viable, key=lambda row: (float(row.get("recovery_factor", 0.0)), float(row.get("profit", 0.0))), reverse=True),
    ]
    pool: list[dict[str, object]] = []
    seen: set[tuple[object, ...]] = set()
    for ranking in rankings:
        for row in ranking:
            fingerprint = tuple(row.get(key) for key in V1_DEFAULTS)
            if fingerprint in seen:
                continue
            seen.add(fingerprint)
            pool.append(row)
            if len(pool) >= limit:
                return pool
    return pool


def candidate_values(row: dict[str, object]) -> dict[str, object]:
    values = dict(V1_DEFAULTS)
    for key in V1_DEFAULTS:
        if key in row:
            values[key] = row[key]
    return values


def narrow_ranges(values: dict[str, object]) -> dict[str, tuple[object, object, object]]:
    ranges: dict[str, tuple[object, object, object]] = {}
    for name, phase_range in PHASE1_RANGES.items():
        current = values[name]
        start, step, stop = phase_range
        if isinstance(current, bool):
            continue
        if isinstance(current, int):
            lo = max(int(start), int(current) - 1)
            hi = min(int(stop), int(current) + 1)
            ranges[name] = (lo, 1, hi)
        else:
            current_f = float(current)
            step_f = float(step)
            lo = max(float(start), current_f - step_f)
            hi = min(float(stop), current_f + step_f)
            ranges[name] = (round(lo, 10), step, round(hi, 10))
    return ranges


def select_v2_candidate(phase_outputs: list[dict[str, object]]) -> tuple[dict[str, object], list[dict[str, object]]]:
    rows: list[dict[str, object]] = []
    for output in phase_outputs:
        rows.extend(output["rows"])
    candidates = top_profit_candidates(rows, 30)
    if not candidates:
        fallback = {
            "phase": "fallback_v1",
            "profit": 0.0,
            "profit_factor": 0.0,
            "trades": 0.0,
            "equity_dd_pct": 0.0,
            **V1_DEFAULTS,
        }
        return fallback, []
    return candidates[0], candidates


def run_oos_candidate(candidate: dict[str, object], index: int, timeout: int) -> dict[str, object]:
    values = candidate_values(candidate)
    set_file = write_set(f"InvictusForward8_V2_oos_candidate_{index:02d}.set", values)
    v2 = next(expert for expert in EXPERTS_TO_RUN if expert.key == "v2")
    window = next(window for window in WINDOWS if window.key == "oos_may")
    case = CaseSpec(expert=v2, window=window, deposit=1000, set_file=set_file)
    stem = (
        f"InvictusForward8_v2_oos_candidate_{index:02d}_d1000USC_"
        f"{SYMBOL}_{PERIOD}_lev2000_delay{EXECUTION_MODE_MS}_model{MODEL}_20260501_20260510"
    )
    remove_old_reports(stem)
    ini = tester_ini(
        expert=v2,
        stem=stem,
        from_date=window.from_date,
        to_date=window.to_date,
        deposit=1000,
        optimization=0,
        set_file=set_file,
    )
    cached_report = OPT_DIR / f"{stem}.htm"
    cached_ini = OPT_DIR / ini.name
    if cached_report.exists() and cached_report.stat().st_size > 0 and cached_ini.exists():
        row = parse_report(cached_report, case, cached_ini)
        row.update(
            {
                "candidate_index": index,
                "optimizer_profit": candidate.get("profit"),
                "optimizer_profit_factor": candidate.get("profit_factor"),
                "optimizer_equity_dd_pct": candidate.get("equity_dd_pct"),
                "optimizer_phase": candidate.get("phase"),
                "completed_before_timeout": True,
                "report": str(cached_report),
                "ini": str(cached_ini),
                "artifacts": [str(path) for path in sorted(OPT_DIR.glob(f"{stem}*"))],
                "set": str(set_file),
                "cached": True,
            }
        )
        return row
    completed = run_terminal_config(ini, timeout)
    report = REPORTS / f"{stem}.htm"
    for _ in range(300):
        if report.exists() and report.stat().st_size > 0:
            break
        time.sleep(1)
    if not report.exists() or report.stat().st_size == 0:
        raise RuntimeError(f"OOS candidate report missing after {stem}; completed={completed}")
    shutil.copy2(ini, OPT_DIR / ini.name)
    copied = copy_report_artifacts(stem, OPT_DIR)
    row = parse_report(report, case, ini)
    row.update(
        {
            "candidate_index": index,
            "optimizer_profit": candidate.get("profit"),
            "optimizer_profit_factor": candidate.get("profit_factor"),
            "optimizer_equity_dd_pct": candidate.get("equity_dd_pct"),
            "optimizer_phase": candidate.get("phase"),
            "completed_before_timeout": completed,
            "report": str(OPT_DIR / f"{stem}.htm"),
            "ini": str(OPT_DIR / ini.name),
            "artifacts": copied,
            "set": str(set_file),
        }
    )
    return row


def select_v2_candidate_by_oos(
    phase_outputs: list[dict[str, object]],
    *,
    limit: int,
    timeout: int,
) -> tuple[dict[str, object], list[dict[str, object]], list[dict[str, object]]]:
    optimizer_selected, optimizer_candidates = select_v2_candidate(phase_outputs)
    screened_candidates = optimizer_candidate_pool(phase_outputs, limit)
    oos_rows: list[dict[str, object]] = []
    for index, candidate in enumerate(screened_candidates, start=1):
        row = run_oos_candidate(candidate, index, timeout)
        candidate["oos_net"] = row["net"]
        candidate["oos_profit_factor"] = row["profit_factor"]
        candidate["oos_trades"] = row["trades"]
        candidate["oos_equity_dd_pct"] = row["equity_dd_pct"]
        candidate["oos_validation_issues"] = row["validation_issues"]
        oos_rows.append(row)
        print(
            f"candidate {index:02d} OOS May net={row['net']:.2f} "
            f"pf={row['profit_factor']:.2f} validation={','.join(row['validation_issues']) if row['validation_issues'] else 'OK'}",
            flush=True,
        )
    viable = [
        candidate
        for candidate in screened_candidates
        if float(candidate.get("oos_net", 0.0)) > 0.0
        and float(candidate.get("oos_profit_factor", 0.0)) > 1.0
        and not candidate.get("oos_validation_issues")
    ]
    viable.sort(
        key=lambda row: (float(row.get("oos_net", 0.0)), float(row.get("oos_profit_factor", 0.0))),
        reverse=True,
    )
    if viable:
        selected = dict(viable[0])
        selected["selection_basis"] = "native_oos_may"
        selected["selection_rule"] = "highest OOS May native report net profit with profit_factor > 1.0"
        return selected, screened_candidates, oos_rows
    selected = dict(optimizer_selected)
    selected["selection_basis"] = "optimizer_fallback"
    selected["selection_rule"] = "fallback to highest optimizer OnTester profit because no OOS May candidate had PF > 1.0"
    return selected, screened_candidates, oos_rows


def write_candidate_json(
    rows: list[dict[str, object]],
    phase_outputs: list[dict[str, object]],
    selected: dict[str, object],
    oos_rows: list[dict[str, object]] | None = None,
) -> None:
    (REPORT_DIR / "optimization_candidates.json").write_text(json.dumps(rows, indent=2, default=str) + "\n")
    (REPORT_DIR / "optimization_oos_candidates.json").write_text(json.dumps(oos_rows or [], indent=2, default=str) + "\n")
    (REPORT_DIR / "optimization_summary.json").write_text(
        json.dumps(
            {
                "phases": [
                    {k: v for k, v in output.items() if k != "rows"}
                    | {"row_count": len(output["rows"])}
                    for output in phase_outputs
                ],
                "selected": selected,
                "selection_rule": selected.get(
                    "selection_rule",
                    "highest OOS May native report net profit with profit_factor > 1.0",
                ),
                "oos_candidate_count": len(oos_rows or []),
            },
            indent=2,
            default=str,
        )
        + "\n"
    )


def build_comparisons(results: list[dict[str, object]]) -> list[dict[str, object]]:
    by_key: dict[tuple[int, str], list[dict[str, object]]] = {}
    for row in results:
        by_key.setdefault((int(row["deposit"]), str(row["window_key"])), []).append(row)
    comparisons: list[dict[str, object]] = []
    window_order = {window.key: index for index, window in enumerate(WINDOWS)}
    for key in sorted(by_key, key=lambda item: (item[0], window_order.get(item[1], 99))):
        rows = by_key[key]
        by_expert = {str(row["expert_key"]): row for row in rows}
        if not {"base", "v1", "v2"}.issubset(by_expert):
            continue
        winner = max(rows, key=lambda row: float(row["net"]))
        v1 = by_expert["v1"]
        v2 = by_expert["v2"]
        v2_dd_worse = (
            float(v2["equity_dd_pct"]) > float(v1["equity_dd_pct"])
            or parse_first_number(str(v2["equity_dd"])) > parse_first_number(str(v1["equity_dd"]))
        )
        note = ""
        if winner["expert_key"] == "v2" and v2_dd_worse:
            note = "profit winner, not live-ready"
        elif v2_dd_worse:
            note = "V2 DD worse than V1"
        comparisons.append(
            {
                "deposit": key[0],
                "window_key": key[1],
                "window": str(rows[0]["window"]),
                "result_winner": str(winner["expert"]),
                "v2_live_ready": not v2_dd_worse,
                "note": note,
                "base_net": by_expert["base"]["net"],
                "base_pf": by_expert["base"]["profit_factor"],
                "base_eqdd": by_expert["base"]["equity_dd"],
                "v1_net": v1["net"],
                "v1_pf": v1["profit_factor"],
                "v1_eqdd": v1["equity_dd"],
                "v2_net": v2["net"],
                "v2_pf": v2["profit_factor"],
                "v2_eqdd": v2["equity_dd"],
            }
        )
    return comparisons


def write_param_diff(selected_values: dict[str, object]) -> None:
    lines = [
        "# V1 vs V2 Parameter Diff",
        "",
        "V1 is the first tuned version. V2 is the selected native MT5 optimization profile.",
        "",
        "| Parameter | V1 Default | V2 Selected | Changed |",
        "| --- | ---: | ---: | --- |",
    ]
    for name in V1_DEFAULTS:
        v1 = V1_DEFAULTS[name]
        v2 = selected_values.get(name, v1)
        lines.append(f"| {name} | {set_value(v1)} | {set_value(v2)} | {'yes' if v1 != v2 else ''} |")
    (REPORT_DIR / "PARAM_DIFF.md").write_text("\n".join(lines) + "\n")


def write_code_diff() -> None:
    base = (SRC_ROOT / "base" / "InvictusForward-8.mq5").read_text(errors="ignore").splitlines()
    v1 = (SRC_ROOT / "v1" / "InvictusForward-8-Tuned.mq5").read_text(errors="ignore").splitlines()
    v2 = (SRC_ROOT / "v2" / "InvictusForward-8-V2.mq5").read_text(errors="ignore").splitlines()
    base_v1 = list(difflib.unified_diff(base, v1, fromfile="Base/InvictusForward-8.mq5", tofile="V1/InvictusForward-8-Tuned.mq5", lineterm=""))
    v1_v2 = list(difflib.unified_diff(v1, v2, fromfile="V1/InvictusForward-8-Tuned.mq5", tofile="V2/InvictusForward-8-V2.mq5", lineterm=""))
    lines = [
        "# Base vs V1 vs V2 Code/Logic Diff",
        "",
        "## Summary",
        "",
        "- Base is the untouched source from the zip.",
        "- V1 adds the research guardrails: bad-hour filters, Drop Catcher hour filter, max trend position guard, and range-entry cap input.",
        "- V2 keeps V1 trading logic and adds `OnTester()` export for native MT5 optimization pass capture; selected behavior differences are parameter-level and documented in `PARAM_DIFF.md`.",
        "",
        "## Base -> V1 Unified Diff",
        "",
        "```diff",
        *base_v1[:500],
        "```",
        "",
        "## V1 -> V2 Unified Diff",
        "",
        "```diff",
        *v1_v2[:500],
        "```",
    ]
    (REPORT_DIR / "CODE_DIFF.md").write_text("\n".join(lines) + "\n")


def write_summary(
    results: list[dict[str, object]],
    selected_values: dict[str, object],
    phase_outputs: list[dict[str, object]],
    selected_candidate: dict[str, object] | None = None,
) -> None:
    comparisons = build_comparisons(results)
    (REPORT_DIR / "results.json").write_text(json.dumps(results, indent=2, default=str) + "\n")
    (REPORT_DIR / "comparison.json").write_text(json.dumps(comparisons, indent=2, default=str) + "\n")

    expert_order = {"base": 0, "v1": 1, "v2": 2}
    window_order = {window.key: index for index, window in enumerate(WINDOWS)}
    lines = [
        "# Invictus Forward-8 Base vs V1 vs V2",
        "",
        "Source of truth: native MT5 Strategy Tester reports generated through `terminal64.exe /config`.",
        "",
        f"Setup: account `{LOGIN}` on `{SERVER}`, `{SYMBOL}` `{PERIOD}`, currency `{CURRENCY}`, leverage `{LEVERAGE}`, `Model={MODEL}`, `ExecutionMode={EXECUTION_MODE_MS}`, `UseLocal=1`, `UseRemote=0`, `UseCloud=0`.",
        "",
        "All optimization and confirmation windows are 2026+ only. No 2025 result is used.",
        "",
        "## Optimization",
        "",
        "| Phase | Completed | Pass rows | CSV artifacts | Opt artifacts |",
        "| --- | --- | ---: | ---: | ---: |",
    ]
    for output in phase_outputs:
        lines.append(
            f"| {output['phase']} | {output['completed_before_timeout']} | {len(output['rows'])} | {len(output['csv_artifacts'])} | {len(output['opt_artifacts'])} |"
        )
    selection_rule = (selected_candidate or {}).get(
        "selection_rule",
        "highest OOS May native report net profit with profit_factor > 1.0",
    )
    lines.extend(
        [
            "",
            "Selected V2 parameters are written to `sets/InvictusForward8_V2_selected.set` and compared in `reports/PARAM_DIFF.md`.",
            f"V2 selection rule: `{selection_rule}`.",
        ]
    )
    if (selected_candidate or {}).get("selection_basis") == "optimizer_fallback":
        lines.append("OOS candidate screen: no screened optimizer candidate met `PF > 1.0`; V2 is kept only as an optimizer-fallback comparison profile.")
    lines.extend(
        [
            "",
            "## All Confirmation Runs",
            "",
            "| Expert | Deposit | Window | Net | PF | Trades | WR | Eq DD | Balance DD | Largest Loss | Max Consecutive Losses | History | Validation |",
            "| --- | ---: | --- | ---: | ---: | ---: | ---: | --- | --- | ---: | --- | --- | --- |",
        ]
    )
    for row in sorted(results, key=lambda r: (int(r["deposit"]), window_order.get(str(r["window_key"]), 99), expert_order.get(str(r["expert_key"]), 99))):
        validation = ", ".join(row["validation_issues"]) if row["validation_issues"] else "OK"
        lines.append(
            "| {expert} | {deposit} {currency} | {window} | {net:.2f} | {profit_factor:.2f} | {trades} | {win_rate_pct:.2f}% | {equity_dd} | {balance_dd} | {largest_loss:.2f} | {max_consecutive_losses} | {history_quality} | {validation} |".format(
                validation=validation,
                **row,
            )
        )
    lines.extend(
        [
            "",
            "## Winner By Window",
            "",
            "| Deposit | Window | Base Net/PF/DD | V1 Net/PF/DD | V2 Net/PF/DD | Result Winner | V2 Live-Ready | Note |",
            "| ---: | --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for row in comparisons:
        lines.append(
            "| {deposit} USC | {window} | {base_net:.2f} / {base_pf:.2f} / {base_eqdd} | {v1_net:.2f} / {v1_pf:.2f} / {v1_eqdd} | {v2_net:.2f} / {v2_pf:.2f} / {v2_eqdd} | {result_winner} | {v2_live_ready} | {note} |".format(
                **row
            )
        )
    thousand_v2 = [row for row in results if row["expert_key"] == "v2" and int(row["deposit"]) == 1000]
    max_v2_1000_dd = max((float(row["equity_dd_pct"]) for row in thousand_v2), default=0.0)
    if max_v2_1000_dd >= 30:
        recommendation = "V2 is profit-first, but 1000 USC still has aggressive drawdown. Treat it as research-only unless a lower-risk cent profile is created."
    else:
        recommendation = "V2 passes the configured drawdown screen for 1000 USC, but final live suitability should follow the V2-vs-V1 drawdown notes per window."
    lines.extend(["", "## Recommendation", "", recommendation])
    (REPORT_DIR / "SUMMARY.md").write_text("\n".join(lines) + "\n")


def run_full(args: argparse.Namespace) -> None:
    ensure_dirs()
    print("compile Base/V1/V2", flush=True)
    for expert in EXPERTS_TO_RUN:
        compile_expert(expert)

    phase_outputs: list[dict[str, object]] = []
    if args.reuse_optimization:
        print("reuse existing native optimization CSV artifacts", flush=True)
        phase_outputs = load_existing_phase_outputs()
        if not phase_outputs:
            raise RuntimeError(f"no phase optimization CSV artifacts found in {OPT_DIR}")
    elif not args.skip_optimization:
        print("run phase1 native genetic optimization", flush=True)
        phase1 = run_optimization_phase(
            name="phase1",
            values=dict(V1_DEFAULTS),
            ranges=PHASE1_RANGES,
            timeout=args.optimization_timeout,
        )
        phase_outputs.append(phase1)
        selected_phase1, top_phase1 = select_v2_candidate([phase1])
        if top_phase1 and not args.skip_phase2:
            print("run phase2 native narrow optimization", flush=True)
            seed_values = candidate_values(selected_phase1)
            phase2 = run_optimization_phase(
                name="phase2",
                values=seed_values,
                ranges=narrow_ranges(seed_values),
                timeout=args.optimization_timeout,
            )
            phase_outputs.append(phase2)
    else:
        print("skip optimization; use V1 defaults as V2 selected params", flush=True)

    all_rows: list[dict[str, object]] = []
    for output in phase_outputs:
        all_rows.extend(output["rows"])
    if phase_outputs:
        print("screen top V2 candidates on native OOS May", flush=True)
        selected, candidates, oos_rows = select_v2_candidate_by_oos(
            phase_outputs,
            limit=args.candidate_oos_limit,
            timeout=args.backtest_timeout,
        )
    else:
        selected, candidates = select_v2_candidate(phase_outputs)
        oos_rows = []
    selected_values = candidate_values(selected)
    selected_set = write_set("InvictusForward8_V2_selected.set", selected_values)
    shutil.copy2(selected_set, OPT_DIR / selected_set.name)
    write_candidate_json(candidates, phase_outputs, selected, oos_rows)
    write_param_diff(selected_values)
    write_code_diff()

    v2 = next(expert for expert in EXPERTS_TO_RUN if expert.key == "v2")
    cases = [
        CaseSpec(expert=expert, window=window, deposit=deposit, set_file=selected_set if expert.key == "v2" else None)
        for deposit in DEPOSITS
        for window in WINDOWS
        for expert in EXPERTS_TO_RUN
    ]
    results: list[dict[str, object]] = []
    requested = set(args.cases or [])
    if requested:
        cases = [case for case in cases if f"{case.expert.key}:{case.window.key}:{case.deposit}" in requested]
    for case in cases:
        print(f"run {case.expert.label} {case.window.key} d{case.deposit}", flush=True)
        row = run_case(case, args.backtest_timeout)
        issues = ",".join(row["validation_issues"]) if row["validation_issues"] else "OK"
        print(
            f"done {case.expert.label} {case.window.key} d{case.deposit} "
            f"net={row['net']:.2f} pf={row['profit_factor']:.2f} trades={row['trades']} validation={issues}",
            flush=True,
        )
        results.append(row)
        write_summary(results, selected_values, phase_outputs, selected)
    if v2.source_dir.exists():
        write_summary(results, selected_values, phase_outputs, selected)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--optimization-timeout", type=int, default=7200)
    parser.add_argument("--backtest-timeout", type=int, default=2400)
    parser.add_argument("--skip-optimization", action="store_true")
    parser.add_argument("--skip-phase2", action="store_true")
    parser.add_argument("--reuse-optimization", action="store_true")
    parser.add_argument("--candidate-oos-limit", type=int, default=OOS_CANDIDATE_LIMIT)
    parser.add_argument("--cases", nargs="*", help="optional confirmation case keys like v2:oos_may:1000")
    args = parser.parse_args()
    run_full(args)


if __name__ == "__main__":
    main()
