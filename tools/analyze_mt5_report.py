#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import html
import re
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path


def parse_float(value: str) -> float:
    value = value.strip().replace(" ", "")
    if value == "":
        return 0.0
    return float(value)


def parse_report_metrics(text: str) -> dict[str, str]:
    plain = re.sub(r"<[^>]+>", " ", text).replace("\xa0", " ")
    plain = re.sub(r"\s+", " ", plain)
    keys = [
        "Total Net Profit:",
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


def extract_deal_rows(text: str) -> list[list[str]]:
    start = text.find("<b>Deals</b>")
    if start < 0:
        raise RuntimeError("Deals table not found")
    table_start = text.rfind("<table", 0, start)
    table_end = text.find("</table>", start)
    if table_start < 0 or table_end < 0:
        raise RuntimeError("Deals table bounds not found")
    table_html = text[table_start : table_end + len("</table>")]
    rows: list[list[str]] = []
    for row_html in re.findall(r"<tr[^>]*>(.*?)</tr>", table_html, flags=re.S | re.I):
        cols = [html.unescape(re.sub(r"<[^>]+>", "", cell)).strip() for cell in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", row_html, flags=re.S | re.I)]
        if len(cols) == 13:
            rows.append(cols)
    return rows


def parse_deals(rows: list[list[str]]) -> list[dict[str, object]]:
    deals: list[dict[str, object]] = []
    for cols in rows:
        if cols[0] in {"Time", ""}:
            continue
        if cols[3] == "balance":
            continue
        try:
            ts = datetime.strptime(cols[0], "%Y.%m.%d %H:%M:%S")
        except ValueError:
            continue
        deals.append(
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
    return deals


def infer_closed_position_direction(deal_type: str, direction: str) -> str:
    if direction != "out":
        return ""
    if deal_type == "sell":
        return "buy"
    if deal_type == "buy":
        return "sell"
    return ""


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def build_analysis(report_path: Path, out_dir: Path) -> None:
    text = report_path.read_bytes().decode("utf-16le", errors="ignore")
    metrics = parse_report_metrics(text)
    deals = parse_deals(extract_deal_rows(text))
    exits = []
    for deal in deals:
        if deal["direction"] != "out":
            continue
        closed_dir = infer_closed_position_direction(str(deal["type"]), str(deal["direction"]))
        if not closed_dir:
            continue
        exits.append(
            {
                "time": deal["time"],
                "date": deal["time"].strftime("%Y-%m-%d"),
                "hour": deal["time"].hour,
                "closed_direction": closed_dir,
                "volume": deal["volume"],
                "price": deal["price"],
                "profit": deal["profit"],
                "balance": deal["balance"],
                "comment": str(deal["comment"]),
                "reason": str(deal["comment"]).split(" ", 1)[0].lower() if str(deal["comment"]) else "",
            }
        )

    exits.sort(key=lambda row: row["time"])
    losses = [row for row in exits if float(row["profit"]) < 0.0]
    top_losses = sorted(losses, key=lambda row: float(row["profit"]))[:50]
    write_csv(
        out_dir / "top_losses.csv",
        [
            {
                "time": row["time"].strftime("%Y-%m-%d %H:%M:%S"),
                "closed_direction": row["closed_direction"],
                "profit": f"{float(row['profit']):.2f}",
                "volume": f"{float(row['volume']):.2f}",
                "balance": f"{float(row['balance']):.2f}",
                "reason": row["reason"],
                "comment": row["comment"],
            }
            for row in top_losses
        ],
        ["time", "closed_direction", "profit", "volume", "balance", "reason", "comment"],
    )

    by_day: dict[str, dict[str, float]] = defaultdict(lambda: {"pnl": 0.0, "losses": 0, "wins": 0})
    for row in exits:
        day = str(row["date"])
        pnl = float(row["profit"])
        by_day[day]["pnl"] += pnl
        if pnl < 0:
            by_day[day]["losses"] += 1
        elif pnl > 0:
            by_day[day]["wins"] += 1
    worst_days = [
        {"date": day, "pnl": f"{stats['pnl']:.2f}", "losses": int(stats["losses"]), "wins": int(stats["wins"])}
        for day, stats in sorted(by_day.items(), key=lambda item: item[1]["pnl"])[:40]
    ]
    write_csv(out_dir / "worst_loss_days.csv", worst_days, ["date", "pnl", "losses", "wins"])

    by_hour: dict[tuple[str, int], dict[str, float]] = defaultdict(lambda: {"pnl": 0.0, "wins": 0, "losses": 0})
    for row in exits:
        key = (str(row["closed_direction"]), int(row["hour"]))
        pnl = float(row["profit"])
        by_hour[key]["pnl"] += pnl
        if pnl < 0:
            by_hour[key]["losses"] += 1
        elif pnl > 0:
            by_hour[key]["wins"] += 1
    hour_rows = [
        {
            "closed_direction": direction,
            "hour": hour,
            "pnl": f"{stats['pnl']:.2f}",
            "wins": int(stats["wins"]),
            "losses": int(stats["losses"]),
        }
        for (direction, hour), stats in sorted(by_hour.items(), key=lambda item: (item[0][0], item[0][1]))
    ]
    write_csv(out_dir / "exit_hour_stats.csv", hour_rows, ["closed_direction", "hour", "pnl", "wins", "losses"])

    by_reason: dict[tuple[str, str], dict[str, float]] = defaultdict(lambda: {"pnl": 0.0, "count": 0})
    for row in exits:
        key = (str(row["closed_direction"]), str(row["reason"]))
        by_reason[key]["pnl"] += float(row["profit"])
        by_reason[key]["count"] += 1
    reason_rows = [
        {
            "closed_direction": direction,
            "reason": reason,
            "pnl": f"{stats['pnl']:.2f}",
            "count": int(stats["count"]),
        }
        for (direction, reason), stats in sorted(by_reason.items())
    ]
    write_csv(out_dir / "exit_reason_stats.csv", reason_rows, ["closed_direction", "reason", "pnl", "count"])

    clusters: list[dict[str, object]] = []
    current: list[dict[str, object]] = []
    for row in losses:
        if not current:
            current = [row]
            continue
        gap = row["time"] - current[-1]["time"]
        if gap <= timedelta(hours=4):
            current.append(row)
            continue
        if len(current) >= 3:
            clusters.append(current)
        current = [row]
    if len(current) >= 3:
        clusters.append(current)

    cluster_rows = []
    for cluster in clusters:
        pnl = sum(float(row["profit"]) for row in cluster)
        buy_losses = sum(1 for row in cluster if row["closed_direction"] == "buy")
        sell_losses = sum(1 for row in cluster if row["closed_direction"] == "sell")
        cluster_rows.append(
            {
                "start": cluster[0]["time"].strftime("%Y-%m-%d %H:%M:%S"),
                "end": cluster[-1]["time"].strftime("%Y-%m-%d %H:%M:%S"),
                "count": len(cluster),
                "pnl": f"{pnl:.2f}",
                "buy_losses": buy_losses,
                "sell_losses": sell_losses,
            }
        )
    cluster_rows.sort(key=lambda row: float(row["pnl"]))
    write_csv(out_dir / "loss_clusters.csv", cluster_rows[:40], ["start", "end", "count", "pnl", "buy_losses", "sell_losses"])

    md_lines = [
        f"# Analysis for {report_path.name}",
        "",
        "## Summary Metrics",
    ]
    for key, value in metrics.items():
        md_lines.append(f"- {key} {value}")
    md_lines.extend(
        [
            "",
            "## Files",
            f"- [top_losses.csv]({(out_dir / 'top_losses.csv').as_posix()})",
            f"- [worst_loss_days.csv]({(out_dir / 'worst_loss_days.csv').as_posix()})",
            f"- [exit_hour_stats.csv]({(out_dir / 'exit_hour_stats.csv').as_posix()})",
            f"- [exit_reason_stats.csv]({(out_dir / 'exit_reason_stats.csv').as_posix()})",
            f"- [loss_clusters.csv]({(out_dir / 'loss_clusters.csv').as_posix()})",
        ]
    )
    (out_dir / "analysis.md").write_text("\n".join(md_lines) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("report", type=Path)
    parser.add_argument("out_dir", type=Path)
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    build_analysis(args.report, args.out_dir)


if __name__ == "__main__":
    main()
