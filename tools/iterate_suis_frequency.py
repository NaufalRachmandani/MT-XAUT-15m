#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path

from analyze_mt5_report import parse_first_number, parse_report_metrics, read_report


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "mt5" / "SuisM5_v1.mq5"
OUT = ROOT / "build" / "suis_frequency_iteration"

WINEPREFIX = Path.home() / "Library/Application Support/net.metaquotes.wine.metatrader5"
WINE = Path("/Applications/MetaTrader 5.app/Contents/SharedSupport/wine/bin/wine64")
METAEDITOR = r"C:\Program Files\MetaTrader 5\metaeditor64.exe"
TERMINAL = r"C:\Program Files\MetaTrader 5\terminal64.exe"
MT5_BUILD = WINEPREFIX / "drive_c" / "MT5Build"
EXPERTS = WINEPREFIX / "drive_c" / "Program Files" / "MetaTrader 5" / "MQL5" / "Experts" / "Suis"
REPORTS = WINEPREFIX / "drive_c" / "Program Files" / "MetaTrader 5" / "Reports"


@dataclass(frozen=True)
class Variant:
    name: str
    replacements: dict[str, str]
    note: str


def const_value(value: object) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, str):
        if value.startswith('"') and value.endswith('"'):
            return value
        return json.dumps(value)
    if isinstance(value, float):
        return f"{value:.2f}"
    return str(value)


def patch_source(text: str, stem: str, replacements: dict[str, object]) -> str:
    text = re.sub(r'#property version\s+"[^"]+"', '#property version   "4.10"', text, count=1)
    text = text.replace("SuisM5_v1", stem)
    for name, raw_value in replacements.items():
        value = const_value(raw_value)
        pattern = re.compile(rf"const\s+([A-Za-z0-9_]+)\s+{re.escape(name)}\s*=\s*[^;]+;")
        text, count = pattern.subn(lambda m: f"const {m.group(1):<6} {name} = {value};", text, count=1)
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


def compile_variant(stem: str, source_text: str) -> Path:
    MT5_BUILD.mkdir(parents=True, exist_ok=True)
    EXPERTS.mkdir(parents=True, exist_ok=True)
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
        raise RuntimeError(f"compile failed for {stem}: {log_text[-1000:]}")
    ex5 = MT5_BUILD / f"{stem}.ex5"
    if not ex5.exists():
        raise RuntimeError(f"missing compiled ex5 for {stem}")
    target = EXPERTS / f"{stem}.ex5"
    shutil.copy2(ex5, target)
    return target


