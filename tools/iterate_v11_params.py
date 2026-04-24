#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path("/Users/naufalrachmandani/Hobby/MT5 XAU 15m")
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.backtest_v11_split import (
    TESTER_PROFILE_DIR,
    compile_exact,
    parse_report,
    run_backtest,
)

RUN_DIR = ROOT / "build" / "v11_param_round1"
RUN_DIR.mkdir(parents=True, exist_ok=True)

STEM = "InvictusCombinedM5_v11"
BASE_SET = ROOT / "mt5" / "InvictusCombinedM5_v11.default_2026.set"

FAST_WINDOWS = [
    ("last_2w", "2026.04.10", "2026.04.25"),
    ("2026_ytd", "2026.01.01", "2026.04.25"),
]
VALIDATION_WINDOWS = [
    ("2025_current", "2025.01.01", "2026.04.25"),
]


@dataclass(frozen=True)
class Preset:
    name: str
    note: str
    overrides: dict[str, str]


def load_set(path: Path) -> dict[str, str]:
    data: dict[str, str] = {}
    for line in path.read_text().splitlines():
        if not line.strip() or "=" not in line:
            continue
        name, value = line.split("=", 1)
        data[name.strip()] = value.strip()
    return data


def write_set(name: str, values: dict[str, str]) -> str:
    set_name = f"{STEM}_{name}.set"
    content = "\n".join(f"{key}={value}" for key, value in values.items()) + "\n"
    (RUN_DIR / set_name).write_text(content)
    TESTER_PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy2(RUN_DIR / set_name, TESTER_PROFILE_DIR / set_name)
    return set_name


def pct_score(metrics: dict[str, dict[str, float]]) -> float:
    recent = metrics["last_2w"]
    ytd = metrics["2026_ytd"]
    recent_trade_penalty = max(0.0, 18.0 - recent["total_trades"]) * 2.0
    dd_penalty = max(0.0, ytd["equity_dd_pct"] - 18.0) * 3.0
    loss_penalty = 80.0 if recent["net_profit"] < 0.0 else 0.0
    return ytd["net_profit"] + (recent["net_profit"] * 2.0) + (recent["total_trades"] * 1.5) - dd_penalty - recent_trade_penalty - loss_penalty


BASE_V10_LIKE = {
    "V10_RiskPercent": "4.50",
    "V10_BuyRiskMultiplier": "0.60",
    "V10_SellRiskMultiplier": "1.00",
    "V10_WeakBuyRiskMultiplier": "0.22",
    "V10_WeakSellRiskMultiplier": "0.55",
    "V10_MaxPositions": "5",
    "V10_WeakRegimeMaxPositions": "1",
    "V10_EnableBullSubEngine": "false",
    "V10_BullSubAllowWeakBull": "false",
    "V10_EnableBearSubEngine": "false",
    "V10_BearSubAllowWeakBear": "false",
    "V10_ZoneRiskMultiplier": "0.60",
    "V10_ZoneRR": "1.40",
    "V10_FastFailBuyGuard": "false",
    "V10_FastFailPullbackOnly": "true",
    "V10_FastFailBars": "6",
    "V10_FastFailMinProgressR": "0.10",
    "V10_WeakOutsideSellQuickExit": "true",
    "V10_WeakOutsideSellExitBars": "6",
    "V10_MinTradeScore": "72",
    "V10_EnableBuyAddOns": "true",
    "V10_EnableSellAddOns": "false",
    "V10_AddOnRiskMultiplier": "0.35",
    "V10_AddOnRR": "1.10",
}


def merged(**kwargs: str) -> dict[str, str]:
    data = dict(BASE_V10_LIKE)
    data.update(kwargs)
    return data


