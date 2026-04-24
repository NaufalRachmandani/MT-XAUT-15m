#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import shutil
import sys
import textwrap
import time
from dataclasses import dataclass
from pathlib import Path

ROOT = Path("/Users/naufalrachmandani/Hobby/MT5 XAU 15m")
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.compare_versions_6m_100 import (  # noqa: E402
    MT5_BUILD,
    MT5_EXPERTS,
    REPORTS_DIR,
    TERMINAL_EXE,
    WINE,
    compile_variant,
    latest_tester_log,
    launch_subprocess,
    parse_report,
)

RUN_DIR = ROOT / "build" / "v10_dual_m5_round2"
RUN_DIR.mkdir(parents=True, exist_ok=True)

SOURCE = ROOT / "mt5" / "InvictusForward1M15_v10.mq5"
DEPOSIT = 100
LEV = "1:100"

WINDOWS = [
    ("2025-11", "2025.11.01", "2025.11.30"),
    ("2025-12", "2025.12.01", "2025.12.31"),
    ("2025-current", "2025.01.01", "2026.04.15"),
    ("2026-only", "2026.01.01", "2026.04.15"),
]


@dataclass(frozen=True)
class Preset:
    name: str
    note: str
    overrides: dict[str, str]


BASE = {
    "V10_RiskPercent": "4.50",
    "V10_BuyRiskMultiplier": "0.45",
    "V10_SellRiskMultiplier": "1.00",
    "V10_WeakBuyRiskMultiplier": "0.15",
    "V10_WeakSellRiskMultiplier": "0.55",
    "V10_MaxPositions": "3",
    "V10_WeakRegimeMaxPositions": "1",
    "V10_SellSessionStartHour": "8",
    "V10_SellSessionEndHour": "20",
    "V10_BuySessionStartHour": "5",
    "V10_BuySessionEndHour": "20",
    "V10_H1ADXMin": "20.0",
    "V10_H1ADXStrongMin": "26.0",
    "V10_StrongGapATR": "0.10",
    "V10_BullPullbackLookback": "8",
    "V10_BullTouchATR": "0.12",
    "V10_BullReclaimATR": "0.02",
    "V10_BullMaxStretchATR": "1.10",
    "V10_BearRejectLookback": "6",
    "V10_BearTouchATR": "0.12",
    "V10_BearBreakBelowPrevATR": "0.02",
    "V10_BearMaxStretchATR": "1.30",
    "V10_BuyMinBodyRatio": "0.54",
    "V10_WeakBuyMinBodyRatio": "0.60",
    "V10_MinBodyRatio": "0.48",
    "V10_WeakSellMinBodyRatio": "0.54",
    "V10_BuyRR": "1.40",
    "V10_WeakBuyRR": "1.20",
    "V10_SellRR": "1.30",
    "V10_WeakSellRR": "1.10",
    "V10_MaxHoldBars": "24",
    "V10_CloseOnRegimeFlip": "true",
}


def merged(**kwargs: str) -> dict[str, str]:
    data = dict(BASE)
    data.update(kwargs)
    return data


