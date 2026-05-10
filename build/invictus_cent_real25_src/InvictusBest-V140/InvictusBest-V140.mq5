//+------------------------------------------------------------------+
//|                                           InvictusHelperBT.mq5   |
//|            Backtest wrapper — reads InvictusHelper detection      |
//|            logic and places real trades in Strategy Tester        |
//+------------------------------------------------------------------+
#property copyright   "Invictus Trading System"
#property version     "1.10"
#property description "Backtest EA for InvictusHelper signals"
#property description "Uses same detection modules as InvictusHelper indicator"
#property description "Includes Sideways Range Bounce (ADX H1 < 20)"

#include <Trade\Trade.mqh>

//--- Reuse InvictusHelper detection modules (relative path to Indicators folder)
#include "..\..\Indicators\InvictusHelper\Modules\IH_Config.mqh"
#include "..\..\Indicators\InvictusHelper\Modules\IH_Detector.mqh"

//--- EA-specific inputs
input group "══════ Trade Settings ══════"
input double   BT_RiskPercent       = 3.0;      // Risk % per trade
input bool     BT_UseFixedLot       = false;     // Use fixed lot size
input double   BT_FixedLot          = 0.01;      // Fixed lot size
input double   BT_CompoundingPer    = 500.0;     // Balance per 0.01 lot
input int      BT_MaxDailyWins      = 3;         // Max wins per day (KillSwitch)

//=== Magic Numbers ===
#define EA_MAGIC_BT       202604100    // Trending (SMC Breakout)
#define EA_MAGIC_SIDEWAYS  202604200    // Sideways (Range Bounce)

//--- Module instances
CIH_Detector   g_detector;
CTrade         g_trade;
CTrade         gs_trade;   // Sideways trade object

//============================================================
//  TRENDING STATE (prefix g_)
//============================================================
datetime       g_lastBarTime = 0;
int            g_dailyWins   = 0;
int            g_currentDay  = -1;
datetime       g_lastSLTime  = 0;
bool           g_dirBlocked  = false;
bool           g_lastSLWasBuy = false;

//--- Zone cooldown (matches SignalEngine)
double         g_lastZonePrice = 0;
datetime       g_lastZoneTime  = 0;

//--- Consecutive loss protection
int            g_consLosses    = 0;
double         g_dailyLossUSD  = 0;
double         g_dayStartBal   = 0;

//============================================================
//  SIDEWAYS STATE (prefix gs_)
//============================================================
int            gs_adxHandle   = INVALID_HANDLE;
int            gs_atrHandle   = INVALID_HANDLE;
datetime       gs_lastBarTime = 0;
int            gs_consLosses  = 0;
double         gs_dailyLossUSD = 0;
double         gs_dayStartBal  = 0;
int            gs_dailyWins    = 0;
datetime       gs_lastSLTime   = 0;
//--- Shared ADX value (read once in OnTick, used by both strategies)
double         g_adxH4Value   = 25.0;
//--- Cluster protection: max 2 entries per range per day
double         gs_lastRangeHigh = 0;
double         gs_lastRangeLow  = 0;
int            gs_rangeEntries  = 0;

//+------------------------------------------------------------------+
int OnInit()
{
   //--- Initialize TF-dependent parameters
   IH_InitParams();

   if(StringFind(_Symbol, "XAUUSD") < 0 && StringFind(_Symbol, "GOLD") < 0)
      Print("[BT] WARNING: Designed for XAUUSD. Current: ", _Symbol);

   if(!g_detector.Init(_Symbol))
   {
      Print("[BT] FATAL: Detector init failed");
      return INIT_FAILED;
   }

   //--- Trending trade object
   g_trade.SetExpertMagicNumber(EA_MAGIC_BT);
   g_trade.SetDeviationInPoints(50);

   //--- Sideways trade object
   gs_trade.SetExpertMagicNumber(EA_MAGIC_SIDEWAYS);
   gs_trade.SetDeviationInPoints(50);

   //--- ADX(14) on H4 for regime detection (H4 more stable than H1)
   gs_adxHandle = iADX(_Symbol, PERIOD_H4, 14);
   if(gs_adxHandle == INVALID_HANDLE)
      Print("[BT] WARNING: Could not create ADX H4 handle");

   //--- ATR(14) on M15 for sideways SL buffer
   gs_atrHandle = iATR(_Symbol, _Period, 14);
   if(gs_atrHandle == INVALID_HANDLE)
      Print("[BT] WARNING: Could not create ATR M15 handle");

   //--- Load InvictusHelper indicator on chart (visual overlay)
   int ihHandle = iCustom(_Symbol, _Period, "InvictusHelper\\InvictusHelper");
   if(ihHandle != INVALID_HANDLE)
   {
      ChartIndicatorAdd(0, 0, ihHandle);
      Print("[BT] InvictusHelper indicator loaded on chart");
   }
   else
      Print("[BT] WARNING: Could not load InvictusHelper indicator");

   Print("[BT] InvictusHelperBT v1.10 initialized — Trending + Sideways ready");
   return INIT_SUCCEEDED;
}

