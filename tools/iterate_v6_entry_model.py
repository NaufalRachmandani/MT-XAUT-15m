#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

ROOT = Path("/Users/naufalrachmandani/Hobby/MT5 XAU 15m")
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.compare_versions_6m_100 import compile_variant, parse_report, run_backtest


RUN_DIR = ROOT / "build" / "v6_entry_model_round1"
RUN_DIR.mkdir(parents=True, exist_ok=True)

SOURCE = ROOT / "mt5" / "InvictusForward1M15_v6.mq5"
RECENT_FROM = "2025.10.18"
RECENT_TO = "2026.04.15"
DEPOSIT = 100
LEVERAGE = "1:100"


@dataclass(frozen=True)
class Preset:
    name: str
    note: str
    overrides: dict[str, str]


@dataclass
class SweepResult:
    preset: str
    note: str
    report_path: str
    tester_log: str
    net_profit: float
    profit_pct: float
    profit_factor: float
    expected_payoff: float
    total_trades: int
    win_rate: float
    balance_dd_pct: float
    equity_dd_pct: float
    score: float
    trend_closed_pnl: float = 0.0
    sideways_closed_pnl: float = 0.0
    trend_buy_pnl: float = 0.0
    trend_sell_pnl: float = 0.0
    trend_low_pnl: float = 0.0
    trend_mid_pnl: float = 0.0
    trend_high_pnl: float = 0.0
    trend_tp_pnl: float = 0.0
    trend_sl_pnl: float = 0.0
    sell_low_pnl: float = 0.0
    sell_mid_pnl: float = 0.0
    sell_high_pnl: float = 0.0
    worst_buy_hours: str = ""
    worst_sell_hours: str = ""
    buy_break_blocked: int = 0
    buy_bosq_blocked: int = 0
    buy_premium_blocked: int = 0
    buy_tests_blocked: int = 0
    buy_fvg_blocked: int = 0


