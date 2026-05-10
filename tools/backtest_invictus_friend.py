#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path

from analyze_mt5_report import iter_rows, parse_first_number, read_report


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "build" / "invictus_friend_backtest" / "src"
OUT = ROOT / "build" / "invictus_friend_backtest"

WINEPREFIX = Path.home() / "Library/Application Support/net.metaquotes.wine.metatrader5"
WINE = Path("/Applications/MetaTrader 5.app/Contents/SharedSupport/wine/bin/wine64")
TERMINAL = r"C:\Program Files\MetaTrader 5\terminal64.exe"
MT5_BUILD = WINEPREFIX / "drive_c" / "MT5Build"
REPORTS = WINEPREFIX / "drive_c" / "Program Files" / "MetaTrader 5" / "Reports"
EXPERTS = WINEPREFIX / "drive_c" / "Program Files" / "MetaTrader 5" / "MQL5" / "Experts"


@dataclass(frozen=True)
class Expert:
    name: str
    folder: str
    ex5: Path


@dataclass(frozen=True)
class Case:
    name: str
    symbol: str
    period: str
    from_date: str
    to_date: str
    deposit: int
    currency: str
    leverage: str
    execution_mode: int
    model: int = 4


EXPERT_LIST = [
    Expert(
        "InvictusForward-8",
        "InvictusForward-8",
        SRC / "InvictusForward-8" / "InvictusForward-8.ex5",
    ),
    Expert(
        "InvictusBest-V140",
        "InvictusBest-V140",
        SRC / "InvictusBest-V140" / "InvictusBest-V140.ex5",
    ),
]

CASES = [
    Case("friend_2025_to_20260430", "XAUUSDc", "M15", "2025.01.01", "2026.04.30", 1000, "USC", "1:100", 100),
    Case("friend_ytd_2026", "XAUUSDc", "M15", "2026.01.01", "2026.05.09", 1000, "USC", "1:100", 100),
    Case("friend_lastweek_20260501", "XAUUSDc", "M15", "2026.05.01", "2026.05.09", 1000, "USC", "1:100", 100),
    Case("pro_ytd_2026_d29", "XAUUSD", "M15", "2026.01.01", "2026.05.09", 29, "USD", "1:2000", 50),
    Case("pro_lastweek_20260501_d29", "XAUUSD", "M15", "2026.05.01", "2026.05.09", 29, "USD", "1:2000", 50),
]


def env() -> dict[str, str]:
    output = os.environ.copy()
    output["WINEPREFIX"] = str(WINEPREFIX)
    output["WINEDEBUG"] = "-all"
    return output


def win_build_path(filename: str) -> str:
    return rf"C:\MT5Build\{filename}"


def copy_experts() -> None:
    for expert in EXPERT_LIST:
        if not expert.ex5.exists():
            raise RuntimeError(f"missing {expert.ex5}")
        target_dir = EXPERTS / expert.folder
        target_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(expert.ex5, target_dir / expert.ex5.name)


def report_stem(expert: Expert, case: Case) -> str:
    start = case.from_date.replace(".", "")
    end = case.to_date.replace(".", "")
    return (
        f"{expert.name}_{case.name}_{case.symbol}_{case.period}_"
        f"d{case.deposit}_{case.currency}_delay{case.execution_mode}_model{case.model}_{start}_{end}"
    )


def write_ini(expert: Expert, case: Case) -> Path:
    MT5_BUILD.mkdir(parents=True, exist_ok=True)
    name = report_stem(expert, case)
    config = f"""[Common]
Login=265874264
Server=Exness-MT5Real38
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
Expert={expert.folder}\\{expert.ex5.name}
Symbol={case.symbol}
Period={case.period}
Login=265874264
Model={case.model}
ExecutionMode={case.execution_mode}
Optimization=0
FromDate={case.from_date}
ToDate={case.to_date}
ForwardMode=0
Report=\\Reports\\{name}
ReplaceReport=1
ShutdownTerminal=1
Deposit={case.deposit}
Currency={case.currency}
Leverage={case.leverage}
UseLocal=1
UseRemote=0
UseCloud=0
Visual=0
"""
    path = MT5_BUILD / f"{name}.ini"
    path.write_bytes(b"\xff\xfe" + config.encode("utf-16le"))
    return path


