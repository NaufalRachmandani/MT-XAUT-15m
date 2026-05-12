#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import random
import shutil
import statistics
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "invictusforward-8-research" / "tools"))

import run_invictus8_v5_quality_boost as mt5  # noqa: E402
from analyze_mt5_report import (  # noqa: E402
    extract_deal_rows,
    read_report,
    reconstruct_closed_trades,
)


RESEARCH = ROOT / "invictusforward-8-research"
EXP_ROOT = RESEARCH / "invictus8_v8_risk_certified"
SRC_ROOT = EXP_ROOT / "source"
SETS_DIR = EXP_ROOT / "sets"
STRESS_DIR = EXP_ROOT / "native_stress"
REPORT_DIR = EXP_ROOT / "reports"

V8 = mt5.ExpertSpec(
    "v8riskcert",
    "V8 Risk Certified",
    SRC_ROOT / "v8riskcert",
    "InvictusForward-8-V8RiskCertified.mq5",
    "InvictusForward8_V8RC_V8Risk",
    "InvictusForward-8-V8RiskCertified.ex5",
)

CENT = mt5.AccountSpec("cent", "Cent Real25", "184000633", "Exness-MT5Real25", "XAUUSDc", "USC")
USD = mt5.AccountSpec("usd_real38", "USD Real38", "265874264", "Exness-MT5Real38", "XAUUSD", "USD")

CENT_WINDOWS = [
    mt5.WindowSpec("oos_may", "Cent OOS May", "2026.05.01", "2026.05.10"),
    mt5.WindowSpec("last_month", "Cent Last Month", "2026.04.10", "2026.05.10"),
    mt5.WindowSpec("ytd_2026", "Cent 2026 YTD", "2026.01.01", "2026.05.10"),
]
USD_WINDOWS = [
    mt5.WindowSpec("usd_jun_dec_2025", "USD Jun-Dec 2025", "2025.06.01", "2025.12.31"),
    mt5.WindowSpec("usd_jun2025_now", "USD Jun2025-Now", "2025.06.01", "2026.05.10"),
]

CENT_DELAYS = [0, 100, 300, 500]
USD_DELAYS = [100, 300]

BASE_SETS = {
    "v5max_raw": {
        "label": "V5 max raw",
        "path": RESEARCH / "invictus8_v5_quality_boost" / "sets" / "InvictusForward8_v5_max_profit_scaled.set",
        "purpose": "Profit baseline favorite, no V8 risk throttle.",
    },
    "v6balance_raw": {
        "label": "V6 profit-balanced raw",
        "path": RESEARCH / "invictus8_v6_jun2025_archive_boost" / "sets" / "InvictusForward8_V6_selected_profit_balanced_not_live.set",
        "purpose": "Safer archive baseline, no V8 risk throttle.",
    },
    "v7h8m25_raw": {
        "label": "V7 soft H8 m25 raw",
        "path": RESEARCH / "invictus8_v7_live_risk_candidate" / "sets" / "InvictusForward8_V7_selected_soft_h8_m25_profit_candidate_not_live.set",
        "purpose": "Latest profit candidate, no V8 risk throttle.",
    },
}

RISK_MODERATE = {
    "V7_EnableRiskGuard": True,
    "V7_EquityDDSoftPct": 10.0,
    "V7_EquityDDSoftLotMult": 0.50,
    "V7_EquityDDHardPct": 18.0,
    "V7_EquityDDHardLotMult": 0.25,
    "V7_StopTradingDDPct": 35.0,
    "V7_DailyEquityLossPct": 4.0,
    "V7_LargeLossPct": 4.0,
    "V7_LargeLossCooldownBars": 32,
    "V7_MaxTotalPositions": 3,
    "V7_BalanceBelowLotCap": 20000.0,
    "V7_LowBalanceMaxLot": 0.75,
}

