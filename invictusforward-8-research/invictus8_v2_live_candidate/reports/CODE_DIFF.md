# Base vs V1 vs V2Live Code/Logic Diff

## Summary

- Base is the untouched source from the zip.
- V1 is the first tuned research guardrail profile.
- V2Live starts from V1, lowers cent-account exposure, adds module-specific order comments, and exports a risk-adjusted native `OnTester()` score.

## Base -> V1 Unified Diff

```diff
--- Base/InvictusForward-8.mq5
+++ V1/InvictusForward-8-Tuned.mq5
@@ -1,10 +1,10 @@
 //+------------------------------------------------------------------+
-//|                                    InvictusForward-8.mq5       |
+//|                              InvictusForward-8-Tuned.mq5       |
 //|                           Invictus Trading System                |
 //|            M15 Scalping EA — SMC Breakout + Sideways Bounce      |
 //+------------------------------------------------------------------+
 #property copyright   "Invictus Trading System"
-#property version     "1.20"
+#property version     "1.25"
 #property description "M15 Scalping EA — Trending (SMC Breakout) + Sideways (Range Bounce)"
 #property description "XAUUSD optimized | ADX H4 regime detection"
 
@@ -78,6 +78,36 @@
 double         gs_lastRangeLow  = 0;
 int            gs_rangeEntries  = 0;
 
+//+------------------------------------------------------------------+
+//  Research guardrails
+//+------------------------------------------------------------------+
+bool GuardBadHour(int hour)
+{
+   if(!Guard_EnableBadHourFilter) return false;
+   if(hour == 4  && Guard_BlockHour04) return true;
+   if(hour == 5  && Guard_BlockHour05) return true;
+   if(hour == 10 && Guard_BlockHour10) return true;
+   if(hour == 11 && Guard_BlockHour11) return true;
+   return false;
+}
+
+bool GuardDropCatcherHour(int hour)
+{
+   if(!Guard_EnableDropCatcherHourFilter) return false;
+   if(hour == 0  && Guard_DC_BlockHour00) return true;
+   if(hour == 1  && Guard_DC_BlockHour01) return true;
+   if(hour == 10 && Guard_DC_BlockHour10) return true;
+   if(hour == 23 && Guard_DC_BlockHour23) return true;
+   return false;
+}
+
+int GuardMaxTrendPositions(double balance)
+{
+   if(balance <= 20000.0) return MathMax(1, Guard_MaxTrendPosLowBalance);
+   if(balance <= 50000.0) return MathMax(1, Guard_MaxTrendPosMidBalance);
+   return MathMax(1, Guard_MaxTrendPosHighBalance);
+}
+
 //--- Trade management module (uses globals declared above)
 #include "IH_TradeManager.mqh"
 
@@ -134,7 +164,7 @@
       Print("[BT] WARNING: Could not create ADX H1 handle");
 
    LogOpen();
-   LogWrite("[INIT] InvictusForward-8 v1.24 M15 — Iter5: RangeBounce Dual");
+   LogWrite("[INIT] InvictusForward-8-Tuned v1.25 M15 — Research guardrails");
    return INIT_SUCCEEDED;
 }
 
@@ -268,6 +298,7 @@
    MqlDateTime dcDt;
    TimeToStruct(iTime(_Symbol, _Period, refBar), dcDt);
    if(dcDt.hour == 3 || dcDt.hour == 17 || dcDt.hour == 19) return;
+   if(GuardDropCatcherHour(dcDt.hour)) return;
 
    double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
    double slDist = atr * DropCatcher_SL_ATR;
@@ -465,6 +496,7 @@
 
    //--- Toxic hours filter (H3,H17 original + H1,H2,H14 from backtest data: WR ~50%, net -$97k)
    if(dt.hour == 1 || dt.hour == 2 || dt.hour == 3 || dt.hour == 14 || dt.hour == 17) return;
+   if(GuardBadHour(dt.hour)) { LogWrite("[TR-SKIP] GuardBadHour H" + IntegerToString(dt.hour)); return; }
 
    //--- High volatility filter: skip during ATR spikes (news/flash crash)
    {
@@ -587,7 +619,7 @@
 
    //--- Max positions check (tier-based)
    double bal = AccountInfoDouble(ACCOUNT_BALANCE);
-   int maxPos = (bal <= 20000.0) ? 5 : (bal <= 50000.0) ? 3 : 3;
+   int maxPos = GuardMaxTrendPositions(bal);
    int openPos = CountPositions(EA_MAGIC_BT);
    if(openPos >= maxPos) { LogWrite("[TR-SKIP] MaxPos " + IntegerToString(openPos) + "/" + IntegerToString(maxPos)); return; }
 
@@ -718,6 +750,7 @@
 
    //--- Toxic hours: data-driven (WR 0-14% at these hours)
    if(dt.hour == 3 || dt.hour == 19) return;
+   if(GuardBadHour(dt.hour)) return;
 
    //--- After-loss cooldown: 2 bars M15 (30 min)
    if(gs_lastSLTime > 0)
@@ -791,7 +824,7 @@
    //--- Cluster protection: max 2 entries per range per day
    bool sameRange = (MathAbs(rangeHigh - gs_lastRangeHigh) < 5.0 &&
                      MathAbs(rangeLow - gs_lastRangeLow) < 5.0);
-   if(sameRange && gs_rangeEntries >= 4) return;
+   if(sameRange && gs_rangeEntries >= RangeBounce_MaxEntriesPerRange) return;
 
    //--- Calculate SL/TP
    double slBuffer = (atrVal > 0) ? atrVal * 0.5 : 3.0;
```

