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
    WINEPREFIX,
    compile_variant,
    latest_tester_log,
    launch_subprocess,
    parse_report,
)
from tools.analyze_mt5_report import extract_deal_rows, parse_deals  # noqa: E402

RUN_DIR = ROOT / "build" / "v10_week_livefix"
RUN_DIR.mkdir(parents=True, exist_ok=True)

SOURCE = ROOT / "mt5" / "InvictusForward1M15_v10.mq5"
TESTER_PROFILE_DIR = WINEPREFIX / "drive_c" / "Program Files" / "MetaTrader 5" / "MQL5" / "Profiles" / "Tester"
DEPOSIT = 100
LEV = "1:100"

WINDOWS = [
    ("week", "2026.04.20", "2026.04.25"),
    ("last_2w", "2026.04.10", "2026.04.25"),
    ("2026_ytd", "2026.01.01", "2026.04.25"),
]


@dataclass(frozen=True)
class Preset:
    name: str
    note: str
    overrides: dict[str, str]
    patches: tuple[str, ...] = ()


def replace_named_value(text: str, name: str, value: str) -> str:
    escaped = re.escape(name)
    pattern = re.compile(rf"^(input\s+[^\n]*{escaped})\s*=\s*[^;]+;", re.MULTILINE)
    text, count = pattern.subn(rf"\1 = {value};", text, count=1)
    if count == 1:
        return text
    raise RuntimeError(f"Failed to replace {name}")


def patch_weak_sell_xh_block(text: str) -> str:
    needle = "   bool sessionCore = V10HourInSession(currentHour, 10, 17);\n   int score = 40;"
    repl = (
        "   bool sessionCore = V10HourInSession(currentHour, 10, 17);\n"
        "   if(!V10RegimeIsStrong(regime) && !sessionCore)\n"
        "      return(false);\n"
        "   int score = 40;"
    )
    if needle not in text:
        raise RuntimeError("weak sell XH block insertion point not found")
    return text.replace(needle, repl, 1)


def patch_weak_sell_xh_gate72(text: str) -> str:
    needle = "   if(cleanStretch)\n      score += 5;\n   if(V10_MinTradeScore > 0 && score < V10_MinTradeScore)"
    repl = (
        "   if(cleanStretch)\n"
        "      score += 5;\n"
        "   if(!V10RegimeIsStrong(regime) && !sessionCore && score < 72)\n"
        "      return(false);\n"
        "   if(V10_MinTradeScore > 0 && score < V10_MinTradeScore)"
    )
    if needle not in text:
        raise RuntimeError("weak sell XH gate insertion point not found")
    return text.replace(needle, repl, 1)


def patch_base_sell_score72(text: str) -> str:
    needle = "   if(cleanStretch)\n      score += 5;\n   if(V10_MinTradeScore > 0 && score < V10_MinTradeScore)"
    repl = (
        "   if(cleanStretch)\n"
        "      score += 5;\n"
        "   if(score < 72)\n"
        "      return(false);\n"
        "   if(V10_MinTradeScore > 0 && score < V10_MinTradeScore)"
    )
    if needle not in text:
        raise RuntimeError("base sell score gate insertion point not found")
    return text.replace(needle, repl, 1)


def patch_quick_exit_weak_sell_xh(text: str) -> str:
    needle = "      if(V10_FastFailBuyGuard && type == POSITION_TYPE_BUY && barsHeld <= V10_FastFailBars && emaM5 > 0.0)"
    repl = (
        "      bool weakOutsideBaseSell = type == POSITION_TYPE_SELL &&\n"
        "                                 StringFind(comment, \"|BE|\") >= 0 &&\n"
        "                                 StringFind(comment, \"|WG|\") >= 0 &&\n"
        "                                 StringFind(comment, \"|XH|\") >= 0;\n"
        "      if(weakOutsideBaseSell && barsHeld >= 6 && PositionGetDouble(POSITION_PROFIT) < 0.0)\n"
        "        {\n"
        "         g_trade.PositionClose(ticket);\n"
        "         continue;\n"
        "        }\n"
        "      if(V10_FastFailBuyGuard && type == POSITION_TYPE_BUY && barsHeld <= V10_FastFailBars && emaM5 > 0.0)"
    )
    if needle not in text:
        raise RuntimeError("quick exit insertion point not found")
    return text.replace(needle, repl, 1)


