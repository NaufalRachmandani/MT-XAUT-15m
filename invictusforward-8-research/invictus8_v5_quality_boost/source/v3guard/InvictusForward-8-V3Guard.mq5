//+------------------------------------------------------------------+
//|                            InvictusForward-8-V3Guard.mq5       |
//|                           Invictus Trading System                |
//|            M15 Scalping EA — SMC Breakout + Sideways Bounce      |
//+------------------------------------------------------------------+
#property copyright   "Invictus Trading System"
#property version     "3.00"
#property description "M15 Scalping EA — Trending (SMC Breakout) + Sideways (Range Bounce)"
#property description "XAUUSD optimized | ADX H4 regime detection"

#include <Trade\Trade.mqh>

//--- Local modules
#include "IH_Config.mqh"
#include "IH_Detector.mqh"
#include "IH_Logger.mqh"

//--- EA-specific inputs
input group "══════ Trade Settings ══════"
input double   BT_RiskPercent       = 1.0;      // Risk % per trade
input bool     BT_UseFixedLot       = false;     // Use fixed lot size
input double   BT_FixedLot          = 0.01;      // Fixed lot size
input double   BT_CompoundingPer    = 1000.0;    // Balance per 0.01 lot
input double   BT_MaxLotCap         = 0.25;      // Absolute max lot size
input bool     BT_EnableTrending    = true;       // Enable trending SMC breakout
input bool     BT_EnableSideways    = true;       // Enable sideways range bounce
input double   BT_MinSLDollar       = 25.0;      // Min SL distance ($)
input double   BT_MaxSLDollar       = 25.0;      // Max SL distance ($)

//=== Magic Numbers ===
#define EA_MAGIC_BT       202604100    // Trending (SMC Breakout)
#define EA_MAGIC_SIDEWAYS  202604200    // Sideways (Range Bounce)
#define EA_MAGIC_DC        202604300    // Drop Catcher (SELL)

//--- Module instances
CIH_Detector   g_detector;
CTrade         g_trade;
CTrade         gs_trade;   // Sideways trade object
CTrade         gdc_trade;  // Drop Catcher trade object

//============================================================
//  TRENDING STATE (prefix g_)
//============================================================
datetime       g_lastBarTime = 0;
int            g_dailyWins   = 0;
int            g_currentDay  = -1;
datetime       g_lastSLTime  = 0;

//--- Zone cooldown (matches SignalEngine)
double         g_lastZonePrice = 0;
datetime       g_lastZoneTime  = 0;

//--- Consecutive loss protection
int            g_consLosses    = 0;
double         g_dailyLossUSD  = 0;
int            g_dailyLossCount = 0;
double         g_dayStartBal   = 0;

//============================================================
//  SIDEWAYS STATE (prefix gs_)
//============================================================
int            gs_adxHandle   = INVALID_HANDLE;
int            gs_atrHandle   = INVALID_HANDLE;
int            gs_consLosses  = 0;
double         gs_dailyLossUSD = 0;
int            gs_dailyLossCount = 0;
double         gs_dayStartBal  = 0;
int            gs_dailyWins    = 0;
datetime       gs_lastSLTime   = 0;
//--- Shared ADX value (read once in OnTick, used by both strategies)
double         g_adxH4Value   = 25.0;
//--- H4 EMA-50 handle for reversal close
int            g_emaH4Handle  = INVALID_HANDLE;
//--- Sideways detection handles (Iter 3)
int            g_bbHandle     = INVALID_HANDLE;
int            g_adxH1Handle  = INVALID_HANDLE;
//--- Cluster protection: max 2 entries per range per day
double         gs_lastRangeHigh = 0;
double         gs_lastRangeLow  = 0;
int            gs_rangeEntries  = 0;

//+------------------------------------------------------------------+
//  Research guardrails
//+------------------------------------------------------------------+
bool GuardBadHour(int hour)
{
   if(!Guard_EnableBadHourFilter) return false;
   if(hour == 4  && Guard_BlockHour04) return true;
   if(hour == 5  && Guard_BlockHour05) return true;
   if(hour == 10 && Guard_BlockHour10) return true;
   if(hour == 11 && Guard_BlockHour11) return true;
   return false;
}

bool GuardDropCatcherHour(int hour)
{
   if(!Guard_EnableDropCatcherHourFilter) return false;
   if(hour == 0  && Guard_DC_BlockHour00) return true;
   if(hour == 1  && Guard_DC_BlockHour01) return true;
   if(hour == 10 && Guard_DC_BlockHour10) return true;
   if(hour == 23 && Guard_DC_BlockHour23) return true;
   return false;
}

