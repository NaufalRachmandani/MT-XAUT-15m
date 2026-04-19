#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
import shutil
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path

ROOT = Path("/Users/naufalrachmandani/Hobby/MT5 XAU 15m")
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.compare_versions_6m_100 import (
    MT5_BUILD,
    MT5_EXPERTS,
    REPORTS_DIR,
    TERMINAL_EXE,
    WINE,
    build_ini,
    compile_variant,
    launch_subprocess,
    parse_report,
)

RUN_DIR = ROOT / "build" / "v8_round4_cross_scale"
RUN_DIR.mkdir(parents=True, exist_ok=True)

SOURCE = ROOT / "mt5" / "InvictusForward1M15_v8.mq5"
FROM_DATE = "2026.01.01"
TO_DATE = "2026.04.15"
LEV = "1:100"
DEPOSITS = [100, 10000]


@dataclass(frozen=True)
class Preset:
    name: str
    note: str
    overrides: dict[str, str]


PRESETS = [
    Preset("control", "Current v8 champion.", {}),
    Preset("trend195", "Slight trend risk uplift.", {
        "V7_TrendRiskPercent": "1.95",
    }),
    Preset("trend210", "Moderate trend risk uplift.", {
        "V7_TrendRiskPercent": "2.10",
    }),
    Preset("trend225", "Aggressive trend risk uplift.", {
        "V7_TrendRiskPercent": "2.25",
    }),
    Preset("buyrisk010", "Lower residual bearish-regime buy participation.", {
        "V8_BEARISH_BUY_RISK_MULT": "0.10",
    }),
    Preset("buyrisk020", "Higher residual bearish-regime buy participation.", {
        "V8_BEARISH_BUY_RISK_MULT": "0.20",
    }),
    Preset("close2_buy015", "Faster bearish regime detection.", {
        "V8_BEARISH_REGIME_CLOSE_LOOKBACK": "2",
    }),
    Preset("close2_buy010", "Faster bearish regime plus lower residual buy risk.", {
        "V8_BEARISH_REGIME_CLOSE_LOOKBACK": "2",
        "V8_BEARISH_BUY_RISK_MULT": "0.10",
    }),
]


def replace_named_value(text: str, name: str, value: str) -> str:
    patterns = [
        re.compile(rf"^(input\s+[^\n]*\b{name}\b)\s*=\s*[^;]+;", re.MULTILINE),
        re.compile(rf"^(static const\s+[^\n]*\b{name}\b)\s*=\s*[^;]+;", re.MULTILINE),
        re.compile(rf"^(static int\s+[^\n]*\b{name}\b\[\])\s*=\s*[^;]+;", re.MULTILINE),
        re.compile(rf"^(static int\s+[^\n]*\b{name}\b)\s*=\s*[^;]+;", re.MULTILINE),
    ]
    for pattern in patterns:
        text, count = pattern.subn(rf"\1 = {value};", text, count=1)
        if count == 1:
            return text
    raise RuntimeError(f"Failed to replace {name}")


def build_source(preset: Preset) -> Path:
    text = SOURCE.read_text()
    for name, value in preset.overrides.items():
        text = replace_named_value(text, name, value)
    path = RUN_DIR / f"InvictusForward1M15_v8_{preset.name}.mq5"
    path.write_text(text)
    return path


def run_backtest_safe(stem: str, deposit: int) -> Path:
    ini_path = MT5_BUILD / f"{stem}_{deposit}.backtest.ini"
    ini_path.write_text(build_ini(stem, FROM_DATE, TO_DATE, deposit, LEV))
    shutil.copy2(MT5_BUILD / f"{stem}.ex5", MT5_EXPERTS / f"{stem}.ex5")

    suffix = f"{FROM_DATE.replace('.', '')}_{TO_DATE.replace('.', '')}"
    report_path = REPORTS_DIR / f"{stem}_XAUUSDc_M15_{suffix}.htm"
    for old in REPORTS_DIR.glob(f"{stem}_XAUUSDc_M15_{suffix}*"):
        old.unlink(missing_ok=True)

    start_time = time.time()
    proc = launch_subprocess([WINE, TERMINAL_EXE, f"/config:C:\\MT5Build\\{ini_path.name}"])
    proc.wait(timeout=1200)
    deadline = time.time() + 120
    while time.time() < deadline:
        if report_path.exists() and report_path.stat().st_mtime >= start_time:
            return report_path
        time.sleep(1)
    raise RuntimeError(f"Missing report for {stem} deposit={deposit}")


