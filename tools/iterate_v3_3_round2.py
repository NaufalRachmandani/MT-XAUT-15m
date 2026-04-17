#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import textwrap
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path("/Users/naufalrachmandani/Hobby/MT5 XAU 15m")
EA_SOURCE = ROOT / "mt5" / "InvictusForward1M15_v3_3.mq5"
TOOLS_DIR = ROOT / "tools"
RUN_DIR = ROOT / "build" / "v3_3_sell_round2"
RUN_DIR.mkdir(parents=True, exist_ok=True)

WINEPREFIX = Path("/Users/naufalrachmandani/Library/Application Support/net.metaquotes.wine.metatrader5")
MT5_BUILD = WINEPREFIX / "drive_c" / "MT5Build"
MT5_EXPERTS = WINEPREFIX / "drive_c" / "Program Files" / "MetaTrader 5" / "MQL5" / "Experts" / "Invictus"
REPORTS_DIR = WINEPREFIX / "drive_c" / "Program Files" / "MetaTrader 5" / "Reports"
TESTER_LOG = WINEPREFIX / "drive_c" / "Program Files" / "MetaTrader 5" / "Tester" / "logs" / "20260417.log"
WINE = "/Applications/MetaTrader 5.app/Contents/SharedSupport/wine/bin/wine64"
METAEDITOR_EXE = r"C:\Program Files\MetaTrader 5\metaeditor64.exe"
TERMINAL_EXE = r"C:\Program Files\MetaTrader 5\terminal64.exe"


PARAMS: dict[str, Any] = {
    "IF1_TREND_MAX_POSITIONS_LOW_OVERRIDE": 7,
    "IF1_TREND_MAX_POSITIONS_MID_OVERRIDE": 11,
    "IF1_TREND_MAX_POSITIONS_HIGH_OVERRIDE": 15,
    "IF1_COMPOUND_BALANCE_STEP_LOW_OVERRIDE": 250.0,
    "IF1_COMPOUND_BALANCE_STEP_MID_OVERRIDE": 300.0,
    "IF1_COMPOUND_BALANCE_STEP_HIGH_OVERRIDE": 375.0,
    "IF1_COMPOUND_BASE_LOT_MID_OVERRIDE": 0.82,
    "IF1_COMPOUND_BASE_LOT_HIGH_OVERRIDE": 1.92,
    "IF1_PENDING_CANCEL_LOSS_CAP_PCT": 6.0,
    "IF1_BREAKEVEN_LOCK_USD": 1.5,
    "IF1_SIDEWAYS_TP_FRACTION_OVERRIDE": 0.55,
    "IF1_SIDEWAYS_MIN_TP_USD": 6.5,
    "IF1_TREND_MIN_SL_OVERRIDE": 12.0,
    "IF1_TREND_MAX_SL_OVERRIDE": 30.0,
    "IF1_COOLDOWN_BARS_OVERRIDE": 1,
    "IF1_ZONE_COOLDOWN_BARS_OVERRIDE": 1,
    "IF1_MIN_BREAK_ATR_OVERRIDE": 0.18,
    "IF1_ZONE_SEARCH_WINDOW_OVERRIDE": 12,
    "IF1_MAX_ZONE_RANGE_USD_OVERRIDE": 30.0,
    "IF1_MAX_ZONE_PRIOR_TESTS_OVERRIDE": 2,
    "IF1_ENTRY_BODY_RATIO_OVERRIDE": 0.35,
    "IF1_SCORE_BUY_MIN_OVERRIDE": 70,
    "IF1_SCORE_SELL_MIN_OVERRIDE": 75,
    "IF1_TREND_LOW_SCORE_SELL_MAX": 84,
    "IF1_TREND_LOW_SCORE_SELL_RR_OVERRIDE": 1.35,
    "IF1_TREND_LOW_SCORE_SELL_LOT_MULT": 0.60,
    "IF1_TREND_SELL_TP_RR_DEFAULT_OVERRIDE": 1.62,
    "IF1_TREND_SELL_TP_RR_BOOST_OVERRIDE": 2.25,
    "IF1_TREND_HIGH_SCORE_BUY_RR_MIN": 95,
    "IF1_TREND_HIGH_SCORE_BUY_RR_OVERRIDE": 2.45,
    "IF1_SCORE_RR_BOOST_MIN_OVERRIDE": 84,
    "IF1_SELL_LOT_MODIFIER_OVERRIDE": 0.75,
    "IF1_SIDEWAYS_LOT_MODIFIER_OVERRIDE": 0.10,
    "IF1_TREND_DAILY_LOSS_CAP_PCT_OVERRIDE": 8.0,
    "IF1_SIDEWAYS_DAILY_LOSS_CAP_PCT_OVERRIDE": 5.0,
    "IF1_TREND_KILLSWITCH_WINS_OVERRIDE": 50,
    "IF1_SIDEWAYS_WINS_CAP_OVERRIDE": 20,
    "IF1_SIDEWAYS_ADX_THRESHOLD_OVERRIDE": 28.0,
    "IF1_SIDEWAYS_ENTRY_ZONE_FRACTION_OVERRIDE": 0.40,
    "IF1_SIDEWAYS_MAX_POSITIONS_OVERRIDE": 8,
    "IF1_SIDEWAYS_CLUSTER_MAX_PER_DAY_OVERRIDE": 5,
    "IF1_TREND_TIMED_PROFIT_CLOSE_HOURS_OVERRIDE": 4,
    "IF1_SIDEWAYS_TIMED_PROFIT_CLOSE_HOURS_OVERRIDE": 2,
    "IF1_TREND_TIMED_PROFIT_USD_PER_001_OVERRIDE": 24.0,
    "IF1_SIDEWAYS_TIMED_PROFIT_USD_PER_001_OVERRIDE": 15.0,
    "IF1_TREND_TP_RR_DEFAULT_OVERRIDE": 1.62,
    "IF1_TREND_TP_RR_BOOST_OVERRIDE": 2.25,
    "IF1_TREND_HIGH_SCORE_LOT_BOOST_MIN": 95,
    "IF1_TREND_HIGH_SCORE_LOT_BOOST": 1.18,
}


