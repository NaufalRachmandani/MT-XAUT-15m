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

RUN_DIR = ROOT / "build" / "v11_param_round2"
RUN_DIR.mkdir(parents=True, exist_ok=True)

STEM = "InvictusCombinedM5_v11"
BASE_SET = ROOT / "build" / "v11_param_round1" / "InvictusCombinedM5_v11_aggressive_qty.set"

WINDOWS = [
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
    values: dict[str, str] = {}
    for line in path.read_text().splitlines():
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    return values


def write_set(name: str, values: dict[str, str]) -> str:
    set_name = f"{STEM}_{name}.set"
    content = "\n".join(f"{key}={value}" for key, value in values.items()) + "\n"
    path = RUN_DIR / set_name
    path.write_text(content)
    TESTER_PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, TESTER_PROFILE_DIR / set_name)
    return set_name


def score(row: dict) -> float:
    recent = row["metrics"]["last_2w"]
    ytd = row["metrics"]["2026_ytd"]
    quantity_bonus = min(recent["total_trades"], 30.0) * 3.0
    dd_penalty = max(0.0, ytd["equity_dd_pct"] - 35.0) * 2.0
    recent_loss = 100.0 if recent["net_profit"] < 0.0 else 0.0
    return ytd["net_profit"] + recent["net_profit"] * 2.5 + quantity_bonus - dd_penalty - recent_loss


def merged(**kwargs: str) -> dict[str, str]:
    data = {
        "V10_RiskPercent": "5.00",
        "V10_MaxPositions": "6",
        "V10_WeakRegimeMaxPositions": "2",
        "V10_MinTradeScore": "68",
        "V10_BuyMinBreakATR": "0.08",
        "V10_WeakBuyMinBreakATR": "0.12",
        "V10_WeakSellMinBreakATR": "0.08",
        "V10_BuyMinBodyRatio": "0.50",
        "V10_WeakBuyMinBodyRatio": "0.56",
        "V10_WeakSellMinBodyRatio": "0.50",
        "V10_EnableSellAddOns": "true",
        "V10_AddOnRiskMultiplier": "0.32",
        "V10_AddOnMinProgressR": "0.65",
    }
    data.update(kwargs)
    return data


