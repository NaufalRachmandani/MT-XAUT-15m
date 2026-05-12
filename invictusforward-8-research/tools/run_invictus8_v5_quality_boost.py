#!/usr/bin/env python3
from __future__ import annotations

import argparse
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

from analyze_mt5_report import (  # noqa: E402
    extract_deal_rows,
    iter_rows,
    parse_first_number,
    read_report,
    reconstruct_closed_trades,
)


RESEARCH = ROOT / "invictusforward-8-research"
EXP_ROOT = RESEARCH / "invictus8_v5_quality_boost"
SRC_ROOT = EXP_ROOT / "source"
SETS_DIR = EXP_ROOT / "sets"
CENT_DIR = EXP_ROOT / "cent_confirmation"
REPORT_DIR = EXP_ROOT / "reports"

WINEPREFIX = Path.home() / "Library/Application Support/net.metaquotes.wine.metatrader5"
WINE = Path("/Applications/MetaTrader 5.app/Contents/SharedSupport/wine/bin/wine64")
TERMINAL = r"C:\Program Files\MetaTrader 5\terminal64.exe"
METAEDITOR = r"C:\Program Files\MetaTrader 5\metaeditor64.exe"
MT5_BUILD = WINEPREFIX / "drive_c" / "MT5Build"
REPORTS = WINEPREFIX / "drive_c" / "Program Files" / "MetaTrader 5" / "Reports"
EXPERTS = WINEPREFIX / "drive_c" / "Program Files" / "MetaTrader 5" / "MQL5" / "Experts"
PROFILES_TESTER = WINEPREFIX / "drive_c" / "Program Files" / "MetaTrader 5" / "MQL5" / "Profiles" / "Tester"

MODEL = 4
EXECUTION_MODE_MS = 100
LEVERAGE = "1:2000"
PERIOD = "M15"


@dataclass(frozen=True)
class AccountSpec:
    key: str
    label: str
    login: str
    server: str
    symbol: str
    currency: str


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
    account: AccountSpec
    window: WindowSpec
    deposit: int
    variant_key: str
    variant_label: str
    set_file: Path | None = None


CENT = AccountSpec("cent", "Cent confirmation", "184000633", "Exness-MT5Real25", "XAUUSDc", "USC")

V3_REF = ExpertSpec(
    "v3ref",
    "V3 Reference",
    SRC_ROOT / "v3guard",
    "InvictusForward-8-V3Guard.mq5",
    "InvictusForward8_V5QB_V3Ref",
    "InvictusForward-8-V3Guard.ex5",
)
V5 = ExpertSpec(
    "v5boost",
    "V5 Quality Boost",
    SRC_ROOT / "v5boost",
    "InvictusForward-8-V5Boost.mq5",
    "InvictusForward8_V5QB_V5Boost",
    "InvictusForward-8-V5Boost.ex5",
)
EXPERTS_TO_RUN = [V3_REF, V5]

CENT_WINDOWS_FAST = [
    WindowSpec("last_month", "Cent Last Month", "2026.04.10", "2026.05.10"),
    WindowSpec("ytd_2026", "Cent 2026 YTD", "2026.01.01", "2026.05.10"),
]
CENT_WINDOWS_CONFIRM = [
    WindowSpec("validate_mar", "Cent Validate Mar", "2026.03.01", "2026.03.31"),
    WindowSpec("validate_apr", "Cent Validate Apr", "2026.04.01", "2026.04.30"),
    WindowSpec("oos_may", "Cent OOS May", "2026.05.01", "2026.05.10"),
    WindowSpec("last_month", "Cent Last Month", "2026.04.10", "2026.05.10"),
    WindowSpec("ytd_2026", "Cent 2026 YTD", "2026.01.01", "2026.05.10"),
]
V3_SELECTED: dict[str, object] = {
    "BT_RiskPercent": 1.0,
    "BT_UseFixedLot": False,
    "BT_FixedLot": 0.01,
    "BT_CompoundingPer": 1000.0,
    "BT_MaxLotCap": 0.25,
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
    "RangeBounce_LotMult": 0.15,
    "RangeBounce_MaxBuy": 1,
    "RangeBounce_MaxSell": 0,
    "RangeBounce_EntryPct": 0.25,
    "RangeBounce_MaxEntriesPerRange": 2,
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
    "Guard_MaxTrendPosLowBalance": 2,
    "Guard_MaxTrendPosMidBalance": 3,
    "Guard_MaxTrendPosHighBalance": 2,
    "EnableDropCatcher": True,
    "DropCatcher_BodyATR": 1.8,
    "DropCatcher_MinBodyDlr": 12.0,
    "DropCatcher_VolMult": 1.3,
    "DropCatcher_MaxATR": 15.0,
    "DropCatcher_SL_ATR": 2.0,
    "DropCatcher_RR": 3.0,
    "DropCatcher_LotMult": 0.10,
    "DropCatcher_TrailATR": 1.0,
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
    "Guard_TrendMinScoreAdd": 0,
    "Guard_AllowTrendCorrective": True,
    "Guard_TrendLossCooldownBars": 2,
    "Guard_TrendLossCooldownTrigger": 2,
    "Guard_MaxTrendDailyLossCount": 5,
    "Trend_LotMult": 1.0,
}


