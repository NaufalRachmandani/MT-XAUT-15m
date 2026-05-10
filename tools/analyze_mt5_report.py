#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import html
import json
import math
import re
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Iterable


ENGINE_NAMES = {
    "BO": "BUY_BREAK",
    "PB": "BUY_PULLBACK",
    "ZB": "BUY_ZONE",
    "IB": "BUY_IMPULSE",
    "SB": "BUY_COMP",
    "AB": "BUY_ADDON",
    "BE": "SELL_BREAK",
    "ZS": "SELL_ZONE",
    "IS": "SELL_IMPULSE",
    "SS": "SELL_COMP",
    "AS": "SELL_ADDON",
}

TAG_NAMES = {
    "RG": "strong regime",
    "WG": "weak regime",
    "CH": "core hour",
    "XH": "outside hour",
    "X": "outside hour (truncated)",
    "ZN": "zone retest",
    "RT": "retest",
    "RJ": "rejection",
    "AD": "add-on",
    "CT": "continuation",
    "RC": "reclaim/continuation",
}


@dataclass
class Position:
    entry_time: datetime
    side: str
    volume: float
    entry_price: float
    deal_id: str
    order_id: str
    comment: str


@dataclass
class ClosedTrade:
    entry_time: datetime
    exit_time: datetime
    side: str
    volume: float
    entry_price: float
    exit_price: float
    profit: float
    balance: float
    entry_deal_id: str
    entry_order_id: str
    exit_deal_id: str
    exit_order_id: str
    entry_comment: str
    exit_comment: str
    match_error: float
    hold_minutes: float


def parse_float(value: str) -> float:
    value = value.strip().replace(" ", "")
    if value == "":
        return 0.0
    return float(value)


def read_report(path: Path) -> str:
    return path.read_bytes().decode("utf-16le", errors="ignore")


def plain_report_text(text: str) -> str:
    plain = re.sub(r"<[^>]+>", " ", text).replace("\xa0", " ")
    return re.sub(r"\s+", " ", plain)


def parse_report_metrics(text: str) -> dict[str, str]:
    plain = plain_report_text(text)
    keys = [
        "Total Net Profit:",
        "Gross Profit:",
        "Gross Loss:",
        "Profit Factor:",
        "Expected Payoff:",
        "Total Trades:",
        "Profit Trades (% of total):",
        "Loss Trades (% of total):",
        "Balance Drawdown Maximal:",
        "Equity Drawdown Maximal:",
        "Largest loss trade:",
        "Average loss trade:",
        "Maximum consecutive losses ($):",
        "Maximal consecutive loss (count):",
        "Average consecutive losses:",
    ]
    metrics: dict[str, str] = {}
    for key in keys:
        match = re.search(re.escape(key) + r"\s*([^:]{1,120})", plain)
        metrics[key] = match.group(1).strip() if match else ""
    return metrics


def parse_first_number(value: str) -> float:
    match = re.search(r"-?[\d ]+(?:\.\d+)?", value)
    return float(match.group(0).replace(" ", "")) if match else 0.0


