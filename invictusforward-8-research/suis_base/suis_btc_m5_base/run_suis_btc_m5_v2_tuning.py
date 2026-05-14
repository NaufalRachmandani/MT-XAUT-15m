#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))

from analyze_mt5_report import iter_rows, parse_first_number, read_report  # noqa: E402


EXP_ROOT = Path(__file__).resolve().parent
SOURCE = (
    Path.home()
    / "Library/Application Support/net.metaquotes.wine.metatrader5/drive_c/MT5Build/Suis_BTC_M5_V1/Suis_BTC_M5_V1.mq5"
)
OUT_ROOT = EXP_ROOT / "v2_tuning"
CONFIG_DIR = EXP_ROOT / "configs" / "suis_btc_m5_v2"

WINEPREFIX = Path.home() / "Library/Application Support/net.metaquotes.wine.metatrader5"
WINE = Path("/Applications/MetaTrader 5.app/Contents/SharedSupport/wine/bin/wine64")
METAEDITOR_WIN = r"C:\Program Files\MetaTrader 5\MetaEditor64.exe"
TERMINAL_WIN = r"C:\MT5PortableSuis\terminal64.exe"
PORTABLE = WINEPREFIX / "drive_c" / "MT5PortableSuis"
BUILD = WINEPREFIX / "drive_c" / "MT5Build"
BUILD_DIR = BUILD / "Suis_BTC_M5_V2_Tune"
REPORTS = PORTABLE / "Reports"
EXPERT_DIR = PORTABLE / "MQL5" / "Experts" / "Suis_BTC_M5_V2_Tune"
EXPERT = EXPERT_DIR / "Suis_BTC_M5_V2_Tune.ex5"

ACCOUNT = {
    "name": "cent25",
    "login": "184000633",
    "server": "Exness-MT5Real25",
    "symbol": "BTCUSDc",
    "deposit": "1000",
    "currency": "USC",
    "leverage": "1:2000",
}

FROM_DATE = "2026.01.01"
TO_DATE = "2026.05.14"
PERIOD = "M5"
MODEL = 4
EXECUTION_MODE_MS = 20

ALL_HOURS = "0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23"
HOURS_5_6_15_16_BLOCKED = "0,1,2,3,4,7,8,9,10,11,12,13,14,17,18,19,20,21,22,23"
HOURS_5_6_10_15_16_BLOCKED = "0,1,2,3,4,7,8,9,11,12,13,14,17,18,19,20,21,22,23"
HOURS_5_6_9_15_16_BLOCKED = "0,1,2,3,4,7,8,10,11,12,13,14,17,18,19,20,21,22,23"


def hour_overrides(blocked: str) -> dict[str, Any]:
    return {
        "V11_BlockSellBreakHours": blocked,
        "V11_BlockSellZoneHours": blocked,
        "V11_BlockSellImpulseHours": blocked,
        "V11_BlockSellSubHours": blocked,
        "V11_BlockSellAddOnHours": blocked,
    }


NO_ZONE = {
    "V10_EnableZoneRetestEngine": False,
    "V11_BlockSellZoneHours": ALL_HOURS,
}

NO_ZONE_ADDON = NO_ZONE | {
    "V10_EnableAddOnEngine": False,
    "V10_EnableSellAddOns": False,
    "V11_BlockSellAddOnHours": ALL_HOURS,
}

NO_ZONE_ADDON_COMP = NO_ZONE_ADDON | {
    "V10_EnableBearSubEngine": False,
    "V11_BlockSellSubHours": ALL_HOURS,
}

QUEUE_CORE = {
    "V12_EnableMultiSignalQueue": True,
    "V12_MaxSignalsPerBar": 4,
    "V12_AllowIndependentAddOns": True,
    "V10_MaxPositions": 18,
    "V10_AddOnMaxPerSide": 4,
    "V10_AddOnRiskMultiplier": 0.16,
    "V12_MaxOpenRiskPctOfEquity": 32.0,
    "V12_MaxOpenRiskPctOfStartEquity": 42.0,
    "V12_RiskBudgetCapPctOfStartEquity": 52.0,
    "V11_MaxConsecutiveLosses": 4,
    "V11_LossCooldownMinutes": 120,
    "V12_ThrottleStartDrawdownPct": 13.0,
    "V12_ThrottleFullDrawdownPct": 38.0,
    "V12_ThrottleMinMultiplier": 0.25,
}

QUEUE_LOOSE = QUEUE_CORE | {
    "V10_MaxPositions": 24,
    "V12_MaxOpenRiskPctOfEquity": 48.0,
    "V12_MaxOpenRiskPctOfStartEquity": 60.0,
    "V12_RiskBudgetCapPctOfStartEquity": 68.0,
    "V11_MaxConsecutiveLosses": 5,
    "V11_LossCooldownMinutes": 90,
    "V12_ThrottleStartDrawdownPct": 16.0,
    "V12_ThrottleFullDrawdownPct": 46.0,
    "V12_ThrottleMinMultiplier": 0.35,
}

QUEUE_PUSH = QUEUE_LOOSE | {
    "V10_MaxPositions": 30,
    "V12_MaxOpenRiskPctOfEquity": 0.0,
    "V12_MaxOpenRiskPctOfStartEquity": 0.0,
    "V12_RiskBudgetCapPctOfStartEquity": 90.0,
    "V11_MaxConsecutiveLosses": 6,
    "V11_LossCooldownMinutes": 45,
    "V12_ThrottleStartDrawdownPct": 22.0,
    "V12_ThrottleFullDrawdownPct": 58.0,
    "V12_ThrottleMinMultiplier": 0.45,
}