def cell(text: str, label: str, default: str = "") -> str:
    for row in iter_rows(text):
        for index, value in enumerate(row[:-1]):
            if value == label:
                return row[index + 1]
    return default


def pct_in(value: str) -> float:
    import re

    match = re.search(r"\(([-\d.]+)%\)", value)
    return float(match.group(1)) if match else 0.0


def parse_report(path: Path, expert: Expert, case: Case) -> dict[str, object]:
    text = read_report(path)
    profit_trades = cell(text, "Profit Trades (% of total):")
    loss_trades = cell(text, "Loss Trades (% of total):")
    eqdd = cell(text, "Equity Drawdown Maximal:")
    return {
        "expert": expert.name,
        "case": case.name,
        "symbol": case.symbol,
        "period": case.period,
        "from": case.from_date,
        "to": case.to_date,
        "deposit": case.deposit,
        "currency": case.currency,
        "leverage": cell(text, "Leverage:", case.leverage),
        "model": case.model,
        "delay_ms": case.execution_mode,
        "history_quality": cell(text, "History Quality:"),
        "net": parse_first_number(cell(text, "Total Net Profit:")),
        "pf": parse_first_number(cell(text, "Profit Factor:")),
        "trades": int(parse_first_number(cell(text, "Total Trades:"))),
        "wins": int(parse_first_number(profit_trades)),
        "losses": int(parse_first_number(loss_trades)),
        "win_rate": pct_in(profit_trades),
        "eqdd": eqdd,
        "largest_loss": parse_first_number(cell(text, "Largest loss trade:")),
        "avg_loss": parse_first_number(cell(text, "Average loss trade:")),
        "report": str(OUT / f"{report_stem(expert, case)}.htm"),
    }


def run_case(expert: Expert, case: Case, timeout: int) -> dict[str, object]:
    name = report_stem(expert, case)
    report = REPORTS / f"{name}.htm"
    for old in REPORTS.glob(f"{name}*"):
        if old.is_file():
            old.unlink()
    ini = write_ini(expert, case)
    subprocess.run(
        [str(WINE), TERMINAL, f"/config:{win_build_path(ini.name)}"],
        env=env(),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
        timeout=timeout,
    )
    for _ in range(180):
        if report.exists() and report.stat().st_size > 0:
            break
        time.sleep(1)
    if not report.exists() or report.stat().st_size == 0:
        raise RuntimeError(f"report missing: {report}")
    OUT.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ini, OUT / ini.name)
    for artifact in REPORTS.glob(f"{name}*"):
        if artifact.is_file():
            shutil.copy2(artifact, OUT / artifact.name)
    return parse_report(report, expert, case)


def write_outputs(results: list[dict[str, object]]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "results.json").write_text(json.dumps(results, indent=2) + "\n")
    lines = [
        "# Invictus Friend Backtests",
        "",
        "All rows use `Model=4` / every tick based on real ticks.",
        "",
        "| Expert | Case | Symbol | Deposit | Delay | Net | PF | Trades | WR | Eq DD | History |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    for row in results:
        lines.append(
            "| {expert} | {case} | {symbol} | {deposit} {currency} | {delay_ms}ms | {net:.2f} | {pf:.2f} | {trades} | {win_rate:.2f}% | {eqdd} | {history_quality} |".format(
                **row
            )
        )
    (OUT / "SUMMARY.md").write_text("\n".join(lines) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--experts", nargs="*", help="expert names to run")
    parser.add_argument("--cases", nargs="*", help="case names to run")
    parser.add_argument("--timeout", type=int, default=1200)
    args = parser.parse_args()

    copy_experts()
    experts = [e for e in EXPERT_LIST if not args.experts or e.name in set(args.experts)]
    cases = [c for c in CASES if not args.cases or c.name in set(args.cases)]
    results: list[dict[str, object]] = []
    for expert in experts:
        for case in cases:
            print(f"run {expert.name} {case.name}", flush=True)
            result = run_case(expert, case, args.timeout)
            print(
                f"done {expert.name} {case.name} net={result['net']:.2f} pf={result['pf']:.2f} trades={result['trades']} history={result['history_quality']}",
                flush=True,
            )
            results.append(result)
            write_outputs(results)
    print(OUT / "SUMMARY.md")


if __name__ == "__main__":
    main()
