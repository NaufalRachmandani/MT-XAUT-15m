#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import textwrap
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path("/Users/naufalrachmandani/Hobby/MT5 XAU 15m")
EA_SOURCE = ROOT / "mt5" / "InvictusForward1M15_v5.mq5"
RUN_DIR = ROOT / "build" / "v5_20x"
RUN_DIR.mkdir(parents=True, exist_ok=True)

WINEPREFIX = Path("/Users/naufalrachmandani/Library/Application Support/net.metaquotes.wine.metatrader5")
MT5_BUILD = WINEPREFIX / "drive_c" / "MT5Build"
MT5_EXPERTS = WINEPREFIX / "drive_c" / "Program Files" / "MetaTrader 5" / "MQL5" / "Experts" / "Invictus"
REPORTS_DIR = WINEPREFIX / "drive_c" / "Program Files" / "MetaTrader 5" / "Reports"
TESTER_LOG_DIR = WINEPREFIX / "drive_c" / "Program Files" / "MetaTrader 5" / "Tester" / "logs"
WINE = "/Applications/MetaTrader 5.app/Contents/SharedSupport/wine/bin/wine64"
METAEDITOR_EXE = r"C:\Program Files\MetaTrader 5\metaeditor64.exe"
TERMINAL_EXE = r"C:\Program Files\MetaTrader 5\terminal64.exe"


BASE_PARAMS: dict[str, Any] = {
    "IF1_PENDING_CANCEL_LOSS_CAP_PCT": 6.0,
    "IF1_BREAKEVEN_LOCK_USD": 1.5,
    "IF1_SIDEWAYS_TP_FRACTION_OVERRIDE": 0.55,
    "IF1_SIDEWAYS_MIN_TP_USD": 6.5,
    "IF1_REFERENCE_GOLD_CONTRACT_SIZE": 100.0,
    "IF1_TREND_MIN_SL_OVERRIDE": 12.0,
    "IF1_TREND_MAX_SL_OVERRIDE": 30.0,
    "IF1_TREND_MAX_POSITIONS_VERY_LOW_OVERRIDE": 2,
    "IF1_TREND_MAX_POSITIONS_LOW_OVERRIDE": 7,
    "IF1_TREND_MAX_POSITIONS_MID_OVERRIDE": 11,
    "IF1_TREND_MAX_POSITIONS_HIGH_OVERRIDE": 15,
    "IF1_COMPOUND_BALANCE_STEP_LOW_OVERRIDE": 250.0,
    "IF1_COMPOUND_BALANCE_STEP_MID_OVERRIDE": 300.0,
    "IF1_COMPOUND_BALANCE_STEP_HIGH_OVERRIDE": 375.0,
    "IF1_COMPOUND_BASE_LOT_MID_OVERRIDE": 0.82,
    "IF1_COMPOUND_BASE_LOT_HIGH_OVERRIDE": 1.92,
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
    "IF1_TREND_LOW_SCORE_SELL_LOT_MULT": 0.50,
    "IF1_TREND_POSITIVE_SELL_MIN": 85,
    "IF1_TREND_POSITIVE_SELL_MAX": 94,
    "IF1_TREND_POSITIVE_SELL_LOT_MULT": 1.0,
    "IF1_TREND_SELL_TP_RR_DEFAULT_OVERRIDE": 1.62,
    "IF1_TREND_SELL_TP_RR_BOOST_OVERRIDE": 2.25,
    "IF1_SCORE_RR_BOOST_MIN_OVERRIDE": 84,
    "IF1_VERY_LOW_BALANCE_CUTOFF_OVERRIDE": 250.0,
    "IF1_SELL_LOT_MODIFIER_OVERRIDE": 0.75,
    "IF1_SIDEWAYS_LOT_MODIFIER_VERY_LOW_OVERRIDE": 0.06,
    "IF1_SIDEWAYS_LOT_MODIFIER_OVERRIDE": 0.10,
    "IF1_LOW_BALANCE_SELL_LOT_MODIFIER_OVERRIDE": 1.0,
    "IF1_LOW_BALANCE_BUY_LOT_MULT_OVERRIDE": 1.0,
    "IF1_TREND_DAILY_LOSS_CAP_PCT_VERY_LOW_OVERRIDE": 6.0,
    "IF1_TREND_DAILY_LOSS_CAP_PCT_OVERRIDE": 8.0,
    "IF1_SIDEWAYS_DAILY_LOSS_CAP_PCT_VERY_LOW_OVERRIDE": 4.0,
    "IF1_SIDEWAYS_DAILY_LOSS_CAP_PCT_OVERRIDE": 5.0,
    "IF1_TREND_KILLSWITCH_WINS_OVERRIDE": 50,
    "IF1_SIDEWAYS_WINS_CAP_OVERRIDE": 20,
    "IF1_SIDEWAYS_ADX_THRESHOLD_OVERRIDE": 28.0,
    "IF1_SIDEWAYS_ENTRY_ZONE_FRACTION_OVERRIDE": 0.40,
    "IF1_SIDEWAYS_MAX_POSITIONS_VERY_LOW_OVERRIDE": 2,
    "IF1_SIDEWAYS_MAX_POSITIONS_OVERRIDE": 8,
    "IF1_SIDEWAYS_CLUSTER_MAX_PER_DAY_OVERRIDE": 5,
    "IF1_ALLOW_ALL_SELL_HOURS": True,
    "IF1_SELL_BLOCK_HOURS_MASK": 0,
    "IF1_LOW_SCORE_SELL_BLOCK_HOURS_MASK": 341600,
    "IF1_GOLD_HIGH_SCORE_SELL_REQUIRE_IMPULSIVE_BOS": True,
    "IF1_GOLD_HIGH_SCORE_SELL_MIN_LL_HH_EDGE": 0,
    "IF1_GOLD_HIGH_SCORE_SELL_MIN_BREAK_ATR_OVERRIDE": 0.0,
    "IF1_TREND_TIMED_PROFIT_CLOSE_HOURS_OVERRIDE": 4,
    "IF1_SIDEWAYS_TIMED_PROFIT_CLOSE_HOURS_OVERRIDE": 2,
    "IF1_TREND_TIMED_PROFIT_USD_PER_001_OVERRIDE": 24.0,
    "IF1_SIDEWAYS_TIMED_PROFIT_USD_PER_001_OVERRIDE": 15.0,
    "IF1_LOW_SCORE_SELL_TIMED_CLOSE_HOURS_OVERRIDE": 0,
    "IF1_LOW_SCORE_SELL_TIMED_PROFIT_USD_PER_001_OVERRIDE": 0.0,
    "IF1_LOW_SCORE_SELL_TIMED_MAX_LOSS_USD_PER_001_OVERRIDE": 0.0,
    "IF1_TREND_TP_RR_DEFAULT_OVERRIDE": 1.62,
    "IF1_TREND_TP_RR_BOOST_OVERRIDE": 2.25,
    "IF1_TREND_HIGH_SCORE_SELL_RR_OVERRIDE": 0.0,
    "IF1_BUY_LOW_SCORE_MAX": 84,
    "IF1_BUY_MID_SCORE_MIN": 85,
    "IF1_BUY_MID_SCORE_MAX": 94,
    "IF1_TREND_HIGH_SCORE_BUY_RR_MIN": 95,
    "IF1_TREND_HIGH_SCORE_BUY_RR_OVERRIDE": 2.45,
    "IF1_BUY_LOW_SCORE_RR_OVERRIDE": 0.0,
    "IF1_BUY_MID_SCORE_RR_OVERRIDE": 0.0,
    "IF1_BUY_LOW_SCORE_LOT_MULT": 1.0,
    "IF1_TREND_HIGH_SCORE_LOT_BOOST_MIN": 95,
    "IF1_TREND_HIGH_SCORE_LOT_BOOST": 1.18,
    "IF1_TREND_HIGH_SCORE_SELL_LOT_MULT": 1.0,
    "IF1_BUY_MIN_BREAK_ATR_OVERRIDE": 0.24,
    "IF1_BUY_MAX_ENTRY_PREMIUM_ATR_OVERRIDE": 0.0,
    "IF1_BUY_ENTRY_PREMIUM_SCORE_LIMIT_OVERRIDE": 101,
    "IF1_BUY_MAX_ZONE_PRIOR_TESTS_OVERRIDE": -1,
    "IF1_GOLD_HIGH_SCORE_BUY_REQUIRE_IMPULSIVE_BOS": False,
    "IF1_BUY_LOW_SCORE_REQUIRE_FVG": False,
    "IF1_BUY_BREAKEVEN_TRIGGER_R_MULT": 1.0,
    "IF1_BUY_BREAKEVEN_LOCK_USD_OVERRIDE": 0.0,
}


