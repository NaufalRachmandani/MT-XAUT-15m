#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path("/Users/naufalrachmandani/Hobby/MT5 XAU 15m")
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.backtest_v11_split import compile_exact, latest_tester_log, parse_report, run_backtest  # noqa: E402
from tools.iterate_v11_10x import load_set, write_tester_set  # noqa: E402

RUN_DIR = ROOT / "build" / "v11_diagnostics"
RUN_DIR.mkdir(parents=True, exist_ok=True)


def read_log_delta(pre_log: Path | None, pre_size: int) -> str:
    post_log = latest_tester_log()
    if post_log is None or not post_log.exists():
        return ""
    raw = post_log.read_bytes()
    if pre_log is not None and post_log == pre_log:
        raw = raw[pre_size:]
    return raw.decode("utf-16le", errors="ignore")


def count_matches(lines: list[str], pattern: str) -> Counter[str]:
    counter: Counter[str] = Counter()
    regex = re.compile(pattern)
    for line in lines:
        match = regex.search(line)
        if match:
            counter[match.group(1)] += 1
    return counter


def main() -> None:
    stem = "InvictusBearM5_v11"
    base_set = "InvictusBearM5_v11.default_2026.set"
    compile_exact(stem)
    values = load_set(ROOT / "mt5" / base_set)
    values.update(
        {
            "V11_LogRejectedSignals": "true",
            "V11_MinRejectedScoreToLog": "50",
            "V11_LogExitActions": "true",
            "V11_LogStatusOnNewBar": "false",
        }
    )
    set_name = write_tester_set(stem, "diagnostic_recent", values)
    pre_log = latest_tester_log()
    pre_size = pre_log.stat().st_size if pre_log is not None and pre_log.exists() else 0
    report = run_backtest(stem, set_name, "2026.04.01", "2026.04.25")
    text = read_log_delta(pre_log, pre_size)
    lines = [line for line in text.splitlines() if "V11 " in line]
    reject_lines = [line for line in lines if "V11 REJECT" in line]
    entry_lines = [line for line in lines if "V11 ENTRY" in line]
    exit_lines = [line for line in lines if "V11 EXIT" in line]

    result = {
        "bot": stem,
        "window": "2026.04.01-2026.04.25",
        "report": str(report),
        "metrics": parse_report(report),
        "entries": len(entry_lines),
        "exits": len(exit_lines),
        "rejects": len(reject_lines),
        "reject_by_engine": dict(count_matches(reject_lines, r"engine=.*\\(([^)]+)\\)")),
        "reject_by_reason": dict(count_matches(reject_lines, r"reason=([^|]+)")),
        "exit_by_action": dict(count_matches(exit_lines, r"V11 EXIT ([^|]+)")),
        "sample_rejects": reject_lines[:20],
    }

    (RUN_DIR / "bear_recent_diagnostics.json").write_text(json.dumps(result, indent=2))
    lines_out = [
        "# v11 Bear Recent Diagnostics",
        "",
        "Setup: `InvictusBearM5_v11`, `XAUUSDc`, `M5`, `2026.04.01-2026.04.25`, diagnostic reject log enabled.",
        "",
        f"- Entries: `{result['entries']}`",
        f"- Exits: `{result['exits']}`",
        f"- Rejects near threshold: `{result['rejects']}`",
        f"- Reject by engine: `{result['reject_by_engine']}`",
        f"- Reject by reason: `{result['reject_by_reason']}`",
        f"- Exit by action: `{result['exit_by_action']}`",
    ]
    (RUN_DIR / "summary.md").write_text("\n".join(lines_out) + "\n")
    print(RUN_DIR / "summary.md")


if __name__ == "__main__":
    main()