def score(rows: list[dict[str, float]]) -> float:
    by_dep = {row["deposit"]: row for row in rows}
    low = by_dep[100]
    high = by_dep[10000]
    if low["equity_dd_pct"] > 15.0 or high["equity_dd_pct"] > 15.0:
        return -100000.0 + low["profit_pct"] + high["profit_pct"]
    return (
        low["profit_pct"] * 1.2
        + high["profit_pct"] * 0.8
        + (low["profit_factor"] - 1.0) * 80.0
        + (high["profit_factor"] - 1.0) * 60.0
        - low["equity_dd_pct"] * 1.2
        - high["equity_dd_pct"] * 1.0
    )


def main() -> None:
    all_rows: list[dict[str, float | str | int]] = []
    preset_summaries: list[dict[str, float | str]] = []
    for preset in PRESETS:
        source_path = build_source(preset)
        stem = compile_variant("v8", source_path, f"round4_{preset.name}")
        rows_for_preset = []
        for deposit in DEPOSITS:
            report_path = run_backtest_safe(stem, deposit)
            metrics = parse_report(report_path)
            row = {
                "preset": preset.name,
                "note": preset.note,
                "deposit": deposit,
                "report_path": str(report_path),
                "net_profit": metrics["net_profit"],
                "profit_pct": (metrics["net_profit"] / deposit) * 100.0,
                "profit_factor": metrics["profit_factor"],
                "win_rate": metrics["win_rate"],
                "total_trades": int(metrics["total_trades"]),
                "equity_dd_pct": metrics["equity_dd_pct"],
            }
            rows_for_preset.append(row)
            all_rows.append(row)
            print(
                f"[{preset.name}] deposit={deposit}: net={row['net_profit']:.2f} pct={row['profit_pct']:.2f}% "
                f"pf={row['profit_factor']:.2f} wr={row['win_rate']:.2f}% trades={row['total_trades']} "
                f"eqdd={row['equity_dd_pct']:.2f}%",
                flush=True,
            )
        preset_summaries.append({
            "preset": preset.name,
            "note": preset.note,
            "score": score(rows_for_preset),
            "profit_pct_100": next(r["profit_pct"] for r in rows_for_preset if r["deposit"] == 100),
            "eqdd_100": next(r["equity_dd_pct"] for r in rows_for_preset if r["deposit"] == 100),
            "pf_100": next(r["profit_factor"] for r in rows_for_preset if r["deposit"] == 100),
            "profit_pct_10000": next(r["profit_pct"] for r in rows_for_preset if r["deposit"] == 10000),
            "eqdd_10000": next(r["equity_dd_pct"] for r in rows_for_preset if r["deposit"] == 10000),
            "pf_10000": next(r["profit_factor"] for r in rows_for_preset if r["deposit"] == 10000),
        })

    (RUN_DIR / "results.json").write_text(json.dumps(all_rows, indent=2))
    with (RUN_DIR / "results.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(all_rows[0].keys()))
        writer.writeheader()
        writer.writerows(all_rows)

    ranked = sorted(preset_summaries, key=lambda row: row["score"], reverse=True)
    (RUN_DIR / "summary.json").write_text(json.dumps(ranked, indent=2))
    lines = [
        "# v8 Round 4 Cross-Scale",
        "",
        f"Window: `{FROM_DATE} - {TO_DATE}`, `XAUUSDc`, `M15`, deposits `100` and `10000`, `Leverage {LEV}`.",
        "",
        "| Rank | Preset | Pct $100 | PF $100 | DD $100 | Pct $10k | PF $10k | DD $10k |",
        "| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for idx, row in enumerate(ranked, start=1):
        lines.append(
            f"| {idx} | {row['preset']} | {row['profit_pct_100']:.2f}% | {row['pf_100']:.2f} | {row['eqdd_100']:.2f}% | "
            f"{row['profit_pct_10000']:.2f}% | {row['pf_10000']:.2f} | {row['eqdd_10000']:.2f}% |"
        )
    (RUN_DIR / "summary.md").write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
