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

RUN_DIR = ROOT / "build" / "v11_daily_guard_iteration"
RUN_DIR.mkdir(parents=True, exist_ok=True)

STEM = "InvictusCombinedM5_v11"
BASE_SET = ROOT / "mt5" / "InvictusCombinedM5_v11.default_2026.set"
WINDOWS = [
    ("2026_ytd", "2026.01.01", "2026.04.25"),
    ("worst_2025_09", "2025.09.01", "2025.09.30"),
    ("worst_2024_05", "2024.05.01", "2024.05.31"),
    ("worst_2023_04", "2023.04.01", "2023.04.30"),
    ("stress_2025_12", "2025.12.01", "2025.12.31"),
]


@dataclass(frozen=True)
class Preset:
    name: str
    note: str
    overrides: dict[str, str]


def guard_base() -> dict[str, str]:
    return {
        "V11_EnableDailyGuard": "true",
        "V11_DailyGuardLog": "false",
    }


PRESETS = [
    Preset("control", "Current v11 behavior; all guards off.", {}),
    Preset(
        "loss_cap_8",
        "Stop new entries after daily equity drawdown reaches 8%; do not force-close current positions.",
        {**guard_base(), "V11_DailyMaxLossPct": "8.00", "V11_DailyClosePositionsOnStop": "false"},
    ),
    Preset(
        "loss_cap_8_close",
        "Stop and close own positions after daily drawdown reaches 8%.",
        {**guard_base(), "V11_DailyMaxLossPct": "8.00", "V11_DailyClosePositionsOnStop": "true"},
    ),
    Preset(
        "loss_cap_5_close",
        "Stricter daily kill switch at 5%, closes own positions.",
        {**guard_base(), "V11_DailyMaxLossPct": "5.00", "V11_DailyClosePositionsOnStop": "true"},
    ),
    Preset(
        "profit_stop_12",
        "After a day reaches +12%, stop taking new entries to protect the day.",
        {**guard_base(), "V11_DailyProfitStopPct": "12.00"},
    ),
    Preset(
        "profit_lock_8_3",
        "If daily high reaches +8%, block new entries after 3% giveback.",
        {**guard_base(), "V11_DailyProfitLockStartPct": "8.00", "V11_DailyMaxGivebackPct": "3.00"},
    ),
    Preset(
        "profit_lock_12_5",
        "Looser lock: daily high +12%, block after 5% giveback.",
        {**guard_base(), "V11_DailyProfitLockStartPct": "12.00", "V11_DailyMaxGivebackPct": "5.00"},
    ),
    Preset(
        "cooldown_2x120",
        "After 2 consecutive closed losses, pause entries for 120 minutes.",
        {"V11_DailyGuardLog": "false", "V11_MaxConsecutiveLosses": "2", "V11_LossCooldownMinutes": "120"},
    ),
    Preset(
        "loss8_cooldown",
        "Daily 8% loss cap plus 2-loss cooldown.",
        {
            **guard_base(),
            "V11_DailyMaxLossPct": "8.00",
            "V11_DailyClosePositionsOnStop": "false",
            "V11_MaxConsecutiveLosses": "2",
            "V11_LossCooldownMinutes": "120",
        },
    ),
    Preset(
        "balanced_guard",
        "8% daily loss cap, +12%/4% profit lock, and 3-loss cooldown.",
        {
            **guard_base(),
            "V11_DailyMaxLossPct": "8.00",
            "V11_DailyClosePositionsOnStop": "false",
            "V11_DailyProfitLockStartPct": "12.00",
            "V11_DailyMaxGivebackPct": "4.00",
            "V11_MaxConsecutiveLosses": "3",
            "V11_LossCooldownMinutes": "180",
        },
    ),
    Preset(
        "strict_guard",
        "Aggressive protection: 5% daily close, +8%/3% lock, 2-loss 240m cooldown.",
        {
            **guard_base(),
            "V11_DailyMaxLossPct": "5.00",
            "V11_DailyClosePositionsOnStop": "true",
            "V11_DailyProfitLockStartPct": "8.00",
            "V11_DailyMaxGivebackPct": "3.00",
            "V11_MaxConsecutiveLosses": "2",
            "V11_LossCooldownMinutes": "240",
        },
    ),
]


def score(row: dict) -> float:
    metrics = row["metrics"]
    y26 = metrics["2026_ytd"]
    bad = [metrics["worst_2025_09"], metrics["worst_2024_05"], metrics["worst_2023_04"], metrics["stress_2025_12"]]
    bad_net = sum(item["net_profit"] for item in bad)
    bad_dd = max(item["equity_dd_pct"] for item in bad)
    trade_penalty = max(0.0, 130.0 - y26["total_trades"]) * 1.2
    ytd_penalty = max(0.0, 500.0 - y26["net_profit"]) * 0.8
    dd_penalty = max(0.0, bad_dd - 30.0) * 5.0
    return (y26["net_profit"] * 0.9) + (bad_net * 2.5) - ytd_penalty - trade_penalty - dd_penalty


def main() -> None:
    compile_exact(STEM)
    base = load_set(BASE_SET)
    rows = []
    for index, preset in enumerate(PRESETS, start=1):
        values = dict(base)
        values.update(preset.overrides)
        set_name = write_tester_set(STEM, f"daily_guard_{preset.name}", values)
        metrics = {}
        reports = {}
        for window, from_date, to_date in WINDOWS:
            print(f"daily guard {index:02d}/{len(PRESETS)} {preset.name} {window}", flush=True)
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
    rows = sorted(rows, key=lambda row: row["score"], reverse=True)
    (RUN_DIR / "results.json").write_text(json.dumps(rows, indent=2))

    lines = [
        "# v11 Daily Guard Iteration",
        "",
        "Setup: `InvictusCombinedM5_v11`, `XAUUSDc`, `M5`, `Deposit 100 USD`, `Leverage 1:100`, `Every tick`.",
        "",
        "| Rank | Iter | Preset | 2026 Net | 2026 Trades | 2026 PF | 2026 EqDD | 2025-09 Net/DD | 2024-05 Net/DD | 2023-04 Net/DD | 2025-12 Net/DD | Score |",
        "| ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for rank, row in enumerate(rows, start=1):
        m = row["metrics"]
        y26 = m["2026_ytd"]
        lines.append(
            f"| {rank} | {row['iteration']} | {row['preset']} | "
            f"{y26['net_profit']:.2f} | {y26['total_trades']:.0f} | {y26['profit_factor']:.2f} | {y26['equity_dd_pct']:.2f}% | "
            f"{m['worst_2025_09']['net_profit']:.2f}/{m['worst_2025_09']['equity_dd_pct']:.2f}% | "
            f"{m['worst_2024_05']['net_profit']:.2f}/{m['worst_2024_05']['equity_dd_pct']:.2f}% | "
            f"{m['worst_2023_04']['net_profit']:.2f}/{m['worst_2023_04']['equity_dd_pct']:.2f}% | "
            f"{m['stress_2025_12']['net_profit']:.2f}/{m['stress_2025_12']['equity_dd_pct']:.2f}% | "
            f"{row['score']:.2f} |"
        )
    (RUN_DIR / "summary.md").write_text("\n".join(lines) + "\n")
    print(RUN_DIR / "summary.md")


if __name__ == "__main__":
    main()
