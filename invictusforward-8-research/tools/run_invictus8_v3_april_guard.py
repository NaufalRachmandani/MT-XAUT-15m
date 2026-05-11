#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import difflib
import json
import os
import re
import shutil
import statistics
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from analyze_mt5_report import (  # noqa: E402
    extract_deal_rows,
    iter_rows,
    parse_first_number,
    read_report,
    reconstruct_closed_trades,
)


RESEARCH = ROOT / "invictusforward-8-research"
EXP_ROOT = RESEARCH / "invictus8_v3_april_guard"
SRC_ROOT = EXP_ROOT / "source"
SETS_DIR = EXP_ROOT / "sets"
OPT_DIR = EXP_ROOT / "optimization"
VAL_DIR = EXP_ROOT / "validation"
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
OPT_PASS_CSV = "InvictusForward8_V3Guard_optimization_passes.csv"
MAX_CANDIDATES = 150

OPT_COLUMNS = [
    "score",
    "profit",
    "profit_factor",
    "trades",
    "equity_dd_pct",
    "balance_dd_pct",
    "recovery_factor",
    "BT_RiskPercent",
    "BT_CompoundingPer",
    "BT_MaxLotCap",
    "Guard_MaxTrendPosLowBalance",
    "RangeBounce_LotMult",
    "RangeBounce_MaxBuy",
    "RangeBounce_MaxSell",
    "RangeBounce_MaxEntriesPerRange",
    "DropCatcher_LotMult",
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
    stem_override: str | None = None


EXPERTS_TO_RUN = [
    ExpertSpec("v1", "V1", SRC_ROOT / "v1", "InvictusForward-8-Tuned.mq5", "InvictusForward8_V3AG_V1", "InvictusForward-8-Tuned.ex5"),
    ExpertSpec("v2live", "V2Live", SRC_ROOT / "v2live", "InvictusForward-8-V2Live.mq5", "InvictusForward8_V3AG_V2Live", "InvictusForward-8-V2Live.ex5"),
    ExpertSpec("v3guard", "V3Guard", SRC_ROOT / "v3guard", "InvictusForward-8-V3Guard.mq5", "InvictusForward8_V3AG_V3Guard", "InvictusForward-8-V3Guard.ex5"),
]

WALK_FORWARD = [
    {
        "key": "wf_a",
        "train": WindowSpec("train_a_jan_feb", "Train A Jan-Feb", "2026.01.01", "2026.02.28"),
        "validate": WindowSpec("validate_mar", "Validate Mar", "2026.03.01", "2026.03.31"),
    },
    {
        "key": "wf_b",
        "train": WindowSpec("train_b_feb_mar", "Train B Feb-Mar", "2026.02.01", "2026.03.31"),
        "validate": WindowSpec("validate_apr", "Validate Apr", "2026.04.01", "2026.04.30"),
    },
    {
        "key": "wf_c",
        "train": WindowSpec("train_c_jan_apr", "Train C Jan-Apr", "2026.01.01", "2026.04.30"),
        "validate": WindowSpec("validate_may", "Validate May", "2026.05.01", "2026.05.10"),
    },
]
VALIDATION_WINDOWS = [item["validate"] for item in WALK_FORWARD]
CONFIRM_WINDOWS = [
    WindowSpec("train_2026_jan_apr", "Train Jan-Apr", "2026.01.01", "2026.04.30"),
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

V2LIVE_DEFAULTS = dict(V1_DEFAULTS) | {
    "BT_RiskPercent": 1.0,
    "BT_CompoundingPer": 1000.0,
    "BT_MaxLotCap": 0.25,
    "Guard_MaxTrendPosLowBalance": 2,
    "RangeBounce_LotMult": 0.15,
    "RangeBounce_MaxBuy": 1,
    "RangeBounce_MaxSell": 0,
    "RangeBounce_MaxEntriesPerRange": 2,
    "DropCatcher_LotMult": 0.10,
}

V3_DEFAULTS = dict(V2LIVE_DEFAULTS) | {
    "BT_EnableTrending": True,
    "Guard_EnableTrendFillHourFilter": True,
    "Guard_TR_BlockHour00": True,
    "Guard_TR_BlockHour01": True,
    "Guard_TR_BlockHour04": True,
    "Guard_TR_BlockHour05": True,
    "Guard_TR_BlockHour10": True,
    "Guard_TR_BlockHour11": True,
    "Guard_TR_BlockHour19": True,
    "Guard_TR_BlockHour20": True,
    "Guard_TR_BlockHour22": True,
    "Guard_TR_BlockHour23": True,
    "Guard_TrendMinScoreAdd": 10,
    "Guard_AllowTrendCorrective": True,
    "Guard_TrendLossCooldownBars": 8,
    "Guard_TrendLossCooldownTrigger": 2,
    "Guard_MaxTrendDailyLossCount": 3,
    "Trend_LotMult": 1.0,
    "Guard_MaxTrendPosLowBalance": 1,
}

OPT_RANGES: dict[str, tuple[object, object, object]] = {
    "BT_RiskPercent": (0.5, 0.25, 2.0),
    "BT_CompoundingPer": (600.0, 100.0, 1500.0),
    "BT_MaxLotCap": (0.10, 0.05, 0.75),
    "Guard_MaxTrendPosLowBalance": (1, 1, 3),
    "RangeBounce_LotMult": (0.10, 0.05, 0.25),
    "RangeBounce_MaxBuy": (1, 1, 2),
    "RangeBounce_MaxEntriesPerRange": (1, 1, 3),
    "DropCatcher_LotMult": (0.10, 0.05, 0.20),
}

PARAM_TYPES = {name: type(value) for name, value in V3_DEFAULTS.items()}


def env() -> dict[str, str]:
    output = os.environ.copy()
    output["WINEPREFIX"] = str(WINEPREFIX)
    output["WINEDEBUG"] = "-all"
    return output


def ensure_dirs() -> None:
    for directory in (EXP_ROOT, SETS_DIR, OPT_DIR, VAL_DIR, CONF_DIR, REPORT_DIR, MT5_BUILD, PROFILES_TESTER):
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
        "; InvictusForward8 V2Live native MT5 set",
        f"; Symbol={SYMBOL}, Period={PERIOD}, Currency={CURRENCY}, Leverage={LEVERAGE}, Model={MODEL}",
    ]
    for name, default in values.items():
        if name in ranges:
            start, step, stop = ranges[name]
            enabled = "Y"
        else:
            start, step, stop = default, 0, default
            enabled = "N"
        lines.append(f"{name}={set_value(default)}||{set_value(start)}||{set_value(step)}||{set_value(stop)}||{enabled}")
    return lines


def write_set(name: str, values: dict[str, object], ranges: dict[str, tuple[object, object, object]] | None = None) -> Path:
    path = SETS_DIR / name
    write_utf16(path, "\r\n".join(set_lines(values, ranges)) + "\r\n")
    shutil.copy2(path, PROFILES_TESTER / name)
    return path


def compile_expert(expert: ExpertSpec) -> Path:
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
    target_log = (OPT_DIR if expert.key == "v2live" else CONF_DIR) / log.name
    shutil.copy2(log, target_log)
    if "0 errors" not in text:
        raise RuntimeError(f"{expert.label} compile failed; see {target_log}")
    ex5 = build_dir / expert.ex5_file
    if not ex5.exists():
        raise RuntimeError(f"compiled ex5 missing: {ex5}")
    target_dir = EXPERTS / expert.install_folder
    target_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ex5, target_dir / expert.ex5_file)
    shutil.copy2(ex5, (OPT_DIR if expert.key == "v2live" else CONF_DIR) / f"{expert.install_folder}_{expert.ex5_file}")
    return ex5