ITERATIONS: list[dict[str, Any]] = [
    {
        "name": "baseline_v4_clone",
        "hypothesis": "Baseline v5 pada setup akun kecil 100 USD dan 6 bulan terakhir.",
        "changes": {},
        "leverage": "1:100",
    },
    {
        "name": "leverage_1_50",
        "hypothesis": "Turunkan leverage untuk memaksa margin discipline tanpa ubah logic entry.",
        "changes": {},
        "leverage": "1:50",
    },
    {
        "name": "leverage_1_75",
        "hypothesis": "Versi leverage lebih konservatif tapi tidak seketat 1:50.",
        "changes": {},
        "leverage": "1:75",
    },
    {
        "name": "slow_compound_a",
        "hypothesis": "Perlambat compounding agar equity tidak terlalu agresif setelah akun mulai tumbuh.",
        "changes": {
            "IF1_COMPOUND_BALANCE_STEP_LOW_OVERRIDE": 400.0,
            "IF1_COMPOUND_BALANCE_STEP_MID_OVERRIDE": 500.0,
            "IF1_COMPOUND_BALANCE_STEP_HIGH_OVERRIDE": 650.0,
            "IF1_COMPOUND_BASE_LOT_MID_OVERRIDE": 0.52,
            "IF1_COMPOUND_BASE_LOT_HIGH_OVERRIDE": 1.12,
        },
        "leverage": "1:100",
    },
    {
        "name": "slow_compound_b",
        "hypothesis": "Versi compounding yang lebih lambat lagi untuk prioritas drawdown.",
        "changes": {
            "IF1_COMPOUND_BALANCE_STEP_LOW_OVERRIDE": 500.0,
            "IF1_COMPOUND_BALANCE_STEP_MID_OVERRIDE": 650.0,
            "IF1_COMPOUND_BALANCE_STEP_HIGH_OVERRIDE": 800.0,
            "IF1_COMPOUND_BASE_LOT_MID_OVERRIDE": 0.42,
            "IF1_COMPOUND_BASE_LOT_HIGH_OVERRIDE": 0.92,
        },
        "leverage": "1:100",
    },
    {
        "name": "position_caps_a",
        "hypothesis": "Batasi stacking lebih awal di semua balance tier.",
        "changes": {
            "IF1_TREND_MAX_POSITIONS_VERY_LOW_OVERRIDE": 1,
            "IF1_TREND_MAX_POSITIONS_LOW_OVERRIDE": 3,
            "IF1_TREND_MAX_POSITIONS_MID_OVERRIDE": 5,
            "IF1_TREND_MAX_POSITIONS_HIGH_OVERRIDE": 7,
            "IF1_SIDEWAYS_MAX_POSITIONS_VERY_LOW_OVERRIDE": 1,
            "IF1_SIDEWAYS_MAX_POSITIONS_OVERRIDE": 3,
        },
        "leverage": "1:100",
    },
    {
        "name": "position_caps_b",
        "hypothesis": "Versi cap posisi yang lebih keras untuk akun kecil.",
        "changes": {
            "IF1_TREND_MAX_POSITIONS_VERY_LOW_OVERRIDE": 1,
            "IF1_TREND_MAX_POSITIONS_LOW_OVERRIDE": 2,
            "IF1_TREND_MAX_POSITIONS_MID_OVERRIDE": 4,
            "IF1_TREND_MAX_POSITIONS_HIGH_OVERRIDE": 6,
            "IF1_SIDEWAYS_MAX_POSITIONS_VERY_LOW_OVERRIDE": 1,
            "IF1_SIDEWAYS_MAX_POSITIONS_OVERRIDE": 2,
        },
        "leverage": "1:100",
    },
    {
        "name": "daily_caps_a",
        "hypothesis": "Daily loss cap lebih ketat supaya drawdown harian tidak membesar.",
        "changes": {
            "IF1_TREND_DAILY_LOSS_CAP_PCT_VERY_LOW_OVERRIDE": 4.0,
            "IF1_TREND_DAILY_LOSS_CAP_PCT_OVERRIDE": 6.0,
            "IF1_SIDEWAYS_DAILY_LOSS_CAP_PCT_VERY_LOW_OVERRIDE": 2.5,
            "IF1_SIDEWAYS_DAILY_LOSS_CAP_PCT_OVERRIDE": 3.5,
        },
        "leverage": "1:100",
    },
    {
        "name": "daily_caps_b",
        "hypothesis": "Daily loss cap paling defensif untuk mencegah deep slide pada account kecil.",
        "changes": {
            "IF1_TREND_DAILY_LOSS_CAP_PCT_VERY_LOW_OVERRIDE": 3.5,
            "IF1_TREND_DAILY_LOSS_CAP_PCT_OVERRIDE": 5.0,
            "IF1_SIDEWAYS_DAILY_LOSS_CAP_PCT_VERY_LOW_OVERRIDE": 2.0,
            "IF1_SIDEWAYS_DAILY_LOSS_CAP_PCT_OVERRIDE": 3.0,
        },
        "leverage": "1:100",
    },
    {
        "name": "buy_filter_a",
        "hypothesis": "Buy harus lebih jelas follow-through-nya pada akun kecil.",
        "changes": {
            "IF1_BUY_MIN_BREAK_ATR_OVERRIDE": 0.30,
            "IF1_SCORE_BUY_MIN_OVERRIDE": 75,
        },
        "leverage": "1:100",
    },
    {
        "name": "buy_filter_b",
        "hypothesis": "Versi buy filter paling ketat untuk memangkas fast-fail breakout.",
        "changes": {
            "IF1_BUY_MIN_BREAK_ATR_OVERRIDE": 0.32,
            "IF1_SCORE_BUY_MIN_OVERRIDE": 80,
            "IF1_BUY_MAX_ZONE_PRIOR_TESTS_OVERRIDE": 1,
        },
        "leverage": "1:100",
    },
    {
        "name": "sell_filter_a",
        "hypothesis": "Sell dibuat lebih selektif dan lebih ringan supaya minus kasar berkurang.",
        "changes": {
            "IF1_SCORE_SELL_MIN_OVERRIDE": 80,
            "IF1_TREND_LOW_SCORE_SELL_MAX": 79,
            "IF1_SELL_LOT_MODIFIER_OVERRIDE": 0.65,
            "IF1_TREND_LOW_SCORE_SELL_LOT_MULT": 0.35,
        },
        "leverage": "1:100",
    },
    {
        "name": "sell_filter_b",
        "hypothesis": "Sell berkualitas rendah dipangkas lebih keras dan sell high-score wajib break bearish yang lebih jelas.",
        "changes": {
            "IF1_SCORE_SELL_MIN_OVERRIDE": 85,
            "IF1_TREND_LOW_SCORE_SELL_MAX": 79,
            "IF1_SELL_LOT_MODIFIER_OVERRIDE": 0.55,
            "IF1_TREND_LOW_SCORE_SELL_LOT_MULT": 0.25,
            "IF1_GOLD_HIGH_SCORE_SELL_MIN_LL_HH_EDGE": 1,
            "IF1_GOLD_HIGH_SCORE_SELL_MIN_BREAK_ATR_OVERRIDE": 0.18,
        },
        "leverage": "1:100",
    },
    {
        "name": "low_balance_a",
        "hypothesis": "Saat balance masih kecil, lot dan sideways exposure dibuat jauh lebih ringan.",
        "changes": {
            "IF1_VERY_LOW_BALANCE_CUTOFF_OVERRIDE": 400.0,
            "IF1_SIDEWAYS_LOT_MODIFIER_VERY_LOW_OVERRIDE": 0.04,
            "IF1_LOW_BALANCE_SELL_LOT_MODIFIER_OVERRIDE": 0.75,
            "IF1_LOW_BALANCE_BUY_LOT_MULT_OVERRIDE": 0.85,
        },
        "leverage": "1:100",
    },
    {
        "name": "low_balance_b",
        "hypothesis": "Versi paling defensif untuk exposure balance kecil.",
        "changes": {
            "IF1_VERY_LOW_BALANCE_CUTOFF_OVERRIDE": 500.0,
            "IF1_SIDEWAYS_LOT_MODIFIER_VERY_LOW_OVERRIDE": 0.03,
            "IF1_LOW_BALANCE_SELL_LOT_MODIFIER_OVERRIDE": 0.70,
            "IF1_LOW_BALANCE_BUY_LOT_MULT_OVERRIDE": 0.75,
        },
        "leverage": "1:100",
    },
    {
        "name": "combo_core",
        "hypothesis": "Gabungkan leverage lebih rendah, compounding lambat, cap posisi, dan daily loss cap.",
        "changes": {
            "IF1_COMPOUND_BALANCE_STEP_LOW_OVERRIDE": 400.0,
            "IF1_COMPOUND_BALANCE_STEP_MID_OVERRIDE": 500.0,
            "IF1_COMPOUND_BALANCE_STEP_HIGH_OVERRIDE": 650.0,
            "IF1_COMPOUND_BASE_LOT_MID_OVERRIDE": 0.52,
            "IF1_COMPOUND_BASE_LOT_HIGH_OVERRIDE": 1.12,
            "IF1_TREND_MAX_POSITIONS_VERY_LOW_OVERRIDE": 1,
            "IF1_TREND_MAX_POSITIONS_LOW_OVERRIDE": 3,
            "IF1_TREND_MAX_POSITIONS_MID_OVERRIDE": 5,
            "IF1_TREND_MAX_POSITIONS_HIGH_OVERRIDE": 7,
            "IF1_SIDEWAYS_MAX_POSITIONS_VERY_LOW_OVERRIDE": 1,
            "IF1_SIDEWAYS_MAX_POSITIONS_OVERRIDE": 3,
            "IF1_TREND_DAILY_LOSS_CAP_PCT_VERY_LOW_OVERRIDE": 4.0,
            "IF1_TREND_DAILY_LOSS_CAP_PCT_OVERRIDE": 6.0,
            "IF1_SIDEWAYS_DAILY_LOSS_CAP_PCT_VERY_LOW_OVERRIDE": 2.5,
            "IF1_SIDEWAYS_DAILY_LOSS_CAP_PCT_OVERRIDE": 3.5,
        },
        "leverage": "1:50",
    },
    {
        "name": "combo_core_buy",
        "hypothesis": "Tambah filter buy yang lebih ketat di atas paket risk core.",
        "changes": {
            "IF1_COMPOUND_BALANCE_STEP_LOW_OVERRIDE": 400.0,
            "IF1_COMPOUND_BALANCE_STEP_MID_OVERRIDE": 500.0,
            "IF1_COMPOUND_BALANCE_STEP_HIGH_OVERRIDE": 650.0,
            "IF1_COMPOUND_BASE_LOT_MID_OVERRIDE": 0.52,
            "IF1_COMPOUND_BASE_LOT_HIGH_OVERRIDE": 1.12,
            "IF1_TREND_MAX_POSITIONS_VERY_LOW_OVERRIDE": 1,
            "IF1_TREND_MAX_POSITIONS_LOW_OVERRIDE": 3,
            "IF1_TREND_MAX_POSITIONS_MID_OVERRIDE": 5,
            "IF1_TREND_MAX_POSITIONS_HIGH_OVERRIDE": 7,
            "IF1_SIDEWAYS_MAX_POSITIONS_VERY_LOW_OVERRIDE": 1,
            "IF1_SIDEWAYS_MAX_POSITIONS_OVERRIDE": 3,
            "IF1_TREND_DAILY_LOSS_CAP_PCT_VERY_LOW_OVERRIDE": 4.0,
            "IF1_TREND_DAILY_LOSS_CAP_PCT_OVERRIDE": 6.0,
            "IF1_SIDEWAYS_DAILY_LOSS_CAP_PCT_VERY_LOW_OVERRIDE": 2.5,
            "IF1_SIDEWAYS_DAILY_LOSS_CAP_PCT_OVERRIDE": 3.5,
            "IF1_BUY_MIN_BREAK_ATR_OVERRIDE": 0.30,
            "IF1_SCORE_BUY_MIN_OVERRIDE": 75,
        },
        "leverage": "1:50",
    },
    {
        "name": "combo_core_sell",
        "hypothesis": "Tambah filter sell defensif di atas paket risk core.",
        "changes": {
            "IF1_COMPOUND_BALANCE_STEP_LOW_OVERRIDE": 400.0,
            "IF1_COMPOUND_BALANCE_STEP_MID_OVERRIDE": 500.0,
            "IF1_COMPOUND_BALANCE_STEP_HIGH_OVERRIDE": 650.0,
            "IF1_COMPOUND_BASE_LOT_MID_OVERRIDE": 0.52,
            "IF1_COMPOUND_BASE_LOT_HIGH_OVERRIDE": 1.12,
            "IF1_TREND_MAX_POSITIONS_VERY_LOW_OVERRIDE": 1,
            "IF1_TREND_MAX_POSITIONS_LOW_OVERRIDE": 3,
            "IF1_TREND_MAX_POSITIONS_MID_OVERRIDE": 5,
            "IF1_TREND_MAX_POSITIONS_HIGH_OVERRIDE": 7,
            "IF1_SIDEWAYS_MAX_POSITIONS_VERY_LOW_OVERRIDE": 1,
            "IF1_SIDEWAYS_MAX_POSITIONS_OVERRIDE": 3,
            "IF1_TREND_DAILY_LOSS_CAP_PCT_VERY_LOW_OVERRIDE": 4.0,
            "IF1_TREND_DAILY_LOSS_CAP_PCT_OVERRIDE": 6.0,
            "IF1_SIDEWAYS_DAILY_LOSS_CAP_PCT_VERY_LOW_OVERRIDE": 2.5,
            "IF1_SIDEWAYS_DAILY_LOSS_CAP_PCT_OVERRIDE": 3.5,
            "IF1_SCORE_SELL_MIN_OVERRIDE": 80,
            "IF1_TREND_LOW_SCORE_SELL_MAX": 79,
            "IF1_SELL_LOT_MODIFIER_OVERRIDE": 0.65,
            "IF1_TREND_LOW_SCORE_SELL_LOT_MULT": 0.35,
        },
        "leverage": "1:50",
    },
    {
        "name": "combo_balanced",
        "hypothesis": "Paket seimbang: risk core + buy filter + sell filter + low-balance throttle.",
        "changes": {
            "IF1_COMPOUND_BALANCE_STEP_LOW_OVERRIDE": 400.0,
            "IF1_COMPOUND_BALANCE_STEP_MID_OVERRIDE": 500.0,
            "IF1_COMPOUND_BALANCE_STEP_HIGH_OVERRIDE": 650.0,
            "IF1_COMPOUND_BASE_LOT_MID_OVERRIDE": 0.52,
            "IF1_COMPOUND_BASE_LOT_HIGH_OVERRIDE": 1.12,
            "IF1_TREND_MAX_POSITIONS_VERY_LOW_OVERRIDE": 1,
            "IF1_TREND_MAX_POSITIONS_LOW_OVERRIDE": 3,
            "IF1_TREND_MAX_POSITIONS_MID_OVERRIDE": 5,
            "IF1_TREND_MAX_POSITIONS_HIGH_OVERRIDE": 7,
            "IF1_SIDEWAYS_MAX_POSITIONS_VERY_LOW_OVERRIDE": 1,
            "IF1_SIDEWAYS_MAX_POSITIONS_OVERRIDE": 3,
            "IF1_TREND_DAILY_LOSS_CAP_PCT_VERY_LOW_OVERRIDE": 4.0,
            "IF1_TREND_DAILY_LOSS_CAP_PCT_OVERRIDE": 6.0,
            "IF1_SIDEWAYS_DAILY_LOSS_CAP_PCT_VERY_LOW_OVERRIDE": 2.5,
            "IF1_SIDEWAYS_DAILY_LOSS_CAP_PCT_OVERRIDE": 3.5,
            "IF1_BUY_MIN_BREAK_ATR_OVERRIDE": 0.30,
            "IF1_SCORE_BUY_MIN_OVERRIDE": 75,
            "IF1_SCORE_SELL_MIN_OVERRIDE": 80,
            "IF1_TREND_LOW_SCORE_SELL_MAX": 79,
            "IF1_SELL_LOT_MODIFIER_OVERRIDE": 0.65,
            "IF1_TREND_LOW_SCORE_SELL_LOT_MULT": 0.35,
            "IF1_VERY_LOW_BALANCE_CUTOFF_OVERRIDE": 400.0,
            "IF1_SIDEWAYS_LOT_MODIFIER_VERY_LOW_OVERRIDE": 0.04,
            "IF1_LOW_BALANCE_SELL_LOT_MODIFIER_OVERRIDE": 0.75,
            "IF1_LOW_BALANCE_BUY_LOT_MULT_OVERRIDE": 0.85,
        },
        "leverage": "1:75",
    },
    {
        "name": "champion_challenge",
        "hypothesis": "Versi paling defensif yang tetap mencoba menjaga edge trend dan menahan sell buruk.",
        "changes": {
            "IF1_COMPOUND_BALANCE_STEP_LOW_OVERRIDE": 500.0,
            "IF1_COMPOUND_BALANCE_STEP_MID_OVERRIDE": 650.0,
            "IF1_COMPOUND_BALANCE_STEP_HIGH_OVERRIDE": 800.0,
            "IF1_COMPOUND_BASE_LOT_MID_OVERRIDE": 0.42,
            "IF1_COMPOUND_BASE_LOT_HIGH_OVERRIDE": 0.92,
            "IF1_TREND_MAX_POSITIONS_VERY_LOW_OVERRIDE": 1,
            "IF1_TREND_MAX_POSITIONS_LOW_OVERRIDE": 2,
            "IF1_TREND_MAX_POSITIONS_MID_OVERRIDE": 4,
            "IF1_TREND_MAX_POSITIONS_HIGH_OVERRIDE": 6,
            "IF1_SIDEWAYS_MAX_POSITIONS_VERY_LOW_OVERRIDE": 1,
            "IF1_SIDEWAYS_MAX_POSITIONS_OVERRIDE": 2,
            "IF1_TREND_DAILY_LOSS_CAP_PCT_VERY_LOW_OVERRIDE": 3.5,
            "IF1_TREND_DAILY_LOSS_CAP_PCT_OVERRIDE": 5.0,
            "IF1_SIDEWAYS_DAILY_LOSS_CAP_PCT_VERY_LOW_OVERRIDE": 2.0,
            "IF1_SIDEWAYS_DAILY_LOSS_CAP_PCT_OVERRIDE": 3.0,
            "IF1_BUY_MIN_BREAK_ATR_OVERRIDE": 0.32,
            "IF1_SCORE_BUY_MIN_OVERRIDE": 80,
            "IF1_BUY_MAX_ZONE_PRIOR_TESTS_OVERRIDE": 1,
            "IF1_SCORE_SELL_MIN_OVERRIDE": 80,
            "IF1_TREND_LOW_SCORE_SELL_MAX": 79,
            "IF1_SELL_LOT_MODIFIER_OVERRIDE": 0.60,
            "IF1_TREND_LOW_SCORE_SELL_LOT_MULT": 0.30,
            "IF1_GOLD_HIGH_SCORE_SELL_MIN_LL_HH_EDGE": 1,
            "IF1_GOLD_HIGH_SCORE_SELL_MIN_BREAK_ATR_OVERRIDE": 0.18,
            "IF1_VERY_LOW_BALANCE_CUTOFF_OVERRIDE": 500.0,
            "IF1_SIDEWAYS_LOT_MODIFIER_VERY_LOW_OVERRIDE": 0.03,
            "IF1_LOW_BALANCE_SELL_LOT_MODIFIER_OVERRIDE": 0.70,
            "IF1_LOW_BALANCE_BUY_LOT_MULT_OVERRIDE": 0.75,
        },
        "leverage": "1:50",
    },
]