def with_v5(overrides: dict[str, object]) -> dict[str, object]:
    values = dict(V3_SELECTED)
    values.update({
        # V3 effectively used 500 in code; V4/V5 honor this input.
        "BT_CompoundingPer": 500.0,
        "Trend_RRStandard": 1.5,
        "Trend_RRStrong": 2.0,
        "Trend_RRTop": 2.5,
        "V5_EnableTrendQualityScaling": True,
        "V5_TrendScore85LotMult": 0.65,
        "V5_TrendScore90LotMult": 0.85,
        "V5_TrendScore95LotMult": 1.00,
        "V5_TrendHour09LotMult": 0.75,
        "V5_TrendHour12LotMult": 0.80,
        "V5_TrendHour15LotMult": 0.60,
        "V5_BlockScore85Hour09": False,
        "V5_BlockScore90Hour12": False,
        "V5_BlockScore85Hour15": False,
    })
    values.update(overrides)
    return values


V5_VARIANTS: list[dict[str, object]] = [
    {
        "key": "v5_quality_scaled",
        "label": "V5 quality-scaled",
        "purpose": "V4 lot +100% base with score/hour quality scaling to reduce H09/H12/H15 leak size.",
        "values": with_v5({"BT_CompoundingPer": 250.0, "BT_MaxLotCap": 0.75}),
    },
    {
        "key": "v5_profit_scaled",
        "label": "V5 profit-scaled",
        "purpose": "Higher base lot than V4 lot +100%, offset by quality scaling.",
        "values": with_v5({"BT_CompoundingPer": 200.0, "BT_MaxLotCap": 1.00}),
    },
    {
        "key": "v5_high_profit_scaled",
        "label": "V5 high-profit scaled",
        "purpose": "Aggressive profit probe with softer quality scaling than leak-block profile.",
        "values": with_v5({
            "BT_CompoundingPer": 150.0,
            "BT_MaxLotCap": 1.25,
            "V5_TrendScore85LotMult": 0.70,
            "V5_TrendScore90LotMult": 0.90,
            "V5_TrendScore95LotMult": 1.00,
            "V5_TrendHour09LotMult": 0.80,
            "V5_TrendHour12LotMult": 0.85,
            "V5_TrendHour15LotMult": 0.65,
        }),
    },
    {
        "key": "v5_mid_profit_scaled",
        "label": "V5 mid-profit scaled",
        "purpose": "Middle profile between profit-scaled and high-profit scaled.",
        "values": with_v5({
            "BT_CompoundingPer": 175.0,
            "BT_MaxLotCap": 1.10,
        }),
    },
    {
        "key": "v5_max_profit_scaled",
        "label": "V5 max-profit scaled",
        "purpose": "Maximum profit probe with stronger leak dampening to avoid pure lot escalation.",
        "values": with_v5({
            "BT_CompoundingPer": 125.0,
            "BT_MaxLotCap": 1.50,
            "V5_TrendScore85LotMult": 0.60,
            "V5_TrendScore90LotMult": 0.85,
            "V5_TrendScore95LotMult": 1.00,
            "V5_TrendHour09LotMult": 0.70,
            "V5_TrendHour12LotMult": 0.80,
            "V5_TrendHour15LotMult": 0.55,
        }),
    },
    {
        "key": "v5_leak_block_scaled",
        "label": "V5 leak-block scaled",
        "purpose": "Quality-scaled profile plus hard blocks on the weakest score/hour leak clusters.",
        "values": with_v5({
            "BT_CompoundingPer": 200.0,
            "BT_MaxLotCap": 1.00,
            "V5_BlockScore85Hour09": True,
            "V5_BlockScore90Hour12": True,
            "V5_BlockScore85Hour15": True,
        }),
    },
    {
        "key": "v5_strong_rr_scaled",
        "label": "V5 strong-RR scaled",
        "purpose": "Quality scaling plus larger RR on higher-score trend setups.",
        "values": with_v5({
            "BT_CompoundingPer": 250.0,
            "BT_MaxLotCap": 0.75,
            "Trend_RRStrong": 2.3,
            "Trend_RRTop": 3.0,
        }),
    },
]