PRESETS = [
    Preset("control_hybrid", "Hybrid buy engine with v9-style sell engine.", merged()),
    Preset(
        "bull_open",
        "Open bull participation earlier with moderate scaling.",
        merged(
            V10_BuyRiskMultiplier="0.60",
            V10_WeakBuyRiskMultiplier="0.20",
            V10_MaxPositions="4",
            V10_WeakRegimeMaxPositions="2",
            V10_BuySessionStartHour="3",
            V10_BuySessionEndHour="23",
            V10_BullTouchATR="0.15",
            V10_BullReclaimATR="0.00",
            V10_BuyRR="1.55",
            V10_WeakBuyRR="1.30",
        ),
    ),
    Preset(
        "bull_open_carry",
        "Open bull participation and let winners run longer.",
        merged(
            V10_BuyRiskMultiplier="0.60",
            V10_WeakBuyRiskMultiplier="0.20",
            V10_MaxPositions="4",
            V10_WeakRegimeMaxPositions="2",
            V10_BuySessionStartHour="3",
            V10_BuySessionEndHour="23",
            V10_BullTouchATR="0.15",
            V10_BullReclaimATR="0.00",
            V10_BuyRR="1.55",
            V10_WeakBuyRR="1.30",
            V10_MaxHoldBars="36",
            V10_CloseOnRegimeFlip="false",
        ),
    ),
    Preset(
        "bull_breakout_loose",
        "Looser bullish breakout thresholds on top of hybrid buy path.",
        merged(
            V10_BuyRiskMultiplier="0.55",
            V10_WeakBuyRiskMultiplier="0.20",
            V10_BuySessionStartHour="3",
            V10_BuySessionEndHour="23",
            V10_BuyMinBreakATR="0.08",
            V10_WeakBuyMinBreakATR="0.12",
            V10_BuyMinBodyRatio="0.48",
            V10_WeakBuyMinBodyRatio="0.54",
            V10_BuyRR="1.55",
            V10_WeakBuyRR="1.30",
        ),
    ),
    Preset(
        "bull_breakout_rr",
        "Bull breakout path with wider profit target.",
        merged(
            V10_BuyRiskMultiplier="0.60",
            V10_WeakBuyRiskMultiplier="0.20",
            V10_BuySessionStartHour="3",
            V10_BuySessionEndHour="23",
            V10_BuyMinBreakATR="0.08",
            V10_WeakBuyMinBreakATR="0.12",
            V10_BuyRR="1.70",
            V10_WeakBuyRR="1.40",
        ),
    ),
    Preset(
        "bull_pb_focus",
        "Bias the buy side toward reclaim after deeper pullback.",
        merged(
            V10_BuyRiskMultiplier="0.55",
            V10_WeakBuyRiskMultiplier="0.20",
            V10_BuySessionStartHour="3",
            V10_BuySessionEndHour="23",
            V10_BullTouchATR="0.18",
            V10_BullReclaimATR="0.00",
            V10_BullMaxStretchATR="1.30",
            V10_BuyRR="1.60",
            V10_WeakBuyRR="1.30",
        ),
    ),
    Preset(
        "bull_trend_hold",
        "Higher buy risk plus longer hold for trending months.",
        merged(
            V10_BuyRiskMultiplier="0.70",
            V10_WeakBuyRiskMultiplier="0.25",
            V10_MaxPositions="4",
            V10_WeakRegimeMaxPositions="2",
            V10_BuySessionStartHour="3",
            V10_BuySessionEndHour="23",
            V10_BuyRR="1.70",
            V10_WeakBuyRR="1.45",
            V10_MaxHoldBars="40",
            V10_CloseOnRegimeFlip="false",
        ),
    ),
    Preset(
        "late2025_probe",
        "Probe a more aggressive late-2025 bullish adaptation.",
        merged(
            V10_BuyRiskMultiplier="0.75",
            V10_WeakBuyRiskMultiplier="0.30",
            V10_MaxPositions="5",
            V10_WeakRegimeMaxPositions="2",
            V10_BuySessionStartHour="2",
            V10_BuySessionEndHour="23",
            V10_BuyMinBreakATR="0.08",
            V10_WeakBuyMinBreakATR="0.10",
            V10_BullTouchATR="0.18",
            V10_BullReclaimATR="0.00",
            V10_BullMaxStretchATR="1.40",
            V10_BuyRR="1.65",
            V10_WeakBuyRR="1.35",
        ),
    ),
    Preset(
        "bearish_anchor",
        "Keep sell side slightly stronger while loosening buy engine.",
        merged(
            V10_BuyRiskMultiplier="0.60",
            V10_WeakBuyRiskMultiplier="0.20",
            V10_SellRiskMultiplier="1.10",
            V10_WeakSellRiskMultiplier="0.60",
            V10_MaxPositions="4",
            V10_WeakRegimeMaxPositions="2",
            V10_BuySessionStartHour="3",
            V10_BuySessionEndHour="23",
            V10_BullTouchATR="0.15",
            V10_BullReclaimATR="0.00",
            V10_BuyRR="1.55",
            V10_WeakBuyRR="1.35",
        ),
    ),
    Preset(
        "balanced_guard",
        "Moderate bullish opening with tighter spread guard.",
        merged(
            V10_BuyRiskMultiplier="0.55",
            V10_WeakBuyRiskMultiplier="0.20",
            V10_MaxPositions="4",
            V10_WeakRegimeMaxPositions="2",
            V10_BuySessionStartHour="4",
            V10_BuySessionEndHour="22",
            V10_BullTouchATR="0.15",
            V10_BullReclaimATR="0.00",
            V10_BuyRR="1.55",
            V10_WeakBuyRR="1.30",
            V10_MaxSpreadUsd="1.00",
        ),
    ),
    Preset(
        "mixed_full",
        "Looser hybrid buy with more stacking, sell unchanged.",
        merged(
            V10_BuyRiskMultiplier="0.65",
            V10_WeakBuyRiskMultiplier="0.22",
            V10_MaxPositions="4",
            V10_WeakRegimeMaxPositions="2",
            V10_BuySessionStartHour="3",
            V10_BuySessionEndHour="23",
            V10_BuyMinBreakATR="0.08",
            V10_WeakBuyMinBreakATR="0.12",
            V10_BullTouchATR="0.16",
            V10_BullReclaimATR="0.00",
            V10_BullMaxStretchATR="1.30",
            V10_BuyRR="1.60",
            V10_WeakBuyRR="1.35",
        ),
    ),
]


