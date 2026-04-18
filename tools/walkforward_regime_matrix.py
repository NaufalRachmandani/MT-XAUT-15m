#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import os
import re
import shutil
import statistics
import subprocess
import textwrap
import time
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path


ROOT = Path("/Users/naufalrachmandani/Hobby/MT5 XAU 15m")
RUN_DIR = ROOT / "build" / "walkforward_100"
RUN_DIR.mkdir(parents=True, exist_ok=True)

WINEPREFIX = Path("/Users/naufalrachmandani/Library/Application Support/net.metaquotes.wine.metatrader5")
MT5_BUILD = WINEPREFIX / "drive_c" / "MT5Build"
MT5_EXPERTS = WINEPREFIX / "drive_c" / "Program Files" / "MetaTrader 5" / "MQL5" / "Experts" / "Invictus"
REPORTS_DIR = WINEPREFIX / "drive_c" / "Program Files" / "MetaTrader 5" / "Reports"
TESTER_LOG_DIR = WINEPREFIX / "drive_c" / "Program Files" / "MetaTrader 5" / "Tester" / "logs"
WINE = "/Applications/MetaTrader 5.app/Contents/SharedSupport/wine/bin/wine64"
METAEDITOR_EXE = r"C:\Program Files\MetaTrader 5\metaeditor64.exe"
TERMINAL_EXE = r"C:\Program Files\MetaTrader 5\terminal64.exe"

VERSIONS = ["v1", "v4", "v5"]
START_DATE = date(2025, 1, 1)
END_DATE = date(2026, 4, 15)
DEPOSIT = 100
LEVERAGE = "1:100"


@dataclass
class Window:
    label: str
    from_date: str
    to_date: str


@dataclass
class ResultRow:
    window_label: str
    from_date: str
    to_date: str
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

    @property
    def recovery_proxy(self) -> float:
        dd_abs = self.equity_dd_abs if self.equity_dd_abs > 0 else 1.0
        return self.net_profit / dd_abs


def month_end(year: int, month: int) -> int:
    if month == 12:
        return 31
    next_month = date(year + (1 if month == 12 else 0), 1 if month == 12 else month + 1, 1)
    return (next_month - date.resolution).day


def generate_windows(start: date, end: date) -> list[Window]:
    windows: list[Window] = []
    cursor = date(start.year, start.month, 1)
    while cursor <= end:
        if cursor.year == end.year and cursor.month == end.month:
            window_end = end
        else:
            if cursor.month == 12:
                next_month = date(cursor.year + 1, 1, 1)
            else:
                next_month = date(cursor.year, cursor.month + 1, 1)
            window_end = next_month - date.resolution
        windows.append(
            Window(
                label=f"{cursor.year}-{cursor.month:02d}",
                from_date=f"{cursor.year:04d}.{cursor.month:02d}.01",
                to_date=f"{window_end.year:04d}.{window_end.month:02d}.{window_end.day:02d}",
            )
        )
        cursor = date(cursor.year + (1 if cursor.month == 12 else 0), 1 if cursor.month == 12 else cursor.month + 1, 1)
    return windows


def run_subprocess(args: list[str], quiet: bool = True) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["WINEPREFIX"] = str(WINEPREFIX)
    env["WINEDEBUG"] = "-all"
    kwargs: dict[str, object] = {"cwd": ROOT, "env": env, "text": True, "check": False}
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


def compile_variant(version: str, source_file: Path) -> str:
    stem = f"InvictusForward1M15_{version}_walkforward_100"
    build_source = MT5_BUILD / f"{stem}.mq5"
    compile_log = MT5_BUILD / f"{stem}.compile.log"
    build_source.write_text(source_file.read_text())
    run_subprocess([WINE, METAEDITOR_EXE, f"/compile:C:\\MT5Build\\{stem}.mq5", f"/log:C:\\MT5Build\\{stem}.compile.log"])
    log_text = compile_log.read_bytes().decode("utf-16le", errors="ignore")
    if "0 errors" not in log_text:
        raise RuntimeError(f"Compilation failed for {version}: {log_text[-600:]}")
    shutil.copy2(MT5_BUILD / f"{stem}.ex5", MT5_EXPERTS / f"{stem}.ex5")
    return stem