//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
   g_detector.Deinit();

   if(gs_adxHandle != INVALID_HANDLE)  IndicatorRelease(gs_adxHandle);
   if(gs_atrHandle != INVALID_HANDLE)  IndicatorRelease(gs_atrHandle);

   Print("[BT] Deinitialized — reason: ", reason);
}

//+------------------------------------------------------------------+
void OnTick()
{
   //--- New bar check (M15)
   datetime barTime[];
   if(CopyTime(_Symbol, _Period, 0, 1, barTime) <= 0) return;

   //--- Daily reset (shared)
   MqlDateTime dt;
   TimeToStruct(barTime[0], dt);

   bool newDay = (dt.day_of_year != g_currentDay);
   if(newDay)
   {
      g_currentDay = dt.day_of_year;

      //--- Trending daily reset
      g_dailyWins = 0;
      g_dirBlocked = false;
      g_consLosses = 0;
      g_dailyLossUSD = 0;
      g_dayStartBal = AccountInfoDouble(ACCOUNT_BALANCE);

      //--- Sideways daily reset
      gs_dailyWins = 0;
      gs_consLosses = 0;
      gs_dailyLossUSD = 0;
      gs_dayStartBal = AccountInfoDouble(ACCOUNT_BALANCE);
      gs_rangeEntries = 0;
      gs_lastRangeHigh = 0;
      gs_lastRangeLow = 0;
   }

   //--- Weekend filter (shared)
   if(dt.day_of_week == 0 || dt.day_of_week == 6) return;
   if(dt.day_of_week == 5 && dt.hour >= 15) return;

   //--- Read ADX H4 once (shared by both strategies)
   g_adxH4Value = 25.0;
   if(gs_adxHandle != INVALID_HANDLE)
   {
      double adxBuf[];
      if(CopyBuffer(gs_adxHandle, 0, 0, 1, adxBuf) > 0)
         g_adxH4Value = adxBuf[0];
   }

   //--- TRENDING: SELALU jalan setiap bar
   if(barTime[0] != g_lastBarTime)
   {
      g_lastBarTime = barTime[0];
      ProcessTrending(barTime[0], dt);
   }

   //--- SIDEWAYS: TAMBAHAN saat ADX H4 < 20
   if(barTime[0] != gs_lastBarTime && g_adxH4Value < 20.0)
   {
      gs_lastBarTime = barTime[0];
      ProcessSideways(barTime[0], dt);
   }
}