def env() -> dict[str, str]:
    output = os.environ.copy()
    output["WINEPREFIX"] = str(WINEPREFIX)
    output["WINEDEBUG"] = "-all"
    return output


def ensure_dirs() -> None:
    for directory in (EXP_ROOT, SETS_DIR, CENT_DIR, REPORT_DIR, MT5_BUILD, PROFILES_TESTER):
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


def write_set(name: str, values: dict[str, object], note: str) -> Path:
    lines = [f"; {note}", "; Native MT5 Strategy Tester set; generated for research only"]
    for key, value in values.items():
        lines.append(f"{key}={set_value(value)}||{set_value(value)}||0||{set_value(value)}||N")
    path = SETS_DIR / name
    write_utf16(path, "\r\n".join(lines) + "\r\n")
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
    target_log = REPORT_DIR / log.name
    shutil.copy2(log, target_log)
    if "0 errors" not in text:
        raise RuntimeError(f"{expert.label} compile failed; see {target_log}")
    ex5 = build_dir / expert.ex5_file
    if not ex5.exists():
        raise RuntimeError(f"compiled ex5 missing: {ex5}")
    target_dir = EXPERTS / expert.install_folder
    target_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ex5, target_dir / expert.ex5_file)
    shutil.copy2(ex5, REPORT_DIR / f"{expert.install_folder}_{expert.ex5_file}")
    return ex5


def report_stem(case: CaseSpec) -> str:
    start = case.window.from_date.replace(".", "")
    end = case.window.to_date.replace(".", "")
    return (
        f"InvictusForward8_V5QB_{case.account.key}_{case.expert.key}_{case.variant_key}_"
        f"{case.window.key}_d{case.deposit}{case.account.currency}_{case.account.symbol}_{PERIOD}_"
        f"lev2000_delay{EXECUTION_MODE_MS}_model{MODEL}_{start}_{end}"
    )


def tester_ini(case: CaseSpec, stem: str) -> Path:
    lines = [
        "[Common]",
        f"Login={case.account.login}",
        f"Server={case.account.server}",
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
        f"Expert={case.expert.install_folder}\\{case.expert.ex5_file}",
    ]
    if case.set_file:
        lines.append(f"ExpertParameters={case.set_file.name}")
    lines.extend([
        f"Symbol={case.account.symbol}",
        f"Period={PERIOD}",
        f"Login={case.account.login}",
        f"Model={MODEL}",
        f"ExecutionMode={EXECUTION_MODE_MS}",
        "Optimization=0",
        "OptimizationCriterion=0",
        f"FromDate={case.window.from_date}",
        f"ToDate={case.window.to_date}",
        "ForwardMode=0",
        f"Report=\\Reports\\{stem}",
        "ReplaceReport=1",
        "ShutdownTerminal=1",
        f"Deposit={case.deposit}",
        f"Currency={case.account.currency}",
        f"Leverage={LEVERAGE}",
        "UseLocal=1",
        "UseRemote=0",
        "UseCloud=0",
        "Visual=0",
        "",
    ])
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


