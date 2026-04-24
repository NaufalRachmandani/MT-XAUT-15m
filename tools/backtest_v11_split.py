#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import textwrap
import time
from pathlib import Path

ROOT = Path("/Users/naufalrachmandani/Hobby/MT5 XAU 15m")
WINEPREFIX = Path("/Users/naufalrachmandani/Library/Application Support/net.metaquotes.wine.metatrader5")
MT5_BUILD = WINEPREFIX / "drive_c" / "MT5Build"
MT5_EXPERTS = WINEPREFIX / "drive_c" / "Program Files" / "MetaTrader 5" / "MQL5" / "Experts" / "Invictus"
REPORTS_DIR = WINEPREFIX / "drive_c" / "Program Files" / "MetaTrader 5" / "Reports"
TESTER_PROFILE_DIR = WINEPREFIX / "drive_c" / "Program Files" / "MetaTrader 5" / "MQL5" / "Profiles" / "Tester"
TESTER_LOG_DIR = WINEPREFIX / "drive_c" / "Program Files" / "MetaTrader 5" / "Tester" / "logs"
WINE = "/Applications/MetaTrader 5.app/Contents/SharedSupport/wine/bin/wine64"
METAEDITOR_EXE = r"C:\Program Files\MetaTrader 5\metaeditor64.exe"
TERMINAL_EXE = r"C:\Program Files\MetaTrader 5\terminal64.exe"

RUN_DIR = ROOT / "build" / "v11_split_m5"
RUN_DIR.mkdir(parents=True, exist_ok=True)

BOTS = [
    ("bull", "InvictusBullM5_v11", "InvictusBullM5_v11.default_2026.set"),
    ("bear", "InvictusBearM5_v11", "InvictusBearM5_v11.default_2026.set"),
    ("combined", "InvictusCombinedM5_v11", "InvictusCombinedM5_v11.default_2026.set"),
]

WINDOWS = [
    ("last_2w", "2026.04.10", "2026.04.25"),
    ("2026_ytd", "2026.01.01", "2026.04.25"),
    ("2025_current", "2025.01.01", "2026.04.25"),
]