PRESETS = [
    Preset("aggressive_qty", "Round 1 champion baseline.", {}),
    Preset(
        "session_all",
        "Let both engines trade all day and remove buy core-hour gate.",
        merged(
            V10_SellSessionStartHour="0",
            V10_SellSessionEndHour="23",
            V10_BuySessionStartHour="0",
            V10_BuySessionEndHour="23",
            V10_UseBuyCoreHours="false",
        ),
    ),
    Preset(
        "mixed_regime",
        "Allow mixed H1/H4 state to participate with the current M5 bias.",
        merged(
            V10_EnableMixedMomentumEntries="true",
            V10_H1ADXMin="16.0",
            V10_H1ADXStrongMin="24.0",
            V10_StrongGapATR="0.08",
        ),
    ),
    Preset(
        "dense_score60",
        "Loosen score/body/break thresholds to force quantity.",
        merged(
            V10_MinTradeScore="60",
            V10_MinBodyRatio="0.42",
            V10_BuyMinBodyRatio="0.44",
            V10_WeakSellMinBodyRatio="0.44",
            V10_WeakBuyMinBodyRatio="0.48",
            V10_MinBreakATR="0.02",
            V10_BuyMinBreakATR="0.04",
            V10_WeakBuyMinBreakATR="0.06",
            V10_WeakSellMinBreakATR="0.04",
            V10_MaxPositions="8",
            V10_WeakRegimeMaxPositions="3",
            V10_TimeCloseProfitOnly="false",
        ),
    ),
    Preset(
        "zone_loose",
        "Make retest engine more sensitive, but keep score floor.",
        merged(
            V10_ZoneLookback="8",
            V10_ZoneMinBodyRatio="0.46",
            V10_ZoneBreakATR="0.02",
            V10_ZoneMidTouchATR="0.10",
            V10_ZoneOvershootATR="0.35",
            V10_ZoneRiskMultiplier="0.70",
            V10_ZoneRR="1.20",
        ),
    ),
    Preset(
        "sub_loose",
        "Enable loose compression breakout engines both directions.",
        merged(
            V10_EnableBullSubEngine="true",
            V10_BullSubAllowWeakBull="true",
            V10_BullSubCompressionBars="8",
            V10_BullSubMaxRangeATR="2.20",
            V10_BullSubBreakATR="0.00",
            V10_BullSubMinBodyRatio="0.48",
            V10_BullSubRiskMultiplier="0.30",
            V10_BullSubRR="1.35",
            V10_EnableBearSubEngine="true",
            V10_BearSubAllowWeakBear="true",
            V10_BearSubCompressionBars="8",
            V10_BearSubMaxRangeATR="2.20",
            V10_BearSubBreakATR="0.00",
            V10_BearSubMinBodyRatio="0.48",
            V10_BearSubRiskMultiplier="0.30",
            V10_BearSubRR="1.30",
        ),
    ),
    Preset(
        "addon_dense",
        "Allow more continuation add-ons per side.",
        merged(
            V10_AddOnMaxPerSide="2",
            V10_AddOnMinProgressR="0.45",
            V10_AddOnBreakATR="0.00",
            V10_AddOnMinBodyRatio="0.48",
            V10_AddOnRiskMultiplier="0.36",
            V10_AddOnRR="0.95",
        ),
    ),
    Preset(
        "tp_dense",
        "Dense entries with partial close/trailing manager to control damage.",
        merged(
            V10_MinTradeScore="62",
            V10_MaxPositions="8",
            V10_WeakRegimeMaxPositions="3",
            V10_EnableTPManager="true",
            V10_TP1R="0.85",
            V10_TP1CloseFraction="0.50",
            V10_RunnerRR="2.20",
            V10_TrailStartR="1.10",
            V10_TrailATR="0.90",
            V10_AddOnMaxPerSide="2",
            V10_AddOnMinProgressR="0.50",
            V10_AddOnRiskMultiplier="0.28",
        ),
    ),
    Preset(
        "trend_allin",
        "Strong trend mode: bigger risk, looser sessions, longer RR.",
        merged(
            V10_RiskPercent="6.00",
            V10_BuyRiskMultiplier="0.75",
            V10_SellRiskMultiplier="1.25",
            V10_WeakBuyRiskMultiplier="0.30",
            V10_WeakSellRiskMultiplier="0.70",
            V10_MaxPositions="7",
            V10_WeakRegimeMaxPositions="2",
            V10_SellSessionStartHour="0",
            V10_SellSessionEndHour="23",
            V10_BuySessionStartHour="0",
            V10_BuySessionEndHour="23",
            V10_UseBuyCoreHours="false",
            V10_BuyRR="1.75",
            V10_SellRR="1.45",
            V10_WeakBuyRR="1.35",
            V10_WeakSellRR="1.15",
        ),
    ),
]


def main() -> None:
    base = load_set(BASE_SET)
    compile_exact(STEM)
    rows = []
    for preset in PRESETS:
        values = dict(base)
        values.update(preset.overrides)
        set_name = write_set(preset.name, values)
        metrics = {}
        reports = {}
        for window, from_date, to_date in WINDOWS:
            print(f"backtest {preset.name} {window}", flush=True)
            report = run_backtest(STEM, set_name, from_date, to_date)
            metrics[window] = parse_report(report)
            reports[window] = str(report)
        rows.append({"name": preset.name, "note": preset.note, "set": set_name, "metrics": metrics, "reports": reports})

    for row in sorted(rows, key=score, reverse=True)[:3]:
        for window, from_date, to_date in VALIDATION_WINDOWS:
            print(f"validate {row['name']} {window}", flush=True)
            report = run_backtest(STEM, row["set"], from_date, to_date)
            row["metrics"][window] = parse_report(report)
            row["reports"][window] = str(report)

    rows = sorted(rows, key=score, reverse=True)
    (RUN_DIR / "results.json").write_text(json.dumps(rows, indent=2))
    lines = [
        "# v11 Parameter Round 2",
        "",
        "| Preset | 2W Net | 2W Trades | 2W PF | 2026 Net | 2026 Trades | 2026 PF | 2026 EqDD | 2025-Current Net | 2025-Current EqDD |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in rows:
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