def copy_report_artifacts(stem: str, destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    for artifact in REPORTS.glob(f"{stem}*"):
        if artifact.is_file():
            shutil.copy2(artifact, destination / artifact.name)


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


def parse_report(report: Path, case: CaseSpec, ini: Path) -> dict[str, object]:
    text = read_report(report)
    profit_trades = cell(text, "Profit Trades (% of total):")
    loss_trades = cell(text, "Loss Trades (% of total):")
    row: dict[str, object] = {
        "expert_key": case.expert.key,
        "expert": case.expert.label,
        "variant_key": case.variant_key,
        "variant": case.variant_label,
        "account_key": case.account.key,
        "account": case.account.label,
        "login": case.account.login,
        "server": case.account.server,
        "symbol": cell(text, "Symbol:", case.account.symbol),
        "period": PERIOD,
        "window_key": case.window.key,
        "window": case.window.label,
        "from": case.window.from_date,
        "to": case.window.to_date,
        "deposit": case.deposit,
        "currency": cell(text, "Currency:", ""),
        "initial_deposit": parse_first_number(cell(text, "Initial Deposit:")),
        "leverage": cell(text, "Leverage:", LEVERAGE),
        "model": MODEL,
        "execution_mode_ms": EXECUTION_MODE_MS,
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
        "max_consecutive_losses": cell(text, "Maximum consecutive losses ($):"),
        "max_consecutive_loss_count": int(parse_first_number(cell(text, "Maximum consecutive losses ($):"))),
        "report": str(report),
        "ini": str(ini),
        "set": str(case.set_file) if case.set_file else "",
        "ini_settings": read_ini_settings(ini),
    }
    row["validation_issues"] = validate_result(row, case)
    return row


def validate_result(row: dict[str, object], case: CaseSpec) -> list[str]:
    issues: list[str] = []
    settings = row["ini_settings"]
    if row["symbol"] != case.account.symbol:
        issues.append(f"symbol={row['symbol']}")
    if row["currency"] != case.account.currency:
        issues.append(f"currency={row['currency']}")
    if row["leverage"] != LEVERAGE:
        issues.append(f"leverage={row['leverage']}")
    if row["history_quality"] != "100% real ticks":
        issues.append(f"history={row['history_quality']}")
    if abs(float(row["initial_deposit"]) - float(row["deposit"])) > 0.01:
        issues.append(f"initial_deposit={row['initial_deposit']}")
    expected = {
        "Symbol": case.account.symbol,
        "Period": PERIOD,
        "Model": str(MODEL),
        "ExecutionMode": str(EXECUTION_MODE_MS),
        "Optimization": "0",
        "Deposit": str(case.deposit),
        "Currency": case.account.currency,
        "Leverage": LEVERAGE,
        "UseLocal": "1",
        "UseRemote": "0",
        "UseCloud": "0",
    }
    if isinstance(settings, dict):
        for key, value in expected.items():
            if settings.get(key) != value:
                issues.append(f"ini_{key}={settings.get(key)}")
    return issues


def run_case(case: CaseSpec, timeout: int, destination: Path, force: bool = False) -> dict[str, object]:
    stem = report_stem(case)
    copied_report = destination / f"{stem}.htm"
    copied_ini = destination / f"{stem}.ini"
    if not force and copied_report.exists() and copied_report.stat().st_size > 0 and copied_ini.exists():
        return parse_report(copied_report, case, copied_ini) | {"cached": True, "completed_before_timeout": True}
    remove_old_reports(stem)
    ini = tester_ini(case, stem)
    completed = run_terminal_config(ini, timeout)
    report = REPORTS / f"{stem}.htm"
    for _ in range(300):
        if report.exists() and report.stat().st_size > 0:
            break
        time.sleep(1)
    if not report.exists() or report.stat().st_size == 0:
        raise RuntimeError(f"report missing after {stem}; completed={completed}")
    destination.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ini, copied_ini)
    copy_report_artifacts(stem, destination)
    return parse_report(copied_report, case, copied_ini) | {"cached": False, "completed_before_timeout": completed}


def classify_module(comment: str) -> str:
    if "IF8V7R_DC" in comment or "IF8V6A_DC" in comment or "IF8V5Q_DC" in comment or "IF8V4B_DC" in comment or "IF8V3G_DC" in comment or "DropCatch" in comment:
        return "DropCatcher"
    if "IF8V7R_RB" in comment or "IF8V6A_RB" in comment or "IF8V5Q_RB" in comment or "IF8V4B_RB" in comment or "IF8V3G_RB" in comment or "IHS RB" in comment:
        return "RangeBounce"
    if "IF8V7R_TR" in comment or "IF8V6A_TR" in comment or "IF8V5Q_TR" in comment or "IF8V4B_TR" in comment or "IF8V3G_TR" in comment or "IHB S:" in comment:
        return "Trend"
    return "Unknown"