//+------------------------------------------------------------------+
//  TRENDING LOGIC — 100% sama dengan V1.20 (tidak diubah)
//+------------------------------------------------------------------+
void ProcessTrending(datetime barTime, MqlDateTime &dt)
{
   //--- KillSwitch (M15=20 wins, H4=user setting)
   int maxW = (_Period <= PERIOD_M15) ? 20 : BT_MaxDailyWins;
   if(g_dailyWins >= maxW) return;

   //--- Daily loss limit: stop trading if daily loss > 5% of day-start balance
   if(g_dayStartBal > 0 && g_dailyLossUSD > g_dayStartBal * 0.05) return;

   //--- Toxic hours filter (M15: jam 03 dan 17 WR < 27%)
   if(_Period <= PERIOD_M15)
   {
      if(dt.hour == 3 || dt.hour == 17) return;
   }

   //--- Session check (dynamic bar duration)
   //    Disabled for M15 scalping
   if(_Period > PERIOD_M15 && IH_FilterSessions)
   {
      int bH = dt.hour;
      int bDur = MathMax(1, PeriodSeconds(_Period) / 3600);
      int bEnd = bH + bDur;
      bool inSession = false;
      if(bH < IH_AsiaEnd   && bEnd > IH_AsiaStart)   inSession = true;
      if(bH < IH_LondonEnd && bEnd > IH_LondonStart) inSession = true;
      if(bH < IH_NYEnd     && bEnd > IH_NYStart)      inSession = true;
      if(!inSession) return;
   }

   //--- Load price data
   int need = IH_MaxBOSBarsBack + IH_SwingLookback + 60;
   double open[], high[], low[], close[];
   datetime time[];
   if(CopyOpen(_Symbol, _Period, 0, need, open)   < need) return;
   if(CopyHigh(_Symbol, _Period, 0, need, high)   < need) return;
   if(CopyLow(_Symbol, _Period, 0, need, low)     < need) return;
   if(CopyClose(_Symbol, _Period, 0, need, close) < need) return;
   if(CopyTime(_Symbol, _Period, 0, need, time)   < need) return;
   ArraySetAsSeries(open, true);
   ArraySetAsSeries(high, true);
   ArraySetAsSeries(low, true);
   ArraySetAsSeries(close, true);
   ArraySetAsSeries(time, true);

   int refBar = 1; // just-completed bar
   int totalBars = need;

   //--- After-loss cooldown (time-based: 2 bars * bar duration)
   if(g_lastSLTime > 0)
   {
      int cooldown = 2 * PeriodSeconds(_Period);
      if((int)(TimeCurrent() - g_lastSLTime) < cooldown)
         return;
   }

   //--- Bias
   ENUM_IH_BIAS bias = g_detector.DetectBias(refBar, high, low, close, totalBars);
   bool isBuy = (bias == IH_BIAS_BULLISH || bias == IH_BIAS_NEUTRAL);

   //--- SELL ultra-strict filter: data shows SELL only profitable at specific hours
   //    Hour 7 (WR 60%), 10 (WR 80%), 22 (WR 100%) — all others = disaster
   //    BOS must be Impulsive (already filtered by detector for SELL bias)
   if(!isBuy)
   {
      if(dt.hour != 7 && dt.hour != 10 && dt.hour != 22) return;
   }

   //--- Same-dir block (disabled for M15 scalping)
   if(_Period > PERIOD_M15 && g_dirBlocked && isBuy == g_lastSLWasBuy) return;

   //--- BOS
   IH_BOSInfo bos = g_detector.AnalyzeBOS(refBar, isBuy, open, high, low, close, totalBars);
   if(bos.quality == IH_BOS_NONE) return;

   //--- Zone
   IH_Zone zone;
   if(!g_detector.DetectZone(refBar, isBuy, open, high, low, close, time, totalBars, zone))
      return;

   //--- Zone cooldown: skip if same zone attempted recently (matches SignalEngine)
   double zoneTolerance = 1.0;  // $1 tolerance
   if(g_lastZonePrice > 0 && MathAbs(zone.entryPrice - g_lastZonePrice) < zoneTolerance)
   {
      int cooldownSec = 2 * PeriodSeconds(_Period);
      if((int)(time[refBar] - g_lastZoneTime) < cooldownSec)
         return;
   }

   //--- Scoring
   int score = 40; // Zone always +40

   //--- Volatility +15
   double atr14 = g_detector.GetATR(refBar);
   if(atr14 > 0)
   {
      double sum = 0; int cnt = 0;
      for(int i = refBar; i < refBar + 50 && i < totalBars; i++)
      {
         double v = g_detector.GetATR(i);
         if(v > 0) { sum += v; cnt++; }
      }
      if(cnt > 20 && atr14 < 1.3 * (sum / cnt)) score += 15;
   }

   //--- BOS Bonus +25 max
   if(bos.hasFVG)    score += 10;
   if(bos.hasRetest) score += 10;
   if(bos.hasSweep)  score += 5;

   //--- Trend +20
   if(refBar + 11 < totalBars)
   {
      if(isBuy)
      {
         int hh = 0;
         for(int k = refBar + 1; k < refBar + 10 && k + 1 < totalBars; k++)
            if(high[k] > high[k + 1]) hh++;
         if(hh >= 5) score += 20;
      }
      else
      {
         int ll = 0;
         for(int k = refBar + 1; k < refBar + 10 && k + 1 < totalBars; k++)
            if(low[k] < low[k + 1]) ll++;
         if(ll >= 5) score += 20;
      }
   }

   //--- Gold buy bonus +10
   if(isBuy && IH_GoldBuyBonus > 0) score += IH_GoldBuyBonus;

   //--- SELL: require BOS Impulsive + score 10 poin lebih tinggi
   if(!isBuy)
   {
      if(bos.quality != IH_BOS_IMPULSIVE) return;
      if(score < IH_MinScoreA + 10) return;
   }

   //--- Grade check
   if(score < IH_MinScoreA) return;

   //--- Max positions check (tier-based)
   double bal = AccountInfoDouble(ACCOUNT_BALANCE);
   int maxPos = (bal <= 20000.0) ? 8 : (bal <= 50000.0) ? 4 : 3;
   int openPos = CountPositions(EA_MAGIC_BT);
   if(openPos >= maxPos) return;

   //--- Calculate SL/TP
   double atr = g_detector.GetATR(refBar);
   double buffer = atr * IH_ATRBufferSL;

   double entryPrice = NormalizeDouble(zone.entryPrice, 2);
   double sl, tp;

   //--- Dynamic RR based on score (strong setup = bigger TP)
   double rr = (score >= 95) ? 2.0 : IH_TP1_RR;

   if(isBuy)
   {
      sl = zone.priceLow - buffer;
      double dist = entryPrice - sl;
      if(dist < IH_MinSLDollar) sl = entryPrice - IH_MinSLDollar;
      if(dist > IH_MaxSLDollar) sl = entryPrice - IH_MaxSLDollar;
      dist = entryPrice - sl;
      tp = entryPrice + dist * rr;
   }
   else
   {
      sl = zone.priceHigh + buffer;
      double dist = sl - entryPrice;
      if(dist < IH_MinSLDollar) sl = entryPrice + IH_MinSLDollar;
      if(dist > IH_MaxSLDollar) sl = entryPrice + IH_MaxSLDollar;
      dist = sl - entryPrice;
      tp = entryPrice - dist * rr;
   }

   sl = NormalizeDouble(sl, 2);
   tp = NormalizeDouble(tp, 2);

   //--- Lot sizing (compounding 3-tier, aggressive at mid-high balance)
   //    Tier 1: 0-20k  = $500/0.01 (safe growth phase)
   //    Tier 2: 20-50k = $750/0.01 (accelerate — edge proven by now)
   //    Tier 3: 50k+   = $1500/0.01 (aggressive — BUY-only = higher WR)
   double balance = AccountInfoDouble(ACCOUNT_BALANCE);
   double lot;
   if(balance <= 20000.0)
      lot = NormalizeDouble(MathFloor(balance / 500.0) * 0.01, 2);
   else if(balance <= 50000.0)
   {
      double baseLot = 0.40;
      double extraLot = NormalizeDouble(MathFloor((balance - 20000.0) / 750.0) * 0.01, 2);
      lot = baseLot + extraLot;
   }
   else
   {
      double baseLot = 0.80;  // 0.40 + 0.40 at $50k
      double extraLot = NormalizeDouble(MathFloor((balance - 50000.0) / 1500.0) * 0.01, 2);
      lot = baseLot + extraLot;
   }
   if(lot < 0.01) lot = 0.01;

   //--- Progressive lot reduction on consecutive losses
   if(g_consLosses >= 7)
      lot = NormalizeDouble(lot * 0.10, 2);
   else if(g_consLosses >= 5)
      lot = NormalizeDouble(lot * 0.25, 2);
   else if(g_consLosses >= 3)
      lot = NormalizeDouble(lot * 0.50, 2);
   if(lot < 0.01) lot = 0.01;

   //--- Update zone cooldown tracking
   g_lastZonePrice = entryPrice;
   g_lastZoneTime  = time[refBar];

   //--- Expiry: PendingExpiryBars * bar duration
   datetime expiry = TimeCurrent() + IH_PendingExpiryBars * PeriodSeconds(_Period);

   //--- SELL lot reduction: 50% of normal (lower conviction)
   if(!isBuy)
      lot = NormalizeDouble(lot * 0.50, 2);
   if(lot < 0.01) lot = 0.01;

   //--- Place order
   double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   string comment = StringFormat("IHB S:%d %s", score,
                                  bos.quality == IH_BOS_IMPULSIVE ? "IMP" : "COR");

   if(isBuy)
   {
      if(ask <= entryPrice)
         g_trade.Buy(lot, _Symbol, 0, sl, tp, comment);
      else
         g_trade.BuyLimit(lot, entryPrice, _Symbol, sl, tp,
                          ORDER_TIME_SPECIFIED, expiry, comment);
   }
   else
   {
      if(bid >= entryPrice)
         g_trade.Sell(lot, _Symbol, 0, sl, tp, comment);
      else
         g_trade.SellLimit(lot, entryPrice, _Symbol, sl, tp,
                           ORDER_TIME_SPECIFIED, expiry, comment);
   }

   Print("[BT] ", isBuy ? "BUY" : "SELL", " @ ", entryPrice,
         " SL:", sl, " TP:", tp, " Score:", score,
         " BOS:", bos.quality == IH_BOS_IMPULSIVE ? "Imp" : "Cor");
}

