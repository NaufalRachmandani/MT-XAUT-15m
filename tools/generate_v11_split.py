#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path("/Users/naufalrachmandani/Hobby/MT5 XAU 15m")
SOURCE = ROOT / "mt5" / "InvictusForward1M15_v10.mq5"


def replace_named_value(text: str, name: str, value: str) -> str:
    pattern = re.compile(rf"^(input\s+[^\n]*{re.escape(name)})\s*=\s*[^;]+;", re.MULTILINE)
    text, count = pattern.subn(rf"\1 = {value};", text, count=1)
    if count != 1:
        raise RuntimeError(f"failed to replace {name}")
    return text


def insert_after(text: str, needle: str, addition: str) -> str:
    if needle not in text:
        raise RuntimeError(f"needle not found: {needle[:80]!r}")
    return text.replace(needle, needle + addition, 1)


def insert_before(text: str, needle: str, addition: str) -> str:
    if needle not in text:
        raise RuntimeError(f"needle not found: {needle[:80]!r}")
    return text.replace(needle, addition + needle, 1)


def patch_common(text: str, *, magic: int, comment_prefix: str, variant: str, opposite_magic: int) -> str:
    text = text.replace('#property version   "2.00"', '#property version   "3.00"', 1)
    text = text.replace("// Variant: v10", f"// Variant: {variant}", 1)
    text = text.replace("static const ulong V10_MAGIC = 2026042001;", f"static const ulong V10_MAGIC = {magic};", 1)
    text = text.replace('string comment = "Inv|" + engineCode + "|S" + IntegerToString(score) + "|" + grade;',
                        f'string comment = "{comment_prefix}|" + engineCode + "|S" + IntegerToString(score) + "|" + grade;',
                        1)

    text = insert_after(
        text,
        "input bool   V10_EnableMixedMomentumEntries = false;\n",
        "input bool   V11_BlockOppositeDirection = true;\n"
        f"input long   V11_OppositeMagic = {opposite_magic};\n",
    )

    text = insert_after(
        text,
        "int V10CountOpenPositionsByType(const bool sell)\n"
        "  {\n"
        "   int count = 0;\n"
        "   for(int i = PositionsTotal() - 1; i >= 0; i--)\n"
        "     {\n"
        "      ulong ticket = PositionGetTicket(i);\n"
        "      if(ticket == 0 || !PositionSelectByTicket(ticket))\n"
        "         continue;\n"
        "      if(PositionGetString(POSITION_SYMBOL) != _Symbol)\n"
        "         continue;\n"
        "      if((ulong)PositionGetInteger(POSITION_MAGIC) != V10_MAGIC)\n"
        "         continue;\n"
        "      ENUM_POSITION_TYPE type = (ENUM_POSITION_TYPE)PositionGetInteger(POSITION_TYPE);\n"
        "      if((sell && type == POSITION_TYPE_SELL) || (!sell && type == POSITION_TYPE_BUY))\n"
        "         count++;\n"
        "     }\n"
        "   return(count);\n"
        "  }\n",
        "\n\n"
        "bool V11HasOpenPositionByMagicType(const bool sell, const ulong magic)\n"
        "  {\n"
        "   for(int i = PositionsTotal() - 1; i >= 0; i--)\n"
        "     {\n"
        "      ulong ticket = PositionGetTicket(i);\n"
        "      if(ticket == 0 || !PositionSelectByTicket(ticket))\n"
        "         continue;\n"
        "      if(PositionGetString(POSITION_SYMBOL) != _Symbol)\n"
        "         continue;\n"
        "      if((ulong)PositionGetInteger(POSITION_MAGIC) != magic)\n"
        "         continue;\n"
        "      ENUM_POSITION_TYPE type = (ENUM_POSITION_TYPE)PositionGetInteger(POSITION_TYPE);\n"
        "      if((sell && type == POSITION_TYPE_SELL) || (!sell && type == POSITION_TYPE_BUY))\n"
        "         return(true);\n"
        "     }\n"
        "   return(false);\n"
        "  }\n\n"
        "bool V11OppositePositionBlocks(const bool wantSell)\n"
        "  {\n"
        "   if(!V11_BlockOppositeDirection)\n"
        "      return(false);\n"
        "   bool oppositeSell = !wantSell;\n"
        "   if(V11HasOpenPositionByMagicType(oppositeSell, V10_MAGIC))\n"
        "      return(true);\n"
        "   if(V11_OppositeMagic > 0 && V11HasOpenPositionByMagicType(oppositeSell, (ulong)V11_OppositeMagic))\n"
        "      return(true);\n"
        "   return(false);\n"
        "  }\n",
    )

    text = insert_before(
        text,
        "      if(V10BuildBearSubSignal(rates, emaM5, atr, entryRegime, signal))\n",
        "      if(V11OppositePositionBlocks(true))\n"
        "         return(false);\n",
    )
    text = insert_before(
        text,
        "      if(V10BuildBullSubSignal(rates, emaM5, atr, entryRegime, signal))\n",
        "      if(V11OppositePositionBlocks(false))\n"
        "         return(false);\n",
    )
    return text


