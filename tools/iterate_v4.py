#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import textwrap
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path("/Users/naufalrachmandani/Hobby/MT5 XAU 15m")
EA_SOURCE = ROOT / "mt5" / "InvictusForward1M15_v4.mq5"
RUN_DIR = ROOT / "build" / "v4_20x"
RUN_DIR.mkdir(parents=True, exist_ok=True)

WINEPREFIX = Path("/Users/naufalrachmandani/Library/Application Support/net.metaquotes.wine.metatrader5")
MT5_BUILD = WINEPREFIX / "drive_c" / "MT5Build"
MT5_EXPERTS = WINEPREFIX / "drive_c" / "Program Files" / "MetaTrader 5" / "MQL5" / "Experts" / "Invictus"
REPORTS_DIR = WINEPREFIX / "drive_c" / "Program Files" / "MetaTrader 5" / "Reports"
TESTER_LOG_DIR = WINEPREFIX / "drive_c" / "Program Files" / "MetaTrader 5" / "Tester" / "logs"
WINE = "/Applications/MetaTrader 5.app/Contents/SharedSupport/wine/bin/wine64"
METAEDITOR_EXE = r"C:\Program Files\MetaTrader 5\metaeditor64.exe"
TERMINAL_EXE = r"C:\Program Files\MetaTrader 5\terminal64.exe"