ITERATIONS: list[dict[str, Any]] = [
    {
        "name": "baseline",
        "hypothesis": "Baseline champion v3.3 sebagai pembanding round 2.",
        "changes": {},
    },
    {
        "name": "score75_lot_050",
        "hypothesis": "Beban sell score 75 diturunkan, tapi sell score 80+ tetap utuh sebagai hedge.",
        "changes": {
            "IF1_TREND_LOW_SCORE_SELL_MAX": 75,
            "IF1_TREND_LOW_SCORE_SELL_RR_OVERRIDE": 1.62,
            "IF1_TREND_LOW_SCORE_SELL_LOT_MULT": 0.50,
        },
    },
    {
        "name": "score75_lot_040",
        "hypothesis": "Versi lebih defensif: sell score 75 diperkecil lebih jauh.",
        "changes": {
            "IF1_TREND_LOW_SCORE_SELL_MAX": 75,
            "IF1_TREND_LOW_SCORE_SELL_RR_OVERRIDE": 1.62,
            "IF1_TREND_LOW_SCORE_SELL_LOT_MULT": 0.40,
        },
    },
    {
        "name": "score75_lot_050_rr_145",
        "hypothesis": "Sell score 75 dikecilkan dan TP-nya sedikit dipendekkan, tapi tidak sekeras bucket 84 sebelumnya.",
        "changes": {
            "IF1_TREND_LOW_SCORE_SELL_MAX": 75,
            "IF1_TREND_LOW_SCORE_SELL_RR_OVERRIDE": 1.45,
            "IF1_TREND_LOW_SCORE_SELL_LOT_MULT": 0.50,
        },
    },
    {
        "name": "score75_lot_030",
        "hypothesis": "Uji batas bawah: sell score 75 hampir dimatikan tapi masih tetap ada secara struktural.",
        "changes": {
            "IF1_TREND_LOW_SCORE_SELL_MAX": 75,
            "IF1_TREND_LOW_SCORE_SELL_RR_OVERRIDE": 1.62,
            "IF1_TREND_LOW_SCORE_SELL_LOT_MULT": 0.30,
        },
    },
]


@dataclass
class IterationResult:
    index: int
    name: str
    hypothesis: str
    params: dict[str, Any]
    metrics: dict[str, float]
    trend_diag: dict[str, float]
    sideways_diag: dict[str, float]
    sell_dir_diag: dict[str, float]
    sell_score_diag: dict[str, float]
    sell_exit_diag: dict[str, float]
    accepted: bool
    takeaway: str


def fmt_value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        text = f"{value:.10f}".rstrip("0").rstrip(".")
        if "." not in text:
            text += ".0"
        return text
    raise TypeError(f"Unsupported value type: {type(value)!r}")