def clean_cell(cell_html: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", "", cell_html)).strip().replace("\xa0", " ")


def iter_rows(text: str) -> Iterable[list[str]]:
    for row_html in re.findall(r"<tr[^>]*>(.*?)</tr>", text, flags=re.S | re.I):
        cells = [clean_cell(cell) for cell in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", row_html, flags=re.S | re.I)]
        if cells:
            yield cells


def extract_deal_rows(text: str) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for cols in iter_rows(text):
        if len(cols) != 13:
            continue
        if cols[0] in {"Time", ""} or cols[3] == "balance":
            continue
        if cols[4] not in {"in", "out"}:
            continue
        try:
            ts = datetime.strptime(cols[0], "%Y.%m.%d %H:%M:%S")
        except ValueError:
            continue
        rows.append(
            {
                "time": ts,
                "deal": cols[1],
                "symbol": cols[2],
                "type": cols[3],
                "direction": cols[4],
                "volume": parse_float(cols[5]),
                "price": parse_float(cols[6]),
                "order": cols[7],
                "commission": parse_float(cols[8]),
                "swap": parse_float(cols[9]),
                "profit": parse_float(cols[10]),
                "balance": parse_float(cols[11]),
                "comment": cols[12],
            }
        )
    return rows


def closed_side_for_exit(deal_type: str) -> str:
    if deal_type == "sell":
        return "buy"
    if deal_type == "buy":
        return "sell"
    return ""


def expected_profit(side: str, entry_price: float, exit_price: float, volume: float) -> float:
    if side == "buy":
        return (exit_price - entry_price) * volume
    if side == "sell":
        return (entry_price - exit_price) * volume
    return 0.0


def match_exit_to_position(positions: list[Position], side: str, volume: float, exit_price: float, profit: float) -> tuple[int, float]:
    candidates: list[tuple[float, float, int]] = []
    for index, position in enumerate(positions):
        if position.side != side:
            continue
        if position.volume + 1e-9 < volume:
            continue
        expected = expected_profit(side, position.entry_price, exit_price, volume)
        candidates.append((abs(expected - profit), abs(position.volume - volume), index))
    if not candidates:
        return -1, math.inf
    candidates.sort(key=lambda row: (row[0], row[1], row[2]))
    return candidates[0][2], candidates[0][0]


def reconstruct_closed_trades(deals: list[dict[str, object]]) -> tuple[list[ClosedTrade], list[dict[str, object]]]:
    positions: list[Position] = []
    closed: list[ClosedTrade] = []
    unmatched: list[dict[str, object]] = []

    for deal in deals:
        direction = str(deal["direction"])
        deal_type = str(deal["type"])
        volume = float(deal["volume"])
        price = float(deal["price"])
        timestamp = deal["time"]
        assert isinstance(timestamp, datetime)

        if direction == "in" and deal_type in {"buy", "sell"}:
            positions.append(
                Position(
                    entry_time=timestamp,
                    side=deal_type,
                    volume=volume,
                    entry_price=price,
                    deal_id=str(deal["deal"]),
                    order_id=str(deal["order"]),
                    comment=str(deal["comment"]),
                )
            )
            continue

        if direction != "out" or deal_type not in {"buy", "sell"}:
            continue

        closed_side = closed_side_for_exit(deal_type)
        profit = float(deal["profit"])
        match_index, match_error = match_exit_to_position(positions, closed_side, volume, price, profit)
        if match_index < 0:
            unmatched.append(deal)
            continue

        position = positions[match_index]
        hold_minutes = (timestamp - position.entry_time).total_seconds() / 60.0
        closed.append(
            ClosedTrade(
                entry_time=position.entry_time,
                exit_time=timestamp,
                side=closed_side,
                volume=volume,
                entry_price=position.entry_price,
                exit_price=price,
                profit=profit,
                balance=float(deal["balance"]),
                entry_deal_id=position.deal_id,
                entry_order_id=position.order_id,
                exit_deal_id=str(deal["deal"]),
                exit_order_id=str(deal["order"]),
                entry_comment=position.comment,
                exit_comment=str(deal["comment"]),
                match_error=match_error,
                hold_minutes=hold_minutes,
            )
        )

        position.volume -= volume
        if position.volume <= 1e-7:
            positions.pop(match_index)

    return closed, unmatched


def parse_entry_comment(comment: str) -> dict[str, object]:
    parts = [part.strip() for part in comment.split("|")]
    if parts and parts[0] == "AC1":
        score = 0
        grade = ""
        tags: list[str] = []
        for token in parts[2:]:
            if token.startswith("S") and token[1:].isdigit():
                score = int(token[1:])
                continue
            if token in {"A", "B", "C"} and not grade:
                grade = token
                continue
            if token:
                tags.append(token)
        code = parts[1] if len(parts) > 1 else ""
        engine = code
    else:
        score = 0
        score_token = parts[3] if len(parts) > 3 else ""
        if score_token.startswith("S") and score_token[1:].isdigit():
            score = int(score_token[1:])
        code = parts[2] if len(parts) > 2 else ""
        engine = parts[1] if len(parts) > 1 else ENGINE_NAMES.get(code, "")
        grade = parts[4] if len(parts) > 4 else ""
        tags = [tag for tag in parts[5:] if tag]
    return {
        "family": parts[0] if parts else "",
        "engine": engine,
        "code": code,
        "score": score,
        "grade": grade,
        "regime_tag": "WG" if "WG" in tags else ("RG" if "RG" in tags else ""),
        "hour_tag": "XH" if ("XH" in tags or "X" in tags) else ("CH" if "CH" in tags else ""),
        "tags": tags,
    }


def exit_reason(comment: str, profit: float) -> str:
    lower = comment.lower().strip()
    if lower.startswith("tp"):
        return "tp"
    if lower.startswith("sl"):
        return "sl"
    if "risk_guard" in lower:
        return "risk_guard"
    if profit > 0:
        return "manual/exit_profit"
    if profit < 0:
        return "manual/exit_loss"
    return "flat"


def score_bucket(score: int) -> str:
    if score <= 0:
        return "unknown"
    if score < 70:
        return "S00-69"
    if score < 80:
        return "S70-79"
    if score < 90:
        return "S80-89"
    return "S90-99"


def trade_to_row(trade: ClosedTrade) -> dict[str, object]:
    meta = parse_entry_comment(trade.entry_comment)
    return {
        "entry_time": trade.entry_time.strftime("%Y-%m-%d %H:%M:%S"),
        "exit_time": trade.exit_time.strftime("%Y-%m-%d %H:%M:%S"),
        "entry_month": trade.entry_time.strftime("%Y-%m"),
        "entry_date": trade.entry_time.strftime("%Y-%m-%d"),
        "entry_hour": trade.entry_time.hour,
        "exit_hour": trade.exit_time.hour,
        "side": trade.side,
        "volume": trade.volume,
        "entry_price": trade.entry_price,
        "exit_price": trade.exit_price,
        "profit": trade.profit,
        "balance": trade.balance,
        "hold_minutes": trade.hold_minutes,
        "exit_reason": exit_reason(trade.exit_comment, trade.profit),
        "entry_comment": trade.entry_comment,
        "exit_comment": trade.exit_comment,
        "match_error": trade.match_error,
        "family": meta["family"],
        "engine": meta["engine"],
        "code": meta["code"],
        "score": meta["score"],
        "grade": meta["grade"],
        "regime_tag": meta["regime_tag"],
        "hour_tag": meta["hour_tag"],
        "tags": ",".join(meta["tags"]),
        "score_bucket": score_bucket(int(meta["score"])),
    }


def metrics_for(rows: list[dict[str, object]]) -> dict[str, float]:
    profits = [float(row["profit"]) for row in rows]
    wins = [p for p in profits if p > 0.0]
    losses = [p for p in profits if p < 0.0]
    gross_profit = sum(wins)
    gross_loss = sum(losses)
    return {
        "trades": float(len(profits)),
        "net": sum(profits),
        "gross_profit": gross_profit,
        "gross_loss": gross_loss,
        "win_rate": (len(wins) / len(profits) * 100.0) if profits else 0.0,
        "profit_factor": gross_profit / abs(gross_loss) if gross_loss < 0.0 else 0.0,
        "avg": (sum(profits) / len(profits)) if profits else 0.0,
        "avg_win": (sum(wins) / len(wins)) if wins else 0.0,
        "avg_loss": (sum(losses) / len(losses)) if losses else 0.0,
        "largest_win": max(wins) if wins else 0.0,
        "largest_loss": min(losses) if losses else 0.0,
        "loss_count": float(len(losses)),
        "win_count": float(len(wins)),
    }


def group_rows(rows: list[dict[str, object]], keys: tuple[str, ...], min_trades: int = 1) -> list[dict[str, object]]:
    groups: dict[tuple[object, ...], list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        groups[tuple(row.get(key, "") for key in keys)].append(row)
    output = []
    for key_values, members in groups.items():
        if len(members) < min_trades:
            continue
        metrics = metrics_for(members)
        output.append({**{key: value for key, value in zip(keys, key_values)}, **metrics})
    output.sort(key=lambda row: (float(row["net"]), -float(row["trades"])))
    return output


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def fmt(value: float, decimals: int = 2) -> str:
    return f"{value:.{decimals}f}"


def markdown_group_table(rows: list[dict[str, object]], keys: tuple[str, ...], limit: int = 10) -> list[str]:
    visible = rows[:limit]
    header = [*keys, "trades", "net", "win_rate", "PF", "avg", "largest_loss"]
    lines = [
        "| " + " | ".join(header) + " |",
        "| " + " | ".join("---" if i < len(keys) else "---:" for i in range(len(header))) + " |",
    ]
    for row in visible:
        cells = [str(row.get(key, "")) for key in keys]
        cells.extend(
            [
                str(int(float(row["trades"]))),
                fmt(float(row["net"])),
                fmt(float(row["win_rate"])) + "%",
                fmt(float(row["profit_factor"])),
                fmt(float(row["avg"])),
                fmt(float(row["largest_loss"])),
            ]
        )
        lines.append("| " + " | ".join(cells) + " |")
    return lines


def build_loss_clusters(rows: list[dict[str, object]], gap_hours: int = 4) -> list[dict[str, object]]:
    losses = sorted([row for row in rows if float(row["profit"]) < 0.0], key=lambda row: str(row["entry_time"]))
    clusters: list[list[dict[str, object]]] = []
    current: list[dict[str, object]] = []
    for row in losses:
        entry_time = datetime.strptime(str(row["entry_time"]), "%Y-%m-%d %H:%M:%S")
        if not current:
            current = [row]
            continue
        previous_time = datetime.strptime(str(current[-1]["entry_time"]), "%Y-%m-%d %H:%M:%S")
        if entry_time - previous_time <= timedelta(hours=gap_hours):
            current.append(row)
            continue
        if len(current) >= 3:
            clusters.append(current)
        current = [row]
    if len(current) >= 3:
        clusters.append(current)

    output = []
    for cluster in clusters:
        pnl = sum(float(row["profit"]) for row in cluster)
        engines = defaultdict(int)
        for row in cluster:
            engines[str(row["engine"])] += 1
        output.append(
            {
                "start": cluster[0]["entry_time"],
                "end": cluster[-1]["exit_time"],
                "count": len(cluster),
                "pnl": pnl,
                "buy_losses": sum(1 for row in cluster if row["side"] == "buy"),
                "sell_losses": sum(1 for row in cluster if row["side"] == "sell"),
                "engines": ", ".join(f"{key}:{value}" for key, value in sorted(engines.items())),
            }
        )
    output.sort(key=lambda row: float(row["pnl"]))
    return output


def build_analysis(report_path: Path, out_dir: Path) -> None:
    text = read_report(report_path)
    metrics = parse_report_metrics(text)
    deals = extract_deal_rows(text)
    trades, unmatched = reconstruct_closed_trades(deals)
    rows = [trade_to_row(trade) for trade in trades]
    out_dir.mkdir(parents=True, exist_ok=True)

    trade_fields = [
        "entry_time",
        "exit_time",
        "entry_month",
        "entry_date",
        "entry_hour",
        "side",
        "volume",
        "entry_price",
        "exit_price",
        "profit",
        "balance",
        "hold_minutes",
        "exit_reason",
        "family",
        "engine",
        "code",
        "score",
        "grade",
        "regime_tag",
        "hour_tag",
        "tags",
        "score_bucket",
        "entry_comment",
        "exit_comment",
        "match_error",
    ]
    write_csv(out_dir / "trade_log.csv", rows, trade_fields)

    top_losses = sorted(rows, key=lambda row: float(row["profit"]))[:50]
    write_csv(out_dir / "top_losses.csv", top_losses, trade_fields)
    top_winners = sorted(rows, key=lambda row: float(row["profit"]), reverse=True)[:50]
    write_csv(out_dir / "top_winners.csv", top_winners, trade_fields)

    group_specs = {
        "by_engine.csv": ("engine",),
        "by_code.csv": ("code",),
        "by_side.csv": ("side",),
        "by_month.csv": ("entry_month",),
        "by_entry_hour.csv": ("entry_hour",),
        "by_engine_hour.csv": ("engine", "entry_hour"),
        "by_engine_regime.csv": ("engine", "regime_tag"),
        "by_engine_grade.csv": ("engine", "grade"),
        "by_engine_score_bucket.csv": ("engine", "score_bucket"),
        "by_exit_reason.csv": ("exit_reason",),
        "by_side_exit_reason.csv": ("side", "exit_reason"),
    }
    grouped: dict[str, list[dict[str, object]]] = {}
    for filename, keys in group_specs.items():
        grouped_rows = group_rows(rows, keys)
        grouped[filename] = grouped_rows
        fieldnames = [*keys, "trades", "net", "gross_profit", "gross_loss", "win_rate", "profit_factor", "avg", "avg_win", "avg_loss", "largest_win", "largest_loss", "win_count", "loss_count"]
        write_csv(out_dir / filename, grouped_rows, fieldnames)

    clusters = build_loss_clusters(rows)
    write_csv(out_dir / "loss_clusters.csv", clusters[:50], ["start", "end", "count", "pnl", "buy_losses", "sell_losses", "engines"])

    summary = {
        "report": str(report_path),
        "report_metrics": metrics,
        "reconstructed_trades": len(rows),
        "unmatched_exits": len(unmatched),
        "reconstructed_net": sum(float(row["profit"]) for row in rows),
        "max_match_error": max((float(row["match_error"]) for row in rows), default=0.0),
        "engine": grouped["by_engine.csv"],
        "month": grouped["by_month.csv"],
        "exit_reason": grouped["by_exit_reason.csv"],
        "worst_clusters": clusters[:10],
        "top_losses": top_losses[:20],
    }
    (out_dir / "analysis.json").write_text(json.dumps(summary, indent=2, default=str))

    total = metrics_for(rows)
    worst_engine = grouped["by_engine.csv"][:8]
    worst_month = grouped["by_month.csv"][:8]
    worst_engine_hour = [row for row in grouped["by_engine_hour.csv"] if int(float(row["trades"])) >= 3][:12]
    worst_regime = grouped["by_engine_regime.csv"][:10]
    best_engine = sorted(grouped["by_engine.csv"], key=lambda row: float(row["net"]), reverse=True)[:8]

    md_lines = [
        f"# Trade-Level Analysis: {report_path.name}",
        "",
        "## Summary",
        f"- Report net profit: `{metrics.get('Total Net Profit:', '')}`",
        f"- Reconstructed closed trades: `{len(rows)}`",
        f"- Reconstructed net: `{total['net']:.2f}`",
        f"- Win rate: `{total['win_rate']:.2f}%`",
        f"- Profit factor: `{total['profit_factor']:.2f}`",
        f"- Unmatched exits: `{len(unmatched)}`",
        f"- Max price/PnL match error: `{summary['max_match_error']:.4f}`",
        "",
        "## Worst Engines",
        *markdown_group_table(worst_engine, ("engine",), 12),
        "",
        "## Best Engines",
        *markdown_group_table(best_engine, ("engine",), 12),
        "",
        "## Worst Engine x Regime",
        *markdown_group_table(worst_regime, ("engine", "regime_tag"), 12),
        "",
        "## Worst Engine x Entry Hour",
        *markdown_group_table(worst_engine_hour, ("engine", "entry_hour"), 12),
        "",
        "## Worst Months",
        *markdown_group_table(worst_month, ("entry_month",), 12),
        "",
        "## Worst Loss Clusters",
        "| start | end | count | pnl | buy_losses | sell_losses | engines |",
        "| --- | --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for cluster in clusters[:10]:
        md_lines.append(
            f"| {cluster['start']} | {cluster['end']} | {cluster['count']} | {float(cluster['pnl']):.2f} | "
            f"{cluster['buy_losses']} | {cluster['sell_losses']} | {cluster['engines']} |"
        )
    md_lines.extend(
        [
            "",
            "## Files",
            f"- `trade_log.csv`: all reconstructed closed trades with original entry label.",
            f"- `top_losses.csv`: worst individual trades.",
            f"- `by_engine.csv`, `by_engine_hour.csv`, `by_engine_regime.csv`: leak maps.",
            f"- `loss_clusters.csv`: clustered losses within a 4-hour gap.",
            "",
            "## Label Legend",
        ]
    )
    for code, name in ENGINE_NAMES.items():
        md_lines.append(f"- `{code}` = `{name}`")
    for tag, meaning in TAG_NAMES.items():
        md_lines.append(f"- `{tag}` = {meaning}")

    (out_dir / "analysis.md").write_text("\n".join(md_lines) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("report", type=Path)
    parser.add_argument("out_dir", type=Path)
    args = parser.parse_args()
    build_analysis(args.report, args.out_dir)


if __name__ == "__main__":
    main()