RISK_STRICT = {
    "V7_EnableRiskGuard": True,
    "V7_EquityDDSoftPct": 8.0,
    "V7_EquityDDSoftLotMult": 0.40,
    "V7_EquityDDHardPct": 14.0,
    "V7_EquityDDHardLotMult": 0.20,
    "V7_StopTradingDDPct": 25.0,
    "V7_DailyEquityLossPct": 3.0,
    "V7_LargeLossPct": 3.5,
    "V7_LargeLossCooldownBars": 48,
    "V7_MaxTotalPositions": 2,
    "V7_BalanceBelowLotCap": 20000.0,
    "V7_LowBalanceMaxLot": 0.50,
}

MICRO_200_CAP100 = {
    "BT_CompoundingPer": 200.0,
    "BT_MaxLotCap": 1.00,
    "V7_EnableRiskGuard": False,
}

MICRO_250_CAP075 = {
    "BT_CompoundingPer": 250.0,
    "BT_MaxLotCap": 0.75,
    "V7_EnableRiskGuard": False,
}


def patch_mt5_globals() -> None:
    mt5.EXP_ROOT = EXP_ROOT
    mt5.SETS_DIR = SETS_DIR
    mt5.CENT_DIR = STRESS_DIR
    mt5.REPORT_DIR = REPORT_DIR

    def stem(case: mt5.CaseSpec) -> str:
        start = case.window.from_date.replace(".", "")
        end = case.window.to_date.replace(".", "")
        return (
            f"InvictusForward8_V8RC_{case.account.key}_{case.expert.key}_{case.variant_key}_"
            f"{case.window.key}_d{case.deposit}{case.account.currency}_{case.account.symbol}_{mt5.PERIOD}_"
            f"lev2000_delay{mt5.EXECUTION_MODE_MS}_model{mt5.MODEL}_{start}_{end}"
        )

    mt5.report_stem = stem


def ensure_dirs() -> None:
    for directory in (EXP_ROOT, SRC_ROOT, SETS_DIR, STRESS_DIR, REPORT_DIR, mt5.MT5_BUILD, mt5.PROFILES_TESTER):
        directory.mkdir(parents=True, exist_ok=True)


def decode_set_text(path: Path) -> str:
    data = path.read_bytes()
    for encoding in ("utf-16le", "utf-8"):
        text = data.decode(encoding, errors="ignore")
        if "=" in text:
            return text.lstrip("\ufeff")
    return data.decode("utf-16le", errors="ignore").lstrip("\ufeff")


def parse_value(value: str) -> Any:
    raw = value.split("||", 1)[0].strip()
    low = raw.lower()
    if low == "true":
        return True
    if low == "false":
        return False
    try:
        if "." in raw:
            return float(raw)
        return int(raw)
    except ValueError:
        return raw


def read_set(path: Path) -> dict[str, Any]:
    values: dict[str, Any] = {}
    for line in decode_set_text(path).splitlines():
        line = line.strip()
        if not line or line.startswith(";") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = parse_value(value)
    return values


def set_value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, float):
        return f"{value:.10g}"
    return str(value)


def write_set(path: Path, values: dict[str, Any], note: str) -> Path:
    lines = [f"; {note}", "; Native MT5 Strategy Tester set; generated for V8 risk-certified validation"]
    for key, value in values.items():
        v = set_value(value)
        lines.append(f"{key}={v}||{v}||0||{v}||N")
    text = "\r\n".join(lines) + "\r\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"\xff\xfe" + text.encode("utf-16le"))
    shutil.copy2(path, mt5.PROFILES_TESTER / path.name)
    return path


