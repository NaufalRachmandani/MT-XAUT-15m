#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path("/Users/naufalrachmandani/Hobby/MT5 XAU 15m")
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.backtest_v11_split import (  # noqa: E402
    TESTER_PROFILE_DIR,
    compile_exact,
    parse_report,
    run_backtest,
)

RUN_DIR = ROOT / "build" / "v11_10x_iteration"
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


def load_set(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in path.read_text().splitlines():
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    return values


def write_tester_set(stem: str, name: str, values: dict[str, str]) -> str:
    set_name = f"{stem}_{name}.set"
    TESTER_PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    (TESTER_PROFILE_DIR / set_name).write_text("\n".join(f"{key}={value}" for key, value in values.items()) + "\n")
    return set_name


def score_candidate(row: dict) -> float:
    recent = row["metrics"]["recent"]
    ytd = row["metrics"]["ytd"]
    daily_target = 16.0
    trade_bonus = min(recent["total_trades"], 35.0) * 4.0
    trade_penalty = max(0.0, daily_target - recent["total_trades"]) * 6.0
    dd_penalty = max(0.0, ytd["equity_dd_pct"] - 35.0) * 3.0
    pf_penalty = max(0.0, 1.15 - ytd["profit_factor"]) * 120.0
    loss_penalty = 150.0 if recent["net_profit"] < 0.0 else 0.0
    return ytd["net_profit"] + (recent["net_profit"] * 3.0) + trade_bonus - trade_penalty - dd_penalty - pf_penalty - loss_penalty


BULL_PRESETS = [
    Preset("bull_control", "Current v11 bull-only baseline.", {}),
    Preset(
        "bull_score62",
        "Lower score gate while preserving current sessions.",
        {"V10_MinTradeScore": "62"},
    ),
    Preset(
        "bull_session_open",
        "Allow buy entries across the full day instead of core hours only.",
        {"V10_MinTradeScore": "64", "V10_BuySessionStartHour": "0", "V10_BuySessionEndHour": "23", "V10_UseBuyCoreHours": "false"},
    ),
    Preset(
        "bull_zone_dense",
        "More sensitive zone retest for M5 bullish pullbacks.",
        {
            "V10_MinTradeScore": "62",
            "V10_ZoneLookback": "10",
            "V10_ZoneMinBodyRatio": "0.40",
            "V10_ZoneBreakATR": "0.00",
            "V10_ZoneMidTouchATR": "0.18",
            "V10_ZoneOvershootATR": "0.55",
            "V10_ZoneRR": "1.05",
        },
    ),
    Preset(
        "bull_sub_loose",
        "Enable compression breakout sub-engine for missed momentum pushes.",
        {
            "V10_MinTradeScore": "62",
            "V10_EnableBullSubEngine": "true",
            "V10_BullSubAllowWeakBull": "true",
            "V10_BullSubOnlyOutsideCore": "false",
            "V10_BullSubCompressionBars": "8",
            "V10_BullSubMaxRangeATR": "2.40",
            "V10_BullSubBreakATR": "0.00",
            "V10_BullSubMinBodyRatio": "0.46",
            "V10_BullSubRiskMultiplier": "0.28",
            "V10_BullSubRR": "1.35",
        },
    ),
    Preset(
        "bull_addon_dense",
        "Allow more add-ons once a bull lead trade is already moving.",
        {
            "V10_AddOnMaxPerSide": "2",
            "V10_AddOnMinProgressR": "0.35",
            "V10_AddOnBreakATR": "0.00",
            "V10_AddOnMinBodyRatio": "0.46",
            "V10_AddOnRiskMultiplier": "0.30",
            "V10_AddOnRR": "0.95",
        },
    ),
    Preset(
        "bull_dense_mix",
        "Combined dense profile: open session, looser zone, sub-engine, and add-ons.",
        {
            "V10_MinTradeScore": "60",
            "V10_BuySessionStartHour": "0",
            "V10_BuySessionEndHour": "23",
            "V10_UseBuyCoreHours": "false",
            "V10_MaxPositions": "8",
            "V10_WeakRegimeMaxPositions": "3",
            "V10_BuyMinBreakATR": "0.04",
            "V10_WeakBuyMinBreakATR": "0.06",
            "V10_BuyMinBodyRatio": "0.44",
            "V10_WeakBuyMinBodyRatio": "0.48",
            "V10_ZoneLookback": "10",
            "V10_ZoneMinBodyRatio": "0.40",
            "V10_ZoneBreakATR": "0.00",
            "V10_ZoneMidTouchATR": "0.18",
            "V10_ZoneOvershootATR": "0.55",
            "V10_ZoneRR": "1.05",
            "V10_EnableBullSubEngine": "true",
            "V10_BullSubAllowWeakBull": "true",
            "V10_BullSubOnlyOutsideCore": "false",
            "V10_BullSubMinBodyRatio": "0.46",
            "V10_BullSubRR": "1.25",
            "V10_AddOnMaxPerSide": "2",
            "V10_AddOnMinProgressR": "0.35",
            "V10_AddOnMinBodyRatio": "0.46",
            "V10_AddOnRR": "0.95",
        },
    ),
    Preset(
        "bull_tp_dense",
        "Dense entries plus partial close/trailing to avoid letting M5 wins decay.",
        {
            "V10_MinTradeScore": "60",
            "V10_BuySessionStartHour": "0",
            "V10_BuySessionEndHour": "23",
            "V10_UseBuyCoreHours": "false",
            "V10_EnableTPManager": "true",
            "V10_TP1R": "0.85",
            "V10_TP1CloseFraction": "0.50",
            "V10_RunnerRR": "2.20",
            "V10_TrailStartR": "1.10",
            "V10_TrailATR": "0.90",
            "V10_AddOnMaxPerSide": "2",
            "V10_AddOnMinProgressR": "0.45",
        },
    ),
    Preset(
        "bull_trend_push",
        "Higher risk and larger RR for bullish trend capture.",
        {
            "V10_RiskPercent": "6.00",
            "V10_BuyRiskMultiplier": "0.75",
            "V10_WeakBuyRiskMultiplier": "0.30",
            "V10_MaxPositions": "8",
            "V10_WeakRegimeMaxPositions": "3",
            "V10_BuySessionStartHour": "0",
            "V10_BuySessionEndHour": "23",
            "V10_UseBuyCoreHours": "false",
            "V10_BuyRR": "1.75",
            "V10_WeakBuyRR": "1.35",
            "V10_MaxHoldBars": "48",
        },
    ),
    Preset(
        "bull_fast_scalp",
        "Shorter RR and time-close for high-frequency M5 scalping.",
        {
            "V10_MinTradeScore": "58",
            "V10_BuySessionStartHour": "0",
            "V10_BuySessionEndHour": "23",
            "V10_UseBuyCoreHours": "false",
            "V10_BuyRR": "1.10",
            "V10_WeakBuyRR": "0.95",
            "V10_ZoneRR": "0.95",
            "V10_MaxHoldBars": "18",
            "V10_TimeCloseProfitOnly": "false",
            "V10_BuyMinBodyRatio": "0.42",
            "V10_WeakBuyMinBodyRatio": "0.46",
        },
    ),
]

BEAR_PRESETS = [
    Preset("bear_control", "Current v11 bear-only baseline.", {}),
    Preset("bear_score62", "Lower score gate while preserving session filter.", {"V10_MinTradeScore": "62"}),
    Preset(
        "bear_session_open",
        "Allow sell entries across the full day.",
        {"V10_MinTradeScore": "64", "V10_SellSessionStartHour": "0", "V10_SellSessionEndHour": "23"},
    ),
    Preset(
        "bear_zone_dense",
        "More sensitive zone retest for M5 bearish pullbacks.",
        {
            "V10_MinTradeScore": "62",
            "V10_ZoneLookback": "10",
            "V10_ZoneMinBodyRatio": "0.40",
            "V10_ZoneBreakATR": "0.00",
            "V10_ZoneMidTouchATR": "0.18",
            "V10_ZoneOvershootATR": "0.55",
            "V10_ZoneRR": "1.05",
        },
    ),
    Preset(
        "bear_sub_loose",
        "Enable compression breakdown sub-engine.",
        {
            "V10_MinTradeScore": "62",
            "V10_EnableBearSubEngine": "true",
            "V10_BearSubAllowWeakBear": "true",
            "V10_BearSubCompressionBars": "8",
            "V10_BearSubMaxRangeATR": "2.40",
            "V10_BearSubBreakATR": "0.00",
            "V10_BearSubMinBodyRatio": "0.46",
            "V10_BearSubRiskMultiplier": "0.28",
            "V10_BearSubRR": "1.30",
        },
    ),
    Preset(
        "bear_addon_dense",
        "Allow more sell add-ons after lead trade progress.",
        {
            "V10_AddOnMaxPerSide": "2",
            "V10_AddOnMinProgressR": "0.35",
            "V10_AddOnBreakATR": "0.00",
            "V10_AddOnMinBodyRatio": "0.46",
            "V10_AddOnRiskMultiplier": "0.30",
            "V10_AddOnRR": "0.95",
        },
    ),
    Preset(
        "bear_dense_mix",
        "Combined dense bearish profile.",
        {
            "V10_MinTradeScore": "60",
            "V10_SellSessionStartHour": "0",
            "V10_SellSessionEndHour": "23",
            "V10_MaxPositions": "8",
            "V10_WeakRegimeMaxPositions": "3",
            "V10_MinBreakATR": "0.02",
            "V10_WeakSellMinBreakATR": "0.04",
            "V10_MinBodyRatio": "0.42",
            "V10_WeakSellMinBodyRatio": "0.46",
            "V10_ZoneLookback": "10",
            "V10_ZoneMinBodyRatio": "0.40",
            "V10_ZoneBreakATR": "0.00",
            "V10_ZoneMidTouchATR": "0.18",
            "V10_ZoneOvershootATR": "0.55",
            "V10_ZoneRR": "1.05",
            "V10_EnableBearSubEngine": "true",
            "V10_BearSubAllowWeakBear": "true",
            "V10_BearSubMinBodyRatio": "0.46",
            "V10_BearSubRR": "1.20",
            "V10_AddOnMaxPerSide": "2",
            "V10_AddOnMinProgressR": "0.35",
            "V10_AddOnMinBodyRatio": "0.46",
            "V10_AddOnRR": "0.95",
        },
    ),
    Preset(
        "bear_tp_dense",
        "Dense sell entries plus partial close/trailing.",
        {
            "V10_MinTradeScore": "60",
            "V10_SellSessionStartHour": "0",
            "V10_SellSessionEndHour": "23",
            "V10_EnableTPManager": "true",
            "V10_TP1R": "0.85",
            "V10_TP1CloseFraction": "0.50",
            "V10_RunnerRR": "2.20",
            "V10_TrailStartR": "1.10",
            "V10_TrailATR": "0.90",
            "V10_AddOnMaxPerSide": "2",
            "V10_AddOnMinProgressR": "0.45",
        },
    ),
    Preset(
        "bear_trend_push",
        "Higher risk for bearish 2026 continuation.",
        {
            "V10_RiskPercent": "6.00",
            "V10_SellRiskMultiplier": "1.25",
            "V10_WeakSellRiskMultiplier": "0.70",
            "V10_MaxPositions": "8",
            "V10_WeakRegimeMaxPositions": "3",
            "V10_SellSessionStartHour": "0",
            "V10_SellSessionEndHour": "23",
            "V10_SellRR": "1.45",
            "V10_WeakSellRR": "1.15",
            "V10_MaxHoldBars": "48",
        },
    ),
    Preset(
        "bear_fast_scalp",
        "Shorter RR and time-close for higher-frequency sell scalps.",
        {
            "V10_MinTradeScore": "58",
            "V10_SellSessionStartHour": "0",
            "V10_SellSessionEndHour": "23",
            "V10_SellRR": "1.05",
            "V10_WeakSellRR": "0.95",
            "V10_ZoneRR": "0.95",
            "V10_MaxHoldBars": "18",
            "V10_TimeCloseProfitOnly": "false",
            "V10_MinBodyRatio": "0.40",
            "V10_WeakSellMinBodyRatio": "0.44",
        },
    ),
]


def run_side(label: str, stem: str, base_set: str, presets: list[Preset]) -> list[dict]:
    compile_exact(stem)
    base = load_set(ROOT / "mt5" / base_set)
    rows = []
    for index, preset in enumerate(presets, start=1):
        values = dict(base)
        values.update(preset.overrides)
        set_name = write_tester_set(stem, preset.name, values)
        metrics = {}
        reports = {}
        for window, from_date, to_date in WINDOWS:
            print(f"{label} iter {index:02d}/10 {preset.name} {window}", flush=True)
            report = run_backtest(stem, set_name, from_date, to_date)
            metrics[window] = parse_report(report)
            reports[window] = str(report)
        rows.append(
            {
                "side": label,
                "iteration": index,
                "preset": preset.name,
                "note": preset.note,
                "overrides": preset.overrides,
                "metrics": metrics,
                "reports": reports,
            }
        )
    return sorted(rows, key=score_candidate, reverse=True)


def main() -> None:
    all_rows = []
    all_rows.extend(run_side("bull", "InvictusBullM5_v11", "InvictusBullM5_v11.default_2026.set", BULL_PRESETS))
    all_rows.extend(run_side("bear", "InvictusBearM5_v11", "InvictusBearM5_v11.default_2026.set", BEAR_PRESETS))

    (RUN_DIR / "results.json").write_text(json.dumps(all_rows, indent=2))
    lines = [
        "# v11 10x Iteration",
        "",
        "Setup: `XAUUSDc`, `M5`, `Deposit 100 USD`, `Leverage 1:100`, `Every tick`.",
        "",
        "| Side | Rank | Iter | Preset | Recent Net | Recent Trades | Recent PF | YTD Net | YTD Trades | YTD PF | YTD EqDD |",
        "| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for side in ("bull", "bear"):
        side_rows = [row for row in all_rows if row["side"] == side]
        for rank, row in enumerate(side_rows, start=1):
            recent = row["metrics"]["recent"]
            ytd = row["metrics"]["ytd"]
            lines.append(
                f"| {side} | {rank} | {row['iteration']} | {row['preset']} | "
                f"{recent['net_profit']:.2f}% | {recent['total_trades']:.0f} | {recent['profit_factor']:.2f} | "
                f"{ytd['net_profit']:.2f}% | {ytd['total_trades']:.0f} | {ytd['profit_factor']:.2f} | {ytd['equity_dd_pct']:.2f}% |"
            )
    (RUN_DIR / "summary.md").write_text("\n".join(lines) + "\n")
    print(RUN_DIR / "summary.md")


if __name__ == "__main__":
    main()