//+------------------------------------------------------------------+
//  SIDEWAYS LOGIC — Range Bounce BUY-only (runs ADDITIONALLY when ADX H4 < 20)
//  Trending tetap jalan, sideways = bonus. Cluster max 2/range/day.
//+------------------------------------------------------------------+
void ProcessSideways(datetime barTime, MqlDateTime &dt)
{
   //--- KillSwitch sideways: max 10 wins/day
   if(gs_dailyWins >= 10) return;

   //--- Daily loss limit: 3%
   if(gs_dayStartBal > 0 && gs_dailyLossUSD > gs_dayStartBal * 0.03) return;

   //--- Toxic hours: data-driven (WR 0-14% at these hours)
   if(dt.hour == 3 || dt.hour == 19) return;

   //--- After-loss cooldown: 2 bars M15 (30 min)
   if(gs_lastSLTime > 0)
   {
      int cooldown = 2 * PeriodSeconds(_Period);
      if((int)(TimeCurrent() - gs_lastSLTime) < cooldown)
         return;
   }

   //--- Max sideways positions: 4
   int openPos = CountPositions(EA_MAGIC_SIDEWAYS);
   if(openPos >= 4) return;

   //--- Load 48 bars M15 for range calculation
   double high[], low[], close[];
   datetime time[];
   if(CopyHigh(_Symbol, _Period, 0, 49, high)   < 49) return;
   if(CopyLow(_Symbol, _Period, 0, 49, low)     < 49) return;
   if(CopyClose(_Symbol, _Period, 0, 49, close) < 49) return;
   if(CopyTime(_Symbol, _Period, 0, 49, time)   < 49) return;
   ArraySetAsSeries(high, true);
   ArraySetAsSeries(low, true);
   ArraySetAsSeries(close, true);
   ArraySetAsSeries(time, true);

   //--- Calculate range from bar 1..48 (skip current bar 0)
   double rangeHigh = high[1];
   double rangeLow  = low[1];
   for(int i = 2; i <= 48; i++)
   {
      if(high[i] > rangeHigh) rangeHigh = high[i];
      if(low[i]  < rangeLow)  rangeLow  = low[i];
   }
   double rangeSize = rangeHigh - rangeLow;

   //--- Validate range: min $15, max via ATR
   if(rangeSize < 15.0) return;

   //--- ATR for range max validation
   double atrVal = 0;
   if(gs_atrHandle != INVALID_HANDLE)
   {
      double atrBuf[];
      if(CopyBuffer(gs_atrHandle, 0, 0, 1, atrBuf) > 0)
         atrVal = atrBuf[0];
   }
   //--- Range too large = probably trending, not sideways
   if(atrVal > 0 && rangeSize > atrVal * 10) return;

   //--- Entry zone: lower 25% of range (same as V1 yang profit)
   double curClose = close[1];
   double buyZoneTop = rangeLow + rangeSize * 0.25;
   double midRange   = rangeLow + rangeSize * 0.50;

   //--- BUY only
   if(curClose > buyZoneTop) return;

   //--- Cluster protection: max 2 entries per range per day
   //    Same range = rangeHigh/Low within $5 of last entry's range
   bool sameRange = (MathAbs(rangeHigh - gs_lastRangeHigh) < 5.0 &&
                     MathAbs(rangeLow - gs_lastRangeLow) < 5.0);
   if(sameRange && gs_rangeEntries >= 2) return;

   //--- Calculate SL/TP (V1 style: TP at mid-range = high probability)
   double slBuffer = (atrVal > 0) ? atrVal * 0.5 : 3.0;
   double entryPrice = curClose;
   double sl = rangeLow - slBuffer;
   double tp = midRange;   // TP at 50% — proven profitable in V1

   //--- SL clamp: min $5, max $20
   double slDist = entryPrice - sl;
   if(slDist < 5.0)  sl = entryPrice - 5.0;
   if(slDist > 20.0) sl = entryPrice - 20.0;

   entryPrice = NormalizeDouble(entryPrice, 2);
   sl = NormalizeDouble(sl, 2);
   tp = NormalizeDouble(tp, 2);

   //--- Lot sizing: 25% of compounding (conservative sideways)
   double balance = AccountInfoDouble(ACCOUNT_BALANCE);
   double lot;
   if(balance <= 20000.0)
      lot = NormalizeDouble(MathFloor(balance / 500.0) * 0.01, 2);
   else if(balance <= 50000.0)
   {
      double baseLot = 0.40;
      double extraLot = NormalizeDouble(MathFloor((balance - 20000.0) / 750.0) * 0.01, 2);
      lot = baseLot + extraLot;
   }
   else
   {
      double baseLot = 0.80;
      double extraLot = NormalizeDouble(MathFloor((balance - 50000.0) / 1500.0) * 0.01, 2);
      lot = baseLot + extraLot;
   }
   lot = NormalizeDouble(lot * 0.25, 2);  // 25% of normal
   if(lot < 0.01) lot = 0.01;

   //--- Progressive lot reduction (sideways own counter)
   if(gs_consLosses >= 7)
      lot = NormalizeDouble(lot * 0.10, 2);
   else if(gs_consLosses >= 5)
      lot = NormalizeDouble(lot * 0.25, 2);
   else if(gs_consLosses >= 3)
      lot = NormalizeDouble(lot * 0.50, 2);
   if(lot < 0.01) lot = 0.01;

   //--- Update cluster tracking
   if(!sameRange)
   {
      gs_lastRangeHigh = rangeHigh;
      gs_lastRangeLow  = rangeLow;
      gs_rangeEntries  = 0;
   }
   gs_rangeEntries++;

   //--- Place market BUY order
   string comment = StringFormat("IHS RB R:$%.0f", rangeSize);
   gs_trade.Buy(lot, _Symbol, 0, sl, tp, comment);

   Print("[BT-SW] BUY @ ", entryPrice,
         " SL:", sl, " TP:", tp, " Range:$", rangeSize,
         " Cluster:", gs_rangeEntries, "/2 | Lot:", lot);
}

