#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path

from analyze_mt5_report import iter_rows, parse_first_number, parse_report_metrics, read_report


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "build" / "acane_v2_delay_backtest"

WINEPREFIX = Path.home() / "Library/Application Support/net.metaquotes.wine.metatrader5"
WINE = Path("/Applications/MetaTrader 5.app/Contents/SharedSupport/wine/bin/wine64")
TERMINAL = r"C:\Program Files\MetaTrader 5\terminal64.exe"
MT5_BUILD = WINEPREFIX / "drive_c" / "MT5Build"
REPORTS = WINEPREFIX / "drive_c" / "Program Files" / "MetaTrader 5" / "Reports"


@dataclass(frozen=True)
class Case:
    name: str
    from_date: str
    to_date: str
    execution_mode: int
    deposit: int = 29
    leverage: str = "1:2000"
    model: int = 4


def env() -> dict[str, str]:
    output = os.environ.copy()
    output["WINEPREFIX"] = str(WINEPREFIX)
    output["WINEDEBUG"] = "-all"
    return output


def win_build_path(filename: str) -> str:
    return rf"C:\MT5Build\{filename}"


def write_tester_ini(case: Case) -> Path:
    MT5_BUILD.mkdir(parents=True, exist_ok=True)
    report_name = report_stem(case)
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
Expert=Acane\\AcaneM1_v2.ex5
Symbol=XAUUSD
Period=M1
Login=265874264
Model={case.model}
ExecutionMode={case.execution_mode}
Optimization=0
FromDate={case.from_date}
ToDate={case.to_date}
ForwardMode=0
Report=\\Reports\\{report_name}
ReplaceReport=1
ShutdownTerminal=1
Deposit={case.deposit}
Currency=USD
Leverage={case.leverage}
UseLocal=1
UseRemote=0
UseCloud=0
Visual=0
"""
    ini = MT5_BUILD / f"{report_name}.ini"
    ini.write_bytes(b"\xff\xfe" + config.encode("utf-16le"))
    return ini


def report_stem(case: Case) -> str:
    start = case.from_date.replace(".", "")
    end = case.to_date.replace(".", "")
    delay = f"delay{case.execution_mode}ms" if case.execution_mode > 0 else "delay0"
    return f"AcaneM1_v2_{case.name}_d{case.deposit}_{delay}_real_ticks_{start}_{end}"


def dd_percent(value: str) -> float:
    match = re.search(r"\(([-\d.]+)%\)", value)
    return float(match.group(1)) if match else 0.0


def value_for_label(text: str, label: str, default: str = "") -> str:
    for row in iter_rows(text):
        for index, cell in enumerate(row[:-1]):
            if cell == label:
                return row[index + 1]
    return default


def percent_inside(value: str) -> float:
    match = re.search(r"\(([-\d.]+)%\)", value)
    return float(match.group(1)) if match else 0.0


def parse_report(report: Path, case: Case) -> dict[str, object]:
    text = read_report(report)
    metrics = parse_report_metrics(text)
    net = parse_first_number(value_for_label(text, "Total Net Profit:"))
    trades = int(parse_first_number(value_for_label(text, "Total Trades:")))
    profit_trades = value_for_label(text, "Profit Trades (% of total):")
    loss_trades = value_for_label(text, "Loss Trades (% of total):")
    equity_dd = value_for_label(text, "Equity Drawdown Maximal:")
    balance_dd = value_for_label(text, "Balance Drawdown Maximal:")
    return {
        "case": case.name,
        "from": case.from_date,
        "to": case.to_date,
        "deposit": case.deposit,
        "leverage": value_for_label(text, "Leverage:", case.leverage),
        "model": case.model,
        "execution_mode_ms": case.execution_mode,
        "history_quality": value_for_label(text, "History Quality:"),
        "bars": int(parse_first_number(value_for_label(text, "Bars:"))),
        "ticks": int(parse_first_number(value_for_label(text, "Ticks:"))),
        "net": net,
        "gross_profit": parse_first_number(value_for_label(text, "Gross Profit:")),
        "gross_loss": parse_first_number(value_for_label(text, "Gross Loss:")),
        "profit_factor": parse_first_number(value_for_label(text, "Profit Factor:")),
        "expected_payoff": parse_first_number(value_for_label(text, "Expected Payoff:")),
        "trades": trades,
        "profit_trades": int(parse_first_number(profit_trades)),
        "loss_trades": int(parse_first_number(loss_trades)),
        "win_rate_pct": percent_inside(profit_trades),
        "loss_rate_pct": percent_inside(loss_trades),
        "equity_dd": equity_dd,
        "equity_dd_pct": dd_percent(equity_dd),
        "balance_dd": balance_dd,
        "balance_dd_pct": dd_percent(balance_dd),
        "largest_loss": parse_first_number(value_for_label(text, "Largest loss trade:")),
        "avg_loss": parse_first_number(value_for_label(text, "Average loss trade:")),
        "max_consecutive_losses": value_for_label(text, "Maximum consecutive losses ($):"),
        "report": str(OUT / f"{report_stem(case)}.htm"),
    }


def run_case(case: Case, timeout: int = 1200) -> dict[str, object]:
    OUT.mkdir(parents=True, exist_ok=True)
    report_name = report_stem(case)
    report = REPORTS / f"{report_name}.htm"
    for existing in REPORTS.glob(f"{report_name}*"):
        if existing.is_file():
            existing.unlink()
    ini = write_tester_ini(case)
    subprocess.run(
        [str(WINE), TERMINAL, f"/config:{win_build_path(ini.name)}"],
        env=env(),
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        timeout=timeout,
    )
    for _ in range(180):
        if report.exists() and report.stat().st_size > 0:
            break
        time.sleep(1)
    if not report.exists() or report.stat().st_size == 0:
        raise RuntimeError(f"report missing: {report}")
    shutil.copy2(ini, OUT / ini.name)
    for artifact in REPORTS.glob(f"{report_name}*"):
        if artifact.is_file():
            shutil.copy2(artifact, OUT / artifact.name)
    return parse_report(report, case)


def write_summary(results: list[dict[str, object]]) -> None:
    rows = sorted(results, key=lambda row: (str(row["case"]), int(row["execution_mode_ms"])))
    lines = [
        "# AcaneM1 v2 delay backtest",
        "",
        "Setup: `XAUUSD`, `M1`, account `265874264` on `Exness-MT5Real38`, deposit `$29`, leverage `1:2000`, `Model=4` real ticks.",
        "",
        "| Window | Delay | Net | PF | Trades | Win rate | Eq DD | History |",
        "| --- | ---: | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| {case} | {execution_mode_ms}ms | {net:.2f} | {profit_factor:.2f} | {trades} | {win_rate_pct:.2f}% | {equity_dd} | {history_quality} |".format(
                **row
            )
        )
    lines.extend(["", "Raw results are in `delay_results.json`."])
    (OUT / "SUMMARY.md").write_text("\n".join(lines) + "\n")
    (OUT / "delay_results.json").write_text(json.dumps(results, indent=2) + "\n")


def main() -> None:
    cases = [
        Case("friday_20260508", "2026.05.08", "2026.05.09", 100),
        Case("recent_20260501", "2026.05.01", "2026.05.09", 100),
        Case("ytd_2026", "2026.01.01", "2026.05.09", 100),
        Case("current_2025", "2025.01.01", "2026.05.09", 100),
        Case("recent_20260501_stress", "2026.05.01", "2026.05.09", 200),
        Case("ytd_2026_stress", "2026.01.01", "2026.05.09", 200),
        Case("recent_20260501_d100", "2026.05.01", "2026.05.09", 100, deposit=100),
        Case("ytd_2026_d100", "2026.01.01", "2026.05.09", 100, deposit=100),
    ]
    results = []
    for case in cases:
        print(f"running {case.name} execution={case.execution_mode}ms model={case.model}", flush=True)
        result = run_case(case)
        print(
            f"done {case.name} execution={case.execution_mode}ms net={result['net']:.2f} pf={result['profit_factor']:.2f} trades={result['trades']}",
            flush=True,
        )
        results.append(result)
    write_summary(results)
    print(OUT / "SUMMARY.md")


if __name__ == "__main__":
    main()