PEAK_35 = {
    "V12_EnablePeakEquityGuard": True,
    "V12_PeakDrawdownStopPct": 35.0,
    "V12_PeakClosePositionsOnStop": True,
}

PEAK_32 = PEAK_35 | {
    "V12_PeakDrawdownStopPct": 32.0,
}

PEAK_30 = PEAK_35 | {
    "V12_PeakDrawdownStopPct": 30.0,
}

PEAK_42 = PEAK_35 | {
    "V12_PeakDrawdownStopPct": 42.0,
}

BASE_V1_COMMON = {
    "V12_BlockTradeMonths": "4,7,8,9,10,12",
}

CANDIDATES: dict[str, dict[str, Any]] = {
    "v2_block_h9": BASE_V1_COMMON | hour_overrides(HOURS_5_6_15_16_BLOCKED),
    "v2_block_h9_nozone": BASE_V1_COMMON | hour_overrides(HOURS_5_6_15_16_BLOCKED) | NO_ZONE,
    "v2_block_h9_nozone_r15": BASE_V1_COMMON
    | hour_overrides(HOURS_5_6_15_16_BLOCKED)
    | NO_ZONE
    | {
        "V10_RiskPercent": 15.0,
        "V11_MaxLotCap": 22.5,
        "V11_DailyMaxLossPct": 9.5,
        "V11_DailyProfitLockStartPct": 22.0,
        "V11_DailyMaxGivebackPct": 7.5,
    },
    "v2_block_h9_nozone_r155": BASE_V1_COMMON
    | hour_overrides(HOURS_5_6_15_16_BLOCKED)
    | NO_ZONE
    | {
        "V10_RiskPercent": 15.5,
        "V11_MaxLotCap": 23.25,
        "V11_DailyMaxLossPct": 9.75,
        "V11_DailyProfitLockStartPct": 23.0,
        "V11_DailyMaxGivebackPct": 7.75,
    },
    "v2_mt5opt_r17_rr78_score42": BASE_V1_COMMON
    | hour_overrides(HOURS_5_6_15_16_BLOCKED)
    | NO_ZONE
    | {
        "V10_RiskPercent": 17.0,
        "V11_MaxLotCap": 23.25,
        "V11_DailyMaxLossPct": 9.75,
        "V11_DailyProfitLockStartPct": 23.0,
        "V11_DailyMaxGivebackPct": 7.75,
        "V10_SellRR": 0.78,
        "V10_MinTradeScore": 42,
    },
    "v2_mt5opt_r17_rr74_score42": BASE_V1_COMMON
    | hour_overrides(HOURS_5_6_15_16_BLOCKED)
    | NO_ZONE
    | {
        "V10_RiskPercent": 17.0,
        "V11_MaxLotCap": 23.25,
        "V11_DailyMaxLossPct": 9.75,
        "V11_DailyProfitLockStartPct": 23.0,
        "V11_DailyMaxGivebackPct": 7.75,
        "V10_SellRR": 0.74,
        "V10_MinTradeScore": 42,
    },
    "v2_mt5opt_r155_rr78_score42": BASE_V1_COMMON
    | hour_overrides(HOURS_5_6_15_16_BLOCKED)
    | NO_ZONE
    | {
        "V10_RiskPercent": 15.5,
        "V11_MaxLotCap": 23.25,
        "V11_DailyMaxLossPct": 9.75,
        "V11_DailyProfitLockStartPct": 23.0,
        "V11_DailyMaxGivebackPct": 7.75,
        "V10_SellRR": 0.78,
        "V10_MinTradeScore": 42,
    },
    "v2_mt5opt_r155_rr74_score42": BASE_V1_COMMON
    | hour_overrides(HOURS_5_6_15_16_BLOCKED)
    | NO_ZONE
    | {
        "V10_RiskPercent": 15.5,
        "V11_MaxLotCap": 23.25,
        "V11_DailyMaxLossPct": 9.75,
        "V11_DailyProfitLockStartPct": 23.0,
        "V11_DailyMaxGivebackPct": 7.75,
        "V10_SellRR": 0.74,
        "V10_MinTradeScore": 42,
    },
    "v2_mt5opt_r15_rr74_score42": BASE_V1_COMMON
    | hour_overrides(HOURS_5_6_15_16_BLOCKED)
    | NO_ZONE
    | {
        "V10_RiskPercent": 15.0,
        "V11_MaxLotCap": 22.5,
        "V11_DailyMaxLossPct": 9.5,
        "V11_DailyProfitLockStartPct": 22.0,
        "V11_DailyMaxGivebackPct": 7.5,
        "V10_SellRR": 0.74,
        "V10_MinTradeScore": 42,
    },
    "v2_mt5opt_r1475_rr74_score42": BASE_V1_COMMON
    | hour_overrides(HOURS_5_6_15_16_BLOCKED)
    | NO_ZONE
    | {
        "V10_RiskPercent": 14.75,
        "V11_MaxLotCap": 22.125,
        "V11_DailyMaxLossPct": 9.375,
        "V11_DailyProfitLockStartPct": 21.5,
        "V11_DailyMaxGivebackPct": 7.375,
        "V10_SellRR": 0.74,
        "V10_MinTradeScore": 42,
    },
    "v2_mt5opt_r1525_rr74_score42": BASE_V1_COMMON
    | hour_overrides(HOURS_5_6_15_16_BLOCKED)
    | NO_ZONE
    | {
        "V10_RiskPercent": 15.25,
        "V11_MaxLotCap": 22.875,
        "V11_DailyMaxLossPct": 9.625,
        "V11_DailyProfitLockStartPct": 22.5,
        "V11_DailyMaxGivebackPct": 7.625,
        "V10_SellRR": 0.74,
        "V10_MinTradeScore": 42,
    },
    "v2_mt5opt_r15_rr75_score42": BASE_V1_COMMON
    | hour_overrides(HOURS_5_6_15_16_BLOCKED)
    | NO_ZONE
    | {
        "V10_RiskPercent": 15.0,
        "V11_MaxLotCap": 22.5,
        "V11_DailyMaxLossPct": 9.5,
        "V11_DailyProfitLockStartPct": 22.0,
        "V11_DailyMaxGivebackPct": 7.5,
        "V10_SellRR": 0.75,
        "V10_MinTradeScore": 42,
    },
    "v2_mt5opt_r15_rr76_score42": BASE_V1_COMMON
    | hour_overrides(HOURS_5_6_15_16_BLOCKED)
    | NO_ZONE
    | {
        "V10_RiskPercent": 15.0,
        "V11_MaxLotCap": 22.5,
        "V11_DailyMaxLossPct": 9.5,
        "V11_DailyProfitLockStartPct": 22.0,
        "V11_DailyMaxGivebackPct": 7.5,
        "V10_SellRR": 0.76,
        "V10_MinTradeScore": 42,
    },
    "v2_mt5opt_r15_rr77_score42": BASE_V1_COMMON
    | hour_overrides(HOURS_5_6_15_16_BLOCKED)
    | NO_ZONE
    | {
        "V10_RiskPercent": 15.0,
        "V11_MaxLotCap": 22.5,
        "V11_DailyMaxLossPct": 9.5,
        "V11_DailyProfitLockStartPct": 22.0,
        "V11_DailyMaxGivebackPct": 7.5,
        "V10_SellRR": 0.77,
        "V10_MinTradeScore": 42,
    },
    "v2_mt5opt_r1475_rr76_score42": BASE_V1_COMMON
    | hour_overrides(HOURS_5_6_15_16_BLOCKED)
    | NO_ZONE
    | {
        "V10_RiskPercent": 14.75,
        "V11_MaxLotCap": 22.125,
        "V11_DailyMaxLossPct": 9.375,
        "V11_DailyProfitLockStartPct": 21.5,
        "V11_DailyMaxGivebackPct": 7.375,
        "V10_SellRR": 0.76,
        "V10_MinTradeScore": 42,
    },
    "v2_mt5opt_r1525_rr75_score42": BASE_V1_COMMON
    | hour_overrides(HOURS_5_6_15_16_BLOCKED)
    | NO_ZONE
    | {
        "V10_RiskPercent": 15.25,
        "V11_MaxLotCap": 22.875,
        "V11_DailyMaxLossPct": 9.625,
        "V11_DailyProfitLockStartPct": 22.5,
        "V11_DailyMaxGivebackPct": 7.625,
        "V10_SellRR": 0.75,
        "V10_MinTradeScore": 42,
    },
    "v2_mt5opt_r1525_rr76_score42": BASE_V1_COMMON
    | hour_overrides(HOURS_5_6_15_16_BLOCKED)
    | NO_ZONE
    | {
        "V10_RiskPercent": 15.25,
        "V11_MaxLotCap": 22.875,
        "V11_DailyMaxLossPct": 9.625,
        "V11_DailyProfitLockStartPct": 22.5,
        "V11_DailyMaxGivebackPct": 7.625,
        "V10_SellRR": 0.76,
        "V10_MinTradeScore": 42,
    },
    "v2_mt5opt_r16_rr74_score42": BASE_V1_COMMON
    | hour_overrides(HOURS_5_6_15_16_BLOCKED)
    | NO_ZONE
    | {
        "V10_RiskPercent": 16.0,
        "V11_MaxLotCap": 24.0,
        "V11_DailyMaxLossPct": 10.0,
        "V11_DailyProfitLockStartPct": 24.0,
        "V11_DailyMaxGivebackPct": 8.0,
        "V10_SellRR": 0.74,
        "V10_MinTradeScore": 42,
    },
    "v2_mt5opt_r165_rr74_score42": BASE_V1_COMMON
    | hour_overrides(HOURS_5_6_15_16_BLOCKED)
    | NO_ZONE
    | {
        "V10_RiskPercent": 16.5,
        "V11_MaxLotCap": 24.75,
        "V11_DailyMaxLossPct": 10.25,
        "V11_DailyProfitLockStartPct": 24.5,
        "V11_DailyMaxGivebackPct": 8.25,
        "V10_SellRR": 0.74,
        "V10_MinTradeScore": 42,
    },
    "v2_block_h9_nozone_r16": BASE_V1_COMMON
    | hour_overrides(HOURS_5_6_15_16_BLOCKED)
    | NO_ZONE
    | {
        "V10_RiskPercent": 16.0,
        "V11_MaxLotCap": 24.0,
        "V11_DailyMaxLossPct": 10.0,
        "V11_DailyProfitLockStartPct": 24.0,
        "V11_DailyMaxGivebackPct": 8.0,
    },
    "v2_block_h9_nozone_r18": BASE_V1_COMMON
    | hour_overrides(HOURS_5_6_15_16_BLOCKED)
    | NO_ZONE
    | {
        "V10_RiskPercent": 18.0,
        "V11_MaxLotCap": 27.0,
        "V11_DailyMaxLossPct": 11.0,
        "V11_DailyProfitLockStartPct": 26.0,
        "V11_DailyMaxGivebackPct": 9.0,
    },
    "v2_block_h9_nozone_r19": BASE_V1_COMMON
    | hour_overrides(HOURS_5_6_15_16_BLOCKED)
    | NO_ZONE
    | {
        "V10_RiskPercent": 19.0,
        "V11_MaxLotCap": 28.5,
        "V11_DailyMaxLossPct": 11.5,
        "V11_DailyProfitLockStartPct": 27.0,
        "V11_DailyMaxGivebackPct": 9.5,
    },
    "v2_block_h9_nozone_r22": BASE_V1_COMMON
    | hour_overrides(HOURS_5_6_15_16_BLOCKED)
    | NO_ZONE
    | {
        "V10_RiskPercent": 22.0,
        "V11_MaxLotCap": 33.0,
        "V11_DailyMaxLossPct": 13.0,
        "V11_DailyProfitLockStartPct": 31.0,
        "V11_DailyMaxGivebackPct": 10.0,
    },
    "v2_block_h9_nozone_r24": BASE_V1_COMMON
    | hour_overrides(HOURS_5_6_15_16_BLOCKED)
    | NO_ZONE
    | {
        "V10_RiskPercent": 24.0,
        "V11_MaxLotCap": 36.0,
        "V11_DailyMaxLossPct": 14.0,
        "V11_DailyProfitLockStartPct": 34.0,
        "V11_DailyMaxGivebackPct": 11.0,
    },
    "v2_block_h9_break_impulse_r24": BASE_V1_COMMON
    | hour_overrides(HOURS_5_6_15_16_BLOCKED)
    | NO_ZONE_ADDON_COMP
    | {
        "V10_RiskPercent": 24.0,
        "V11_MaxLotCap": 36.0,
        "V11_DailyMaxLossPct": 14.0,
        "V11_DailyProfitLockStartPct": 34.0,
        "V11_DailyMaxGivebackPct": 11.0,
    },
    "v2_queue_h5_6_15_16_nozone_r12": BASE_V1_COMMON
    | hour_overrides(HOURS_5_6_15_16_BLOCKED)
    | NO_ZONE
    | QUEUE_CORE
    | {
        "V10_RiskPercent": 12.0,
        "V11_MaxLotCap": 24.0,
        "V11_DailyMaxLossPct": 9.0,
        "V11_DailyProfitLockStartPct": 20.0,
        "V11_DailyMaxGivebackPct": 7.0,
    },
    "v2_queue_h5_6_15_16_nozone_r14": BASE_V1_COMMON
    | hour_overrides(HOURS_5_6_15_16_BLOCKED)
    | NO_ZONE
    | QUEUE_CORE
    | {
        "V10_RiskPercent": 14.0,
        "V11_MaxLotCap": 28.0,
        "V11_DailyMaxLossPct": 10.0,
        "V11_DailyProfitLockStartPct": 23.0,
        "V11_DailyMaxGivebackPct": 8.0,
    },
    "v2_queue_h5_6_15_16_nozone_r16_peak35": BASE_V1_COMMON
    | hour_overrides(HOURS_5_6_15_16_BLOCKED)
    | NO_ZONE
    | QUEUE_CORE
    | PEAK_35
    | {
        "V10_RiskPercent": 16.0,
        "V11_MaxLotCap": 32.0,
        "V11_DailyMaxLossPct": 11.0,
        "V11_DailyProfitLockStartPct": 26.0,
        "V11_DailyMaxGivebackPct": 9.0,
    },
    "v2_h10_nozone_r20": BASE_V1_COMMON | hour_overrides(HOURS_5_6_10_15_16_BLOCKED) | NO_ZONE,
    "v2_queue_h10_nozone_r12": BASE_V1_COMMON
    | hour_overrides(HOURS_5_6_10_15_16_BLOCKED)
    | NO_ZONE
    | QUEUE_CORE
    | {
        "V10_RiskPercent": 12.0,
        "V11_MaxLotCap": 24.0,
        "V11_DailyMaxLossPct": 9.0,
        "V11_DailyProfitLockStartPct": 20.0,
        "V11_DailyMaxGivebackPct": 7.0,
    },
    "v2_queue_h5_6_15_16_nozone_r16": BASE_V1_COMMON
    | hour_overrides(HOURS_5_6_15_16_BLOCKED)
    | NO_ZONE
    | QUEUE_LOOSE
    | {
        "V10_RiskPercent": 16.0,
        "V11_MaxLotCap": 32.0,
        "V11_DailyMaxLossPct": 12.0,
        "V11_DailyProfitLockStartPct": 28.0,
        "V11_DailyMaxGivebackPct": 10.0,
    },
    "v2_queue_h5_6_15_16_nozone_r18": BASE_V1_COMMON
    | hour_overrides(HOURS_5_6_15_16_BLOCKED)
    | NO_ZONE
    | QUEUE_LOOSE
    | {
        "V10_RiskPercent": 18.0,
        "V11_MaxLotCap": 36.0,
        "V11_DailyMaxLossPct": 13.0,
        "V11_DailyProfitLockStartPct": 31.0,
        "V11_DailyMaxGivebackPct": 11.0,
    },
    "v2_queue_h5_6_15_16_nozone_r20": BASE_V1_COMMON
    | hour_overrides(HOURS_5_6_15_16_BLOCKED)
    | NO_ZONE
    | QUEUE_LOOSE
    | {
        "V10_RiskPercent": 20.0,
        "V11_MaxLotCap": 40.0,
        "V11_DailyMaxLossPct": 14.0,
        "V11_DailyProfitLockStartPct": 34.0,
        "V11_DailyMaxGivebackPct": 12.0,
    },
    "v2_queue_break_impulse_r16": BASE_V1_COMMON
    | hour_overrides(HOURS_5_6_15_16_BLOCKED)
    | NO_ZONE_ADDON_COMP
    | QUEUE_LOOSE
    | {
        "V10_RiskPercent": 16.0,
        "V11_MaxLotCap": 32.0,
        "V11_DailyMaxLossPct": 12.0,
        "V11_DailyProfitLockStartPct": 28.0,
        "V11_DailyMaxGivebackPct": 10.0,
    },
    "v2_queue_break_impulse_r18": BASE_V1_COMMON
    | hour_overrides(HOURS_5_6_15_16_BLOCKED)
    | NO_ZONE_ADDON_COMP
    | QUEUE_LOOSE
    | {
        "V10_RiskPercent": 18.0,
        "V11_MaxLotCap": 36.0,
        "V11_DailyMaxLossPct": 13.0,
        "V11_DailyProfitLockStartPct": 31.0,
        "V11_DailyMaxGivebackPct": 11.0,
    },
    "v2_queue_break_impulse_r20": BASE_V1_COMMON
    | hour_overrides(HOURS_5_6_15_16_BLOCKED)
    | NO_ZONE_ADDON_COMP
    | QUEUE_LOOSE
    | {
        "V10_RiskPercent": 20.0,
        "V11_MaxLotCap": 40.0,
        "V11_DailyMaxLossPct": 14.0,
        "V11_DailyProfitLockStartPct": 34.0,
        "V11_DailyMaxGivebackPct": 12.0,
    },
    "v2_queue_push_nozone_r28": BASE_V1_COMMON
    | hour_overrides(HOURS_5_6_15_16_BLOCKED)
    | NO_ZONE
    | QUEUE_PUSH
    | {
        "V10_RiskPercent": 28.0,
        "V11_MaxLotCap": 56.0,
        "V11_DailyMaxLossPct": 18.0,
        "V11_DailyProfitLockStartPct": 42.0,
        "V11_DailyMaxGivebackPct": 16.0,
    },
    "v2_queue_push_nozone_r34": BASE_V1_COMMON
    | hour_overrides(HOURS_5_6_15_16_BLOCKED)
    | NO_ZONE
    | QUEUE_PUSH
    | {
        "V10_RiskPercent": 34.0,
        "V11_MaxLotCap": 68.0,
        "V11_DailyMaxLossPct": 22.0,
        "V11_DailyProfitLockStartPct": 52.0,
        "V11_DailyMaxGivebackPct": 20.0,
    },
    "v2_queue_push_nozone_r40": BASE_V1_COMMON
    | hour_overrides(HOURS_5_6_15_16_BLOCKED)
    | NO_ZONE
    | QUEUE_PUSH
    | {
        "V10_RiskPercent": 40.0,
        "V11_MaxLotCap": 80.0,
        "V11_DailyMaxLossPct": 26.0,
        "V11_DailyProfitLockStartPct": 60.0,
        "V11_DailyMaxGivebackPct": 24.0,
    },
    "v2_queue_push_nozone_r34_peak42": BASE_V1_COMMON
    | hour_overrides(HOURS_5_6_15_16_BLOCKED)
    | NO_ZONE
    | QUEUE_PUSH
    | PEAK_42
    | {
        "V10_RiskPercent": 34.0,
        "V11_MaxLotCap": 68.0,
        "V11_DailyMaxLossPct": 22.0,
        "V11_DailyProfitLockStartPct": 52.0,
        "V11_DailyMaxGivebackPct": 20.0,
    },
    "v2_block_h9_nozone_peak32": BASE_V1_COMMON
    | hour_overrides(HOURS_5_6_15_16_BLOCKED)
    | NO_ZONE
    | PEAK_32,
    "v2_block_h9_nozone_peak30": BASE_V1_COMMON
    | hour_overrides(HOURS_5_6_15_16_BLOCKED)
    | NO_ZONE
    | PEAK_30,
    "v2_block_h9_nozone_r22_peak32": BASE_V1_COMMON
    | hour_overrides(HOURS_5_6_15_16_BLOCKED)
    | NO_ZONE
    | PEAK_32
    | {
        "V10_RiskPercent": 22.0,
        "V11_MaxLotCap": 33.0,
        "V11_DailyMaxLossPct": 13.0,
        "V11_DailyProfitLockStartPct": 31.0,
        "V11_DailyMaxGivebackPct": 10.0,
    },
    "v2_block_h9_nozone_r24_peak32": BASE_V1_COMMON
    | hour_overrides(HOURS_5_6_15_16_BLOCKED)
    | NO_ZONE
    | PEAK_32
    | {
        "V10_RiskPercent": 24.0,
        "V11_MaxLotCap": 36.0,
        "V11_DailyMaxLossPct": 14.0,
        "V11_DailyProfitLockStartPct": 34.0,
        "V11_DailyMaxGivebackPct": 11.0,
    },
}


