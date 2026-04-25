#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path("/Users/naufalrachmandani/Hobby/MT5 XAU 15m")
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.backtest_v11_split import TESTER_PROFILE_DIR, compile_exact, parse_report, run_backtest  # noqa: E402
from tools.iterate_v11_10x import load_set, write_tester_set  # noqa: E402

RUN_DIR = ROOT / "build" / "v11_exit_iteration"
RUN_DIR.mkdir(parents=True, exist_ok=True)

WINDOWS = [
    ("recent", "2026.04.01", "2026.04.25"),
    ("ytd", "2026.01.01", "2026.04.25"),
]


@dataclass(frozen=True)
class ExitPreset:
    name: str
    note: str
    overrides: dict[str, str]


PRESETS = [
    ExitPreset("exit_control", "Current default: BE move active, TP manager disabled.", {}),
    ExitPreset(
        "tp_default",
        "Enable existing partial close and runner manager.",
        {"V10_EnableTPManager": "true"},
    ),
    ExitPreset(
        "tp_quick_scalp",
        "Earlier partial close, tighter trail for M5 scalping.",
        {
            "V10_EnableTPManager": "true",
            "V10_TP1R": "0.85",
            "V10_TP1CloseFraction": "0.50",
            "V10_RunnerRR": "2.20",
            "V10_TrailStartR": "1.10",
            "V10_TrailATR": "0.90",
        },
    ),
    ExitPreset(
        "tp_late_runner",
        "Let stronger trades breathe before partial, then target larger runner.",
        {
            "V10_EnableTPManager": "true",
            "V10_TP1R": "1.35",
            "V10_TP1CloseFraction": "0.35",
            "V10_RunnerRR": "3.00",
            "V10_TrailStartR": "1.80",
            "V10_TrailATR": "1.40",
        },
    ),
    ExitPreset(
        "tp_heavy_partial",
        "Lock most of the position early, smaller runner.",
        {
            "V10_EnableTPManager": "true",
            "V10_TP1R": "0.75",
            "V10_TP1CloseFraction": "0.70",
            "V10_RunnerRR": "1.80",
            "V10_TrailStartR": "1.00",
            "V10_TrailATR": "0.75",
        },
    ),
    ExitPreset(
        "be_early",
        "Move SL to breakeven sooner to reduce giveback.",
        {"V10_BreakevenR": "0.60", "V10_BreakevenLockUsd": "0.10"},
    ),
    ExitPreset(
        "be_late",
        "Move SL later so valid trends are not cut too early.",
        {"V10_BreakevenR": "1.00", "V10_BreakevenLockUsd": "0.25"},
    ),
    ExitPreset(
        "time_strict",
        "Allow max-hold close even when the position is negative.",
        {"V10_TimeCloseProfitOnly": "false", "V10_MaxHoldBars": "24", "V10_ZoneMaxHoldBars": "12", "V10_AddOnMaxHoldBars": "8"},
    ),
    ExitPreset(
        "regime_flip",
        "Close when H1/H4 regime flips against the position.",
        {"V10_CloseOnRegimeFlip": "true"},
    ),
    ExitPreset(
        "adaptive_combo",
        "Moderate TP manager plus slightly later BE and regime flip close.",
        {
            "V10_EnableTPManager": "true",
            "V10_TP1R": "1.05",
            "V10_TP1CloseFraction": "0.45",
            "V10_RunnerRR": "2.60",
            "V10_TrailStartR": "1.30",
            "V10_TrailATR": "1.00",
            "V10_BreakevenR": "0.90",
            "V10_BreakevenLockUsd": "0.20",
            "V10_CloseOnRegimeFlip": "true",
        },
    ),
]


def score_candidate(row: dict) -> float:
    recent = row["metrics"]["recent"]
    ytd = row["metrics"]["ytd"]
    dd_penalty = max(0.0, ytd["equity_dd_pct"] - 25.0) * 5.0
    pf_penalty = max(0.0, 1.25 - ytd["profit_factor"]) * 150.0
    trade_bonus = min(recent["total_trades"], 35.0) * 2.0
    loss_penalty = 200.0 if recent["net_profit"] < 0.0 else 0.0
    return ytd["net_profit"] + recent["net_profit"] * 2.0 + trade_bonus - dd_penalty - pf_penalty - loss_penalty


def main() -> None:
    stem = "InvictusCombinedM5_v11"
    base_set = "InvictusCombinedM5_v11.default_2026.set"
    compile_exact(stem)
    base = load_set(ROOT / "mt5" / base_set)
    rows = []
    TESTER_PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    for index, preset in enumerate(PRESETS, start=1):
        values = dict(base)
        values.update(preset.overrides)
        set_name = write_tester_set(stem, preset.name, values)
        metrics = {}
        reports = {}
        for window, from_date, to_date in WINDOWS:
            print(f"exit iter {index:02d}/10 {preset.name} {window}", flush=True)
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
        "# v11 Exit Iteration",
        "",
        "Setup: `InvictusCombinedM5_v11`, `XAUUSDc`, `M5`, `Deposit 100 USD`, `Leverage 1:100`, `Every tick`.",
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