BASE_PARAMS: dict[str, Any] = {
    "IF1_PENDING_CANCEL_LOSS_CAP_PCT": 6.0,
    "IF1_BREAKEVEN_LOCK_USD": 1.5,
    "IF1_SIDEWAYS_TP_FRACTION_OVERRIDE": 0.55,
    "IF1_SIDEWAYS_MIN_TP_USD": 6.5,
    "IF1_REFERENCE_GOLD_CONTRACT_SIZE": 100.0,
    "IF1_TREND_MIN_SL_OVERRIDE": 12.0,
    "IF1_TREND_MAX_SL_OVERRIDE": 30.0,
    "IF1_TREND_MAX_POSITIONS_LOW_OVERRIDE": 7,
    "IF1_TREND_MAX_POSITIONS_MID_OVERRIDE": 11,
    "IF1_TREND_MAX_POSITIONS_HIGH_OVERRIDE": 15,
    "IF1_COMPOUND_BALANCE_STEP_LOW_OVERRIDE": 250.0,
    "IF1_COMPOUND_BALANCE_STEP_MID_OVERRIDE": 300.0,
    "IF1_COMPOUND_BALANCE_STEP_HIGH_OVERRIDE": 375.0,
    "IF1_COMPOUND_BASE_LOT_MID_OVERRIDE": 0.82,
    "IF1_COMPOUND_BASE_LOT_HIGH_OVERRIDE": 1.92,
    "IF1_COOLDOWN_BARS_OVERRIDE": 1,
    "IF1_ZONE_COOLDOWN_BARS_OVERRIDE": 1,
    "IF1_MIN_BREAK_ATR_OVERRIDE": 0.18,
    "IF1_ZONE_SEARCH_WINDOW_OVERRIDE": 12,
    "IF1_MAX_ZONE_RANGE_USD_OVERRIDE": 30.0,
    "IF1_MAX_ZONE_PRIOR_TESTS_OVERRIDE": 2,
    "IF1_ENTRY_BODY_RATIO_OVERRIDE": 0.35,
    "IF1_SCORE_BUY_MIN_OVERRIDE": 70,
    "IF1_SCORE_SELL_MIN_OVERRIDE": 75,
    "IF1_TREND_LOW_SCORE_SELL_MAX": 84,
    "IF1_TREND_LOW_SCORE_SELL_RR_OVERRIDE": 1.35,
    "IF1_TREND_LOW_SCORE_SELL_LOT_MULT": 0.50,
    "IF1_TREND_POSITIVE_SELL_MIN": 85,
    "IF1_TREND_POSITIVE_SELL_MAX": 94,
    "IF1_TREND_POSITIVE_SELL_LOT_MULT": 1.0,
    "IF1_TREND_SELL_TP_RR_DEFAULT_OVERRIDE": 1.62,
    "IF1_TREND_SELL_TP_RR_BOOST_OVERRIDE": 2.25,
    "IF1_SCORE_RR_BOOST_MIN_OVERRIDE": 84,
    "IF1_SELL_LOT_MODIFIER_OVERRIDE": 0.75,
    "IF1_SIDEWAYS_LOT_MODIFIER_OVERRIDE": 0.10,
    "IF1_TREND_DAILY_LOSS_CAP_PCT_OVERRIDE": 8.0,
    "IF1_SIDEWAYS_DAILY_LOSS_CAP_PCT_OVERRIDE": 5.0,
    "IF1_TREND_KILLSWITCH_WINS_OVERRIDE": 50,
    "IF1_SIDEWAYS_WINS_CAP_OVERRIDE": 20,
    "IF1_SIDEWAYS_ADX_THRESHOLD_OVERRIDE": 28.0,
    "IF1_SIDEWAYS_ENTRY_ZONE_FRACTION_OVERRIDE": 0.40,
    "IF1_SIDEWAYS_MAX_POSITIONS_OVERRIDE": 8,
    "IF1_SIDEWAYS_CLUSTER_MAX_PER_DAY_OVERRIDE": 5,
    "IF1_ALLOW_ALL_SELL_HOURS": True,
    "IF1_SELL_BLOCK_HOURS_MASK": 0,
    "IF1_LOW_SCORE_SELL_BLOCK_HOURS_MASK": 341600,
    "IF1_GOLD_HIGH_SCORE_SELL_REQUIRE_IMPULSIVE_BOS": True,
    "IF1_GOLD_HIGH_SCORE_SELL_MIN_LL_HH_EDGE": 0,
    "IF1_GOLD_HIGH_SCORE_SELL_MIN_BREAK_ATR_OVERRIDE": 0.0,
    "IF1_TREND_TIMED_PROFIT_CLOSE_HOURS_OVERRIDE": 4,
    "IF1_SIDEWAYS_TIMED_PROFIT_CLOSE_HOURS_OVERRIDE": 2,
    "IF1_TREND_TIMED_PROFIT_USD_PER_001_OVERRIDE": 24.0,
    "IF1_SIDEWAYS_TIMED_PROFIT_USD_PER_001_OVERRIDE": 15.0,
    "IF1_LOW_SCORE_SELL_TIMED_CLOSE_HOURS_OVERRIDE": 0,
    "IF1_LOW_SCORE_SELL_TIMED_PROFIT_USD_PER_001_OVERRIDE": 0.0,
    "IF1_LOW_SCORE_SELL_TIMED_MAX_LOSS_USD_PER_001_OVERRIDE": 0.0,
    "IF1_TREND_TP_RR_DEFAULT_OVERRIDE": 1.62,
    "IF1_TREND_TP_RR_BOOST_OVERRIDE": 2.25,
    "IF1_TREND_HIGH_SCORE_SELL_RR_OVERRIDE": 0.0,
    "IF1_BUY_LOW_SCORE_MAX": 84,
    "IF1_BUY_MID_SCORE_MIN": 85,
    "IF1_BUY_MID_SCORE_MAX": 94,
    "IF1_TREND_HIGH_SCORE_BUY_RR_MIN": 95,
    "IF1_TREND_HIGH_SCORE_BUY_RR_OVERRIDE": 2.45,
    "IF1_BUY_LOW_SCORE_RR_OVERRIDE": 0.0,
    "IF1_BUY_MID_SCORE_RR_OVERRIDE": 0.0,
    "IF1_BUY_LOW_SCORE_LOT_MULT": 1.0,
    "IF1_TREND_HIGH_SCORE_LOT_BOOST_MIN": 95,
    "IF1_TREND_HIGH_SCORE_LOT_BOOST": 1.18,
    "IF1_TREND_HIGH_SCORE_SELL_LOT_MULT": 1.0,
    "IF1_BUY_MIN_BREAK_ATR_OVERRIDE": 0.0,
    "IF1_BUY_MAX_ENTRY_PREMIUM_ATR_OVERRIDE": 0.0,
    "IF1_BUY_ENTRY_PREMIUM_SCORE_LIMIT_OVERRIDE": 101,
    "IF1_BUY_MAX_ZONE_PRIOR_TESTS_OVERRIDE": -1,
    "IF1_GOLD_HIGH_SCORE_BUY_REQUIRE_IMPULSIVE_BOS": False,
    "IF1_BUY_LOW_SCORE_REQUIRE_FVG": False,
    "IF1_BUY_BREAKEVEN_TRIGGER_R_MULT": 1.0,
    "IF1_BUY_BREAKEVEN_LOCK_USD_OVERRIDE": 0.0,
}


