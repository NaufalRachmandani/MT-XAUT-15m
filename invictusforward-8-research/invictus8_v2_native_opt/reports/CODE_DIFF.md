# Base vs V1 vs V2 Code/Logic Diff

## Summary

- Base is the untouched source from the zip.
- V1 adds the research guardrails: bad-hour filters, Drop Catcher hour filter, max trend position guard, and range-entry cap input.
- V2 keeps V1 trading logic and adds `OnTester()` export for native MT5 optimization pass capture; selected behavior differences are parameter-level and documented in `PARAM_DIFF.md`.

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

## V1 -> V2 Unified Diff

```diff
--- V1/InvictusForward-8-Tuned.mq5
+++ V2/InvictusForward-8-V2.mq5
@@ -1,10 +1,10 @@
 //+------------------------------------------------------------------+
-//|                              InvictusForward-8-Tuned.mq5       |
+//|                                 InvictusForward-8-V2.mq5       |
 //|                           Invictus Trading System                |
 //|            M15 Scalping EA — SMC Breakout + Sideways Bounce      |
 //+------------------------------------------------------------------+
 #property copyright   "Invictus Trading System"
-#property version     "1.25"
+#property version     "2.00"
 #property description "M15 Scalping EA — Trending (SMC Breakout) + Sideways (Range Bounce)"
 #property description "XAUUSD optimized | ADX H4 regime detection"
 
@@ -164,7 +164,7 @@
       Print("[BT] WARNING: Could not create ADX H1 handle");
 
    LogOpen();
-   LogWrite("[INIT] InvictusForward-8-Tuned v1.25 M15 — Research guardrails");
+   LogWrite("[INIT] InvictusForward-8 V2 M15 — Native MT5 optimization profile");
    return INIT_SUCCEEDED;
 }
 
@@ -983,4 +983,50 @@
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
+   int handle = FileOpen(
+      "InvictusForward8_V2_optimization_passes.csv",
+      FILE_COMMON | FILE_CSV | FILE_READ | FILE_WRITE | FILE_SHARE_READ | FILE_SHARE_WRITE,
+      ';'
+   );
+   if(handle != INVALID_HANDLE)
+   {
+      if(FileSize(handle) <= 2)
+      {
+         FileWrite(handle,
+                   "profit", "profit_factor", "trades", "equity_dd_pct", "balance_dd_pct", "recovery_factor",
+                   "BT_CompoundingPer", "BT_MaxLotCap",
+                   "Guard_BlockHour04", "Guard_BlockHour05", "Guard_BlockHour10", "Guard_BlockHour11",
+                   "Guard_DC_BlockHour00", "Guard_DC_BlockHour01", "Guard_DC_BlockHour10", "Guard_DC_BlockHour23",
+                   "Guard_MaxTrendPosLowBalance", "Guard_MaxTrendPosMidBalance", "Guard_MaxTrendPosHighBalance",
+                   "RangeBounce_LotMult", "RangeBounce_MaxBuy", "RangeBounce_MaxSell", "RangeBounce_EntryPct", "RangeBounce_MaxEntriesPerRange",
+                   "DropCatcher_BodyATR", "DropCatcher_MinBodyDlr", "DropCatcher_VolMult", "DropCatcher_MaxATR",
+                   "DropCatcher_SL_ATR", "DropCatcher_RR", "DropCatcher_LotMult", "DropCatcher_TrailATR",
+                   "SidewaysMinMethods", "MTF_H1_ADX_Max", "MTF_H4_ADX_Max", "PriceRange_ATRMult");
+      }
+      FileSeek(handle, 0, SEEK_END);
+      FileWrite(handle,
+                profit, pf, trades, equityDdPct, balanceDdPct, recovery,
+                BT_CompoundingPer, BT_MaxLotCap,
+                Guard_BlockHour04, Guard_BlockHour05, Guard_BlockHour10, Guard_BlockHour11,
+                Guard_DC_BlockHour00, Guard_DC_BlockHour01, Guard_DC_BlockHour10, Guard_DC_BlockHour23,
+                Guard_MaxTrendPosLowBalance, Guard_MaxTrendPosMidBalance, Guard_MaxTrendPosHighBalance,
+                RangeBounce_LotMult, RangeBounce_MaxBuy, RangeBounce_MaxSell, RangeBounce_EntryPct, RangeBounce_MaxEntriesPerRange,
+                DropCatcher_BodyATR, DropCatcher_MinBodyDlr, DropCatcher_VolMult, DropCatcher_MaxATR,
+                DropCatcher_SL_ATR, DropCatcher_RR, DropCatcher_LotMult, DropCatcher_TrailATR,
+                SidewaysMinMethods, MTF_H1_ADX_Max, MTF_H4_ADX_Max, PriceRange_ATRMult);
+      FileClose(handle);
+   }
+
+   return profit;
+}
+//+------------------------------------------------------------------+
```