def replace_named_value(text: str, name: str, value: str) -> str:
    escaped = re.escape(name)
    pattern = re.compile(rf"^(input\s+[^\n]*{escaped})\s*=\s*[^;]+;", re.MULTILINE)
    text, count = pattern.subn(rf"\1 = {value};", text, count=1)
    if count == 1:
        return text
    raise RuntimeError(f"Failed to replace {name}")


def build_source(preset: Preset) -> Path:
    text = SOURCE.read_text()
    for name, value in preset.overrides.items():
        text = replace_named_value(text, name, value)
    path = RUN_DIR / f"InvictusForward1M15_v10_{preset.name}.mq5"
    path.write_text(text)
    return path


def build_ini(stem: str, from_date: str, to_date: str) -> str:
    suffix = f"{from_date.replace('.', '')}_{to_date.replace('.', '')}"
    return textwrap.dedent(
        f"""\
        [Common]
        Login=257385275
        Server=Exness-MT5Real36
        ProxyEnable=0
        KeepPrivate=1
        NewsEnable=1
        CertInstall=1

        [Experts]
        AllowLiveTrading=0
        AllowDllImport=0
        Enabled=1
        Account=0
        Profile=0

        [Tester]
        Expert=Invictus\\{stem}.ex5
        Symbol=XAUUSDc
        Period=M5
        Login=257385275
        Model=0
        ExecutionMode=0
        Optimization=0
        FromDate={from_date}
        ToDate={to_date}
        ForwardMode=0
        Report=\\Reports\\{stem}_XAUUSDc_M5_{suffix}
        ReplaceReport=1
        ShutdownTerminal=1
        Deposit={DEPOSIT}
        Currency=USD
        Leverage={LEV}
        UseLocal=1
        UseRemote=0
        UseCloud=0
        Visual=0
        """
    )


def run_backtest(stem: str, from_date: str, to_date: str) -> tuple[Path, Path | None]:
    ini_path = MT5_BUILD / f"{stem}.backtest.ini"
    ini_path.write_text(build_ini(stem, from_date, to_date))
    shutil.copy2(MT5_BUILD / f"{stem}.ex5", MT5_EXPERTS / f"{stem}.ex5")

    suffix = f"{from_date.replace('.', '')}_{to_date.replace('.', '')}"
    report_path = REPORTS_DIR / f"{stem}_XAUUSDc_M5_{suffix}.htm"
    for old in REPORTS_DIR.glob(f"{stem}_XAUUSDc_M5_{suffix}*"):
        old.unlink(missing_ok=True)

    pre_log = latest_tester_log()
    pre_size = pre_log.stat().st_size if pre_log and pre_log.exists() else 0
    proc = launch_subprocess([WINE, TERMINAL_EXE, f"/config:C:\\MT5Build\\{stem}.backtest.ini"])
    start_time = time.time()
    stable_size = -1
    stable_hits = 0
    deadline = time.time() + 1200
    active_log: Path | None = pre_log

    while time.time() < deadline:
        current_log = latest_tester_log()
        if current_log is not None:
            active_log = current_log

        if report_path.exists():
            stat = report_path.stat()
            if stat.st_mtime >= start_time:
                log_done = False
                if active_log and active_log.exists():
                    raw_bytes = active_log.read_bytes()
                    if active_log == pre_log:
                        tail_text = raw_bytes[pre_size:].decode("utf-16le", errors="ignore")
                    else:
                        tail_text = raw_bytes.decode("utf-16le", errors="ignore")
                    if "automatical testing finished" in tail_text:
                        log_done = True

                if stat.st_size == stable_size:
                    stable_hits += 1
                else:
                    stable_size = stat.st_size
                    stable_hits = 0

                if log_done and stable_hits >= 2:
                    break
        time.sleep(2)

    if proc.poll() is None:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except Exception:
            proc.kill()
            proc.wait(timeout=10)

    if not report_path.exists():
        raise RuntimeError(f"Missing report for {stem}")
    return report_path, active_log