def win_path(path: Path) -> str:
    drive = WINEPREFIX / "drive_c"
    raw = str(path)
    if not raw.startswith(str(drive)):
        raise ValueError(f"path is outside drive_c: {path}")
    return "C:" + raw[len(str(drive)) :].replace("/", "\\")


def write_utf16(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"\xff\xfe" + text.encode("utf-16le"))


def value_to_mql(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, str):
        return f'"{value}"'
    if isinstance(value, float):
        return f"{value:.10g}"
    return str(value)


def patch_constants(source: str, overrides: dict[str, Any], name: str) -> str:
    patched = source
    patched = re.sub(r'#property version\s+".*?"', '#property version   "2.00"', patched)
    patched = re.sub(
        r'#property description\s+".*?"',
        f'#property description "Suis_BTC_M5_V2 tuning candidate {name}"',
        patched,
    )
    patched = re.sub(
        r"// Suis BTC M5 V1 baked no-set build\.",
        f"// Suis BTC M5 V2 tuning candidate: {name}.",
        patched,
    )
    patched = patched.replace("Suis_BTC_M5_Base requires M5.", "Suis_BTC_M5_V2 requires M5.")
    for const_name, value in overrides.items():
        pattern = re.compile(
            rf"^(\s*(?:static\s+)?const\s+(?:bool|int|long|double|string|ENUM_TIMEFRAMES)\s+{re.escape(const_name)}\s*=\s*)(.*?)(;)",
            flags=re.M,
        )
        patched, count = pattern.subn(rf"\g<1>{value_to_mql(value)}\3", patched)
        if count != 1:
            raise ValueError(f"constant not found or duplicated: {const_name}")
    return patched


