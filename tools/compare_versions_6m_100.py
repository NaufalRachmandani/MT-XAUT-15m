#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import shutil
import subprocess
import textwrap
import time
from dataclasses import dataclass, asdict
from pathlib import Path


ROOT = Path("/Users/naufalrachmandani/Hobby/MT5 XAU 15m")

WINEPREFIX = Path("/Users/naufalrachmandani/Library/Application Support/net.metaquotes.wine.metatrader5")
MT5_BUILD = WINEPREFIX / "drive_c" / "MT5Build"
MT5_EXPERTS = WINEPREFIX / "drive_c" / "Program Files" / "MetaTrader 5" / "MQL5" / "Experts" / "Invictus"
REPORTS_DIR = WINEPREFIX / "drive_c" / "Program Files" / "MetaTrader 5" / "Reports"
TESTER_LOG_DIR = WINEPREFIX / "drive_c" / "Program Files" / "MetaTrader 5" / "Tester" / "logs"
WINE = "/Applications/MetaTrader 5.app/Contents/SharedSupport/wine/bin/wine64"
METAEDITOR_EXE = r"C:\Program Files\MetaTrader 5\metaeditor64.exe"
TERMINAL_EXE = r"C:\Program Files\MetaTrader 5\terminal64.exe"

VERSIONS = ["base", "v1", "v2", "v3", "v4", "v5"]


@dataclass
class VersionResult:
    version: str
    report_path: str
    tester_log: str
    net_profit: float
    profit_factor: float
    expected_payoff: float
    total_trades: int
    win_rate: float
    balance_dd_abs: float
    balance_dd_pct: float
    equity_dd_abs: float
    equity_dd_pct: float


def run_subprocess(args: list[str], quiet: bool = True) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["WINEPREFIX"] = str(WINEPREFIX)
    env["WINEDEBUG"] = "-all"
    kwargs = {"cwd": ROOT, "env": env, "text": True, "check": False}
    if quiet:
        kwargs["stdout"] = subprocess.DEVNULL
        kwargs["stderr"] = subprocess.DEVNULL
    else:
        kwargs["stdout"] = subprocess.PIPE
        kwargs["stderr"] = subprocess.STDOUT
    return subprocess.run(args, **kwargs)


def launch_subprocess(args: list[str]) -> subprocess.Popen[str]:
    env = os.environ.copy()
    env["WINEPREFIX"] = str(WINEPREFIX)
    env["WINEDEBUG"] = "-all"
    return subprocess.Popen(
        args,
        cwd=ROOT,
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        text=True,
    )


def latest_tester_log() -> Path | None:
    logs = sorted(TESTER_LOG_DIR.glob("*.log"), key=lambda p: p.stat().st_mtime)
    return logs[-1] if logs else None


def compile_variant(version: str, source_file: Path, label: str) -> str:
    stem = f"InvictusForward1M15_{version}_{label}"
    build_source = MT5_BUILD / f"{stem}.mq5"
    compile_log = MT5_BUILD / f"{stem}.compile.log"
    build_source.write_text(source_file.read_text())
    run_subprocess([WINE, METAEDITOR_EXE, f"/compile:C:\\MT5Build\\{stem}.mq5", f"/log:C:\\MT5Build\\{stem}.compile.log"])
    log_text = compile_log.read_bytes().decode("utf-16le", errors="ignore")
    if "0 errors" not in log_text:
        raise RuntimeError(f"Compilation failed for {version}: {log_text[-600:]}")
    return stem


