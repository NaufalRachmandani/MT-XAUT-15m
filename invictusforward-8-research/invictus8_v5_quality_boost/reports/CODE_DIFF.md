# V3Guard vs V5Boost Code Diff

```diff
--- V3Guard/InvictusForward-8-V3Guard.mq5
+++ V5Boost/InvictusForward-8-V5Boost.mq5
@@ -1,10 +1,10 @@
 //+------------------------------------------------------------------+
-//|                            InvictusForward-8-V3Guard.mq5       |
+//|                            InvictusForward-8-V5Boost.mq5       |
 //|                           Invictus Trading System                |
 //|            M15 Scalping EA — SMC Breakout + Sideways Bounce      |
 //+------------------------------------------------------------------+
 #property copyright   "Invictus Trading System"
-#property version     "3.00"
+#property version     "5.00"
 #property description "M15 Scalping EA — Trending (SMC Breakout) + Sideways (Range Bounce)"
 #property description "XAUUSD optimized | ADX H4 regime detection"
 
@@ -125,6 +125,66 @@
    return MathMax(1, Guard_MaxTrendPosHighBalance);
 }
 
+double BaseLotByBalance(double balance)
+{
+   double lowPer = MathMax(BT_CompoundingPer, 100.0);
+   double midPer = MathMax(lowPer * 1.5, 100.0);
+   double highPer = MathMax(lowPer * 3.0, 100.0);
+   double lot;
+
+   if(BT_UseFixedLot)
+      lot = BT_FixedLot;
+   else if(balance <= 20000.0)
+      lot = NormalizeDouble(MathFloor(balance / lowPer) * 0.01, 2);
+   else if(balance <= 50000.0)
+   {
+      double baseLot = NormalizeDouble(MathFloor(20000.0 / lowPer) * 0.01, 2);
+      double extraLot = NormalizeDouble(MathFloor((balance - 20000.0) / midPer) * 0.01, 2);
+      lot = baseLot + extraLot;
+   }
+   else
+   {
+      double baseLot = NormalizeDouble(MathFloor(20000.0 / lowPer) * 0.01, 2);
+      baseLot += NormalizeDouble(MathFloor(30000.0 / midPer) * 0.01, 2);
+      double extraLot = NormalizeDouble(MathFloor((balance - 50000.0) / highPer) * 0.01, 2);
+      lot = baseLot + extraLot;
+   }
+
+   if(lot < 0.01) lot = 0.01;
+   if(lot > BT_MaxLotCap) lot = BT_MaxLotCap;
+   return NormalizeDouble(lot, 2);
+}
+
+double V5TrendQualityLotMultiplier(int score, int hour)
+{
+   if(!V5_EnableTrendQualityScaling)
+      return 1.0;
+
+   if(V5_BlockScore85Hour09 && hour == 9 && score <= 85)
+      return 0.0;
+   if(V5_BlockScore90Hour12 && hour == 12 && score <= 90)
+      return 0.0;
+   if(V5_BlockScore85Hour15 && hour == 15 && score <= 85)
+      return 0.0;
+
+   double mult = 1.0;
+   if(score <= 85)
+      mult *= V5_TrendScore85LotMult;
+   else if(score <= 90)
+      mult *= V5_TrendScore90LotMult;
+   else if(score <= 95)
+      mult *= V5_TrendScore95LotMult;
+
+   if(hour == 9)
+      mult *= V5_TrendHour09LotMult;
+   else if(hour == 12)
+      mult *= V5_TrendHour12LotMult;
+   else if(hour == 15)
+      mult *= V5_TrendHour15LotMult;
+
+   return MathMax(0.0, MathMin(mult, 2.0));
+}
+
 //--- Trade management module (uses globals declared above)
 #include "IH_TradeManager.mqh"
 
@@ -181,7 +241,7 @@
       Print("[BT] WARNING: Could not create ADX H1 handle");
 
    LogOpen();
-   LogWrite("[INIT] InvictusForward-8-V3Guard v3.00 M15 — April guard experiment");
+   LogWrite("[INIT] InvictusForward-8-V5Boost v5.00 M15 — quality-scaled profit boost experiment");
    return INIT_SUCCEEDED;
 }
 
@@ -324,26 +384,12 @@
    double dcTP = NormalizeDouble(bid - (slDist * DropCatcher_RR), 2);
 
    double balance = AccountInfoDouble(ACCOUNT_BALANCE);
-   double lot;
-   if(balance <= 20000.0)
-      lot = NormalizeDouble(MathFloor(balance / 500.0) * 0.01, 2);
-   else if(balance <= 50000.0)
-   {
-      double baseLot = 0.40;
-      double extraLot = NormalizeDouble(MathFloor((balance - 20000.0) / 750.0) * 0.01, 2);
-      lot = baseLot + extraLot;
-   }
-   else
-   {
-      double baseLot = 0.80;
-      double extraLot = NormalizeDouble(MathFloor((balance - 50000.0) / 1500.0) * 0.01, 2);
-      lot = baseLot + extraLot;
-   }
+   double lot = BaseLotByBalance(balance);
    lot = NormalizeDouble(lot * DropCatcher_LotMult, 2);
    if(lot < 0.01) lot = 0.01;
    if(lot > BT_MaxLotCap) lot = BT_MaxLotCap;
 
-   gdc_trade.Sell(lot, _Symbol, 0, dcSL, dcTP, "IF8V3G_DC DropCatch");
+   gdc_trade.Sell(lot, _Symbol, 0, dcSL, dcTP, "IF8V5Q_DC DropCatch");
 
    LogWrite("[DC-ORDER] SELL @ " + DoubleToString(bid,2) +
             " SL:" + DoubleToString(dcSL,2) +
@@ -642,6 +688,13 @@
    //--- Grade check
    if(score < minScore) { LogWrite("[TR-SKIP] Score " + IntegerToString(score) + " < " + IntegerToString(minScore) + " | " + (isBuy?"BUY":"SELL") + (isSideways?" SW":"")); return; }
 
+   double v5QualityLotMult = V5TrendQualityLotMultiplier(score, dt.hour);
+   if(v5QualityLotMult <= 0.0)
+   {
+      LogWrite("[TR-SKIP] V5 quality hard block | Score:" + IntegerToString(score) + " H:" + IntegerToString(dt.hour));
+      return;
+   }
+
    //--- Max positions check (tier-based)
    double bal = AccountInfoDouble(ACCOUNT_BALANCE);
    int maxPos = GuardMaxTrendPositions(bal);
@@ -657,9 +710,9 @@
 
    //--- Dynamic RR tiers based on score (stronger setup = bigger TP)
    double rr;
-   if(score >= 100)      rr = 2.5;        // top setup: FVG+Retest+Trend+Zone
-   else if(score >= 90)  rr = 2.0;        // strong setup
-   else                  rr = IH_TP1_RR;  // standard (1.5)
+   if(score >= 100)      rr = Trend_RRTop;
+   else if(score >= 90)  rr = Trend_RRStrong;
+   else                  rr = Trend_RRStandard;
 
    if(isBuy)
    {
@@ -683,29 +736,12 @@
    sl = NormalizeDouble(sl, 2);
    tp = NormalizeDouble(tp, 2);
 
-   //--- Lot sizing (compounding 3-tier, aggressive at mid-high balance)
-   //    Tier 1: 0-20k  = $500/0.01 (safe growth phase)
-   //    Tier 2: 20-50k = $750/0.01 (accelerate — edge proven by now)
-   //    Tier 3: 50k+   = $1500/0.01 (aggressive — BUY-only = higher WR)
    double balance = AccountInfoDouble(ACCOUNT_BALANCE);
-   double lot;
-   if(balance <= 20000.0)
-      lot = NormalizeDouble(MathFloor(balance / 500.0) * 0.01, 2);
-   else if(balance <= 50000.0)
-   {
-      double baseLot = 0.40;
-      double extraLot = NormalizeDouble(MathFloor((balance - 20000.0) / 750.0) * 0.01, 2);
-      lot = baseLot + extraLot;
-   }
-   else
-   {
-      double baseLot = 0.80;  // 0.40 + 0.40 at $50k
-      double extraLot = NormalizeDouble(MathFloor((balance - 50000.0) / 1500.0) * 0.01, 2);
-      lot = baseLot + extraLot;
-   }
+   double lot = BaseLotByBalance(balance);
    if(lot < 0.01) lot = 0.01;
    if(lot > BT_MaxLotCap) lot = BT_MaxLotCap;
    lot = NormalizeDouble(lot * Trend_LotMult, 2);
+   lot = NormalizeDouble(lot * v5QualityLotMult, 2);
    if(lot < 0.01) lot = 0.01;
 
    //--- Progressive lot reduction on consecutive losses (start at 2)
@@ -727,7 +763,7 @@
    //--- Place order
    double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
    double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
-   string comment = StringFormat("IF8V3G_TR S:%d %s", score,
+   string comment = StringFormat("IF8V5Q_TR S:%d %s", score,
                                   bos.quality == IH_BOS_IMPULSIVE ? "IMP" : "COR");
 
    if(isBuy)
@@ -757,6 +793,7 @@
            " Ret:" + (bos.hasRetest ? "Y" : "N") +
            " Swp:" + (bos.hasSweep ? "Y" : "N") +
            " Lot:" + DoubleToString(lot,2) +
+           " QMult:" + DoubleToString(v5QualityLotMult,2) +
            " RR:" + DoubleToString(rr,1) +
            (ask > entryPrice && isBuy ? " LIMIT" : " MARKET"));
 }
@@ -880,23 +917,8 @@
    sl = NormalizeDouble(sl, 2);
    tp = NormalizeDouble(tp, 2);
 
-   //--- Lot sizing with RangeBounce_LotMult
    double balance = AccountInfoDouble(ACCOUNT_BALANCE);
-   double lot;
-   if(balance <= 20000.0)
-      lot = NormalizeDouble(MathFloor(balance / 500.0) * 0.01, 2);
-   else if(balance <= 50000.0)
-   {
-      double baseLot = 0.40;
-      double extraLot = NormalizeDouble(MathFloor((balance - 20000.0) / 750.0) * 0.01, 2);
-      lot = baseLot + extraLot;
-   }
-   else
-   {
-      double baseLot = 0.80;
-      double extraLot = NormalizeDouble(MathFloor((balance - 50000.0) / 1500.0) * 0.01, 2);
-      lot = baseLot + extraLot;
-   }
+   double lot = BaseLotByBalance(balance);
    lot = NormalizeDouble(lot * RangeBounce_LotMult, 2);
    if(lot < 0.01) lot = 0.01;
    if(lot > BT_MaxLotCap) lot = BT_MaxLotCap;
@@ -921,7 +943,7 @@
 
    //--- Place order
    string dir = doBuy ? "BUY" : "SELL";
-   string comment = StringFormat("IF8V3G_RB %s R:$%.0f", dir, rangeSize);
+   string comment = StringFormat("IF8V5Q_RB %s R:$%.0f", dir, rangeSize);
 
    if(doBuy)
       gs_trade.Buy(lot, _Symbol, 0, sl, tp, comment);
@@ -1027,7 +1049,7 @@
       score = profit * MathMin(pf, 3.0) * MathMax(recovery, 0.1) / (1.0 + equityDdPct + (balanceDdPct * 0.5));
 
    int handle = FileOpen(
-      "InvictusForward8_V3Guard_optimization_passes.csv",
+      "InvictusForward8_V4Boost_optimization_passes.csv",
       FILE_COMMON | FILE_CSV | FILE_READ | FILE_WRITE | FILE_SHARE_READ | FILE_SHARE_WRITE,
       ';'
    );
@@ -1038,17 +1060,23 @@
          FileWrite(handle,
                    "score", "profit", "profit_factor", "trades", "equity_dd_pct", "balance_dd_pct", "recovery_factor",
                    "BT_RiskPercent", "BT_CompoundingPer", "BT_MaxLotCap",
-                   "Guard_MaxTrendPosLowBalance",
+                   "Guard_MaxTrendPosLowBalance", "Trend_LotMult", "Trend_RRStandard", "Trend_RRStrong", "Trend_RRTop",
                    "RangeBounce_LotMult", "RangeBounce_MaxBuy", "RangeBounce_MaxSell", "RangeBounce_MaxEntriesPerRange",
-                   "DropCatcher_LotMult");
+                   "DropCatcher_LotMult",
+                   "V5_TrendScore85LotMult", "V5_TrendScore90LotMult", "V5_TrendScore95LotMult",
+                   "V5_TrendHour09LotMult", "V5_TrendHour12LotMult", "V5_TrendHour15LotMult",
+                   "V5_BlockScore85Hour09", "V5_BlockScore90Hour12", "V5_BlockScore85Hour15");
       }
       FileSeek(handle, 0, SEEK_END);
       FileWrite(handle,
                 score, profit, pf, trades, equityDdPct, balanceDdPct, recovery,
                 BT_RiskPercent, BT_CompoundingPer, BT_MaxLotCap,
-                Guard_MaxTrendPosLowBalance,
+                Guard_MaxTrendPosLowBalance, Trend_LotMult, Trend_RRStandard, Trend_RRStrong, Trend_RRTop,
                 RangeBounce_LotMult, RangeBounce_MaxBuy, RangeBounce_MaxSell, RangeBounce_MaxEntriesPerRange,
-                DropCatcher_LotMult);
+                DropCatcher_LotMult,
+                V5_TrendScore85LotMult, V5_TrendScore90LotMult, V5_TrendScore95LotMult,
+                V5_TrendHour09LotMult, V5_TrendHour12LotMult, V5_TrendHour15LotMult,
+                V5_BlockScore85Hour09, V5_BlockScore90Hour12, V5_BlockScore85Hour15);
       FileClose(handle);
    }
 
```
