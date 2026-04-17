#!/usr/bin/env python3

import difflib
import json
from pathlib import Path


ROOT = Path("/Users/naufalrachmandani/Hobby/MT5 XAU 15m")
SPEC_PATH = ROOT / "spec" / "invictus_forward_1_m15.json"
HTML_OUT = ROOT / "build" / "InvictusForward-1-Docs.generated.html"
MQH_OUT = ROOT / "mt5" / "InvictusForward1Spec.generated.mqh"
COMPARE_OUT = ROOT / "build" / "InvictusForward-1-Docs.compare.txt"


def load_spec():
    with SPEC_PATH.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def table(headers, rows, indent="    "):
    lines = [f"{indent}<table>"]
    lines.append(f"{indent}  <tr>{''.join(f'<th>{cell}</th>' for cell in headers)}</tr>")
    for row in rows:
        lines.append(f"{indent}  <tr>{''.join(f'<td>{cell}</td>' for cell in row)}</tr>")
    lines.append(f"{indent}</table>")
    return lines


def flow(steps, indent="  "):
    lines = [f"{indent}<div class=\"flow\">"]
    for step in steps:
        lines.extend(
            [
                f"{indent}  <div class=\"flow-step {step['class_name']}\">",
                f"{indent}    <div class=\"flow-line\"></div>",
                f"{indent}    <div class=\"flow-box\">",
                f"{indent}      <div class=\"ft\">{step['title']}</div>",
                f"{indent}      <div class=\"fd\">{step['detail_html']}</div>",
                f"{indent}    </div>",
                f"{indent}  </div>",
            ]
        )
    lines.append(f"{indent}</div>")
    return lines


def recommendation_blocks(recommendations, indent="  "):
    lines = []
    for rec in recommendations:
        paragraphs = rec["body_html"].split("</p><p>")
        lines.extend(
            [
                f"{indent}<div class=\"rec\">",
                f"{indent}  <div class=\"rt\">{rec['title_html']}</div>",
            ]
        )
        for paragraph in paragraphs:
            lines.append(f"{indent}  <p>{paragraph}</p>")
        lines.extend(
            [
                f"{indent}</div>",
                "",
            ]
        )
    if lines and lines[-1] == "":
        lines.pop()
    return lines