def compile_candidate(name: str, overrides: dict[str, Any]) -> Path:
    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)
    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    source_path = BUILD_DIR / "Suis_BTC_M5_V2_Tune.mq5"
    source_path.write_text(patch_constants(SOURCE.read_text(encoding="utf-8"), overrides, name), encoding="utf-8")
    log_path = BUILD_DIR / "compile.log"
    command = [
        str(WINE),
        METAEDITOR_WIN,
        f"/compile:{win_path(source_path)}",
        f"/log:{win_path(log_path)}",
    ]
    subprocess.run(
        command,
        env={**os.environ, "WINEPREFIX": str(WINEPREFIX)},
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        timeout=120,
    )
    log_text = log_path.read_bytes().decode("utf-16le", errors="ignore")
    if "Result: 0 errors, 0 warnings" not in log_text and " 0 error(s), 0 warning(s)" not in log_text:
        raise RuntimeError(f"compile failed for {name}\n{log_text}")
    ex5 = BUILD_DIR / "Suis_BTC_M5_V2_Tune.ex5"
    if not ex5.exists():
        raise RuntimeError(f"missing compiled EX5 for {name}")
    EXPERT_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ex5, EXPERT)
    return source_path


def report_stem(name: str) -> str:
    return (
        f"SUIS_BTC_M5_V2_TUNE_{ACCOUNT['name']}_{name}_ytd2026_"
        f"{ACCOUNT['symbol']}_d{ACCOUNT['deposit']}{ACCOUNT['currency']}_{PERIOD}_model{MODEL}_"
        f"exec{EXECUTION_MODE_MS}ms_realticks_{FROM_DATE.replace('.', '')}_{TO_DATE.replace('.', '')}"
    )