ITERATIONS: list[dict[str, Any]] = [
    {"name": "baseline_v3_clone", "hypothesis": "Baseline v4 identik dengan v3 resmi.", "changes": {}},
    {"name": "buy_premium_cap_075", "hypothesis": "Jangan kejar buy yang terlalu jauh dari zone; cap premium 0.75 ATR.", "changes": {
        "IF1_BUY_MAX_ENTRY_PREMIUM_ATR_OVERRIDE": 0.75,
        "IF1_BUY_ENTRY_PREMIUM_SCORE_LIMIT_OVERRIDE": 95,
    }},
    {"name": "buy_premium_cap_060", "hypothesis": "Versi lebih ketat dari entry premium cap.", "changes": {
        "IF1_BUY_MAX_ENTRY_PREMIUM_ATR_OVERRIDE": 0.60,
        "IF1_BUY_ENTRY_PREMIUM_SCORE_LIMIT_OVERRIDE": 95,
    }},
    {"name": "buy_break_024", "hypothesis": "Buy butuh break ATR yang lebih solid untuk kurangi breakout palsu.", "changes": {
        "IF1_BUY_MIN_BREAK_ATR_OVERRIDE": 0.24,
    }},
    {"name": "buy_break_028", "hypothesis": "Uji break ATR bullish yang lebih tegas lagi.", "changes": {
        "IF1_BUY_MIN_BREAK_ATR_OVERRIDE": 0.28,
    }},
    {"name": "buy_highscore_impulsive", "hypothesis": "High-score buy di gold hanya valid jika BOS bullish impulsif.", "changes": {
        "IF1_GOLD_HIGH_SCORE_BUY_REQUIRE_IMPULSIVE_BOS": True,
    }},
    {"name": "buy_low_rr_145", "hypothesis": "Low-score buy diberi TP lebih dekat untuk naikkan hit-rate.", "changes": {
        "IF1_BUY_LOW_SCORE_RR_OVERRIDE": 1.45,
    }},
    {"name": "buy_low_rr_135_lot_090", "hypothesis": "Low-score buy lebih defensif: TP lebih dekat dan lot sedikit dikecilkan.", "changes": {
        "IF1_BUY_LOW_SCORE_RR_OVERRIDE": 1.35,
        "IF1_BUY_LOW_SCORE_LOT_MULT": 0.90,
    }},
    {"name": "buy_mid_rr_155", "hypothesis": "Mid-score buy ikut dipercepat take-profit-nya.", "changes": {
        "IF1_BUY_MID_SCORE_RR_OVERRIDE": 1.55,
    }},
    {"name": "buy_breakeven_085r", "hypothesis": "Buy pindah ke breakeven sedikit lebih cepat pada 0.85R.", "changes": {
        "IF1_BUY_BREAKEVEN_TRIGGER_R_MULT": 0.85,
        "IF1_BUY_BREAKEVEN_LOCK_USD_OVERRIDE": 1.0,
    }},
    {"name": "buy_breakeven_070r", "hypothesis": "Versi lebih agresif dari early breakeven buy.", "changes": {
        "IF1_BUY_BREAKEVEN_TRIGGER_R_MULT": 0.70,
        "IF1_BUY_BREAKEVEN_LOCK_USD_OVERRIDE": 1.0,
    }},
    {"name": "buy_zone_tests_1", "hypothesis": "Buy hanya boleh dari zone yang belum terlalu sering disentuh.", "changes": {
        "IF1_BUY_MAX_ZONE_PRIOR_TESTS_OVERRIDE": 1,
    }},
    {"name": "buy_low_fvg", "hypothesis": "Low-score buy wajib punya FVG supaya tidak masuk setup murahan.", "changes": {
        "IF1_BUY_LOW_SCORE_REQUIRE_FVG": True,
    }},
    {"name": "combo_premium075_break024", "hypothesis": "Gabungkan anti-chase dan breakout bullish yang lebih valid.", "changes": {
        "IF1_BUY_MAX_ENTRY_PREMIUM_ATR_OVERRIDE": 0.75,
        "IF1_BUY_ENTRY_PREMIUM_SCORE_LIMIT_OVERRIDE": 95,
        "IF1_BUY_MIN_BREAK_ATR_OVERRIDE": 0.24,
    }},
    {"name": "combo_premium075_lowrr145", "hypothesis": "Anti-chase + TP low-score buy lebih cepat.", "changes": {
        "IF1_BUY_MAX_ENTRY_PREMIUM_ATR_OVERRIDE": 0.75,
        "IF1_BUY_ENTRY_PREMIUM_SCORE_LIMIT_OVERRIDE": 95,
        "IF1_BUY_LOW_SCORE_RR_OVERRIDE": 1.45,
    }},
    {"name": "combo_break024_lowrr145", "hypothesis": "Break bullish lebih kuat dan low-score buy lebih cepat cash out.", "changes": {
        "IF1_BUY_MIN_BREAK_ATR_OVERRIDE": 0.24,
        "IF1_BUY_LOW_SCORE_RR_OVERRIDE": 1.45,
    }},
    {"name": "combo_premium075_break024_be085", "hypothesis": "Paket inti: anti-chase, breakout lebih kuat, dan breakeven buy lebih cepat.", "changes": {
        "IF1_BUY_MAX_ENTRY_PREMIUM_ATR_OVERRIDE": 0.75,
        "IF1_BUY_ENTRY_PREMIUM_SCORE_LIMIT_OVERRIDE": 95,
        "IF1_BUY_MIN_BREAK_ATR_OVERRIDE": 0.24,
        "IF1_BUY_BREAKEVEN_TRIGGER_R_MULT": 0.85,
        "IF1_BUY_BREAKEVEN_LOCK_USD_OVERRIDE": 1.0,
    }},
    {"name": "combo_premium075_break024_zone1", "hypothesis": "Tambahkan zone freshness pada paket anti-chase + valid BOS.", "changes": {
        "IF1_BUY_MAX_ENTRY_PREMIUM_ATR_OVERRIDE": 0.75,
        "IF1_BUY_ENTRY_PREMIUM_SCORE_LIMIT_OVERRIDE": 95,
        "IF1_BUY_MIN_BREAK_ATR_OVERRIDE": 0.24,
        "IF1_BUY_MAX_ZONE_PRIOR_TESTS_OVERRIDE": 1,
    }},
    {"name": "combo_premium075_break024_lowrr145_be085", "hypothesis": "Gabungkan anti-chase, BOS kuat, low-score TP lebih dekat, dan early breakeven.", "changes": {
        "IF1_BUY_MAX_ENTRY_PREMIUM_ATR_OVERRIDE": 0.75,
        "IF1_BUY_ENTRY_PREMIUM_SCORE_LIMIT_OVERRIDE": 95,
        "IF1_BUY_MIN_BREAK_ATR_OVERRIDE": 0.24,
        "IF1_BUY_LOW_SCORE_RR_OVERRIDE": 1.45,
        "IF1_BUY_BREAKEVEN_TRIGGER_R_MULT": 0.85,
        "IF1_BUY_BREAKEVEN_LOCK_USD_OVERRIDE": 1.0,
    }},
    {"name": "champion_challenge", "hypothesis": "Versi agresif final untuk menantang champion dengan paket buy yang lebih disiplin tapi tidak terlalu ketat.", "changes": {
        "IF1_BUY_MAX_ENTRY_PREMIUM_ATR_OVERRIDE": 0.70,
        "IF1_BUY_ENTRY_PREMIUM_SCORE_LIMIT_OVERRIDE": 95,
        "IF1_BUY_MIN_BREAK_ATR_OVERRIDE": 0.24,
        "IF1_BUY_LOW_SCORE_RR_OVERRIDE": 1.45,
        "IF1_BUY_MID_SCORE_RR_OVERRIDE": 1.55,
        "IF1_BUY_BREAKEVEN_TRIGGER_R_MULT": 0.85,
        "IF1_BUY_BREAKEVEN_LOCK_USD_OVERRIDE": 1.0,
        "IF1_GOLD_HIGH_SCORE_BUY_REQUIRE_IMPULSIVE_BOS": True,
    }},
]