def build_html(spec):
    logic = spec["logic"]
    meta = spec["meta"]
    docs = spec["docs"]
    t = logic["trending"]
    s = logic["sideways"]
    r = logic["risk"]

    tf_rows = [
        ["<code>IH_SwingLookback</code>", str(t["swing_lookback"]), "Fractal: butuh 2 bar kiri &amp; 2 bar kanan untuk validasi swing"],
        ["<code>IH_MinBreakATR</code>", f"{t['min_break_atr']:.2f}", "Break distance minimal = ATR &times; 0.30"],
        ["<code>IH_MinBodyRatio</code>", f"{t['min_body_ratio']:.2f}", "Body/range ratio candle BOS untuk qualify Impulsive"],
        ["<code>IH_MaxBOSBarsBack</code>", str(t["max_bos_bars_back"]), "Cari swing sampai 60 bar ke belakang (15 jam)"],
        ["<code>IH_ZoneSearchWindow</code>", str(t["zone_search_window"]), "Cari Candle A/B sampai 8 bar dari refBar (2 jam)"],
        ["<code>IH_MaxZoneRange</code>", "$20", "Zone harus compact, max $20"],
        ["<code>IH_MinScoreA</code>", str(t["score"]["buy_min"]), "Score minimum untuk entry BUY"],
        ["<code>IH_GoldBuyBonus</code>", str(t["score"]["gold_buy_bonus"]), "Bonus score otomatis untuk BUY gold"],
        ["<code>IH_MinSLDollar</code>", "$25", "Minimum SL distance"],
        ["<code>IH_MaxSLDollar</code>", "$25", "Maximum SL distance (sama = <strong>fixed $25</strong>)"],
        ["<code>IH_TP1_RR</code>", f"{t['tp_rr_default']:.1f}", "Default Risk-Reward ratio"],
        ["<code>IH_ATRBufferSL</code>", f"{t['sl_atr_buffer']:.1f}", "SL = zone boundary + ATR &times; 0.5"],
        ["<code>IH_PendingExpiryBars</code>", str(t["pending_expiry_bars"]), "Limit order expired setelah 8 bar = 2 jam"],
        ["<code>IH_EntryBodyRatio</code>", f"{t['entry_body_ratio']:.2f}", "Entry di 50% body Candle B"],
    ]

    hardcoded_rows = [
        ["KillSwitch wins", str(t["killswitch_daily_wins"]), "Max wins/day trending (hardcoded untuk M15)"],
        ["Daily loss cap (trending)", "5%", "Dari balance awal hari"],
        ["Daily loss cap (sideways)", "3%", "Dari balance awal hari"],
        ["Sideways wins cap", str(s["daily_wins_cap"]), "Max wins/day sideways"],
        ["ADX threshold", "20", "ADX H4 &lt; 20 = sideways aktif"],
        ["Cooldown after loss", "2 bar (30 min)", "Kedua strategy"],
        ["Zone cooldown tolerance", "$1", "Same zone jika entry price &lt; $1 beda"],
        ["Toxic hours (trending)", "03, 17", "WR &lt; 27%"],
        ["Toxic hours (sideways)", "03, 19", "WR 0-14%"],
        ["SELL hours", "07, 10, 22", "Hanya 3 jam SELL diizinkan"],
        ["Friday cutoff", "15:00", "No trading setelah ini"],
        ["Timed profit close", "5 jam, $15/0.01lot", "Close jika profit + open &gt; 5 jam"],
        ["Slippage", str(r["slippage_points"]) + " points", "Max deviation"],
        ["Sideways range min/max", "$15 / ATR&times;10", "Range validation"],
        ["Sideways SL clamp", "$5 - $20", "SL boundaries"],
        ["Sideways lot modifier", "&times;0.25", "25% dari trending lot"],
        ["Cluster max", "2 entry/range/day", "Same range = &lt;$5 delta"],
    ]

    dead_input_rows = [
        ["<code>BT_RiskPercent</code> (3.0)", "Declared, tidak dipanggil &mdash; lot pakai compounding"],
        ["<code>BT_UseFixedLot</code> (false)", "Declared, tidak ada if-check"],
        ["<code>BT_FixedLot</code> (0.01)", "Declared, tidak dipanggil"],
        ["<code>BT_CompoundingPer</code> (500)", "Declared, tier values di-hardcode"],
    ]

    buy_scoring_rows = [
        ["Zone Detected", "+40", "Selalu +40 jika Candle A/B valid"],
        ["Volatility Normal", "+15", "ATR saat ini &lt; 130% rata-rata 50 bar"],
        ["FVG", "+10", "Fair Value Gap di sekitar BOS candle"],
        ["Retest", "+10", "Harga kembali ke swing &amp; bounce (wick &gt; 50% atau body engulf)"],
        ["Sweep", "+5", "Liquidity grab: low &lt; swing tapi close &gt; swing (dalam 5 bar)"],
        ["Trend", "+20", "5+ dari 9 bar membentuk higher highs"],
        ["Gold Buy Bonus", "+10", "Selalu +10 untuk BUY gold"],
    ]

    gate3_rows = [
        ["BOS Quality", "Impulsive atau Corrective", "<strong>HARUS Impulsive</strong>"],
        ["Min Score", "80", "<strong>90</strong>"],
        ["Lot", "100%", "<strong>50%</strong>"],
        ["Gold Bonus", "+10", "Tidak ada"],
    ]

    sideways_protection_rows = [
        ["Max wins/day", "10"],
        ["Daily loss cap", "3%"],
        ["Toxic hours", "03, 19"],
        ["Cooldown after loss", "2 bar (30 min)"],
        ["Max positions", "4"],
        ["Cluster protection", "2 entry per range per hari"],
        ["Lot", "25% dari trending lot"],
        ["SL clamp", "$5 - $20"],
    ]

    compare_rows = [
        ["Aktif", "Selalu", "ADX H4 &lt; 20"],
        ["Arah", "BUY + SELL", "BUY only"],
        ["Logika", "BOS + Zone + Scoring", "Range boundary bounce"],
        ["Order type", "Market + Limit", "Market only"],
        ["Lot", "100% compounding", "25% compounding"],
        ["Daily loss", "5%", "3%"],
        ["Max wins", "20", "10"],
        ["SL", "Fixed $25", "$5-$20"],
    ]

    multiple_position_rows = [
        ["&le; $20k", "5", "4", "9"],
        ["$20-50k", "4", "4", "8"],
        ["$50k+", "3", "4", "7"],
    ]

    limit_order_rows = [
        ["BUY: ask &le; entry price", "Market Buy"],
        ["BUY: ask &gt; entry price", "<strong>Buy Limit</strong> (harga di atas zone, tunggu turun)"],
        ["SELL: bid &ge; entry price", "Market Sell"],
        ["SELL: bid &lt; entry price", "<strong>Sell Limit</strong> (harga di bawah zone, tunggu naik)"],
    ]

    limit_expired_rows = [
        ["Position count", "Tidak berubah (pending bukan posisi)"],
        ["Consecutive losses", "Tidak bertambah"],
        ["Daily wins/loss", "Tidak terpengaruh"],
        ["Zone cooldown", "Sudah tersimpan &mdash; zone yang sama kena cooldown 2 bar"],
        ["Re-entry", "Bar berikutnya bisa generate setup baru"],
    ]

    compounding_rows = [
        ["&le; $20k", "<code>floor(bal/500) &times; 0.01</code>", "$10k &rarr; 0.20"],
        ["$20-50k", "<code>0.40 + floor((bal-20k)/750) &times; 0.01</code>", "$35k &rarr; 0.60"],
        ["$50k+", "<code>0.80 + floor((bal-50k)/1500) &times; 0.01</code>", "$80k &rarr; 1.00"],
    ]

    lot_modifier_rows = [
        ["Sideways", "&times; 0.25"],
        ["SELL", "&times; 0.50"],
        ["3-4 consecutive losses", "&times; 0.50"],
        ["5-6 consecutive losses", "&times; 0.25"],
        ["7+ consecutive losses", "&times; 0.10"],
    ]

    priority_rows = [
        ["<span class=\"badge\" style=\"background:rgba(248,81,73,0.2);color:var(--red)\">HIGH</span>", "Fixed SL, No cancel, Dead params", "Bug / risk langsung"],
        ["<span class=\"badge\" style=\"background:rgba(210,153,34,0.2);color:var(--orange)\">MED</span>", "No trailing, Timed close, Bias, Exposure", "Profit factor"],
        ["<span class=\"badge\" style=\"background:rgba(63,185,80,0.2);color:var(--green)\">LOW</span>", "Sideways TP, Zone reset, Logging", "Quality of life"],
    ]

    lines = [
        "<!DOCTYPE html>",
        "<html lang=\"id\">",
        "<head>",
        "<meta charset=\"UTF-8\">",
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">",
        f"<title>{meta['title']}</title>",
        "<style>",
        "  :root {",
        "    --bg: #0d1117;",
        "    --surface: #161b22;",
        "    --surface2: #1c2333;",
        "    --border: #30363d;",
        "    --text: #e6edf3;",
        "    --text-dim: #8b949e;",
        "    --accent: #58a6ff;",
        "    --green: #3fb950;",
        "    --red: #f85149;",
        "    --orange: #d29922;",
        "    --purple: #bc8cff;",
        "    --gold: #e3b341;",
        "  }",
        "  * { margin: 0; padding: 0; box-sizing: border-box; }",
        "  body {",
        "    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;",
        "    background: var(--bg); color: var(--text); line-height: 1.7; padding: 0;",
        "  }",
        "",
        "  .hero {",
        "    background: linear-gradient(135deg, #0d1117 0%, #1a1e2e 50%, #0d1117 100%);",
        "    border-bottom: 1px solid var(--border); padding: 50px 40px; text-align: center;",
        "  }",
        "  .hero h1 {",
        "    font-size: 2.6rem; font-weight: 800;",
        "    background: linear-gradient(135deg, var(--accent), var(--purple));",
        "    -webkit-background-clip: text; -webkit-text-fill-color: transparent;",
        "    margin-bottom: 10px;",
        "  }",
        "  .hero .subtitle { color: var(--text-dim); font-size: 1.1rem; max-width: 650px; margin: 0 auto; }",
        "  .hero .badge {",
        "    display: inline-block; margin-top: 14px; padding: 4px 16px; border-radius: 20px;",
        "    background: rgba(88,166,255,0.12); border: 1px solid rgba(88,166,255,0.3);",
        "    color: var(--accent); font-size: 0.85rem; font-weight: 600;",
        "  }",
        "",
        "  .container { max-width: 1050px; margin: 0 auto; padding: 36px 28px; }",
        "",
        "  /* TOC */",
        "  .toc {",
        "    background: var(--surface); border: 1px solid var(--border); border-radius: 12px;",
        "    padding: 24px 28px; margin-bottom: 44px;",
        "  }",
        "  .toc h2 { font-size: 1rem; color: var(--text-dim); text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 14px; }",
        "  .toc-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 6px 28px; }",
        "  .toc a { color: var(--accent); text-decoration: none; font-size: 0.93rem; padding: 3px 0; display: block; }",
        "  .toc a:hover { color: var(--purple); }",
        "  .toc .n { color: var(--text-dim); font-size: 0.78rem; margin-right: 6px; font-weight: 600; }",
        "",
        "  /* Sections */",
        "  section { margin-bottom: 52px; }",
        "  section h2 {",
        "    font-size: 1.6rem; font-weight: 700; margin-bottom: 20px; padding-bottom: 10px;",
        "    border-bottom: 2px solid var(--border); display: flex; align-items: center; gap: 12px;",
        "  }",
        "  section h2 .ic {",
        "    font-size: 1.3rem; width: 38px; height: 38px; display: flex; align-items: center;",
        "    justify-content: center; border-radius: 10px; flex-shrink: 0;",
        "  }",
        "  section h3 { font-size: 1.1rem; font-weight: 600; margin: 22px 0 10px; color: var(--accent); }",
        "",
        "  p { margin-bottom: 11px; }",
        "",
        "  /* Cards */",
        "  .card {",
        "    background: var(--surface); border: 1px solid var(--border); border-radius: 10px;",
        "    padding: 22px; margin-bottom: 14px;",
        "  }",
        "  .card.buy  { border-left: 4px solid var(--green); }",
        "  .card.sell { border-left: 4px solid var(--red); }",
        "  .card.info { border-left: 4px solid var(--accent); }",
        "  .card.warn { border-left: 4px solid var(--orange); }",
        "  .card.purple { border-left: 4px solid var(--purple); }",
        "  .card-title { font-weight: 700; font-size: 1.02rem; margin-bottom: 8px; }",
        "",
        "  /* Tables */",
        "  table { width: 100%; border-collapse: collapse; margin: 14px 0; font-size: 0.91rem; }",
        "  th, td { padding: 9px 13px; text-align: left; border-bottom: 1px solid var(--border); }",
        "  th { background: var(--surface2); color: var(--accent); font-weight: 600; font-size: 0.79rem; text-transform: uppercase; letter-spacing: 0.5px; }",
        "  tr:hover td { background: rgba(88,166,255,0.04); }",
        "",
        "  code {",
        "    background: var(--surface2); color: var(--gold); padding: 2px 6px; border-radius: 4px;",
        "    font-size: 0.86rem; font-family: 'SF Mono','Fira Code',monospace;",
        "  }",
        "  pre {",
        "    background: var(--surface2); border: 1px solid var(--border); border-radius: 8px;",
        "    padding: 18px; overflow-x: auto; font-size: 0.84rem; line-height: 1.6; margin: 10px 0 14px;",
        "    font-family: 'SF Mono','Fira Code',monospace; color: var(--text);",
        "  }",
        "",
        "  /* Flow */",
        "  .flow { display: flex; flex-direction: column; margin: 18px 0; }",
        "  .flow-step { display: flex; align-items: stretch; gap: 14px; }",
        "  .flow-line {",
        "    width: 3px; background: var(--border); margin-left: 16px; flex-shrink: 0; position: relative;",
        "  }",
        "  .flow-line::before {",
        "    content: ''; width: 13px; height: 13px; border-radius: 50%; background: var(--accent);",
        "    position: absolute; top: 14px; left: -5px;",
        "  }",
        "  .flow-step.ok .flow-line::before { background: var(--green); }",
        "  .flow-step.no .flow-line::before { background: var(--red); }",
        "  .flow-step.ck .flow-line::before { background: var(--orange); }",
        "  .flow-box {",
        "    background: var(--surface); border: 1px solid var(--border); border-radius: 8px;",
        "    padding: 12px 16px; margin: 5px 0; flex: 1;",
        "  }",
        "  .flow-box .ft { font-weight: 700; font-size: 0.93rem; margin-bottom: 3px; }",
        "  .flow-box .fd { font-size: 0.86rem; color: var(--text-dim); }",
        "",
        "  .badge {",
        "    display: inline-block; padding: 2px 10px; border-radius: 12px; font-size: 0.76rem; font-weight: 600;",
        "  }",
        "  .b-buy  { background: rgba(63,185,80,0.15); color: var(--green); }",
        "  .b-sell { background: rgba(248,81,73,0.15); color: var(--red); }",
        "  .b-info { background: rgba(88,166,255,0.15); color: var(--accent); }",
        "  .b-warn { background: rgba(210,153,34,0.15); color: var(--orange); }",
        "",
        "  .split { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin: 14px 0; }",
        "",
        "  .formula {",
        "    background: var(--surface2); border: 1px solid var(--border); border-radius: 8px;",
        "    padding: 14px 18px; margin: 10px 0; font-family: 'SF Mono','Fira Code',monospace;",
        "    font-size: 0.88rem; text-align: center; color: var(--gold);",
        "  }",
        "",
        "  ul, ol { margin: 6px 0 10px 22px; }",
        "  li { margin-bottom: 5px; font-size: 0.93rem; }",
        "",
        "  .rec {",
        "    background: linear-gradient(135deg, rgba(88,166,255,0.06), rgba(188,140,255,0.06));",
        "    border: 1px solid rgba(88,166,255,0.2); border-radius: 12px; padding: 22px; margin-bottom: 14px;",
        "  }",
        "  .rec .rt { font-weight: 700; font-size: 0.98rem; color: var(--accent); margin-bottom: 6px; }",
        "  .rec .rp {",
        "    display: inline-block; padding: 2px 8px; border-radius: 8px; font-size: 0.71rem;",
        "    font-weight: 700; text-transform: uppercase; margin-left: 8px;",
        "  }",
        "  .rp-h { background: rgba(248,81,73,0.2); color: var(--red); }",
        "  .rp-m { background: rgba(210,153,34,0.2); color: var(--orange); }",
        "  .rp-l { background: rgba(63,185,80,0.2); color: var(--green); }",
        "",
        "  .footer {",
        "    text-align: center; padding: 36px; color: var(--text-dim); font-size: 0.84rem;",
        "    border-top: 1px solid var(--border);",
        "  }",
        "",
        "  @media (max-width: 768px) {",
        "    .split, .toc-grid { grid-template-columns: 1fr; }",
        "    .hero h1 { font-size: 1.9rem; }",
        "    .container { padding: 20px 14px; }",
        "  }",
        "  ::-webkit-scrollbar { width: 8px; height: 8px; }",
        "  ::-webkit-scrollbar-track { background: var(--bg); }",
        "  ::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }",
        "</style>",
        "</head>",
        "<body>",
        "",
        "<div class=\"hero\">",
        f"  <h1>{meta['hero_title']}</h1>",
        f"  <p class=\"subtitle\">{meta['subtitle_html']}</p>",
        f"  <span class=\"badge\">{meta['badge_html']}</span>",
        "</div>",
        "",
        "<div class=\"container\">",
        "",
        "<nav class=\"toc\">",
        "  <h2>Daftar Isi</h2>",
        "  <div class=\"toc-grid\">",
        "    <div>",
    ]

    for toc in docs["toc"][:5]:
        lines.append(f"      <a href=\"#{toc['id']}\"><span class=\"n\">{toc['number']}</span>{toc['label']}</a>")
    lines.extend(
        [
            "    </div>",
            "    <div>",
        ]
    )
    for toc in docs["toc"][5:]:
        lines.append(f"      <a href=\"#{toc['id']}\"><span class=\"n\">{toc['number']}</span>{toc['label']}</a>")
    lines.extend(
        [
            "    </div>",
            "  </div>",
            "</nav>",
            "",
            "<!-- ============================================================ -->",
            "<!-- 1. ARSITEKTUR -->",
            "<!-- ============================================================ -->",
            "<section id=\"s1\">",
            "  <h2><span class=\"ic\" style=\"background:rgba(88,166,255,0.12)\">01</span> Arsitektur Dual-Strategy di M15</h2>",
            "",
            "  <p>Di M15, EA menjalankan <strong>dua strategi paralel</strong> dengan state dan magic number terpisah:</p>",
            "",
            "  <div class=\"split\">",
            "    <div class=\"card buy\">",
            "      <div class=\"card-title\">Trending (SMC Breakout)</div>",
            f"      <p>Magic: <code>{t['magic']}</code></p>",
            "      <ul>",
            "        <li><strong>Selalu aktif</strong> setiap bar M15 baru</li>",
            "        <li>BUY + SELL (SELL sangat restricted)</li>",
            "        <li>Market order atau Buy/Sell Limit</li>",
            "        <li>Max posisi: 3-5 tergantung balance</li>",
            "      </ul>",
            "    </div>",
            "    <div class=\"card purple\">",
            "      <div class=\"card-title\">Sideways (Range Bounce)</div>",
            f"      <p>Magic: <code>{s['magic']}</code></p>",
            "      <ul>",
            "        <li>Aktif <strong>hanya saat ADX H4 &lt; 20</strong></li>",
            "        <li>BUY-only, selalu market order</li>",
            "        <li>Lot = 25% dari trending</li>",
            "        <li>Max posisi: 4, max 2 entry/range/hari</li>",
            "      </ul>",
            "    </div>",
            "  </div>",
            "",
            "  <h3>Apa yang TIDAK berlaku di M15</h3>",
            "  <div class=\"card warn\">",
            "    <p>Beberapa fitur di kode <strong>hanya aktif di TF &gt; M15</strong> dan sepenuhnya di-skip saat M15:</p>",
            "    <ul>",
            "      <li><strong>Session Filter</strong> &mdash; DISABLED. M15 boleh entry kapan saja (kecuali toxic hours).</li>",
            "      <li><strong>Same-Direction Block</strong> &mdash; DISABLED. Setelah loss, arah yang sama tetap boleh entry lagi.</li>",
            "      <li><strong>BT_MaxDailyWins</strong> &mdash; TIDAK dipakai. M15 hardcoded ke 20 wins/day.</li>",
            "    </ul>",
            "  </div>",
            "",
            "  <h3>Regime Switch: ADX H4</h3>",
            "  <div class=\"card info\">",
            "    <p>ADX(14) pada H4 dibaca sekali per tick sebagai regime detector:</p>",
        ]
    )
    lines.extend(table(["ADX H4", "Yang Jalan"], [["&ge; 20", "Trending saja"], ["&lt; 20", "Trending + Sideways (bonus layer)"]], indent="    "))
    lines.extend(
        [
            "    <p style=\"margin-bottom:0\">Trending <strong>tidak pernah dimatikan</strong>. Sideways = tambahan saat market flat.</p>",
            "  </div>",
            "</section>",
            "",
            "<!-- ============================================================ -->",
            "<!-- 2. CARA ENTRY -->",
            "<!-- ============================================================ -->",
            "<section id=\"s2\">",
            "  <h2><span class=\"ic\" style=\"background:rgba(63,185,80,0.12)\">02</span> Cara Entry (Pipeline M15)</h2>",
            "",
            "  <h3>A. Trending Entry &mdash; 14 Step</h3>",
            "  <p>Setiap bar M15 baru yang close, pipeline ini jalan berurutan. Gagal di step mana pun = <strong>tidak ada entry</strong>.</p>",
            "",
        ]
    )
    lines.extend(flow(docs["trending_flow"], indent="  "))
    lines.extend(
        [
            "",
            "  <h3>B. Sideways Entry &mdash; 5 Step</h3>",
            "  <p>Hanya jalan saat ADX H4 &lt; 20. Lebih simpel, BUY-only, selalu market order.</p>",
            "",
        ]
    )
    lines.extend(flow(docs["sideways_flow"], indent="  "))
    lines.extend(
        [
            "</section>",
            "",
            "<!-- ============================================================ -->",
            "<!-- 3. PARAMETER M15 -->",
            "<!-- ============================================================ -->",
            "<section id=\"s3\">",
            "  <h2><span class=\"ic\" style=\"background:rgba(210,153,34,0.12)\">03</span> Semua Parameter M15</h2>",
            "",
            "  <h3>TF-Dependent (Otomatis di-set oleh IH_InitParams)</h3>",
        ]
    )
    lines.extend(table(["Parameter", "Nilai", "Fungsi"], tf_rows, indent="  "))
    lines.extend(
        [
            "",
            "  <h3>Hardcoded Constants (Berlaku M15)</h3>",
        ]
    )
    lines.extend(table(["Parameter", "Nilai", "Keterangan"], hardcoded_rows, indent="  "))
    lines.extend(
        [
            "",
            "  <h3>Input Parameters (TIDAK berfungsi)</h3>",
            "  <div class=\"card warn\">",
            "    <p>4 dari 5 input parameters <strong>tidak digunakan di kode</strong>:</p>",
        ]
    )
    lines.extend(table(["Parameter", "Status"], dead_input_rows, indent="    "))
    lines.extend(
        [
            "    <p style=\"margin-bottom:0\"><code>BT_MaxDailyWins</code> juga <strong>tidak dipakai di M15</strong> &mdash; hardcoded ke 20.</p>",
            "  </div>",
            "</section>",
            "",
            "<!-- ============================================================ -->",
            "<!-- 4. BULLISH -->",
            "<!-- ============================================================ -->",
            "<section id=\"s4\">",
            "  <h2><span class=\"ic\" style=\"background:rgba(63,185,80,0.12)\">04</span> Penentu Bullish</h2>",
            "",
            "  <div class=\"card buy\">",
            "    <div class=\"card-title\">DetectBias() &mdash; 9 Bar Analysis</div>",
            "    <p>Dari 9 bar M15 terakhir (2 jam 15 menit), hitung:</p>",
            "    <ul>",
            "      <li><strong>Higher High (HH)</strong>: berapa bar yang <code>high[k] &gt; high[k+1]</code></li>",
            "      <li><strong>Lower Low (LL)</strong>: berapa bar yang <code>low[k] &lt; low[k+1]</code></li>",
            "    </ul>",
        ]
    )
    lines.extend(
        table(
            ["Kondisi", "Hasil"],
            [
                ["HH &ge; 5", "<span class=\"badge b-buy\">BULLISH</span> &rarr; BUY"],
                ["LL &ge; 6", "<span class=\"badge b-sell\">BEARISH</span> &rarr; SELL (restricted)"],
                ["Keduanya tidak terpenuhi", "<span class=\"badge b-buy\">BULLISH</span> (default gold)"],
            ],
            indent="    ",
        )
    )
    lines.extend(
        [
            "    <p style=\"margin-bottom:0\"><strong>Bullish + Neutral = BUY</strong>. EA sangat bias ke BUY karena gold cenderung naik jangka panjang.</p>",
            "  </div>",
            "",
            "  <h3>BUY Scoring</h3>",
        ]
    )
    lines.extend(table(["Komponen", "Poin", "Cara Qualify"], buy_scoring_rows, indent="  "))
    lines.extend(
        [
            "  <div class=\"formula\">",
            "    Min BUY = <strong>80</strong> &nbsp;&bull;&nbsp; Max = <strong>110</strong> &nbsp;&bull;&nbsp; RR boost ke 2.0 jika score &ge; 95",
            "  </div>",
            "",
            "  <h3>Contoh BUY Setup</h3>",
            "  <pre>",
            docs["buy_example_pre"],
            "  </pre>",
            "</section>",
            "",
            "<!-- ============================================================ -->",
            "<!-- 5. BEARISH -->",
            "<!-- ============================================================ -->",
            "<section id=\"s5\">",
            "  <h2><span class=\"ic\" style=\"background:rgba(248,81,73,0.12)\">05</span> Penentu Bearish</h2>",
            "",
            "  <div class=\"card sell\">",
            "    <div class=\"card-title\">SELL: Triple Gate (sangat restricted di M15)</div>",
            "    <p>Setelah pipeline normal, SELL harus lolos 3 gate tambahan:</p>",
            "  </div>",
            "",
            "  <h3>Gate 1: Bias Bearish (LL &ge; 6)</h3>",
            "  <p>Minimal 67% bar dari 9 terakhir membuat lower-low. Lebih ketat dari BUY (56%).</p>",
            "",
            "  <h3>Gate 2: Hanya 3 Jam</h3>",
        ]
    )
    lines.extend(table(["Jam (Server)", "Session"], [["07:00", "Early London"], ["10:00", "Mid London"], ["22:00", "Late Asia"]], indent="  "))
    lines.extend(
        [
            "  <p>Di luar 3 jam ini = <strong>SELL langsung di-skip</strong>.</p>",
            "",
            "  <h3>Gate 3: BOS Impulsive + Score 90+</h3>",
        ]
    )
    lines.extend(table(["Requirement", "BUY", "SELL"], gate3_rows, indent="  "))
    lines.extend(
        [
            "",
            "  <h3>BOS Impulsive Requirements</h3>",
            "  <ul>",
            "    <li>Body candle BOS &ge; 45% dari total range</li>",
            "    <li>Minimal 1 dari 3 bar sebelumnya juga bearish (momentum)</li>",
            "    <li>Lower wick (opposite wick untuk sell) &le; 40% dari range</li>",
            "  </ul>",
            "",
            "  <h3>Bearish Zone</h3>",
            "  <ul>",
            "    <li>Candle B: bearish, close &lt; Candle A body bottom</li>",
            "    <li>Supply zone: [open_B (high), close_B (low)]</li>",
            "    <li>Entry: 50% body B</li>",
            "    <li>SL: zone high + ATR&times;0.5 (clamp $25)</li>",
            "    <li>TP: entry - $25 &times; 1.5 = entry - $37.50 (atau &times;2.0 jika score &ge; 95)</li>",
            "  </ul>",
            "</section>",
            "",
            "<!-- ============================================================ -->",
            "<!-- 6. SIDEWAYS -->",
            "<!-- ============================================================ -->",
            "<section id=\"s6\">",
            "  <h2><span class=\"ic\" style=\"background:rgba(188,140,255,0.12)\">06</span> Saat Sideways</h2>",
            "",
            "  <div class=\"card purple\">",
            "    <div class=\"card-title\">ADX H4 &lt; 20 = Sideways Regime</div>",
            "    <p>Saat ADX rendah, EA menambahkan strategy <strong>Range Bounce BUY-only</strong> di atas trending yang tetap jalan.</p>",
            "  </div>",
            "",
            "  <h3>Range Calculation</h3>",
            "  <ul>",
            "    <li>48 bar M15 terakhir (12 jam) &rarr; highest high, lowest low</li>",
            "    <li>Min range: $15 (di bawah = noise)</li>",
            "    <li>Max range: ATR(14) &times; 10 (di atas = trending, bukan sideways)</li>",
            "  </ul>",
            "",
            "  <h3>Entry Logic</h3>",
            "  <div class=\"formula\">",
            "    Buy Zone = rangeLow s/d rangeLow + (rangeSize &times; 0.25)",
            "    <br>Close bar terakhir HARUS di bawah buy zone top",
            "    <br>TP = mid-range (50%) &bull; SL = rangeLow - ATR buffer",
            "  </div>",
            "",
            "  <h3>Proteksi Sideways</h3>",
        ]
    )
    lines.extend(table(["Proteksi", "Nilai"], sideways_protection_rows, indent="  "))
    lines.extend(
        [
            "",
            "  <h3>Trending vs Sideways di M15</h3>",
        ]
    )
    lines.extend(table(["", "Trending", "Sideways"], compare_rows, indent="  "))
    lines.extend(
        [
            "</section>",
            "",
            "<!-- ============================================================ -->",
            "<!-- 7. POSISI LIFECYCLE -->",
            "<!-- ============================================================ -->",
            "<section id=\"s7\">",
            "  <h2><span class=\"ic\" style=\"background:rgba(57,211,83,0.12)\">07</span> Posisi ke-1 s/d ke-N &amp; Close</h2>",
            "",
            "  <h3>Multiple Positions</h3>",
            "  <p>Setiap posisi adalah <strong>independent trade</strong> dari BOS + Zone baru. Bukan grid/averaging.</p>",
        ]
    )
    lines.extend(table(["Balance", "Max Trending", "Max Sideways", "Total Max"], multiple_position_rows, indent="  "))
    lines.extend(
        [
            "",
            "  <h3>Cara Posisi Close</h3>",
            "",
            "  <div class=\"split\">",
            "    <div class=\"card buy\">",
            "      <div class=\"card-title\">TP Hit</div>",
            "      <p>Broker close otomatis. EA: <code>dailyWins++</code>, <code>consLosses = 0</code>. Lot kembali normal.</p>",
            "    </div>",
            "    <div class=\"card sell\">",
            "      <div class=\"card-title\">SL Hit</div>",
            "      <p>Broker close otomatis. EA: <code>consLosses++</code>, <code>dailyLossUSD += |loss|</code>, cooldown 30 menit. Lot dikurangi jika &ge; 3 losses.</p>",
            "    </div>",
            "  </div>",
            "",
            "  <div class=\"card info\">",
            "    <div class=\"card-title\">Timed Profit Close</div>",
            "    <p>Setiap tick, EA scan semua posisi. Jika:</p>",
            "    <div class=\"formula\">",
            "      profit + swap &ge; (lot / 0.01) &times; $15 &nbsp;&nbsp;DAN&nbsp;&nbsp; sudah buka &gt; 5 jam",
            "    </div>",
            "    <p style=\"margin-bottom:0\">Posisi di-close manual. Contoh: 0.05 lot butuh profit &ge; $75 + open &gt; 5 jam.</p>",
            "  </div>",
            "",
            "  <h3>State Setelah Close</h3>",
            "  <div class=\"split\">",
            "    <div class=\"card buy\">",
            "      <div class=\"card-title\">Setelah WIN</div>",
            "      <ul>",
            "        <li><code>dailyWins++</code></li>",
            "        <li><code>consLosses = 0</code></li>",
            "        <li>Lot kembali ke 100%</li>",
            "      </ul>",
            "    </div>",
            "    <div class=\"card sell\">",
            "      <div class=\"card-title\">Setelah LOSS</div>",
            "      <ul>",
            "        <li><code>consLosses++</code></li>",
            "        <li><code>dailyLossUSD += |loss|</code></li>",
            "        <li>Cooldown 30 menit dimulai</li>",
            "        <li>Lot: 50%/25%/10% pada 3/5/7 losses</li>",
            "      </ul>",
            "    </div>",
            "  </div>",
            "",
            "  <h3>Contoh Timeline</h3>",
            "  <pre>",
            docs["timeline_pre"],
            "  </pre>",
            "</section>",
            "",
            "<!-- ============================================================ -->",
            "<!-- 8. LIMIT ORDER -->",
            "<!-- ============================================================ -->",
            "<section id=\"s8\">",
            "  <h2><span class=\"ic\" style=\"background:rgba(248,81,73,0.12)\">08</span> Limit Order, Expired, Tidak Kena</h2>",
            "",
            "  <h3>Kapan Limit Order Dipakai</h3>",
            "  <p>Hanya di <strong>Trending</strong>. Sideways selalu market order.</p>",
        ]
    )
    lines.extend(table(["Kondisi", "Order Type"], limit_order_rows, indent="  "))
    lines.extend(
        [
            "",
            "  <h3>Expiry</h3>",
            "  <div class=\"formula\">",
            "    Expiry = sekarang + 8 bar &times; 900 detik = <strong>2 jam</strong>",
            "  </div>",
            "  <p>Menggunakan <code>ORDER_TIME_SPECIFIED</code>. Broker otomatis hapus setelah waktu habis.</p>",
            "",
            "  <h3>Jika Limit Tidak Kena (Expired)</h3>",
        ]
    )
    lines.extend(table(["Aspek", "Impact"], limit_expired_rows, indent="  "))
    lines.extend(
        [
            "",
            "  <h3>Cancel Order</h3>",
            "  <div class=\"card warn\">",
            "    <p>EA <strong>TIDAK memiliki mekanisme cancel</strong>. Tidak ada <code>OrderDelete()</code> di kode. Pending order hanya berakhir dengan:</p>",
            "    <ol>",
            "      <li><strong>Filled</strong> &mdash; harga sentuh entry</li>",
            "      <li><strong>Expired</strong> &mdash; 2 jam berlalu</li>",
            "      <li><strong>Manual</strong> &mdash; trader hapus dari MT5</li>",
            "    </ol>",
            "    <p style=\"margin-bottom:0\">Jika bias berubah atau news spike terjadi, pending order <strong>tetap aktif</strong> sampai expired/filled.</p>",
            "  </div>",
            "",
            "  <h3>OnTradeTransaction &mdash; Apa yang Di-track</h3>",
            "  <p>Hanya <code>DEAL_ENTRY_OUT</code> (posisi ditutup). EA <strong>tidak tracking</strong>: order placement, order fill, order expired, atau order modify.</p>",
            "</section>",
            "",
            "<!-- ============================================================ -->",
            "<!-- 9. RISK + LOT -->",
            "<!-- ============================================================ -->",
            "<section id=\"s9\">",
            "  <h2><span class=\"ic\" style=\"background:rgba(227,179,65,0.12)\">09</span> Risk Management &amp; Lot Sizing</h2>",
            "",
            "  <h3>5 Layer Proteksi</h3>",
        ]
    )
    lines.extend(
        [
            "  <table>",
            "    <tr><th>Layer</th><th>Trending M15</th><th>Sideways</th></tr>",
            "    <tr><td>Weekend</td><td colspan=\"2\">No trade Sat/Sun, Fri &ge; 15:00</td></tr>",
            "    <tr><td>Toxic Hours</td><td>03, 17</td><td>03, 19</td></tr>",
            "    <tr><td>Cooldown</td><td colspan=\"2\">30 menit setelah loss</td></tr>",
            "    <tr><td>Max Wins/Day</td><td>20</td><td>10</td></tr>",
            "    <tr><td>Daily Loss Cap</td><td>5%</td><td>3%</td></tr>",
            "    <tr><td>Max Positions</td><td>3-5</td><td>4</td></tr>",
            "    <tr><td>Zone Cooldown</td><td>$1 / 2 bar</td><td>Cluster 2/range</td></tr>",
            "    <tr><td>SL Boundaries</td><td>Fixed $25</td><td>$5-$20</td></tr>",
            "  </table>",
        ]
    )
    lines.extend(
        [
            "",
            "  <h3>Compounding 3-Tier</h3>",
        ]
    )
    lines.extend(table(["Balance", "Formula", "Contoh Lot"], compounding_rows, indent="  "))
    lines.extend(
        [
            "",
            "  <h3>Lot Modifiers</h3>",
        ]
    )
    lines.extend(table(["Kondisi", "Multiplier"], lot_modifier_rows, indent="  "))
    lines.extend(
        [
            "  <p>Minimum selalu 0.01 lot. Reset ke 100% setelah 1 win.</p>",
            "",
            "  <h3>Worst Case Exposure di M15</h3>",
            "  <pre>",
            docs["worst_case_pre"],
            "  </pre>",
            "</section>",
            "",
            "<!-- ============================================================ -->",
            "<!-- 10. REKOMENDASI -->",
            "<!-- ============================================================ -->",
            "<section id=\"s10\">",
            "  <h2><span class=\"ic\" style=\"background:linear-gradient(135deg,rgba(88,166,255,0.2),rgba(188,140,255,0.2))\">10</span> Rekomendasi</h2>",
            "",
        ]
    )
    lines.extend(recommendation_blocks(docs["recommendations"], indent="  "))
    lines.extend(
        [
            "",
            "  <h3>Prioritas</h3>",
        ]
    )
    lines.extend(table(["Priority", "Items", "Impact"], priority_rows, indent="  "))
    lines.extend(
        [
            "",
            "  <div class=\"card info\" style=\"margin-top: 20px;\">",
            "    <div class=\"card-title\">Bottom Line</div>",
            "    <p style=\"margin-bottom:0\">Fondasi SMC solid dengan risk management berlapis. Kekuatan: gold buy bias, progressive lot reduction, dual-strategy regime switch. Kelemahan utama: <strong>SL fixed $25</strong>, <strong>tidak ada trailing/breakeven</strong>, <strong>pending order tidak bisa cancel</strong>. Fix ketiganya = profit factor naik signifikan tanpa ubah core logic.</p>",
            "  </div>",
            "</section>",
            "",
            "</div>",
            "",
            "<div class=\"footer\">",
            f"  <p>{meta['footer_html']}</p>",
            "</div>",
            "",
            "</body>",
            "</html>",
        ]
    )
    return "\n".join(lines) + "\n"


