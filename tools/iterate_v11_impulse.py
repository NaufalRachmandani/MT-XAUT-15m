#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path("/Users/naufalrachmandani/Hobby/MT5 XAU 15m")
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.iterate_v11_10x import load_set, write_tester_set  # noqa: E402
from tools.backtest_v11_split import compile_exact, parse_report, run_backtest  # noqa: E402

RUN_DIR = ROOT / "build" / "v11_impulse_iteration"
RUN_DIR.mkdir(parents=True, exist_ok=True)

STEM = "InvictusCombinedM5_v11"
BASE_SET = "InvictusCombinedM5_v11.default_2026.set"
WINDOWS = [
    ("recent", "2026.04.01", "2026.04.25"),
    ("ytd", "2026.01.01", "2026.04.25"),
]


@dataclass(frozen=True)
class Preset:
    name: str
    note: str
    overrides: dict[str, str]


def score(row: dict) -> float:
    recent = row["metrics"]["recent"]
    ytd = row["metrics"]["ytd"]
    trade_bonus = min(ytd["total_trades"], 220.0) * 0.9
    recent_bonus = min(recent["total_trades"], 55.0) * 2.5
    dd_penalty = max(0.0, ytd["equity_dd_pct"] - 24.0) * 8.0
    pf_penalty = max(0.0, 1.35 - ytd["profit_factor"]) * 140.0
    recent_loss_penalty = 120.0 if recent["net_profit"] < 0 else 0.0
    return ytd["net_profit"] + (recent["net_profit"] * 2.5) + trade_bonus + recent_bonus - dd_penalty - pf_penalty - recent_loss_penalty


COMMON_ON = {
    "V11_EnableImpulsePullbackEngine": "true",
    "V11_ImpulseAllowWeakRegime": "true",
    "V11_ImpulseSessionStartHour": "0",
    "V11_ImpulseSessionEndHour": "23",
}