def write_tester_ini(stem: str, report_name: str, from_date: str, to_date: str, deposit: int, leverage: str) -> Path:
    ini = MT5_BUILD / f"{report_name}.ini"
    config = f"""[Common]
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
Expert=Suis\\{stem}.ex5
Symbol=XAUUSDc
Period=M5
Login=257385275
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
    # MT5 under Wine has intermittently ignored UTF-8 tester configs and produced
    # empty M0 reports. UTF-16LE with BOM matches MetaTrader's native config files.
    ini.write_bytes(b"\xff\xfe" + config.encode("utf-16le"))
    return ini


def run_backtest(stem: str, variant: str, window: str, from_date: str, to_date: str, deposit: int, leverage: str, timeout: int) -> dict[str, object]:
    report_name = f"{stem}_{variant}_{window}_{from_date.replace('.', '')}_{to_date.replace('.', '')}"
    report = REPORTS / f"{report_name}.htm"
    if report.exists():
        report.unlink()
    ini = write_tester_ini(stem, report_name, from_date, to_date, deposit, leverage)
    subprocess.run(
        [str(WINE), TERMINAL, f"/config:{win_build_path(ini.name)}"],
        env=env(),
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        timeout=timeout,
    )
    for _ in range(90):
        if report.exists() and report.stat().st_size > 0:
            break
        time.sleep(1)
    if not report.exists() or report.stat().st_size == 0:
        raise RuntimeError(f"report missing: {report}")
    metrics = parse_report_metrics(read_report(report))
    report_text = read_report(report)
    plain = re.sub(r"<[^>]+>", " ", report_text).replace("\xa0", " ")
    plain = re.sub(r"\s+", " ", plain)
    bars_match = re.search(r"\bBars:\s*([\d ]+)", plain)
    period_match = re.search(r"\bPeriod:\s*([^I]{1,80})", plain)
    bars = int(bars_match.group(1).replace(" ", "")) if bars_match else 0
    period = period_match.group(1).strip() if period_match else ""
    if bars <= 0 or not period.startswith("M5"):
        raise RuntimeError(f"invalid MT5 report ({period=}, {bars=}): {report}")
    net = parse_first_number(metrics.get("Total Net Profit:", ""))
    trades = int(parse_first_number(metrics.get("Total Trades:", "")))
    pf = parse_first_number(metrics.get("Profit Factor:", ""))
    eqdd = metrics.get("Equity Drawdown Maximal:", "")
    baldd = metrics.get("Balance Drawdown Maximal:", "")
    return {
        "window": window,
        "from": from_date,
        "to": to_date,
        "report": str(report),
        "net": net,
        "net_pct": net / deposit * 100.0,
        "trades": trades,
        "profit_factor": pf,
        "equity_dd": eqdd,
        "balance_dd": baldd,
        "metrics": metrics,
    }


VARIANTS = [
    Variant("suis_unified_current", {}, "current SuisM5_v1 unified aggressive/frequency source default"),
    Variant(
        "suis_open_hours",
        {
            "SUIS_UseBuyCoreHours": False,
            "SUIS_BuySessionStartHour": 0,
            "SUIS_BuySessionEndHour": 23,
            "SUIS_BlockBuyBreakHours": "",
            "SUIS_BlockBuyPullbackHours": "",
            "SUIS_BlockBuyZoneHours": "",
            "SUIS_BlockBuyAddOnHours": "",
            "SUIS_OverextensionGuardBlocksZone": False,
        },
        "open all buy hours and restore zone availability",
    ),
    Variant(
        "suis_mixed_open",
        {
            "SUIS_EnableMixedMomentumEntries": True,
            "SUIS_H1ADXMin": 14.0,
            "SUIS_H1ADXStrongMin": 21.0,
            "SUIS_UseBuyCoreHours": False,
            "SUIS_BuySessionStartHour": 0,
            "SUIS_BuySessionEndHour": 23,
            "SUIS_BlockBuyBreakHours": "",
            "SUIS_BlockBuyPullbackHours": "",
            "SUIS_BlockBuyZoneHours": "",
            "SUIS_BlockBuyAddOnHours": "",
            "SUIS_OverextensionGuardBlocksZone": False,
            "SUIS_AllowBuyInMacroSideways": True,
            "SUIS_MacroSidewaysMinScore": 70,
            "SUIS_AllowBuyInMacroBear": True,
            "SUIS_MacroBearMinScore": 90,
            "SUIS_BlockAddOnOutsideMacroBull": False,
        },
        "mixed-regime open-hours profile with looser D1 macro buy escape",
    ),
    Variant(
        "suis_scalp_engines",
        {
            "SUIS_EnableMixedMomentumEntries": True,
            "SUIS_H1ADXMin": 14.0,
            "SUIS_H1ADXStrongMin": 21.0,
            "SUIS_UseBuyCoreHours": False,
            "SUIS_BuySessionStartHour": 0,
            "SUIS_BuySessionEndHour": 23,
            "SUIS_EnableImpulsePullbackEngine": True,
            "SUIS_EnableBullSubEngine": True,
            "SUIS_BullSubAllowWeakBull": True,
            "SUIS_BullSubOnlyOutsideCore": False,
            "SUIS_EnableBearSubEngine": True,
            "SUIS_BearSubAllowWeakBear": True,
            "SUIS_EnableSellAddOns": True,
            "SUIS_AddOnAllowWeakRegime": True,
            "SUIS_AddOnMaxPerSide": 2,
            "SUIS_AddOnMinProgressR": 0.35,
            "SUIS_BlockBuyBreakHours": "",
            "SUIS_BlockBuyPullbackHours": "",
            "SUIS_BlockBuyZoneHours": "",
            "SUIS_BlockBuyImpulseHours": "",
            "SUIS_BlockBuySubHours": "",
            "SUIS_BlockBuyAddOnHours": "",
            "SUIS_BlockSellBreakHours": "",
            "SUIS_BlockSellImpulseHours": "",
            "SUIS_BlockSellSubHours": "",
            "SUIS_BlockSellAddOnHours": "",
            "SUIS_OverextensionGuardBlocksZone": False,
            "SUIS_AllowBuyInMacroSideways": True,
            "SUIS_MacroSidewaysMinScore": 68,
            "SUIS_AllowBuyInMacroBear": True,
            "SUIS_MacroBearMinScore": 88,
            "SUIS_BlockAddOnOutsideMacroBull": False,
            "SUIS_MaxPositions": 10,
            "SUIS_WeakRegimeMaxPositions": 4,
        },
        "enable all existing M5 sub-engines to test frequency ceiling",
    ),
    Variant(
        "suis_score60_fast",
        {
            "SUIS_EnableMixedMomentumEntries": True,
            "SUIS_MinTradeScore": 60,
            "SUIS_H1ADXMin": 12.0,
            "SUIS_H1ADXStrongMin": 20.0,
            "SUIS_MinBodyRatio": 0.42,
            "SUIS_BuyMinBodyRatio": 0.44,
            "SUIS_WeakSellMinBodyRatio": 0.44,
            "SUIS_WeakBuyMinBodyRatio": 0.48,
            "SUIS_BuyMinBreakATR": 0.04,
            "SUIS_WeakBuyMinBreakATR": 0.06,
            "SUIS_MinBreakATR": 0.03,
            "SUIS_WeakSellMinBreakATR": 0.05,
            "SUIS_UseBuyCoreHours": False,
            "SUIS_BuySessionStartHour": 0,
            "SUIS_BuySessionEndHour": 23,
            "SUIS_EnableImpulsePullbackEngine": True,
            "SUIS_EnableBullSubEngine": True,
            "SUIS_BullSubAllowWeakBull": True,
            "SUIS_BullSubOnlyOutsideCore": False,
            "SUIS_EnableBearSubEngine": True,
            "SUIS_BearSubAllowWeakBear": True,
            "SUIS_EnableSellAddOns": True,
            "SUIS_AddOnAllowWeakRegime": True,
            "SUIS_AddOnMaxPerSide": 3,
            "SUIS_AddOnMinProgressR": 0.25,
            "SUIS_MaxPositions": 12,
            "SUIS_WeakRegimeMaxPositions": 5,
            "SUIS_MaxConsecutiveLosses": 4,
            "SUIS_LossCooldownMinutes": 60,
            "SUIS_BlockBuyBreakHours": "",
            "SUIS_BlockBuyPullbackHours": "",
            "SUIS_BlockBuyZoneHours": "",
            "SUIS_BlockBuyImpulseHours": "",
            "SUIS_BlockBuySubHours": "",
            "SUIS_BlockBuyAddOnHours": "",
            "SUIS_BlockSellBreakHours": "",
            "SUIS_BlockSellImpulseHours": "",
            "SUIS_BlockSellSubHours": "",
            "SUIS_BlockSellAddOnHours": "",
            "SUIS_OverextensionGuardBlocksZone": False,
            "SUIS_AllowBuyInMacroSideways": True,
            "SUIS_MacroSidewaysMinScore": 60,
            "SUIS_AllowBuyInMacroBear": True,
            "SUIS_MacroBearMinScore": 82,
            "SUIS_BlockAddOnOutsideMacroBull": False,
        },
        "aggressive lower-score fast scalp profile",
    ),
    Variant(
        "suis_score55_maxfreq",
        {
            "SUIS_EnableMixedMomentumEntries": True,
            "SUIS_MinTradeScore": 55,
            "SUIS_H1ADXMin": 10.0,
            "SUIS_H1ADXStrongMin": 18.0,
            "SUIS_MinBodyRatio": 0.38,
            "SUIS_BuyMinBodyRatio": 0.40,
            "SUIS_WeakSellMinBodyRatio": 0.40,
            "SUIS_WeakBuyMinBodyRatio": 0.44,
            "SUIS_BuyMinBreakATR": 0.02,
            "SUIS_WeakBuyMinBreakATR": 0.04,
            "SUIS_MinBreakATR": 0.02,
            "SUIS_WeakSellMinBreakATR": 0.04,
            "SUIS_UseBuyCoreHours": False,
            "SUIS_BuySessionStartHour": 0,
            "SUIS_BuySessionEndHour": 23,
            "SUIS_EnableBullSubEngine": True,
            "SUIS_BullSubAllowWeakBull": True,
            "SUIS_BullSubOnlyOutsideCore": False,
            "SUIS_EnableBearSubEngine": True,
            "SUIS_BearSubAllowWeakBear": True,
            "SUIS_EnableImpulsePullbackEngine": True,
            "SUIS_EnableSellAddOns": True,
            "SUIS_AddOnAllowWeakRegime": True,
            "SUIS_AddOnMaxPerSide": 4,
            "SUIS_AddOnMinProgressR": 0.15,
            "SUIS_MaxPositions": 16,
            "SUIS_WeakRegimeMaxPositions": 8,
            "SUIS_MaxConsecutiveLosses": 5,
            "SUIS_LossCooldownMinutes": 30,
            "SUIS_BlockBuyBreakHours": "",
            "SUIS_BlockBuyPullbackHours": "",
            "SUIS_BlockBuyZoneHours": "",
            "SUIS_BlockBuyImpulseHours": "",
            "SUIS_BlockBuySubHours": "",
            "SUIS_BlockBuyAddOnHours": "",
            "SUIS_BlockSellBreakHours": "",
            "SUIS_BlockSellZoneHours": "",
            "SUIS_BlockSellImpulseHours": "",
            "SUIS_BlockSellSubHours": "",
            "SUIS_BlockSellAddOnHours": "",
            "SUIS_OverextensionGuardBlocksZone": False,
            "SUIS_AllowBuyInMacroSideways": True,
            "SUIS_MacroSidewaysMinScore": 55,
            "SUIS_AllowBuyInMacroBear": True,
            "SUIS_MacroBearMinScore": 75,
            "SUIS_BlockAddOnOutsideMacroBull": False,
        },
        "maximum-frequency stress test; expected to reveal DD limits",
    ),
    Variant(
        "suis_sell_scalp_guarded",
        {
            "SUIS_EnableBearSubEngine": True,
            "SUIS_BearSubAllowWeakBear": True,
            "SUIS_BearSubRiskMultiplier": 0.20,
            "SUIS_BearSubRR": 1.20,
            "SUIS_EnableImpulsePullbackEngine": True,
            "SUIS_EnableBuyImpulsePullback": False,
            "SUIS_EnableSellImpulsePullback": True,
            "SUIS_ImpulseRiskMultiplier": 0.22,
            "SUIS_ImpulseRR": 1.10,
            "SUIS_EnableSellAddOns": True,
            "SUIS_AddOnAllowWeakRegime": True,
            "SUIS_AddOnMaxPerSide": 2,
            "SUIS_AddOnMinProgressR": 0.30,
            "SUIS_AddOnRiskMultiplier": 0.20,
            "SUIS_AddOnRR": 1.05,
            "SUIS_BlockSellImpulseHours": "",
            "SUIS_BlockSellSubHours": "",
            "SUIS_BlockSellAddOnHours": "",
            "SUIS_MaxPositions": 8,
            "SUIS_WeakRegimeMaxPositions": 3,
        },
        "base buy profile plus guarded sell sub/impulse/add-on scalps only",
    ),
    Variant(
        "suis_sell_scalp_scaled",
        {
            "SUIS_SellRiskMultiplier": 0.30,
            "SUIS_WeakSellRiskMultiplier": 0.15,
            "SUIS_EnableBearSubEngine": True,
            "SUIS_BearSubAllowWeakBear": True,
            "SUIS_BearSubRiskMultiplier": 0.28,
            "SUIS_BearSubRR": 1.20,
            "SUIS_EnableImpulsePullbackEngine": True,
            "SUIS_EnableBuyImpulsePullback": False,
            "SUIS_EnableSellImpulsePullback": True,
            "SUIS_ImpulseRiskMultiplier": 0.28,
            "SUIS_ImpulseRR": 1.10,
            "SUIS_EnableSellAddOns": True,
            "SUIS_AddOnAllowWeakRegime": True,
            "SUIS_AddOnMaxPerSide": 2,
            "SUIS_AddOnMinProgressR": 0.30,
            "SUIS_AddOnRiskMultiplier": 0.28,
            "SUIS_AddOnRR": 1.05,
            "SUIS_BlockSellImpulseHours": "",
            "SUIS_BlockSellSubHours": "",
            "SUIS_BlockSellAddOnHours": "",
            "SUIS_MaxPositions": 8,
            "SUIS_WeakRegimeMaxPositions": 3,
        },
        "same as guarded sell scalp but with stronger sell sizing",
    ),
    Variant(
        "suis_open_lowrisk",
        {
            "SUIS_BuyRiskMultiplier": 0.35,
            "SUIS_WeakBuyRiskMultiplier": 0.12,
            "SUIS_SellRiskMultiplier": 0.16,
            "SUIS_WeakSellRiskMultiplier": 0.08,
            "SUIS_ZoneRiskMultiplier": 0.45,
            "SUIS_AddOnRiskMultiplier": 0.18,
            "SUIS_UseBuyCoreHours": False,
            "SUIS_BuySessionStartHour": 0,
            "SUIS_BuySessionEndHour": 23,
            "SUIS_BlockBuyBreakHours": "",
            "SUIS_BlockBuyPullbackHours": "1,2,3,7,12,17,18",
            "SUIS_BlockBuyZoneHours": "",
            "SUIS_BlockBuyAddOnHours": "9,16,19",
            "SUIS_OverextensionGuardBlocksZone": False,
            "SUIS_MaxPositions": 10,
            "SUIS_WeakRegimeMaxPositions": 4,
        },
        "open hours but reduce per-engine risk and block worst pullback leaks",
    ),
    Variant(
        "suis_open_lowrisk_sellscalp",
        {
            "SUIS_BuyRiskMultiplier": 0.35,
            "SUIS_WeakBuyRiskMultiplier": 0.12,
            "SUIS_SellRiskMultiplier": 0.18,
            "SUIS_WeakSellRiskMultiplier": 0.08,
            "SUIS_ZoneRiskMultiplier": 0.45,
            "SUIS_AddOnRiskMultiplier": 0.18,
            "SUIS_UseBuyCoreHours": False,
            "SUIS_BuySessionStartHour": 0,
            "SUIS_BuySessionEndHour": 23,
            "SUIS_BlockBuyBreakHours": "",
            "SUIS_BlockBuyPullbackHours": "1,2,3,7,12,17,18",
            "SUIS_BlockBuyZoneHours": "",
            "SUIS_BlockBuyAddOnHours": "9,16,19",
            "SUIS_OverextensionGuardBlocksZone": False,
            "SUIS_EnableBearSubEngine": True,
            "SUIS_BearSubAllowWeakBear": True,
            "SUIS_BearSubRiskMultiplier": 0.22,
            "SUIS_BearSubRR": 1.20,
            "SUIS_EnableImpulsePullbackEngine": True,
            "SUIS_EnableBuyImpulsePullback": False,
            "SUIS_EnableSellImpulsePullback": True,
            "SUIS_ImpulseRiskMultiplier": 0.22,
            "SUIS_ImpulseRR": 1.10,
            "SUIS_EnableSellAddOns": True,
            "SUIS_AddOnAllowWeakRegime": True,
            "SUIS_AddOnMaxPerSide": 2,
            "SUIS_AddOnMinProgressR": 0.30,
            "SUIS_BlockSellImpulseHours": "",
            "SUIS_BlockSellSubHours": "",
            "SUIS_BlockSellAddOnHours": "",
            "SUIS_MaxPositions": 10,
            "SUIS_WeakRegimeMaxPositions": 4,
        },
        "low-risk open buy profile plus sell scalp engines",
    ),
    Variant(
        "suis_open_filtered",
        {
            "SUIS_BuyRiskMultiplier": 0.30,
            "SUIS_WeakBuyRiskMultiplier": 0.10,
            "SUIS_SellRiskMultiplier": 0.16,
            "SUIS_WeakSellRiskMultiplier": 0.08,
            "SUIS_ZoneRiskMultiplier": 0.35,
            "SUIS_EnableBuyAddOns": False,
            "SUIS_ZoneAllowWeakRegime": False,
            "SUIS_UseBuyCoreHours": False,
            "SUIS_BuySessionStartHour": 0,
            "SUIS_BuySessionEndHour": 23,
            "SUIS_BlockBuyBreakHours": "5",
            "SUIS_BlockBuyPullbackHours": "1,2,3,5,7,8,9,12,14,17,18",
            "SUIS_BlockBuyZoneHours": "",
            "SUIS_OverextensionGuardBlocksZone": False,
            "SUIS_MaxPositions": 8,
            "SUIS_WeakRegimeMaxPositions": 3,
        },
        "filter open-hours buy leaks: no weak zones, no buy add-ons, block bad PB/BO hours",
    ),
    Variant(
        "suis_open_filtered_high",
        {
            "SUIS_BuyRiskMultiplier": 0.35,
            "SUIS_WeakBuyRiskMultiplier": 0.12,
            "SUIS_SellRiskMultiplier": 0.18,
            "SUIS_WeakSellRiskMultiplier": 0.09,
            "SUIS_ZoneRiskMultiplier": 0.40,
            "SUIS_EnableBuyAddOns": False,
            "SUIS_ZoneAllowWeakRegime": False,
            "SUIS_UseBuyCoreHours": False,
            "SUIS_BuySessionStartHour": 0,
            "SUIS_BuySessionEndHour": 23,
            "SUIS_BlockBuyBreakHours": "5",
            "SUIS_BlockBuyPullbackHours": "1,2,3,5,7,8,9,12,14,17,18",
            "SUIS_BlockBuyZoneHours": "",
            "SUIS_OverextensionGuardBlocksZone": False,
            "SUIS_MaxPositions": 8,
            "SUIS_WeakRegimeMaxPositions": 3,
        },
        "same filtered logic with more aggressive size",
    ),
    Variant(
        "suis_open_filtered_equity30",
        {
            "SUIS_BuyRiskMultiplier": 0.35,
            "SUIS_WeakBuyRiskMultiplier": 0.12,
            "SUIS_SellRiskMultiplier": 0.18,
            "SUIS_WeakSellRiskMultiplier": 0.09,
            "SUIS_ZoneRiskMultiplier": 0.40,
            "SUIS_EnableBuyAddOns": False,
            "SUIS_ZoneAllowWeakRegime": False,
            "SUIS_UseBuyCoreHours": False,
            "SUIS_BuySessionStartHour": 0,
            "SUIS_BuySessionEndHour": 23,
            "SUIS_BlockBuyBreakHours": "5",
            "SUIS_BlockBuyPullbackHours": "1,2,3,5,7,8,9,12,14,17,18",
            "SUIS_BlockBuyZoneHours": "",
            "SUIS_OverextensionGuardBlocksZone": False,
            "SUIS_MaxPositions": 8,
            "SUIS_WeakRegimeMaxPositions": 3,
            "SUIS_MaxEquityDrawdownPct": 30.00,
            "SUIS_ClosePositionsOnSafetyStop": True,
        },
        "filtered high profile with account equity circuit breaker at 30%",
    ),
    Variant(
        "suis_open_filtered_micro",
        {
            "SUIS_BuyRiskMultiplier": 0.22,
            "SUIS_WeakBuyRiskMultiplier": 0.08,
            "SUIS_SellRiskMultiplier": 0.12,
            "SUIS_WeakSellRiskMultiplier": 0.06,
            "SUIS_ZoneRiskMultiplier": 0.28,
            "SUIS_EnableBuyAddOns": False,
            "SUIS_ZoneAllowWeakRegime": False,
            "SUIS_UseBuyCoreHours": False,
            "SUIS_BuySessionStartHour": 0,
            "SUIS_BuySessionEndHour": 23,
            "SUIS_BlockBuyBreakHours": "5",
            "SUIS_BlockBuyPullbackHours": "1,2,3,5,7,8,9,12,14,17,18",
            "SUIS_BlockBuyZoneHours": "",
            "SUIS_OverextensionGuardBlocksZone": False,
            "SUIS_MaxPositions": 8,
            "SUIS_WeakRegimeMaxPositions": 3,
        },
        "filtered open-hours profile with lower per-trade risk for DD control",
    ),
    Variant(
        "suis_open_filtered_tight",
        {
            "SUIS_BuyRiskMultiplier": 0.30,
            "SUIS_WeakBuyRiskMultiplier": 0.10,
            "SUIS_SellRiskMultiplier": 0.16,
            "SUIS_WeakSellRiskMultiplier": 0.08,
            "SUIS_ZoneRiskMultiplier": 0.35,
            "SUIS_EnableBuyAddOns": False,
            "SUIS_ZoneAllowWeakRegime": False,
            "SUIS_UseBuyCoreHours": False,
            "SUIS_BuySessionStartHour": 0,
            "SUIS_BuySessionEndHour": 23,
            "SUIS_BlockBuyBreakHours": "1,2,4,5,7,10,20",
            "SUIS_BlockBuyPullbackHours": "1,2,3,5,7,8,9,10,12,14,16,17,18",
            "SUIS_BlockBuyZoneHours": "7,10,13,15,20",
            "SUIS_OverextensionGuardBlocksZone": False,
            "SUIS_MaxPositions": 8,
            "SUIS_WeakRegimeMaxPositions": 3,
        },
        "tight hour leak map on top of filtered profile",
    ),
    Variant(
        "suis_open_filtered_tight_sellscalp",
        {
            "SUIS_BuyRiskMultiplier": 0.30,
            "SUIS_WeakBuyRiskMultiplier": 0.10,
            "SUIS_SellRiskMultiplier": 0.16,
            "SUIS_WeakSellRiskMultiplier": 0.08,
            "SUIS_ZoneRiskMultiplier": 0.35,
            "SUIS_EnableBuyAddOns": False,
            "SUIS_ZoneAllowWeakRegime": False,
            "SUIS_UseBuyCoreHours": False,
            "SUIS_BuySessionStartHour": 0,
            "SUIS_BuySessionEndHour": 23,
            "SUIS_BlockBuyBreakHours": "1,2,4,5,7,10,20",
            "SUIS_BlockBuyPullbackHours": "1,2,3,5,7,8,9,10,12,14,16,17,18",
            "SUIS_BlockBuyZoneHours": "7,10,13,15,20",
            "SUIS_OverextensionGuardBlocksZone": False,
            "SUIS_EnableBearSubEngine": True,
            "SUIS_BearSubAllowWeakBear": True,
            "SUIS_BearSubRiskMultiplier": 0.16,
            "SUIS_BearSubRR": 1.20,
            "SUIS_EnableImpulsePullbackEngine": True,
            "SUIS_EnableBuyImpulsePullback": False,
            "SUIS_EnableSellImpulsePullback": True,
            "SUIS_ImpulseRiskMultiplier": 0.16,
            "SUIS_ImpulseRR": 1.10,
            "SUIS_EnableSellAddOns": True,
            "SUIS_AddOnAllowWeakRegime": True,
            "SUIS_AddOnMaxPerSide": 2,
            "SUIS_AddOnMinProgressR": 0.30,
            "SUIS_AddOnRiskMultiplier": 0.16,
            "SUIS_AddOnRR": 1.05,
            "SUIS_BlockSellImpulseHours": "",
            "SUIS_BlockSellSubHours": "",
            "SUIS_BlockSellAddOnHours": "",
            "SUIS_MaxPositions": 8,
            "SUIS_WeakRegimeMaxPositions": 3,
        },
        "tight leak map plus low-risk sell scalp engines",
    ),
    Variant(
        "diag_status",
        {
            "SUIS_LogStatusOnNewBar": True,
            "SUIS_StatusEveryBars": 1,
            "SUIS_LogRejectedSignals": True,
            "SUIS_MinRejectedScoreToLog": 40,
        },
        "baseline with verbose status/reject logs",
    ),
    Variant(
        "old_live303",
        {
            "SUIS_EnableSells": False,
            "SUIS_EnableBearSafeMode": False,
            "SUIS_BearSafeStrongMinScore": 60,
            "SUIS_BearSafeWeakMinScore": 72,
            "SUIS_BearSafeWeakMinBodyRatio": 0.50,
            "SUIS_BlockSellBreakHours": "",
            "SUIS_BlockSellZoneHours": "",
            "SUIS_SellRiskMultiplier": 1.00,
            "SUIS_WeakSellRiskMultiplier": 0.55,
        },
        "previous buy-only locked live profile v3.03",
    ),
    Variant(
        "old_live304",
        {
            "SUIS_SellSessionStartHour": 8,
            "SUIS_SellSessionEndHour": 20,
            "SUIS_BlockSellBreakHours": "14,19",
            "SUIS_SellRiskMultiplier": 0.20,
            "SUIS_WeakSellRiskMultiplier": 0.10,
        },
        "previous locked live profile v3.04",
    ),
    Variant(
        "old_live305",
        {
            "SUIS_EnableMacroRegimeSwitch": False,
            "SUIS_AllowBuyInMacroBear": False,
            "SUIS_MacroBearMinScore": 94,
        },
        "previous locked live profile v3.05 before D1 macro guard",
    ),
    Variant(
        "old_live306",
        {
            "SUIS_EnableStructuralPriceGate": False,
        },
        "previous locked live profile v3.06 before structural price gate",
    ),
    Variant("suis_v1_legacy", {}, "current locked live profile Suis v1 legacy"),
    Variant(
        "structural_price_gate",
        {
            "SUIS_EnableStructuralPriceGate": True,
            "SUIS_MinD1CloseForTrading": 2500.00,
        },
        "v3.06 plus D1 close structural high-price regime gate",
    ),
    Variant(
        "macro_buy_guard",
        {
            "SUIS_EnableMacroRegimeSwitch": True,
        },
        "enable D1 macro regime gate for buy engines",
    ),
    Variant(
        "macro_strict_bull",
        {
            "SUIS_EnableMacroRegimeSwitch": True,
            "SUIS_AllowStrongBullBuyInMacroSideways": False,
        },
        "only allow buys when D1 macro is bullish",
    ),
    Variant(
        "engine_fail_guard",
        {
            "SUIS_EnableEngineFailGuard": True,
        },
        "pause high-score buy zone/pullback after daily losses",
    ),
    Variant(
        "fast_fail_guard",
        {
            "SUIS_FastFailBuyGuard": True,
        },
        "close pullback buys early when they lose M5 EMA momentum",
    ),
    Variant(
        "macro_fast_fail",
        {
            "SUIS_EnableMacroRegimeSwitch": True,
            "SUIS_FastFailBuyGuard": True,
        },
        "D1 macro buy gate plus pullback fast-fail exit",
    ),
    Variant(
        "macro_no_addon",
        {
            "SUIS_EnableMacroRegimeSwitch": True,
            "SUIS_EnableBuyAddOns": False,
        },
        "macro gate and disable buy add-ons",
    ),
    Variant(
        "macro_no_pb",
        {
            "SUIS_EnableMacroRegimeSwitch": True,
            "SUIS_AllowPullbackBuys": False,
        },
        "macro gate and disable base buy pullback engine",
    ),
    Variant(
        "macro_bear94",
        {
            "SUIS_EnableMacroRegimeSwitch": True,
            "SUIS_AllowBuyInMacroBear": True,
            "SUIS_MacroBearMinScore": 94,
        },
        "macro gate but allow emergency strong-H1/H4 buys in D1 bear at score 94+",
    ),
    Variant(
        "macro_bear97",
        {
            "SUIS_EnableMacroRegimeSwitch": True,
            "SUIS_AllowBuyInMacroBear": True,
            "SUIS_MacroBearMinScore": 97,
        },
        "macro gate but allow only elite score 97+ buys in D1 bear",
    ),
    Variant(
        "macro_addon_free",
        {
            "SUIS_EnableMacroRegimeSwitch": True,
            "SUIS_BlockAddOnOutsideMacroBull": False,
        },
        "macro gate but allow buy add-ons outside D1 bull",
    ),
    Variant(
        "macro_bear97_addon_free",
        {
            "SUIS_EnableMacroRegimeSwitch": True,
            "SUIS_AllowBuyInMacroBear": True,
            "SUIS_MacroBearMinScore": 97,
            "SUIS_BlockAddOnOutsideMacroBull": False,
        },
        "macro gate with elite D1-bear buy escape and add-ons allowed",
    ),
    Variant(
        "unblock_hours",
        {
            "SUIS_BlockBuyBreakHours": "",
            "SUIS_BlockBuyPullbackHours": "",
            "SUIS_BlockBuyZoneHours": "",
            "SUIS_BlockBuyAddOnHours": "",
        },
        "remove promoted hour blocks only",
    ),
    Variant(
        "core_wide",
        {
            "SUIS_UseBuyCoreHours": False,
            "SUIS_BlockBuyBreakHours": "",
            "SUIS_BlockBuyPullbackHours": "",
            "SUIS_BlockBuyZoneHours": "",
            "SUIS_BlockBuyAddOnHours": "",
        },
        "allow all buy-session hours",
    ),
    Variant(
        "session_24h",
        {
            "SUIS_UseBuyCoreHours": False,
            "SUIS_BuySessionStartHour": 0,
            "SUIS_BuySessionEndHour": 23,
            "SUIS_BlockBuyBreakHours": "",
            "SUIS_BlockBuyPullbackHours": "",
            "SUIS_BlockBuyZoneHours": "",
            "SUIS_BlockBuyAddOnHours": "",
        },
        "allow all hours for buy engines",
    ),
    Variant(
        "adx_relax",
        {
            "SUIS_H1ADXMin": 16.0,
            "SUIS_H1ADXStrongMin": 22.0,
            "SUIS_UseBuyCoreHours": False,
            "SUIS_BlockBuyBreakHours": "",
            "SUIS_BlockBuyPullbackHours": "",
            "SUIS_BlockBuyZoneHours": "",
            "SUIS_BlockBuyAddOnHours": "",
        },
        "relax H1 ADX gate and hours",
    ),
    Variant(
        "mixed_relax",
        {
            "SUIS_EnableMixedMomentumEntries": True,
            "SUIS_H1ADXMin": 16.0,
            "SUIS_H1ADXStrongMin": 22.0,
            "SUIS_UseBuyCoreHours": False,
            "SUIS_BlockBuyBreakHours": "",
            "SUIS_BlockBuyPullbackHours": "",
            "SUIS_BlockBuyZoneHours": "",
            "SUIS_BlockBuyAddOnHours": "",
        },
        "allow mixed H1/H4 with H1 bias",
    ),
    Variant(
        "zone_open",
        {
            "SUIS_BlockBuyZoneHours": "",
            "SUIS_OverextensionGuardBlocksZone": False,
        },
        "make zone retests available again",
    ),
    Variant(
        "impulse_on",
        {
            "SUIS_EnableImpulsePullbackEngine": True,
            "SUIS_ImpulseRiskMultiplier": 0.25,
            "SUIS_BlockBuyImpulseHours": "",
        },
        "enable small impulse pullback entries",
    ),
    Variant(
        "bullsub_on",
        {
            "SUIS_EnableBullSubEngine": True,
            "SUIS_BullSubAllowWeakBull": True,
            "SUIS_BullSubOnlyOutsideCore": False,
            "SUIS_BullSubRiskMultiplier": 0.25,
        },
        "enable compression breakout sub-engine",
    ),
    Variant(
        "scalp_all",
        {
            "SUIS_EnableMixedMomentumEntries": True,
            "SUIS_H1ADXMin": 14.0,
            "SUIS_H1ADXStrongMin": 21.0,
            "SUIS_UseBuyCoreHours": False,
            "SUIS_BuySessionStartHour": 0,
            "SUIS_BuySessionEndHour": 23,
            "SUIS_EnableImpulsePullbackEngine": True,
            "SUIS_EnableBullSubEngine": True,
            "SUIS_BullSubAllowWeakBull": True,
            "SUIS_BullSubOnlyOutsideCore": False,
            "SUIS_BlockBuyBreakHours": "",
            "SUIS_BlockBuyPullbackHours": "",
            "SUIS_BlockBuyZoneHours": "",
            "SUIS_BlockBuyAddOnHours": "",
            "SUIS_OverextensionGuardBlocksZone": False,
        },
        "aggressive buy-only frequency test",
    ),
    Variant(
        "mixed_hold",
        {
            "SUIS_EnableMixedMomentumEntries": True,
            "SUIS_CloseOnRegimeFlip": False,
            "SUIS_H1ADXMin": 16.0,
            "SUIS_H1ADXStrongMin": 22.0,
            "SUIS_UseBuyCoreHours": False,
            "SUIS_BuySessionStartHour": 0,
            "SUIS_BuySessionEndHour": 23,
            "SUIS_BlockBuyBreakHours": "",
            "SUIS_BlockBuyPullbackHours": "",
            "SUIS_BlockBuyZoneHours": "",
            "SUIS_BlockBuyAddOnHours": "",
        },
        "mixed regime entries without instant regime-flip close",
    ),
    Variant(
        "scalp_hold",
        {
            "SUIS_EnableMixedMomentumEntries": True,
            "SUIS_CloseOnRegimeFlip": False,
            "SUIS_H1ADXMin": 14.0,
            "SUIS_H1ADXStrongMin": 21.0,
            "SUIS_UseBuyCoreHours": False,
            "SUIS_BuySessionStartHour": 0,
            "SUIS_BuySessionEndHour": 23,
            "SUIS_EnableImpulsePullbackEngine": True,
            "SUIS_EnableBullSubEngine": True,
            "SUIS_BullSubAllowWeakBull": True,
            "SUIS_BullSubOnlyOutsideCore": False,
            "SUIS_BlockBuyBreakHours": "",
            "SUIS_BlockBuyPullbackHours": "",
            "SUIS_BlockBuyZoneHours": "",
            "SUIS_BlockBuyAddOnHours": "",
            "SUIS_OverextensionGuardBlocksZone": False,
        },
        "scalp_all with regime-flip close disabled",
    ),
    Variant(
        "scalp_hold_profit_time",
        {
            "SUIS_EnableMixedMomentumEntries": True,
            "SUIS_CloseOnRegimeFlip": False,
            "SUIS_TimeCloseProfitOnly": True,
            "SUIS_BuyBreakTimeCloseProfitOnly": True,
            "SUIS_BuyZoneTimeCloseProfitOnly": True,
            "SUIS_BuyAddOnTimeCloseProfitOnly": True,
            "SUIS_H1ADXMin": 14.0,
            "SUIS_H1ADXStrongMin": 21.0,
            "SUIS_UseBuyCoreHours": False,
            "SUIS_BuySessionStartHour": 0,
            "SUIS_BuySessionEndHour": 23,
            "SUIS_EnableImpulsePullbackEngine": True,
            "SUIS_EnableBullSubEngine": True,
            "SUIS_BullSubAllowWeakBull": True,
            "SUIS_BullSubOnlyOutsideCore": False,
            "SUIS_BlockBuyBreakHours": "",
            "SUIS_BlockBuyPullbackHours": "",
            "SUIS_BlockBuyZoneHours": "",
            "SUIS_BlockBuyAddOnHours": "",
            "SUIS_OverextensionGuardBlocksZone": False,
        },
        "scalp_hold plus time-close only when profitable",
    ),
    Variant(
        "dual_safe",
        {
            "SUIS_EnableSells": True,
            "SUIS_EnableBearSafeMode": True,
            "SUIS_BearSafeStrongMinScore": 72,
            "SUIS_BearSafeWeakMinScore": 82,
            "SUIS_BearSafeWeakMinBodyRatio": 0.58,
            "SUIS_UseBuyCoreHours": False,
            "SUIS_BlockBuyBreakHours": "",
            "SUIS_BlockBuyPullbackHours": "",
            "SUIS_BlockBuyZoneHours": "",
            "SUIS_BlockBuyAddOnHours": "",
        },
        "reintroduce guarded sell path",
    ),
    Variant(
        "dual_safe_hold",
        {
            "SUIS_EnableSells": True,
            "SUIS_EnableMixedMomentumEntries": True,
            "SUIS_CloseOnRegimeFlip": False,
            "SUIS_EnableBearSafeMode": True,
            "SUIS_BearSafeStrongMinScore": 72,
            "SUIS_BearSafeWeakMinScore": 82,
            "SUIS_BearSafeWeakMinBodyRatio": 0.58,
            "SUIS_UseBuyCoreHours": False,
            "SUIS_BuySessionStartHour": 0,
            "SUIS_BuySessionEndHour": 23,
            "SUIS_BlockBuyBreakHours": "",
            "SUIS_BlockBuyPullbackHours": "",
            "SUIS_BlockBuyZoneHours": "",
            "SUIS_BlockBuyAddOnHours": "",
        },
        "guarded sell plus mixed entries without instant close",
    ),
    Variant(
        "sell_break_filtered",
        {
            "SUIS_EnableSells": True,
            "SUIS_EnableBearSafeMode": True,
            "SUIS_BearSafeStrongMinScore": 72,
            "SUIS_BearSafeWeakMinScore": 82,
            "SUIS_BearSafeWeakMinBodyRatio": 0.58,
            "SUIS_BlockSellBreakHours": "14,19",
            "SUIS_BlockSellZoneHours": "0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23",
            "SUIS_SellRiskMultiplier": 0.55,
            "SUIS_WeakSellRiskMultiplier": 0.25,
        },
        "sell breakout only, block recent leak hours and sell zone",
    ),
    Variant(
        "sell_break_midday",
        {
            "SUIS_EnableSells": True,
            "SUIS_EnableBearSafeMode": True,
            "SUIS_BearSafeStrongMinScore": 72,
            "SUIS_BearSafeWeakMinScore": 82,
            "SUIS_BearSafeWeakMinBodyRatio": 0.58,
            "SUIS_BlockSellBreakHours": "0,1,2,3,4,5,6,7,8,9,10,12,14,15,16,17,18,19,20,21,22,23",
            "SUIS_BlockSellZoneHours": "0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23",
            "SUIS_SellRiskMultiplier": 0.55,
            "SUIS_WeakSellRiskMultiplier": 0.25,
        },
        "sell breakout only at hours 11 and 13",
    ),
    Variant(
        "sell_break_tiny",
        {
            "SUIS_EnableSells": True,
            "SUIS_EnableBearSafeMode": True,
            "SUIS_BearSafeStrongMinScore": 72,
            "SUIS_BearSafeWeakMinScore": 82,
            "SUIS_BearSafeWeakMinBodyRatio": 0.58,
            "SUIS_BlockSellBreakHours": "14,19",
            "SUIS_BlockSellZoneHours": "0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23",
            "SUIS_SellRiskMultiplier": 0.30,
            "SUIS_WeakSellRiskMultiplier": 0.15,
        },
        "same filtered sell path with smaller risk",
    ),
    Variant(
        "sell_break_micro",
        {
            "SUIS_EnableSells": True,
            "SUIS_EnableBearSafeMode": True,
            "SUIS_BearSafeStrongMinScore": 72,
            "SUIS_BearSafeWeakMinScore": 82,
            "SUIS_BearSafeWeakMinBodyRatio": 0.58,
            "SUIS_BlockSellBreakHours": "14,19",
            "SUIS_BlockSellZoneHours": "0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23",
            "SUIS_SellRiskMultiplier": 0.20,
            "SUIS_WeakSellRiskMultiplier": 0.10,
        },
        "filtered sell path with minimal risk",
    ),
    Variant(
        "sell_break_24h_micro",
        {
            "SUIS_EnableSells": True,
            "SUIS_SellSessionStartHour": 0,
            "SUIS_SellSessionEndHour": 23,
            "SUIS_EnableBearSafeMode": True,
            "SUIS_BearSafeStrongMinScore": 72,
            "SUIS_BearSafeWeakMinScore": 82,
            "SUIS_BearSafeWeakMinBodyRatio": 0.58,
            "SUIS_BlockSellBreakHours": "14,19",
            "SUIS_BlockSellZoneHours": "0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23",
            "SUIS_SellRiskMultiplier": 0.20,
            "SUIS_WeakSellRiskMultiplier": 0.10,
        },
        "current sell-break filter but allow 24h sell session",
    ),
    Variant(
        "sell_zone_micro",
        {
            "SUIS_EnableSells": True,
            "SUIS_EnableBearSafeMode": True,
            "SUIS_BearSafeStrongMinScore": 78,
            "SUIS_BearSafeWeakMinScore": 90,
            "SUIS_BearSafeWeakMinBodyRatio": 0.62,
            "SUIS_BearSafeBlockWeakZone": True,
            "SUIS_BlockSellBreakHours": "14,19",
            "SUIS_BlockSellZoneHours": "0,1,2,3,4,5,6,7,8,9,14,15,16,17,18,19,20,21,22,23",
            "SUIS_SellRiskMultiplier": 0.20,
            "SUIS_WeakSellRiskMultiplier": 0.05,
        },
        "allow only strict strong sell-zone hours 10-13 with micro risk",
    ),
    Variant(
        "sell_impulse_micro",
        {
            "SUIS_EnableSells": True,
            "SUIS_EnableBearSafeMode": True,
            "SUIS_BearSafeStrongMinScore": 72,
            "SUIS_BearSafeWeakMinScore": 84,
            "SUIS_BearSafeWeakMinBodyRatio": 0.60,
            "SUIS_EnableImpulsePullbackEngine": True,
            "SUIS_ImpulseRiskMultiplier": 0.20,
            "SUIS_ImpulseRR": 1.10,
            "SUIS_BlockSellBreakHours": "14,19",
            "SUIS_BlockSellZoneHours": "0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23",
            "SUIS_SellRiskMultiplier": 0.20,
            "SUIS_WeakSellRiskMultiplier": 0.10,
        },
        "add tiny sell impulse pullback engine",
    ),
    Variant(
        "sell_bearsub_micro",
        {
            "SUIS_EnableSells": True,
            "SUIS_EnableBearSafeMode": True,
            "SUIS_BearSafeStrongMinScore": 72,
            "SUIS_BearSafeWeakMinScore": 86,
            "SUIS_BearSafeWeakMinBodyRatio": 0.60,
            "SUIS_EnableBearSubEngine": True,
            "SUIS_BearSubAllowWeakBear": False,
            "SUIS_BearSubRiskMultiplier": 0.12,
            "SUIS_BearSubRR": 1.20,
            "SUIS_BlockSellBreakHours": "14,19",
            "SUIS_BlockSellZoneHours": "0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23",
            "SUIS_SellRiskMultiplier": 0.20,
            "SUIS_WeakSellRiskMultiplier": 0.10,
        },
        "add strong-bear compression breakdown with tiny risk",
    ),
    Variant(
        "sell_combo_micro",
        {
            "SUIS_EnableSells": True,
            "SUIS_SellSessionStartHour": 0,
            "SUIS_SellSessionEndHour": 23,
            "SUIS_EnableBearSafeMode": True,
            "SUIS_BearSafeStrongMinScore": 76,
            "SUIS_BearSafeWeakMinScore": 88,
            "SUIS_BearSafeWeakMinBodyRatio": 0.62,
            "SUIS_BearSafeBlockWeakZone": True,
            "SUIS_EnableImpulsePullbackEngine": True,
            "SUIS_ImpulseRiskMultiplier": 0.18,
            "SUIS_ImpulseRR": 1.10,
            "SUIS_EnableBearSubEngine": True,
            "SUIS_BearSubAllowWeakBear": False,
            "SUIS_BearSubRiskMultiplier": 0.10,
            "SUIS_BearSubRR": 1.15,
            "SUIS_BlockSellBreakHours": "14,19",
            "SUIS_BlockSellZoneHours": "0,1,2,3,4,5,6,7,8,9,14,15,16,17,18,19,20,21,22,23",
            "SUIS_SellRiskMultiplier": 0.20,
            "SUIS_WeakSellRiskMultiplier": 0.05,
        },
        "24h break plus strict sell-zone/impulse/bearsub micro blend",
    ),
    Variant(
        "sell24_block_leaks",
        {
            "SUIS_EnableSells": True,
            "SUIS_SellSessionStartHour": 0,
            "SUIS_SellSessionEndHour": 23,
            "SUIS_EnableBearSafeMode": True,
            "SUIS_BearSafeStrongMinScore": 72,
            "SUIS_BearSafeWeakMinScore": 82,
            "SUIS_BearSafeWeakMinBodyRatio": 0.58,
            "SUIS_BlockSellBreakHours": "5,6,14,16,19,20",
            "SUIS_BlockSellZoneHours": "0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23",
            "SUIS_SellRiskMultiplier": 0.20,
            "SUIS_WeakSellRiskMultiplier": 0.10,
        },
        "24h sell-break with proven bad sell hours blocked",
    ),
    Variant(
        "sell24_buy_leak_blocks",
        {
            "SUIS_EnableSells": True,
            "SUIS_SellSessionStartHour": 0,
            "SUIS_SellSessionEndHour": 23,
            "SUIS_EnableBearSafeMode": True,
            "SUIS_BearSafeStrongMinScore": 72,
            "SUIS_BearSafeWeakMinScore": 82,
            "SUIS_BearSafeWeakMinBodyRatio": 0.58,
            "SUIS_BlockSellBreakHours": "5,6,14,16,19,20",
            "SUIS_BlockSellZoneHours": "0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23",
            "SUIS_BlockBuyPullbackHours": "5,16",
            "SUIS_BlockBuyAddOnHours": "9,16,19",
            "SUIS_SellRiskMultiplier": 0.20,
            "SUIS_WeakSellRiskMultiplier": 0.10,
        },
        "24h sell-break plus block worst buy pullback/add-on leak hours",
    ),
    Variant(
        "sell24_buy_leak_risk25",
        {
            "SUIS_EnableSells": True,
            "SUIS_SellSessionStartHour": 0,
            "SUIS_SellSessionEndHour": 23,
            "SUIS_EnableBearSafeMode": True,
            "SUIS_BearSafeStrongMinScore": 72,
            "SUIS_BearSafeWeakMinScore": 82,
            "SUIS_BearSafeWeakMinBodyRatio": 0.58,
            "SUIS_BlockSellBreakHours": "5,6,14,16,19,20",
            "SUIS_BlockSellZoneHours": "0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23",
            "SUIS_BlockBuyPullbackHours": "5,16",
            "SUIS_BlockBuyAddOnHours": "9,16,19",
            "SUIS_SellRiskMultiplier": 0.25,
            "SUIS_WeakSellRiskMultiplier": 0.12,
        },
        "same leak blocks with slightly higher sell risk",
    ),
    Variant(
        "sell24_block_leaks_risk22",
        {
            "SUIS_EnableSells": True,
            "SUIS_SellSessionStartHour": 0,
            "SUIS_SellSessionEndHour": 23,
            "SUIS_EnableBearSafeMode": True,
            "SUIS_BearSafeStrongMinScore": 72,
            "SUIS_BearSafeWeakMinScore": 82,
            "SUIS_BearSafeWeakMinBodyRatio": 0.58,
            "SUIS_BlockSellBreakHours": "5,6,14,16,19,20",
            "SUIS_BlockSellZoneHours": "0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23",
            "SUIS_SellRiskMultiplier": 0.22,
            "SUIS_WeakSellRiskMultiplier": 0.11,
        },
        "leak-blocked 24h sell-break with 0.22x sell risk",
    ),
    Variant(
        "sell24_block_leaks_risk25",
        {
            "SUIS_EnableSells": True,
            "SUIS_SellSessionStartHour": 0,
            "SUIS_SellSessionEndHour": 23,
            "SUIS_EnableBearSafeMode": True,
            "SUIS_BearSafeStrongMinScore": 72,
            "SUIS_BearSafeWeakMinScore": 82,
            "SUIS_BearSafeWeakMinBodyRatio": 0.58,
            "SUIS_BlockSellBreakHours": "5,6,14,16,19,20",
            "SUIS_BlockSellZoneHours": "0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23",
            "SUIS_SellRiskMultiplier": 0.25,
            "SUIS_WeakSellRiskMultiplier": 0.12,
        },
        "leak-blocked 24h sell-break with 0.25x sell risk",
    ),
    Variant(
        "sell24_block_leaks_risk30",
        {
            "SUIS_EnableSells": True,
            "SUIS_SellSessionStartHour": 0,
            "SUIS_SellSessionEndHour": 23,
            "SUIS_EnableBearSafeMode": True,
            "SUIS_BearSafeStrongMinScore": 72,
            "SUIS_BearSafeWeakMinScore": 82,
            "SUIS_BearSafeWeakMinBodyRatio": 0.58,
            "SUIS_BlockSellBreakHours": "5,6,14,16,19,20",
            "SUIS_BlockSellZoneHours": "0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23",
            "SUIS_SellRiskMultiplier": 0.30,
            "SUIS_WeakSellRiskMultiplier": 0.15,
        },
        "leak-blocked 24h sell-break with 0.30x sell risk",
    ),
]


def summarize(results: list[dict[str, object]]) -> str:
    lines = [
        "# Suis Frequency Iteration",
        "",
        "| variant | note | window | net % | trades | PF | EqDD |",
        "| --- | --- | --- | ---: | ---: | ---: | --- |",
    ]
    notes = {variant.name: variant.note for variant in VARIANTS}
    for row in sorted(results, key=lambda item: (str(item["window"]), -float(item["net_pct"]))):
        lines.append(
            f"| `{row['variant']}` | {notes.get(str(row['variant']), '')} | `{row['window']}` | "
            f"{float(row['net_pct']):.2f}% | {int(row['trades'])} | {float(row['profit_factor']):.2f} | {row['equity_dd']} |"
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--from-date", default="2026.04.27")
    parser.add_argument("--to-date", default="2026.05.05")
    parser.add_argument("--deposit", type=int, default=100)
    parser.add_argument("--leverage", default="1:100")
    parser.add_argument("--timeout", type=int, default=240)
    parser.add_argument("--ytd", action="store_true")
    parser.add_argument("--windows", default="")
    parser.add_argument("--variant", action="append")
    args = parser.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    selected = VARIANTS
    if args.variant:
        wanted = set(args.variant)
        selected = [variant for variant in VARIANTS if variant.name in wanted]
        missing = wanted - {variant.name for variant in selected}
        if missing:
            raise SystemExit(f"unknown variants: {', '.join(sorted(missing))}")

    source_text = SOURCE.read_text()
    results: list[dict[str, object]] = []
    if args.windows:
        requested = [item.strip() for item in args.windows.split(",") if item.strip()]
        valid = {"recent", "ytd", "full", "all2023"}
        unknown = set(requested) - valid
        if unknown:
            raise SystemExit(f"unknown windows: {', '.join(sorted(unknown))}")
        windows = []
        for item in requested:
            if item == "recent":
                windows.append(("recent", args.from_date, args.to_date))
            elif item == "ytd":
                windows.append(("ytd", "2026.01.01", args.to_date))
            elif item == "full":
                windows.append(("full", "2025.01.01", args.to_date))
            elif item == "all2023":
                windows.append(("all2023", "2023.01.01", args.to_date))
    else:
        windows = [("recent", args.from_date, args.to_date)]
    if args.ytd and not args.windows:
        windows.append(("ytd", "2026.01.01", args.to_date))
        windows.append(("full", "2025.01.01", args.to_date))

    for variant in selected:
        stem = f"SuisM5_v1_iter_{variant.name}"
        patched = patch_source(source_text, stem, variant.replacements)
        compile_variant(stem, patched)
        for window_name, from_date, to_date in windows:
            print(f"running {variant.name} {window_name} {from_date}-{to_date}", flush=True)
            row = run_backtest(stem, variant.name, window_name, from_date, to_date, args.deposit, args.leverage, args.timeout)
            row["variant"] = variant.name
            row["note"] = variant.note
            results.append(row)
            (OUT / "results.json").write_text(json.dumps(results, indent=2))
            (OUT / "summary.md").write_text(summarize(results))

    print((OUT / "summary.md").read_text())


if __name__ == "__main__":
    main()
