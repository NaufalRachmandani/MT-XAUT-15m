#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import shutil
import re
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path

ROOT = Path("/Users/naufalrachmandani/Hobby/MT5 XAU 15m")
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.compare_versions_6m_100 import (
    MT5_BUILD,
    MT5_EXPERTS,
    REPORTS_DIR,
    TERMINAL_EXE,
    WINE,
    build_ini,
    compile_variant,
    launch_subprocess,
    parse_report,
)


RUN_DIR = ROOT / "build" / "v6_entry_model_round2"
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
class Result:
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


PRESETS = [
    Preset("baseline_champion", "Current v6 default champion.", {}),
    Preset("low_buy_rr125", "Compress TP only for low-score buys.", {
        "IF1_BUY_LOW_SCORE_RR_OVERRIDE": "1.25",
    }),
    Preset("high_buy_impulsive", "High-score buys must come from impulsive BOS.", {
        "IF1_GOLD_HIGH_SCORE_BUY_REQUIRE_IMPULSIVE_BOS": "true",
    }),
    Preset("buy_break_036", "Stronger buy break distance threshold.", {
        "IF1_BUY_MIN_BREAK_ATR_OVERRIDE": "0.36",
    }),
    Preset("buy_break_042", "Very strong buy break distance threshold.", {
        "IF1_BUY_MIN_BREAK_ATR_OVERRIDE": "0.42",
    }),
    Preset("low_buy_rr125_impulsive", "Low-score buy TP compression plus impulsive high-score buy.", {
        "IF1_BUY_LOW_SCORE_RR_OVERRIDE": "1.25",
        "IF1_GOLD_HIGH_SCORE_BUY_REQUIRE_IMPULSIVE_BOS": "true",
    }),
    Preset("low_buy_rr125_break036", "Low-score buy TP compression plus stronger break threshold.", {
        "IF1_BUY_LOW_SCORE_RR_OVERRIDE": "1.25",
        "IF1_BUY_MIN_BREAK_ATR_OVERRIDE": "0.36",
    }),
    Preset("high_buy_rr280", "Extend TP on strongest buys.", {
        "IF1_TREND_HIGH_SCORE_BUY_RR_OVERRIDE": "2.80",
    }),
    Preset("high_buy_rr280_lowrr", "Extend strong-buy TP and compress weak-buy TP.", {
        "IF1_TREND_HIGH_SCORE_BUY_RR_OVERRIDE": "2.80",
        "IF1_BUY_LOW_SCORE_RR_OVERRIDE": "1.25",
    }),
    Preset("boost_min_90", "Reserve boosted RR for stronger trend scores only.", {
        "IF1_SCORE_RR_BOOST_MIN_OVERRIDE": "90",
    }),
    Preset("trend_toxic_8_10", "Block the two worst recent trend hours globally.", {
        "IF1TrendToxicHoursOverride": "{3, 8, 10, 17}",
    }),
    Preset("trend_toxic_7_8_10", "Block the three worst recent buy hours globally.", {
        "IF1TrendToxicHoursOverride": "{3, 7, 8, 10, 17}",
    }),
    Preset("cooldown_2bars", "Longer cooldown to reduce cluster re-entry after losses.", {
        "IF1_COOLDOWN_BARS_OVERRIDE": "2",
        "IF1_ZONE_COOLDOWN_BARS_OVERRIDE": "2",
    }),
    Preset("sell_mult_100", "Restore full sell multiplier after score-85 cut.", {
        "V6_SellRiskMultiplier": "1.00",
    }),
    Preset("sell_mult_075", "Tame all remaining sells slightly.", {
        "V6_SellRiskMultiplier": "0.75",
    }),
    Preset("sideways_half", "Reduce sideways risk participation.", {
        "V6_SidewaysRiskPercent": "0.40",
    }),
    Preset("sideways_off", "Disable sideways participation entirely.", {
        "V6_SidewaysRiskPercent": "0.00",
    }),
    Preset("dailycap_5_3", "Tighten daily caps back down.", {
        "V6_TrendDailyLossCapPercent": "5.0",
        "V6_SidewaysDailyLossCapPercent": "3.0",
    }),
]