PRESETS = [
    Preset("v10_like", "Current v10 livefix profile, but with v11 comments/opposite guard.", merged()),
    Preset(
        "v10_sell_add",
        "v10-like plus sell add-ons for active bearish continuation.",
        merged(V10_EnableSellAddOns="true", V10_AddOnRiskMultiplier="0.30", V10_AddOnRR="1.05"),
    ),
    Preset(
        "dualsub",
        "Enable both compression sub-engines, controlled risk.",
        merged(
            V10_EnableBullSubEngine="true",
            V10_BullSubAllowWeakBull="true",
            V10_BullSubRiskMultiplier="0.24",
            V10_BullSubRR="1.65",
            V10_EnableBearSubEngine="true",
            V10_BearSubAllowWeakBear="false",
            V10_BearSubRiskMultiplier="0.26",
            V10_BearSubRR="1.55",
            V10_EnableSellAddOns="true",
            V10_AddOnRiskMultiplier="0.28",
        ),
    ),
    Preset(
        "score68",
        "Lower score gate to add quantity; keep v10 exits.",
        merged(V10_MinTradeScore="68", V10_EnableSellAddOns="true", V10_AddOnRiskMultiplier="0.28"),
    ),
    Preset(
        "score68_fastfail",
        "Lower gate plus early fail cut on buys and weak outside sells.",
        merged(
            V10_MinTradeScore="68",
            V10_FastFailBuyGuard="true",
            V10_FastFailPullbackOnly="false",
            V10_FastFailBars="5",
            V10_FastFailMinProgressR="0.05",
            V10_EnableSellAddOns="true",
            V10_AddOnRiskMultiplier="0.28",
        ),
    ),
    Preset(
        "aggressive_qty",
        "Open thresholds for quantity and stronger compounding.",
        merged(
            V10_RiskPercent="5.00",
            V10_MaxPositions="6",
            V10_WeakRegimeMaxPositions="2",
            V10_MinTradeScore="68",
            V10_BuyMinBreakATR="0.08",
            V10_WeakBuyMinBreakATR="0.12",
            V10_WeakSellMinBreakATR="0.08",
            V10_BuyMinBodyRatio="0.50",
            V10_WeakBuyMinBodyRatio="0.56",
            V10_WeakSellMinBodyRatio="0.50",
            V10_EnableSellAddOns="true",
            V10_AddOnRiskMultiplier="0.32",
            V10_AddOnMinProgressR="0.65",
        ),
    ),
    Preset(
        "trend_runner",
        "Higher RR and hold for trend weeks.",
        merged(
            V10_BuyRR="1.75",
            V10_SellRR="1.45",
            V10_WeakBuyRR="1.40",
            V10_WeakSellRR="1.15",
            V10_MaxHoldBars="48",
            V10_EnableSellAddOns="true",
            V10_AddOnRiskMultiplier="0.30",
            V10_AddOnRR="1.15",
        ),
    ),
    Preset(
        "scalp_dense",
        "Shorter RR, more entries, expects quantity to drive net.",
        merged(
            V10_RiskPercent="4.20",
            V10_MaxPositions="6",
            V10_WeakRegimeMaxPositions="2",
            V10_MinTradeScore="66",
            V10_BuyRR="1.25",
            V10_SellRR="1.15",
            V10_WeakBuyRR="1.05",
            V10_WeakSellRR="1.00",
            V10_MaxHoldBars="20",
            V10_TimeCloseProfitOnly="false",
            V10_BuyMinBreakATR="0.08",
            V10_WeakBuyMinBreakATR="0.12",
            V10_WeakSellMinBreakATR="0.08",
            V10_EnableSellAddOns="true",
            V10_AddOnRiskMultiplier="0.26",
            V10_AddOnRR="0.95",
        ),
    ),
    Preset(
        "tp_manager_probe",
        "Use partial runner manager for longer trend capture.",
        merged(
            V10_EnableTPManager="true",
            V10_TP1R="1.00",
            V10_TP1CloseFraction="0.45",
            V10_RunnerRR="2.80",
            V10_TrailStartR="1.35",
            V10_TrailATR="1.00",
            V10_EnableSellAddOns="true",
            V10_AddOnRiskMultiplier="0.28",
        ),
    ),
    Preset(
        "bear_push_bull_safe",
        "Bigger sell risk for 2026 bear moves, keep buy side v10-like.",
        merged(
            V10_SellRiskMultiplier="1.20",
            V10_WeakSellRiskMultiplier="0.65",
            V10_EnableSellAddOns="true",
            V10_AddOnRiskMultiplier="0.30",
            V10_SellRR="1.35",
            V10_WeakSellRR="1.12",
        ),
    ),
]


def main() -> None:
    base_set = load_set(BASE_SET)
    compile_exact(STEM)
    results = []
    for preset in PRESETS:
        values = dict(base_set)
        values.update(preset.overrides)
        set_name = write_set(preset.name, values)
        metrics = {}
        reports = {}
        for window, from_date, to_date in FAST_WINDOWS:
            print(f"backtest {preset.name} {window}", flush=True)
            report = run_backtest(STEM, set_name, from_date, to_date)
            metrics[window] = parse_report(report)
            reports[window] = str(report)
        results.append(
            {
                "name": preset.name,
                "note": preset.note,
                "set": set_name,
                "metrics": metrics,
                "reports": reports,
                "score": pct_score(metrics),
            }
        )

    top = sorted(results, key=lambda row: row["score"], reverse=True)[:4]
    for row in top:
        for window, from_date, to_date in VALIDATION_WINDOWS:
            print(f"validate {row['name']} {window}", flush=True)
            report = run_backtest(STEM, row["set"], from_date, to_date)
            row["metrics"][window] = parse_report(report)
            row["reports"][window] = str(report)

    results = sorted(results, key=lambda row: row["score"], reverse=True)
    (RUN_DIR / "results.json").write_text(json.dumps(results, indent=2))
    lines = [
        "# v11 Parameter Round 1",
        "",
        "| Preset | 2W Net | 2W Trades | 2W PF | 2026 Net | 2026 Trades | 2026 PF | 2026 EqDD | 2025-Current Net | 2025-Current EqDD |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in results:
        m2 = row["metrics"]["last_2w"]
        y26 = row["metrics"]["2026_ytd"]
        full = row["metrics"].get("2025_current", {})
        lines.append(
            f"| {row['name']} | {m2['net_profit']:.2f}% | {m2['total_trades']:.0f} | {m2['profit_factor']:.2f} | "
            f"{y26['net_profit']:.2f}% | {y26['total_trades']:.0f} | {y26['profit_factor']:.2f} | {y26['equity_dd_pct']:.2f}% | "
            f"{full.get('net_profit', 0.0):.2f}% | {full.get('equity_dd_pct', 0.0):.2f}% |"
        )
    (RUN_DIR / "summary.md").write_text("\n".join(lines) + "\n")
    print(RUN_DIR / "summary.md")


if __name__ == "__main__":
    main()