bool GuardTrendFillHour(int hour)
{
   if(!Guard_EnableTrendFillHourFilter) return false;
   if(hour == 0  && Guard_TR_BlockHour00) return true;
   if(hour == 1  && Guard_TR_BlockHour01) return true;
   if(hour == 4  && Guard_TR_BlockHour04) return true;
   if(hour == 5  && Guard_TR_BlockHour05) return true;
   if(hour == 10 && Guard_TR_BlockHour10) return true;
   if(hour == 11 && Guard_TR_BlockHour11) return true;
   if(hour == 19 && Guard_TR_BlockHour19) return true;
   if(hour == 20 && Guard_TR_BlockHour20) return true;
   if(hour == 22 && Guard_TR_BlockHour22) return true;
   if(hour == 23 && Guard_TR_BlockHour23) return true;
   return false;
}

int GuardMaxTrendPositions(double balance)
{
   if(balance <= 20000.0) return MathMax(1, Guard_MaxTrendPosLowBalance);
   if(balance <= 50000.0) return MathMax(1, Guard_MaxTrendPosMidBalance);
   return MathMax(1, Guard_MaxTrendPosHighBalance);
}

//--- Trade management module (uses globals declared above)
#include "IH_TradeManager.mqh"

//+------------------------------------------------------------------+
int OnInit()
{
   //--- Initialize TF-dependent parameters
   IH_InitParams();
   IH_MinSLDollar = BT_MinSLDollar;
   IH_MaxSLDollar = BT_MaxSLDollar;

   if(StringFind(_Symbol, "XAUUSD") < 0 && StringFind(_Symbol, "GOLD") < 0)
      Print("[BT] WARNING: Designed for XAUUSD. Current: " + _Symbol);

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

   //--- Drop Catcher trade object
   gdc_trade.SetExpertMagicNumber(EA_MAGIC_DC);
   gdc_trade.SetDeviationInPoints(50);

   //--- ADX(14) on H4 for regime detection (H4 more stable than H1)
   gs_adxHandle = iADX(_Symbol, PERIOD_H4, 14);
   if(gs_adxHandle == INVALID_HANDLE)
      Print("[BT] WARNING: Could not create ADX H4 handle");

   //--- ATR(14) on M15 for sideways SL buffer
   gs_atrHandle = iATR(_Symbol, _Period, 14);
   if(gs_atrHandle == INVALID_HANDLE)
      Print("[BT] WARNING: Could not create ATR M15 handle");

   //--- EMA(50) on H4 for reversal close
   g_emaH4Handle = iMA(_Symbol, PERIOD_H4, 50, 0, MODE_EMA, PRICE_CLOSE);
   if(g_emaH4Handle == INVALID_HANDLE)
      Print("[BT] WARNING: Could not create EMA H4 handle");

   //--- Bollinger Bands M15 + ADX H1 for sideways detection (Iter 3)
   g_bbHandle = iBands(_Symbol, _Period, BB_Period, 0, BB_Deviation, PRICE_CLOSE);
   if(g_bbHandle == INVALID_HANDLE)
      Print("[BT] WARNING: Could not create BB handle");
   g_adxH1Handle = iADX(_Symbol, PERIOD_H1, 14);
   if(g_adxH1Handle == INVALID_HANDLE)
      Print("[BT] WARNING: Could not create ADX H1 handle");

   LogOpen();
   LogWrite("[INIT] InvictusForward-8-V3Guard v3.00 M15 — April guard experiment");
   return INIT_SUCCEEDED;
}

//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
   g_detector.Deinit();

   if(gs_adxHandle  != INVALID_HANDLE) IndicatorRelease(gs_adxHandle);
   if(gs_atrHandle  != INVALID_HANDLE) IndicatorRelease(gs_atrHandle);
   if(g_emaH4Handle != INVALID_HANDLE) IndicatorRelease(g_emaH4Handle);
   if(g_bbHandle    != INVALID_HANDLE) IndicatorRelease(g_bbHandle);
   if(g_adxH1Handle != INVALID_HANDLE) IndicatorRelease(g_adxH1Handle);

   LogWrite("[DEINIT] reason: " + IntegerToString(reason));
   LogClose();
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
      g_consLosses = 0;
      g_dailyLossUSD = 0;
      g_dailyLossCount = 0;
      g_dayStartBal = AccountInfoDouble(ACCOUNT_BALANCE);
      g_lastZonePrice = 0;
      g_lastZoneTime  = 0;

      //--- Sideways daily reset
      gs_dailyWins = 0;
      gs_consLosses = 0;
      gs_dailyLossUSD = 0;
      gs_dailyLossCount = 0;
      gs_dayStartBal = AccountInfoDouble(ACCOUNT_BALANCE);
      gs_rangeEntries = 0;
      gs_lastRangeHigh = 0;
      gs_lastRangeLow = 0;
   }

   //--- Read ADX H4 once (shared by both strategies)
   g_adxH4Value = 25.0;
   if(gs_adxHandle != INVALID_HANDLE)
   {
      double adxBuf[];
      if(CopyBuffer(gs_adxHandle, 0, 0, 1, adxBuf) > 0)
         g_adxH4Value = adxBuf[0];
   }

   //--- Cancel pending orders jika bias berubah
   ManagePendingOrders();

   //--- Trailing stop — geser SL saat profit bertahap
   ManageTrailing();

   //--- Close profit positions open > 5 hours
   CheckTimedProfitClose();

   //--- Weekend + Friday afternoon: manage existing but no new entries
   if(dt.day_of_week == 0 || dt.day_of_week == 6) return;
   if(dt.day_of_week == 5 && dt.hour >= 15) return;

   //--- TRENDING: SELALU jalan setiap bar
   if(barTime[0] != g_lastBarTime)
   {
      g_lastBarTime = barTime[0];

      int swScore = DetectSidewaysAdvanced();
      bool isSideways = (swScore >= SidewaysMinMethods);

      CheckDropCatcher();
      CheckReversalClose();
      if(BT_EnableTrending)
         ProcessTrending(barTime[0], dt, isSideways);
      ManageTPSwap();

      //--- SIDEWAYS: range bounce when confirmed sideways (Iter 5)
      if(BT_EnableSideways && isSideways)
         ProcessSideways(barTime[0], dt);
   }
}