def replace_named_value(text: str, name: str, value: str) -> str:
    patterns = [
        re.compile(rf"^(input\s+[^\n]*\b{name}\b)\s*=\s*[^;]+;", re.MULTILINE),
        re.compile(rf"^(static const\s+[^\n]*\b{name}\b)\s*=\s*[^;]+;", re.MULTILINE),
        re.compile(rf"^(static int\s+[^\n]*\b{name}\b\[\])\s*=\s*[^;]+;", re.MULTILINE),
    ]
    for pattern in patterns:
        text, count = pattern.subn(rf"\1 = {value};", text, count=1)
        if count == 1:
            return text
    raise RuntimeError(f"Failed to replace {name}")


def build_source_for_preset(preset: Preset) -> Path:
    text = SOURCE.read_text()
    for name, value in preset.overrides.items():
        text = replace_named_value(text, name, value)
    path = RUN_DIR / f"InvictusForward1M15_v6_{preset.name}.mq5"
    path.write_text(text)
    return path


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        return
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def result_score(metrics: dict[str, float]) -> float:
    return (
        metrics["net_profit"]
        + max(metrics["profit_factor"] - 1.0, 0.0) * 180.0
        - metrics["equity_dd_pct"] * 0.95
    )


def run_backtest_safe(stem: str, from_date: str, to_date: str, deposit: int, leverage: str) -> tuple[Path, str]:
    ini_path = MT5_BUILD / f"{stem}.backtest.ini"
    ini_path.write_text(build_ini(stem, from_date, to_date, deposit, leverage))
    shutil.copy2(MT5_BUILD / f"{stem}.ex5", MT5_EXPERTS / f"{stem}.ex5")

    report_suffix = f"{from_date.replace('.', '')}_{to_date.replace('.', '')}"
    report_path = REPORTS_DIR / f"{stem}_XAUUSDc_M15_{report_suffix}.htm"
    for old in REPORTS_DIR.glob(f"{stem}_XAUUSDc_M15_{report_suffix}*"):
        old.unlink(missing_ok=True)

    start_time = time.time()
    proc = launch_subprocess([WINE, TERMINAL_EXE, f"/config:C:\\MT5Build\\{stem}.backtest.ini"])
    try:
        proc.wait(timeout=1200)
    except Exception:
        proc.kill()
        proc.wait(timeout=10)
        raise

    deadline = time.time() + 120
    while time.time() < deadline:
        if report_path.exists() and report_path.stat().st_mtime >= start_time:
            return report_path, ""
        time.sleep(1)

    raise RuntimeError(f"Missing report for {stem}")


def main() -> None:
    results: list[Result] = []
    for preset in PRESETS:
        source_path = build_source_for_preset(preset)
        stem = compile_variant("v6", source_path, f"round2_{preset.name}")
        print(f"[compile] {preset.name} -> {stem}", flush=True)
        report_path, tester_log = run_backtest_safe(stem, RECENT_FROM, RECENT_TO, DEPOSIT, LEVERAGE)
        metrics = parse_report(report_path)
        results.append(
            Result(
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
            )
        )
        row = results[-1]
        print(
            f"[result] {row.preset}: net={row.net_profit:.2f} pf={row.profit_factor:.2f} "
            f"wr={row.win_rate:.2f}% trades={row.total_trades} eqdd={row.equity_dd_pct:.2f}%",
            flush=True,
        )

    rows = [asdict(r) for r in results]
    (RUN_DIR / "results.json").write_text(json.dumps(rows, indent=2))
    write_csv(RUN_DIR / "results.csv", rows)

    ranked = sorted(results, key=lambda item: result_score({
        "net_profit": item.net_profit,
        "profit_factor": item.profit_factor,
        "equity_dd_pct": item.equity_dd_pct,
    }), reverse=True)
    lines = [
        "# v6 Entry Model Round 2",
        "",
        f"Window: `{RECENT_FROM} - {RECENT_TO}`, `XAUUSDc`, `M15`, `Deposit {DEPOSIT} USD`, `Leverage {LEVERAGE}`, `Every tick`.",
        "",
        "| Rank | Preset | Net | Profit % | PF | WR | Trades | EqDD |",
        "| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for idx, item in enumerate(ranked, start=1):
        lines.append(
            f"| {idx} | {item.preset} | {item.net_profit:.2f} | {item.profit_pct:.2f}% | "
            f"{item.profit_factor:.2f} | {item.win_rate:.2f}% | {item.total_trades} | {item.equity_dd_pct:.2f}% |"
        )
    (RUN_DIR / "summary.md").write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