def patch_fast_fail_both(text: str) -> str:
    needle = "      bool regimeFlip = V10_CloseOnRegimeFlip &&"
    repl = (
        "      if(barsHeld <= 8 && emaM5 > 0.0 && PositionGetDouble(POSITION_PROFIT) < 0.0)\n"
        "        {\n"
        "         double progressR = favorable / riskDistance;\n"
        "         double failBuffer = (atrM5 > 0.0) ? (atrM5 * V10_HoldBufferATR) : 0.0;\n"
        "         bool trendFailed = (type == POSITION_TYPE_BUY)\n"
        "                            ? (currentPrice <= (emaM5 + failBuffer))\n"
        "                            : (currentPrice >= (emaM5 - failBuffer));\n"
        "         if(trendFailed && progressR < 0.05)\n"
        "           {\n"
        "            g_trade.PositionClose(ticket);\n"
        "            continue;\n"
        "           }\n"
        "        }\n"
        "      bool regimeFlip = V10_CloseOnRegimeFlip &&"
    )
    if needle not in text:
        raise RuntimeError("fast fail both insertion point not found")
    return text.replace(needle, repl, 1)


PATCHES = {
    "weak_sell_xh_block": patch_weak_sell_xh_block,
    "weak_sell_xh_gate72": patch_weak_sell_xh_gate72,
    "base_sell_score72": patch_base_sell_score72,
    "quick_exit_weak_sell_xh": patch_quick_exit_weak_sell_xh,
    "fast_fail_both": patch_fast_fail_both,
}


PRESETS = [
    Preset("control", "Current v10 default.", {}),
    Preset("global_score72", "Require B-grade or better for all engines.", {"V10_MinTradeScore": "72"}),
    Preset("global_score68", "Require at least score 68 globally.", {"V10_MinTradeScore": "68"}),
    Preset("weak_xh_block", "Block weak-regime base sells outside core sell session.", {}, ("weak_sell_xh_block",)),
    Preset("weak_xh_gate72", "Only weak out-of-core base sells must be at least B-grade.", {}, ("weak_sell_xh_gate72",)),
    Preset("base_sell_score72", "Base bearish engine must be B-grade; other engines unchanged.", {}, ("base_sell_score72",)),
    Preset("weak_xh_quick_exit", "Allow weak XH base sells but cut them if still red after 6 bars.", {}, ("quick_exit_weak_sell_xh",)),
    Preset("score68_quick", "Score floor 68 plus quick exit for weak XH sells.", {"V10_MinTradeScore": "68"}, ("quick_exit_weak_sell_xh",)),
    Preset("gate72_quick", "Weak XH gate B-grade plus quick exit.", {}, ("weak_sell_xh_gate72", "quick_exit_weak_sell_xh")),
    Preset("fast_fail_both", "Cut early trend-fail losers on both buy and sell.", {}, ("fast_fail_both",)),
    Preset(
        "open_fast_safe_sell",
        "More frequent entries but block weak outside-core base sells.",
        {
            "V10_BuyMinBreakATR": "0.08",
            "V10_WeakBuyMinBreakATR": "0.14",
            "V10_WeakSellMinBreakATR": "0.08",
            "V10_MinBodyRatio": "0.44",
            "V10_BuyMinBodyRatio": "0.50",
            "V10_WeakSellMinBodyRatio": "0.50",
            "V10_WeakBuyMinBodyRatio": "0.56",
            "V10_MaxHoldBars": "24",
            "V10_TimeCloseProfitOnly": "false",
        },
        ("weak_sell_xh_gate72", "fast_fail_both"),
    ),
]


def build_source(preset: Preset) -> Path:
    text = SOURCE.read_text()
    for name, value in preset.overrides.items():
        text = replace_named_value(text, name, value)
    for patch_name in preset.patches:
        text = PATCHES[patch_name](text)
    path = RUN_DIR / f"InvictusForward1M15_v10_{preset.name}.mq5"
    path.write_text(text)
    return path


def write_set_file(stem: str, source_text: str) -> str:
    values = []
    pattern = re.compile(r"^input\s+[A-Za-z_][A-Za-z0-9_<>]*\s+([A-Za-z_][A-Za-z0-9_]*)\s*=\s*([^;]+);", re.MULTILINE)
    for name, raw_value in pattern.findall(source_text):
        values.append(f"{name}={raw_value.strip()}")
    set_name = f"{stem}.set"
    TESTER_PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    (TESTER_PROFILE_DIR / set_name).write_text("\n".join(values) + "\n")
    return set_name


def build_ini(stem: str, from_date: str, to_date: str, set_name: str) -> str:
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
        ExpertParameters={set_name}
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


def run_backtest(stem: str, from_date: str, to_date: str, set_name: str) -> tuple[Path, Path | None]:
    ini_path = MT5_BUILD / f"{stem}.backtest.ini"
    ini_path.write_text(build_ini(stem, from_date, to_date, set_name))
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
    deadline = time.time() + 900
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

                if log_done and stable_hits >= 1:
                    break
                if stable_hits >= 3:
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


