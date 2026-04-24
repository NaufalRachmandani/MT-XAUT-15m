#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import shutil
import sys
import textwrap
import time
from dataclasses import dataclass
from datetime import datetime
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

RUN_DIR = ROOT / "build" / "v10_zone_m5_round1"
RUN_DIR.mkdir(parents=True, exist_ok=True)

SOURCE = ROOT / "mt5" / "InvictusForward1M15_v10.mq5"
DEPOSIT = 100
LEV = "1:100"

WINDOWS = [
    ("recent_2m", "2026.02.22", "2026.04.22"),
    ("recent_1m", "2026.03.22", "2026.04.22"),
    ("2026_only", "2026.01.01", "2026.04.15"),
]


@dataclass(frozen=True)
class Preset:
    name: str
    note: str
    overrides: dict[str, str]


def merged(**kwargs: str) -> dict[str, str]:
    return dict(kwargs)


PRESETS = [
    Preset("control", "Official v10 control.", merged()),
    Preset(
        "zone_soft",
        "Base-inspired zone retest with permissive weak-regime access.",
        merged(
            V10_EnableZoneRetestEngine="true",
            V10_ZoneAllowWeakRegime="true",
            V10_ZoneUseCoreHours="false",
            V10_ZoneLookback="12",
            V10_ZoneMinBodyRatio="0.54",
            V10_ZoneBreakATR="0.04",
            V10_ZoneMidTouchATR="0.08",
            V10_ZoneOvershootATR="0.24",
            V10_ZoneRiskMultiplier="0.45",
            V10_ZoneRR="1.35",
            V10_ZoneMaxHoldBars="16",
        ),
    ),
    Preset(
        "zone_mid",
        "Balanced zone retest closest to base thinking.",
        merged(
            V10_EnableZoneRetestEngine="true",
            V10_ZoneAllowWeakRegime="true",
            V10_ZoneUseCoreHours="true",
            V10_ZoneLookback="12",
            V10_ZoneMinBodyRatio="0.56",
            V10_ZoneBreakATR="0.05",
            V10_ZoneMidTouchATR="0.06",
            V10_ZoneOvershootATR="0.20",
            V10_ZoneRiskMultiplier="0.55",
            V10_ZoneRR="1.45",
            V10_ZoneMaxHoldBars="18",
        ),
    ),
    Preset(
        "zone_push",
        "Push quantity with looser break/body and bigger zone participation.",
        merged(
            V10_EnableZoneRetestEngine="true",
            V10_ZoneAllowWeakRegime="true",
            V10_ZoneUseCoreHours="false",
            V10_ZoneLookback="10",
            V10_ZoneMinBodyRatio="0.52",
            V10_ZoneBreakATR="0.03",
            V10_ZoneMidTouchATR="0.10",
            V10_ZoneOvershootATR="0.28",
            V10_ZoneRiskMultiplier="0.70",
            V10_ZoneRR="1.30",
            V10_ZoneMaxHoldBars="16",
            V10_MaxPositions="5",
        ),
    ),
    Preset(
        "zone_dual_hold",
        "Zone retest with longer hold to capture continuation after reclaim.",
        merged(
            V10_EnableZoneRetestEngine="true",
            V10_ZoneAllowWeakRegime="true",
            V10_ZoneUseCoreHours="false",
            V10_ZoneLookback="12",
            V10_ZoneMinBodyRatio="0.54",
            V10_ZoneBreakATR="0.04",
            V10_ZoneMidTouchATR="0.08",
            V10_ZoneOvershootATR="0.24",
            V10_ZoneRiskMultiplier="0.60",
            V10_ZoneRR="1.55",
            V10_ZoneMaxHoldBars="24",
        ),
    ),
    Preset(
        "zone_core_clean",
        "Stronger quality filter, core-hours only, strong regime only.",
        merged(
            V10_EnableZoneRetestEngine="true",
            V10_ZoneAllowWeakRegime="false",
            V10_ZoneUseCoreHours="true",
            V10_ZoneLookback="14",
            V10_ZoneMinBodyRatio="0.58",
            V10_ZoneBreakATR="0.06",
            V10_ZoneMidTouchATR="0.05",
            V10_ZoneOvershootATR="0.18",
            V10_ZoneRiskMultiplier="0.50",
            V10_ZoneRR="1.55",
            V10_ZoneMaxHoldBars="20",
        ),
    ),
    Preset(
        "zone_buyheavy",
        "Favor bullish zone stacking in line with base buy-first bias.",
        merged(
            V10_EnableZoneRetestEngine="true",
            V10_ZoneAllowWeakRegime="true",
            V10_ZoneUseCoreHours="false",
            V10_ZoneLookback="11",
            V10_ZoneMinBodyRatio="0.54",
            V10_ZoneBreakATR="0.04",
            V10_ZoneRiskMultiplier="0.60",
            V10_ZoneRR="1.40",
            V10_BuyRiskMultiplier="0.60",
            V10_WeakBuyRiskMultiplier="0.22",
            V10_MaxPositions="5",
        ),
    ),
    Preset(
        "zone_sellheavy",
        "Lean into bearish retests for 2026-style drops.",
        merged(
            V10_EnableZoneRetestEngine="true",
            V10_ZoneAllowWeakRegime="true",
            V10_ZoneUseCoreHours="false",
            V10_ZoneLookback="11",
            V10_ZoneMinBodyRatio="0.54",
            V10_ZoneBreakATR="0.04",
            V10_ZoneRiskMultiplier="0.60",
            V10_ZoneRR="1.35",
            V10_SellRiskMultiplier="1.15",
            V10_WeakSellRiskMultiplier="0.65",
            V10_MaxPositions="5",
        ),
    ),
    Preset(
        "zone_base_imit",
        "Closer to explorer/base: zone reclaim + no add-ons.",
        merged(
            V10_EnableZoneRetestEngine="true",
            V10_ZoneAllowWeakRegime="false",
            V10_ZoneUseCoreHours="true",
            V10_ZoneLookback="12",
            V10_ZoneMinBodyRatio="0.56",
            V10_ZoneBreakATR="0.05",
            V10_ZoneMidTouchATR="0.06",
            V10_ZoneRiskMultiplier="0.55",
            V10_ZoneRR="1.50",
            V10_EnableAddOnEngine="false",
            V10_MaxPositions="4",
        ),
    ),
    Preset(
        "zone_hybrid_quantity",
        "Zone retest plus slightly more permissive add-on layering.",
        merged(
            V10_EnableZoneRetestEngine="true",
            V10_ZoneAllowWeakRegime="true",
            V10_ZoneUseCoreHours="false",
            V10_ZoneLookback="10",
            V10_ZoneMinBodyRatio="0.54",
            V10_ZoneBreakATR="0.04",
            V10_ZoneRiskMultiplier="0.50",
            V10_ZoneRR="1.40",
            V10_MaxPositions="5",
            V10_AddOnMaxPerSide="2",
            V10_AddOnMinProgressR="0.60",
            V10_AddOnRiskMultiplier="0.30",
            V10_AddOnRR="1.05",
        ),
    ),
    Preset(
        "zone_session_open",
        "Wider sessions to mimic base session thinking on M5.",
        merged(
            V10_EnableZoneRetestEngine="true",
            V10_ZoneAllowWeakRegime="true",
            V10_ZoneUseCoreHours="false",
            V10_ZoneLookback="12",
            V10_ZoneMinBodyRatio="0.54",
            V10_ZoneBreakATR="0.04",
            V10_ZoneRiskMultiplier="0.55",
            V10_ZoneRR="1.45",
            V10_BuySessionStartHour="3",
            V10_BuySessionEndHour="23",
            V10_SellSessionStartHour="6",
            V10_SellSessionEndHour="23",
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
    deadline = time.time() + 1800
    active_log: Path | None = pre_log

    while time.time() < deadline:
        current_log = latest_tester_log()
        if current_log is not None:
            active_log = current_log

        if report_path.exists():
            stat = report_path.stat()
            if stat.st_mtime >= start_time:
                if stat.st_size == stable_size:
                    stable_hits += 1
                else:
                    stable_size = stat.st_size
                    stable_hits = 0

                if proc.poll() is not None and stable_hits >= 1:
                    break
                if stable_hits >= 2:
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


def trades_per_week(total_trades: float, from_date: str, to_date: str) -> float:
    start = datetime.strptime(from_date, "%Y.%m.%d")
    end = datetime.strptime(to_date, "%Y.%m.%d")
    days = max(1, (end - start).days)
    return total_trades / (days / 7.0)


def score_result(metrics: dict[str, dict[str, float]]) -> float:
    r2 = metrics["recent_2m"]
    r1 = metrics["recent_1m"]
    y26 = metrics["2026_only"]
    return (
        (r2["net_profit"] * 1.30)
        + (trades_per_week(r2["total_trades"], "2026.02.22", "2026.04.22") * 8.0)
        + (r1["net_profit"] * 0.80)
        + (trades_per_week(r1["total_trades"], "2026.03.22", "2026.04.22") * 10.0)
        + (y26["net_profit"] * 0.65)
        + (trades_per_week(y26["total_trades"], "2026.01.01", "2026.04.15") * 4.0)
        - (max(0.0, r2["equity_dd_pct"] - 25.0) * 1.0)
        - (max(0.0, y26["equity_dd_pct"] - 35.0) * 0.8)
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
        "# v10 Zone M5 Round 1",
        "",
        "Setup: `XAUUSDc`, `M5`, `Deposit 100 USD`, `Leverage 1:100`, `Every tick`.",
        "",
        "| Rank | Preset | Recent 2M Net % | Recent 2M Trades | Recent 2M / Week | 1M Net % | 1M Trades | 1M / Week | 2026 Net % | 2026 Trades | 2026 / Week | Score |",
        "| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for idx, item in enumerate(results, start=1):
        r2 = item["metrics"]["recent_2m"]
        r1 = item["metrics"]["recent_1m"]
        y26 = item["metrics"]["2026_only"]
        lines.append(
            f"| {idx} | {item['name']} | {r2['net_profit']:.2f}% | {r2['total_trades']:.0f} | {trades_per_week(r2['total_trades'], '2026.02.22', '2026.04.22'):.2f} | "
            f"{r1['net_profit']:.2f}% | {r1['total_trades']:.0f} | {trades_per_week(r1['total_trades'], '2026.03.22', '2026.04.22'):.2f} | "
            f"{y26['net_profit']:.2f}% | {y26['total_trades']:.0f} | {trades_per_week(y26['total_trades'], '2026.01.01', '2026.04.15'):.2f} | "
            f"{item['score']:.2f} |"
        )
    (RUN_DIR / "summary.md").write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