@dataclass
class IterationResult:
    index: int
    name: str
    hypothesis: str
    params: dict[str, Any]
    metrics: dict[str, float]
    tester_log: str
    trend_diag: dict[str, float]
    trend_dir_diag: dict[str, float]
    trend_score_diag: dict[str, float]
    v4_buy_diag: dict[str, float]
    accepted: bool
    takeaway: str


def fmt_value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        text = f"{value:.10f}".rstrip("0").rstrip(".")
        if "." not in text:
            text += ".0"
        return text
    raise TypeError(f"Unsupported value type: {type(value)!r}")


def patch_source(template: str, params: dict[str, Any]) -> str:
    result = template
    for name, value in params.items():
        pattern = re.compile(rf"(static const [^;\n]*\b{name}\b\s*=\s*)([^;]+)(;)")
        result, count = pattern.subn(lambda m: f"{m.group(1)}{fmt_value(value)}{m.group(3)}", result)
        if count != 1:
            raise RuntimeError(f"Failed to patch constant {name}")
    return result


def run_subprocess(args: list[str], *, quiet: bool = True) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["WINEPREFIX"] = str(WINEPREFIX)
    env["WINEDEBUG"] = "-all"
    kwargs: dict[str, Any] = {"cwd": ROOT, "env": env, "text": True, "check": False}
    if quiet:
        kwargs["stdout"] = subprocess.DEVNULL
        kwargs["stderr"] = subprocess.DEVNULL
    else:
        kwargs["stdout"] = subprocess.PIPE
        kwargs["stderr"] = subprocess.STDOUT
    return subprocess.run(args, **kwargs)