PRESETS = [
    Preset(
        "baseline_b_r175",
        "Aggressive sizing champion from the previous risk sweep.",
        {
            "V6_TrendRiskPercent": "1.75",
            "V6_SidewaysRiskPercent": "0.80",
            "V6_SellRiskMultiplier": "0.85",
            "V6_HighScoreBuyRiskMultiplier": "1.15",
            "V6_TrendDailyLossCapPercent": "6.0",
            "V6_SidewaysDailyLossCapPercent": "4.0",
        },
    ),
    Preset(
        "buy_break_036",
        "Require stronger bullish BOS break distance for buy entries.",
        {
            "V6_TrendRiskPercent": "1.75",
            "V6_SidewaysRiskPercent": "0.80",
            "V6_SellRiskMultiplier": "0.85",
            "V6_HighScoreBuyRiskMultiplier": "1.15",
            "V6_TrendDailyLossCapPercent": "6.0",
            "V6_SidewaysDailyLossCapPercent": "4.0",
            "IF1_BUY_MIN_BREAK_ATR_OVERRIDE": "0.36",
        },
    ),
    Preset(
        "buy_break_042",
        "Push bullish BOS break threshold higher.",
        {
            "V6_TrendRiskPercent": "1.75",
            "V6_SidewaysRiskPercent": "0.80",
            "V6_SellRiskMultiplier": "0.85",
            "V6_HighScoreBuyRiskMultiplier": "1.15",
            "V6_TrendDailyLossCapPercent": "6.0",
            "V6_SidewaysDailyLossCapPercent": "4.0",
            "IF1_BUY_MIN_BREAK_ATR_OVERRIDE": "0.42",
        },
    ),
    Preset(
        "buy_break_048",
        "Very selective bullish break requirement.",
        {
            "V6_TrendRiskPercent": "1.75",
            "V6_SidewaysRiskPercent": "0.80",
            "V6_SellRiskMultiplier": "0.85",
            "V6_HighScoreBuyRiskMultiplier": "1.15",
            "V6_TrendDailyLossCapPercent": "6.0",
            "V6_SidewaysDailyLossCapPercent": "4.0",
            "IF1_BUY_MIN_BREAK_ATR_OVERRIDE": "0.48",
        },
    ),
    Preset(
        "buy_premium_025",
        "Reject market buys that are too far above the zone.",
        {
            "V6_TrendRiskPercent": "1.75",
            "V6_SidewaysRiskPercent": "0.80",
            "V6_SellRiskMultiplier": "0.85",
            "V6_HighScoreBuyRiskMultiplier": "1.15",
            "V6_TrendDailyLossCapPercent": "6.0",
            "V6_SidewaysDailyLossCapPercent": "4.0",
            "IF1_BUY_MAX_ENTRY_PREMIUM_ATR_OVERRIDE": "0.25",
            "IF1_BUY_ENTRY_PREMIUM_SCORE_LIMIT_OVERRIDE": "94",
        },
    ),
    Preset(
        "buy_premium_015",
        "Tighter anti-chase gate for market buys.",
        {
            "V6_TrendRiskPercent": "1.75",
            "V6_SidewaysRiskPercent": "0.80",
            "V6_SellRiskMultiplier": "0.85",
            "V6_HighScoreBuyRiskMultiplier": "1.15",
            "V6_TrendDailyLossCapPercent": "6.0",
            "V6_SidewaysDailyLossCapPercent": "4.0",
            "IF1_BUY_MAX_ENTRY_PREMIUM_ATR_OVERRIDE": "0.15",
            "IF1_BUY_ENTRY_PREMIUM_SCORE_LIMIT_OVERRIDE": "94",
        },
    ),
    Preset(
        "low_buy_fvg",
        "Low-score buys must also have FVG support.",
        {
            "V6_TrendRiskPercent": "1.75",
            "V6_SidewaysRiskPercent": "0.80",
            "V6_SellRiskMultiplier": "0.85",
            "V6_HighScoreBuyRiskMultiplier": "1.15",
            "V6_TrendDailyLossCapPercent": "6.0",
            "V6_SidewaysDailyLossCapPercent": "4.0",
            "IF1_BUY_LOW_SCORE_REQUIRE_FVG": "true",
        },
    ),
    Preset(
        "high_buy_impulsive",
        "High-score buys must come from impulsive BOS.",
        {
            "V6_TrendRiskPercent": "1.75",
            "V6_SidewaysRiskPercent": "0.80",
            "V6_SellRiskMultiplier": "0.85",
            "V6_HighScoreBuyRiskMultiplier": "1.15",
            "V6_TrendDailyLossCapPercent": "6.0",
            "V6_SidewaysDailyLossCapPercent": "4.0",
            "IF1_GOLD_HIGH_SCORE_BUY_REQUIRE_IMPULSIVE_BOS": "true",
        },
    ),
    Preset(
        "high_buy_rr_280",
        "Extend TP for the strongest buy setups.",
        {
            "V6_TrendRiskPercent": "1.75",
            "V6_SidewaysRiskPercent": "0.80",
            "V6_SellRiskMultiplier": "0.85",
            "V6_HighScoreBuyRiskMultiplier": "1.15",
            "V6_TrendDailyLossCapPercent": "6.0",
            "V6_SidewaysDailyLossCapPercent": "4.0",
            "IF1_TREND_HIGH_SCORE_BUY_RR_OVERRIDE": "2.80",
        },
    ),
    Preset(
        "high_buy_rr_320",
        "Push strongest buy TP even further.",
        {
            "V6_TrendRiskPercent": "1.75",
            "V6_SidewaysRiskPercent": "0.80",
            "V6_SellRiskMultiplier": "0.85",
            "V6_HighScoreBuyRiskMultiplier": "1.15",
            "V6_TrendDailyLossCapPercent": "6.0",
            "V6_SidewaysDailyLossCapPercent": "4.0",
            "IF1_TREND_HIGH_SCORE_BUY_RR_OVERRIDE": "3.20",
        },
    ),
    Preset(
        "boost_min_90",
        "Reserve boosted RR only for stronger scores.",
        {
            "V6_TrendRiskPercent": "1.75",
            "V6_SidewaysRiskPercent": "0.80",
            "V6_SellRiskMultiplier": "0.85",
            "V6_HighScoreBuyRiskMultiplier": "1.15",
            "V6_TrendDailyLossCapPercent": "6.0",
            "V6_SidewaysDailyLossCapPercent": "4.0",
            "IF1_SCORE_RR_BOOST_MIN_OVERRIDE": "90",
        },
    ),
    Preset(
        "low_buy_rr_125",
        "Reduce TP on low-score buys to improve conversion.",
        {
            "V6_TrendRiskPercent": "1.75",
            "V6_SidewaysRiskPercent": "0.80",
            "V6_SellRiskMultiplier": "0.85",
            "V6_HighScoreBuyRiskMultiplier": "1.15",
            "V6_TrendDailyLossCapPercent": "6.0",
            "V6_SidewaysDailyLossCapPercent": "4.0",
            "IF1_BUY_LOW_SCORE_RR_OVERRIDE": "1.25",
        },
    ),
    Preset(
        "sell_score_85",
        "Cut low-score sells entirely.",
        {
            "V6_TrendRiskPercent": "1.75",
            "V6_SidewaysRiskPercent": "0.80",
            "V6_SellRiskMultiplier": "0.85",
            "V6_HighScoreBuyRiskMultiplier": "1.15",
            "V6_TrendDailyLossCapPercent": "6.0",
            "V6_SidewaysDailyLossCapPercent": "4.0",
            "IF1_SCORE_SELL_MIN_OVERRIDE": "85",
        },
    ),
    Preset(
        "sell_tame_060",
        "Scale total sell risk down further.",
        {
            "V6_TrendRiskPercent": "1.75",
            "V6_SidewaysRiskPercent": "0.80",
            "V6_SellRiskMultiplier": "0.60",
            "V6_HighScoreBuyRiskMultiplier": "1.15",
            "V6_TrendDailyLossCapPercent": "6.0",
            "V6_SidewaysDailyLossCapPercent": "4.0",
        },
    ),
    Preset(
        "sell_low_015",
        "Heavily shrink low-score sell exposure only.",
        {
            "V6_TrendRiskPercent": "1.75",
            "V6_SidewaysRiskPercent": "0.80",
            "V6_SellRiskMultiplier": "0.85",
            "V6_HighScoreBuyRiskMultiplier": "1.15",
            "V6_TrendDailyLossCapPercent": "6.0",
            "V6_SidewaysDailyLossCapPercent": "4.0",
            "V6_LowScoreSellRiskMultiplier": "0.15",
        },
    ),
    Preset(
        "sideways_half",
        "Reduce sideways participation while keeping the regime active.",
        {
            "V6_TrendRiskPercent": "1.75",
            "V6_SidewaysRiskPercent": "0.40",
            "V6_SellRiskMultiplier": "0.85",
            "V6_HighScoreBuyRiskMultiplier": "1.15",
            "V6_TrendDailyLossCapPercent": "6.0",
            "V6_SidewaysDailyLossCapPercent": "4.0",
        },
    ),
    Preset(
        "sideways_off",
        "Remove sideways exposure and let trend carry the system.",
        {
            "V6_TrendRiskPercent": "1.75",
            "V6_SidewaysRiskPercent": "0.00",
            "V6_SellRiskMultiplier": "0.85",
            "V6_HighScoreBuyRiskMultiplier": "1.15",
            "V6_TrendDailyLossCapPercent": "6.0",
            "V6_SidewaysDailyLossCapPercent": "4.0",
        },
    ),
    Preset(
        "combo_quality_a",
        "Break + anti-chase + FVG for weak buys.",
        {
            "V6_TrendRiskPercent": "1.75",
            "V6_SidewaysRiskPercent": "0.80",
            "V6_SellRiskMultiplier": "0.85",
            "V6_HighScoreBuyRiskMultiplier": "1.15",
            "V6_TrendDailyLossCapPercent": "6.0",
            "V6_SidewaysDailyLossCapPercent": "4.0",
            "IF1_BUY_MIN_BREAK_ATR_OVERRIDE": "0.36",
            "IF1_BUY_MAX_ENTRY_PREMIUM_ATR_OVERRIDE": "0.25",
            "IF1_BUY_ENTRY_PREMIUM_SCORE_LIMIT_OVERRIDE": "94",
            "IF1_BUY_LOW_SCORE_REQUIRE_FVG": "true",
        },
    ),
    Preset(
        "combo_quality_b",
        "Break + anti-chase + impulsive high-score buy.",
        {
            "V6_TrendRiskPercent": "1.75",
            "V6_SidewaysRiskPercent": "0.80",
            "V6_SellRiskMultiplier": "0.85",
            "V6_HighScoreBuyRiskMultiplier": "1.15",
            "V6_TrendDailyLossCapPercent": "6.0",
            "V6_SidewaysDailyLossCapPercent": "4.0",
            "IF1_BUY_MIN_BREAK_ATR_OVERRIDE": "0.36",
            "IF1_BUY_MAX_ENTRY_PREMIUM_ATR_OVERRIDE": "0.20",
            "IF1_BUY_ENTRY_PREMIUM_SCORE_LIMIT_OVERRIDE": "94",
            "IF1_GOLD_HIGH_SCORE_BUY_REQUIRE_IMPULSIVE_BOS": "true",
        },
    ),
    Preset(
        "combo_quality_c",
        "Quality buy filters plus higher RR and tamer sells.",
        {
            "V6_TrendRiskPercent": "1.75",
            "V6_SidewaysRiskPercent": "0.80",
            "V6_SellRiskMultiplier": "0.60",
            "V6_HighScoreBuyRiskMultiplier": "1.15",
            "V6_TrendDailyLossCapPercent": "6.0",
            "V6_SidewaysDailyLossCapPercent": "4.0",
            "IF1_BUY_MIN_BREAK_ATR_OVERRIDE": "0.36",
            "IF1_BUY_MAX_ENTRY_PREMIUM_ATR_OVERRIDE": "0.25",
            "IF1_BUY_ENTRY_PREMIUM_SCORE_LIMIT_OVERRIDE": "94",
            "IF1_TREND_HIGH_SCORE_BUY_RR_OVERRIDE": "2.80",
        },
    ),
    Preset(
        "combo_quality_d",
        "Quality buys plus removal of low-score sells.",
        {
            "V6_TrendRiskPercent": "1.75",
            "V6_SidewaysRiskPercent": "0.80",
            "V6_SellRiskMultiplier": "0.85",
            "V6_HighScoreBuyRiskMultiplier": "1.15",
            "V6_TrendDailyLossCapPercent": "6.0",
            "V6_SidewaysDailyLossCapPercent": "4.0",
            "IF1_BUY_MIN_BREAK_ATR_OVERRIDE": "0.36",
            "IF1_BUY_MAX_ENTRY_PREMIUM_ATR_OVERRIDE": "0.20",
            "IF1_BUY_ENTRY_PREMIUM_SCORE_LIMIT_OVERRIDE": "94",
            "IF1_BUY_LOW_SCORE_REQUIRE_FVG": "true",
            "IF1_SCORE_SELL_MIN_OVERRIDE": "85",
        },
    ),
]


