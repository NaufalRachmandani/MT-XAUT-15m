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


RUN_DIR = ROOT / "build" / "v6_entry_model_round4"
RUN_DIR.mkdir(parents=True, exist_ok=True)

SOURCE = ROOT / "mt5" / "InvictusForward1M15_v6.mq5"
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
    Preset("toxic_7_8_10_11", "Profit leader from round 3.", {
        "IF1TrendToxicHoursOverride": "{3, 7, 8, 10, 11, 17}",
    }),
    Preset("toxic_7_8_9_10_impulsive", "Best balanced round 3 preset.", {
        "IF1TrendToxicHoursOverride": "{3, 7, 8, 9, 10, 17}",
        "IF1_GOLD_HIGH_SCORE_BUY_REQUIRE_IMPULSIVE_BOS": "true",
    }),
    Preset("toxic_7_8_10_11_impulsive", "Profit leader plus impulsive high-score buys.", {
        "IF1TrendToxicHoursOverride": "{3, 7, 8, 10, 11, 17}",
        "IF1_GOLD_HIGH_SCORE_BUY_REQUIRE_IMPULSIVE_BOS": "true",
    }),
    Preset("toxic_7_8_9_10_11", "Block the full bad morning cluster plus 11.", {
        "IF1TrendToxicHoursOverride": "{3, 7, 8, 9, 10, 11, 17}",
    }),
    Preset("toxic_7_8_9_10_11_impulsive", "Full morning toxic block plus impulsive high-score buys.", {
        "IF1TrendToxicHoursOverride": "{3, 7, 8, 9, 10, 11, 17}",
        "IF1_GOLD_HIGH_SCORE_BUY_REQUIRE_IMPULSIVE_BOS": "true",
    }),
    Preset("toxic_7_8_10_11_sideways_half", "Profit leader plus lighter sideways participation.", {
        "IF1TrendToxicHoursOverride": "{3, 7, 8, 10, 11, 17}",
        "V6_SidewaysRiskPercent": "0.40",
    }),
    Preset("toxic_7_8_9_10_impulsive_sideways_half", "Balanced leader plus lighter sideways participation.", {
        "IF1TrendToxicHoursOverride": "{3, 7, 8, 9, 10, 17}",
        "IF1_GOLD_HIGH_SCORE_BUY_REQUIRE_IMPULSIVE_BOS": "true",
        "V6_SidewaysRiskPercent": "0.40",
    }),
    Preset("toxic_7_8_10_11_sell100", "Profit leader plus full sell size.", {
        "IF1TrendToxicHoursOverride": "{3, 7, 8, 10, 11, 17}",
        "V6_SellRiskMultiplier": "1.00",
    }),
    Preset("toxic_7_8_9_10_impulsive_sell100", "Balanced leader plus full sell size.", {
        "IF1TrendToxicHoursOverride": "{3, 7, 8, 9, 10, 17}",
        "IF1_GOLD_HIGH_SCORE_BUY_REQUIRE_IMPULSIVE_BOS": "true",
        "V6_SellRiskMultiplier": "1.00",
    }),
    Preset("toxic_7_8_9_10_11_break036", "Full morning toxic block plus stronger buy break threshold.", {
        "IF1TrendToxicHoursOverride": "{3, 7, 8, 9, 10, 11, 17}",
        "IF1_BUY_MIN_BREAK_ATR_OVERRIDE": "0.36",
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
        - metrics["equity_dd_pct"] * 1.10
    )


def run_backtest_safe(stem: str) -> Path:
    ini_path = MT5_BUILD / f"{stem}.backtest.ini"
    ini_path.write_text(build_ini(stem, FROM_DATE, TO_DATE, DEPOSIT, LEVERAGE))
    shutil.copy2(MT5_BUILD / f"{stem}.ex5", MT5_EXPERTS / f"{stem}.ex5")

    report_suffix = f"{FROM_DATE.replace('.', '')}_{TO_DATE.replace('.', '')}"
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
            return report_path
        time.sleep(1)

    raise RuntimeError(f"Missing report for {stem}")


def main() -> None:
    results: list[Result] = []
    for preset in PRESETS:
        source_path = build_source_for_preset(preset)
        stem = compile_variant("v6", source_path, f"round4_{preset.name}")
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

    ranked = sorted(
        results,
        key=lambda item: result_score(
            {
                "net_profit": item.net_profit,
                "profit_factor": item.profit_factor,
                "equity_dd_pct": item.equity_dd_pct,
            }
        ),
        reverse=True,
    )
    lines = [
        "# v6 Entry Model Round 4",
        "",
        f"Window: `{FROM_DATE} - {TO_DATE}`, `XAUUSDc`, `M15`, `Deposit {DEPOSIT} USD`, `Leverage {LEVERAGE}`, `Every tick`.",
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