def tester_ini(
    *,
    expert: ExpertSpec,
    stem: str,
    from_date: str,
    to_date: str,
    deposit: int,
    optimization: int,
    set_file: Path | None = None,
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
            "ForwardMode=0",
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


def cell(text: str, label: str, default: str = "") -> str:
    for row in iter_rows(text):
        for index, value in enumerate(row[:-1]):
            if value == label:
                return row[index + 1]
    return default


def pct_in(value: str) -> float:
    match = re.search(r"\(([-\d.]+)%\)", value)
    return float(match.group(1)) if match else 0.0


def read_ini_settings(path: Path) -> dict[str, str]:
    text = path.read_bytes().decode("utf-16le", errors="ignore").lstrip("\ufeff")
    settings: dict[str, str] = {}
    for line in text.splitlines():
        if "=" not in line or line.lstrip().startswith(";"):
            continue
        key, value = line.split("=", 1)
        settings[key.strip()] = value.strip()
    return settings


def parse_report(report: Path, case: CaseSpec, ini: Path, copied_report: Path) -> dict[str, object]:
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
        "equity_dd_amount": parse_first_number(cell(text, "Equity Drawdown Maximal:")),
        "equity_dd_pct": pct_in(cell(text, "Equity Drawdown Maximal:")),
        "balance_dd": cell(text, "Balance Drawdown Maximal:"),
        "balance_dd_amount": parse_first_number(cell(text, "Balance Drawdown Maximal:")),
        "balance_dd_pct": pct_in(cell(text, "Balance Drawdown Maximal:")),
        "largest_loss": parse_first_number(cell(text, "Largest loss trade:")),
        "largest_loss_abs": abs(parse_first_number(cell(text, "Largest loss trade:"))),
        "avg_loss": parse_first_number(cell(text, "Average loss trade:")),
        "max_consecutive_losses": cell(text, "Maximum consecutive losses ($):"),
        "max_consecutive_loss_count": int(parse_first_number(cell(text, "Maximum consecutive losses ($):"))),
        "on_tester": parse_first_number(cell(text, "OnTester result:")),
        "report": str(copied_report),
        "ini": str(ini),
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


def report_stem(case: CaseSpec) -> str:
    if case.stem_override:
        return case.stem_override
    start = case.window.from_date.replace(".", "")
    end = case.window.to_date.replace(".", "")
    return (
        f"InvictusForward8_LC_{case.expert.key}_{case.window.key}_d{case.deposit}USC_"
        f"{SYMBOL}_{PERIOD}_lev2000_delay{EXECUTION_MODE_MS}_model{MODEL}_{start}_{end}"
    )


def run_case(case: CaseSpec, timeout: int, destination: Path, *, force: bool = False) -> dict[str, object]:
    stem = report_stem(case)
    copied_report = destination / f"{stem}.htm"
    copied_ini = destination / f"{stem}.ini"
    if not force and copied_report.exists() and copied_report.stat().st_size > 0 and copied_ini.exists():
        return parse_report(copied_report, case, copied_ini, copied_report) | {"completed_before_timeout": True, "cached": True}
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
    shutil.copy2(ini, copied_ini)
    copy_report_artifacts(stem, destination)
    return parse_report(copied_report, case, copied_ini, copied_report) | {"completed_before_timeout": completed, "cached": False}


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
                value = (value or "").strip()
                if key in PARAM_TYPES:
                    row[key] = cast_param(key, value)
                else:
                    try:
                        row[key] = float(value)
                    except ValueError:
                        row[key] = value
            fingerprint = tuple(row.get(key, V2LIVE_DEFAULTS.get(key)) for key in V2LIVE_DEFAULTS)
            if fingerprint in seen:
                continue
            seen.add(fingerprint)
            rows.append(row)
    return rows


def load_existing_phase_outputs() -> list[dict[str, object]]:
    outputs: list[dict[str, object]] = []
    for item in WALK_FORWARD:
        phase = item["key"]
        csv_paths = sorted(OPT_DIR.glob(f"{phase}_{OPT_PASS_CSV}"))
        if not csv_paths:
            continue
        rows = read_optimization_rows(csv_paths)
        for row in rows:
            row["phase"] = phase
            row["train_window"] = item["train"].key
        outputs.append(
            {
                "phase": phase,
                "train": item["train"].__dict__,
                "validate": item["validate"].__dict__,
                "completed_before_timeout": "reused",
                "csv_artifacts": [str(path) for path in csv_paths],
                "opt_artifacts": [str(path) for path in sorted(OPT_DIR.glob(f"{phase}_*.opt"))],
                "rows": rows,
            }
        )
    return outputs


def run_optimization_phase(item: dict[str, object], timeout: int) -> dict[str, object]:
    phase = str(item["key"])
    train: WindowSpec = item["train"]  # type: ignore[assignment]
    existing = OPT_DIR / f"{phase}_{OPT_PASS_CSV}"
    if existing.exists() and existing.stat().st_size > 0:
        rows = read_optimization_rows([existing])
        for row in rows:
            row["phase"] = phase
            row["train_window"] = train.key
        return {
            "phase": phase,
            "train": train.__dict__,
            "validate": item["validate"].__dict__,  # type: ignore[index]
            "completed_before_timeout": "cached",
            "csv_artifacts": [str(existing)],
            "opt_artifacts": [str(path) for path in sorted(OPT_DIR.glob(f"{phase}_*.opt"))],
            "rows": rows,
        }
    clear_optimization_csvs()
    set_file = write_set(f"InvictusForward8_V2Live_{phase}_opt.set", V2LIVE_DEFAULTS, OPT_RANGES)
    stem = (
        f"InvictusForward8_LC_v2live_{phase}_genetic_d1000USC_"
        f"{SYMBOL}_{PERIOD}_{train.from_date.replace('.', '')}_{train.to_date.replace('.', '')}"
    )
    ini = tester_ini(
        expert=next(expert for expert in EXPERTS_TO_RUN if expert.key == "v2live"),
        stem=stem,
        from_date=train.from_date,
        to_date=train.to_date,
        deposit=1000,
        optimization=2,
        set_file=set_file,
    )
    shutil.copy2(ini, OPT_DIR / ini.name)
    before_opt = {path: path.stat().st_mtime for path in TESTER_CACHE.glob("*.opt")}
    completed = run_terminal_config(ini, timeout)
    time.sleep(3)
    csv_paths = find_optimization_csvs()
    copied_csvs: list[str] = []
    for path in csv_paths:
        target = OPT_DIR / f"{phase}_{path.name}"
        shutil.copy2(path, target)
        copied_csvs.append(str(target))
    opt_artifacts: list[str] = []
    for path in TESTER_CACHE.glob("*.opt"):
        if path not in before_opt or path.stat().st_mtime > before_opt.get(path, 0):
            target = OPT_DIR / f"{phase}_{path.name}"
            shutil.copy2(path, target)
            opt_artifacts.append(str(target))
    rows = read_optimization_rows([Path(path) for path in copied_csvs])
    for row in rows:
        row["phase"] = phase
        row["train_window"] = train.key
    return {
        "phase": phase,
        "train": train.__dict__,
        "validate": item["validate"].__dict__,  # type: ignore[index]
        "completed_before_timeout": completed,
        "csv_artifacts": copied_csvs,
        "opt_artifacts": opt_artifacts,
        "rows": rows,
    }


def candidate_values(row: dict[str, object]) -> dict[str, object]:
    values = dict(V2LIVE_DEFAULTS)
    for key in V2LIVE_DEFAULTS:
        if key in row:
            values[key] = row[key]
    return values


def candidate_fingerprint(row: dict[str, object]) -> tuple[object, ...]:
    values = candidate_values(row)
    return tuple(values[key] for key in V2LIVE_DEFAULTS)


def candidate_pool(phase_outputs: list[dict[str, object]], limit: int) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for output in phase_outputs:
        rows.extend(output["rows"])
    viable = [
        row for row in rows
        if float(row.get("profit", 0.0)) > 0.0
        and float(row.get("profit_factor", 0.0)) > 1.0
        and float(row.get("score", -1e9)) > -1e8
    ]
    rankings = [
        sorted(viable, key=lambda row: (float(row.get("score", 0.0)), float(row.get("profit_factor", 0.0))), reverse=True),
        sorted(viable, key=lambda row: (float(row.get("profit_factor", 0.0)), float(row.get("score", 0.0))), reverse=True),
        sorted(viable, key=lambda row: (float(row.get("equity_dd_pct", 999.0)), -float(row.get("score", 0.0)))),
        sorted(viable, key=lambda row: (float(row.get("recovery_factor", 0.0)), float(row.get("score", 0.0))), reverse=True),
    ]
    pool: list[dict[str, object]] = []
    seen: set[tuple[object, ...]] = set()
    for ranking in rankings:
        for row in ranking:
            fingerprint = candidate_fingerprint(row)
            if fingerprint in seen:
                continue
            seen.add(fingerprint)
            pool.append(row)
            if len(pool) >= limit:
                return pool
    return pool


def run_v1_validation_baselines(timeout: int) -> dict[str, dict[str, object]]:
    v1 = next(expert for expert in EXPERTS_TO_RUN if expert.key == "v1")
    baselines: dict[str, dict[str, object]] = {}
    for window in VALIDATION_WINDOWS:
        stem = f"InvictusForward8_LC_v1_baseline_{window.key}_d1000USC_{SYMBOL}_{PERIOD}_{window.from_date.replace('.', '')}_{window.to_date.replace('.', '')}"
        case = CaseSpec(v1, window, 1000, stem_override=stem)
        row = run_case(case, timeout, VAL_DIR)
        baselines[window.key] = row
    return baselines


def validation_score(row: dict[str, object]) -> float:
    net = float(row["net"])
    pf = float(row["profit_factor"])
    dd = float(row["equity_dd_pct"])
    trades = max(float(row["trades"]), 1.0)
    return (net * min(pf, 3.0) / (1.0 + dd)) * min(1.0, trades / 10.0)


def candidate_gate(candidate_rows: list[dict[str, object]], v1_baselines: dict[str, dict[str, object]]) -> tuple[bool, list[str], float]:
    reasons: list[str] = []
    scores: list[float] = []
    for row in candidate_rows:
        window_key = str(row["window_key"])
        v1 = v1_baselines[window_key]
        if row["validation_issues"]:
            reasons.append(f"{window_key}: validation {row['validation_issues']}")
        if float(row["net"]) <= 0.0:
            reasons.append(f"{window_key}: net <= 0")
        if float(row["profit_factor"]) < 1.15:
            reasons.append(f"{window_key}: PF < 1.15")
        if float(row["equity_dd_amount"]) > float(v1["equity_dd_amount"]) or float(row["equity_dd_pct"]) > float(v1["equity_dd_pct"]):
            reasons.append(f"{window_key}: equity DD > V1")
        if float(row["largest_loss_abs"]) > float(v1["largest_loss_abs"]):
            reasons.append(f"{window_key}: largest loss > V1")
        if int(row["max_consecutive_loss_count"]) > int(v1["max_consecutive_loss_count"]):
            reasons.append(f"{window_key}: max consecutive losses > V1")
        scores.append(validation_score(row))
    passed = not reasons and len(candidate_rows) == len(VALIDATION_WINDOWS)
    median_score = statistics.median(scores) if scores else -1e9
    return passed, reasons, median_score


def run_candidate_screen(candidates: list[dict[str, object]], v1_baselines: dict[str, dict[str, object]], timeout: int) -> tuple[dict[str, object] | None, list[dict[str, object]]]:
    v2live = next(expert for expert in EXPERTS_TO_RUN if expert.key == "v2live")
    screen: list[dict[str, object]] = []
    selected: dict[str, object] | None = None
    for index, candidate in enumerate(candidates, start=1):
        values = candidate_values(candidate)
        set_file = write_set(f"InvictusForward8_V2Live_candidate_{index:03d}.set", values)
        rows: list[dict[str, object]] = []
        for window in VALIDATION_WINDOWS:
            stem = (
                f"InvictusForward8_LC_v2live_candidate_{index:03d}_{window.key}_d1000USC_"
                f"{SYMBOL}_{PERIOD}_{window.from_date.replace('.', '')}_{window.to_date.replace('.', '')}"
            )
            case = CaseSpec(v2live, window, 1000, set_file=set_file, stem_override=stem)
            rows.append(run_case(case, timeout, VAL_DIR))
        passed, reasons, median_score = candidate_gate(rows, v1_baselines)
        record = {
            "candidate_index": index,
            "optimizer": candidate,
            "values": values,
            "set": str(set_file),
            "validation_rows": rows,
            "passed": passed,
            "fail_reasons": sorted(set(reasons)),
            "median_validation_score": median_score,
        }
        screen.append(record)
        best_net = min(float(row["net"]) for row in rows) if rows else 0.0
        best_pf = min(float(row["profit_factor"]) for row in rows) if rows else 0.0
        print(f"candidate {index:03d} pass={passed} min_net={best_net:.2f} min_pf={best_pf:.2f}", flush=True)
        if passed and (selected is None or median_score > float(selected["median_validation_score"])):
            selected = record
    return selected, screen


def selected_or_rejected_set(selected: dict[str, object] | None) -> tuple[Path, bool]:
    selected_path = SETS_DIR / "InvictusForward8_V2Live_selected.set"
    if selected:
        set_file = write_set("InvictusForward8_V2Live_selected.set", selected["values"])  # type: ignore[arg-type]
        shutil.copy2(set_file, OPT_DIR / set_file.name)
        return set_file, True
    if selected_path.exists():
        selected_path.unlink()
    opt_selected = OPT_DIR / selected_path.name
    if opt_selected.exists():
        opt_selected.unlink()
    rejected = write_set("InvictusForward8_V2Live_rejected_default.set", V2LIVE_DEFAULTS)
    return rejected, False


def run_final_confirmation(set_file: Path, timeout: int) -> list[dict[str, object]]:
    results: list[dict[str, object]] = []
    requested_experts = EXPERTS_TO_RUN
    for deposit in DEPOSITS:
        for window in CONFIRM_WINDOWS:
            for expert in requested_experts:
                case_set = set_file if expert.key == "v2live" else None
                case = CaseSpec(expert, window, deposit, set_file=case_set)
                print(f"run {expert.label} {window.key} d{deposit}", flush=True)
                row = run_case(case, timeout, CONF_DIR)
                issues = ",".join(row["validation_issues"]) if row["validation_issues"] else "OK"
                print(
                    f"done {expert.label} {window.key} d{deposit} "
                    f"net={row['net']:.2f} pf={row['profit_factor']:.2f} trades={row['trades']} validation={issues}",
                    flush=True,
                )
                results.append(row)
                write_json_reports(results, [], {}, None)
    return results


def build_comparisons(results: list[dict[str, object]]) -> list[dict[str, object]]:
    by_key: dict[tuple[int, str], list[dict[str, object]]] = {}
    for row in results:
        by_key.setdefault((int(row["deposit"]), str(row["window_key"])), []).append(row)
    comparisons: list[dict[str, object]] = []
    window_order = {window.key: index for index, window in enumerate(CONFIRM_WINDOWS)}
    for key in sorted(by_key, key=lambda item: (item[0], window_order.get(item[1], 99))):
        rows = by_key[key]
        by_expert = {str(row["expert_key"]): row for row in rows}
        if not {"base", "v1", "v2live"}.issubset(by_expert):
            continue
        winner = max(rows, key=lambda row: float(row["net"]))
        v1 = by_expert["v1"]
        v2 = by_expert["v2live"]
        v2_dd_worse = (
            float(v2["equity_dd_amount"]) > float(v1["equity_dd_amount"])
            or float(v2["equity_dd_pct"]) > float(v1["equity_dd_pct"])
        )
        note = ""
        if winner["expert_key"] == "v2live" and v2_dd_worse:
            note = "profit winner, not live-ready"
        elif v2_dd_worse:
            note = "V2Live DD worse than V1"
        comparisons.append(
            {
                "deposit": key[0],
                "window_key": key[1],
                "window": str(rows[0]["window"]),
                "result_winner": str(winner["expert"]),
                "v2live_live_ready_by_dd": not v2_dd_worse,
                "note": note,
                "base_net": by_expert["base"]["net"],
                "base_pf": by_expert["base"]["profit_factor"],
                "base_eqdd": by_expert["base"]["equity_dd"],
                "v1_net": v1["net"],
                "v1_pf": v1["profit_factor"],
                "v1_eqdd": v1["equity_dd"],
                "v2live_net": v2["net"],
                "v2live_pf": v2["profit_factor"],
                "v2live_eqdd": v2["equity_dd"],
            }
        )
    return comparisons


def live_ready_gate(results: list[dict[str, object]], selected_exists: bool) -> tuple[bool, list[str]]:
    if not selected_exists:
        return False, ["no candidate passed walk-forward validation gates"]
    by_key = {(str(row["expert_key"]), int(row["deposit"]), str(row["window_key"])): row for row in results}
    reasons: list[str] = []
    for window_key in ("oos_may", "last_month"):
        row = by_key.get(("v2live", 1000, window_key))
        v1 = by_key.get(("v1", 1000, window_key))
        if not row or not v1:
            reasons.append(f"{window_key}: missing final result")
            continue
        if float(row["net"]) <= 0.0:
            reasons.append(f"{window_key}: net <= 0")
        if float(row["profit_factor"]) < 1.20:
            reasons.append(f"{window_key}: PF < 1.20")
        if float(row["equity_dd_amount"]) > float(v1["equity_dd_amount"]) or float(row["equity_dd_pct"]) > float(v1["equity_dd_pct"]):
            reasons.append(f"{window_key}: equity DD > V1")
        if float(row["largest_loss_abs"]) > float(v1["largest_loss_abs"]):
            reasons.append(f"{window_key}: largest loss > V1")
        if int(row["max_consecutive_loss_count"]) > int(v1["max_consecutive_loss_count"]):
            reasons.append(f"{window_key}: max consecutive losses > V1")
    ytd = by_key.get(("v2live", 1000, "ytd_2026"))
    v1_ytd = by_key.get(("v1", 1000, "ytd_2026"))
    if ytd and v1_ytd:
        lower_profit_lower_dd = (
            float(ytd["net"]) >= 0.80 * float(v1_ytd["net"])
            and float(ytd["equity_dd_amount"]) <= 0.70 * float(v1_ytd["equity_dd_amount"])
            and float(ytd["equity_dd_pct"]) <= 0.70 * float(v1_ytd["equity_dd_pct"])
        )
        equal_profit_equal_dd = (
            float(ytd["net"]) >= float(v1_ytd["net"])
            and float(ytd["equity_dd_amount"]) <= float(v1_ytd["equity_dd_amount"])
            and float(ytd["equity_dd_pct"]) <= float(v1_ytd["equity_dd_pct"])
        )
        if not (lower_profit_lower_dd or equal_profit_equal_dd):
            reasons.append("ytd_2026: fails profit/DD live gate")
    else:
        reasons.append("ytd_2026: missing final result")
    return not reasons, reasons


def write_json_reports(
    results: list[dict[str, object]],
    comparisons: list[dict[str, object]],
    live_ready: dict[str, object],
    selected: dict[str, object] | None,
) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    (REPORT_DIR / "results.json").write_text(json.dumps(results, indent=2, default=str) + "\n")
    (REPORT_DIR / "comparison.json").write_text(json.dumps(comparisons, indent=2, default=str) + "\n")
    (REPORT_DIR / "live_ready.json").write_text(json.dumps(live_ready, indent=2, default=str) + "\n")
    (REPORT_DIR / "selected_candidate.json").write_text(json.dumps(selected, indent=2, default=str) + "\n")


def write_param_diff(selected_values: dict[str, object] | None) -> None:
    lines = [
        "# V1 vs V2Live Parameter Diff",
        "",
        "V2Live starts from V1 and uses a cent-account micro-risk profile.",
        "",
        "| Parameter | V1 Default | V2Live Value | Changed |",
        "| --- | ---: | ---: | --- |",
    ]
    values = selected_values or V2LIVE_DEFAULTS
    for name in V1_DEFAULTS:
        v1 = V1_DEFAULTS[name]
        v2 = values.get(name, v1)
        lines.append(f"| {name} | {set_value(v1)} | {set_value(v2)} | {'yes' if v1 != v2 else ''} |")
    (REPORT_DIR / "PARAM_DIFF_V1_V2LIVE.md").write_text("\n".join(lines) + "\n")


def write_code_diff() -> None:
    base = (SRC_ROOT / "base" / "InvictusForward-8.mq5").read_text(errors="ignore").splitlines()
    v1 = (SRC_ROOT / "v1" / "InvictusForward-8-Tuned.mq5").read_text(errors="ignore").splitlines()
    v2 = (SRC_ROOT / "v2live" / "InvictusForward-8-V2Live.mq5").read_text(errors="ignore").splitlines()
    base_v1 = list(difflib.unified_diff(base, v1, fromfile="Base/InvictusForward-8.mq5", tofile="V1/InvictusForward-8-Tuned.mq5", lineterm=""))
    v1_v2 = list(difflib.unified_diff(v1, v2, fromfile="V1/InvictusForward-8-Tuned.mq5", tofile="V2Live/InvictusForward-8-V2Live.mq5", lineterm=""))
    lines = [
        "# Base vs V1 vs V2Live Code/Logic Diff",
        "",
        "## Summary",
        "",
        "- Base is the untouched source from the zip.",
        "- V1 is the first tuned research guardrail profile.",
        "- V2Live starts from V1, lowers cent-account exposure, adds module-specific order comments, and exports a risk-adjusted native `OnTester()` score.",
        "",
        "## Base -> V1 Unified Diff",
        "",
        "```diff",
        *base_v1[:500],
        "```",
        "",
        "## V1 -> V2Live Unified Diff",
        "",
        "```diff",
        *v1_v2[:500],
        "```",
    ]
    (REPORT_DIR / "CODE_DIFF.md").write_text("\n".join(lines) + "\n")


def write_walk_forward(phase_outputs: list[dict[str, object]], v1_baselines: dict[str, dict[str, object]], screen: list[dict[str, object]], selected: dict[str, object] | None) -> None:
    (REPORT_DIR / "walk_forward.json").write_text(
        json.dumps(
            {
                "phases": [{k: v for k, v in output.items() if k != "rows"} | {"row_count": len(output["rows"])} for output in phase_outputs],
                "v1_validation_baselines": v1_baselines,
                "candidate_count": len(screen),
                "selected_candidate_index": selected["candidate_index"] if selected else None,
            },
            indent=2,
            default=str,
        )
        + "\n"
    )
    (REPORT_DIR / "candidate_screen.json").write_text(json.dumps(screen, indent=2, default=str) + "\n")
    lines = [
        "# V2Live Walk-Forward",
        "",
        "Native MT5 optimization was run per train window, then candidates were validated on Mar, Apr, and May using `.htm` reports.",
        "",
        "## Optimization Phases",
        "",
        "| Phase | Train | Validation | Completed | Pass Rows |",
        "| --- | --- | --- | --- | ---: |",
    ]
    for output in phase_outputs:
        train = output["train"]
        validate = output["validate"]
        lines.append(
            f"| {output['phase']} | {train['from_date']} to {train['to_date']} | "
            f"{validate['from_date']} to {validate['to_date']} | {output['completed_before_timeout']} | {len(output['rows'])} |"
        )
    lines.extend(
        [
            "",
            "## V1 Validation Baselines",
            "",
            "| Window | Net | PF | Eq DD | Largest Loss | Max Consecutive Losses |",
            "| --- | ---: | ---: | --- | ---: | --- |",
        ]
    )
    for key, row in v1_baselines.items():
        lines.append(
            f"| {key} | {row['net']:.2f} | {row['profit_factor']:.2f} | {row['equity_dd']} | "
            f"{row['largest_loss']:.2f} | {row['max_consecutive_losses']} |"
        )
    passed = [row for row in screen if row["passed"]]
    lines.extend(
        [
            "",
            "## Candidate Gate",
            "",
            f"Screened candidates: `{len(screen)}`. Passed all gates: `{len(passed)}`.",
            f"Selected candidate: `{selected['candidate_index'] if selected else 'none'}`.",
            "",
            "| Candidate | Passed | Median Score | Fail Reasons |",
            "| ---: | --- | ---: | --- |",
        ]
    )
    for row in screen[:150]:
        reasons = "; ".join(row["fail_reasons"][:6])
        if len(row["fail_reasons"]) > 6:
            reasons += "; ..."
        lines.append(f"| {row['candidate_index']} | {row['passed']} | {row['median_validation_score']:.4f} | {reasons} |")
    (REPORT_DIR / "WALK_FORWARD.md").write_text("\n".join(lines) + "\n")


def classify_module(comment: str) -> str:
    if "IF8V3G_DC" in comment or "IF8V2L_DC" in comment or "DropCatch" in comment:
        return "DropCatcher"
    if "IF8V3G_RB" in comment or "IF8V2L_RB" in comment or "IHS RB" in comment:
        return "RangeBounce"
    if "IF8V3G_TR" in comment or "IF8V2L_TR" in comment or "IHB S:" in comment:
        return "Trend"
    return "Unknown"


def write_trade_diagnosis(results: list[dict[str, object]]) -> None:
    diagnosis: list[dict[str, object]] = []
    for row in results:
        report = Path(str(row["report"]))
        if not report.exists():
            continue
        trades, unmatched = reconstruct_closed_trades(extract_deal_rows(read_report(report)))
        for trade in trades:
            diagnosis.append(
                {
                    "expert": row["expert"],
                    "deposit": row["deposit"],
                    "window": row["window_key"],
                    "module": classify_module(trade.entry_comment or trade.exit_comment),
                    "entry_hour": trade.entry_time.hour,
                    "profit": trade.profit,
                    "volume": trade.volume,
                    "entry_comment": trade.entry_comment,
                    "exit_comment": trade.exit_comment,
                    "hold_minutes": trade.hold_minutes,
                }
            )
    (REPORT_DIR / "trade_diagnosis.json").write_text(json.dumps(diagnosis, indent=2, default=str) + "\n")
    v2_1000 = [row for row in diagnosis if row["expert"] == "V2Live" and int(row["deposit"]) == 1000]
    by_module: dict[str, dict[str, float]] = {}
    by_hour: dict[int, dict[str, float]] = {}
    for trade in v2_1000:
        module = str(trade["module"])
        hour = int(trade["entry_hour"])
        for bucket in (by_module.setdefault(module, {"trades": 0, "net": 0.0, "losses": 0}), by_hour.setdefault(hour, {"trades": 0, "net": 0.0, "losses": 0})):
            bucket["trades"] += 1
            bucket["net"] += float(trade["profit"])
            if float(trade["profit"]) < 0:
                bucket["losses"] += 1
    largest = sorted(v2_1000, key=lambda row: float(row["profit"]))[:20]
    lines = [
        "# V2Live Trade Diagnosis",
        "",
        "Diagnosis uses closed trades reconstructed from native MT5 `.htm` deal tables. Focus below is V2Live deposit 1000.",
        "",
        "## By Module",
        "",
        "| Module | Trades | Net | Losses |",
        "| --- | ---: | ---: | ---: |",
    ]
    for module, bucket in sorted(by_module.items(), key=lambda item: item[1]["net"]):
        lines.append(f"| {module} | {int(bucket['trades'])} | {bucket['net']:.2f} | {int(bucket['losses'])} |")
    lines.extend(["", "## Worst Entry Hours", "", "| Hour | Trades | Net | Losses |", "| ---: | ---: | ---: | ---: |"])
    for hour, bucket in sorted(by_hour.items(), key=lambda item: item[1]["net"])[:12]:
        lines.append(f"| {hour} | {int(bucket['trades'])} | {bucket['net']:.2f} | {int(bucket['losses'])} |")
    lines.extend(["", "## Largest Losses", "", "| Window | Time Hour | Module | Profit | Comment |", "| --- | ---: | --- | ---: | --- |"])
    for trade in largest:
        lines.append(
            f"| {trade['window']} | {trade['entry_hour']} | {trade['module']} | {float(trade['profit']):.2f} | {trade['entry_comment']} |"
        )
    (REPORT_DIR / "TRADE_DIAGNOSIS.md").write_text("\n".join(lines) + "\n")


def write_summary(results: list[dict[str, object]], comparisons: list[dict[str, object]], live_ready: dict[str, object], selected: dict[str, object] | None) -> None:
    expert_order = {"base": 0, "v1": 1, "v2live": 2}
    window_order = {window.key: index for index, window in enumerate(CONFIRM_WINDOWS)}
    lines = [
        "# Invictus Forward-8 V2Live Candidate",
        "",
        "Source of truth: native MT5 Strategy Tester reports generated through `terminal64.exe /config`.",
        "",
        f"Setup: account `{LOGIN}` on `{SERVER}`, `{SYMBOL}` `{PERIOD}`, currency `{CURRENCY}`, leverage `{LEVERAGE}`, `Model={MODEL}`, `ExecutionMode={EXECUTION_MODE_MS}`, `UseLocal=1`, `UseRemote=0`, `UseCloud=0`.",
        "",
        "All optimization, validation, and confirmation windows are 2026+ only. No 2025 result is used.",
        "",
        f"Selected candidate: `{selected['candidate_index'] if selected else 'none'}`.",
        f"Live-ready: `{live_ready['live_ready']}`.",
        f"Decision: `{live_ready['decision']}`.",
        "",
        "## All Confirmation Runs",
        "",
        "| Expert | Deposit | Window | Net | PF | Trades | WR | Eq DD | Balance DD | Largest Loss | Max Consecutive Losses | History | Validation |",
        "| --- | ---: | --- | ---: | ---: | ---: | ---: | --- | --- | ---: | --- | --- | --- |",
    ]
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
            "| Deposit | Window | Base Net/PF/DD | V1 Net/PF/DD | V2Live Net/PF/DD | Result Winner | V2Live DD OK | Note |",
            "| ---: | --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for row in comparisons:
        lines.append(
            "| {deposit} USC | {window} | {base_net:.2f} / {base_pf:.2f} / {base_eqdd} | {v1_net:.2f} / {v1_pf:.2f} / {v1_eqdd} | {v2live_net:.2f} / {v2live_pf:.2f} / {v2live_eqdd} | {result_winner} | {v2live_live_ready_by_dd} | {note} |".format(
                **row
            )
        )
    lines.extend(["", "## Live-Ready Gate", "", "| Status | Detail |", "| --- | --- |"])
    if live_ready["reasons"]:
        for reason in live_ready["reasons"]:
            lines.append(f"| fail | {reason} |")
    else:
        lines.append("| pass | all configured gates passed |")
    lines.extend(["", "## Recommendation", "", str(live_ready["decision"])])
    (REPORT_DIR / "SUMMARY.md").write_text("\n".join(lines) + "\n")


APRIL_WINDOW = WindowSpec("validate_apr", "Validate Apr", "2026.04.01", "2026.04.30")
V3_VALIDATION_WINDOWS = [
    WindowSpec("validate_mar", "Validate Mar", "2026.03.01", "2026.03.31"),
    APRIL_WINDOW,
    WindowSpec("validate_may", "Validate May", "2026.05.01", "2026.05.10"),
]


def with_v3(overrides: dict[str, object]) -> dict[str, object]:
    values = dict(V3_DEFAULTS)
    values.update(overrides)
    return values


V3_VARIANTS: list[dict[str, object]] = [
    {
        "key": "trend_only_v2rules",
        "label": "Trend only, V2 rules",
        "purpose": "Isolate Trend logic without the new April guards.",
        "values": with_v3({
            "BT_EnableSideways": False,
            "EnableDropCatcher": False,
            "Guard_EnableTrendFillHourFilter": False,
            "Guard_TrendMinScoreAdd": 0,
            "Guard_TrendLossCooldownBars": 2,
            "Guard_MaxTrendDailyLossCount": 5,
            "Guard_MaxTrendPosLowBalance": 2,
        }),
    },
    {
        "key": "range_only",
        "label": "RangeBounce only",
        "purpose": "Isolate RangeBounce contribution.",
        "values": with_v3({
            "BT_EnableTrending": False,
            "BT_EnableSideways": True,
            "EnableDropCatcher": False,
        }),
    },
    {
        "key": "drop_only",
        "label": "DropCatcher only",
        "purpose": "Isolate DropCatcher contribution.",
        "values": with_v3({
            "BT_EnableTrending": False,
            "BT_EnableSideways": False,
            "EnableDropCatcher": True,
        }),
    },
    {
        "key": "pending_guard_only",
        "label": "Pending fill-hour guard only",
        "purpose": "Cancel/avoid Trend pending fills in observed loss-cluster hours without score tightening.",
        "values": with_v3({
            "Guard_EnableTrendFillHourFilter": True,
            "Guard_TrendMinScoreAdd": 0,
            "Guard_TrendLossCooldownBars": 2,
            "Guard_MaxTrendDailyLossCount": 5,
            "Guard_MaxTrendPosLowBalance": 2,
        }),
    },
    {
        "key": "score90_only",
        "label": "Trend score +10 only",
        "purpose": "Raise Trend threshold to reduce S85 entries without extra fill-hour guard.",
        "values": with_v3({
            "Guard_EnableTrendFillHourFilter": False,
            "Guard_TrendMinScoreAdd": 10,
            "Guard_TrendLossCooldownBars": 2,
            "Guard_MaxTrendDailyLossCount": 5,
            "Guard_MaxTrendPosLowBalance": 2,
        }),
    },
    {
        "key": "v3_default",
        "label": "V3 default April guard",
        "purpose": "Fill-hour guard + score +10 + stricter daily loss count + one Trend position at 1000 USC.",
        "values": V3_DEFAULTS,
    },
    {
        "key": "v3_imp_only",
        "label": "V3 default + IMP only",
        "purpose": "Reject corrective Trend setups on top of V3 default.",
        "values": with_v3({"Guard_AllowTrendCorrective": False}),
    },
    {
        "key": "v3_micro",
        "label": "V3 micro-risk",
        "purpose": "V3 default with half Trend size for 1000 USC survival testing.",
        "values": with_v3({"Trend_LotMult": 0.5}),
    },
]


def run_baseline_validation(timeout: int) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for expert_key in ("v1", "v2live"):
        expert = next(item for item in EXPERTS_TO_RUN if item.key == expert_key)
        for window in V3_VALIDATION_WINDOWS:
            stem = (
                f"InvictusForward8_V3AG_{expert.key}_baseline_{window.key}_d1000USC_"
                f"{SYMBOL}_{PERIOD}_{window.from_date.replace('.', '')}_{window.to_date.replace('.', '')}"
            )
            rows.append(run_case(CaseSpec(expert, window, 1000, stem_override=stem), timeout, VAL_DIR))
    return rows


def run_v3_variant_validation(timeout: int) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    expert = next(item for item in EXPERTS_TO_RUN if item.key == "v3guard")
    rows: list[dict[str, object]] = []
    variants: list[dict[str, object]] = []
    for variant in V3_VARIANTS:
        key = str(variant["key"])
        values = dict(variant["values"])  # type: ignore[arg-type]
        set_file = write_set(f"InvictusForward8_V3Guard_{key}.set", values)
        record = {k: v for k, v in variant.items() if k != "values"} | {"set": str(set_file), "values": values}
        variants.append(record)
        for window in V3_VALIDATION_WINDOWS:
            stem = (
                f"InvictusForward8_V3AG_v3guard_{key}_{window.key}_d1000USC_"
                f"{SYMBOL}_{PERIOD}_{window.from_date.replace('.', '')}_{window.to_date.replace('.', '')}"
            )
            print(f"run V3 {key} {window.key}", flush=True)
            row = run_case(CaseSpec(expert, window, 1000, set_file=set_file, stem_override=stem), timeout, VAL_DIR)
            row["variant_key"] = key
            row["variant_label"] = variant["label"]
            rows.append(row)
            issues = ",".join(row["validation_issues"]) if row["validation_issues"] else "OK"
            print(
                f"done V3 {key} {window.key} net={row['net']:.2f} pf={row['profit_factor']:.2f} "
                f"trades={row['trades']} dd={row['equity_dd_pct']:.2f}% validation={issues}",
                flush=True,
            )
    return variants, rows


def validation_by_key(rows: list[dict[str, object]]) -> dict[tuple[str, str], dict[str, object]]:
    output: dict[tuple[str, str], dict[str, object]] = {}
    for row in rows:
        expert_key = str(row.get("variant_key") or row["expert_key"])
        output[(expert_key, str(row["window_key"]))] = row
    return output


def score_variant(key: str, rows_by_key: dict[tuple[str, str], dict[str, object]], v1_by_window: dict[str, dict[str, object]]) -> dict[str, object]:
    mar = rows_by_key[(key, "validate_mar")]
    apr = rows_by_key[(key, "validate_apr")]
    may = rows_by_key[(key, "validate_may")]
    v1_apr = v1_by_window["validate_apr"]
    v1_mar = v1_by_window["validate_mar"]
    v1_may = v1_by_window["validate_may"]
    reasons: list[str] = []
    if float(apr["net"]) <= float(v1_apr["net"]):
        reasons.append("April net not better than V1")
    if float(apr["profit_factor"]) < float(v1_apr["profit_factor"]):
        reasons.append("April PF worse than V1")
    if int(apr["max_consecutive_loss_count"]) > int(v1_apr["max_consecutive_loss_count"]):
        reasons.append("April max consecutive losses worse than V1")
    if float(apr["equity_dd_pct"]) > float(v1_apr["equity_dd_pct"]):
        reasons.append("April equity DD pct worse than V1")
    if float(mar["net"]) <= 0.0:
        reasons.append("March net <= 0")
    if float(may["net"]) <= 0.0:
        reasons.append("May net <= 0")
    if float(mar["equity_dd_pct"]) > float(v1_mar["equity_dd_pct"]) or float(may["equity_dd_pct"]) > float(v1_may["equity_dd_pct"]):
        reasons.append("Mar/May DD worse than V1")
    strict_live = (
        not reasons
        and float(apr["net"]) > 0.0
        and float(apr["profit_factor"]) >= 1.15
        and float(mar["profit_factor"]) >= 1.15
        and float(may["profit_factor"]) >= 1.15
    )
    aggregate_net = float(mar["net"]) + float(apr["net"]) + float(may["net"])
    min_net = min(float(mar["net"]), float(apr["net"]), float(may["net"]))
    max_dd = max(float(mar["equity_dd_pct"]), float(apr["equity_dd_pct"]), float(may["equity_dd_pct"]))
    score = aggregate_net + max(0.0, float(apr["net"]) - float(v1_apr["net"])) * 3.0 - max_dd * 10.0
    return {
        "variant_key": key,
        "passed_relative_gate": not reasons,
        "strict_live_candidate": strict_live,
        "fail_reasons": reasons,
        "aggregate_net": aggregate_net,
        "min_net": min_net,
        "max_equity_dd_pct": max_dd,
        "score": score,
        "apr_net": apr["net"],
        "apr_pf": apr["profit_factor"],
        "apr_equity_dd": apr["equity_dd"],
        "apr_max_consecutive_losses": apr["max_consecutive_losses"],
    }


def select_best_variant(variants: list[dict[str, object]], validation_rows: list[dict[str, object]], baseline_rows: list[dict[str, object]]) -> dict[str, object]:
    rows_by_key = validation_by_key(validation_rows)
    v1_by_window = {str(row["window_key"]): row for row in baseline_rows if row["expert_key"] == "v1"}
    scored = [score_variant(str(variant["key"]), rows_by_key, v1_by_window) for variant in variants]
    for score in scored:
        variant = next(item for item in variants if item["key"] == score["variant_key"])
        score["label"] = variant["label"]
        score["set"] = variant["set"]
        score["values"] = variant["values"]
    relative_pass = [row for row in scored if row["passed_relative_gate"]]
    pool = relative_pass or scored
    selected = sorted(pool, key=lambda row: (bool(row["passed_relative_gate"]), float(row["score"]), float(row["apr_net"])), reverse=True)[0]
    return {"selected": selected, "scores": scored}


def run_selected_final(selected: dict[str, object], timeout: int) -> list[dict[str, object]]:
    expert = next(item for item in EXPERTS_TO_RUN if item.key == "v3guard")
    set_file = Path(str(selected["set"]))
    rows: list[dict[str, object]] = []
    for deposit in DEPOSITS:
        for window in CONFIRM_WINDOWS:
            stem = (
                f"InvictusForward8_V3AG_v3guard_selected_{selected['variant_key']}_{window.key}_d{deposit}USC_"
                f"{SYMBOL}_{PERIOD}_{window.from_date.replace('.', '')}_{window.to_date.replace('.', '')}"
            )
            print(f"run selected V3 {selected['variant_key']} {window.key} d{deposit}", flush=True)
            row = run_case(CaseSpec(expert, window, deposit, set_file=set_file, stem_override=stem), timeout, CONF_DIR)
            row["variant_key"] = selected["variant_key"]
            row["variant_label"] = selected["label"]
            rows.append(row)
            issues = ",".join(row["validation_issues"]) if row["validation_issues"] else "OK"
            print(
                f"done selected V3 {window.key} d{deposit} net={row['net']:.2f} pf={row['profit_factor']:.2f} "
                f"trades={row['trades']} dd={row['equity_dd_pct']:.2f}% validation={issues}",
                flush=True,
            )
    return rows


def rows_table(rows: list[dict[str, object]], include_variant: bool = False) -> list[str]:
    lines = [
        "| Variant/Expert | Window | Net | PF | Trades | Win Rate | Eq DD | Largest Loss | Max Consecutive Losses | History |",
        "| --- | --- | ---: | ---: | ---: | ---: | --- | ---: | --- | --- |",
    ]
    for row in rows:
        name = str(row.get("variant_label") or row["expert"])
        lines.append(
            f"| {name} | {row['window']} | {float(row['net']):.2f} | {float(row['profit_factor']):.2f} | "
            f"{row['trades']} | {float(row['win_rate_pct']):.2f}% | {row['equity_dd']} | "
            f"{float(row['largest_loss']):.2f} | {row['max_consecutive_losses']} | {row['history_quality']} |"
        )
    return lines


def diagnose_trades(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    diagnosis: list[dict[str, object]] = []
    for row in rows:
        report = Path(str(row["report"]))
        if not report.exists():
            continue
        trades, _ = reconstruct_closed_trades(extract_deal_rows(read_report(report)))
        for trade in trades:
            diagnosis.append(
                {
                    "expert": row.get("variant_label") or row["expert"],
                    "expert_key": row.get("variant_key") or row["expert_key"],
                    "window": row["window_key"],
                    "deposit": row["deposit"],
                    "module": classify_module(trade.entry_comment or trade.exit_comment),
                    "entry_hour": trade.entry_time.hour,
                    "profit": trade.profit,
                    "volume": trade.volume,
                    "entry_comment": trade.entry_comment,
                    "exit_comment": trade.exit_comment,
                    "hold_minutes": trade.hold_minutes,
                }
            )
    return diagnosis


def write_v3_reports(
    baseline_rows: list[dict[str, object]],
    variants: list[dict[str, object]],
    validation_rows: list[dict[str, object]],
    selection: dict[str, object],
    final_rows: list[dict[str, object]],
) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    diagnosis = diagnose_trades(baseline_rows + validation_rows + final_rows)
    selected = selection["selected"]
    scores = selection["scores"]
    (REPORT_DIR / "baseline_validation.json").write_text(json.dumps(baseline_rows, indent=2, default=str) + "\n")
    (REPORT_DIR / "variants.json").write_text(json.dumps(variants, indent=2, default=str) + "\n")
    (REPORT_DIR / "validation_results.json").write_text(json.dumps(validation_rows, indent=2, default=str) + "\n")
    (REPORT_DIR / "variant_scores.json").write_text(json.dumps(scores, indent=2, default=str) + "\n")
    (REPORT_DIR / "selected_variant.json").write_text(json.dumps(selected, indent=2, default=str) + "\n")
    (REPORT_DIR / "final_results.json").write_text(json.dumps(final_rows, indent=2, default=str) + "\n")
    (REPORT_DIR / "trade_diagnosis.json").write_text(json.dumps(diagnosis, indent=2, default=str) + "\n")

    apr_rows = [row for row in baseline_rows + validation_rows if row["window_key"] == "validate_apr"]
    lines = [
        "# April Failure Diagnosis",
        "",
        "Source of truth: native MT5 Strategy Tester `.htm` reports. Local runs use `AllowLiveTrading=0`; this experiment does not enable live Algo Trading.",
        "",
        "## April Validation Table",
        "",
        *rows_table(apr_rows),
        "",
        "## April Loss By Variant And Module",
        "",
        "| Variant/Expert | Module | Trades | Net | Losses |",
        "| --- | --- | ---: | ---: | ---: |",
    ]
    apr_diag = [row for row in diagnosis if row["window"] == "validate_apr" and int(row["deposit"]) == 1000]
    buckets: dict[tuple[str, str], dict[str, float]] = {}
    for row in apr_diag:
        key = (str(row["expert"]), str(row["module"]))
        bucket = buckets.setdefault(key, {"trades": 0, "net": 0.0, "losses": 0})
        bucket["trades"] += 1
        bucket["net"] += float(row["profit"])
        if float(row["profit"]) < 0:
            bucket["losses"] += 1
    for (expert, module), bucket in sorted(buckets.items(), key=lambda item: (item[0][0], item[1]["net"])):
        lines.append(f"| {expert} | {module} | {int(bucket['trades'])} | {bucket['net']:.2f} | {int(bucket['losses'])} |")
    lines.extend(["", "## Worst April Hours", "", "| Variant/Expert | Hour | Trades | Net | Losses |", "| --- | ---: | ---: | ---: | ---: |"])
    hour_buckets: dict[tuple[str, int], dict[str, float]] = {}
    for row in apr_diag:
        key = (str(row["expert"]), int(row["entry_hour"]))
        bucket = hour_buckets.setdefault(key, {"trades": 0, "net": 0.0, "losses": 0})
        bucket["trades"] += 1
        bucket["net"] += float(row["profit"])
        if float(row["profit"]) < 0:
            bucket["losses"] += 1
    for (expert, hour), bucket in sorted(hour_buckets.items(), key=lambda item: item[1]["net"])[:30]:
        lines.append(f"| {expert} | {hour} | {int(bucket['trades'])} | {bucket['net']:.2f} | {int(bucket['losses'])} |")
    (REPORT_DIR / "APRIL_DIAGNOSIS.md").write_text("\n".join(lines) + "\n")

    ablation_lines = [
        "# V3 Module Ablation And Guard Matrix",
        "",
        "All rows below are native MT5 `.htm` validation runs on 1000 USC.",
        "",
        *rows_table(validation_rows),
        "",
        "## Variant Gate Scores",
        "",
        "| Variant | Relative Gate | Strict Live | Score | Aggregate Net | Min Net | Max Eq DD % | April Net | April PF | Fail Reasons |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in sorted(scores, key=lambda item: float(item["score"]), reverse=True):
        ablation_lines.append(
            f"| {row['label']} | {row['passed_relative_gate']} | {row['strict_live_candidate']} | "
            f"{float(row['score']):.2f} | {float(row['aggregate_net']):.2f} | {float(row['min_net']):.2f} | "
            f"{float(row['max_equity_dd_pct']):.2f} | {float(row['apr_net']):.2f} | {float(row['apr_pf']):.2f} | "
            f"{'; '.join(row['fail_reasons'])} |"
        )
    (REPORT_DIR / "ABLATION.md").write_text("\n".join(ablation_lines) + "\n")

    summary_lines = [
        "# Invictus Forward-8 V3 April Guard",
        "",
        "V3 is an April-failure guard experiment, not a live deployment package.",
        "",
        f"Selected diagnostic variant: `{selected['label']}` (`{selected['variant_key']}`).",
        f"Relative gate passed: `{selected['passed_relative_gate']}`.",
        f"Strict live candidate: `{selected['strict_live_candidate']}`.",
        "",
        "## Decision",
        "",
    ]
    if selected["strict_live_candidate"]:
        summary_lines.append("V3 produced a strict validation candidate, but it still needs final forward testing before live use.")
    elif selected["passed_relative_gate"]:
        summary_lines.append("V3 improved the relative April/V1 gate, but it is not yet a strict live candidate.")
    else:
        summary_lines.append("No V3 variant fixed April enough to be live-ready. Continue with logic-level changes before any optimization.")
    summary_lines.extend(
        [
            "",
            "## Baseline Validation",
            "",
            *rows_table(baseline_rows),
            "",
            "## V3 Validation",
            "",
            *rows_table(validation_rows),
            "",
            "## Selected Variant Final Checks",
            "",
            *rows_table(final_rows),
            "",
            "## Safety Note",
            "",
            "All generated tester configs use `AllowLiveTrading=0`, `Visual=0`, and `ShutdownTerminal=1`. Do not attach these research builds to a live local chart while VPS trading is active.",
        ]
    )
    (REPORT_DIR / "SUMMARY.md").write_text("\n".join(summary_lines) + "\n")


def run_v3_guard(args: argparse.Namespace) -> None:
    ensure_dirs()
    print("safety check: local MT5 tester only; generated configs use AllowLiveTrading=0", flush=True)
    print("compile V1/V2Live/V3Guard", flush=True)
    for expert in EXPERTS_TO_RUN:
        compile_expert(expert)
    print("run V1/V2Live validation baselines", flush=True)
    baseline_rows = run_baseline_validation(args.backtest_timeout)
    print("run V3 ablation/guard validation matrix", flush=True)
    variants, validation_rows = run_v3_variant_validation(args.backtest_timeout)
    selection = select_best_variant(variants, validation_rows, baseline_rows)
    print(
        f"selected diagnostic variant {selection['selected']['variant_key']} "
        f"relative_gate={selection['selected']['passed_relative_gate']} strict_live={selection['selected']['strict_live_candidate']}",
        flush=True,
    )
    print("run selected V3 final checks", flush=True)
    final_rows = run_selected_final(selection["selected"], args.backtest_timeout)
    write_v3_reports(baseline_rows, variants, validation_rows, selection, final_rows)


def run_full(args: argparse.Namespace) -> None:
    run_v3_guard(args)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--optimization-timeout", type=int, default=7200)
    parser.add_argument("--backtest-timeout", type=int, default=2400)
    parser.add_argument("--candidate-limit", type=int, default=MAX_CANDIDATES)
    parser.add_argument("--reuse-optimization", action="store_true")
    args = parser.parse_args()
    run_full(args)


if __name__ == "__main__":
    main()