def replace_symbol_value(text: str, name: str, value: str) -> str:
    patterns = [
        re.compile(rf"^input\s+([^\n]*\b{name}\b)\s*=\s*[^;]+;", re.MULTILINE),
        re.compile(rf"^static const\s+([^\n]*\b{name}\b)\s*=\s*[^;]+;", re.MULTILINE),
    ]
    for pattern in patterns:
        new_text, count = pattern.subn(rf"{pattern.pattern.split(r'\\s+')[0].replace('^', '')} \1 = {value};", text, count=1)
        if count == 1:
            return new_text
    raise RuntimeError(f"Failed to replace {name}")


def replace_named_value(text: str, name: str, value: str) -> str:
    input_pattern = re.compile(rf"^(input\s+[^\n]*\b{name}\b)\s*=\s*[^;]+;", re.MULTILINE)
    text, count = input_pattern.subn(rf"\1 = {value};", text, count=1)
    if count == 1:
        return text
    const_pattern = re.compile(rf"^(static const\s+[^\n]*\b{name}\b)\s*=\s*[^;]+;", re.MULTILINE)
    text, count = const_pattern.subn(rf"\1 = {value};", text, count=1)
    if count == 1:
        return text
    raise RuntimeError(f"Failed to replace {name}")


def build_source_for_preset(preset: Preset) -> Path:
    text = SOURCE.read_text()
    for name, value in preset.overrides.items():
        text = replace_named_value(text, name, value)
    temp_path = RUN_DIR / f"InvictusForward1M15_v6_{preset.name}.mq5"
    temp_path.write_text(text)
    return(temp_path)