def write_ini(name: str) -> Path:
    stem = report_stem(name)
    lines = [
        "[Common]",
        f"Login={ACCOUNT['login']}",
        f"Server={ACCOUNT['server']}",
        "ProxyEnable=0",
        "KeepPrivate=1",
        "NewsEnable=0",
        "CertInstall=1",
        "",
        "[Events]",
        "Enable=0",
        "ConnectEnable=0",
        "DisconnectEnable=0",
        "Email NotifyEnable=0",
        "TimeoutEnable=0",
        "OkEnable=0",
        "NewsEnable=0",
        "Expert AdvisorEnable=0",
        "AlertEnable=0",
        "RequoteEnable=0",
        "Trailing StopEnable=0",
        "Testing FinishedEnable=0",
        "",
        "[Experts]",
        "AllowLiveTrading=0",
        "AllowDllImport=0",
        "Enabled=1",
        "Account=0",
        "Profile=0",
        "",
        "[Tester]",
        r"Expert=Suis_BTC_M5_V2_Tune\Suis_BTC_M5_V2_Tune.ex5",
        "ExpertParameters=",
        f"Symbol={ACCOUNT['symbol']}",
        f"Period={PERIOD}",
        f"Login={ACCOUNT['login']}",
        f"Model={MODEL}",
        f"ExecutionMode={EXECUTION_MODE_MS}",
        "Optimization=0",
        "OptimizationCriterion=0",
        f"FromDate={FROM_DATE}",
        f"ToDate={TO_DATE}",
        "ForwardMode=0",
        rf"Report=\Reports\{stem}",
        "ReplaceReport=1",
        "ShutdownTerminal=1",
        f"Deposit={ACCOUNT['deposit']}",
        f"Currency={ACCOUNT['currency']}",
        f"Leverage={ACCOUNT['leverage']}",
        "UseLocal=1",
        "UseRemote=0",
        "UseCloud=0",
        "Visual=0",
        "",
    ]
    path = BUILD / f"{stem}.ini"
    write_utf16(path, "\r\n".join(lines))
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, CONFIG_DIR / path.name)
    return path


