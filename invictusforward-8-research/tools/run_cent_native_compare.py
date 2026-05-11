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
OUT = RESEARCH / "backtests" / "cent_native_2026_lev2000_compare"

WINEPREFIX = Path.home() / "Library/Application Support/net.metaquotes.wine.metatrader5"
WINE = Path("/Applications/MetaTrader 5.app/Contents/SharedSupport/wine/bin/wine64")
TERMINAL = r"C:\Program Files\MetaTrader 5\terminal64.exe"
METAEDITOR = r"C:\Program Files\MetaTrader 5\metaeditor64.exe"
MT5_BUILD = WINEPREFIX / "drive_c" / "MT5Build"
REPORTS = WINEPREFIX / "drive_c" / "Program Files" / "MetaTrader 5" / "Reports"
EXPERTS = WINEPREFIX / "drive_c" / "Program Files" / "MetaTrader 5" / "MQL5" / "Experts"

LOGIN = "184000633"
SERVER = "Exness-MT5Real25"
SYMBOL = "XAUUSDc"
PERIOD = "M15"
CURRENCY = "USC"
LEVERAGE = "1:2000"
MODEL = 4
EXECUTION_MODE_MS = 100


@dataclass(frozen=True)
class ExpertSpec:
    key: str
    label: str
    source_dir: Path
    source_file: str
    install_folder: str
    ex5_file: str


@dataclass(frozen=True)
class WindowSpec:
    key: str
    label: str
    from_date: str
    to_date: str


@dataclass(frozen=True)
class CaseSpec:
    expert: ExpertSpec
    window: WindowSpec
    deposit: int


EXPERTS_TO_RUN = [
    ExpertSpec(
        key="base",
        label="Base",
        source_dir=RESEARCH / "source" / "original" / "InvictusForward-8",
        source_file="InvictusForward-8.mq5",
        install_folder="InvictusForward-8-CentBase",
        ex5_file="InvictusForward-8.ex5",
    ),
    ExpertSpec(
        key="tuned",
        label="Tuned",
        source_dir=RESEARCH / "source" / "tuned" / "InvictusForward-8-Tuned",
        source_file="InvictusForward-8-Tuned.mq5",
        install_folder="InvictusForward-8-CentTuned",
        ex5_file="InvictusForward-8-Tuned.ex5",
    ),
]

WINDOWS = [
    WindowSpec("ytd_2026", "2026 YTD", "2026.01.01", "2026.05.10"),
    WindowSpec("last_month", "Last Month", "2026.04.10", "2026.05.10"),
    WindowSpec("last_week", "Last Week", "2026.05.01", "2026.05.10"),
]

DEPOSITS = [1000, 20000]


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


def compile_expert(expert: ExpertSpec) -> Path:
    if not expert.source_dir.exists():
        raise RuntimeError(f"source folder missing: {expert.source_dir}")

    build_dir = MT5_BUILD / expert.install_folder
    if build_dir.exists():
        shutil.rmtree(build_dir)
    shutil.copytree(expert.source_dir, build_dir)

    log = build_dir / f"{expert.install_folder}.compile.log"
    source = rf"C:\MT5Build\{expert.install_folder}\{expert.source_file}"
    log_win = rf"C:\MT5Build\{expert.install_folder}\{log.name}"
    subprocess.run(
        [str(WINE), METAEDITOR, f"/compile:{source}", f"/log:{log_win}"],
        env=env(),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
        timeout=180,
    )
    text = decode_log(log)
    OUT.mkdir(parents=True, exist_ok=True)
    shutil.copy2(log, OUT / log.name)
    if "0 errors" not in text:
        raise RuntimeError(f"{expert.label} compile failed; see {log}")

    ex5 = build_dir / expert.ex5_file
    if not ex5.exists():
        raise RuntimeError(f"compiled ex5 missing: {ex5}")

    target_dir = EXPERTS / expert.install_folder
    target_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ex5, target_dir / expert.ex5_file)
    shutil.copy2(ex5, OUT / f"{expert.install_folder}_{expert.ex5_file}")
    return ex5


def report_stem(case: CaseSpec) -> str:
    start = case.window.from_date.replace(".", "")
    end = case.window.to_date.replace(".", "")
    return (
        f"Forward8Cent_{case.expert.key}_{case.window.key}_d{case.deposit}USC_"
        f"{SYMBOL}_{PERIOD}_lev2000_delay{EXECUTION_MODE_MS}_model{MODEL}_{start}_{end}"
    )