def build_sets() -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for key, spec in BASE_SETS.items():
        values = read_set(Path(spec["path"]))
        values.setdefault("V7_EnableRiskGuard", False)
        path = write_set(SETS_DIR / f"InvictusForward8_V8_{key}.set", values, str(spec["purpose"]))
        output.append({"key": key, "label": spec["label"], "path": path, "purpose": spec["purpose"], "values": values})

    derived = [
        ("v8_v5max_guard_moderate", "V8 V5max guard moderate", "v5max_raw", RISK_MODERATE),
        ("v8_v5max_guard_strict", "V8 V5max guard strict", "v5max_raw", RISK_STRICT),
        ("v8_v6balance_guard_moderate", "V8 V6balance guard moderate", "v6balance_raw", RISK_MODERATE),
        ("v8_v7h8m25_guard_moderate", "V8 V7H8m25 guard moderate", "v7h8m25_raw", RISK_MODERATE),
        ("v8_v5max_micro200_cap100", "V8 V5max micro 200 cap1.00", "v5max_raw", MICRO_200_CAP100),
        ("v8_v6balance_micro200_cap100", "V8 V6balance micro 200 cap1.00", "v6balance_raw", MICRO_200_CAP100),
        ("v8_v6balance_micro250_cap075", "V8 V6balance micro 250 cap0.75", "v6balance_raw", MICRO_250_CAP075),
        ("v8_v7h8m25_micro200_cap100", "V8 V7H8m25 micro 200 cap1.00", "v7h8m25_raw", MICRO_200_CAP100),
        ("v8_v7h8m25_micro250_cap075", "V8 V7H8m25 micro 250 cap0.75", "v7h8m25_raw", MICRO_250_CAP075),
    ]
    base_values = {row["key"]: dict(row["values"]) for row in output}
    for key, label, base_key, overrides in derived:
        values = dict(base_values[base_key])
        values.update(overrides)
        path = write_set(SETS_DIR / f"InvictusForward8_V8_{key}.set", values, f"{label}; base={base_key}")
        output.append({"key": key, "label": label, "path": path, "purpose": f"Risk guard over {base_key}", "values": values})
    return output


def run_matrix(profiles: list[dict[str, Any]], timeout: int, force: bool) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for profile in profiles:
        for delay in CENT_DELAYS:
            mt5.EXECUTION_MODE_MS = delay
            for window in CENT_WINDOWS:
                case = mt5.CaseSpec(V8, CENT, window, 1000, str(profile["key"]), str(profile["label"]), Path(profile["path"]))
                row = mt5.run_case(case, timeout, STRESS_DIR / "cent", force=force)
                row["delay_ms"] = delay
                rows.append(row)
                print(f"cent delay={delay} {profile['key']} {window.key}: net={row['net']} pf={row['profit_factor']} dd={row['equity_dd_pct']} history={row['history_quality']}", flush=True)

        for delay in USD_DELAYS:
            mt5.EXECUTION_MODE_MS = delay
            for window in USD_WINDOWS:
                case = mt5.CaseSpec(V8, USD, window, 1000, str(profile["key"]), str(profile["label"]), Path(profile["path"]))
                row = mt5.run_case(case, timeout, STRESS_DIR / "usd", force=force)
                row["delay_ms"] = delay
                rows.append(row)
                print(f"usd delay={delay} {profile['key']} {window.key}: net={row['net']} pf={row['profit_factor']} dd={row['equity_dd_pct']} history={row['history_quality']}", flush=True)
    return rows


def max_drawdown_pct(profits: list[float], start_balance: float) -> float:
    equity = start_balance
    peak = start_balance
    max_dd = 0.0
    for profit in profits:
        equity += profit
        peak = max(peak, equity)
        if peak > 0:
            max_dd = max(max_dd, (peak - equity) / peak * 100.0)
    return max_dd