def build_ini(stem: str, window: Window) -> str:
    report_suffix = f"{window.from_date.replace('.', '')}_{window.to_date.replace('.', '')}"
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
        FromDate={window.from_date}
        ToDate={window.to_date}
        ForwardMode=0
        Report=\\Reports\\{stem}_XAUUSDc_M15_{report_suffix}
        ReplaceReport=1
        ShutdownTerminal=1
        Deposit={DEPOSIT}
        Currency=USD
        Leverage={LEVERAGE}
        UseLocal=1
        UseRemote=0
        UseCloud=0
        Visual=0
        """
    )


def run_backtest(stem: str, window: Window) -> tuple[Path, Path | None]:
    ini_path = MT5_BUILD / f"{stem}_{window.label}.backtest.ini"
    ini_path.write_text(build_ini(stem, window))

    report_suffix = f"{window.from_date.replace('.', '')}_{window.to_date.replace('.', '')}"
    report_path = REPORTS_DIR / f"{stem}_XAUUSDc_M15_{report_suffix}.htm"
    for old in REPORTS_DIR.glob(f"{stem}_XAUUSDc_M15_{report_suffix}*"):
        old.unlink(missing_ok=True)

    pre_log = latest_tester_log()
    pre_size = pre_log.stat().st_size if pre_log and pre_log.exists() else 0
    proc = launch_subprocess([WINE, TERMINAL_EXE, f"/config:C:\\MT5Build\\{ini_path.name}"])
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
        raise RuntimeError(f"Missing report for {stem} {window.label}")
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
        "total_trades": int(first_number(extract("Total Trades:"))),
        "win_rate": first_pct(extract("Profit Trades (% of total):")),
        "balance_dd_abs": first_number(extract("Balance Drawdown Maximal:")),
        "balance_dd_pct": first_pct(extract("Balance Drawdown Maximal:")),
        "equity_dd_abs": first_number(extract("Equity Drawdown Maximal:")),
        "equity_dd_pct": first_pct(extract("Equity Drawdown Maximal:")),
    }


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        return
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def fmt_pct(value: float) -> str:
    return f"{value:.2f}%"


def fmt_num(value: float) -> str:
    return f"{value:.2f}"


def build_outputs(rows: list[ResultRow]) -> None:
    rows_json = [asdict(r) for r in rows]
    (RUN_DIR / "walkforward_results.json").write_text(json.dumps(rows_json, indent=2))
    write_csv(RUN_DIR / "walkforward_results.csv", rows_json)

    grouped: dict[str, list[ResultRow]] = {}
    for row in rows:
        grouped.setdefault(row.window_label, []).append(row)

    windows = sorted(grouped.keys())
    winners: list[dict[str, object]] = []
    version_summary: list[dict[str, object]] = []

    best_net_counts = {version: 0 for version in VERSIONS}
    best_pf_counts = {version: 0 for version in VERSIONS}
    best_recovery_counts = {version: 0 for version in VERSIONS}

    for window_label in windows:
        group = grouped[window_label]
        best_net = max(group, key=lambda r: r.net_profit)
        best_pf = max(group, key=lambda r: r.profit_factor)
        best_recovery = max(group, key=lambda r: r.recovery_proxy)
        best_net_counts[best_net.version] += 1
        best_pf_counts[best_pf.version] += 1
        best_recovery_counts[best_recovery.version] += 1
        winners.append(
            {
                "window_label": window_label,
                "from_date": group[0].from_date,
                "to_date": group[0].to_date,
                "best_net_version": best_net.version,
                "best_net_profit": round(best_net.net_profit, 2),
                "best_pf_version": best_pf.version,
                "best_pf": round(best_pf.profit_factor, 2),
                "best_recovery_version": best_recovery.version,
                "best_recovery_proxy": round(best_recovery.recovery_proxy, 4),
            }
        )
    write_csv(RUN_DIR / "walkforward_winners.csv", winners)

    for version in VERSIONS:
        subset = [row for row in rows if row.version == version]
        nets = [row.net_profit for row in subset]
        pfs = [row.profit_factor for row in subset]
        wrs = [row.win_rate for row in subset]
        eqdds = [row.equity_dd_pct for row in subset]
        positive = sum(1 for value in nets if value > 0)
        best = max(subset, key=lambda r: r.net_profit)
        worst = min(subset, key=lambda r: r.net_profit)
        version_summary.append(
            {
                "version": version,
                "positive_windows": positive,
                "total_windows": len(subset),
                "avg_net_profit": round(sum(nets) / len(nets), 2),
                "median_net_profit": round(statistics.median(nets), 2),
                "avg_profit_factor": round(sum(pfs) / len(pfs), 2),
                "avg_win_rate": round(sum(wrs) / len(wrs), 2),
                "avg_equity_dd_pct": round(sum(eqdds) / len(eqdds), 2),
                "worst_equity_dd_pct": round(max(eqdds), 2),
                "best_window": best.window_label,
                "best_window_net": round(best.net_profit, 2),
                "worst_window": worst.window_label,
                "worst_window_net": round(worst.net_profit, 2),
                "best_net_wins": best_net_counts[version],
                "best_pf_wins": best_pf_counts[version],
                "best_recovery_wins": best_recovery_counts[version],
            }
        )
    write_csv(RUN_DIR / "walkforward_version_summary.csv", version_summary)

    matrix_rows: list[dict[str, object]] = []
    for window_label in windows:
        group = sorted(grouped[window_label], key=lambda r: VERSIONS.index(r.version))
        row: dict[str, object] = {
            "window_label": window_label,
            "from_date": group[0].from_date,
            "to_date": group[0].to_date,
        }
        for item in group:
            row[f"{item.version}_net"] = round(item.net_profit, 2)
            row[f"{item.version}_pf"] = round(item.profit_factor, 2)
            row[f"{item.version}_eqdd"] = round(item.equity_dd_pct, 2)
        matrix_rows.append(row)
    write_csv(RUN_DIR / "walkforward_matrix.csv", matrix_rows)

    recent_windows = [row for row in winners if row["window_label"] >= "2025-11"]
    recent_best_net_counts = {version: 0 for version in VERSIONS}
    for row in recent_windows:
        recent_best_net_counts[str(row["best_net_version"])] += 1
    recent_leader = max(recent_best_net_counts, key=recent_best_net_counts.get)
    robust_leader = max(version_summary, key=lambda row: (row["best_recovery_wins"], row["positive_windows"], -row["avg_equity_dd_pct"]))
    absolute_leader = max(version_summary, key=lambda row: (row["best_net_wins"], row["avg_net_profit"]))

    lines = [
        "# Walk-Forward Regime Matrix",
        "",
        f"Setup: `XAUUSDc`, `M15`, monthly windows from `{START_DATE:%Y.%m.%d}` to `{END_DATE:%Y.%m.%d}`, `Deposit {DEPOSIT} USD`, `Leverage {LEVERAGE}`, `Every tick`.",
        "",
        "## Aggregate Version Summary",
        "",
        "| Version | Positive Windows | Avg Net | Median Net | Avg PF | Avg WR | Avg EqDD | Worst EqDD | Best Net Wins | Best PF Wins | Best Recovery Wins |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in version_summary:
        lines.append(
            f"| {row['version']} | {row['positive_windows']}/{row['total_windows']} | {row['avg_net_profit']:.2f} | "
            f"{row['median_net_profit']:.2f} | {row['avg_profit_factor']:.2f} | {row['avg_win_rate']:.2f}% | "
            f"{row['avg_equity_dd_pct']:.2f}% | {row['worst_equity_dd_pct']:.2f}% | {row['best_net_wins']} | "
            f"{row['best_pf_wins']} | {row['best_recovery_wins']} |"
        )

    lines.extend(
        [
            "",
            "## Window Winners",
            "",
            "| Window | Period | Best Net | Best PF | Best Recovery Proxy |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for row in winners:
        lines.append(
            f"| {row['window_label']} | {row['from_date']} - {row['to_date']} | "
            f"{row['best_net_version']} ({row['best_net_profit']:.2f}) | "
            f"{row['best_pf_version']} ({row['best_pf']:.2f}) | "
            f"{row['best_recovery_version']} ({row['best_recovery_proxy']:.2f}) |"
        )

    lines.extend(
        [
            "",
            "## Regime Takeaways",
            "",
            f"- `Recent-leader` by monthly net profit is `{recent_leader}` over the recent windows set (`2025-11` onward).",
            f"- `Robust-leader` by recovery-style consistency is `{robust_leader['version']}`.",
            f"- `Absolute-leader` by number of monthly net-profit wins is `{absolute_leader['version']}`.",
            "- `Best Recovery Proxy` uses `net profit / equity drawdown absolute` as a simple walk-forward robustness measure on the same 100 USD account base.",
            "",
            "## Files",
            f"- [walkforward_results.json]({(RUN_DIR / 'walkforward_results.json').as_posix()})",
            f"- [walkforward_results.csv]({(RUN_DIR / 'walkforward_results.csv').as_posix()})",
            f"- [walkforward_winners.csv]({(RUN_DIR / 'walkforward_winners.csv').as_posix()})",
            f"- [walkforward_version_summary.csv]({(RUN_DIR / 'walkforward_version_summary.csv').as_posix()})",
            f"- [walkforward_matrix.csv]({(RUN_DIR / 'walkforward_matrix.csv').as_posix()})",
        ]
    )
    (RUN_DIR / "walkforward_summary.md").write_text("\n".join(lines) + "\n")


def main() -> None:
    windows = generate_windows(START_DATE, END_DATE)
    compiled: dict[str, str] = {}
    for version in VERSIONS:
        source_file = ROOT / "mt5" / f"InvictusForward1M15_{version}.mq5"
        compiled[version] = compile_variant(version, source_file)
        print(f"compiled {version} -> {compiled[version]}", flush=True)

    rows: list[ResultRow] = []
    total_runs = len(windows) * len(VERSIONS)
    run_index = 0
    for window in windows:
        for version in VERSIONS:
            run_index += 1
            stem = compiled[version]
            report_path, tester_log = run_backtest(stem, window)
            metrics = parse_report(report_path)
            row = ResultRow(
                window_label=window.label,
                from_date=window.from_date,
                to_date=window.to_date,
                version=version,
                report_path=str(report_path),
                tester_log=str(tester_log) if tester_log else "",
                net_profit=metrics["net_profit"],
                profit_factor=metrics["profit_factor"],
                expected_payoff=metrics["expected_payoff"],
                total_trades=metrics["total_trades"],
                win_rate=metrics["win_rate"],
                balance_dd_abs=metrics["balance_dd_abs"],
                balance_dd_pct=metrics["balance_dd_pct"],
                equity_dd_abs=metrics["equity_dd_abs"],
                equity_dd_pct=metrics["equity_dd_pct"],
            )
            rows.append(row)
            print(
                f"[{run_index}/{total_runs}] {window.label} {version}: "
                f"net={row.net_profit:.2f} pf={row.profit_factor:.2f} wr={row.win_rate:.2f}% eqdd={row.equity_dd_pct:.2f}%",
                flush=True,
            )

    build_outputs(rows)
    print(f"wrote outputs to {RUN_DIR}", flush=True)


if __name__ == "__main__":
    main()