PRESETS = [
    Preset("control", "Current pushed v11 default; impulse engine disabled.", {}),
    Preset(
        "both_soft_scalp",
        "Loose continuation scalp after impulse-pullback; low risk and short hold.",
        {
            **COMMON_ON,
            "V11_EnableBuyImpulsePullback": "true",
            "V11_EnableSellImpulsePullback": "true",
            "V11_ImpulseMinBodyRatio": "0.44",
            "V11_ImpulseMinMoveATR": "0.42",
            "V11_ImpulsePullbackMaxATR": "1.35",
            "V11_ImpulseEntryBodyRatio": "0.28",
            "V11_ImpulseRiskMultiplier": "0.18",
            "V11_ImpulseRR": "0.95",
            "V11_ImpulseMaxHoldBars": "6",
            "V11_BuyImpulseTimeCloseProfitOnly": "false",
            "V11_SellImpulseTimeCloseProfitOnly": "false",
        },
    ),
    Preset(
        "both_balanced",
        "Balanced impulse-pullback candidate, still lower risk than primary entries.",
        {
            **COMMON_ON,
            "V11_EnableBuyImpulsePullback": "true",
            "V11_EnableSellImpulsePullback": "true",
            "V11_ImpulseMinBodyRatio": "0.52",
            "V11_ImpulseMinMoveATR": "0.65",
            "V11_ImpulsePullbackMaxATR": "0.90",
            "V11_ImpulseEntryBodyRatio": "0.38",
            "V11_ImpulseRiskMultiplier": "0.25",
            "V11_ImpulseRR": "1.15",
            "V11_ImpulseMaxHoldBars": "10",
        },
    ),
    Preset(
        "both_runner",
        "Stronger impulse only, wider RR, lets continuation breathe longer.",
        {
            **COMMON_ON,
            "V11_EnableBuyImpulsePullback": "true",
            "V11_EnableSellImpulsePullback": "true",
            "V11_ImpulseMinBodyRatio": "0.58",
            "V11_ImpulseMinMoveATR": "0.85",
            "V11_ImpulsePullbackMaxATR": "0.75",
            "V11_ImpulseEntryBodyRatio": "0.44",
            "V11_ImpulseRiskMultiplier": "0.28",
            "V11_ImpulseRR": "1.45",
            "V11_ImpulseMaxHoldBars": "16",
        },
    ),
    Preset(
        "buy_soft",
        "Buy-only soft impulse continuation for 2026 rebound legs.",
        {
            **COMMON_ON,
            "V11_EnableBuyImpulsePullback": "true",
            "V11_EnableSellImpulsePullback": "false",
            "V11_ImpulseMinBodyRatio": "0.44",
            "V11_ImpulseMinMoveATR": "0.45",
            "V11_ImpulsePullbackMaxATR": "1.25",
            "V11_ImpulseEntryBodyRatio": "0.30",
            "V11_ImpulseRiskMultiplier": "0.20",
            "V11_ImpulseRR": "1.05",
            "V11_ImpulseMaxHoldBars": "8",
            "V11_BuyImpulseTimeCloseProfitOnly": "false",
        },
    ),
    Preset(
        "buy_runner",
        "Buy-only higher quality impulse that targets extended bullish legs.",
        {
            **COMMON_ON,
            "V11_EnableBuyImpulsePullback": "true",
            "V11_EnableSellImpulsePullback": "false",
            "V11_ImpulseMinBodyRatio": "0.56",
            "V11_ImpulseMinMoveATR": "0.80",
            "V11_ImpulsePullbackMaxATR": "0.85",
            "V11_ImpulseEntryBodyRatio": "0.42",
            "V11_ImpulseRiskMultiplier": "0.30",
            "V11_ImpulseRR": "1.45",
            "V11_ImpulseMaxHoldBars": "16",
        },
    ),
    Preset(
        "sell_soft",
        "Sell-only soft impulse continuation for fast bearish drops.",
        {
            **COMMON_ON,
            "V11_EnableBuyImpulsePullback": "false",
            "V11_EnableSellImpulsePullback": "true",
            "V11_ImpulseMinBodyRatio": "0.44",
            "V11_ImpulseMinMoveATR": "0.45",
            "V11_ImpulsePullbackMaxATR": "1.25",
            "V11_ImpulseEntryBodyRatio": "0.30",
            "V11_ImpulseRiskMultiplier": "0.20",
            "V11_ImpulseRR": "1.00",
            "V11_ImpulseMaxHoldBars": "8",
            "V11_SellImpulseTimeCloseProfitOnly": "false",
        },
    ),
    Preset(
        "sell_runner",
        "Sell-only stronger impulse setup for clean breakdown legs.",
        {
            **COMMON_ON,
            "V11_EnableBuyImpulsePullback": "false",
            "V11_EnableSellImpulsePullback": "true",
            "V11_ImpulseMinBodyRatio": "0.58",
            "V11_ImpulseMinMoveATR": "0.85",
            "V11_ImpulsePullbackMaxATR": "0.75",
            "V11_ImpulseEntryBodyRatio": "0.44",
            "V11_ImpulseRiskMultiplier": "0.30",
            "V11_ImpulseRR": "1.35",
            "V11_ImpulseMaxHoldBars": "14",
        },
    ),
    Preset(
        "buy_aggressive",
        "Aggressive buy impulse mode: lower gate, higher risk, still quick exit.",
        {
            **COMMON_ON,
            "V10_MinTradeScore": "60",
            "V11_EnableBuyImpulsePullback": "true",
            "V11_EnableSellImpulsePullback": "false",
            "V11_ImpulseMinBodyRatio": "0.40",
            "V11_ImpulseMinMoveATR": "0.35",
            "V11_ImpulsePullbackMaxATR": "1.50",
            "V11_ImpulseEntryBodyRatio": "0.26",
            "V11_ImpulseRiskMultiplier": "0.28",
            "V11_ImpulseRR": "0.95",
            "V11_ImpulseMaxHoldBars": "6",
            "V11_BuyImpulseTimeCloseProfitOnly": "false",
        },
    ),
    Preset(
        "sell_aggressive",
        "Aggressive sell impulse mode for 2026 drop behavior.",
        {
            **COMMON_ON,
            "V10_MinTradeScore": "60",
            "V11_EnableBuyImpulsePullback": "false",
            "V11_EnableSellImpulsePullback": "true",
            "V11_ImpulseMinBodyRatio": "0.40",
            "V11_ImpulseMinMoveATR": "0.35",
            "V11_ImpulsePullbackMaxATR": "1.50",
            "V11_ImpulseEntryBodyRatio": "0.26",
            "V11_ImpulseRiskMultiplier": "0.28",
            "V11_ImpulseRR": "0.90",
            "V11_ImpulseMaxHoldBars": "6",
            "V11_SellImpulseTimeCloseProfitOnly": "false",
        },
    ),
    Preset(
        "no_weak_runner",
        "Only strong bull/bear regimes; fewer trades but higher structural quality.",
        {
            **COMMON_ON,
            "V11_ImpulseAllowWeakRegime": "false",
            "V11_EnableBuyImpulsePullback": "true",
            "V11_EnableSellImpulsePullback": "true",
            "V11_ImpulseMinBodyRatio": "0.52",
            "V11_ImpulseMinMoveATR": "0.70",
            "V11_ImpulsePullbackMaxATR": "0.80",
            "V11_ImpulseEntryBodyRatio": "0.40",
            "V11_ImpulseRiskMultiplier": "0.30",
            "V11_ImpulseRR": "1.35",
            "V11_ImpulseMaxHoldBars": "14",
        },
    ),
]