def source_inputs(text: str) -> list[str]:
    values: list[str] = []
    pattern = re.compile(r"^input\s+[A-Za-z_][A-Za-z0-9_<>]*\s+([A-Za-z_][A-Za-z0-9_]*)\s*=\s*([^;]+);", re.MULTILINE)
    for name, raw_value in pattern.findall(text):
        values.append(f"{name}={raw_value.strip()}")
    return values


def write_variant(filename: str, set_filename: str, text: str) -> None:
    source_path = ROOT / "mt5" / filename
    source_path.write_text(text)
    (ROOT / "mt5" / set_filename).write_text("\n".join(source_inputs(text)) + "\n")


def main() -> None:
    base = SOURCE.read_text()

    bull = patch_common(
        base,
        magic=2026042411,
        comment_prefix="B11",
        variant="v11 bull-only M5",
        opposite_magic=2026042412,
    )
    for name, value in {
        "V10_RiskPercent": "5.00",
        "V10_BuyRiskMultiplier": "0.60",
        "V10_SellRiskMultiplier": "1.00",
        "V10_WeakBuyRiskMultiplier": "0.22",
        "V10_WeakSellRiskMultiplier": "0.55",
        "V10_EnableBuys": "true",
        "V10_EnableSells": "false",
        "V10_MaxPositions": "6",
        "V10_WeakRegimeMaxPositions": "2",
        "V10_EnableBullSubEngine": "false",
        "V10_BullSubAllowWeakBull": "false",
        "V10_EnableBearSubEngine": "false",
        "V10_ZoneLookback": "8",
        "V10_ZoneMinBodyRatio": "0.46",
        "V10_ZoneBreakATR": "0.02",
        "V10_ZoneMidTouchATR": "0.10",
        "V10_ZoneOvershootATR": "0.35",
        "V10_ZoneRiskMultiplier": "0.70",
        "V10_ZoneRR": "1.20",
        "V10_BuyMinBreakATR": "0.08",
        "V10_WeakBuyMinBreakATR": "0.12",
        "V10_WeakSellMinBreakATR": "0.08",
        "V10_BuyMinBodyRatio": "0.50",
        "V10_WeakBuyMinBodyRatio": "0.56",
        "V10_WeakSellMinBodyRatio": "0.50",
        "V10_FastFailBuyGuard": "false",
        "V10_FastFailPullbackOnly": "true",
        "V10_FastFailBars": "6",
        "V10_FastFailMinProgressR": "0.10",
        "V10_WeakOutsideSellQuickExit": "true",
        "V10_WeakOutsideSellExitBars": "6",
        "V10_MinTradeScore": "68",
        "V10_EnableBuyAddOns": "true",
        "V10_EnableSellAddOns": "false",
        "V10_AddOnRiskMultiplier": "0.32",
        "V10_AddOnMinProgressR": "0.65",
        "V10_AddOnRR": "1.10",
    }.items():
        bull = replace_named_value(bull, name, value)
    write_variant("InvictusBullM5_v11.mq5", "InvictusBullM5_v11.default_2026.set", bull)

    bear = patch_common(
        base,
        magic=2026042412,
        comment_prefix="S11",
        variant="v11 bear-only M5",
        opposite_magic=2026042411,
    )
    for name, value in {
        "V10_RiskPercent": "5.00",
        "V10_BuyRiskMultiplier": "0.60",
        "V10_SellRiskMultiplier": "1.00",
        "V10_WeakBuyRiskMultiplier": "0.22",
        "V10_WeakSellRiskMultiplier": "0.55",
        "V10_EnableBuys": "false",
        "V10_EnableSells": "true",
        "V10_MaxPositions": "6",
        "V10_WeakRegimeMaxPositions": "2",
        "V10_EnableBullSubEngine": "false",
        "V10_EnableBearSubEngine": "false",
        "V10_BearSubAllowWeakBear": "false",
        "V10_ZoneLookback": "8",
        "V10_ZoneMinBodyRatio": "0.46",
        "V10_ZoneBreakATR": "0.02",
        "V10_ZoneMidTouchATR": "0.10",
        "V10_ZoneOvershootATR": "0.35",
        "V10_ZoneAllowWeakRegime": "true",
        "V10_ZoneRiskMultiplier": "0.70",
        "V10_ZoneRR": "1.20",
        "V10_BuyMinBreakATR": "0.08",
        "V10_WeakBuyMinBreakATR": "0.12",
        "V10_WeakSellMinBreakATR": "0.08",
        "V10_BuyMinBodyRatio": "0.50",
        "V10_WeakBuyMinBodyRatio": "0.56",
        "V10_WeakSellMinBodyRatio": "0.50",
        "V10_WeakOutsideSellQuickExit": "true",
        "V10_WeakOutsideSellExitBars": "6",
        "V10_MinTradeScore": "68",
        "V10_EnableBuyAddOns": "false",
        "V10_EnableSellAddOns": "true",
        "V10_AddOnAllowWeakRegime": "false",
        "V10_AddOnRiskMultiplier": "0.32",
        "V10_AddOnMinProgressR": "0.65",
        "V10_AddOnRR": "1.10",
    }.items():
        bear = replace_named_value(bear, name, value)
    write_variant("InvictusBearM5_v11.mq5", "InvictusBearM5_v11.default_2026.set", bear)

    combined = patch_common(
        base,
        magic=2026042499,
        comment_prefix="C11",
        variant="v11 combined tester M5",
        opposite_magic=0,
    )
    for name, value in {
        "V10_RiskPercent": "5.00",
        "V10_BuyRiskMultiplier": "0.60",
        "V10_SellRiskMultiplier": "1.00",
        "V10_WeakBuyRiskMultiplier": "0.22",
        "V10_WeakSellRiskMultiplier": "0.55",
        "V10_EnableBuys": "true",
        "V10_EnableSells": "true",
        "V10_MaxPositions": "6",
        "V10_WeakRegimeMaxPositions": "2",
        "V10_EnableBullSubEngine": "false",
        "V10_BullSubAllowWeakBull": "false",
        "V10_EnableBearSubEngine": "false",
        "V10_BearSubAllowWeakBear": "false",
        "V10_ZoneLookback": "8",
        "V10_ZoneMinBodyRatio": "0.46",
        "V10_ZoneBreakATR": "0.02",
        "V10_ZoneMidTouchATR": "0.10",
        "V10_ZoneOvershootATR": "0.35",
        "V10_ZoneRiskMultiplier": "0.70",
        "V10_ZoneRR": "1.20",
        "V10_BuyMinBreakATR": "0.08",
        "V10_WeakBuyMinBreakATR": "0.12",
        "V10_WeakSellMinBreakATR": "0.08",
        "V10_BuyMinBodyRatio": "0.50",
        "V10_WeakBuyMinBodyRatio": "0.56",
        "V10_WeakSellMinBodyRatio": "0.50",
        "V10_FastFailBuyGuard": "false",
        "V10_FastFailPullbackOnly": "true",
        "V10_FastFailBars": "6",
        "V10_FastFailMinProgressR": "0.10",
        "V10_WeakOutsideSellQuickExit": "true",
        "V10_WeakOutsideSellExitBars": "6",
        "V10_MinTradeScore": "68",
        "V10_EnableBuyAddOns": "true",
        "V10_EnableSellAddOns": "true",
        "V10_AddOnAllowWeakRegime": "false",
        "V10_AddOnRiskMultiplier": "0.32",
        "V10_AddOnMinProgressR": "0.65",
        "V10_AddOnRR": "1.10",
    }.items():
        combined = replace_named_value(combined, name, value)
    write_variant("InvictusCombinedM5_v11.mq5", "InvictusCombinedM5_v11.default_2026.set", combined)


if __name__ == "__main__":
    main()
