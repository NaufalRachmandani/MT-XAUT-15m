#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from analyze_mt5_report import iter_rows, parse_first_number, read_report  # noqa: E402


RESEARCH = ROOT / "invictusforward-8-research"
SRC = RESEARCH / "source" / "tuned" / "InvictusForward-8-Tuned"
OUT = RESEARCH / "backtests" / "tuned_realticks_lev2000"

WINEPREFIX = Path.home() / "Library/Application Support/net.metaquotes.wine.metatrader5"
WINE = Path("/Applications/MetaTrader 5.app/Contents/SharedSupport/wine/bin/wine64")
TERMINAL = r"C:\Program Files\MetaTrader 5\terminal64.exe"
METAEDITOR = r"C:\Program Files\MetaTrader 5\metaeditor64.exe"
MT5_BUILD = WINEPREFIX / "drive_c" / "MT5Build"
REPORTS = WINEPREFIX / "drive_c" / "Program Files" / "MetaTrader 5" / "Reports"
EXPERTS = WINEPREFIX / "drive_c" / "Program Files" / "MetaTrader 5" / "MQL5" / "Experts"


@dataclass(frozen=True)
class Case:
    name: str
    symbol: str
    period: str
    from_date: str
    to_date: str
    deposit: int
    currency: str
    leverage: str = "1:2000"
    execution_mode: int = 100
    model: int = 4


CASES = [
    Case("d100_last_week", "XAUUSD", "M15", "2026.05.01", "2026.05.10", 100, "USD"),
    Case("d100_last_month", "XAUUSD", "M15", "2026.04.10", "2026.05.10", 100, "USD"),
    Case("d100_ytd_2026", "XAUUSD", "M15", "2026.01.01", "2026.05.10", 100, "USD"),
    Case("d29_last_week", "XAUUSD", "M15", "2026.05.01", "2026.05.10", 29, "USD"),
    Case("d29_ytd_2026", "XAUUSD", "M15", "2026.01.01", "2026.05.10", 29, "USD"),
]


def env() -> dict[str, str]:
    output = os.environ.copy()
    output["WINEPREFIX"] = str(WINEPREFIX)
    output["WINEDEBUG"] = "-all"
    return output


def win_build_path(filename: str) -> str:
    return rf"C:\MT5Build\{filename}"


def decode_log(path: Path) -> str:
    data = path.read_bytes()
    for encoding in ("utf-16le", "utf-8"):
        text = data.decode(encoding, errors="ignore")
        if "Result:" in text or "error" in text.lower():
            return text
    return data.decode("utf-16le", errors="ignore")


def compile_expert() -> Path:
    build_src = MT5_BUILD / "InvictusForward-8-Tuned"
    if build_src.exists():
        shutil.rmtree(build_src)
    shutil.copytree(SRC, build_src)

    log = build_src / "InvictusForward-8-Tuned.compile.log"
    subprocess.run(
        [
            str(WINE),
            METAEDITOR,
            r"/compile:C:\MT5Build\InvictusForward-8-Tuned\InvictusForward-8-Tuned.mq5",
            r"/log:C:\MT5Build\InvictusForward-8-Tuned\InvictusForward-8-Tuned.compile.log",
        ],
        env=env(),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
        timeout=120,
    )
    text = decode_log(log)
    if "0 errors" not in text:
        raise RuntimeError("compile failed; see " + str(log))

    ex5 = build_src / "InvictusForward-8-Tuned.ex5"
    if not ex5.exists():
        raise RuntimeError("compiled ex5 missing: " + str(ex5))
    OUT.mkdir(parents=True, exist_ok=True)
    shutil.copy2(log, OUT / log.name)
    shutil.copy2(ex5, SRC / ex5.name)
    return ex5


def install_expert(ex5: Path) -> None:
    target_dir = EXPERTS / "InvictusForward-8-Tuned"
    target_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ex5, target_dir / ex5.name)


def report_stem(case: Case) -> str:
    start = case.from_date.replace(".", "")
    end = case.to_date.replace(".", "")
    return (
        f"InvictusForward-8-Tuned_{case.name}_{case.symbol}_{case.period}_"
        f"d{case.deposit}_{case.currency}_lev2000_delay{case.execution_mode}_model{case.model}_{start}_{end}"
    )