def main() -> None:
    compile_exact(STEM)
    base = load_set(ROOT / "mt5" / BASE_SET)
    rows = []
    for index, preset in enumerate(PRESETS, start=1):
        values = dict(base)
        values.update(preset.overrides)
        set_name = write_tester_set(STEM, preset.name, values)
        metrics = {}
        reports = {}
        for window, from_date, to_date in WINDOWS:
            print(f"impulse iter {index:02d}/{len(PRESETS)} {preset.name} {window}", flush=True)
            report = run_backtest(STEM, set_name, from_date, to_date)
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
                "score": 0.0,
            }
        )

    for row in rows:
        row["score"] = score(row)
    rows = sorted(rows, key=lambda item: item["score"], reverse=True)
    (RUN_DIR / "results.json").write_text(json.dumps(rows, indent=2))

    lines = [
        "# v11 Impulse Pullback Iteration",
        "",
        "Setup: `InvictusCombinedM5_v11`, `XAUUSDc`, `M5`, `Deposit 100 USD`, `Leverage 1:100`, `Every tick`.",
        "",
        "| Rank | Iter | Preset | Recent Net | Recent Trades | Recent PF | Recent EqDD | YTD Net | YTD Trades | YTD PF | YTD EqDD | Score |",
        "| ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for rank, row in enumerate(rows, start=1):
        recent = row["metrics"]["recent"]
        ytd = row["metrics"]["ytd"]
        lines.append(
            f"| {rank} | {row['iteration']} | {row['preset']} | "
            f"{recent['net_profit']:.2f} | {recent['total_trades']:.0f} | {recent['profit_factor']:.2f} | {recent['equity_dd_pct']:.2f}% | "
            f"{ytd['net_profit']:.2f} | {ytd['total_trades']:.0f} | {ytd['profit_factor']:.2f} | {ytd['equity_dd_pct']:.2f}% | "
            f"{row['score']:.2f} |"
        )
    (RUN_DIR / "summary.md").write_text("\n".join(lines) + "\n")
    print(RUN_DIR / "summary.md")


if __name__ == "__main__":
    main()
