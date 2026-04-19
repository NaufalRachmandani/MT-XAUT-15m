#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

ROOT = Path("/Users/naufalrachmandani/Hobby/MT5 XAU 15m")
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.compare_versions_6m_100 import compile_variant, parse_report, run_backtest


RUN_DIR = ROOT / "build" / "v6_scaling"
RUN_DIR.mkdir(parents=True, exist_ok=True)

WINDOWS = [
    ("recent_2026q1", "2026.01.01", "2026.04.15"),
    ("from_2025", "2025.01.01", "2026.04.15"),
]
DEPOSITS = [100, 10000]
LEVERAGE = "1:100"


@dataclass
class ScalingResult:
    window: str
    from_date: str
    to_date: str
    deposit: int
    leverage: str
    report_path: str
    tester_log: str
    net_profit: float
    profit_pct: float
    profit_factor: float
    expected_payoff: float
    total_trades: int
    win_rate: float
    balance_dd_abs: float
    balance_dd_pct: float
    equity_dd_abs: float
    equity_dd_pct: float


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        return
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    stem = compile_variant("v6", ROOT / "mt5" / "InvictusForward1M15_v6.mq5", "scaling")
    results: list[ScalingResult] = []

    for window_label, from_date, to_date in WINDOWS:
        for deposit in DEPOSITS:
            report_path, tester_log = run_backtest(stem, from_date, to_date, deposit, LEVERAGE)
            metrics = parse_report(report_path)
            results.append(
                ScalingResult(
                    window=window_label,
                    from_date=from_date,
                    to_date=to_date,
                    deposit=deposit,
                    leverage=LEVERAGE,
                    report_path=str(report_path),
                    tester_log=str(tester_log) if tester_log else "",
                    net_profit=metrics["net_profit"],
                    profit_pct=(metrics["net_profit"] / deposit) * 100.0,
                    profit_factor=metrics["profit_factor"],
                    expected_payoff=metrics["expected_payoff"],
                    total_trades=int(metrics["total_trades"]),
                    win_rate=metrics["win_rate"],
                    balance_dd_abs=metrics["balance_dd_abs"],
                    balance_dd_pct=metrics["balance_dd_pct"],
                    equity_dd_abs=metrics["equity_dd_abs"],
                    equity_dd_pct=metrics["equity_dd_pct"],
                )
            )

    rows = [asdict(r) for r in results]
    (RUN_DIR / "v6_scaling_results.json").write_text(json.dumps(rows, indent=2))
    write_csv(RUN_DIR / "v6_scaling_results.csv", rows)

    by_window: dict[str, list[ScalingResult]] = {}
    for result in results:
        by_window.setdefault(result.window, []).append(result)

    lines = [
        "# v6 Fixed-Fractional Scaling Check",
        "",
        "Tujuan: membandingkan perilaku `v6` pada modal kecil dan besar dengan setup yang sama, untuk melihat apakah fixed-fractional sizing membuat hasil lebih invariant terhadap ukuran akun.",
        "",
    ]
    for window_label, from_date, to_date in WINDOWS:
        subset = sorted(by_window[window_label], key=lambda item: item.deposit)
        lines.extend(
            [
                f"## {window_label}",
                "",
                f"Period: `{from_date} - {to_date}`, `XAUUSDc`, `M15`, `Leverage {LEVERAGE}`, `Every tick`.",
                "",
                "| Deposit | Net Profit | Profit % | PF | Win Rate | Trades | Balance DD | Equity DD |",
                "| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
            ]
        )
        for item in subset:
            lines.append(
                f"| {item.deposit} | {item.net_profit:.2f} | {item.profit_pct:.2f}% | {item.profit_factor:.2f} | "
                f"{item.win_rate:.2f}% | {item.total_trades} | {item.balance_dd_pct:.2f}% | {item.equity_dd_pct:.2f}% |"
            )
        if len(subset) == 2:
            small, large = subset
            lines.extend(
                [
                    "",
                    f"- Trade count delta: `{large.total_trades - small.total_trades}` trades.",
                    f"- Profit %% delta: `{large.profit_pct - small.profit_pct:.2f}` percentage points.",
                    f"- PF delta: `{large.profit_factor - small.profit_factor:.2f}`.",
                    f"- Equity DD delta: `{large.equity_dd_pct - small.equity_dd_pct:.2f}` percentage points.",
                    "",
                ]
            )

    lines.extend(
        [
            "## Files",
            f"- [v6_scaling_results.json]({(RUN_DIR / 'v6_scaling_results.json').as_posix()})",
            f"- [v6_scaling_results.csv]({(RUN_DIR / 'v6_scaling_results.csv').as_posix()})",
        ]
    )
    (RUN_DIR / "v6_scaling_summary.md").write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