def launch_subprocess(args: list[str]) -> subprocess.Popen[str]:
    env = os.environ.copy()
    env["WINEPREFIX"] = str(WINEPREFIX)
    env["WINEDEBUG"] = "-all"
    return subprocess.Popen(
        args,
        cwd=ROOT,
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        text=True,
    )


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def latest_tester_log() -> Path | None:
    logs = sorted(TESTER_LOG_DIR.glob("*.log"), key=lambda p: p.stat().st_mtime)
    return logs[-1] if logs else None


def compile_variant(stem: str, source_text: str) -> None:
    source_path = MT5_BUILD / f"{stem}.mq5"
    compile_log = MT5_BUILD / f"{stem}.compile.log"
    write_file(source_path, source_text)
    run_subprocess([WINE, METAEDITOR_EXE, f"/compile:C:\\MT5Build\\{stem}.mq5", f"/log:C:\\MT5Build\\{stem}.compile.log"])
    log_text = compile_log.read_bytes().decode("utf-16le", errors="ignore")
    if "0 errors" not in log_text:
        raise RuntimeError(f"Compilation failed for {stem}: {log_text[-600:]}")


def build_ini(stem: str) -> str:
    return textwrap.dedent(
        f"""\
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
        Expert=Invictus\\{stem}.ex5
        Symbol=XAUUSDc
        Period=M15
        Login=257385275
        Model=0
        ExecutionMode=0
        Optimization=0
        FromDate=2025.01.01
        ToDate=2026.04.15
        ForwardMode=0
        Report=\\Reports\\{stem}_XAUUSDc_M15_2025_2026
        ReplaceReport=1
        ShutdownTerminal=1
        Deposit=10000
        Currency=USD
        Leverage=1:100
        UseLocal=1
        UseRemote=0
        UseCloud=0
        Visual=0
        """
    )


