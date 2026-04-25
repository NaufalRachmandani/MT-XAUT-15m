#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path("/Users/naufalrachmandani/Hobby/MT5 XAU 15m")
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.backtest_v11_split import compile_exact, parse_report, run_backtest  # noqa: E402
from tools.iterate_v11_10x import load_set, write_tester_set  # noqa: E402

RUN_DIR = ROOT / "build" / "v11_bear_safety_iteration"
RUN_DIR.mkdir(parents=True, exist_ok=True)

WINDOWS = [
    ("recent", "2026.04.01", "2026.04.25"),
    ("ytd", "2026.01.01", "2026.04.25"),
]


@dataclass(frozen=True)
class Preset:
    name: str
    note: str
    overrides: dict[str, str]


PRESETS = [
    Preset("bear_current", "Current bear dense mix default.", {}),
    Preset(
        "safe_weak_score72",
        "Require weak-bear sells to score at least 72 and have stronger body.",
        {"V11_EnableBearSafeMode": "true", "V11_BearSafeWeakMinScore": "72", "V11_BearSafeWeakMinBodyRatio": "0.50"},
    ),
    Preset(
        "safe_weak_score76",
        "Tighter weak-bear sell filter.",
        {"V11_EnableBearSafeMode": "true", "V11_BearSafeWeakMinScore": "76", "V11_BearSafeWeakMinBodyRatio": "0.52"},
    ),
    Preset(
        "safe_block_weak_addons",
        "Keep weak bear entries but block weak sell add-ons.",
        {"V11_EnableBearSafeMode": "true", "V11_BearSafeWeakMinScore": "68", "V11_BearSafeWeakMinBodyRatio": "0.48", "V11_BearSafeBlockWeakAddOns": "true"},
    ),
    Preset(
        "safe_block_weak_zone",
        "Block weak-regime sell zone retests.",
        {"V11_EnableBearSafeMode": "true", "V11_BearSafeWeakMinScore": "68", "V11_BearSafeBlockWeakZone": "true"},
    ),
    Preset(
        "safe_strong_only",
        "Disable weak-bear sell engines entirely.",
        {
            "V10_WeakRegimeMaxPositions": "0",
            "V10_BearSubAllowWeakBear": "false",
            "V10_ZoneAllowWeakRegime": "false",
            "V10_AddOnAllowWeakRegime": "false",
        },
    ),
    Preset(
        "safe_no_addons",
        "Turn off sell add-ons to reduce stacked DD.",
        {"V10_EnableSellAddOns": "false"},
    ),
    Preset(
        "safe_zone_quality",
        "Raise sell-zone quality while keeping weak regime allowed.",
        {"V10_ZoneMinBodyRatio": "0.48", "V10_ZoneBreakATR": "0.04", "V10_ZoneOvershootATR": "0.40", "V10_ZoneRR": "1.15"},
    ),
    Preset(
        "safe_break_quality",
        "Raise base sell breakout quality.",
        {"V10_MinTradeScore": "64", "V10_MinBreakATR": "0.05", "V10_WeakSellMinBreakATR": "0.08", "V10_MinBodyRatio": "0.46", "V10_WeakSellMinBodyRatio": "0.50"},
    ),
    Preset(
        "safe_sell_time_strict_selective",
        "Allow time-close loss only for sell add-ons and compression, not base/zone sell.",
        {"V11_SellCompTimeCloseProfitOnly": "false", "V11_SellAddOnTimeCloseProfitOnly": "false", "V10_BearSubMaxHoldBars": "18", "V10_AddOnMaxHoldBars": "8"},
    ),
]


def score_candidate(row: dict) -> float:
    recent = row["metrics"]["recent"]
    ytd = row["metrics"]["ytd"]
    dd_penalty = max(0.0, ytd["equity_dd_pct"] - 25.0) * 8.0
    pf_penalty = max(0.0, 1.30 - ytd["profit_factor"]) * 160.0
    recent_penalty = 80.0 if recent["net_profit"] < 0.0 else 0.0
    trade_penalty = max(0.0, 30.0 - ytd["total_trades"]) * 2.0
    return ytd["net_profit"] + recent["net_profit"] * 2.0 - dd_penalty - pf_penalty - recent_penalty - trade_penalty


def main() -> None:
    stem = "InvictusBearM5_v11"
    base_set = "InvictusBearM5_v11.default_2026.set"
    compile_exact(stem)
    base = load_set(ROOT / "mt5" / base_set)
    rows = []
    for index, preset in enumerate(PRESETS, start=1):
        values = dict(base)
        values.update(preset.overrides)
        set_name = write_tester_set(stem, preset.name, values)
        metrics = {}
        reports = {}
        for window, from_date, to_date in WINDOWS:
            print(f"bear safety {index:02d}/10 {preset.name} {window}", flush=True)
            report = run_backtest(stem, set_name, from_date, to_date)
            metrics[window] = parse_report(report)
            reports[window] = str(report)
        rows.append(
            {
                "iteration": index,
                "preset": preset.name,
                "note": preset.note,
                "overrides": preset.overrides,
                "metrics": metrics,
                "reports": reports,
            }
        )

    ranked = sorted(rows, key=score_candidate, reverse=True)
    (RUN_DIR / "results.json").write_text(json.dumps(ranked, indent=2))
    lines = [
        "# v11 Bear Safety Iteration",
        "",
        "Setup: `InvictusBearM5_v11`, `XAUUSDc`, `M5`, `Deposit 100 USD`, `Leverage 1:100`, `Every tick`.",
        "",
        "| Rank | Iter | Preset | Recent Net | Recent Trades | Recent PF | YTD Net | YTD Trades | YTD PF | YTD EqDD |",
        "| ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for rank, row in enumerate(ranked, start=1):
        recent = row["metrics"]["recent"]
        ytd = row["metrics"]["ytd"]
        lines.append(
            f"| {rank} | {row['iteration']} | {row['preset']} | "
            f"{recent['net_profit']:.2f}% | {recent['total_trades']:.0f} | {recent['profit_factor']:.2f} | "
            f"{ytd['net_profit']:.2f}% | {ytd['total_trades']:.0f} | {ytd['profit_factor']:.2f} | {ytd['equity_dd_pct']:.2f}% |"
        )
    (RUN_DIR / "summary.md").write_text("\n".join(lines) + "\n")
    print(RUN_DIR / "summary.md")


if __name__ == "__main__":
    main()
