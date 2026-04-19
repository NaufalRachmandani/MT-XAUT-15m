#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

ROOT = Path("/Users/naufalrachmandani/Hobby/MT5 XAU 15m")
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.compare_versions_6m_100 import compile_variant, parse_report, run_backtest


RUN_DIR = ROOT / "build" / "v6_aggressive"
RUN_DIR.mkdir(parents=True, exist_ok=True)

SOURCE = ROOT / "mt5" / "InvictusForward1M15_v6.mq5"
RECENT_FROM = "2025.10.18"
RECENT_TO = "2026.04.15"
DEPOSIT = 100
LEVERAGES = ["1:100", "1:200", "1:500"]


@dataclass(frozen=True)
class Preset:
    name: str
    trend_risk: float
    sideways_risk: float
    sell_mult: float
    high_score_buy_mult: float
    trend_cap: int
    sideways_cap: int
    trend_loss_cap: float
    sideways_loss_cap: float
    skip_below_min_lot: bool


@dataclass
class SweepResult:
    preset: str
    leverage: str
    trend_risk: float
    sideways_risk: float
    sell_mult: float
    high_score_buy_mult: float
    trend_cap: int
    sideways_cap: int
    trend_loss_cap: float
    sideways_loss_cap: float
    skip_below_min_lot: bool
    report_path: str
    net_profit: float
    profit_pct: float
    profit_factor: float
    expected_payoff: float
    total_trades: int
    win_rate: float
    balance_dd_pct: float
    equity_dd_pct: float
    score: float


PRESETS = [
    Preset("baseline", 0.75, 0.35, 0.85, 1.10, 7, 8, 5.0, 3.0, True),
    Preset("a_r125", 1.25, 0.60, 0.85, 1.10, 7, 8, 5.0, 3.0, True),
    Preset("b_r175", 1.75, 0.80, 0.85, 1.15, 7, 8, 6.0, 4.0, True),
    Preset("c_r225", 2.25, 1.00, 0.90, 1.15, 7, 8, 7.0, 5.0, True),
    Preset("d_r225_force", 2.25, 1.00, 0.90, 1.15, 7, 8, 7.0, 5.0, False),
    Preset("e_r275_force", 2.75, 1.20, 0.95, 1.20, 9, 10, 8.0, 5.0, False),
    Preset("f_r325_force", 3.25, 1.40, 1.00, 1.25, 10, 10, 9.0, 6.0, False),
]


def replace_input(text: str, name: str, value: str) -> str:
    pattern = re.compile(rf"^input\s+([^\n]*\b{name}\b)\s*=\s*[^;]+;", re.MULTILINE)
    replacement = rf"input \1 = {value};"
    new_text, count = pattern.subn(replacement, text, count=1)
    if count != 1:
        raise RuntimeError(f"Failed to replace input {name}")
    return new_text


def build_source_for_preset(preset: Preset) -> Path:
    text = SOURCE.read_text()
    replacements = {
        "V6_TrendRiskPercent": f"{preset.trend_risk:.2f}",
        "V6_SidewaysRiskPercent": f"{preset.sideways_risk:.2f}",
        "V6_SellRiskMultiplier": f"{preset.sell_mult:.2f}",
        "V6_HighScoreBuyRiskMultiplier": f"{preset.high_score_buy_mult:.2f}",
        "V6_TrendMaxPositions": str(preset.trend_cap),
        "V6_SidewaysMaxPositions": str(preset.sideways_cap),
        "V6_TrendDailyLossCapPercent": f"{preset.trend_loss_cap:.1f}",
        "V6_SidewaysDailyLossCapPercent": f"{preset.sideways_loss_cap:.1f}",
        "V6_SkipTradeBelowMinLot": "true" if preset.skip_below_min_lot else "false",
    }
    for key, value in replacements.items():
        text = replace_input(text, key, value)

    temp_path = RUN_DIR / f"InvictusForward1M15_v6_{preset.name}.mq5"
    temp_path.write_text(text)
    return temp_path