def exit_stats(report_path: Path) -> dict[str, object]:
    text = report_path.read_bytes().decode("utf-16le", errors="ignore")
    try:
        deals = parse_deals(extract_deal_rows(text))
    except Exception:
        return {"by_engine": {}, "loss_comments": []}
    exits = [d for d in deals if d["direction"] == "out"]
    by_engine: dict[str, dict[str, float]] = {}
    losses = []
    for deal in exits:
        comment = str(deal["comment"])
        parts = [p for p in comment.split("|") if p]
        engine = parts[1] if len(parts) > 1 else ""
        bucket = by_engine.setdefault(engine, {"count": 0, "pnl": 0.0, "wins": 0, "losses": 0})
        pnl = float(deal["profit"])
        bucket["count"] += 1
        bucket["pnl"] += pnl
        if pnl > 0:
            bucket["wins"] += 1
        elif pnl < 0:
            bucket["losses"] += 1
            losses.append(
                {
                    "time": deal["time"].strftime("%Y-%m-%d %H:%M:%S"),
                    "profit": pnl,
                    "comment": comment,
                }
            )
    losses.sort(key=lambda item: item["profit"])
    return {"by_engine": by_engine, "loss_comments": losses[:20]}


def score_result(metrics: dict[str, dict[str, float]]) -> float:
    week = metrics["week"]
    last_2w = metrics["last_2w"]
    ytd = metrics["2026_ytd"]
    return (
        week["net_profit"] * 2.5
        + trades_per_week(week["total_trades"], "2026.04.20", "2026.04.25") * 4.0
        + last_2w["net_profit"] * 1.2
        + trades_per_week(last_2w["total_trades"], "2026.04.10", "2026.04.25") * 2.0
        + ytd["net_profit"] * 0.35
        - max(0.0, week["equity_dd_pct"] - 20.0) * 1.2
        - max(0.0, ytd["equity_dd_pct"] - 35.0) * 0.6
    )


def main() -> None:
    results = []
    for preset in PRESETS:
        source_path = build_source(preset)
        stem = compile_variant("v10", source_path, preset.name)
        set_name = write_set_file(stem, source_path.read_text())
        metrics_by_window: dict[str, dict[str, float]] = {}
        reports: dict[str, str] = {}
        exit_breakdown: dict[str, object] = {}
        for label, from_date, to_date in WINDOWS:
            report_path, _ = run_backtest(stem, from_date, to_date, set_name)
            metrics_by_window[label] = parse_report(report_path)
            reports[label] = str(report_path)
            if label in {"week", "last_2w"}:
                exit_breakdown[label] = exit_stats(report_path)
        results.append(
            {
                "name": preset.name,
                "note": preset.note,
                "overrides": preset.overrides,
                "patches": preset.patches,
                "reports": reports,
                "metrics": metrics_by_window,
                "exit_breakdown": exit_breakdown,
                "score": score_result(metrics_by_window),
            }
        )

    results.sort(key=lambda item: item["score"], reverse=True)
    (RUN_DIR / "results.json").write_text(json.dumps(results, indent=2))

    lines = [
        "# v10 Week Live-Fix Iteration",
        "",
        "Setup: `XAUUSDc`, `M5`, `Deposit 100 USD`, `Leverage 1:100`, `Every tick`.",
        "",
        "| Rank | Preset | Week Net % | Week Trades | Week/Week | Week WR | Week EqDD | 2W Net % | 2W Trades | 2026 Net % | 2026 Trades | 2026 EqDD | Score |",
        "| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for idx, item in enumerate(results, start=1):
        week = item["metrics"]["week"]
        last_2w = item["metrics"]["last_2w"]
        ytd = item["metrics"]["2026_ytd"]
        lines.append(
            f"| {idx} | {item['name']} | {week['net_profit']:.2f}% | {week['total_trades']:.0f} | "
            f"{trades_per_week(week['total_trades'], '2026.04.20', '2026.04.25'):.2f} | "
            f"{week['win_rate']:.2f}% | {week['equity_dd_pct']:.2f}% | "
            f"{last_2w['net_profit']:.2f}% | {last_2w['total_trades']:.0f} | "
            f"{ytd['net_profit']:.2f}% | {ytd['total_trades']:.0f} | {ytd['equity_dd_pct']:.2f}% | "
            f"{item['score']:.2f} |"
        )
    (RUN_DIR / "summary.md").write_text("\n".join(lines) + "\n")
    print(RUN_DIR / "summary.md")


if __name__ == "__main__":
    main()