def cell(rows: list[list[str]], label: str, default: str = "") -> str:
    for row in rows:
        for index, value in enumerate(row[:-1]):
            if value == label:
                return row[index + 1]
    return default


def pct_in(value: str) -> float:
    match = re.search(r"\(([-\d.]+)%\)", value or "")
    return float(match.group(1)) if match else 0.0


def first_pct(value: str) -> float:
    match = re.search(r"([-]?\d+(?:\.\d+)?)%", value or "")
    return float(match.group(1)) if match else 0.0


def parse_report(path: Path, name: str, source_path: Path, elapsed_sec: float) -> dict[str, Any]:
    text = read_report(path)
    rows = list(iter_rows(text))
    initial_deposit = parse_first_number(cell(rows, "Initial Deposit:"))
    net = parse_first_number(cell(rows, "Total Net Profit:"))
    profit_trades = cell(rows, "Profit Trades (% of total):")
    loss_trades = cell(rows, "Loss Trades (% of total):")
    balance_dd_max = cell(rows, "Balance Drawdown Maximal:")
    balance_dd_rel = cell(rows, "Balance Drawdown Relative:")
    equity_dd_max = cell(rows, "Equity Drawdown Maximal:")
    equity_dd_rel = cell(rows, "Equity Drawdown Relative:")
    return {
        "variant": name,
        "account": ACCOUNT["name"],
        "login": ACCOUNT["login"],
        "server": ACCOUNT["server"],
        "symbol": ACCOUNT["symbol"],
        "from": FROM_DATE,
        "to": TO_DATE,
        "deposit": initial_deposit,
        "currency": ACCOUNT["currency"],
        "period": PERIOD,
        "model": MODEL,
        "execution_mode_ms": EXECUTION_MODE_MS,
        "expert_parameters": "",
        "history_quality": cell(rows, "History Quality:"),
        "bars": int(parse_first_number(cell(rows, "Bars:"))),
        "ticks": int(parse_first_number(cell(rows, "Ticks:"))),
        "net": net,
        "profit_pct": (net / initial_deposit * 100.0) if initial_deposit else 0.0,
        "gross_profit": parse_first_number(cell(rows, "Gross Profit:")),
        "gross_loss": parse_first_number(cell(rows, "Gross Loss:")),
        "profit_factor": parse_first_number(cell(rows, "Profit Factor:")),
        "expected_payoff": parse_first_number(cell(rows, "Expected Payoff:")),
        "recovery_factor": parse_first_number(cell(rows, "Recovery Factor:")),
        "sharpe_ratio": parse_first_number(cell(rows, "Sharpe Ratio:")),
        "margin_level": cell(rows, "Margin Level:"),
        "trades": int(parse_first_number(cell(rows, "Total Trades:"))),
        "deals": int(parse_first_number(cell(rows, "Total Deals:"))),
        "win_rate_pct": pct_in(profit_trades),
        "loss_rate_pct": pct_in(loss_trades),
        "short_trades": cell(rows, "Short Trades (won %):"),
        "long_trades": cell(rows, "Long Trades (won %):"),
        "profit_trades": profit_trades,
        "loss_trades": loss_trades,
        "balance_dd_abs": parse_first_number(cell(rows, "Balance Drawdown Absolute:")),
        "balance_dd_max": balance_dd_max,
        "balance_dd_max_pct": pct_in(balance_dd_max),
        "balance_dd_rel": balance_dd_rel,
        "balance_dd_rel_pct": first_pct(balance_dd_rel),
        "equity_dd_abs": parse_first_number(cell(rows, "Equity Drawdown Absolute:")),
        "equity_dd_max": equity_dd_max,
        "equity_dd_max_pct": pct_in(equity_dd_max),
        "equity_dd_rel": equity_dd_rel,
        "equity_dd_rel_pct": first_pct(equity_dd_rel),
        "max_dd_any_pct": max(pct_in(balance_dd_max), first_pct(balance_dd_rel), pct_in(equity_dd_max), first_pct(equity_dd_rel)),
        "largest_profit": parse_first_number(cell(rows, "Largest profit trade:")),
        "largest_loss": parse_first_number(cell(rows, "Largest loss trade:")),
        "average_profit": parse_first_number(cell(rows, "Average profit trade:")),
        "average_loss": parse_first_number(cell(rows, "Average loss trade:")),
        "max_consecutive_wins": cell(rows, "Maximum consecutive wins ($):"),
        "max_consecutive_losses": cell(rows, "Maximum consecutive losses ($):"),
        "maximal_consecutive_profit": cell(rows, "Maximal consecutive profit (count):"),
        "maximal_consecutive_loss": cell(rows, "Maximal consecutive loss (count):"),
        "average_consecutive_wins": cell(rows, "Average consecutive wins:"),
        "average_consecutive_losses": cell(rows, "Average consecutive losses:"),
        "report": str(path),
        "source": str(source_path),
        "ex5_sha256": hashlib.sha256(EXPERT.read_bytes()).hexdigest() if EXPERT.exists() else "",
        "elapsed_sec": elapsed_sec,
    }