def run_backtest(stem: str) -> tuple[Path, Path | None]:
    ini_path = MT5_BUILD / f"{stem}.backtest.ini"
    write_file(ini_path, build_ini(stem))
    shutil.copy2(MT5_BUILD / f"{stem}.ex5", MT5_EXPERTS / f"{stem}.ex5")

    report_path = REPORTS_DIR / f"{stem}_XAUUSDc_M15_2025_2026.htm"
    for old in REPORTS_DIR.glob(f"{stem}_XAUUSDc_M15_2025_2026*"):
        old.unlink(missing_ok=True)

    pre_log = latest_tester_log()
    pre_size = pre_log.stat().st_size if pre_log and pre_log.exists() else 0
    proc = launch_subprocess([WINE, TERMINAL_EXE, f"/config:C:\\MT5Build\\{stem}.backtest.ini"])
    start_time = time.time()
    stable_size = -1
    stable_hits = 0
    deadline = time.time() + 480
    active_log: Path | None = pre_log

    while time.time() < deadline:
        current_log = latest_tester_log()
        if(current_log := latest_tester_log()) is not None:
            active_log = current_log

        if report_path.exists():
            stat = report_path.stat()
            if stat.st_mtime >= start_time:
                log_done = False
                if active_log and active_log.exists():
                    raw_bytes = active_log.read_bytes()
                    tail_text = raw_bytes[pre_size:].decode("utf-16le", errors="ignore") if active_log == pre_log else raw_bytes.decode("utf-16le", errors="ignore")
                    if "automatical testing finished" in tail_text:
                        log_done = True

                if stat.st_size == stable_size:
                    stable_hits += 1
                else:
                    stable_size = stat.st_size
                    stable_hits = 0

                if log_done and stable_hits >= 2:
                    break
        time.sleep(2)

    if proc.poll() is None:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=10)

    if not report_path.exists():
        raise RuntimeError(f"Missing report for {stem}")
    return report_path, active_log


def parse_report(report_path: Path) -> dict[str, float]:
    text = report_path.read_bytes().decode("utf-16le", errors="ignore")
    plain = re.sub(r"<[^>]+>", " ", text).replace("\xa0", " ")
    plain = re.sub(r"\s+", " ", plain)

    def extract(key: str) -> str:
        match = re.search(re.escape(key) + r"\s*([^:]{1,90})", plain)
        if not match:
            raise RuntimeError(f"Failed to parse {key} from {report_path}")
        return match.group(1).strip()

    def first_number(value: str) -> float:
        match = re.search(r"-?[\d ]+(?:\.\d+)?", value)
        if not match:
            raise RuntimeError(f"No numeric value in {value!r}")
        return float(match.group(0).replace(" ", ""))

    def first_pct(value: str) -> float:
        match = re.search(r"\(([\d.]+)%\)", value)
        if not match:
            raise RuntimeError(f"No percentage value in {value!r}")
        return float(match.group(1))

    return {
        "net_profit": first_number(extract("Total Net Profit:")),
        "profit_factor": first_number(extract("Profit Factor:")),
        "expected_payoff": first_number(extract("Expected Payoff:")),
        "recovery_factor": first_number(extract("Recovery Factor:")),
        "total_trades": first_number(extract("Total Trades:")),
        "profit_trades_pct": first_pct(extract("Profit Trades (% of total):")),
        "loss_trades_pct": first_pct(extract("Loss Trades (% of total):")),
        "balance_dd_abs": first_number(extract("Balance Drawdown Maximal:")),
        "balance_dd_pct": first_pct(extract("Balance Drawdown Maximal:")),
        "equity_dd_abs": first_number(extract("Equity Drawdown Maximal:")),
        "equity_dd_pct": first_pct(extract("Equity Drawdown Maximal:")),
    }


def parse_diag_line(log_path: Path | None, prefix: str) -> dict[str, float]:
    if log_path is None or not log_path.exists():
        return {}
    text = log_path.read_bytes().decode("utf-16le", errors="ignore")
    lines = [line for line in text.splitlines() if prefix in line]
    if not lines:
        return {}
    line = lines[-1]
    pairs = re.findall(r"([A-Za-z]+)=(-?[\d.]+)", line)
    return {key: float(value) for key, value in pairs}


def acceptable(metrics: dict[str, float]) -> bool:
    return metrics["profit_factor"] >= 1.18 and metrics["total_trades"] >= 3200 and metrics["equity_dd_pct"] <= 28.0


def score(metrics: dict[str, float]) -> float:
    dd_penalty = 1.0 + max(0.0, metrics["equity_dd_pct"] - 22.5) / 6.5
    wr_factor = max(metrics["profit_trades_pct"], 45.0) / 50.0
    return metrics["net_profit"] * metrics["profit_factor"] * wr_factor / dd_penalty