//+------------------------------------------------------------------+
//  Drop Catcher SELL (Iter 4)
//  Tangkap sharp gold drops: body > 1.8×ATR, volume spike,
//  swing low break, H4 ADX < 35, bukan toxic hours.
//  RR 4:1, lot 70%, tight SL 1.2×ATR.
//+------------------------------------------------------------------+
void CheckDropCatcher()
{
   if(!EnableDropCatcher) return;
   if(CountPositions(EA_MAGIC_DC) >= 1) return;

   int refBar = 1;
   double open1  = iOpen(_Symbol, _Period, refBar);
   double close1 = iClose(_Symbol, _Period, refBar);
   double atr    = g_detector.GetATR(refBar);
   if(atr <= 0) return;

   if(atr > DropCatcher_MaxATR) return;

   double body = MathAbs(close1 - open1);
   if(close1 >= open1 || body < atr * DropCatcher_BodyATR) return;
   if(body < DropCatcher_MinBodyDlr) return;

   long vol1 = iTickVolume(_Symbol, _Period, refBar);
   long volAvg = 0;
   for(int i = refBar+1; i <= refBar+20; i++) volAvg += iTickVolume(_Symbol, _Period, i);
   volAvg /= 20;
   if(volAvg > 0 && vol1 < (long)(volAvg * DropCatcher_VolMult)) return;

   int swLowBar = iLowest(_Symbol, _Period, MODE_LOW, 10, refBar+1);
   double swingLow = iLow(_Symbol, _Period, swLowBar);
   if(close1 >= swingLow) return;

   if(g_adxH4Value > 35.0) return;

   MqlDateTime dcDt;
   TimeToStruct(iTime(_Symbol, _Period, refBar), dcDt);
   if(dcDt.hour == 3 || dcDt.hour == 17 || dcDt.hour == 19) return;
   if(GuardDropCatcherHour(dcDt.hour)) return;

   double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   double slDist = atr * DropCatcher_SL_ATR;
   double dcSL = NormalizeDouble(bid + slDist, 2);
   double dcTP = NormalizeDouble(bid - (slDist * DropCatcher_RR), 2);

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
   lot = NormalizeDouble(lot * DropCatcher_LotMult, 2);
   if(lot < 0.01) lot = 0.01;
   if(lot > BT_MaxLotCap) lot = BT_MaxLotCap;

   gdc_trade.Sell(lot, _Symbol, 0, dcSL, dcTP, "IF8V3G_DC DropCatch");

   LogWrite("[DC-ORDER] SELL @ " + DoubleToString(bid,2) +
            " SL:" + DoubleToString(dcSL,2) +
            " TP:" + DoubleToString(dcTP,2) +
            " Body:$" + DoubleToString(body,2) +
            " ATR:$" + DoubleToString(atr,2) +
            " Lot:" + DoubleToString(lot,2));
}