def run_candidate(name: str, force: bool, timeout: int) -> dict[str, Any]:
    stem = report_stem(name)
    dest = OUT_ROOT / name
    htm = dest / f"{stem}.htm"
    summary = dest / "summary.json"
    if htm.exists() and summary.exists() and not force:
        return json.loads(summary.read_text(encoding="utf-8")) | {"cached": True}

    source_path = compile_candidate(name, CANDIDATES[name])
    for old in REPORTS.glob(f"{stem}*"):
        if old.is_file():
            old.unlink()
    ini = write_ini(name)
    started = time.time()
    timed_out = False
    command = [str(WINE), TERMINAL_WIN, "/portable", rf"/config:{win_path(ini)}"]
    try:
        subprocess.run(
            command,
            env={**os.environ, "WINEPREFIX": str(WINEPREFIX)},
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        timed_out = True
    elapsed = time.time() - started

    dest.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_path, dest / "Suis_BTC_M5_V2_Tune.mq5")
    shutil.copy2(BUILD_DIR / "compile.log", dest / "compile.log")
    shutil.copy2(ini, dest / ini.name)
    copied = []
    for report_file in REPORTS.glob(f"{stem}*"):
        if report_file.is_file():
            target = dest / report_file.name
            shutil.copy2(report_file, target)
            copied.append(target)
    if not htm.exists():
        return {
            "variant": name,
            "error": f"report missing; timed_out={timed_out}; copied={[str(p) for p in copied]}",
            "elapsed_sec": elapsed,
        }
    row = parse_report(htm, name, dest / "Suis_BTC_M5_V2_Tune.mq5", elapsed)
    row["timed_out"] = timed_out
    row["cached"] = False
    row["overrides"] = CANDIDATES[name]
    summary.write_text(json.dumps(row, indent=2, ensure_ascii=False), encoding="utf-8")
    return row