//+------------------------------------------------------------------+
void OnTradeTransaction(const MqlTradeTransaction &trans,
                         const MqlTradeRequest &request,
                         const MqlTradeResult &result)
{
   if(trans.type == TRADE_TRANSACTION_DEAL_ADD && trans.deal > 0)
   {
      if(HistoryDealSelect(trans.deal))
      {
         long magic = HistoryDealGetInteger(trans.deal, DEAL_MAGIC);
         long dealEntry = HistoryDealGetInteger(trans.deal, DEAL_ENTRY);

         if(dealEntry == DEAL_ENTRY_OUT)
         {
            double profit = HistoryDealGetDouble(trans.deal, DEAL_PROFIT) +
                            HistoryDealGetDouble(trans.deal, DEAL_COMMISSION) +
                            HistoryDealGetDouble(trans.deal, DEAL_SWAP);

            //--- Route to correct state based on magic number
            if(magic == EA_MAGIC_BT)
            {
               //--- TRENDING state
               if(profit > 0)
               {
                  g_dailyWins++;
                  g_dirBlocked = false;
                  g_consLosses = 0;
               }
               else
               {
                  long dealType = HistoryDealGetInteger(trans.deal, DEAL_TYPE);
                  g_lastSLWasBuy = (dealType == DEAL_TYPE_SELL);
                  g_dirBlocked = true;
                  g_lastSLTime = TimeCurrent();
                  g_consLosses++;
                  g_dailyLossUSD += MathAbs(profit);
               }
            }
            else if(magic == EA_MAGIC_SIDEWAYS)
            {
               //--- SIDEWAYS state
               if(profit > 0)
               {
                  gs_dailyWins++;
                  gs_consLosses = 0;
               }
               else
               {
                  gs_lastSLTime = TimeCurrent();
                  gs_consLosses++;
                  gs_dailyLossUSD += MathAbs(profit);
               }
            }
         }
      }
   }
}

//+------------------------------------------------------------------+
int CountPositions(long magicNumber)
{
   int count = 0;
   for(int i = 0; i < PositionsTotal(); i++)
   {
      if(PositionGetTicket(i) > 0 &&
         PositionGetInteger(POSITION_MAGIC) == magicNumber)
         count++;
   }
   return count;
}
//+------------------------------------------------------------------+