//+------------------------------------------------------------------+
//  Advanced Sideways Detection (Iter 3)
//  6 metode, bobot KUAT=2 / standar=1. Max score = 8.
//  Return: weighted score (sideways jika >= SidewaysMinMethods)
//+------------------------------------------------------------------+
int DetectSidewaysAdvanced()
{
   int score = 0;

   // Method 1: ADX H4 < threshold
   if(g_adxH4Value < MTF_H4_ADX_Max) score++;

   // Method 2: BB Squeeze Classic (BB inside Keltner) — bobot KUAT
   if(g_bbHandle != INVALID_HANDLE && gs_atrHandle != INVALID_HANDLE)
   {
      double bbU[], bbL[], bbM[], atrBuf[];
      if(CopyBuffer(g_bbHandle, 1, 1, 1, bbU) > 0 &&
         CopyBuffer(g_bbHandle, 2, 1, 1, bbL) > 0 &&
         CopyBuffer(g_bbHandle, 0, 1, 1, bbM) > 0 &&
         CopyBuffer(gs_atrHandle, 0, 1, 1, atrBuf) > 0)
      {
         double kcU = bbM[0] + atrBuf[0] * KC_ATRMultiplier;
         double kcL = bbM[0] - atrBuf[0] * KC_ATRMultiplier;
         if(bbU[0] < kcU && bbL[0] > kcL) score += 2;
      }
   }

   // Method 3: BB Width Relative (current width < 70% of 50-bar avg)
   if(g_bbHandle != INVALID_HANDLE)
   {
      double bbU50[], bbL50[];
      if(CopyBuffer(g_bbHandle, 1, 1, 50, bbU50) == 50 &&
         CopyBuffer(g_bbHandle, 2, 1, 50, bbL50) == 50)
      {
         double widthNow = bbU50[0] - bbL50[0];
         double widthAvg = 0;
         for(int i = 0; i < 50; i++) widthAvg += (bbU50[i] - bbL50[i]);
         widthAvg /= 50.0;
         if(widthAvg > 0 && widthNow < widthAvg * BBWidth_RelativeRatio) score++;
      }
   }

   // Method 4: ATR Compression (ATR14 < 65% of ATR50 avg)
   double atr14 = g_detector.GetATR(1);
   if(atr14 > 0)
   {
      double atr50sum = 0;
      int cnt = 0;
      for(int i = 1; i <= 50; i++)
      {
         double v = g_detector.GetATR(i);
         if(v > 0) { atr50sum += v; cnt++; }
      }
      if(cnt > 20)
      {
         double atr50avg = atr50sum / cnt;
         if(atr14 < atr50avg * ATR_CompressionRatio) score++;
      }
   }

   // Method 5: MTF Agreement (H1 ADX < 25 AND H4 ADX < 22) — bobot KUAT
   if(g_adxH1Handle != INVALID_HANDLE)
   {
      double adxH1[];
      if(CopyBuffer(g_adxH1Handle, 0, 1, 1, adxH1) > 0)
      {
         if(adxH1[0] < MTF_H1_ADX_Max && g_adxH4Value < MTF_H4_ADX_Max) score += 2;
      }
   }

   // Method 6: Price Range Contained (30-bar range < 2.3 x ATR14)
   if(atr14 > 0)
   {
      double high30[], low30[];
      if(CopyHigh(_Symbol, _Period, 1, 30, high30) == 30 &&
         CopyLow(_Symbol, _Period, 1, 30, low30) == 30)
      {
         double highest = high30[ArrayMaximum(high30)];
         double lowest  = low30[ArrayMinimum(low30)];
         if((highest - lowest) < atr14 * PriceRange_ATRMult) score++;
      }
   }

   return score;
}

//+------------------------------------------------------------------+
//  Smart Reversal Close — tutup BUY trending saat bearish reversal
//  4 kondisi wajib SEMUA terpenuhi:
//  1. Candle bearish kuat: body > 1.5 x ATR
//  2. Close di bawah swing low 10 bar
//  3. H4 EMA-50 slope turun
//  4. Total floating loss BUY > 3% balance
//+------------------------------------------------------------------+
void CheckReversalClose()
{
   if(!EnableReversalClose) return;

   double close1 = iClose(_Symbol, _Period, 1);
   double open1  = iOpen(_Symbol, _Period, 1);
   double atr    = g_detector.GetATR(1);
   if(atr <= 0) return;

   double body = MathAbs(close1 - open1);
   if(close1 >= open1 || body < atr * 1.5) return;

   int swLowBar = iLowest(_Symbol, _Period, MODE_LOW, 10, 2);
   double swLow = iLow(_Symbol, _Period, swLowBar);
   if(close1 >= swLow) return;

   if(g_emaH4Handle == INVALID_HANDLE) return;
   double ema50[];
   if(CopyBuffer(g_emaH4Handle, 0, 0, 4, ema50) < 4) return;
   ArraySetAsSeries(ema50, true);
   if(ema50[0] >= ema50[3]) return;

   double floatingLoss = 0;
   double balance = AccountInfoDouble(ACCOUNT_BALANCE);
   for(int i = 0; i < PositionsTotal(); i++)
   {
      ulong ticket = PositionGetTicket(i);
      if(ticket <= 0) continue;
      if(PositionGetInteger(POSITION_MAGIC) != EA_MAGIC_BT) continue;
      if(PositionGetString(POSITION_SYMBOL) != _Symbol) continue;
      if(PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY)
         floatingLoss += PositionGetDouble(POSITION_PROFIT);
   }
   if(floatingLoss > -balance * 0.03) return;

   LogWrite("[REV-CLOSE] Bearish reversal | Body:$" + DoubleToString(body,2) +
            " ATR:$" + DoubleToString(atr,2) +
            " FloatLoss:$" + DoubleToString(floatingLoss,2));
   for(int i = PositionsTotal()-1; i >= 0; i--)
   {
      ulong ticket = PositionGetTicket(i);
      if(ticket <= 0) continue;
      if(PositionGetInteger(POSITION_MAGIC) != EA_MAGIC_BT) continue;
      if(PositionGetString(POSITION_SYMBOL) != _Symbol) continue;
      if(PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY)
         g_trade.PositionClose(ticket);
   }
}

