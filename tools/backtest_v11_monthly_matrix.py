#!/usr/bin/env python3
from __future__ import annotations

import calendar
import json
import sys
from pathlib import Path

ROOT = Path("/Users/naufalrachmandani/Hobby/MT5 XAU 15m")
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.backtest_v11_split import compile_exact, parse_report, run_backtest  # noqa: E402
from tools.iterate_v11_10x import write_tester_set, load_set  # noqa: E402

RUN_DIR = ROOT / "build" / "v11_monthly_matrix"
RUN_DIR.mkdir(parents=True, exist_ok=True)

STEM = "InvictusCombinedM5_v11"
BASE_SET = ROOT / "mt5" / "InvictusCombinedM5_v11.default_2026.set"
END_YEAR = 2026
END_MONTH = 4
END_DAY = 25


def month_windows(start_year: int = 2023) -> list[tuple[str, str, str]]:
    windows: list[tuple[str, str, str]] = []
    for year in range(start_year, END_YEAR + 1):
        last_month = END_MONTH if year == END_YEAR else 12
        for month in range(1, last_month + 1):
            last_day = END_DAY if (year == END_YEAR and month == END_MONTH) else calendar.monthrange(year, month)[1]
            label = f"{year}-{month:02d}"
            windows.append((label, f"{year}.{month:02d}.01", f"{year}.{month:02d}.{last_day:02d}"))
    return windows


def classify(row: dict[str, float]) -> str:
    net = row["net_profit"]
    trades = row["total_trades"]
    dd = row["equity_dd_pct"]
    pf = row["profit_factor"]
    if trades < 5:
        return "LOW_SAMPLE"
    if net < 0:
        return "RED"
    if dd >= 30:
        return "HIGH_DD"
    if pf < 1.2:
        return "LOW_EDGE"
    if net >= 100 and pf >= 1.8:
        return "EXPANSION_EDGE"
    return "NORMAL"


def main() -> None:
    compile_exact(STEM)
    base = load_set(BASE_SET)
    set_name = write_tester_set(STEM, "monthly_matrix", base)

    rows = []
    for label, from_date, to_date in month_windows():
        print(f"monthly {label} {from_date}-{to_date}", flush=True)
        report = run_backtest(STEM, set_name, from_date, to_date)
        metrics = parse_report(report)
        rows.append(
            {
                "month": label,
                "from": from_date,
                "to": to_date,
                "metrics": metrics,
                "regime_note": classify(metrics),
                "report": str(report),
            }
        )

    (RUN_DIR / "results.json").write_text(json.dumps(rows, indent=2))
    lines = [
        "# v11 Monthly Matrix",
        "",
        "Setup: `InvictusCombinedM5_v11`, `XAUUSDc`, `M5`, `Deposit 100 USD`, `Leverage 1:100`, `Every tick`.",
        "",
        "| Month | Net | Trades | Win Rate | PF | EqDD | Note |",
        "| --- | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in rows:
        m = row["metrics"]
        lines.append(
            f"| {row['month']} | {m['net_profit']:.2f} | {m['total_trades']:.0f} | "
            f"{m['win_rate']:.2f}% | {m['profit_factor']:.2f} | {m['equity_dd_pct']:.2f}% | {row['regime_note']} |"
        )

    yearly: dict[str, dict[str, float]] = {}
    for row in rows:
        year = row["month"][:4]
        m = row["metrics"]
        item = yearly.setdefault(year, {"net": 0.0, "trades": 0.0, "red_months": 0.0, "max_dd": 0.0})
        item["net"] += m["net_profit"]
        item["trades"] += m["total_trades"]
        item["max_dd"] = max(item["max_dd"], m["equity_dd_pct"])
        if m["net_profit"] < 0:
            item["red_months"] += 1

    lines.extend(["", "## Year Summary", "", "| Year | Sum Monthly Net | Trades | Red Months | Worst Monthly EqDD |", "| --- | ---: | ---: | ---: | ---: |"])
    for year, item in sorted(yearly.items()):
        lines.append(f"| {year} | {item['net']:.2f} | {item['trades']:.0f} | {item['red_months']:.0f} | {item['max_dd']:.2f}% |")

    worst = sorted(rows, key=lambda row: (row["metrics"]["net_profit"], -row["metrics"]["equity_dd_pct"]))[:8]
    lines.extend(["", "## Worst Months", "", "| Month | Net | Trades | PF | EqDD | Note |", "| --- | ---: | ---: | ---: | ---: | --- |"])
    for row in worst:
        m = row["metrics"]
        lines.append(f"| {row['month']} | {m['net_profit']:.2f} | {m['total_trades']:.0f} | {m['profit_factor']:.2f} | {m['equity_dd_pct']:.2f}% | {row['regime_note']} |")

    (RUN_DIR / "summary.md").write_text("\n".join(lines) + "\n")
    print(RUN_DIR / "summary.md")


if __name__ == "__main__":
    main()
