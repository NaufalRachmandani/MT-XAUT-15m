#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import time
import zipfile
from dataclasses import dataclass
from pathlib import Path

from analyze_mt5_report import parse_first_number, parse_report_metrics, read_report


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "mt5" / "Suis_BTC_v1.mq5"
OUT = ROOT / "build" / "suis_btc_v1_backtest"
PACKAGE = ROOT / "build" / "suis_btc_v1_live_package"

WINEPREFIX = Path.home() / "Library/Application Support/net.metaquotes.wine.metatrader5"
WINE = Path("/Applications/MetaTrader 5.app/Contents/SharedSupport/wine/bin/wine64")
METAEDITOR = r"C:\Program Files\MetaTrader 5\metaeditor64.exe"
TERMINAL = r"C:\Program Files\MetaTrader 5\terminal64.exe"
MT5_BUILD = WINEPREFIX / "drive_c" / "MT5Build"
EXPERTS = WINEPREFIX / "drive_c" / "Program Files" / "MetaTrader 5" / "MQL5" / "Experts" / "Suis_BTC"
REPORTS = WINEPREFIX / "drive_c" / "Program Files" / "MetaTrader 5" / "Reports"


@dataclass(frozen=True)
class Variant:
    name: str
    replacements: dict[str, object]
    note: str
    period: str = "H1"


def const_value(value: object) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, float):
        return f"{value:.2f}"
    if isinstance(value, str):
        if value.startswith("PERIOD_"):
            return value
        return json.dumps(value)
    return str(value)


def patch_source(text: str, stem: str, replacements: dict[str, object]) -> str:
    text = re.sub(r'#property version\s+"[^"]+"', '#property version   "1.00"', text, count=1)
    text = text.replace("Suis_BTC_v1", stem)
    for name, raw_value in replacements.items():
        value = const_value(raw_value)
        pattern = re.compile(rf"(input\s+[A-Za-z0-9_]+\s+{re.escape(name)}\s*=\s*)[^;]+;")
        text, count = pattern.subn(lambda m: f"{m.group(1)}{value};", text, count=1)
        if count != 1:
            raise RuntimeError(f"failed to replace {name}")
    return text


def env() -> dict[str, str]:
    output = os.environ.copy()
    output["WINEPREFIX"] = str(WINEPREFIX)
    output["WINEDEBUG"] = "-all"
    return output


def win_build_path(filename: str) -> str:
    return rf"C:\MT5Build\{filename}"