def build_mqh(spec):
    logic = spec["logic"]
    t = logic["trending"]
    s = logic["sideways"]
    r = logic["risk"]
    dead = logic["dead_inputs"]

    return f"""#ifndef __INVICTUS_FORWARD_1_SPEC_GENERATED_MQH__
#define __INVICTUS_FORWARD_1_SPEC_GENERATED_MQH__

#define IF1_REQUIRED_TF PERIOD_M15
#define IF1_TREND_MAGIC {t['magic']}
#define IF1_SIDEWAYS_MAGIC {s['magic']}
#define IF1_TREND_KILLSWITCH_WINS {t['killswitch_daily_wins']}
#define IF1_TREND_DAILY_LOSS_CAP_PCT {t['daily_loss_cap_pct']:.2f}
#define IF1_SIDEWAYS_DAILY_LOSS_CAP_PCT {s['daily_loss_cap_pct']:.2f}
#define IF1_SIDEWAYS_WINS_CAP {s['daily_wins_cap']}
#define IF1_FRIDAY_CUTOFF_HOUR {t['friday_cutoff_hour']}
#define IF1_COOLDOWN_BARS {t['cooldown_bars_after_loss']}
#define IF1_BIAS_LOOKBACK {t['bias_lookback_bars']}
#define IF1_BULLISH_HH_MIN {t['bullish_hh_min']}
#define IF1_BEARISH_LL_MIN {t['bearish_ll_min']}
#define IF1_SWING_LOOKBACK {t['swing_lookback']}
#define IF1_MAX_BOS_BARS_BACK {t['max_bos_bars_back']}
#define IF1_MIN_BREAK_ATR {t['min_break_atr']:.2f}
#define IF1_MIN_BODY_RATIO {t['min_body_ratio']:.2f}
#define IF1_ZONE_SEARCH_WINDOW {t['zone_search_window']}
#define IF1_MAX_ZONE_RANGE_USD {t['max_zone_range_usd']:.2f}
#define IF1_MAX_ZONE_PRIOR_TESTS {t['max_zone_prior_tests']}
#define IF1_ZONE_COOLDOWN_BARS {t['zone_cooldown_bars']}
#define IF1_ZONE_COOLDOWN_TOLERANCE_USD {t['zone_cooldown_tolerance_usd']:.2f}
#define IF1_ENTRY_BODY_RATIO {t['entry_body_ratio']:.2f}
#define IF1_SCORE_ZONE {t['score']['zone']}
#define IF1_SCORE_VOLATILITY {t['score']['volatility']}
#define IF1_SCORE_FVG {t['score']['fvg']}
#define IF1_SCORE_RETEST {t['score']['retest']}
#define IF1_SCORE_SWEEP {t['score']['sweep']}
#define IF1_SCORE_TREND {t['score']['trend']}
#define IF1_SCORE_GOLD_BUY_BONUS {t['score']['gold_buy_bonus']}
#define IF1_SCORE_BUY_MIN {t['score']['buy_min']}
#define IF1_SCORE_SELL_MIN {t['score']['sell_min']}
#define IF1_SCORE_RR_BOOST_MIN {t['score']['rr_boost_min']}
#define IF1_SELL_LOT_MODIFIER {t['sell_lot_modifier']:.2f}
#define IF1_TREND_SL_ATR_BUFFER {t['sl_atr_buffer']:.2f}
#define IF1_TREND_MIN_SL_USD {t['min_sl_usd']:.2f}
#define IF1_TREND_MAX_SL_USD {t['max_sl_usd']:.2f}
#define IF1_TREND_TP_RR_DEFAULT {t['tp_rr_default']:.2f}
#define IF1_TREND_TP_RR_BOOST {t['tp_rr_boost']:.2f}
#define IF1_PENDING_EXPIRY_BARS {t['pending_expiry_bars']}
#define IF1_PENDING_EXPIRY_SECONDS {t['pending_expiry_seconds']}
#define IF1_TIMED_PROFIT_CLOSE_HOURS {t['timed_profit_close_hours']}
#define IF1_TIMED_PROFIT_USD_PER_001 {t['timed_profit_usd_per_0_01']:.2f}
#define IF1_SIDEWAYS_ADX_THRESHOLD {s['adx_threshold_h4']:.2f}
#define IF1_SIDEWAYS_RANGE_BARS {s['range_bars']}
#define IF1_SIDEWAYS_MIN_RANGE_USD {s['min_range_usd']:.2f}
#define IF1_SIDEWAYS_MAX_RANGE_ATR_MULT {s['max_range_atr_multiplier']:.2f}
#define IF1_SIDEWAYS_ENTRY_ZONE_FRACTION {s['entry_zone_fraction']:.2f}
#define IF1_SIDEWAYS_MAX_POSITIONS {s['max_positions']}
#define IF1_SIDEWAYS_CLUSTER_MAX_PER_DAY {s['cluster_max_per_day']}
#define IF1_SIDEWAYS_CLUSTER_TOLERANCE_USD {s['cluster_tolerance_usd']:.2f}
#define IF1_SIDEWAYS_SL_ATR_BUFFER {s['sl_atr_buffer']:.2f}
#define IF1_SIDEWAYS_SL_MIN_USD {s['sl_min_usd']:.2f}
#define IF1_SIDEWAYS_SL_MAX_USD {s['sl_max_usd']:.2f}
#define IF1_SIDEWAYS_TP_FRACTION {s['tp_fraction']:.2f}
#define IF1_SIDEWAYS_LOT_MODIFIER {s['lot_modifier']:.2f}
#define IF1_SLIPPAGE_POINTS {r['slippage_points']}
#define IF1_MIN_LOT {r['min_lot']:.2f}

// Kept intentionally for documentation parity with the original EA notes.
input double BT_RiskPercent = {dead['BT_RiskPercent']:.1f};
input bool   BT_UseFixedLot = {"true" if dead['BT_UseFixedLot'] else "false"};
input double BT_FixedLot = {dead['BT_FixedLot']:.2f};
input int    BT_CompoundingPer = {dead['BT_CompoundingPer']};
input int    BT_MaxDailyWins = {dead['BT_MaxDailyWins']};

static int IF1TrendToxicHours[] = {{{", ".join(str(x) for x in t['toxic_hours'])}}};
static int IF1TrendSellHours[] = {{{", ".join(str(x) for x in t['sell_hours'])}}};
static int IF1SidewaysToxicHours[] = {{{", ".join(str(x) for x in s['toxic_hours'])}}};

#endif
"""


def compare_against_original(spec, generated_html):
    original_path = Path(spec["meta"]["original_html"])
    if not original_path.exists():
        return "Original HTML file not found.\n"

    original = original_path.read_text(encoding="utf-8")
    if original == generated_html:
        return "EXACT MATCH\n"

    diff = difflib.unified_diff(
        original.splitlines(),
        generated_html.splitlines(),
        fromfile=str(original_path),
        tofile=str(HTML_OUT),
        lineterm="",
    )
    diff_lines = list(diff)
    if not diff_lines:
        return "MATCH AFTER LINE NORMALIZATION ONLY\n"
    return "\n".join(diff_lines) + "\n"


def main():
    spec = load_spec()
    html = build_html(spec)
    mqh = build_mqh(spec)

    HTML_OUT.write_text(html, encoding="utf-8")
    MQH_OUT.write_text(mqh, encoding="utf-8")
    COMPARE_OUT.write_text(compare_against_original(spec, html), encoding="utf-8")

    print(f"Wrote {HTML_OUT}")
    print(f"Wrote {MQH_OUT}")
    print(f"Wrote {COMPARE_OUT}")


if __name__ == "__main__":
    main()