//+------------------------------------------------------------------+
//  TRENDING LOGIC — SMC Breakout (M15)
//+------------------------------------------------------------------+
void ProcessTrending(datetime barTime, MqlDateTime &dt, bool isSideways)
{
   //--- KillSwitch: max 20 wins/day
   if(g_dailyWins >= 20) { LogWrite("[TR-SKIP] KillSwitch " + IntegerToString(g_dailyWins) + "/20 wins"); return; }

   //--- Daily loss limit: max 5 losses OR 3% of balance (whichever first)
   int maxTrendLosses = (Guard_MaxTrendDailyLossCount > 0) ? Guard_MaxTrendDailyLossCount : 5;
   if(g_dailyLossCount >= maxTrendLosses) { LogWrite("[TR-SKIP] DailyLoss " + IntegerToString(g_dailyLossCount) + "/" + IntegerToString(maxTrendLosses)); return; }
   if(g_dayStartBal > 0)
   {
      double maxDailyLoss = MathMin(g_dayStartBal * 0.03, 15000.0);
      if(g_dailyLossUSD > maxDailyLoss) { LogWrite("[TR-SKIP] DailyLoss $" + DoubleToString(g_dailyLossUSD,2) + " > 3%/$" + DoubleToString(maxDailyLoss,0)); return; }
   }

   //--- Toxic hours filter (H3,H17 original + H1,H2,H14 from backtest data: WR ~50%, net -$97k)
   if(dt.hour == 1 || dt.hour == 2 || dt.hour == 3 || dt.hour == 14 || dt.hour == 17) return;
   if(GuardBadHour(dt.hour)) { LogWrite("[TR-SKIP] GuardBadHour H" + IntegerToString(dt.hour)); return; }
   if(GuardTrendFillHour(dt.hour)) { LogWrite("[TR-SKIP] GuardTrendFillHour H" + IntegerToString(dt.hour)); return; }

   //--- High volatility filter: skip during ATR spikes (news/flash crash)
   {
      double hvATR = g_detector.GetATR(1);
      if(hvATR > 0)
      {
         double sum = 0; int cnt = 0;
         for(int i = 1; i <= 50; i++)
         {
            double v = g_detector.GetATR(i);
            if(v > 0) { sum += v; cnt++; }
         }
         if(cnt > 20 && hvATR > (sum / cnt) * 2.0)
         { LogWrite("[TR-SKIP] HighVol ATR:" + DoubleToString(hvATR,2)); return; }
      }
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
      int cooldownBars = (g_consLosses >= Guard_TrendLossCooldownTrigger) ? Guard_TrendLossCooldownBars : 2;
      int cooldown = cooldownBars * PeriodSeconds(_Period);
      if((int)(TimeCurrent() - g_lastSLTime) < cooldown)
         return;
   }

   //--- Bias
   ENUM_IH_BIAS bias = g_detector.DetectBias(refBar, high, low, close, totalBars);
   if(bias == IH_BIAS_NEUTRAL) { LogWrite("[TR-SKIP] Bias NEUTRAL"); return; }
   bool isBuy = (bias == IH_BIAS_BULLISH);

   //--- BOS
   IH_BOSInfo bos = g_detector.AnalyzeBOS(refBar, isBuy, open, high, low, close, totalBars);
   if(bos.quality == IH_BOS_NONE) { LogWrite("[TR-SKIP] No BOS | " + (isBuy ? "BUY" : "SELL") + " H:" + IntegerToString(dt.hour)); return; }

   //--- Zone
   IH_Zone zone;
   if(!g_detector.DetectZone(refBar, isBuy, open, high, low, close, time, totalBars, zone))
   { LogWrite("[TR-SKIP] No Zone | " + (isBuy ? "BUY" : "SELL") + " BOS:" + (bos.quality == IH_BOS_IMPULSIVE ? "Imp" : "Cor")); return; }

   //--- Zone cooldown: skip if same zone attempted recently (matches SignalEngine)
   double zoneTolerance = 1.0;  // $1 tolerance
   if(g_lastZonePrice > 0 && MathAbs(zone.entryPrice - g_lastZonePrice) < zoneTolerance)
   {
      int cooldownSec = 2 * PeriodSeconds(_Period);
      if((int)(time[refBar] - g_lastZoneTime) < cooldownSec)
      { LogWrite("[TR-SKIP] ZoneCooldown $" + DoubleToString(zone.entryPrice,2)); return; }
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



   //--- Sideways: raise minimum score by 10 (80→90 BUY, 90→100 SELL)
   int minScore = isSideways ? IH_MinScoreA + 10 : IH_MinScoreA;
   minScore += Guard_TrendMinScoreAdd;

   if(!Guard_AllowTrendCorrective && bos.quality != IH_BOS_IMPULSIVE)
   { LogWrite("[TR-SKIP] Corrective blocked | Score:" + IntegerToString(score)); return; }

   //--- SELL: require BOS Impulsive
   if(!isBuy)
   {
      if(bos.quality != IH_BOS_IMPULSIVE) { LogWrite("[TR-SKIP] SELL BOS not Impulsive | Score:" + IntegerToString(score)); return; }
   }

   //--- Grade check
   if(score < minScore) { LogWrite("[TR-SKIP] Score " + IntegerToString(score) + " < " + IntegerToString(minScore) + " | " + (isBuy?"BUY":"SELL") + (isSideways?" SW":"")); return; }

   //--- Max positions check (tier-based)
   double bal = AccountInfoDouble(ACCOUNT_BALANCE);
   int maxPos = GuardMaxTrendPositions(bal);
   int openPos = CountPositions(EA_MAGIC_BT);
   if(openPos >= maxPos) { LogWrite("[TR-SKIP] MaxPos " + IntegerToString(openPos) + "/" + IntegerToString(maxPos)); return; }

   //--- Calculate SL/TP
   double atr = g_detector.GetATR(refBar);
   double buffer = atr * IH_ATRBufferSL;

   double entryPrice = NormalizeDouble(zone.entryPrice, 2);
   double sl, tp;

   //--- Dynamic RR tiers based on score (stronger setup = bigger TP)
   double rr;
   if(score >= 100)      rr = 2.5;        // top setup: FVG+Retest+Trend+Zone
   else if(score >= 90)  rr = 2.0;        // strong setup
   else                  rr = IH_TP1_RR;  // standard (1.5)

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
   if(lot > BT_MaxLotCap) lot = BT_MaxLotCap;
   lot = NormalizeDouble(lot * Trend_LotMult, 2);
   if(lot < 0.01) lot = 0.01;

   //--- Progressive lot reduction on consecutive losses (start at 2)
   if(g_consLosses >= 5)
      lot = NormalizeDouble(lot * 0.10, 2);
   else if(g_consLosses >= 3)
      lot = NormalizeDouble(lot * 0.25, 2);
   else if(g_consLosses >= 2)
      lot = NormalizeDouble(lot * 0.50, 2);
   if(lot < 0.01) lot = 0.01;

   //--- Update zone cooldown tracking
   g_lastZonePrice = entryPrice;
   g_lastZoneTime  = time[refBar];

   //--- Expiry: PendingExpiryBars * bar duration
   datetime expiry = TimeCurrent() + IH_PendingExpiryBars * PeriodSeconds(_Period);

   //--- Place order
   double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   string comment = StringFormat("IF8V3G_TR S:%d %s", score,
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

   LogWrite("[TR-ORDER] " + (isBuy ? "BUY" : "SELL") +
           " @ " + DoubleToString(entryPrice,2) +
           " SL:" + DoubleToString(sl,2) +
           " TP:" + DoubleToString(tp,2) +
           " Score:" + IntegerToString(score) +
           " BOS:" + (bos.quality == IH_BOS_IMPULSIVE ? "Imp" : "Cor") +
           " FVG:" + (bos.hasFVG ? "Y" : "N") +
           " Ret:" + (bos.hasRetest ? "Y" : "N") +
           " Swp:" + (bos.hasSweep ? "Y" : "N") +
           " Lot:" + DoubleToString(lot,2) +
           " RR:" + DoubleToString(rr,1) +
           (ask > entryPrice && isBuy ? " LIMIT" : " MARKET"));
}

//+------------------------------------------------------------------+
//  SIDEWAYS LOGIC — Range Bounce Dual-Direction (Iter 5)
//  BUY at lower edge, SELL at upper edge of confirmed sideways range.
//  Gated by DetectSidewaysAdvanced() score. Cluster max 2/dir/day.
//+------------------------------------------------------------------+
void ProcessSideways(datetime barTime, MqlDateTime &dt)
{
   //--- KillSwitch sideways: max 10 wins/day
   if(gs_dailyWins >= 10) return;

   //--- Daily loss limit: max 5 losses OR 3% of balance (whichever first)
   if(gs_dailyLossCount >= 5) return;
   if(gs_dayStartBal > 0 && gs_dailyLossUSD > MathMin(gs_dayStartBal * 0.03, 15000.0)) return;

   //--- Toxic hours: data-driven (WR 0-14% at these hours)
   if(dt.hour == 3 || dt.hour == 19) return;
   if(GuardBadHour(dt.hour)) return;

   //--- After-loss cooldown: 2 bars M15 (30 min)
   if(gs_lastSLTime > 0)
   {
      int cooldown = 2 * PeriodSeconds(_Period);
      if((int)(TimeCurrent() - gs_lastSLTime) < cooldown)
         return;
   }

   //--- Count existing sideways positions per direction
   int existBuy = 0, existSell = 0;
   for(int i = 0; i < PositionsTotal(); i++)
   {
      ulong ticket = PositionGetTicket(i);
      if(ticket <= 0) continue;
      if(PositionGetInteger(POSITION_MAGIC) != EA_MAGIC_SIDEWAYS) continue;
      if(PositionGetString(POSITION_SYMBOL) != _Symbol) continue;
      if(PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY)  existBuy++;
      else existSell++;
   }
   bool buyFull  = (existBuy  >= RangeBounce_MaxBuy);
   bool sellFull = (existSell >= RangeBounce_MaxSell);
   if(buyFull && sellFull) return;

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

   //--- ATR for range max validation + SL buffer
   double atrVal = 0;
   if(gs_atrHandle != INVALID_HANDLE)
   {
      double atrBuf[];
      if(CopyBuffer(gs_atrHandle, 0, 0, 1, atrBuf) > 0)
         atrVal = atrBuf[0];
   }
   if(atrVal > 0 && rangeSize > atrVal * 10) return;

   //--- Entry zones
   double curClose = close[1];
   double buyZoneTop  = rangeLow  + rangeSize * RangeBounce_EntryPct;
   double sellZoneBot = rangeHigh - rangeSize * RangeBounce_EntryPct;
   double midRange    = rangeLow  + rangeSize * 0.50;

   //--- Determine direction
   bool doBuy  = (!buyFull  && curClose <= buyZoneTop);
   bool doSell = (!sellFull && curClose >= sellZoneBot);
   if(!doBuy && !doSell) return;

   //--- Cluster protection: max 2 entries per range per day
   bool sameRange = (MathAbs(rangeHigh - gs_lastRangeHigh) < 5.0 &&
                     MathAbs(rangeLow - gs_lastRangeLow) < 5.0);
   if(sameRange && gs_rangeEntries >= RangeBounce_MaxEntriesPerRange) return;

   //--- Calculate SL/TP
   double slBuffer = (atrVal > 0) ? atrVal * 0.5 : 3.0;
   double entryPrice, sl, tp;

   if(doBuy)
   {
      entryPrice = curClose;
      sl = rangeLow - slBuffer;
      tp = midRange;
      double slDist = entryPrice - sl;
      if(slDist < 5.0)  sl = entryPrice - 5.0;
      if(slDist > 20.0) sl = entryPrice - 20.0;
   }
   else
   {
      entryPrice = curClose;
      sl = rangeHigh + slBuffer;
      tp = midRange;
      double slDist = sl - entryPrice;
      if(slDist < 5.0)  sl = entryPrice + 5.0;
      if(slDist > 20.0) sl = entryPrice + 20.0;
   }

   entryPrice = NormalizeDouble(entryPrice, 2);
   sl = NormalizeDouble(sl, 2);
   tp = NormalizeDouble(tp, 2);

   //--- Lot sizing with RangeBounce_LotMult
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
   lot = NormalizeDouble(lot * RangeBounce_LotMult, 2);
   if(lot < 0.01) lot = 0.01;
   if(lot > BT_MaxLotCap) lot = BT_MaxLotCap;

   //--- Progressive lot reduction (sideways own counter, start at 2)
   if(gs_consLosses >= 5)
      lot = NormalizeDouble(lot * 0.10, 2);
   else if(gs_consLosses >= 3)
      lot = NormalizeDouble(lot * 0.25, 2);
   else if(gs_consLosses >= 2)
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

   //--- Place order
   string dir = doBuy ? "BUY" : "SELL";
   string comment = StringFormat("IF8V3G_RB %s R:$%.0f", dir, rangeSize);

   if(doBuy)
      gs_trade.Buy(lot, _Symbol, 0, sl, tp, comment);
   else
      gs_trade.Sell(lot, _Symbol, 0, sl, tp, comment);

   LogWrite("[SW-ORDER] " + dir + " @ " + DoubleToString(entryPrice,2) +
           " SL:" + DoubleToString(sl,2) +
           " TP:" + DoubleToString(tp,2) +
           " Range:$" + DoubleToString(rangeSize,0) +
           " Cluster:" + IntegerToString(gs_rangeEntries) +
           " Lot:" + DoubleToString(lot,2) +
           " ADX:" + DoubleToString(g_adxH4Value,1));
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

         //--- Partial close: DEAL_ENTRY_OUT but position still exists → skip win/loss counting
         if(dealEntry == DEAL_ENTRY_OUT && trans.position > 0 && PositionSelectByTicket(trans.position))
            return; // partial close, position still open

         if(dealEntry == DEAL_ENTRY_OUT)
         {
            //--- Full close: cleanup partial tracking
            RemovePartialDone(trans.position);

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
                  g_consLosses = 0;
                  LogWrite("[TR-WIN] $" + DoubleToString(profit,2) + " | DayWins:" + IntegerToString(g_dailyWins));
               }
               else
               {
                  g_lastSLTime = TimeCurrent();
                  g_consLosses++;
                  g_dailyLossUSD += MathAbs(profit);
                  g_dailyLossCount++;
                  LogWrite("[TR-LOSS] $" + DoubleToString(profit,2) + " | ConsLoss:" + IntegerToString(g_consLosses) + " DayLoss:" + IntegerToString(g_dailyLossCount) + "/$" + DoubleToString(g_dailyLossUSD,2));
               }
            }
            else if(magic == EA_MAGIC_SIDEWAYS)
            {
               //--- SIDEWAYS state
               if(profit > 0)
               {
                  gs_dailyWins++;
                  gs_consLosses = 0;
                  LogWrite("[SW-WIN] $" + DoubleToString(profit,2) + " | DayWins:" + IntegerToString(gs_dailyWins));
               }
               else
               {
                  gs_lastSLTime = TimeCurrent();
                  gs_consLosses++;
                  gs_dailyLossUSD += MathAbs(profit);
                  gs_dailyLossCount++;
                  LogWrite("[SW-LOSS] $" + DoubleToString(profit,2) + " | ConsLoss:" + IntegerToString(gs_consLosses) + " DayLoss:" + IntegerToString(gs_dailyLossCount) + "/$" + DoubleToString(gs_dailyLossUSD,2));
               }
            }
            else if(magic == EA_MAGIC_DC)
            {
               if(profit > 0)
                  LogWrite("[DC-WIN] $" + DoubleToString(profit,2));
               else
                  LogWrite("[DC-LOSS] $" + DoubleToString(profit,2));
            }
         }
      }
   }
}