def result_score(metrics: dict[str, float]) -> float:
    profit = metrics["net_profit"]
    pf_bonus = max(metrics["profit_factor"] - 1.0, 0.0) * 120.0
    dd_penalty = metrics["equity_dd_pct"] * 1.15
    return profit + pf_bonus - dd_penalty


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        return
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    results: list[SweepResult] = []

    for preset in PRESETS:
        source_path = build_source_for_preset(preset)
        stem = compile_variant("v6", source_path, f"aggr_{preset.name}")
        print(f"[compile] {preset.name} -> {stem}", flush=True)

        for leverage in LEVERAGES:
            print(f"[backtest] preset={preset.name} leverage={leverage}", flush=True)
            report_path, _ = run_backtest(stem, RECENT_FROM, RECENT_TO, DEPOSIT, leverage)
            metrics = parse_report(report_path)
            results.append(
                SweepResult(
                    preset=preset.name,
                    leverage=leverage,
                    trend_risk=preset.trend_risk,
                    sideways_risk=preset.sideways_risk,
                    sell_mult=preset.sell_mult,
                    high_score_buy_mult=preset.high_score_buy_mult,
                    trend_cap=preset.trend_cap,
                    sideways_cap=preset.sideways_cap,
                    trend_loss_cap=preset.trend_loss_cap,
                    sideways_loss_cap=preset.sideways_loss_cap,
                    skip_below_min_lot=preset.skip_below_min_lot,
                    report_path=str(report_path),
                    net_profit=metrics["net_profit"],
                    profit_pct=(metrics["net_profit"] / DEPOSIT) * 100.0,
                    profit_factor=metrics["profit_factor"],
                    expected_payoff=metrics["expected_payoff"],
                    total_trades=int(metrics["total_trades"]),
                    win_rate=metrics["win_rate"],
                    balance_dd_pct=metrics["balance_dd_pct"],
                    equity_dd_pct=metrics["equity_dd_pct"],
                    score=result_score(metrics),
                )
            )

    rows = [asdict(r) for r in results]
    (RUN_DIR / "results.json").write_text(json.dumps(rows, indent=2))
    write_csv(RUN_DIR / "results.csv", rows)

    ranked = sorted(results, key=lambda r: r.score, reverse=True)
    lines = [
        "# v6 Aggressive Sweep",
        "",
        f"Window: `{RECENT_FROM} - {RECENT_TO}`, `XAUUSDc`, `M15`, `Deposit {DEPOSIT} USD`, `Every tick`.",
        "",
        "| Rank | Preset | Lev | Net | Profit % | PF | WR | Trades | EqDD | Score |",
        "| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for idx, item in enumerate(ranked, start=1):
        lines.append(
            f"| {idx} | {item.preset} | {item.leverage} | {item.net_profit:.2f} | "
            f"{item.profit_pct:.2f}% | {item.profit_factor:.2f} | {item.win_rate:.2f}% | "
            f"{item.total_trades} | {item.equity_dd_pct:.2f}% | {item.score:.2f} |"
        )

    if ranked:
        champion = ranked[0]
        lines.extend(
            [
                "",
                "## Champion",
                "",
                f"- Preset: `{champion.preset}`",
                f"- Leverage: `{champion.leverage}`",
                f"- Net profit: `{champion.net_profit:.2f}`",
                f"- Profit factor: `{champion.profit_factor:.2f}`",
                f"- Win rate: `{champion.win_rate:.2f}%`",
                f"- Trades: `{champion.total_trades}`",
                f"- Equity DD: `{champion.equity_dd_pct:.2f}%`",
                "",
                "## Files",
                f"- [results.json]({(RUN_DIR / 'results.json').as_posix()})",
                f"- [results.csv]({(RUN_DIR / 'results.csv').as_posix()})",
            ]
        )

    (RUN_DIR / "summary.md").write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