def compile_source(stem: str, source_text: str, experts_dir: Path = EXPERTS) -> Path:
    MT5_BUILD.mkdir(parents=True, exist_ok=True)
    experts_dir.mkdir(parents=True, exist_ok=True)
    build_src = MT5_BUILD / f"{stem}.mq5"
    build_src.write_text(source_text)
    compile_log = MT5_BUILD / f"{stem}.compile.log"
    subprocess.run(
        [
            str(WINE),
            METAEDITOR,
            f"/compile:{win_build_path(stem + '.mq5')}",
            f"/log:{win_build_path(stem + '.compile.log')}",
        ],
        env=env(),
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    log_text = compile_log.read_bytes().decode("utf-16le", errors="ignore") if compile_log.exists() else ""
    if "0 errors" not in log_text:
        raise RuntimeError(f"compile failed for {stem}: {log_text[-1800:]}")
    ex5 = MT5_BUILD / f"{stem}.ex5"
    if not ex5.exists():
        raise RuntimeError(f"missing compiled ex5 for {stem}")
    target = experts_dir / f"{stem}.ex5"
    shutil.copy2(ex5, target)
    return target


def write_tester_ini(
    stem: str,
    report_name: str,
    symbol: str,
    period: str,
    from_date: str,
    to_date: str,
    deposit: int,
    leverage: str,
    login: int,
    server: str,
) -> Path:
    ini = MT5_BUILD / f"{report_name}.ini"
    config = f"""[Common]
Login={login}
Server={server}
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
Expert=Suis_BTC\\{stem}.ex5
Symbol={symbol}
Period={period}
Login={login}
Model=0
ExecutionMode=0
Optimization=0
FromDate={from_date}
ToDate={to_date}
ForwardMode=0
Report=\\Reports\\{report_name}
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
    ini.write_bytes(b"\xff\xfe" + config.encode("utf-16le"))
    return ini


def dd_percent(value: str) -> float:
    match = re.search(r"\(([-\d.]+)%\)", value)
    return float(match.group(1)) if match else 0.0


def winrate(metrics: dict[str, str]) -> float:
    value = metrics.get("Profit Trades (% of total):", "")
    match = re.search(r"\(([-\d.]+)%\)", value)
    return float(match.group(1)) if match else 0.0


def run_backtest(
    stem: str,
    variant: str,
    window: str,
    symbol: str,
    period: str,
    from_date: str,
    to_date: str,
    deposit: int,
    leverage: str,
    login: int,
    server: str,
    timeout: int,
) -> dict[str, object]:
    report_name = f"{stem}_{variant}_{symbol}_{period}_{window}_{from_date.replace('.', '')}_{to_date.replace('.', '')}"
    report = REPORTS / f"{report_name}.htm"
    if report.exists():
        report.unlink()
    ini = write_tester_ini(stem, report_name, symbol, period, from_date, to_date, deposit, leverage, login, server)
    subprocess.run(
        [str(WINE), TERMINAL, f"/config:{win_build_path(ini.name)}"],
        env=env(),
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        timeout=timeout,
    )
    for _ in range(120):
        if report.exists() and report.stat().st_size > 0:
            break
        time.sleep(1)
    if not report.exists() or report.stat().st_size == 0:
        raise RuntimeError(f"report missing: {report}")

    report_text = read_report(report)
    metrics = parse_report_metrics(report_text)
    plain = re.sub(r"<[^>]+>", " ", report_text).replace("\xa0", " ")
    plain = re.sub(r"\s+", " ", plain)
    bars_match = re.search(r"\bBars:\s*([\d ]+)", plain)
    period_match = re.search(r"\bPeriod:\s*([^I]{1,80})", plain)
    bars = int(bars_match.group(1).replace(" ", "")) if bars_match else 0
    report_period = period_match.group(1).strip() if period_match else ""
    if bars <= 0 or not report_period.startswith(period):
        raise RuntimeError(f"invalid MT5 report ({report_period=}, expected={period}, {bars=}): {report}")

    net = parse_first_number(metrics.get("Total Net Profit:", ""))
    trades = int(parse_first_number(metrics.get("Total Trades:", "")))
    pf = parse_first_number(metrics.get("Profit Factor:", ""))
    eqdd = metrics.get("Equity Drawdown Maximal:", "")
    baldd = metrics.get("Balance Drawdown Maximal:", "")
    return {
        "variant": variant,
        "window": window,
        "symbol": symbol,
        "period": period,
        "from": from_date,
        "to": to_date,
        "deposit": deposit,
        "leverage": leverage,
        "report": str(report),
        "ini": str(ini),
        "bars": bars,
        "net": net,
        "net_pct": net / deposit * 100.0,
        "trades": trades,
        "win_rate": winrate(metrics),
        "profit_factor": pf,
        "equity_dd": eqdd,
        "equity_dd_pct": dd_percent(eqdd),
        "balance_dd": baldd,
        "balance_dd_pct": dd_percent(baldd),
        "metrics": metrics,
    }


VARIANTS = [
    Variant("h1_base", {}, "H1 strict multi-timeframe trend baseline", "H1"),
    Variant(
        "h1_long_pb",
        {
            "SBTC_EnableSells": False,
            "SBTC_EnableBreakoutEngine": False,
            "SBTC_EnableReversalEngine": False,
            "SBTC_RiskPercent": 2.0,
            "SBTC_MaxPositions": 2,
            "SBTC_MaxSameSidePositions": 2,
            "SBTC_MinScore": 70,
            "SBTC_MinSLUsd": 180.0,
            "SBTC_MaxSLUsd": 1100.0,
            "SBTC_StopBufferATR": 0.18,
            "SBTC_PullbackTouchATR": 0.42,
            "SBTC_PullbackRR": 1.75,
            "SBTC_BreakevenR": 0.75,
            "SBTC_TrailStartR": 1.15,
            "SBTC_TrailATR": 0.95,
            "SBTC_MaxHoldBars": 36,
            "SBTC_DailyMaxLossPct": 10.0,
            "SBTC_MaxAccountDrawdownPct": 24.0,
        },
        "H1 long-only pullback in confirmed bull regime",
        "H1",
    ),
    Variant(
        "h1_long_mixed",
        {
            "SBTC_EnableSells": False,
            "SBTC_EnableReversalEngine": False,
            "SBTC_RiskPercent": 2.2,
            "SBTC_MaxPositions": 2,
            "SBTC_MaxSameSidePositions": 2,
            "SBTC_MinScore": 72,
            "SBTC_MinBreakATR": 0.08,
            "SBTC_MinBodyRatio": 0.46,
            "SBTC_MinSLUsd": 180.0,
            "SBTC_MaxSLUsd": 1200.0,
            "SBTC_StopBufferATR": 0.20,
            "SBTC_BreakoutRR": 2.05,
            "SBTC_PullbackRR": 1.65,
            "SBTC_BreakevenR": 0.85,
            "SBTC_TrailStartR": 1.30,
            "SBTC_TrailATR": 1.05,
            "SBTC_MaxHoldBars": 48,
            "SBTC_DailyMaxLossPct": 10.0,
            "SBTC_MaxAccountDrawdownPct": 25.0,
        },
        "H1 long-only breakout plus pullback with wider runners",
        "H1",
    ),
    Variant(
        "h1_two_pb",
        {
            "SBTC_EnableBreakoutEngine": False,
            "SBTC_EnableReversalEngine": False,
            "SBTC_RiskPercent": 1.6,
            "SBTC_MaxPositions": 2,
            "SBTC_MaxSameSidePositions": 1,
            "SBTC_MinScore": 72,
            "SBTC_MinSLUsd": 180.0,
            "SBTC_MaxSLUsd": 900.0,
            "SBTC_StopBufferATR": 0.15,
            "SBTC_PullbackTouchATR": 0.34,
            "SBTC_PullbackRR": 1.45,
            "SBTC_BreakevenR": 0.65,
            "SBTC_TrailStartR": 1.00,
            "SBTC_TrailATR": 0.80,
            "SBTC_MaxHoldBars": 30,
            "SBTC_DailyMaxLossPct": 8.0,
            "SBTC_MaxAccountDrawdownPct": 20.0,
        },
        "H1 two-sided pullback only in confirmed higher-timeframe trend",
        "H1",
    ),
    Variant(
        "m30_long_pb",
        {
            "SBTC_TF": "PERIOD_M30",
            "SBTC_EnableSells": False,
            "SBTC_EnableBreakoutEngine": False,
            "SBTC_EnableReversalEngine": False,
            "SBTC_RiskPercent": 1.8,
            "SBTC_MaxPositions": 2,
            "SBTC_MaxSameSidePositions": 2,
            "SBTC_MinScore": 72,
            "SBTC_MinSLUsd": 120.0,
            "SBTC_MaxSLUsd": 700.0,
            "SBTC_StopBufferATR": 0.14,
            "SBTC_PullbackTouchATR": 0.36,
            "SBTC_PullbackRR": 1.55,
            "SBTC_BreakevenR": 0.65,
            "SBTC_TrailStartR": 1.00,
            "SBTC_TrailATR": 0.80,
            "SBTC_MaxHoldBars": 48,
            "SBTC_DailyMaxLossPct": 9.0,
            "SBTC_MaxAccountDrawdownPct": 22.0,
        },
        "M30 long-only pullback for more frequency with strict trend filter",
        "M30",
    ),
    Variant(
        "m30_two_pb_side",
        {
            "SBTC_TF": "PERIOD_M30",
            "SBTC_EnableBreakoutEngine": False,
            "SBTC_EnableReversalEngine": False,
            "SBTC_AllowSidewaysPullback": True,
            "SBTC_RiskPercent": 1.3,
            "SBTC_MaxPositions": 2,
            "SBTC_MaxSameSidePositions": 1,
            "SBTC_MinScore": 74,
            "SBTC_MinSLUsd": 100.0,
            "SBTC_MaxSLUsd": 620.0,
            "SBTC_StopBufferATR": 0.12,
            "SBTC_PullbackTouchATR": 0.25,
            "SBTC_PullbackRR": 1.25,
            "SBTC_BreakevenR": 0.50,
            "SBTC_TrailStartR": 0.85,
            "SBTC_TrailATR": 0.65,
            "SBTC_MaxHoldBars": 30,
            "SBTC_DailyMaxLossPct": 7.0,
            "SBTC_MaxAccountDrawdownPct": 18.0,
        },
        "M30 two-sided pullback probe allowing only high-score sideways setups",
        "M30",
    ),
    Variant(
        "h4_trend",
        {
            "SBTC_TF": "PERIOD_H4",
            "SBTC_EnableReversalEngine": False,
            "SBTC_RiskPercent": 2.4,
            "SBTC_MaxPositions": 2,
            "SBTC_MaxSameSidePositions": 1,
            "SBTC_MinScore": 72,
            "SBTC_MinSLUsd": 300.0,
            "SBTC_MaxSLUsd": 2200.0,
            "SBTC_StopBufferATR": 0.18,
            "SBTC_BreakoutRR": 2.20,
            "SBTC_PullbackRR": 1.80,
            "SBTC_BreakevenR": 0.95,
            "SBTC_TrailStartR": 1.55,
            "SBTC_TrailATR": 1.25,
            "SBTC_MaxHoldBars": 28,
            "SBTC_DailyMaxLossPct": 10.0,
            "SBTC_MaxAccountDrawdownPct": 24.0,
        },
        "H4 slower trend-following probe with wider ATR exits",
        "H4",
    ),
    Variant(
        "h1_short_pb",
        {
            "SBTC_EnableBuys": False,
            "SBTC_EnableBreakoutEngine": False,
            "SBTC_EnableReversalEngine": False,
            "SBTC_RiskPercent": 1.2,
            "SBTC_MaxPositions": 1,
            "SBTC_MaxSameSidePositions": 1,
            "SBTC_MinScore": 76,
            "SBTC_MinBodyRatio": 0.50,
            "SBTC_MinSLUsd": 180.0,
            "SBTC_MaxSLUsd": 850.0,
            "SBTC_StopBufferATR": 0.12,
            "SBTC_PullbackTouchATR": 0.22,
            "SBTC_PullbackRR": 1.25,
            "SBTC_BreakevenR": 0.55,
            "SBTC_TrailStartR": 0.95,
            "SBTC_TrailATR": 0.70,
            "SBTC_MaxHoldBars": 24,
            "SBTC_DailyMaxLossPct": 6.0,
            "SBTC_MaxAccountDrawdownPct": 16.0,
        },
        "H1 short-only strict pullback probe for bear regimes",
        "H1",
    ),
]


def score_result(result: dict[str, object]) -> float:
    net_pct = float(result["net_pct"])
    eqdd = float(result["equity_dd_pct"])
    pf = float(result["profit_factor"])
    trades = int(result["trades"])
    if trades < 8 or net_pct <= 0:
        return -999999.0 + net_pct
    return net_pct - eqdd * 3.0 + min(pf, 3.0) * 35.0 + min(trades, 80) * 0.15


def write_summary(results: list[dict[str, object]], champion: str, symbol: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    payload = {"symbol": symbol, "champion": champion, "results": results}
    (OUT / "summary.json").write_text(json.dumps(payload, indent=2))

    lines = [
        "# Suis_BTC_v1 Backtest Summary",
        "",
        f"- Symbol: `{symbol}`",
        "- Timeframe: mixed research run",
        f"- Champion: `{champion}`",
        f"- Generated: `{time.strftime('%Y-%m-%d %H:%M:%S')}`",
        "",
        "| Variant | TF | Window | Net % | Trades | Win % | PF | EqDD % | Report |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for item in results:
        report = Path(str(item["report"]))
        lines.append(
            f"| {item['variant']} | {item['period']} | {item['window']} | {float(item['net_pct']):.2f}% | "
            f"{int(item['trades'])} | {float(item['win_rate']):.2f}% | {float(item['profit_factor']):.2f} | "
            f"{float(item['equity_dd_pct']):.2f}% | `{report.name}` |"
        )
    (OUT / "summary.md").write_text("\n".join(lines) + "\n")


def package_champion(champion_source: str, champion_period: str) -> None:
    if PACKAGE.exists():
        shutil.rmtree(PACKAGE)
    package_experts = PACKAGE / "MQL5" / "Experts" / "Suis_BTC"
    package_experts.mkdir(parents=True, exist_ok=True)
    source_text = patch_source(champion_source, "Suis_BTC_v1", {})
    ex5 = compile_source("Suis_BTC_v1", source_text, EXPERTS)
    shutil.copy2(ex5, package_experts / "Suis_BTC_v1.ex5")
    (PACKAGE / "INSTALL.md").write_text(
        "# Suis_BTC_v1 Install\n\n"
        "Copy `MQL5/Experts/Suis_BTC/Suis_BTC_v1.ex5` ke folder MT5 yang sama.\n"
        f"Attach ke chart BTC `{champion_period}` yang sesuai broker, misalnya `BTCUSDm,{champion_period}`.\n"
    )
    zip_path = ROOT / "build" / "suis_btc_v1_live_package.zip"
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for file in PACKAGE.rglob("*"):
            if file.is_file():
                zf.write(file, file.relative_to(PACKAGE))


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    source = SOURCE.read_text()
    login = 109707840
    server = "Exness-MT5Real6"
    symbol = "BTCUSDm"
    deposit = 150
    leverage = "1:2000"
    to_date = "2026.05.08"

    variant_runs: list[dict[str, object]] = []
    variant_sources: dict[str, str] = {}
    variant_periods: dict[str, str] = {}
    for variant in VARIANTS:
        stem = f"Suis_BTC_v1_{variant.name}"
        patched = patch_source(source, stem, variant.replacements)
        variant_sources[variant.name] = patch_source(source, "Suis_BTC_v1", variant.replacements)
        variant_periods[variant.name] = variant.period
        compile_source(stem, patched)
        try:
            result = run_backtest(
                stem,
                variant.name,
                "2026_ytd",
                symbol,
                variant.period,
                "2026.01.01",
                to_date,
                deposit,
                leverage,
                login,
                server,
                timeout=360,
            )
            result["note"] = variant.note
            variant_runs.append(result)
            print(
                f"{variant.name}: net={result['net_pct']:.2f}% trades={result['trades']} "
                f"pf={result['profit_factor']:.2f} eqdd={result['equity_dd_pct']:.2f}%"
            )
        except Exception as exc:
            print(f"{variant.name}: failed: {exc}")

    if not variant_runs:
        raise RuntimeError("no successful BTC backtest runs")

    champion_result = max(variant_runs, key=score_result)
    champion = str(champion_result["variant"])
    champion_source = variant_sources[champion]
    champion_period = variant_periods[champion]
    champion_stem = f"Suis_BTC_v1_{champion}"

    validation: list[dict[str, object]] = []
    for window, start in [("recent_2m", "2026.03.08"), ("2025_current", "2025.01.01")]:
        try:
            item = run_backtest(
                champion_stem,
                champion,
                window,
                symbol,
                champion_period,
                start,
                to_date,
                deposit,
                leverage,
                login,
                server,
                timeout=480,
            )
            item["note"] = "champion validation"
            validation.append(item)
            print(
                f"champion {window}: net={item['net_pct']:.2f}% trades={item['trades']} "
                f"pf={item['profit_factor']:.2f} eqdd={item['equity_dd_pct']:.2f}%"
            )
        except Exception as exc:
            print(f"champion {window}: failed: {exc}")

    results = variant_runs + validation
    write_summary(results, champion, symbol)
    package_champion(champion_source, champion_period)
    print(f"summary: {OUT / 'summary.md'}")
    print(f"package: {PACKAGE}")


if __name__ == "__main__":
    main()