def better(metrics: dict[str, float], best: dict[str, float]) -> bool:
    if not acceptable(metrics):
        return False
    if not acceptable(best):
        return True
    if metrics["net_profit"] > best["net_profit"] * 1.01 and metrics["equity_dd_pct"] <= best["equity_dd_pct"] + 1.25 and metrics["profit_factor"] >= best["profit_factor"] - 0.01:
        return True
    if metrics["net_profit"] >= best["net_profit"] * 0.997 and metrics["equity_dd_pct"] <= best["equity_dd_pct"] - 1.0 and metrics["profit_factor"] >= best["profit_factor"] - 0.01:
        return True
    if metrics["profit_factor"] >= best["profit_factor"] + 0.02 and metrics["equity_dd_pct"] <= best["equity_dd_pct"] and metrics["net_profit"] >= best["net_profit"] * 0.98:
        return True
    if metrics["profit_trades_pct"] >= best["profit_trades_pct"] + 0.20 and metrics["net_profit"] >= best["net_profit"] * 0.99 and metrics["equity_dd_pct"] <= best["equity_dd_pct"] + 0.8:
        return True
    return score(metrics) > score(best) * 1.015


def summarize_takeaway(metrics: dict[str, float], best: dict[str, float], v4_buy: dict[str, float]) -> str:
    if not acceptable(metrics):
        if metrics["equity_dd_pct"] > 28.0:
            return "Ditolak: drawdown melewati guardrail."
        if metrics["profit_factor"] < 1.18:
            return "Ditolak: profit factor terlalu turun."
        if metrics["total_trades"] < 3200:
            return "Ditolak: trade count turun terlalu jauh."
        return "Ditolak: gagal guardrail utama."
    if metrics["net_profit"] > best["net_profit"] and metrics["equity_dd_pct"] <= best["equity_dd_pct"] + 1.25:
        return "Promising: profit naik tanpa merusak risk terlalu banyak."
    if metrics["equity_dd_pct"] < best["equity_dd_pct"] and metrics["net_profit"] >= best["net_profit"] * 0.99:
        return "Promising: risk turun dengan profit tetap dekat baseline."
    if metrics["profit_trades_pct"] > best["profit_trades_pct"] and metrics["net_profit"] >= best["net_profit"] * 0.985:
        return "Promising: hit-rate naik dengan penalty profit terbatas."
    if v4_buy.get("premium", 0.0) > 0.0:
        return "Entry premium cap aktif, tapi edge total belum cukup kuat."
    if v4_buy.get("break", 0.0) > 0.0 or v4_buy.get("bosq", 0.0) > 0.0:
        return "Buy filter struktural aktif, tetapi terlalu banyak opportunity yang terpotong."
    return "Netral: ada sinyal perbaikan lokal, tetapi belum mengalahkan champion."