@dataclass
class IterationResult:
    index: int
    name: str
    hypothesis: str
    params: dict[str, Any]
    leverage: str
    metrics: dict[str, float]
    tester_log: str
    trend_diag: dict[str, float]
    trend_dir_diag: dict[str, float]
    sell_score_diag: dict[str, float]
    trend_score_diag: dict[str, float]
    trend_exit_diag: dict[str, float]
    sell_exit_diag: dict[str, float]
    sideways_diag: dict[str, float]
    buy_hour_line: str
    sell_hour_line: str
    accepted: bool
    takeaway: str


def fmt_value(value: Any) -> str:
    if isinstance(value, bool):
        return("true" if value else "false")
    if isinstance(value, int):
        return(str(value))
    if isinstance(value, float):
        text = f"{value:.10f}".rstrip("0").rstrip(".")
        if "." not in text:
            text += ".0"
        return(text)
    raise TypeError(f"Unsupported value type: {type(value)!r}")


def patch_source(template: str, params: dict[str, Any]) -> str:
    result = template
    for name, value in params.items():
        pattern = re.compile(rf"(static const [^;\n]*\b{name}\b\s*=\s*)([^;]+)(;)")
        result, count = pattern.subn(lambda m: f"{m.group(1)}{fmt_value(value)}{m.group(3)}", result)
        if count != 1:
            raise RuntimeError(f"Failed to patch constant {name}")
    return(result)