def patch_source(template: str, params: dict[str, Any]) -> str:
    result = template
    for name, value in params.items():
        pattern = re.compile(rf"(static const [^;\n]*\b{name}\b\s*=\s*)([^;]+)(;)")
        replacement = lambda match: f"{match.group(1)}{fmt_value(value)}{match.group(3)}"
        result, count = pattern.subn(replacement, result)
        if count != 1:
            raise RuntimeError(f"Failed to patch constant {name}")
    return result


def run_subprocess(args: list[str], *, quiet: bool = True) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["WINEPREFIX"] = str(WINEPREFIX)
    env["WINEDEBUG"] = "-all"
    if quiet:
        return subprocess.run(args, cwd=ROOT, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, text=True, check=False)
    return subprocess.run(args, cwd=ROOT, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, check=False)


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def compile_variant(stem: str, source_text: str) -> None:
    source_path = MT5_BUILD / f"{stem}.mq5"
    compile_log = MT5_BUILD / f"{stem}.compile.log"
    write_file(source_path, source_text)
    run_subprocess([WINE, METAEDITOR_EXE, f"/compile:C:\\MT5Build\\{stem}.mq5", f"/log:C:\\MT5Build\\{stem}.compile.log"])
    log_text = compile_log.read_bytes().decode("utf-16le", errors="ignore")
    if "0 errors" not in log_text:
        raise RuntimeError(f"Compilation failed for {stem}: {log_text[-500:]}")