def monte_carlo_for_report(row: dict[str, Any], iterations: int = 5000) -> dict[str, Any]:
    report = Path(str(row["report"]))
    trades, unmatched = reconstruct_closed_trades(extract_deal_rows(read_report(report)))
    profits = [float(trade.profit) for trade in trades]
    start = float(row.get("deposit") or row.get("initial_deposit") or 1000.0)
    if not profits:
        return {"profile": row["variant_key"], "window_key": row["window_key"], "delay_ms": row["delay_ms"], "trade_count": 0}
    rng = random.Random(20260511)
    dds: list[float] = []
    min_equities: list[float] = []
    ruin_count = 0
    for _ in range(iterations):
        sample = profits[:]
        rng.shuffle(sample)
        equity = start
        min_equity = start
        peak = start
        max_dd = 0.0
        for profit in sample:
            equity += profit
            min_equity = min(min_equity, equity)
            peak = max(peak, equity)
            if peak > 0:
                max_dd = max(max_dd, (peak - equity) / peak * 100.0)
        if min_equity <= 0:
            ruin_count += 1
        dds.append(max_dd)
        min_equities.append(min_equity)
    dds.sort()
    min_equities.sort()
    def pct(values: list[float], q: float) -> float:
        index = min(len(values) - 1, max(0, int(round((len(values) - 1) * q))))
        return values[index]
    return {
        "profile": row["variant_key"],
        "label": row["variant"],
        "account_key": row["account_key"],
        "window_key": row["window_key"],
        "delay_ms": row["delay_ms"],
        "trade_count": len(profits),
        "unmatched_deals": len(unmatched),
        "native_net": row["net"],
        "native_equity_dd_pct": row["equity_dd_pct"],
        "native_largest_loss_abs": row["largest_loss_abs"],
        "mc_iterations": iterations,
        "mc_dd_median_pct": pct(dds, 0.50),
        "mc_dd_p95_pct": pct(dds, 0.95),
        "mc_dd_p99_pct": pct(dds, 0.99),
        "mc_min_equity_p05": pct(min_equities, 0.05),
        "mc_ruin_rate_pct": ruin_count / iterations * 100.0,
    }