def score_result(metrics: dict[str, dict[str, float]]) -> float:
    nov = metrics["2025-11"]
    dec = metrics["2025-12"]
    full = metrics["2025-current"]
    y26 = metrics["2026-only"]
    return (
        (nov["net_profit"] * 0.35)
        + (dec["net_profit"] * 0.45)
        + (full["net_profit"] * 0.12)
        + (y26["net_profit"] * 0.75)
        + (nov["profit_factor"] - 1.0) * 30.0
        + (dec["profit_factor"] - 1.0) * 35.0
        + (full["profit_factor"] - 1.0) * 35.0
        + (y26["profit_factor"] - 1.0) * 40.0
        - (nov["equity_dd_pct"] * 0.40)
        - (dec["equity_dd_pct"] * 0.45)
        - (full["equity_dd_pct"] * 0.25)
        - (y26["equity_dd_pct"] * 0.30)
    )


def main() -> None:
    results = []
    for preset in PRESETS:
        source_path = build_source(preset)
        stem = compile_variant("v10", source_path, preset.name)
        metrics_by_window: dict[str, dict[str, float]] = {}
        reports: dict[str, str] = {}
        logs: dict[str, str] = {}
        for label, from_date, to_date in WINDOWS:
            report_path, tester_log = run_backtest(stem, from_date, to_date)
            metrics_by_window[label] = parse_report(report_path)
            reports[label] = str(report_path)
            logs[label] = str(tester_log) if tester_log else ""
        results.append(
            {
                "name": preset.name,
                "note": preset.note,
                "overrides": preset.overrides,
                "reports": reports,
                "tester_logs": logs,
                "metrics": metrics_by_window,
                "score": score_result(metrics_by_window),
            }
        )

    results.sort(key=lambda item: item["score"], reverse=True)
    (RUN_DIR / "results.json").write_text(json.dumps(results, indent=2))

    lines = [
        "# v10 Dual M5 Round 2",
        "",
        "Setup: `XAUUSDc`, `M5`, `Deposit 100 USD`, `Leverage 1:100`, `Every tick`.",
        "",
        "| Rank | Preset | 2025-11 Net % | 2025-11 PF | 2025-11 EqDD | 2025-12 Net % | 2025-12 PF | 2025-12 EqDD | 2025-Current Net % | 2025-Current PF | 2025-Current EqDD | 2026 Net % | 2026 PF | 2026 EqDD | Score |",
        "| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for idx, item in enumerate(results, start=1):
        nov = item["metrics"]["2025-11"]
        dec = item["metrics"]["2025-12"]
        full = item["metrics"]["2025-current"]
        y26 = item["metrics"]["2026-only"]
        lines.append(
            f"| {idx} | {item['name']} | {nov['net_profit']:.2f}% | {nov['profit_factor']:.2f} | {nov['equity_dd_pct']:.2f}% | "
            f"{dec['net_profit']:.2f}% | {dec['profit_factor']:.2f} | {dec['equity_dd_pct']:.2f}% | "
            f"{full['net_profit']:.2f}% | {full['profit_factor']:.2f} | {full['equity_dd_pct']:.2f}% | "
            f"{y26['net_profit']:.2f}% | {y26['profit_factor']:.2f} | {y26['equity_dd_pct']:.2f}% | {item['score']:.2f} |"
        )
    (RUN_DIR / "summary.md").write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