double OnTester()
{
   double profit = TesterStatistics(STAT_PROFIT);
   double pf = TesterStatistics(STAT_PROFIT_FACTOR);
   double trades = TesterStatistics(STAT_TRADES);
   double equityDdPct = TesterStatistics(STAT_EQUITY_DDREL_PERCENT);
   double balanceDdPct = TesterStatistics(STAT_BALANCE_DDREL_PERCENT);
   double recovery = TesterStatistics(STAT_RECOVERY_FACTOR);

   double score = profit;
   if(profit <= 0.0 || pf < 1.05 || trades < 10.0)
      score = profit - 100000.0;
   else
      score = profit * MathMin(pf, 3.0) * MathMax(recovery, 0.1) / (1.0 + equityDdPct + (balanceDdPct * 0.5));

   int handle = FileOpen(
      "InvictusForward8_V3Guard_optimization_passes.csv",
      FILE_COMMON | FILE_CSV | FILE_READ | FILE_WRITE | FILE_SHARE_READ | FILE_SHARE_WRITE,
      ';'
   );
   if(handle != INVALID_HANDLE)
   {
      if(FileSize(handle) <= 2)
      {
         FileWrite(handle,
                   "score", "profit", "profit_factor", "trades", "equity_dd_pct", "balance_dd_pct", "recovery_factor",
                   "BT_RiskPercent", "BT_CompoundingPer", "BT_MaxLotCap",
                   "Guard_MaxTrendPosLowBalance",
                   "RangeBounce_LotMult", "RangeBounce_MaxBuy", "RangeBounce_MaxSell", "RangeBounce_MaxEntriesPerRange",
                   "DropCatcher_LotMult");
      }
      FileSeek(handle, 0, SEEK_END);
      FileWrite(handle,
                score, profit, pf, trades, equityDdPct, balanceDdPct, recovery,
                BT_RiskPercent, BT_CompoundingPer, BT_MaxLotCap,
                Guard_MaxTrendPosLowBalance,
                RangeBounce_LotMult, RangeBounce_MaxBuy, RangeBounce_MaxSell, RangeBounce_MaxEntriesPerRange,
                DropCatcher_LotMult);
      FileClose(handle);
   }

   return score;
}
//+------------------------------------------------------------------+