def parse_float_map(line: str) -> dict[str, float]:
    return {key: float(value) for key, value in re.findall(r"([A-Za-z]+)=(-?\d+(?:\.\d+)?)", line)}


def parse_hour_stats(line: str) -> list[tuple[int, int, int, float]]:
    rows: list[tuple[int, int, int, float]] = []
    for hour, wins, losses, pnl in re.findall(r"h(\d{2})=(\d+)\/(\d+)\/(-?\d+(?:\.\d+)?)", line):
        rows.append((int(hour), int(wins), int(losses), float(pnl)))
    return rows


def summarize_worst_hours(line: str, limit: int = 3) -> str:
    rows = parse_hour_stats(line)
    negatives = [row for row in rows if row[3] < 0.0]
    negatives.sort(key=lambda row: row[3])
    return ", ".join(f"h{hour:02d} {pnl:.2f}" for hour, _, _, pnl in negatives[:limit])


def result_score(metrics: dict[str, float], diag: dict[str, float]) -> float:
    profit = metrics["net_profit"]
    pf_bonus = max(metrics["profit_factor"] - 1.0, 0.0) * 180.0
    dd_penalty = metrics["equity_dd_pct"] * 0.95
    sell_penalty = max(-diag.get("trend_sell_pnl", 0.0), 0.0) * 0.20
    return profit + pf_bonus - dd_penalty - sell_penalty