def run_subprocess(args: list[str], *, quiet: bool = True) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["WINEPREFIX"] = str(WINEPREFIX)
    env["WINEDEBUG"] = "-all"
    kwargs: dict[str, Any] = {"cwd": ROOT, "env": env, "text": True, "check": False}
    if quiet:
        kwargs["stdout"] = subprocess.DEVNULL
        kwargs["stderr"] = subprocess.DEVNULL
    else:
        kwargs["stdout"] = subprocess.PIPE
        kwargs["stderr"] = subprocess.STDOUT
    return(subprocess.run(args, **kwargs))


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


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def latest_tester_log() -> Path | None:
    logs = sorted(TESTER_LOG_DIR.glob("*.log"), key=lambda p: p.stat().st_mtime)
    return(logs[-1] if logs else None)


def compile_variant(stem: str, source_text: str) -> None:
    source_path = MT5_BUILD / f"{stem}.mq5"
    compile_log = MT5_BUILD / f"{stem}.compile.log"
    write_file(source_path, source_text)
    run_subprocess([WINE, METAEDITOR_EXE, f"/compile:C:\\MT5Build\\{stem}.mq5", f"/log:C:\\MT5Build\\{stem}.compile.log"])
    log_text = compile_log.read_bytes().decode("utf-16le", errors="ignore")
    if "0 errors" not in log_text:
        raise RuntimeError(f"Compilation failed for {stem}: {log_text[-600:]}")