def markdown(rows: list[dict[str, Any]]) -> str:
    lines = [
        "# Suis BTC M5 V2 Tuning",
        "",
        f"All rows use `{ACCOUNT['server']} / {ACCOUNT['login']}`, `{ACCOUNT['symbol']}`, `{PERIOD}`, `Model={MODEL}`, `ExecutionMode={EXECUTION_MODE_MS}`, `ExpertParameters=` empty.",
        "",
        "| Variant | HQ | Net | Profit % | PF | Trades | WR | Bal DD Max | Eq DD Max | Max DD Any | Largest Loss | Max Consecutive Loss | Bars | Ticks |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | --- | --- | ---: | ---: | --- | ---: | ---: |",
    ]
    for row in rows:
        if "error" in row:
            lines.append(f"| {row['variant']} | ERROR | | | | | | | | | | {row['error']} | | |")
            continue
        lines.append(
            f"| {row['variant']} | {row['history_quality']} | {row['net']:.2f} | {row['profit_pct']:.2f}% | "
            f"{row['profit_factor']:.2f} | {row['trades']} | {row['win_rate_pct']:.2f}% | "
            f"{row['balance_dd_max']} | {row['equity_dd_max']} | {row['max_dd_any_pct']:.2f}% | "
            f"{row['largest_loss']:.2f} | {row['max_consecutive_losses']} | {row['bars']} | {row['ticks']} |"
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", action="append", choices=sorted(CANDIDATES))
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--timeout", type=int, default=420)
    args = parser.parse_args()

    names = args.candidate or list(CANDIDATES)
    rows: list[dict[str, Any]] = []
    for index, name in enumerate(names, start=1):
        print(f"[{index}/{len(names)}] {name}", flush=True)
        row = run_candidate(name, args.force, args.timeout)
        rows.append(row)
        if "error" in row:
            print(json.dumps({"variant": name, "error": row["error"]}, ensure_ascii=False), flush=True)
        else:
            print(
                json.dumps(
                    {
                        "variant": name,
                        "hq": row["history_quality"],
                        "net": row["net"],
                        "profit_pct": row["profit_pct"],
                        "pf": row["profit_factor"],
                        "trades": row["trades"],
                        "max_dd_any_pct": row["max_dd_any_pct"],
                        "largest_loss": row["largest_loss"],
                    },
                    ensure_ascii=False,
                ),
                flush=True,
            )

    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    sorted_rows = sorted(rows, key=lambda r: (-1 if "error" in r else r["net"]), reverse=True)
    (OUT_ROOT / "v2_tuning_results.json").write_text(json.dumps(sorted_rows, indent=2, ensure_ascii=False), encoding="utf-8")
    (OUT_ROOT / "V2_TUNING_RESULTS.md").write_text(markdown(sorted_rows), encoding="utf-8")
    print(f"RESULTS={OUT_ROOT / 'V2_TUNING_RESULTS.md'}", flush=True)


if __name__ == "__main__":
    main()