def build_ini(stem: str) -> str:
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
        FromDate=2025.01.01
        ToDate=2026.04.15
        ForwardMode=0
        Report=\\Reports\\{stem}_XAUUSDc_M15_2025_2026
        ReplaceReport=1
        ShutdownTerminal=1
        Deposit=10000
        Currency=USD
        Leverage=1:100
        UseLocal=1
        UseRemote=0
        UseCloud=0
        Visual=0
        """
    )


def run_backtest(stem: str) -> Path:
    ini_path = MT5_BUILD / f"{stem}.backtest.ini"
    write_file(ini_path, build_ini(stem))
    ex5_src = MT5_BUILD / f"{stem}.ex5"
    ex5_dst = MT5_EXPERTS / f"{stem}.ex5"
    shutil.copy2(ex5_src, ex5_dst)
    run_subprocess([WINE, TERMINAL_EXE, f"/config:C:\\MT5Build\\{stem}.backtest.ini"])
    report_path = REPORTS_DIR / f"{stem}_XAUUSDc_M15_2025_2026.htm"
    if not report_path.exists():
        raise RuntimeError(f"Missing report for {stem}")
    return report_path


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

    metrics = {
        "net_profit": first_number(extract("Total Net Profit:")),
        "profit_factor": first_number(extract("Profit Factor:")),
        "expected_payoff": first_number(extract("Expected Payoff:")),
        "recovery_factor": first_number(extract("Recovery Factor:")),
        "total_trades": first_number(extract("Total Trades:")),
        "profit_trades_pct": first_pct(extract("Profit Trades (% of total):")),
        "loss_trades_pct": first_pct(extract("Loss Trades (% of total):")),
        "balance_dd_abs": first_number(extract("Balance Drawdown Maximal:")),
        "balance_dd_pct": first_pct(extract("Balance Drawdown Maximal:")),
        "equity_dd_abs": first_number(extract("Equity Drawdown Maximal:")),
        "equity_dd_pct": first_pct(extract("Equity Drawdown Maximal:")),
    }
    return metrics


def parse_diag_line(prefix: str) -> dict[str, float]:
    text = TESTER_LOG.read_bytes().decode("utf-16le", errors="ignore")
    lines = [line for line in text.splitlines() if prefix in line]
    if not lines:
        return {}
    line = lines[-1]
    pairs = re.findall(r"([A-Za-z]+)=(-?[\d.]+)", line)
    return {key: float(value) for key, value in pairs}


def acceptable(metrics: dict[str, float]) -> bool:
    return metrics["profit_factor"] >= 1.15 and metrics["equity_dd_pct"] <= 35.0 and metrics["total_trades"] >= 3200


def hits_target(metrics: dict[str, float], sell_dir: dict[str, float]) -> bool:
    return (
        metrics["net_profit"] >= 500000.0
        and metrics["equity_dd_pct"] <= 25.0
        and metrics["profit_factor"] >= 1.15
        and metrics["total_trades"] >= 3200
        and sell_dir.get("sellPnl", -1e9) >= 0.0
    )


def composite(metrics: dict[str, float]) -> float:
    dd_penalty = 1.0 + max(0.0, metrics["equity_dd_pct"] - 25.0) / 6.0
    return metrics["net_profit"] * metrics["profit_factor"] / dd_penalty


def better(metrics: dict[str, float], best: dict[str, float], sell_dir: dict[str, float], best_sell_dir: dict[str, float]) -> bool:
    if not acceptable(metrics):
        return False
    if not acceptable(best):
        return True
    cur_target = hits_target(metrics, sell_dir)
    best_target = hits_target(best, best_sell_dir)
    if cur_target and not best_target:
        return True
    if cur_target and best_target:
        if metrics["net_profit"] > best["net_profit"] and metrics["equity_dd_pct"] <= best["equity_dd_pct"] + 1.0 and sell_dir.get("sellPnl", 0.0) >= best_sell_dir.get("sellPnl", 0.0):
            return True
        if metrics["net_profit"] > best["net_profit"] and metrics["equity_dd_pct"] <= best["equity_dd_pct"] and metrics["profit_factor"] >= best["profit_factor"] - 0.01:
            return True
        if metrics["net_profit"] > best["net_profit"] * 1.01 and metrics["profit_factor"] >= best["profit_factor"] - 0.02 and metrics["equity_dd_pct"] <= best["equity_dd_pct"] + 2.5:
            return True
        if metrics["net_profit"] >= best["net_profit"] * 0.995 and metrics["equity_dd_pct"] <= best["equity_dd_pct"] - 1.0:
            return True
        return False
    if best_target and not cur_target:
        return False
    if sell_dir.get("sellPnl", -1e9) > best_sell_dir.get("sellPnl", -1e9) + 15000.0 and metrics["net_profit"] >= best["net_profit"] * 0.98 and metrics["equity_dd_pct"] <= best["equity_dd_pct"] + 1.0:
        return True
    if metrics["net_profit"] >= 490000.0 and metrics["equity_dd_pct"] <= best["equity_dd_pct"] - 1.0 and metrics["profit_factor"] >= best["profit_factor"] - 0.01:
        return True
    return composite(metrics) > composite(best) * 1.03


def summarize_takeaway(metrics: dict[str, float], best: dict[str, float], trend: dict[str, float], sideways: dict[str, float], sell_dir: dict[str, float], sell_score: dict[str, float]) -> str:
    if not acceptable(metrics):
        if metrics["equity_dd_pct"] > 35.0:
            return "Ditolak: drawdown melewati guardrail."
        if metrics["profit_factor"] < 1.15:
            return "Ditolak: profit factor terlalu turun."
        if metrics["total_trades"] < 3200:
            return "Ditolak: trade count turun terlalu jauh."
        return "Ditolak: gagal guardrail utama."
    if hits_target(metrics, sell_dir):
        return "Target tercapai: profit tetap tinggi, DD turun, dan sell tidak minus."
    if sell_dir.get("sellPnl", -1e9) >= 0.0 and metrics["net_profit"] >= 490000.0:
        return "Promising: sell sudah non-negatif sambil profit tetap dekat 5000%."
    if sell_score.get("lowPnl", 0.0) > -10000.0:
        return "Promising: low-score sell jauh lebih sehat."
    if metrics["net_profit"] > best["net_profit"] and metrics["equity_dd_pct"] <= best["equity_dd_pct"] + 3.0:
        return "Promising: profit naik tanpa merusak risk terlalu banyak."
    if sideways.get("closedPnl", 0.0) < 0.0:
        return "Masalah utama: sideways kembali negatif."
    if trend.get("dailyLoss", 0.0) > 900:
        return "Masalah utama: trend terlalu agresif, daily loss block membengkak."
    if sell_dir.get("sellPnl", 0.0) < 0.0:
        return "Masalah utama: layer sell masih negatif."
    if metrics["profit_factor"] < best["profit_factor"]:
        return "Masalah utama: kualitas entry turun lebih cepat daripada growth."
    if metrics["equity_dd_pct"] < best["equity_dd_pct"]:
        return "Promising: drawdown turun, tapi profit belum cukup unggul."
    return "Netral: ada sinyal bagus, tetapi belum cukup mengalahkan champion."


def write_summary(results: list[IterationResult], champion: IterationResult) -> None:
    json_path = RUN_DIR / "v3_3_sell_round2_results.json"
    md_path = RUN_DIR / "v3_3_sell_round2_summary.md"
    json_path.write_text(
        json.dumps(
            {
                "generated_at": datetime.now().isoformat(),
                "champion": champion.index,
                "results": [
                    {
                        "index": r.index,
                        "name": r.name,
                        "hypothesis": r.hypothesis,
                        "accepted": r.accepted,
                        "takeaway": r.takeaway,
                        "metrics": r.metrics,
                        "trend_diag": r.trend_diag,
                        "sideways_diag": r.sideways_diag,
                        "sell_dir_diag": r.sell_dir_diag,
                        "sell_score_diag": r.sell_score_diag,
                        "sell_exit_diag": r.sell_exit_diag,
                        "params": r.params,
                    }
                    for r in results
                ],
            },
            indent=2,
        )
    )

    lines = [
        "# v3.3 Sell-Focused Round 2 Summary",
        "",
        f"Champion: iterasi {champion.index:02d} `{champion.name}`",
        f"Target: net profit >= 500000, equity DD <= 25%, total trades >= 3200, sellPnL >= 0",
        "",
        "| Iter | Name | Accepted | Net Profit | PF | Trades | Eq DD | Sell PnL | Takeaway |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for r in results:
        lines.append(
            f"| {r.index:02d} | {r.name} | {'yes' if r.accepted else 'no'} | "
            f"{r.metrics['net_profit']:.2f} | {r.metrics['profit_factor']:.2f} | "
            f"{int(r.metrics['total_trades'])} | {r.metrics['equity_dd_pct']:.2f}% | {r.sell_dir_diag.get('sellPnl', 0.0):.2f} | {r.takeaway} |"
        )
    md_path.write_text("\n".join(lines) + "\n")


def main() -> None:
    template = EA_SOURCE.read_text()
    current_params = dict(PARAMS)
    results: list[IterationResult] = []
    champion_result: IterationResult | None = None
    champion_metrics: dict[str, float] | None = None
    champion_sell_dir: dict[str, float] | None = None

    for idx, plan in enumerate(ITERATIONS, start=1):
        params = dict(current_params)
        params.update(plan["changes"])
        stem = f"InvictusForward1M15_v3_3_iter{idx:02d}"
        source_text = patch_source(template, params)
        compile_variant(stem, source_text)
        report_path = run_backtest(stem)
        metrics = parse_report(report_path)
        trend_diag = parse_diag_line("IF1 diag trend:")
        sideways_diag = parse_diag_line("IF1 diag sideways:")
        sell_dir_diag = parse_diag_line("IF1 diag trendDir:")
        sell_score_diag = parse_diag_line("IF1 diag sellScore:")
        sell_exit_diag = parse_diag_line("IF1 diag sellExit:")

        if champion_metrics is None:
            accepted = acceptable(metrics)
        else:
            accepted = better(metrics, champion_metrics, sell_dir_diag, champion_sell_dir or {})

        if champion_metrics is None:
            takeaway = "Baseline champion awal."
        else:
            takeaway = summarize_takeaway(metrics, champion_metrics, trend_diag, sideways_diag, sell_dir_diag, sell_score_diag)

        result = IterationResult(
            index=idx,
            name=plan["name"],
            hypothesis=plan["hypothesis"],
            params=params,
            metrics=metrics,
            trend_diag=trend_diag,
            sideways_diag=sideways_diag,
            sell_dir_diag=sell_dir_diag,
            sell_score_diag=sell_score_diag,
            sell_exit_diag=sell_exit_diag,
            accepted=accepted,
            takeaway=takeaway,
        )
        results.append(result)

        if champion_metrics is None or accepted:
            current_params = dict(params)
            champion_metrics = metrics
            champion_sell_dir = dict(sell_dir_diag)
            champion_result = result
            result.accepted = True
            if idx != 1:
                result.takeaway = "Dibawa ke baseline berikutnya."

        print(
            f"[{idx:02d}/{len(ITERATIONS):02d}] {plan['name']}: "
            f"net={metrics['net_profit']:.2f} pf={metrics['profit_factor']:.2f} "
            f"trades={int(metrics['total_trades'])} eqdd={metrics['equity_dd_pct']:.2f}% "
            f"{'ACCEPT' if result.accepted else 'reject'}"
        )

    if champion_result is None:
        raise RuntimeError("No champion result recorded")

    write_summary(results, champion_result)
    print()
    print(f"Champion iteration: {champion_result.index:02d} {champion_result.name}")
    print(f"Champion net profit: {champion_result.metrics['net_profit']:.2f}")
    print(f"Champion PF: {champion_result.metrics['profit_factor']:.2f}")
    print(f"Champion trades: {int(champion_result.metrics['total_trades'])}")
    print(f"Champion equity DD: {champion_result.metrics['equity_dd_pct']:.2f}%")
    print(f"Champion sell PnL: {champion_result.sell_dir_diag.get('sellPnl', 0.0):.2f}")


if __name__ == "__main__":
    main()