## V1 -> V2Live Unified Diff

```diff
--- V1/InvictusForward-8-Tuned.mq5
+++ V2Live/InvictusForward-8-V2Live.mq5
@@ -1,10 +1,10 @@
 //+------------------------------------------------------------------+
-//|                              InvictusForward-8-Tuned.mq5       |
+//|                             InvictusForward-8-V2Live.mq5       |
 //|                           Invictus Trading System                |
 //|            M15 Scalping EA — SMC Breakout + Sideways Bounce      |
 //+------------------------------------------------------------------+
 #property copyright   "Invictus Trading System"
-#property version     "1.25"
+#property version     "2.10"
 #property description "M15 Scalping EA — Trending (SMC Breakout) + Sideways (Range Bounce)"
 #property description "XAUUSD optimized | ADX H4 regime detection"
 
@@ -17,11 +17,11 @@
 
 //--- EA-specific inputs
 input group "══════ Trade Settings ══════"
-input double   BT_RiskPercent       = 3.0;      // Risk % per trade
+input double   BT_RiskPercent       = 1.0;      // Risk % per trade
 input bool     BT_UseFixedLot       = false;     // Use fixed lot size
 input double   BT_FixedLot          = 0.01;      // Fixed lot size
-input double   BT_CompoundingPer    = 500.0;     // Balance per 0.01 lot
-input double   BT_MaxLotCap         = 1.50;      // Absolute max lot size
+input double   BT_CompoundingPer    = 1000.0;    // Balance per 0.01 lot
+input double   BT_MaxLotCap         = 0.25;      // Absolute max lot size
 input bool     BT_EnableSideways    = true;       // Enable sideways range bounce
 input double   BT_MinSLDollar       = 25.0;      // Min SL distance ($)
 input double   BT_MaxSLDollar       = 25.0;      // Max SL distance ($)
@@ -164,7 +164,7 @@
       Print("[BT] WARNING: Could not create ADX H1 handle");
 
    LogOpen();
-   LogWrite("[INIT] InvictusForward-8-Tuned v1.25 M15 — Research guardrails");
+   LogWrite("[INIT] InvictusForward-8-V2Live v2.10 M15 — Cent live-candidate guardrails");
    return INIT_SUCCEEDED;
 }
 
@@ -325,7 +325,7 @@
    if(lot < 0.01) lot = 0.01;
    if(lot > BT_MaxLotCap) lot = BT_MaxLotCap;
 
-   gdc_trade.Sell(lot, _Symbol, 0, dcSL, dcTP, "IHB DropCatch");
+   gdc_trade.Sell(lot, _Symbol, 0, dcSL, dcTP, "IF8V2L_DC DropCatch");
 
    LogWrite("[DC-ORDER] SELL @ " + DoubleToString(bid,2) +
             " SL:" + DoubleToString(dcSL,2) +
@@ -700,7 +700,7 @@
    //--- Place order
    double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
    double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
-   string comment = StringFormat("IHB S:%d %s", score,
+   string comment = StringFormat("IF8V2L_TR S:%d %s", score,
                                   bos.quality == IH_BOS_IMPULSIVE ? "IMP" : "COR");
 
    if(isBuy)
@@ -894,7 +894,7 @@
 
    //--- Place order
    string dir = doBuy ? "BUY" : "SELL";
-   string comment = StringFormat("IHS RB %s R:$%.0f", dir, rangeSize);
+   string comment = StringFormat("IF8V2L_RB %s R:$%.0f", dir, rangeSize);
 
    if(doBuy)
       gs_trade.Buy(lot, _Symbol, 0, sl, tp, comment);
@@ -983,4 +983,48 @@
       }
    }
 }
-//+------------------------------------------------------------------+
+
+double OnTester()
+{
+   double profit = TesterStatistics(STAT_PROFIT);
+   double pf = TesterStatistics(STAT_PROFIT_FACTOR);
+   double trades = TesterStatistics(STAT_TRADES);
+   double equityDdPct = TesterStatistics(STAT_EQUITY_DDREL_PERCENT);
+   double balanceDdPct = TesterStatistics(STAT_BALANCE_DDREL_PERCENT);
+   double recovery = TesterStatistics(STAT_RECOVERY_FACTOR);
+
+   double score = profit;
+   if(profit <= 0.0 || pf < 1.05 || trades < 10.0)
+      score = profit - 100000.0;
+   else
+      score = profit * MathMin(pf, 3.0) * MathMax(recovery, 0.1) / (1.0 + equityDdPct + (balanceDdPct * 0.5));
+
+   int handle = FileOpen(
+      "InvictusForward8_V2Live_optimization_passes.csv",
+      FILE_COMMON | FILE_CSV | FILE_READ | FILE_WRITE | FILE_SHARE_READ | FILE_SHARE_WRITE,
+      ';'
+   );
+   if(handle != INVALID_HANDLE)
+   {
+      if(FileSize(handle) <= 2)
+      {
+         FileWrite(handle,
+                   "score", "profit", "profit_factor", "trades", "equity_dd_pct", "balance_dd_pct", "recovery_factor",
+                   "BT_RiskPercent", "BT_CompoundingPer", "BT_MaxLotCap",
+                   "Guard_MaxTrendPosLowBalance",
+                   "RangeBounce_LotMult", "RangeBounce_MaxBuy", "RangeBounce_MaxSell", "RangeBounce_MaxEntriesPerRange",
+                   "DropCatcher_LotMult");
+      }
+      FileSeek(handle, 0, SEEK_END);
+      FileWrite(handle,
+                score, profit, pf, trades, equityDdPct, balanceDdPct, recovery,
+                BT_RiskPercent, BT_CompoundingPer, BT_MaxLotCap,
+                Guard_MaxTrendPosLowBalance,
+                RangeBounce_LotMult, RangeBounce_MaxBuy, RangeBounce_MaxSell, RangeBounce_MaxEntriesPerRange,
+                DropCatcher_LotMult);
+      FileClose(handle);
+   }
+
+   return score;
+}
+//+------------------------------------------------------------------+
```