def write_summary(results: list[IterationResult], champion: IterationResult) -> None:
    json_path = RUN_DIR / "v4_20x_results.json"
    md_path = RUN_DIR / "v4_20x_summary.md"
    notes_path = RUN_DIR / "v4_20x_notes.md"

    json_path.write_text(
        json.dumps(
            {
                "generated_at": datetime.now().isoformat(),
                "champion": champion.index,
                "results": [
                    {
                        "index": r.index,
                        "name": r.name,
                        "hypothesis": r.hypothesis,
                        "accepted": r.accepted,
                        "takeaway": r.takeaway,
                        "params": r.params,
                        "metrics": r.metrics,
                        "trend_diag": r.trend_diag,
                        "trend_dir_diag": r.trend_dir_diag,
                        "trend_score_diag": r.trend_score_diag,
                        "v4_buy_diag": r.v4_buy_diag,
                        "tester_log": r.tester_log,
                    }
                    for r in results
                ],
            },
            indent=2,
        )
    )

    lines = [
        "# v4 20x Summary",
        "",
        f"Champion: iterasi {champion.index:02d} `{champion.name}`",
        f"Guardrail: PF >= 1.18, trades >= 3200, equity DD <= 28.0%",
        "",
        "| Iter | Name | Accepted | Net Profit | PF | WR | Trades | Eq DD | Buy PnL | break | bosq | premium | tests | fvg | Takeaway |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for r in results:
        lines.append(
            f"| {r.index:02d} | {r.name} | {'yes' if r.accepted else 'no'} | {r.metrics['net_profit']:.2f} | "
            f"{r.metrics['profit_factor']:.2f} | {r.metrics['profit_trades_pct']:.2f}% | {int(r.metrics['total_trades'])} | "
            f"{r.metrics['equity_dd_pct']:.2f}% | {r.trend_dir_diag.get('buyPnl', 0.0):.2f} | "
            f"{int(r.v4_buy_diag.get('break', 0.0))} | {int(r.v4_buy_diag.get('bosq', 0.0))} | "
            f"{int(r.v4_buy_diag.get('premium', 0.0))} | {int(r.v4_buy_diag.get('tests', 0.0))} | {int(r.v4_buy_diag.get('fvg', 0.0))} | {r.takeaway} |"
        )
    md_path.write_text("\n".join(lines) + "\n")

    notes = [
        "# v4 Notes",
        "",
        f"Champion: `{champion.name}`",
        f"- Net profit: {champion.metrics['net_profit']:.2f}",
        f"- Profit factor: {champion.metrics['profit_factor']:.2f}",
        f"- Win rate: {champion.metrics['profit_trades_pct']:.2f}%",
        f"- Trades: {int(champion.metrics['total_trades'])}",
        f"- Equity DD: {champion.metrics['equity_dd_pct']:.2f}%",
        f"- Buy direction pnl: {champion.trend_dir_diag.get('buyPnl', 0.0):.2f}",
        f"- v4 buy diag: {champion.v4_buy_diag}",
    ]
    notes_path.write_text("\n".join(notes) + "\n")


def main() -> None:
    template = EA_SOURCE.read_text()
    current_params = dict(BASE_PARAMS)
    results: list[IterationResult] = []
    champion_result: IterationResult | None = None
    champion_metrics: dict[str, float] | None = None

    for idx, plan in enumerate(ITERATIONS, start=1):
        params = dict(current_params)
        params.update(plan["changes"])
        stem = f"InvictusForward1M15_v4_iter{idx:02d}"
        source_text = patch_source(template, params)
        compile_variant(stem, source_text)
        report_path, tester_log = run_backtest(stem)
        metrics = parse_report(report_path)
        trend_diag = parse_diag_line(tester_log, "IF1 diag trend:")
        trend_dir_diag = parse_diag_line(tester_log, "IF1 diag trendDir:")
        trend_score_diag = parse_diag_line(tester_log, "IF1 diag trendScore:")
        v4_buy_diag = parse_diag_line(tester_log, "IF1 diag v4buy:")

        if champion_metrics is None:
            accepted = acceptable(metrics)
            takeaway = "Baseline champion awal."
        else:
            accepted = better(metrics, champion_metrics)
            takeaway = summarize_takeaway(metrics, champion_metrics, v4_buy_diag)

        result = IterationResult(
            index=idx,
            name=plan["name"],
            hypothesis=plan["hypothesis"],
            params=params,
            metrics=metrics,
            tester_log=str(tester_log) if tester_log else "",
            trend_diag=trend_diag,
            trend_dir_diag=trend_dir_diag,
            trend_score_diag=trend_score_diag,
            v4_buy_diag=v4_buy_diag,
            accepted=accepted,
            takeaway=takeaway,
        )
        results.append(result)

        if champion_metrics is None or accepted:
            current_params = dict(params)
            champion_metrics = dict(metrics)
            champion_result = result
            result.accepted = True
            if idx != 1:
                result.takeaway = "Dibawa ke baseline berikutnya."

        print(
            f"[{idx:02d}/{len(ITERATIONS):02d}] {plan['name']}: "
            f"net={metrics['net_profit']:.2f} pf={metrics['profit_factor']:.2f} "
            f"wr={metrics['profit_trades_pct']:.2f}% trades={int(metrics['total_trades'])} "
            f"eqdd={metrics['equity_dd_pct']:.2f}% {'ACCEPT' if result.accepted else 'reject'}",
            flush=True,
        )

    if champion_result is None:
        raise RuntimeError("No champion result recorded")

    write_summary(results, champion_result)
    print()
    print(f"Champion iteration: {champion_result.index:02d} {champion_result.name}")
    print(f"Champion net profit: {champion_result.metrics['net_profit']:.2f}")
    print(f"Champion PF: {champion_result.metrics['profit_factor']:.2f}")
    print(f"Champion WR: {champion_result.metrics['profit_trades_pct']:.2f}%")
    print(f"Champion trades: {int(champion_result.metrics['total_trades'])}")
    print(f"Champion equity DD: {champion_result.metrics['equity_dd_pct']:.2f}%")


if __name__ == "__main__":
    main()