def build_ini(stem: str, from_date: str, to_date: str, deposit: int, leverage: str) -> str:
    report_suffix = f"{from_date.replace('.', '')}_{to_date.replace('.', '')}"
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
        Period=M15
        Login=257385275
        Model=0
        ExecutionMode=0
        Optimization=0
        FromDate={from_date}
        ToDate={to_date}
        ForwardMode=0
        Report=\\Reports\\{stem}_XAUUSDc_M15_{report_suffix}
        ReplaceReport=1
        ShutdownTerminal=1
        Deposit={deposit}
        Currency=USD
        Leverage={leverage}
        UseLocal=1
        UseRemote=0
        UseCloud=0
        Visual=0
        """
    )


def run_backtest(stem: str, from_date: str, to_date: str, deposit: int, leverage: str) -> tuple[Path, Path | None]:
    ini_path = MT5_BUILD / f"{stem}.backtest.ini"
    ini_path.write_text(build_ini(stem, from_date, to_date, deposit, leverage))
    shutil.copy2(MT5_BUILD / f"{stem}.ex5", MT5_EXPERTS / f"{stem}.ex5")

    report_suffix = f"{from_date.replace('.', '')}_{to_date.replace('.', '')}"
    report_path = REPORTS_DIR / f"{stem}_XAUUSDc_M15_{report_suffix}.htm"
    for old in REPORTS_DIR.glob(f"{stem}_XAUUSDc_M15_{report_suffix}*"):
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

                if log_done and stable_hits >= 2:
                    break
        time.sleep(2)

    if proc.poll() is None:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=10)

    if not report_path.exists():
        raise RuntimeError(f"Missing report for {stem}")
    return report_path, active_log


def parse_report(report_path: Path) -> dict[str, float]:
    text = report_path.read_bytes().decode("utf-16le", errors="ignore")
    plain = re.sub(r"<[^>]+>", " ", text).replace("\xa0", " ")
    plain = re.sub(r"\s+", " ", plain)

    def extract(key: str) -> str:
        match = re.search(re.escape(key) + r"\s*([^:]{1,90})", plain)
        if not match:
            raise RuntimeError(f"Failed to parse {key} from {report_path}")
        return match.group(1).strip()

    def first_number(value: str) -> float:
        match = re.search(r"-?[\d ]+(?:\.\d+)?", value)
        if not match:
            raise RuntimeError(f"No numeric value in {value!r}")
        return float(match.group(0).replace(" ", ""))

    def first_pct(value: str) -> float:
        match = re.search(r"\(([\d.]+)%\)", value)
        if not match:
            raise RuntimeError(f"No percentage value in {value!r}")
        return float(match.group(1))

    return {
        "net_profit": first_number(extract("Total Net Profit:")),
        "profit_factor": first_number(extract("Profit Factor:")),
        "expected_payoff": first_number(extract("Expected Payoff:")),
        "total_trades": first_number(extract("Total Trades:")),
        "win_rate": first_pct(extract("Profit Trades (% of total):")),
        "balance_dd_abs": first_number(extract("Balance Drawdown Maximal:")),
        "balance_dd_pct": first_pct(extract("Balance Drawdown Maximal:")),
        "equity_dd_abs": first_number(extract("Equity Drawdown Maximal:")),
        "equity_dd_pct": first_pct(extract("Equity Drawdown Maximal:")),
    }


def write_outputs(results: list[VersionResult], run_dir: Path, title: str, from_date: str, to_date: str, deposit: int, leverage: str) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    json_path = run_dir / "compare_results.json"
    csv_path = run_dir / "compare_results.csv"
    md_path = run_dir / "compare_summary.md"

    json_path.write_text(json.dumps([asdict(r) for r in results], indent=2))

    with csv_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(asdict(results[0]).keys()))
        writer.writeheader()
        writer.writerows(asdict(r) for r in results)

    lines = [
        f"# {title}",
        "",
        f"Setup: `XAUUSDc`, `M15`, `{from_date} - {to_date}`, `Deposit {deposit} USD`, `Leverage {leverage}`, `Every tick`.",
        "",
        "| Version | Net Profit | PF | Win Rate | Trades | Balance DD | Equity DD |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for r in results:
        lines.append(
            f"| {r.version} | {r.net_profit:.2f} | {r.profit_factor:.2f} | {r.win_rate:.2f}% | "
            f"{r.total_trades} | {r.balance_dd_pct:.2f}% | {r.equity_dd_pct:.2f}% |"
        )
    md_path.write_text("\n".join(lines) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--from-date", default="2025.10.18")
    parser.add_argument("--to-date", default="2026.04.15")
    parser.add_argument("--deposit", type=int, default=100)
    parser.add_argument("--leverage", default="1:100")
    parser.add_argument("--label", default="compare_6m_100")
    parser.add_argument("--title", default="Compare Versions")
    args = parser.parse_args()

    run_dir = ROOT / "build" / args.label
    results: list[VersionResult] = []
    for version in VERSIONS:
        source_file = ROOT / "mt5" / f"InvictusForward1M15_{version}.mq5"
        stem = compile_variant(version, source_file, args.label)
        report_path, tester_log = run_backtest(stem, args.from_date, args.to_date, args.deposit, args.leverage)
        metrics = parse_report(report_path)
        result = VersionResult(
            version=version,
            report_path=str(report_path),
            tester_log=str(tester_log) if tester_log else "",
            net_profit=metrics["net_profit"],
            profit_factor=metrics["profit_factor"],
            expected_payoff=metrics["expected_payoff"],
            total_trades=int(metrics["total_trades"]),
            win_rate=metrics["win_rate"],
            balance_dd_abs=metrics["balance_dd_abs"],
            balance_dd_pct=metrics["balance_dd_pct"],
            equity_dd_abs=metrics["equity_dd_abs"],
            equity_dd_pct=metrics["equity_dd_pct"],
        )
        results.append(result)
        print(
            f"{version}: net={result.net_profit:.2f} pf={result.profit_factor:.2f} "
            f"wr={result.win_rate:.2f}% trades={result.total_trades} eqdd={result.equity_dd_pct:.2f}%",
            flush=True,
        )

    write_outputs(results, run_dir, args.title, args.from_date, args.to_date, args.deposit, args.leverage)


if __name__ == "__main__":
    main()