def build_ini(stem: str, leverage: str) -> str:
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
        FromDate=2025.10.18
        ToDate=2026.04.15
        ForwardMode=0
        Report=\\Reports\\{stem}_XAUUSDc_M15_20251018_20260415
        ReplaceReport=1
        ShutdownTerminal=1
        Deposit=100
        Currency=USD
        Leverage={leverage}
        UseLocal=1
        UseRemote=0
        UseCloud=0
        Visual=0
        """
    )


def run_backtest(stem: str, leverage: str) -> tuple[Path, Path | None]:
    ini_path = MT5_BUILD / f"{stem}.backtest.ini"
    write_file(ini_path, build_ini(stem, leverage))
    shutil.copy2(MT5_BUILD / f"{stem}.ex5", MT5_EXPERTS / f"{stem}.ex5")

    report_path = REPORTS_DIR / f"{stem}_XAUUSDc_M15_20251018_20260415.htm"
    for old in REPORTS_DIR.glob(f"{stem}_XAUUSDc_M15_20251018_20260415*"):
        old.unlink(missing_ok=True)

    pre_log = latest_tester_log()
    pre_size = pre_log.stat().st_size if pre_log and pre_log.exists() else 0
    proc = launch_subprocess([WINE, TERMINAL_EXE, f"/config:C:\\MT5Build\\{stem}.backtest.ini"])
    start_time = time.time()
    stable_size = -1
    stable_hits = 0
    deadline = time.time() + 600
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
    return(report_path, active_log)


def parse_report(report_path: Path) -> dict[str, float]:
    text = report_path.read_bytes().decode("utf-16le", errors="ignore")
    plain = re.sub(r"<[^>]+>", " ", text).replace("\xa0", " ")
    plain = re.sub(r"\s+", " ", plain)

    def extract(key: str) -> str:
        match = re.search(re.escape(key) + r"\s*([^:]{1,90})", plain)
        if not match:
            raise RuntimeError(f"Failed to parse {key} from {report_path}")
        return(match.group(1).strip())

    def first_number(value: str) -> float:
        match = re.search(r"-?[\d ]+(?:\.\d+)?", value)
        if not match:
            raise RuntimeError(f"No numeric value in {value!r}")
        return(float(match.group(0).replace(" ", "")))

    def first_pct(value: str) -> float:
        match = re.search(r"\(([\d.]+)%\)", value)
        if not match:
            raise RuntimeError(f"No percentage value in {value!r}")
        return(float(match.group(1)))

    return(
        {
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
    )


def parse_diag_line(log_path: Path | None, prefix: str) -> dict[str, float]:
    if log_path is None or not log_path.exists():
        return({})
    text = log_path.read_bytes().decode("utf-16le", errors="ignore")
    lines = [line for line in text.splitlines() if prefix in line]
    if not lines:
        return({})
    line = lines[-1]
    pairs = re.findall(r"([A-Za-z]+)=(-?[\d.]+)", line)
    return({key: float(value) for key, value in pairs})


def latest_prefixed_line(log_path: Path | None, prefix: str) -> str:
    if log_path is None or not log_path.exists():
        return("")
    text = log_path.read_bytes().decode("utf-16le", errors="ignore")
    lines = [line for line in text.splitlines() if prefix in line]
    return(lines[-1] if lines else "")


def acceptable(metrics: dict[str, float]) -> bool:
    return(
        metrics["net_profit"] > 0.0
        and metrics["profit_factor"] >= 1.03
        and metrics["total_trades"] >= 350
        and metrics["equity_dd_pct"] <= 95.0
    )


def score(metrics: dict[str, float]) -> float:
    dd_penalty = 1.0 + (metrics["equity_dd_pct"] / 35.0) ** 2
    wr_factor = max(metrics["profit_trades_pct"], 45.0) / 50.0
    return(metrics["net_profit"] * metrics["profit_factor"] * wr_factor / dd_penalty)


def better(metrics: dict[str, float], best: dict[str, float]) -> bool:
    if not acceptable(metrics):
        return(False)
    if not acceptable(best):
        return(True)
    if(
        metrics["equity_dd_pct"] <= best["equity_dd_pct"] - 12.0
        and metrics["net_profit"] >= best["net_profit"] * 0.78
        and metrics["profit_factor"] >= best["profit_factor"] - 0.02
    ):
        return(True)
    if(
        metrics["equity_dd_pct"] <= best["equity_dd_pct"] - 8.0
        and metrics["net_profit"] >= best["net_profit"] * 0.88
        and metrics["profit_factor"] >= best["profit_factor"] - 0.01
    ):
        return(True)
    if(
        metrics["equity_dd_pct"] <= best["equity_dd_pct"] - 5.0
        and metrics["net_profit"] >= best["net_profit"] * 0.95
        and metrics["profit_factor"] >= best["profit_factor"]
    ):
        return(True)
    if(
        metrics["net_profit"] >= best["net_profit"] * 1.15
        and metrics["equity_dd_pct"] <= best["equity_dd_pct"] - 3.0
        and metrics["profit_factor"] >= best["profit_factor"]
    ):
        return(True)
    return(score(metrics) > score(best) * 1.04)


def summarize_takeaway(
    metrics: dict[str, float],
    best: dict[str, float],
    trend_dir: dict[str, float],
    sell_score: dict[str, float],
) -> str:
    if not acceptable(metrics):
        if metrics["net_profit"] <= 0.0:
            return("Ditolak: profit berubah negatif.")
        if metrics["profit_factor"] < 1.03:
            return("Ditolak: profit factor terlalu lemah.")
        if metrics["total_trades"] < 350:
            return("Ditolak: trade count terlalu turun.")
        if metrics["equity_dd_pct"] > 95.0:
            return("Ditolak: drawdown masih ekstrem.")
        return("Ditolak: gagal guardrail utama.")
    if metrics["equity_dd_pct"] <= best["equity_dd_pct"] - 12.0:
        return("Promising: drawdown turun tajam dengan profit masih layak.")
    if metrics["equity_dd_pct"] < best["equity_dd_pct"] and metrics["net_profit"] >= best["net_profit"] * 0.95:
        return("Promising: risk turun dan profit tetap dekat champion.")
    if trend_dir.get("sellPnl", 0.0) > 0.0 and sell_score.get("lowPnl", 0.0) >= 0.0:
        return("Promising: sisi sell terlihat lebih bersih tanpa merusak total edge.")
    if metrics["profit_factor"] > best["profit_factor"] and metrics["equity_dd_pct"] <= best["equity_dd_pct"] + 2.0:
        return("Promising: expectancy membaik dengan risk relatif stabil.")
    return("Netral: ada perbaikan lokal, tapi belum cukup kuat untuk mengganti champion.")


def write_summary(results: list[IterationResult], champion: IterationResult) -> None:
    json_path = RUN_DIR / "v5_20x_results.json"
    md_path = RUN_DIR / "v5_20x_summary.md"
    notes_path = RUN_DIR / "v5_20x_notes.md"

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
                        "leverage": r.leverage,
                        "params": r.params,
                        "metrics": r.metrics,
                        "trend_diag": r.trend_diag,
                        "trend_dir_diag": r.trend_dir_diag,
                        "sell_score_diag": r.sell_score_diag,
                        "trend_score_diag": r.trend_score_diag,
                        "trend_exit_diag": r.trend_exit_diag,
                        "sell_exit_diag": r.sell_exit_diag,
                        "sideways_diag": r.sideways_diag,
                        "buy_hour_line": r.buy_hour_line,
                        "sell_hour_line": r.sell_hour_line,
                        "tester_log": r.tester_log,
                    }
                    for r in results
                ],
            },
            indent=2,
        )
    )

    lines = [
        "# v5 20x Summary",
        "",
        f"Champion: iterasi {champion.index:02d} `{champion.name}`",
        "Guardrail: net profit > 0, PF >= 1.03, trades >= 350, equity DD <= 95%",
        "",
        "| Iter | Name | Lev | Accepted | Net Profit | PF | WR | Trades | Eq DD | Buy PnL | Sell PnL | SW PnL | Trend TP/SL | Takeaway |",
        "| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    for r in results:
        lines.append(
            f"| {r.index:02d} | {r.name} | {r.leverage} | {'yes' if r.accepted else 'no'} | "
            f"{r.metrics['net_profit']:.2f} | {r.metrics['profit_factor']:.2f} | {r.metrics['profit_trades_pct']:.2f}% | "
            f"{int(r.metrics['total_trades'])} | {r.metrics['equity_dd_pct']:.2f}% | "
            f"{r.trend_dir_diag.get('buyPnl', 0.0):.2f} | {r.trend_dir_diag.get('sellPnl', 0.0):.2f} | "
            f"{r.sideways_diag.get('closedPnl', 0.0):.2f} | "
            f"{int(r.trend_exit_diag.get('tp', 0.0))}/{int(r.trend_exit_diag.get('sl', 0.0))} | "
            f"{r.takeaway} |"
        )
    md_path.write_text("\n".join(lines) + "\n")

    notes = [
        "# v5 Notes",
        "",
        f"Champion: `{champion.name}`",
        f"- Leverage: {champion.leverage}",
        f"- Net profit: {champion.metrics['net_profit']:.2f}",
        f"- Profit factor: {champion.metrics['profit_factor']:.2f}",
        f"- Win rate: {champion.metrics['profit_trades_pct']:.2f}%",
        f"- Trades: {int(champion.metrics['total_trades'])}",
        f"- Equity DD: {champion.metrics['equity_dd_pct']:.2f}%",
        f"- Trend buy pnl: {champion.trend_dir_diag.get('buyPnl', 0.0):.2f}",
        f"- Trend sell pnl: {champion.trend_dir_diag.get('sellPnl', 0.0):.2f}",
        f"- Sideways pnl: {champion.sideways_diag.get('closedPnl', 0.0):.2f}",
        f"- Trend exits tp/sl: {int(champion.trend_exit_diag.get('tp', 0.0))}/{int(champion.trend_exit_diag.get('sl', 0.0))}",
        f"- Sell exits tp/sl: {int(champion.sell_exit_diag.get('tp', 0.0))}/{int(champion.sell_exit_diag.get('sl', 0.0))}",
    ]
    if champion.buy_hour_line:
        notes.extend(["", "Buy hour line:", champion.buy_hour_line])
    if champion.sell_hour_line:
        notes.extend(["", "Sell hour line:", champion.sell_hour_line])
    notes_path.write_text("\n".join(notes) + "\n")


def main() -> None:
    template = EA_SOURCE.read_text()
    current_params = dict(BASE_PARAMS)
    current_leverage = "1:100"
    results: list[IterationResult] = []
    champion_result: IterationResult | None = None
    champion_metrics: dict[str, float] | None = None

    for idx, plan in enumerate(ITERATIONS, start=1):
        params = dict(current_params)
        params.update(plan["changes"])
        leverage = str(plan.get("leverage", current_leverage))
        stem = f"InvictusForward1M15_v5_iter{idx:02d}"
        source_text = patch_source(template, params)
        compile_variant(stem, source_text)
        report_path, tester_log = run_backtest(stem, leverage)
        metrics = parse_report(report_path)
        trend_diag = parse_diag_line(tester_log, "IF1 diag trend:")
        trend_dir_diag = parse_diag_line(tester_log, "IF1 diag trendDir:")
        sell_score_diag = parse_diag_line(tester_log, "IF1 diag sellScore:")
        trend_score_diag = parse_diag_line(tester_log, "IF1 diag trendScore:")
        trend_exit_diag = parse_diag_line(tester_log, "IF1 diag trendExit:")
        sell_exit_diag = parse_diag_line(tester_log, "IF1 diag sellExit:")
        sideways_diag = parse_diag_line(tester_log, "IF1 diag sideways:")
        buy_hour_line = latest_prefixed_line(tester_log, "IF1 diag buyHour:")
        sell_hour_line = latest_prefixed_line(tester_log, "IF1 diag sellHour:")

        if champion_metrics is None:
            accepted = acceptable(metrics)
            takeaway = "Baseline champion awal."
        else:
            accepted = better(metrics, champion_metrics)
            takeaway = summarize_takeaway(metrics, champion_metrics, trend_dir_diag, sell_score_diag)

        result = IterationResult(
            index=idx,
            name=plan["name"],
            hypothesis=plan["hypothesis"],
            params=params,
            leverage=leverage,
            metrics=metrics,
            tester_log=str(tester_log) if tester_log else "",
            trend_diag=trend_diag,
            trend_dir_diag=trend_dir_diag,
            sell_score_diag=sell_score_diag,
            trend_score_diag=trend_score_diag,
            trend_exit_diag=trend_exit_diag,
            sell_exit_diag=sell_exit_diag,
            sideways_diag=sideways_diag,
            buy_hour_line=buy_hour_line,
            sell_hour_line=sell_hour_line,
            accepted=accepted,
            takeaway=takeaway,
        )
        results.append(result)

        if champion_metrics is None or accepted:
            current_params = dict(params)
            current_leverage = leverage
            champion_metrics = dict(metrics)
            champion_result = result
            result.accepted = True
            if idx != 1:
                result.takeaway = "Dibawa ke baseline berikutnya."

        print(
            f"[{idx:02d}/{len(ITERATIONS):02d}] {plan['name']} lev={leverage}: "
            f"net={metrics['net_profit']:.2f} pf={metrics['profit_factor']:.2f} "
            f"wr={metrics['profit_trades_pct']:.2f}% trades={int(metrics['total_trades'])} "
            f"eqdd={metrics['equity_dd_pct']:.2f}% {'ACCEPT' if result.accepted else 'reject'}",
            flush=True,
        )

    if champion_result is None:
        raise RuntimeError("No champion result recorded")

    write_summary(results, champion_result)
    print()
    print(f"Champion iteration: {champion_result.index:02d} {champion_result.name}")
    print(f"Champion leverage: {champion_result.leverage}")
    print(f"Champion net profit: {champion_result.metrics['net_profit']:.2f}")
    print(f"Champion PF: {champion_result.metrics['profit_factor']:.2f}")
    print(f"Champion WR: {champion_result.metrics['profit_trades_pct']:.2f}%")
    print(f"Champion trades: {int(champion_result.metrics['total_trades'])}")
    print(f"Champion equity DD: {champion_result.metrics['equity_dd_pct']:.2f}%")


if __name__ == "__main__":
    main()
