#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
import shutil
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


RUN_DIR = ROOT / "build" / "v7_round1"
RUN_DIR.mkdir(parents=True, exist_ok=True)

SOURCE = ROOT / "mt5" / "InvictusForward1M15_v7.mq5"
FROM_DATE = "2026.01.01"
TO_DATE = "2026.04.15"
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
    net_profit: float
    profit_pct: float
    profit_factor: float
    expected_payoff: float
    total_trades: int
    win_rate: float
    balance_dd_pct: float
    equity_dd_pct: float


PRESETS = [
    Preset("seed", "Current v7 seed.", {}),
    Preset("risk_090_030", "Raise both trend and sideways risk.", {
        "V7_TrendRiskPercent": "0.90",
        "V7_SidewaysRiskPercent": "0.30",
    }),
    Preset("risk_120_040", "More aggressive risk increase.", {
        "V7_TrendRiskPercent": "1.20",
        "V7_SidewaysRiskPercent": "0.40",
    }),
    Preset("risk_150_050", "Push exposure harder while keeping filters.", {
        "V7_TrendRiskPercent": "1.50",
        "V7_SidewaysRiskPercent": "0.50",
    }),
    Preset("risk_120_040_pos4", "Higher risk plus one extra trend slot.", {
        "V7_TrendRiskPercent": "1.20",
        "V7_SidewaysRiskPercent": "0.40",
        "V7_TrendMaxPositions": "4",
    }),
    Preset("risk_120_040_sell080", "Higher risk plus slightly looser sell haircut.", {
        "V7_TrendRiskPercent": "1.20",
        "V7_SidewaysRiskPercent": "0.40",
        "V7_SellRiskMultiplier": "0.80",
    }),
    Preset("risk_120_040_buy105", "Higher risk plus smaller high-score buy boost.", {
        "V7_TrendRiskPercent": "1.20",
        "V7_SidewaysRiskPercent": "0.40",
        "V7_HighScoreBuyRiskMultiplier": "1.05",
    }),
    Preset("risk_120_040_toxic_relax_11", "Re-open hour 11 only.", {
        "V7_TrendRiskPercent": "1.20",
        "V7_SidewaysRiskPercent": "0.40",
        "IF1TrendToxicHoursOverride": "{3, 7, 8, 9, 10, 17}",
    }),
    Preset("risk_120_040_toxic_relax_9_11", "Re-open hours 9 and 11.", {
        "V7_TrendRiskPercent": "1.20",
        "V7_SidewaysRiskPercent": "0.40",
        "IF1TrendToxicHoursOverride": "{3, 7, 8, 10, 17}",
    }),
    Preset("risk_120_040_buybreak_024", "Higher risk plus looser buy break threshold.", {
        "V7_TrendRiskPercent": "1.20",
        "V7_SidewaysRiskPercent": "0.40",
        "IF1_BUY_MIN_BREAK_ATR_OVERRIDE": "0.24",
    }),
    Preset("risk_120_040_sell80", "Higher risk plus slightly looser sell score gate.", {
        "V7_TrendRiskPercent": "1.20",
        "V7_SidewaysRiskPercent": "0.40",
        "IF1_SCORE_SELL_MIN_OVERRIDE": "80",
    }),
]


def replace_named_value(text: str, name: str, value: str) -> str:
    patterns = [
        re.compile(rf"^(input\s+[^\n]*\b{name}\b)\s*=\s*[^;]+;", re.MULTILINE),
        re.compile(rf"^(static const\s+[^\n]*\b{name}\b)\s*=\s*[^;]+;", re.MULTILINE),
        re.compile(rf"^(static int\s+[^\n]*\b{name}\b\[\])\s*=\s*[^;]+;", re.MULTILINE),
        re.compile(rf"^(static int\s+[^\n]*\b{name}\b)\s*=\s*[^;]+;", re.MULTILINE),
    ]
    for pattern in patterns:
        text, count = pattern.subn(rf"\1 = {value};", text, count=1)
        if count == 1:
            return text
    raise RuntimeError(f"Failed to replace {name}")


def build_source(preset: Preset) -> Path:
    text = SOURCE.read_text()
    for name, value in preset.overrides.items():
        text = replace_named_value(text, name, value)
    path = RUN_DIR / f"InvictusForward1M15_v7_{preset.name}.mq5"
    path.write_text(text)
    return path


def run_backtest_safe(stem: str) -> Path:
    ini_path = MT5_BUILD / f"{stem}.backtest.ini"
    ini_path.write_text(build_ini(stem, FROM_DATE, TO_DATE, DEPOSIT, LEVERAGE))
    shutil.copy2(MT5_BUILD / f"{stem}.ex5", MT5_EXPERTS / f"{stem}.ex5")

    suffix = f"{FROM_DATE.replace('.', '')}_{TO_DATE.replace('.', '')}"
    report_path = REPORTS_DIR / f"{stem}_XAUUSDc_M15_{suffix}.htm"
    for old in REPORTS_DIR.glob(f"{stem}_XAUUSDc_M15_{suffix}*"):
        old.unlink(missing_ok=True)

    start_time = time.time()
    proc = launch_subprocess([WINE, TERMINAL_EXE, f"/config:C:\\MT5Build\\{stem}.backtest.ini"])
    proc.wait(timeout=1200)

    deadline = time.time() + 120
    while time.time() < deadline:
        if report_path.exists() and report_path.stat().st_mtime >= start_time:
            return report_path
        time.sleep(1)
    raise RuntimeError(f"Missing report for {stem}")


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        return
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def score(row: Result) -> float:
    if row.equity_dd_pct > 20.0:
        return -100000.0 + row.net_profit
    return row.net_profit + max(row.profit_factor - 1.0, 0.0) * 120.0 - row.equity_dd_pct * 1.2


def main() -> None:
    results: list[Result] = []
    for preset in PRESETS:
        source_path = build_source(preset)
        stem = compile_variant("v7", source_path, f"round1_{preset.name}")
        print(f"[compile] {preset.name} -> {stem}", flush=True)
        report_path = run_backtest_safe(stem)
        metrics = parse_report(report_path)
        result = Result(
            preset=preset.name,
            note=preset.note,
            report_path=str(report_path),
            net_profit=metrics["net_profit"],
            profit_pct=(metrics["net_profit"] / DEPOSIT) * 100.0,
            profit_factor=metrics["profit_factor"],
            expected_payoff=metrics["expected_payoff"],
            total_trades=int(metrics["total_trades"]),
            win_rate=metrics["win_rate"],
            balance_dd_pct=metrics["balance_dd_pct"],
            equity_dd_pct=metrics["equity_dd_pct"],
        )
        results.append(result)
        print(
            f"[result] {result.preset}: net={result.net_profit:.2f} pf={result.profit_factor:.2f} "
            f"wr={result.win_rate:.2f}% trades={result.total_trades} eqdd={result.equity_dd_pct:.2f}%",
            flush=True,
        )

    rows = [asdict(r) for r in results]
    (RUN_DIR / "results.json").write_text(json.dumps(rows, indent=2))
    write_csv(RUN_DIR / "results.csv", rows)

    ranked = sorted(results, key=score, reverse=True)
    lines = [
        "# v7 Round 1",
        "",
        f"Window: `{FROM_DATE} - {TO_DATE}`, `XAUUSDc`, `M15`, `Deposit {DEPOSIT} USD`, `Leverage {LEVERAGE}`.",
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