def run_monte_carlo(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    for row in rows:
        if row["delay_ms"] != 100:
            continue
        if row["window_key"] in {"ytd_2026", "usd_jun2025_now"}:
            selected.append(row)
    return [monte_carlo_for_report(row) for row in selected]


def summarize_profiles(rows: list[dict[str, Any]], mc_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_profile: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        by_profile.setdefault(str(row["variant_key"]), []).append(row)
    mc_by_key = {(m["profile"], m["account_key"], m["window_key"], m["delay_ms"]): m for m in mc_rows}
    summary: list[dict[str, Any]] = []
    for key, items in by_profile.items():
        cent_ytd = [r for r in items if r["account_key"] == "cent" and r["window_key"] == "ytd_2026"]
        cent_last = [r for r in items if r["account_key"] == "cent" and r["window_key"] == "last_month"]
        cent_may = [r for r in items if r["account_key"] == "cent" and r["window_key"] == "oos_may"]
        usd_archive = [r for r in items if r["account_key"] == "usd_real38" and r["window_key"] == "usd_jun2025_now"]
        all_rows = cent_ytd + cent_last + cent_may + usd_archive
        fail: list[str] = []
        for row in all_rows:
            if row["validation_issues"]:
                fail.append(f"{row['account_key']}:{row['window_key']}: {row['validation_issues']}")
            if float(row["net"]) <= 0:
                fail.append(f"{row['account_key']}:{row['window_key']}: net <= 0 at delay {row['delay_ms']}")
            if row["account_key"] == "cent" and row["window_key"] in {"last_month", "oos_may"} and float(row["profit_factor"]) not in (0.0,) and float(row["profit_factor"]) < 1.20:
                fail.append(f"{row['window_key']}: PF < 1.20 at delay {row['delay_ms']}")
        max_cent_ytd_dd = max([float(r["equity_dd_pct"]) for r in cent_ytd] or [999.0])
        min_cent_ytd_net = min([float(r["net"]) for r in cent_ytd] or [0.0])
        max_cent_ytd_ll = max([float(r["largest_loss_abs"]) for r in cent_ytd] or [0.0])
        max_usd_archive_dd = max([float(r["equity_dd_pct"]) for r in usd_archive] or [999.0])
        min_usd_archive_net = min([float(r["net"]) for r in usd_archive] or [0.0])
        mc_cent = mc_by_key.get((key, "cent", "ytd_2026", 100), {})
        mc_usd = mc_by_key.get((key, "usd_real38", "usd_jun2025_now", 100), {})
        mc_p95 = max(float(mc_cent.get("mc_dd_p95_pct", 0.0)), float(mc_usd.get("mc_dd_p95_pct", 0.0)))
        if max_cent_ytd_dd > 30.0:
            fail.append("cent YTD DD > 30% under delay stress")
        if max_usd_archive_dd > 45.0:
            fail.append("USD archive DD > 45% under delay stress")
        if mc_p95 > 40.0:
            fail.append("Monte Carlo p95 DD > 40%")
        score = (
            min_cent_ytd_net
            + min_usd_archive_net * 0.25
            - max_cent_ytd_dd * 350.0
            - max_usd_archive_dd * 120.0
            - max_cent_ytd_ll * 1.5
            - mc_p95 * 100.0
        )
        first = items[0]
        summary.append({
            "profile": key,
            "label": first["variant"],
            "score": score,
            "live_ready": not fail,
            "fail_reasons": fail,
            "min_cent_ytd_net": min_cent_ytd_net,
            "max_cent_ytd_dd_pct": max_cent_ytd_dd,
            "max_cent_ytd_largest_loss_abs": max_cent_ytd_ll,
            "min_usd_archive_net": min_usd_archive_net,
            "max_usd_archive_dd_pct": max_usd_archive_dd,
            "max_mc_p95_dd_pct": mc_p95,
        })
    summary.sort(key=lambda item: float(item["score"]), reverse=True)
    return summary


def fmt(value: Any, digits: int = 2) -> str:
    if isinstance(value, (int, float)):
        return f"{float(value):,.{digits}f}"
    return str(value)


def write_reports(rows: list[dict[str, Any]], profiles: list[dict[str, Any]], mc_rows: list[dict[str, Any]]) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    profile_summary = summarize_profiles(rows, mc_rows)
    (REPORT_DIR / "results.json").write_text(json.dumps(rows, indent=2, default=str) + "\n", encoding="utf-8")
    (REPORT_DIR / "monte_carlo.json").write_text(json.dumps(mc_rows, indent=2, default=str) + "\n", encoding="utf-8")
    (REPORT_DIR / "comparison.json").write_text(json.dumps(profile_summary, indent=2, default=str) + "\n", encoding="utf-8")

    lines = [
        "# Invictus Forward-8 V8 Risk-Certified Stress Validation",
        "",
        "Authority: native MT5 Strategy Tester `.htm` reports. Python was used only for orchestration, parsing, and Monte Carlo trade-order stress from native report deals.",
        "",
        "Safety: all generated tester configs use `AllowLiveTrading=0`, `Visual=0`, `ShutdownTerminal=1`, `UseRemote=0`, `UseCloud=0`, and sound events disabled.",
        "",
        "## Candidate Ranking",
        "",
        "| Rank | Profile | Score | Live-ready | Min cent YTD net | Max cent YTD DD | Max cent YTD LL | Min USD archive net | Max USD archive DD | Max MC p95 DD | Fail reasons |",
        "| ---: | --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for idx, row in enumerate(profile_summary, 1):
        reasons = "; ".join(row["fail_reasons"]) if row["fail_reasons"] else "OK"
        lines.append(
            f"| {idx} | {row['label']} | {fmt(row['score'])} | {'yes' if row['live_ready'] else 'no'} | "
            f"{fmt(row['min_cent_ytd_net'])} | {fmt(row['max_cent_ytd_dd_pct'])}% | {fmt(row['max_cent_ytd_largest_loss_abs'])} | "
            f"{fmt(row['min_usd_archive_net'])} | {fmt(row['max_usd_archive_dd_pct'])}% | {fmt(row['max_mc_p95_dd_pct'])}% | {reasons} |"
        )

    lines.extend([
        "",
        "## Native Stress Matrix",
        "",
        "| Profile | Account | Window | Delay | Net | PF | Trades | Win rate | Eq DD | Largest loss | History | Validation |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- | ---: | --- | --- |",
    ])
    for row in sorted(rows, key=lambda r: (str(r["variant_key"]), str(r["account_key"]), str(r["window_key"]), int(r["delay_ms"]))):
        validation = "OK" if not row["validation_issues"] else "; ".join(map(str, row["validation_issues"]))
        lines.append(
            f"| {row['variant']} | {row['account_key']} | {row['window_key']} | {row['delay_ms']} | "
            f"{fmt(row['net'])} | {fmt(row['profit_factor'])} | {int(row['trades'])} | {fmt(row['win_rate_pct'])}% | "
            f"{row['equity_dd']} | {fmt(row['largest_loss_abs'])} | {row['history_quality']} | {validation} |"
        )

    lines.extend([
        "",
        "## Monte Carlo Trade-Order Stress",
        "",
        "| Profile | Account | Window | Delay | Trades | Native DD | MC median DD | MC p95 DD | MC p99 DD | MC ruin rate |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ])
    for row in mc_rows:
        lines.append(
            f"| {row['label']} | {row['account_key']} | {row['window_key']} | {row['delay_ms']} | "
            f"{row['trade_count']} | {fmt(row.get('native_equity_dd_pct', 0.0))}% | {fmt(row.get('mc_dd_median_pct', 0.0))}% | "
            f"{fmt(row.get('mc_dd_p95_pct', 0.0))}% | {fmt(row.get('mc_dd_p99_pct', 0.0))}% | {fmt(row.get('mc_ruin_rate_pct', 0.0))}% |"
        )

    best = profile_summary[0] if profile_summary else {}
    lines.extend([
        "",
        "## Decision",
        "",
        f"Best scored candidate: `{best.get('label', 'n/a')}`.",
        "",
        "A profile is marked live-ready only if it remains net-positive under delay stress, keeps cent YTD DD at or below 30%, keeps USD Jun2025-now DD at or below 45%, and Monte Carlo p95 DD at or below 40%. If no profile passes, the correct recommendation is not live-ready.",
        "",
        "## Files",
        "",
        f"- Results: `{REPORT_DIR / 'results.json'}`",
        f"- Comparison: `{REPORT_DIR / 'comparison.json'}`",
        f"- Monte Carlo: `{REPORT_DIR / 'monte_carlo.json'}`",
        f"- Native reports: `{STRESS_DIR}`",
    ])
    (REPORT_DIR / "SUMMARY.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    diff_lines = [
        "# V8 Parameter Profiles",
        "",
        "| Profile | Source set | Risk guard | Purpose | Set file |",
        "| --- | --- | --- | --- | --- |",
    ]
    for profile in profiles:
        values = profile["values"]
        diff_lines.append(
            f"| {profile['label']} | {profile['key']} | {values.get('V7_EnableRiskGuard', False)} | "
            f"{profile['purpose']} | `{profile['path']}` |"
        )
    (REPORT_DIR / "PARAM_DIFF.md").write_text("\n".join(diff_lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--timeout", type=int, default=3600)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--compile-only", action="store_true")
    args = parser.parse_args()

    patch_mt5_globals()
    ensure_dirs()
    profiles = build_sets()
    mt5.compile_expert(V8)
    if args.compile_only:
        print(f"compiled {V8.label}")
        return
    rows = run_matrix(profiles, args.timeout, args.force)
    mc_rows = run_monte_carlo(rows)
    write_reports(rows, profiles, mc_rows)
    print(f"wrote {REPORT_DIR / 'SUMMARY.md'}", flush=True)


if __name__ == "__main__":
    main()