def run_subprocess(args: list[str]) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["WINEPREFIX"] = str(WINEPREFIX)
    env["WINEDEBUG"] = "-all"
    return subprocess.run(args, cwd=ROOT, env=env, text=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def launch_subprocess(args: list[str]) -> subprocess.Popen[str]:
    env = os.environ.copy()
    env["WINEPREFIX"] = str(WINEPREFIX)
    env["WINEDEBUG"] = "-all"
    return subprocess.Popen(args, cwd=ROOT, env=env, text=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def latest_tester_log() -> Path | None:
    logs = sorted(TESTER_LOG_DIR.glob("*.log"), key=lambda p: p.stat().st_mtime)
    return logs[-1] if logs else None


def compile_exact(stem: str) -> None:
    source = ROOT / "mt5" / f"{stem}.mq5"
    build_source = MT5_BUILD / f"{stem}.mq5"
    compile_log = MT5_BUILD / f"{stem}.compile.log"
    build_source.write_text(source.read_text())
    run_subprocess([WINE, METAEDITOR_EXE, f"/compile:C:\\MT5Build\\{stem}.mq5", f"/log:C:\\MT5Build\\{stem}.compile.log"])
    log_text = compile_log.read_bytes().decode("utf-16le", errors="ignore")
    if "0 errors" not in log_text:
        raise RuntimeError(f"compile failed for {stem}: {log_text[-1000:]}")
    MT5_EXPERTS.mkdir(parents=True, exist_ok=True)
    shutil.copy2(MT5_BUILD / f"{stem}.ex5", MT5_EXPERTS / f"{stem}.ex5")
    shutil.copy2(source, MT5_EXPERTS / f"{stem}.mq5")


def install_set(set_name: str) -> None:
    TESTER_PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / "mt5" / set_name, TESTER_PROFILE_DIR / set_name)


def build_ini(stem: str, set_name: str, from_date: str, to_date: str) -> str:
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
        Deposit=100
        Currency=USD
        Leverage=1:100
        UseLocal=1
        UseRemote=0
        UseCloud=0
        Visual=0
        """
    )


def run_backtest(stem: str, set_name: str, from_date: str, to_date: str) -> Path:
    suffix = f"{from_date.replace('.', '')}_{to_date.replace('.', '')}"
    ini_path = MT5_BUILD / f"{stem}.backtest.ini"
    ini_path.write_text(build_ini(stem, set_name, from_date, to_date))
    report_path = REPORTS_DIR / f"{stem}_XAUUSDc_M5_{suffix}.htm"
    for old in REPORTS_DIR.glob(f"{stem}_XAUUSDc_M5_{suffix}*"):
        old.unlink(missing_ok=True)

    pre_log = latest_tester_log()
    pre_size = pre_log.stat().st_size if pre_log and pre_log.exists() else 0
    proc = launch_subprocess([WINE, TERMINAL_EXE, f"/config:C:\\MT5Build\\{stem}.backtest.ini"])
    start_time = time.time()
    stable_size = -1
    stable_hits = 0
    active_log: Path | None = pre_log
    deadline = time.time() + 1200
    while time.time() < deadline:
        current_log = latest_tester_log()
        if current_log is not None:
            active_log = current_log
        if report_path.exists() and report_path.stat().st_mtime >= start_time:
            log_done = False
            if active_log and active_log.exists():
                raw_bytes = active_log.read_bytes()
                if active_log == pre_log:
                    tail_text = raw_bytes[pre_size:].decode("utf-16le", errors="ignore")
                else:
                    tail_text = raw_bytes.decode("utf-16le", errors="ignore")
                log_done = "automatical testing finished" in tail_text
            size = report_path.stat().st_size
            if size == stable_size:
                stable_hits += 1
            else:
                stable_size = size
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
        raise RuntimeError(f"missing report for {stem} {from_date}-{to_date}")
    return report_path


def parse_report(report_path: Path) -> dict[str, float]:
    text = report_path.read_bytes().decode("utf-16le", errors="ignore")
    plain = re.sub(r"<[^>]+>", " ", text).replace("\xa0", " ")
    plain = re.sub(r"\s+", " ", plain)

    def extract(key: str) -> str:
        match = re.search(re.escape(key) + r"\s*([^:]{1,90})", plain)
        if not match:
            raise RuntimeError(f"failed to parse {key} from {report_path}")
        return match.group(1).strip()

    def first_number(value: str) -> float:
        match = re.search(r"-?[\d ]+(?:\.\d+)?", value)
        if not match:
            return 0.0
        return float(match.group(0).replace(" ", ""))

    def first_pct(value: str) -> float:
        match = re.search(r"\(([\d.]+)%\)", value)
        return float(match.group(1)) if match else 0.0

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


def main() -> None:
    results = []
    for label, stem, set_name in BOTS:
        print(f"compile {stem}", flush=True)
        compile_exact(stem)
        install_set(set_name)
        bot_metrics = {}
        reports = {}
        for window, from_date, to_date in WINDOWS:
            print(f"backtest {label} {window}", flush=True)
            report = run_backtest(stem, set_name, from_date, to_date)
            bot_metrics[window] = parse_report(report)
            reports[window] = str(report)
        results.append({"bot": label, "stem": stem, "set": set_name, "metrics": bot_metrics, "reports": reports})

    (RUN_DIR / "results.json").write_text(json.dumps(results, indent=2))
    lines = [
        "# v11 Split M5 Backtest",
        "",
        "Setup: `XAUUSDc`, `M5`, `Deposit 100 USD`, `Leverage 1:100`, `Every tick`.",
        "",
        "| Bot | 2W Net | 2W Trades | 2W PF | 2026 Net | 2026 Trades | 2026 PF | 2026 EqDD | 2025-Current Net | 2025-Current Trades | 2025-Current EqDD |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in results:
        m2 = row["metrics"]["last_2w"]
        y26 = row["metrics"]["2026_ytd"]
        full = row["metrics"]["2025_current"]
        lines.append(
            f"| {row['bot']} | {m2['net_profit']:.2f}% | {m2['total_trades']:.0f} | {m2['profit_factor']:.2f} | "
            f"{y26['net_profit']:.2f}% | {y26['total_trades']:.0f} | {y26['profit_factor']:.2f} | {y26['equity_dd_pct']:.2f}% | "
            f"{full['net_profit']:.2f}% | {full['total_trades']:.0f} | {full['equity_dd_pct']:.2f}% |"
        )
    (RUN_DIR / "summary.md").write_text("\n".join(lines) + "\n")
    print(RUN_DIR / "summary.md")


if __name__ == "__main__":
    main()