def analyze_diag(log_path: Path, stem: str) -> dict[str, object]:
    result: dict[str, object] = {}
    text = log_path.read_bytes().decode("utf-16le", errors="ignore")
    start_needle = f"Experts\\\\Invictus\\\\{stem}.ex5"
    start = text.rfind(start_needle)
    if start < 0:
        return result

    for match in re.finditer(r"IF1 diag [^\r\n]*", text[start:]):
        line = match.group(0).strip()
        if "IF1 diag trend:" in line:
            values = parse_float_map(line)
            result["trend_closed_pnl"] = values.get("closedPnl", 0.0)
        elif "IF1 diag sideways:" in line:
            values = parse_float_map(line)
            result["sideways_closed_pnl"] = values.get("closedPnl", 0.0)
        elif "IF1 diag trendDir:" in line:
            values = parse_float_map(line)
            result["trend_buy_pnl"] = values.get("buyPnl", 0.0)
            result["trend_sell_pnl"] = values.get("sellPnl", 0.0)
        elif "IF1 diag sellScore:" in line:
            values = parse_float_map(line)
            result["sell_low_pnl"] = values.get("lowPnl", 0.0)
            result["sell_mid_pnl"] = values.get("midPnl", 0.0)
            result["sell_high_pnl"] = values.get("highPnl", 0.0)
        elif "IF1 diag trendScore:" in line:
            values = parse_float_map(line)
            result["trend_low_pnl"] = values.get("lowPnl", 0.0)
            result["trend_mid_pnl"] = values.get("midPnl", 0.0)
            result["trend_high_pnl"] = values.get("highPnl", 0.0)
        elif "IF1 diag trendExit:" in line:
            values = parse_float_map(line)
            result["trend_tp_pnl"] = values.get("tpPnl", 0.0)
            result["trend_sl_pnl"] = values.get("slPnl", 0.0)
        elif "IF1 diag v4buy:" in line:
            values = parse_float_map(line)
            result["buy_break_blocked"] = int(values.get("break", 0.0))
            result["buy_bosq_blocked"] = int(values.get("bosq", 0.0))
            result["buy_premium_blocked"] = int(values.get("premium", 0.0))
            result["buy_tests_blocked"] = int(values.get("tests", 0.0))
            result["buy_fvg_blocked"] = int(values.get("fvg", 0.0))
        elif "IF1 diag buyHour:" in line:
            result["worst_buy_hours"] = summarize_worst_hours(line)
        elif "IF1 diag sellHour:" in line:
            result["worst_sell_hours"] = summarize_worst_hours(line)
    return result


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        return
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    results: list[SweepResult] = []

    for preset in PRESETS:
        source_path = build_source_for_preset(preset)
        stem = compile_variant("v6", source_path, f"entry_{preset.name}")
        print(f"[compile] {preset.name} -> {stem}", flush=True)

        report_path, tester_log = run_backtest(stem, RECENT_FROM, RECENT_TO, DEPOSIT, LEVERAGE)
        metrics = parse_report(report_path)
        diag = analyze_diag(tester_log, stem) if tester_log else {}

        results.append(
            SweepResult(
                preset=preset.name,
                note=preset.note,
                report_path=str(report_path),
                tester_log=str(tester_log) if tester_log else "",
                net_profit=metrics["net_profit"],
                profit_pct=(metrics["net_profit"] / DEPOSIT) * 100.0,
                profit_factor=metrics["profit_factor"],
                expected_payoff=metrics["expected_payoff"],
                total_trades=int(metrics["total_trades"]),
                win_rate=metrics["win_rate"],
                balance_dd_pct=metrics["balance_dd_pct"],
                equity_dd_pct=metrics["equity_dd_pct"],
                score=result_score(metrics, diag),
                trend_closed_pnl=float(diag.get("trend_closed_pnl", 0.0)),
                sideways_closed_pnl=float(diag.get("sideways_closed_pnl", 0.0)),
                trend_buy_pnl=float(diag.get("trend_buy_pnl", 0.0)),
                trend_sell_pnl=float(diag.get("trend_sell_pnl", 0.0)),
                trend_low_pnl=float(diag.get("trend_low_pnl", 0.0)),
                trend_mid_pnl=float(diag.get("trend_mid_pnl", 0.0)),
                trend_high_pnl=float(diag.get("trend_high_pnl", 0.0)),
                trend_tp_pnl=float(diag.get("trend_tp_pnl", 0.0)),
                trend_sl_pnl=float(diag.get("trend_sl_pnl", 0.0)),
                sell_low_pnl=float(diag.get("sell_low_pnl", 0.0)),
                sell_mid_pnl=float(diag.get("sell_mid_pnl", 0.0)),
                sell_high_pnl=float(diag.get("sell_high_pnl", 0.0)),
                worst_buy_hours=str(diag.get("worst_buy_hours", "")),
                worst_sell_hours=str(diag.get("worst_sell_hours", "")),
                buy_break_blocked=int(diag.get("buy_break_blocked", 0)),
                buy_bosq_blocked=int(diag.get("buy_bosq_blocked", 0)),
                buy_premium_blocked=int(diag.get("buy_premium_blocked", 0)),
                buy_tests_blocked=int(diag.get("buy_tests_blocked", 0)),
                buy_fvg_blocked=int(diag.get("buy_fvg_blocked", 0)),
            )
        )
        current = results[-1]
        print(
            f"[result] {current.preset}: net={current.net_profit:.2f} pf={current.profit_factor:.2f} "
            f"wr={current.win_rate:.2f}% trades={current.total_trades} eqdd={current.equity_dd_pct:.2f}% "
            f"buy={current.trend_buy_pnl:.2f} sell={current.trend_sell_pnl:.2f} sideways={current.sideways_closed_pnl:.2f}",
            flush=True,
        )

    rows = [asdict(r) for r in results]
    (RUN_DIR / "results.json").write_text(json.dumps(rows, indent=2))
    write_csv(RUN_DIR / "results.csv", rows)

    ranked = sorted(results, key=lambda r: r.score, reverse=True)
    lines = [
        "# v6 Entry Model Round 1",
        "",
        f"Window: `{RECENT_FROM} - {RECENT_TO}`, `XAUUSDc`, `M15`, `Deposit {DEPOSIT} USD`, `Leverage {LEVERAGE}`, `Every tick`.",
        "",
        "| Rank | Preset | Net | Profit % | PF | WR | Trades | EqDD | Trend Buy | Trend Sell | Sideways | Score |",
        "| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for idx, item in enumerate(ranked, start=1):
        lines.append(
            f"| {idx} | {item.preset} | {item.net_profit:.2f} | {item.profit_pct:.2f}% | "
            f"{item.profit_factor:.2f} | {item.win_rate:.2f}% | {item.total_trades} | {item.equity_dd_pct:.2f}% | "
            f"{item.trend_buy_pnl:.2f} | {item.trend_sell_pnl:.2f} | {item.sideways_closed_pnl:.2f} | {item.score:.2f} |"
        )

    if ranked:
        champion = ranked[0]
        lines.extend(
            [
                "",
                "## Champion",
                "",
                f"- Preset: `{champion.preset}`",
                f"- Note: {champion.note}",
                f"- Net profit: `{champion.net_profit:.2f}`",
                f"- Profit factor: `{champion.profit_factor:.2f}`",
                f"- Win rate: `{champion.win_rate:.2f}%`",
                f"- Trades: `{champion.total_trades}`",
                f"- Equity DD: `{champion.equity_dd_pct:.2f}%`",
                f"- Trend buy PnL: `{champion.trend_buy_pnl:.2f}`",
                f"- Trend sell PnL: `{champion.trend_sell_pnl:.2f}`",
                f"- Sideways PnL: `{champion.sideways_closed_pnl:.2f}`",
                f"- Worst buy hours: `{champion.worst_buy_hours or 'n/a'}`",
                f"- Worst sell hours: `{champion.worst_sell_hours or 'n/a'}`",
                "",
                "## Files",
                f"- [results.json]({(RUN_DIR / 'results.json').as_posix()})",
                f"- [results.csv]({(RUN_DIR / 'results.csv').as_posix()})",
            ]
        )

    (RUN_DIR / "summary.md").write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