def diagnose(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for row in rows:
        report = Path(str(row["report"]))
        if not report.exists():
            continue
        trades, _ = reconstruct_closed_trades(extract_deal_rows(read_report(report)))
        for trade in trades:
            output.append({
                "account_key": row["account_key"],
                "variant_key": row["variant_key"],
                "variant": row["variant"],
                "window_key": row["window_key"],
                "deposit": row["deposit"],
                "module": classify_module(trade.entry_comment or trade.exit_comment),
                "entry_hour": trade.entry_time.hour,
                "profit": trade.profit,
                "volume": trade.volume,
                "entry_comment": trade.entry_comment,
                "exit_comment": trade.exit_comment,
                "hold_minutes": trade.hold_minutes,
            })
    return output


def score_variant(rows: list[dict[str, object]], v3_rows: list[dict[str, object]], *, require_full_confirmation: bool = False) -> dict[str, object]:
    cent = [r for r in rows if r["account_key"] == "cent"]
    v3_by_window = {r["window_key"]: r for r in v3_rows if r["account_key"] == "cent"}
    ytd = next((r for r in cent if r["window_key"] == "ytd_2026"), None)
    last_month = next((r for r in cent if r["window_key"] == "last_month"), None)
    reasons: list[str] = []
    if not ytd or not last_month:
        reasons.append("missing cent fast windows")
    for row in cent:
        if row["validation_issues"]:
            reasons.append(f"{row['account_key']}:{row['window_key']}: {row['validation_issues']}")
    if require_full_confirmation:
        cent_keys = {str(row["window_key"]) for row in cent}
        for window in CENT_WINDOWS_CONFIRM:
            if window.key not in cent_keys:
                reasons.append(f"{window.key}: cent confirmation not tested")
    if last_month and float(last_month["net"]) <= 0:
        reasons.append("cent last_month net <= 0")
    if ytd:
        v3_ytd = v3_by_window.get("ytd_2026")
        if v3_ytd and float(ytd["net"]) <= float(v3_ytd["net"]):
            reasons.append("cent YTD net not above V3")
    score = 0.0
    if ytd:
        score += float(ytd["net"])
        score -= float(ytd["equity_dd_pct"]) * 20.0
    if last_month:
        score += float(last_month["net"]) * 1.5
        score -= float(last_month["equity_dd_pct"]) * 30.0
    return {
        "variant_key": rows[0]["variant_key"] if rows else "",
        "variant": rows[0]["variant"] if rows else "",
        "passed_research_gate": not reasons,
        "fail_reasons": sorted(set(reasons)),
        "score": score,
        "cent_ytd_net": ytd["net"] if ytd else None,
        "cent_ytd_pf": ytd["profit_factor"] if ytd else None,
        "cent_ytd_dd_pct": ytd["equity_dd_pct"] if ytd else None,
        "cent_last_month_net": last_month["net"] if last_month else None,
        "cent_last_month_pf": last_month["profit_factor"] if last_month else None,
        "cent_last_month_dd_pct": last_month["equity_dd_pct"] if last_month else None,
    }


def select_variant(results: list[dict[str, object]]) -> dict[str, object] | None:
    v3_rows = [r for r in results if r["variant_key"] == "v3_reference"]
    require_full = any(
        str(r["window_key"]) in {"validate_mar", "validate_apr", "oos_may"} for r in results
    )
    scores: list[dict[str, object]] = []
    for variant in V5_VARIANTS:
        rows = [r for r in results if r["variant_key"] == variant["key"]]
        if rows:
            scores.append(score_variant(rows, v3_rows, require_full_confirmation=require_full))
    (REPORT_DIR / "variant_scores.json").write_text(json.dumps(scores, indent=2, default=str) + "\n")
    passed = [row for row in scores if row["passed_research_gate"]]
    pool = passed or scores
    if not pool:
        return None
    return sorted(pool, key=lambda row: (bool(row["passed_research_gate"]), float(row["score"])), reverse=True)[0]


def write_reports(results: list[dict[str, object]], selected: dict[str, object] | None) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    diag = diagnose(results)
    (REPORT_DIR / "results.json").write_text(json.dumps(results, indent=2, default=str) + "\n")
    (REPORT_DIR / "trade_diagnosis.json").write_text(json.dumps(diag, indent=2, default=str) + "\n")
    selected_key = selected["variant_key"] if selected else None
    (REPORT_DIR / "selected_variant.json").write_text(json.dumps(selected, indent=2, default=str) + "\n")

    lines = [
        "# Invictus Forward-8 V5 Quality Boost",
        "",
        "V5 is a quality-scaled profit experiment based on V4. It uses only native MT5 cent `XAUUSDc` 2026 real-tick confirmation in this run.",
        "",
        "Safety: all generated native MT5 configs use `AllowLiveTrading=0`, `Visual=0`, and `ShutdownTerminal=1`.",
        "",
        f"Selected research variant: `{selected_key or 'none'}`.",
        "",
        "## Results",
        "",
        "| Account | Variant | Window | Deposit | Net | PF | Trades | WR | Eq DD | Largest Loss | History | Validation |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- | ---: | --- | --- |",
    ]
    order = {"cent": 0}
    for row in sorted(results, key=lambda r: (order.get(str(r["account_key"]), 9), str(r["variant_key"]), str(r["window_key"]))):
        validation = ", ".join(row["validation_issues"]) if row["validation_issues"] else "OK"
        lines.append(
            f"| {row['account']} | {row['variant']} | {row['window']} | {row['deposit']} {row['currency']} | "
            f"{float(row['net']):.2f} | {float(row['profit_factor']):.2f} | {row['trades']} | "
            f"{float(row['win_rate_pct']):.2f}% | {row['equity_dd']} | {float(row['largest_loss']):.2f} | "
            f"{row['history_quality']} | {validation} |"
        )
    score_path = REPORT_DIR / "variant_scores.json"
    scores = json.loads(score_path.read_text()) if score_path.exists() else []
    lines.extend([
        "",
        "## Variant Scores",
        "",
        "| Variant | Gate | Score | Cent YTD Net/PF/DD% | Cent Last Month Net/PF/DD% | Fail Reasons |",
        "| --- | --- | ---: | --- | --- | --- |",
    ])
    for row in sorted(scores, key=lambda item: float(item["score"]), reverse=True):
        lines.append(
            f"| {row['variant']} | {row['passed_research_gate']} | {float(row['score']):.2f} | "
            f"{row['cent_ytd_net']} / {row['cent_ytd_pf']} / {row['cent_ytd_dd_pct']} | "
            f"{row['cent_last_month_net']} / {row['cent_last_month_pf']} / {row['cent_last_month_dd_pct']} | "
            f"{'; '.join(row['fail_reasons'])} |"
        )
    lines.extend([
        "",
        "## Decision",
        "",
    ])
    if selected:
        if selected["passed_research_gate"]:
            lines.append("Selected V5 passed the cent research gate, but it is still not a live profile until forward demo confirms it.")
        else:
            lines.append("No V5 variant passed every research gate. The selected row is the best profit candidate only, not live-ready.")
    else:
        lines.append("No V5 result was available.")
    (REPORT_DIR / "SUMMARY.md").write_text("\n".join(lines) + "\n")

    source_v3 = (SRC_ROOT / "v3guard" / "InvictusForward-8-V3Guard.mq5").read_text(errors="ignore").splitlines()
    source_v5 = (SRC_ROOT / "v5boost" / "InvictusForward-8-V5Boost.mq5").read_text(errors="ignore").splitlines()
    diff = difflib.unified_diff(source_v3, source_v5, fromfile="V3Guard/InvictusForward-8-V3Guard.mq5", tofile="V5Boost/InvictusForward-8-V5Boost.mq5", lineterm="")
    (REPORT_DIR / "CODE_DIFF.md").write_text("# V3Guard vs V5Boost Code Diff\n\n```diff\n" + "\n".join(list(diff)[:800]) + "\n```\n")

    param_lines = [
        "# V5 Variant Parameter Diff",
        "",
        "| Variant | Key Differences |",
        "| --- | --- |",
    ]
    for variant in V5_VARIANTS:
        values = variant["values"]
        changed = []
        for key in (
            "BT_CompoundingPer", "BT_MaxLotCap", "Trend_RRStandard", "Trend_RRStrong", "Trend_RRTop",
            "RangeBounce_LotMult", "DropCatcher_LotMult",
            "V5_TrendScore85LotMult", "V5_TrendScore90LotMult", "V5_TrendHour09LotMult",
            "V5_TrendHour12LotMult", "V5_TrendHour15LotMult",
            "V5_BlockScore85Hour09", "V5_BlockScore90Hour12", "V5_BlockScore85Hour15",
        ):
            changed.append(f"`{key}={set_value(values[key])}`")
        param_lines.append(f"| {variant['label']} | {'; '.join(changed)} |")
    (REPORT_DIR / "PARAM_DIFF.md").write_text("\n".join(param_lines) + "\n")


def build_sets() -> dict[str, Path]:
    sets = {
        "v3_reference": write_set("InvictusForward8_V3_reference.set", V3_SELECTED, "V3 selected pending-guard reference"),
    }
    for variant in V5_VARIANTS:
        sets[variant["key"]] = write_set(f"InvictusForward8_{variant['key']}.set", variant["values"], str(variant["purpose"]))
    return sets


def run(args: argparse.Namespace) -> None:
    ensure_dirs()
    print("safety check: native tester only; AllowLiveTrading=0, Visual=0, ShutdownTerminal=1", flush=True)
    sets = build_sets()
    print("compile V3 reference and V5Boost", flush=True)
    for expert in EXPERTS_TO_RUN:
        compile_expert(expert)
    if args.compile_only:
        return

    results: list[dict[str, object]] = []

    v3_cases = [
        CaseSpec(V3_REF, CENT, window, 1000, "v3_reference", "V3 reference", sets["v3_reference"])
        for window in CENT_WINDOWS_FAST
    ]
    for case in v3_cases:
        print(f"run {case.variant_key} {case.account.key} {case.window.key}", flush=True)
        row = run_case(case, args.backtest_timeout, CENT_DIR, force=args.force)
        results.append(row)
        print(f"done {case.variant_key} {case.window.key} net={row['net']:.2f} pf={row['profit_factor']:.2f} history={row['history_quality']}", flush=True)
        selected = select_variant(results)
        write_reports(results, selected)

    selected_case_results: list[dict[str, object]] = []
    for variant in V5_VARIANTS:
        windows = CENT_WINDOWS_FAST
        for window in windows:
            case = CaseSpec(V5, CENT, window, 1000, variant["key"], str(variant["label"]), sets[variant["key"]])
            print(f"run {case.variant_key} {case.account.key} {case.window.key}", flush=True)
            row = run_case(case, args.backtest_timeout, CENT_DIR, force=args.force)
            results.append(row)
            print(f"done {case.variant_key} {case.window.key} net={row['net']:.2f} pf={row['profit_factor']:.2f} dd={row['equity_dd_pct']:.2f}% history={row['history_quality']}", flush=True)
            selected = select_variant(results)
            write_reports(results, selected)

    selected = select_variant(results)
    if selected:
        selected_key = str(selected["variant_key"])
        selected_variant = next((variant for variant in V5_VARIANTS if variant["key"] == selected_key), None)
        if selected_variant:
            confirm_windows = [w for w in CENT_WINDOWS_CONFIRM if w.key not in {r["window_key"] for r in results if r["variant_key"] == selected_key and r["account_key"] == "cent"}]
            for window in confirm_windows:
                case = CaseSpec(V5, CENT, window, 1000, selected_key, str(selected_variant["label"]), sets[selected_key])
                print(f"confirm selected {selected_key} cent {window.key}", flush=True)
                row = run_case(case, args.backtest_timeout, CENT_DIR, force=args.force)
                results.append(row)
                selected_case_results.append(row)
                print(f"done selected {window.key} net={row['net']:.2f} pf={row['profit_factor']:.2f} dd={row['equity_dd_pct']:.2f}% history={row['history_quality']}", flush=True)
                selected = select_variant(results)
                write_reports(results, selected)

    write_reports(results, select_variant(results))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--backtest-timeout", type=int, default=2400)
    parser.add_argument("--proxy-timeout", type=int, default=5400)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--compile-only", action="store_true")
    args = parser.parse_args()
    run(args)


if __name__ == "__main__":
    main()