def write_ini(case: Case) -> Path:
    MT5_BUILD.mkdir(parents=True, exist_ok=True)
    name = report_stem(case)
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
Expert=InvictusForward-8-Tuned\\InvictusForward-8-Tuned.ex5
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


def parse_report(path: Path, case: Case) -> dict[str, object]:
    text = read_report(path)
    profit_trades = cell(text, "Profit Trades (% of total):")
    loss_trades = cell(text, "Loss Trades (% of total):")
    return {
        "case": case.name,
        "symbol": case.symbol,
        "period": case.period,
        "from": case.from_date,
        "to": case.to_date,
        "deposit": case.deposit,
        "currency": case.currency,
        "leverage": cell(text, "Leverage:", case.leverage),
        "model": case.model,
        "execution_mode_ms": case.execution_mode,
        "history_quality": cell(text, "History Quality:"),
        "bars": int(parse_first_number(cell(text, "Bars:"))),
        "ticks": int(parse_first_number(cell(text, "Ticks:"))),
        "net": parse_first_number(cell(text, "Total Net Profit:")),
        "gross_profit": parse_first_number(cell(text, "Gross Profit:")),
        "gross_loss": parse_first_number(cell(text, "Gross Loss:")),
        "profit_factor": parse_first_number(cell(text, "Profit Factor:")),
        "expected_payoff": parse_first_number(cell(text, "Expected Payoff:")),
        "trades": int(parse_first_number(cell(text, "Total Trades:"))),
        "profit_trades": int(parse_first_number(profit_trades)),
        "loss_trades": int(parse_first_number(loss_trades)),
        "win_rate_pct": pct_in(profit_trades),
        "equity_dd": cell(text, "Equity Drawdown Maximal:"),
        "balance_dd": cell(text, "Balance Drawdown Maximal:"),
        "largest_loss": parse_first_number(cell(text, "Largest loss trade:")),
        "avg_loss": parse_first_number(cell(text, "Average loss trade:")),
        "max_consecutive_losses": cell(text, "Maximum consecutive losses ($):"),
        "report": str(OUT / f"{report_stem(case)}.htm"),
        "ini": str(OUT / f"{report_stem(case)}.ini"),
    }


def run_case(case: Case, timeout: int) -> dict[str, object]:
    name = report_stem(case)
    report = REPORTS / f"{name}.htm"
    for old in REPORTS.glob(f"{name}*"):
        if old.is_file():
            old.unlink()
    ini = write_ini(case)
    subprocess.run(
        [str(WINE), TERMINAL, f"/config:{win_build_path(ini.name)}"],
        env=env(),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
        timeout=timeout,
    )
    for _ in range(240):
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
    return parse_report(report, case)


def write_outputs(results: list[dict[str, object]]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "results.json").write_text(json.dumps(results, indent=2) + "\n")
    lines = [
        "# InvictusForward-8 Tuned Backtests",
        "",
        "All rows use `Model=4` / every tick based on real ticks and `Leverage=1:2000`.",
        "",
        "| Case | Deposit | Window | Net | PF | Trades | WR | Eq DD | Largest Loss | History |",
        "| --- | ---: | --- | ---: | ---: | ---: | ---: | --- | ---: | --- |",
    ]
    for row in results:
        lines.append(
            "| {case} | {deposit} {currency} | {from} to {to} | {net:.2f} | {profit_factor:.2f} | {trades} | {win_rate_pct:.2f}% | {equity_dd} | {largest_loss:.2f} | {history_quality} |".format(
                **row
            )
        )
    (OUT / "SUMMARY.md").write_text("\n".join(lines) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", nargs="*", help="case names to run")
    parser.add_argument("--timeout", type=int, default=1200)
    args = parser.parse_args()

    ex5 = compile_expert()
    install_expert(ex5)
    selected = [c for c in CASES if not args.cases or c.name in set(args.cases)]
    results: list[dict[str, object]] = []
    for case in selected:
        print(f"run {case.name}", flush=True)
        result = run_case(case, args.timeout)
        print(
            f"done {case.name} net={result['net']:.2f} pf={result['profit_factor']:.2f} "
            f"trades={result['trades']} history={result['history_quality']}",
            flush=True,
        )
        results.append(result)
        write_outputs(results)


if __name__ == "__main__":
    main()