def write_ini(case: CaseSpec) -> Path:
    MT5_BUILD.mkdir(parents=True, exist_ok=True)
    name = report_stem(case)
    config = f"""[Common]
Login={LOGIN}
Server={SERVER}
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
Expert={case.expert.install_folder}\\{case.expert.ex5_file}
Symbol={SYMBOL}
Period={PERIOD}
Login={LOGIN}
Model={MODEL}
ExecutionMode={EXECUTION_MODE_MS}
Optimization=0
FromDate={case.window.from_date}
ToDate={case.window.to_date}
ForwardMode=0
Report=\\Reports\\{name}
ReplaceReport=1
ShutdownTerminal=1
Deposit={case.deposit}
Currency={CURRENCY}
Leverage={LEVERAGE}
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


def read_ini_settings(path: Path) -> dict[str, str]:
    text = path.read_bytes().decode("utf-16le", errors="ignore").lstrip("\ufeff")
    settings: dict[str, str] = {}
    for line in text.splitlines():
        if "=" not in line or line.lstrip().startswith(";"):
            continue
        key, value = line.split("=", 1)
        settings[key.strip()] = value.strip()
    return settings


def parse_report(report: Path, case: CaseSpec) -> dict[str, object]:
    text = read_report(report)
    profit_trades = cell(text, "Profit Trades (% of total):")
    loss_trades = cell(text, "Loss Trades (% of total):")
    row = {
        "expert_key": case.expert.key,
        "expert": case.expert.label,
        "window_key": case.window.key,
        "window": case.window.label,
        "from": case.window.from_date,
        "to": case.window.to_date,
        "deposit": case.deposit,
        "currency": cell(text, "Currency:", ""),
        "initial_deposit": parse_first_number(cell(text, "Initial Deposit:")),
        "account": LOGIN,
        "server": SERVER,
        "symbol": cell(text, "Symbol:", SYMBOL),
        "period": PERIOD,
        "period_report": cell(text, "Period:", ""),
        "leverage": cell(text, "Leverage:", LEVERAGE),
        "model": MODEL,
        "execution_mode_ms": EXECUTION_MODE_MS,
        "optimization": 0,
        "use_local": 1,
        "use_remote": 0,
        "use_cloud": 0,
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
    return row


def validate_result(row: dict[str, object]) -> list[str]:
    issues: list[str] = []
    settings = row.get("ini_settings", {})
    if row["symbol"] != SYMBOL:
        issues.append(f"symbol={row['symbol']}")
    if row["leverage"] != LEVERAGE:
        issues.append(f"leverage={row['leverage']}")
    if row["history_quality"] != "100% real ticks":
        issues.append(f"history={row['history_quality']}")
    if row["currency"] != CURRENCY:
        issues.append(f"currency={row['currency']}")
    if abs(float(row["initial_deposit"]) - float(row["deposit"])) > 0.01:
        issues.append(f"initial_deposit={row['initial_deposit']}")
    expected_ini = {
        "Symbol": SYMBOL,
        "Period": PERIOD,
        "Model": str(MODEL),
        "ExecutionMode": str(EXECUTION_MODE_MS),
        "Optimization": "0",
        "Deposit": str(row["deposit"]),
        "Currency": CURRENCY,
        "Leverage": LEVERAGE,
        "UseLocal": "1",
        "UseRemote": "0",
        "UseCloud": "0",
    }
    if isinstance(settings, dict):
        for key, expected in expected_ini.items():
            actual = settings.get(key)
            if actual != expected:
                issues.append(f"ini_{key}={actual}")
    else:
        issues.append("ini_settings=missing")
    return issues


def run_case(case: CaseSpec, timeout: int) -> dict[str, object]:
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
    for _ in range(300):
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

    row = parse_report(report, case)
    row["ini_settings"] = read_ini_settings(ini)
    row["validation_issues"] = validate_result(row)
    return row


def risk_flag(row: dict[str, object]) -> str:
    dd = str(row["equity_dd"])
    try:
        pct = float(dd.split("(")[1].split("%")[0])
    except Exception:
        return "CHECK"
    if pct >= 70:
        return "EXTREME_DD"
    if pct >= 40:
        return "HIGH_DD"
    return "OK"


def build_comparisons(results: list[dict[str, object]]) -> list[dict[str, object]]:
    by_key: dict[tuple[int, str], dict[str, dict[str, object]]] = {}
    for row in results:
        key = (int(row["deposit"]), str(row["window_key"]))
        by_key.setdefault(key, {})[str(row["expert_key"])] = row

    comparisons: list[dict[str, object]] = []
    for key in sorted(by_key, key=lambda item: (item[0], WINDOWS.index(next(w for w in WINDOWS if w.key == item[1])))):
        pair = by_key[key]
        if "base" not in pair or "tuned" not in pair:
            continue
        base = pair["base"]
        tuned = pair["tuned"]
        base_net = float(base["net"])
        tuned_net = float(tuned["net"])
        base_pf = float(base["profit_factor"])
        tuned_pf = float(tuned["profit_factor"])
        if tuned_net > base_net and tuned_pf >= base_pf:
            winner = "Tuned"
        elif base_net > tuned_net and base_pf >= tuned_pf:
            winner = "Base"
        elif tuned_net > base_net:
            winner = "Tuned net, mixed"
        elif base_net > tuned_net:
            winner = "Base net, mixed"
        else:
            winner = "Tie"
        comparisons.append(
            {
                "deposit": key[0],
                "window_key": key[1],
                "window": str(base["window"]),
                "base_net": base_net,
                "base_pf": base_pf,
                "base_trades": int(base["trades"]),
                "base_eqdd": str(base["equity_dd"]),
                "base_risk": risk_flag(base),
                "tuned_net": tuned_net,
                "tuned_pf": tuned_pf,
                "tuned_trades": int(tuned["trades"]),
                "tuned_eqdd": str(tuned["equity_dd"]),
                "tuned_risk": risk_flag(tuned),
                "winner": winner,
                "live_note": (
                    "Not live-ready: tuned improves net/PF but drawdown remains high"
                    if str(winner).startswith("Tuned") and risk_flag(tuned) != "OK"
                    else ""
                ),
            }
        )
    return comparisons


def write_outputs(results: list[dict[str, object]]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    comparisons = build_comparisons(results)
    (OUT / "results.json").write_text(json.dumps(results, indent=2) + "\n")
    (OUT / "comparison.json").write_text(json.dumps(comparisons, indent=2) + "\n")

    lines = [
        "# Forward-8 Cent Native MT5 Compare",
        "",
        "Source of truth: native MT5 Strategy Tester `.htm` reports generated through `terminal64.exe /config`.",
        "",
        f"Setup: account `{LOGIN}` on `{SERVER}`, `{SYMBOL}` `{PERIOD}`, currency `{CURRENCY}`, leverage `{LEVERAGE}`, `Model={MODEL}`, `ExecutionMode={EXECUTION_MODE_MS}`, `UseLocal=1`, `UseRemote=0`, `UseCloud=0`.",
        "",
        "All windows are 2026+ only. No 2025 result is used for tuning decisions.",
        "",
        "## All Runs",
        "",
        "| Expert | Deposit | Window | Net | PF | Trades | WR | Eq DD | Balance DD | Largest Loss | History | Validation |",
        "| --- | ---: | --- | ---: | ---: | ---: | ---: | --- | --- | ---: | --- | --- |",
    ]
    window_order = {window.key: index for index, window in enumerate(WINDOWS)}
    expert_order = {expert.key: index for index, expert in enumerate(EXPERTS_TO_RUN)}
    for row in sorted(
        results,
        key=lambda r: (
            int(r["deposit"]),
            window_order.get(str(r["window_key"]), 99),
            expert_order.get(str(r["expert_key"]), 99),
        ),
    ):
        validation = ", ".join(row["validation_issues"]) if row["validation_issues"] else "OK"
        lines.append(
            "| {expert} | {deposit} {currency} | {window} | {net:.2f} | {profit_factor:.2f} | {trades} | {win_rate_pct:.2f}% | {equity_dd} | {balance_dd} | {largest_loss:.2f} | {history_quality} | {validation} |".format(
                validation=validation,
                **row,
            )
        )

    lines.extend(
        [
            "",
            "## Base vs Tuned",
            "",
            "| Deposit | Window | Base Net/PF/DD | Tuned Net/PF/DD | Winner | Note |",
            "| ---: | --- | --- | --- | --- | --- |",
        ]
    )
    for row in comparisons:
        lines.append(
            "| {deposit} USC | {window} | {base_net:.2f} / {base_pf:.2f} / {base_eqdd} | {tuned_net:.2f} / {tuned_pf:.2f} / {tuned_eqdd} | {winner} | {live_note} |".format(
                **row
            )
        )

    thousand_rows = [row for row in comparisons if int(row["deposit"]) == 1000]
    if any(row["tuned_risk"] != "OK" for row in thousand_rows):
        recommendation = "Tuned at 1000 USC still shows high/extreme drawdown in at least one 2026 window; treat it as research-only unless a micro-risk cent profile reduces exposure."
    else:
        recommendation = "Tuned at 1000 USC passes the configured drawdown screen, but the YTD drawdown is still aggressive; use it as the next cent baseline, not as a conservative live profile."

    lines.extend(["", "## Recommendation", "", recommendation])
    (OUT / "SUMMARY.md").write_text("\n".join(lines) + "\n")


def all_cases() -> list[CaseSpec]:
    return [
        CaseSpec(expert=expert, window=window, deposit=deposit)
        for deposit in DEPOSITS
        for window in WINDOWS
        for expert in EXPERTS_TO_RUN
    ]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", nargs="*", help="optional case keys like base:ytd_2026:1000")
    parser.add_argument("--timeout", type=int, default=1800)
    args = parser.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    for expert in EXPERTS_TO_RUN:
        print(f"compile {expert.label}", flush=True)
        compile_expert(expert)

    cases = all_cases()
    if args.cases:
        requested = set(args.cases)
        cases = [c for c in cases if f"{c.expert.key}:{c.window.key}:{c.deposit}" in requested]

    results: list[dict[str, object]] = []
    for case in cases:
        print(f"run {case.expert.label} {case.window.key} d{case.deposit}", flush=True)
        row = run_case(case, args.timeout)
        issues = ",".join(row["validation_issues"]) if row["validation_issues"] else "OK"
        print(
            f"done {case.expert.label} {case.window.key} d{case.deposit} "
            f"net={row['net']:.2f} pf={row['profit_factor']:.2f} trades={row['trades']} validation={issues}",
            flush=True,
        )
        results.append(row)
        write_outputs(results)


if __name__ == "__main__":
    main()
