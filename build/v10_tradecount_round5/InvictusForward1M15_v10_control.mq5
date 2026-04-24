#property copyright "OpenAI Codex"
#property version   "2.00"
#property strict
// Variant: v10

#include <Trade/Trade.mqh>

input double V10_RiskPercent = 4.50;
input double V10_BuyRiskMultiplier = 0.45;
input double V10_SellRiskMultiplier = 1.00;
input double V10_WeakBuyRiskMultiplier = 0.15;
input double V10_WeakSellRiskMultiplier = 0.55;
input bool   V10_EnableBuys = true;
input bool   V10_EnableSells = true;
input int    V10_MaxPositions = 3;
input int    V10_WeakRegimeMaxPositions = 1;
input int    V10_SellSessionStartHour = 8;
input int    V10_SellSessionEndHour = 20;
input int    V10_BuySessionStartHour = 5;
input int    V10_BuySessionEndHour = 20;
input bool   V10_StrongBullRelaxBuySession = false;
input bool   V10_EnableMixedMomentumEntries = false;
input double V10_MaxSpreadUsd = 1.20;

input int    V10_H1FastEMA = 20;
input int    V10_H1SlowEMA = 50;
input int    V10_H4FastEMA = 20;
input int    V10_H4SlowEMA = 50;
input int    V10_H1ADXPeriod = 14;
input int    V10_H1ATRPeriod = 14;
input double V10_H1ADXMin = 20.0;
input double V10_H1ADXStrongMin = 26.0;
input double V10_StrongGapATR = 0.10;
input int    V10_M5TrendEMA = 20;
input int    V10_M5ATRPeriod = 14;

input int    V10_BreakoutLookback = 12;
input int    V10_PullbackLookback = 6;
input bool   V10_RequirePullback = false;
input bool   V10_AllowBreakoutBuys = true;
input bool   V10_AllowPullbackBuys = true;
input bool   V10_UseBuyCoreHours = true;
input bool   V10_EnableBullSubEngine = false;
input bool   V10_BullSubAllowWeakBull = false;
input int    V10_BullSubSessionStartHour = 0;
input int    V10_BullSubSessionEndHour = 23;
input bool   V10_BullSubOnlyOutsideCore = true;
input int    V10_BullSubCompressionBars = 6;
input double V10_BullSubMaxRangeATR = 1.60;
input double V10_BullSubTouchEmaATR = 0.18;
input double V10_BullSubBreakATR = 0.04;
input double V10_BullSubMinBodyRatio = 0.58;
input double V10_BullSubRiskMultiplier = 0.28;
input double V10_BullSubRR = 1.85;
input int    V10_BullSubMaxHoldBars = 24;
input bool   V10_EnableBearSubEngine = false;
input bool   V10_BearSubAllowWeakBear = false;
input int    V10_BearSubSessionStartHour = 0;
input int    V10_BearSubSessionEndHour = 23;
input int    V10_BearSubCompressionBars = 6;
input double V10_BearSubMaxRangeATR = 1.60;
input double V10_BearSubTouchEmaATR = 0.18;
input double V10_BearSubBreakATR = 0.04;
input double V10_BearSubMinBodyRatio = 0.58;
input double V10_BearSubRiskMultiplier = 0.28;
input double V10_BearSubRR = 1.75;
input int    V10_BearSubMaxHoldBars = 24;
input bool   V10_StrongBullRelaxCoreHours = false;
input bool   V10_StrongBullPullbackOnlyOutsideCore = true;
input bool   V10_BlockBuyHour07 = false;
input bool   V10_BlockBuyHour10 = false;
input bool   V10_BlockBuyHour14 = false;
input bool   V10_BlockBuyHour17 = false;
input int    V10_BullPullbackLookback = 8;
input double V10_BullTouchATR = 0.15;
input double V10_BullReclaimATR = 0.00;
input double V10_BullMaxStretchATR = 1.10;
input int    V10_BearRejectLookback = 6;
input double V10_BearTouchATR = 0.12;
input double V10_BearBreakBelowPrevATR = 0.02;
input double V10_BearMaxStretchATR = 1.30;
input double V10_MinBreakATR = 0.05;
input double V10_BuyMinBreakATR = 0.12;
input double V10_WeakSellMinBreakATR = 0.10;
input double V10_WeakBuyMinBreakATR = 0.18;
input double V10_MinBodyRatio = 0.48;
input double V10_BuyMinBodyRatio = 0.54;
input double V10_WeakSellMinBodyRatio = 0.54;
input double V10_WeakBuyMinBodyRatio = 0.60;
input double V10_MaxStretchATR = 1.50;
input int    V10_ChopLookbackBars = 10;
input int    V10_MaxEmaFlips = 3;
input int    V10_HoldBars = 2;
input double V10_HoldBufferATR = 0.05;

input int    V10_StopLookbackBars = 10;
input double V10_StopBufferATR = 0.25;
input double V10_MinSLUsd = 3.00;
input double V10_MaxSLUsd = 10.00;
input double V10_SellRR = 1.30;
input double V10_BuyRR = 1.55;
input double V10_WeakSellRR = 1.10;
input double V10_WeakBuyRR = 1.30;

input int    V10_MaxHoldBars = 36;
input double V10_BreakevenR = 0.80;
input double V10_BreakevenLockUsd = 0.20;
input bool   V10_FastFailBuyGuard = false;
input bool   V10_FastFailPullbackOnly = true;
input int    V10_FastFailBars = 6;
input double V10_FastFailMinProgressR = 0.10;
input bool   V10_CloseOnRegimeFlip = false;
input bool   V10_TimeCloseProfitOnly = true;
input int    V10_ScoreGradeAMin = 85;
input int    V10_ScoreGradeBMin = 72;
input int    V10_MinTradeScore = 0;
input int    V10_ScoreBoostMin = 90;
input double V10_ScoreRRBonus = 0.00;
input double V10_ScoreRiskBonus = 1.00;
input bool   V10_EnableTPManager = false;
input double V10_TP1R = 1.15;
input double V10_TP1CloseFraction = 0.50;
input double V10_RunnerRR = 2.40;
input double V10_TrailStartR = 1.50;
input double V10_TrailATR = 1.20;
input double V10_TrailLockUsd = 0.40;
input bool   V10_EnableAddOnEngine = false;
input bool   V10_EnableBuyAddOns = true;
input bool   V10_EnableSellAddOns = true;
input bool   V10_AddOnAllowWeakRegime = false;
input int    V10_AddOnMaxPerSide = 1;
input double V10_AddOnMinProgressR = 0.60;
input double V10_AddOnBreakATR = 0.02;
input double V10_AddOnMinBodyRatio = 0.54;
input double V10_AddOnRiskMultiplier = 0.50;
input double V10_AddOnRR = 1.25;
input int    V10_AddOnMaxHoldBars = 18;

enum V10Regime
  {
   V10_REGIME_NONE = 0,
   V10_REGIME_WEAK_BULL = 1,
   V10_REGIME_STRONG_BULL = 2,
   V10_REGIME_WEAK_BEAR = -1,
   V10_REGIME_STRONG_BEAR = -2,
   V10_REGIME_MIXED = 9
  };

struct V10Signal
  {
   bool   valid;
   bool   sell;
   double entry;
   double stopLoss;
   double takeProfit;
   double lot;
   double stopDistance;
   double rr;
   int    score;
   string grade;
   string engineCode;
   string tags;
   string note;
   string comment;
  };

CTrade            g_trade;
int               g_emaFastH1 = INVALID_HANDLE;
int               g_emaSlowH1 = INVALID_HANDLE;
int               g_emaFastH4 = INVALID_HANDLE;
int               g_emaSlowH4 = INVALID_HANDLE;
int               g_adxH1 = INVALID_HANDLE;
int               g_atrH1 = INVALID_HANDLE;
int               g_emaM5 = INVALID_HANDLE;
int               g_atrM5 = INVALID_HANDLE;
datetime          g_lastBarTime = 0;
static const ulong V10_MAGIC = 2026042001;
static const ENUM_TIMEFRAMES V10_EXEC_TF = PERIOD_M5;


double V10NormalizePrice(const double price)
  {
   return(NormalizeDouble(price, (int)SymbolInfoInteger(_Symbol, SYMBOL_DIGITS)));
  }


bool V10NewBar()
  {
   datetime times[];
   if(CopyTime(_Symbol, V10_EXEC_TF, 0, 1, times) != 1)
      return(false);
   if(times[0] == g_lastBarTime)
      return(false);
   g_lastBarTime = times[0];
   return(true);
  }


int V10HourOf(const datetime ts)
  {
   MqlDateTime dt;
   TimeToStruct(ts, dt);
   return(dt.hour);
  }


bool V10HourInSession(const int hour, const int startHour, const int endHour)
  {
   if(startHour == endHour)
      return(true);
   if(startHour < endHour)
      return(hour >= startHour && hour < endHour);
  return(hour >= startHour || hour < endHour);
  }


string V10RegimeLabel(const V10Regime regime)
  {
   switch(regime)
     {
      case V10_REGIME_STRONG_BULL:
         return("SBULL");
      case V10_REGIME_WEAK_BULL:
         return("WBULL");
      case V10_REGIME_STRONG_BEAR:
         return("SBEAR");
      case V10_REGIME_WEAK_BEAR:
         return("WBEAR");
      case V10_REGIME_MIXED:
         return("MIXED");
     }
   return("NONE");
  }


int V10ClampScore(const int score)
  {
   return((int)MathMax(0, MathMin(99, score)));
  }


string V10GradeForScore(const int score)
  {
   if(score >= V10_ScoreGradeAMin)
      return("A");
   if(score >= V10_ScoreGradeBMin)
      return("B");
   return("R");
  }


string V10AppendTag(const string tags, const string tag)
  {
   if(tag == "")
      return(tags);
   if(tags == "")
      return(tag);
   return(tags + "|" + tag);
  }


string V10BuildComment(const string engineCode, const int score, const string grade, const string tags)
  {
   string comment = "Inv|" + engineCode + "|S" + IntegerToString(score) + "|" + grade;
   if(tags != "")
      comment += "|" + tags;
   if(StringLen(comment) > 31)
      comment = StringSubstr(comment, 0, 31);
   return(comment);
  }


void V10FillSignalMeta(V10Signal &signal,
                       const string engineCode,
                       const int score,
                       const string tags,
                       const string note)
  {
   signal.score = V10ClampScore(score);
   signal.grade = V10GradeForScore(signal.score);
   signal.engineCode = engineCode;
   signal.tags = tags;
   signal.note = note;
   signal.comment = V10BuildComment(engineCode, signal.score, signal.grade, tags);
  }


string V10StatePrefix()
  {
   return("InvV10.");
  }


string V10StateKey(const ulong ticket, const string suffix)
  {
   return(V10StatePrefix() + StringFormat("%I64u", ticket) + "." + suffix);
  }


double V10StateGet(const ulong ticket, const string suffix, const double fallback)
  {
   string key = V10StateKey(ticket, suffix);
   if(GlobalVariableCheck(key))
      return(GlobalVariableGet(key));
   return(fallback);
  }


void V10StateSet(const ulong ticket, const string suffix, const double value)
  {
   GlobalVariableSet(V10StateKey(ticket, suffix), value);
  }


void V10ClearState()
  {
   string prefix = V10StatePrefix();
   for(int i = GlobalVariablesTotal() - 1; i >= 0; i--)
     {
      string name = GlobalVariableName(i);
      if(StringFind(name, prefix) == 0)
         GlobalVariableDel(name);
     }
  }


int V10VolumePrecision()
  {
   double step = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);
   int precision = 0;
   double probe = step;
   while(precision < 8 && MathAbs(probe - MathRound(probe)) > 1e-8)
     {
      probe *= 10.0;
      precision++;
     }
   return(precision);
  }


double V10FloorVolume(const double rawVolume)
  {
   double step = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);
   double maxLot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX);
   if(step <= 0.0 || rawVolume <= 0.0)
      return(0.0);
   double clipped = MathMin(maxLot, rawVolume);
   double steps = MathFloor((clipped / step) + 1e-9);
   return(NormalizeDouble(steps * step, V10VolumePrecision()));
  }


double V10InitialVolume(const ulong ticket, const double currentVolume)
  {
   double stored = V10StateGet(ticket, "initvol", 0.0);
   if(stored > 0.0)
      return(stored);
   V10StateSet(ticket, "initvol", currentVolume);
   return(currentVolume);
  }


int V10TPStage(const ulong ticket)
  {
   return((int)V10StateGet(ticket, "tpstage", 0.0));
  }


void V10SetTPStage(const ulong ticket, const int stage)
  {
   V10StateSet(ticket, "tpstage", (double)stage);
  }


bool V10StopFitsMarket(const ENUM_POSITION_TYPE type, const double currentPrice, const double stopLoss)
  {
   double minDistance = V10MinStopDistance();
   if(type == POSITION_TYPE_BUY)
      return(stopLoss < (currentPrice - minDistance));
   return(stopLoss > (currentPrice + minDistance));
  }


bool V10TakeProfitFitsMarket(const ENUM_POSITION_TYPE type, const double currentPrice, const double takeProfit)
  {
   if(takeProfit <= 0.0)
      return(true);
   double minDistance = V10MinStopDistance();
   if(type == POSITION_TYPE_BUY)
      return(takeProfit > (currentPrice + minDistance));
   return(takeProfit < (currentPrice - minDistance));
  }


double V10PartialCloseVolume(const double initialVolume, const double currentVolume)
  {
   double minLot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
   double targetClose = V10FloorVolume(initialVolume * V10_TP1CloseFraction);
   if(targetClose < minLot)
      return(0.0);
   double remaining = V10FloorVolume(currentVolume - targetClose);
   if(remaining < minLot)
     {
      double maxClose = V10FloorVolume(currentVolume - minLot);
      if(maxClose < minLot)
         return(0.0);
      return(maxClose);
     }
   return(targetClose);
  }


bool V10BuyHourBlocked(const int hour)
  {
   if(V10_BlockBuyHour07 && hour == 7)
      return(true);
   if(V10_BlockBuyHour10 && hour == 10)
      return(true);
   if(V10_BlockBuyHour14 && hour == 14)
      return(true);
   if(V10_BlockBuyHour17 && hour == 17)
      return(true);
   return(false);
  }


bool V10BuyHourPreferred(const int hour)
  {
   switch(hour)
     {
      case 5:
      case 6:
      case 9:
      case 11:
      case 15:
      case 16:
      case 18:
      case 19:
         return(true);
     }
   return(false);
  }


bool V10SpreadAllowed()
  {
   double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   if(ask <= 0.0 || bid <= 0.0)
      return(false);
   return((ask - bid) <= V10_MaxSpreadUsd);
  }


bool V10CopyRates(MqlRates &rates[], const int count)
  {
   ArraySetAsSeries(rates, true);
   return(CopyRates(_Symbol, V10_EXEC_TF, 0, count, rates) == count);
  }


double V10IndicatorValue(const int handle, const int shift)
  {
   double buffer[];
   ArraySetAsSeries(buffer, true);
   if(CopyBuffer(handle, 0, 0, shift + 1, buffer) < (shift + 1))
      return(0.0);
   return(buffer[shift]);
  }


double V10IndicatorValueFromBuffer(const int handle, const int bufferIndex, const int shift)
  {
   double buffer[];
   ArraySetAsSeries(buffer, true);
   if(CopyBuffer(handle, bufferIndex, 0, shift + 1, buffer) < (shift + 1))
      return(0.0);
   return(buffer[shift]);
  }


bool V10RegimeIsBull(const V10Regime regime)
  {
   return(regime == V10_REGIME_WEAK_BULL || regime == V10_REGIME_STRONG_BULL);
  }


bool V10RegimeIsBear(const V10Regime regime)
  {
   return(regime == V10_REGIME_WEAK_BEAR || regime == V10_REGIME_STRONG_BEAR);
  }


bool V10RegimeIsStrong(const V10Regime regime)
  {
   return(regime == V10_REGIME_STRONG_BULL || regime == V10_REGIME_STRONG_BEAR);
  }


V10Regime V10DetectRegime()
  {
   double fastH1 = V10IndicatorValue(g_emaFastH1, 1);
   double slowH1 = V10IndicatorValue(g_emaSlowH1, 1);
   double fastH4 = V10IndicatorValue(g_emaFastH4, 1);
   double slowH4 = V10IndicatorValue(g_emaSlowH4, 1);
   double adxH1 = V10IndicatorValueFromBuffer(g_adxH1, 0, 1);
   double atrH1 = V10IndicatorValue(g_atrH1, 1);
   if(fastH1 == 0.0 || slowH1 == 0.0 || fastH4 == 0.0 || slowH4 == 0.0 || adxH1 == 0.0 || atrH1 == 0.0)
      return(V10_REGIME_NONE);

   bool bullAligned = fastH1 > slowH1 && fastH4 > slowH4;
   bool bearAligned = fastH1 < slowH1 && fastH4 < slowH4;
   if(!bullAligned && !bearAligned)
      return(V10_REGIME_MIXED);
   if(adxH1 < V10_H1ADXMin)
      return(V10_REGIME_MIXED);

   double gapAtr = MathAbs(fastH1 - slowH1) / atrH1;
   bool strong = adxH1 >= V10_H1ADXStrongMin && gapAtr >= V10_StrongGapATR;
   if(bullAligned)
      return(strong ? V10_REGIME_STRONG_BULL : V10_REGIME_WEAK_BULL);
   return(strong ? V10_REGIME_STRONG_BEAR : V10_REGIME_WEAK_BEAR);
  }


bool V10MixedBiasBull()
  {
   double fastH1 = V10IndicatorValue(g_emaFastH1, 1);
   double slowH1 = V10IndicatorValue(g_emaSlowH1, 1);
   if(fastH1 == 0.0 || slowH1 == 0.0)
      return(true);
   return(fastH1 >= slowH1);
  }


int V10CountOpenPositions()
  {
   int count = 0;
   for(int i = PositionsTotal() - 1; i >= 0; i--)
     {
      ulong ticket = PositionGetTicket(i);
      if(ticket == 0 || !PositionSelectByTicket(ticket))
         continue;
      if(PositionGetString(POSITION_SYMBOL) != _Symbol)
         continue;
      if((ulong)PositionGetInteger(POSITION_MAGIC) != V10_MAGIC)
         continue;
      count++;
     }
   return(count);
  }


int V10CountOpenPositionsByType(const bool sell)
  {
   int count = 0;
   for(int i = PositionsTotal() - 1; i >= 0; i--)
     {
      ulong ticket = PositionGetTicket(i);
      if(ticket == 0 || !PositionSelectByTicket(ticket))
         continue;
      if(PositionGetString(POSITION_SYMBOL) != _Symbol)
         continue;
      if((ulong)PositionGetInteger(POSITION_MAGIC) != V10_MAGIC)
         continue;
      ENUM_POSITION_TYPE type = (ENUM_POSITION_TYPE)PositionGetInteger(POSITION_TYPE);
      if((sell && type == POSITION_TYPE_SELL) || (!sell && type == POSITION_TYPE_BUY))
         count++;
     }
   return(count);
  }


int V10CountOpenAddOnsByType(const bool sell)
  {
   int count = 0;
   string marker = sell ? "|AS|" : "|AB|";
   for(int i = PositionsTotal() - 1; i >= 0; i--)
     {
      ulong ticket = PositionGetTicket(i);
      if(ticket == 0 || !PositionSelectByTicket(ticket))
         continue;
      if(PositionGetString(POSITION_SYMBOL) != _Symbol)
         continue;
      if((ulong)PositionGetInteger(POSITION_MAGIC) != V10_MAGIC)
         continue;
      ENUM_POSITION_TYPE type = (ENUM_POSITION_TYPE)PositionGetInteger(POSITION_TYPE);
      if(((sell && type == POSITION_TYPE_SELL) || (!sell && type == POSITION_TYPE_BUY)) &&
         StringFind(PositionGetString(POSITION_COMMENT), marker) >= 0)
         count++;
     }
   return(count);
  }


bool V10HasQualifiedLeadPosition(const bool sell, const double minProgressR)
  {
   double currentPrice = sell ? SymbolInfoDouble(_Symbol, SYMBOL_ASK) : SymbolInfoDouble(_Symbol, SYMBOL_BID);
   if(currentPrice <= 0.0)
      return(false);

   string addonMarker = sell ? "|AS|" : "|AB|";
   for(int i = PositionsTotal() - 1; i >= 0; i--)
     {
      ulong ticket = PositionGetTicket(i);
      if(ticket == 0 || !PositionSelectByTicket(ticket))
         continue;
      if(PositionGetString(POSITION_SYMBOL) != _Symbol)
         continue;
      if((ulong)PositionGetInteger(POSITION_MAGIC) != V10_MAGIC)
         continue;
      ENUM_POSITION_TYPE type = (ENUM_POSITION_TYPE)PositionGetInteger(POSITION_TYPE);
      if(!((sell && type == POSITION_TYPE_SELL) || (!sell && type == POSITION_TYPE_BUY)))
         continue;

      string comment = PositionGetString(POSITION_COMMENT);
      if(StringFind(comment, addonMarker) >= 0)
         continue;

      double openPrice = PositionGetDouble(POSITION_PRICE_OPEN);
      double stopLoss = PositionGetDouble(POSITION_SL);
      double riskDistance = sell ? (stopLoss - openPrice) : (openPrice - stopLoss);
      if(riskDistance <= 0.0)
         continue;
      double favorable = sell ? (openPrice - currentPrice) : (currentPrice - openPrice);
      double progressR = favorable / riskDistance;
      if(progressR >= minProgressR && PositionGetDouble(POSITION_PROFIT) > 0.0)
         return(true);
     }
   return(false);
  }


double V10Clamp(const double value, const double lower, const double upper)
  {
   return(MathMax(lower, MathMin(upper, value)));
  }


double V10MinStopDistance()
  {
   double point = SymbolInfoDouble(_Symbol, SYMBOL_POINT);
   double stops = (double)SymbolInfoInteger(_Symbol, SYMBOL_TRADE_STOPS_LEVEL) * point;
   double freeze = (double)SymbolInfoInteger(_Symbol, SYMBOL_TRADE_FREEZE_LEVEL) * point;
   double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   double spread = (ask > 0.0 && bid > 0.0) ? (ask - bid) : 0.0;
   return(MathMax(stops, freeze) + (spread * 2.0) + (point * 10.0));
  }


bool V10StopsValid(const bool sell, const double entry, const double stopLoss, const double takeProfit)
  {
   double minDistance = V10MinStopDistance();
   if(sell)
      return((stopLoss - entry) > minDistance && (entry - takeProfit) > minDistance);
   return((entry - stopLoss) > minDistance && (takeProfit - entry) > minDistance);
  }


double V10NormalizeVolume(const double rawLot)
  {
   double minLot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
   double maxLot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX);
   double step = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);
   if(step <= 0.0)
      return(0.0);
   double clipped = MathMax(minLot, MathMin(maxLot, rawLot));
   double steps = MathFloor(clipped / step);
   double lot = steps * step;
   int precision = 0;
   double probe = step;
   while(precision < 8 && MathAbs(probe - MathRound(probe)) > 1e-8)
     {
      probe *= 10.0;
      precision++;
     }
   return(NormalizeDouble(lot, precision));
  }


double V10LotForRisk(const bool sell, const double entry, const double stopLoss, const double riskUsd)
  {
   double tickSize = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);
   double tickValue = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE_PROFIT);
   if(tickValue <= 0.0)
      tickValue = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE);
   if(tickSize <= 0.0 || tickValue <= 0.0)
      return(0.0);

   double distance = MathAbs(entry - stopLoss);
   if(distance <= 0.0)
      return(0.0);

   double lossPerLot = (distance / tickSize) * tickValue;
   if(lossPerLot <= 0.0)
      return(0.0);

   return(V10NormalizeVolume(riskUsd / lossPerLot));
  }


double V10RiskBudgetUsd(const bool sell)
  {
   return(V10RiskBudgetUsd(sell, V10_REGIME_NONE));
  }


double V10RiskBudgetUsd(const bool sell, const V10Regime regime)
  {
   double equity = AccountInfoDouble(ACCOUNT_EQUITY);
   double riskUsd = equity * (V10_RiskPercent / 100.0);
   double multiplier = 0.0;

   if(sell)
     {
      if(regime == V10_REGIME_STRONG_BEAR)
         multiplier = V10_SellRiskMultiplier;
      else if(regime == V10_REGIME_WEAK_BEAR)
         multiplier = V10_WeakSellRiskMultiplier;
     }
   else
     {
      if(regime == V10_REGIME_STRONG_BULL)
         multiplier = V10_BuyRiskMultiplier;
      else if(regime == V10_REGIME_WEAK_BULL)
         multiplier = V10_WeakBuyRiskMultiplier;
     }

   riskUsd *= multiplier;
   return(riskUsd);
  }


double V10BodyRatio(const MqlRates &bar)
  {
   double range = bar.high - bar.low;
   if(range <= 0.0)
      return(0.0);
   return(MathAbs(bar.close - bar.open) / range);
  }


double V10HighestHigh(const MqlRates &rates[], const int startShift, const int endShift)
  {
   double value = rates[startShift].high;
   for(int shift = startShift + 1; shift <= endShift; shift++)
      value = MathMax(value, rates[shift].high);
   return(value);
  }


double V10LowestLow(const MqlRates &rates[], const int startShift, const int endShift)
  {
   double value = rates[startShift].low;
   for(int shift = startShift + 1; shift <= endShift; shift++)
      value = MathMin(value, rates[shift].low);
   return(value);
  }


bool V10HadPullback(const bool sell, const MqlRates &rates[], const double emaValue)
  {
   if(!V10_RequirePullback)
      return(true);
   int maxShift = MathMin(V10_PullbackLookback + 1, ArraySize(rates) - 1);
   for(int shift = 2; shift <= maxShift; shift++)
     {
      if(sell && (rates[shift].close > rates[shift].open || rates[shift].high >= emaValue))
         return(true);
      if(!sell && (rates[shift].close < rates[shift].open || rates[shift].low <= emaValue))
         return(true);
     }
   return(false);
  }


bool V10BullPullbackSeen(const MqlRates &rates[], const double emaValue, const double atr)
  {
   int maxShift = MathMin(V10_BullPullbackLookback + 1, ArraySize(rates) - 1);
   double touchLevel = emaValue + (atr * V10_BullTouchATR);
   for(int shift = 2; shift <= maxShift; shift++)
     {
      if(rates[shift].low <= touchLevel && rates[shift].close < rates[shift].open)
         return(true);
     }
   return(false);
  }


bool V10BearRejectionSeen(const MqlRates &rates[], const double emaValue, const double atr)
  {
   int maxShift = MathMin(V10_BearRejectLookback + 1, ArraySize(rates) - 1);
   double touchLevel = emaValue - (atr * V10_BearTouchATR);
   for(int shift = 2; shift <= maxShift; shift++)
     {
      if(rates[shift].high >= touchLevel && rates[shift].close > rates[shift].open)
         return(true);
     }
   return(false);
  }


bool V10DirectionalHoldOk(const bool sell, const MqlRates &rates[], const double atr)
  {
   int bars = MathMax(1, V10_HoldBars);
   int lookback = MathMax(bars + 1, V10_ChopLookbackBars);
   double emaBuffer[];
   ArraySetAsSeries(emaBuffer, true);
   if(CopyBuffer(g_emaM5, 0, 0, lookback + 3, emaBuffer) < (lookback + 2))
      return(false);

   double holdBuffer = atr * V10_HoldBufferATR;
   int flips = 0;
   int prevSide = 0;

   for(int shift = lookback; shift >= 1; shift--)
     {
      int side = 0;
      double close = rates[shift].close;
      double ema = emaBuffer[shift];
      if(close > (ema + holdBuffer))
         side = 1;
      else if(close < (ema - holdBuffer))
         side = -1;

      if(side != 0)
        {
         if(prevSide != 0 && side != prevSide)
            flips++;
         prevSide = side;
        }
     }

   if(flips > V10_MaxEmaFlips)
      return(false);

   for(int shift = 1; shift <= bars; shift++)
     {
      double close = rates[shift].close;
      double ema = emaBuffer[shift];
      if(sell)
        {
         if(close >= (ema - holdBuffer))
            return(false);
        }
      else
        {
         if(close <= (ema + holdBuffer))
            return(false);
        }
     }

   return(true);
  }


double V10SellMinBreakATR(const V10Regime regime)
  {
   return(V10RegimeIsStrong(regime) ? V10_MinBreakATR : V10_WeakSellMinBreakATR);
  }


double V10BuyMinBreakATR(const V10Regime regime)
  {
   return(V10RegimeIsStrong(regime) ? V10_BuyMinBreakATR : V10_WeakBuyMinBreakATR);
  }


double V10SellMinBodyRatio(const V10Regime regime)
  {
   return(V10RegimeIsStrong(regime) ? V10_MinBodyRatio : V10_WeakSellMinBodyRatio);
  }


double V10BuyMinBodyRatio(const V10Regime regime)
  {
   return(V10RegimeIsStrong(regime) ? V10_BuyMinBodyRatio : V10_WeakBuyMinBodyRatio);
  }


double V10SellRRForRegime(const V10Regime regime)
  {
   return(V10RegimeIsStrong(regime) ? V10_SellRR : V10_WeakSellRR);
  }


double V10BuyRRForRegime(const V10Regime regime)
  {
   return(V10RegimeIsStrong(regime) ? V10_BuyRR : V10_WeakBuyRR);
  }


double V10BuyRiskMultiplierForRegime(const V10Regime regime)
  {
   return(V10RegimeIsStrong(regime) ? V10_BuyRiskMultiplier : V10_WeakBuyRiskMultiplier);
  }


double V10BuyRiskBudgetUsd(const V10Regime regime, const double overrideMultiplier = -1.0)
  {
   double equity = AccountInfoDouble(ACCOUNT_EQUITY);
   double riskUsd = equity * (V10_RiskPercent / 100.0);
   double multiplier = (overrideMultiplier >= 0.0) ? overrideMultiplier : V10BuyRiskMultiplierForRegime(regime);
   return(riskUsd * multiplier);
  }


int V10AllowedMaxPositions(const V10Regime regime)
  {
   return(V10RegimeIsStrong(regime) ? V10_MaxPositions : V10_WeakRegimeMaxPositions);
  }


bool V10BuildSellSignal(const MqlRates &rates[], const double emaM5, const double atr, const V10Regime regime, V10Signal &signal)
  {
   if(!V10_EnableSells)
      return(false);
   if(!V10RegimeIsBear(regime))
      return(false);
   int currentHour = V10HourOf(TimeCurrent());
   if(!V10HourInSession(currentHour, V10_SellSessionStartHour, V10_SellSessionEndHour))
      return(false);

   const MqlRates bar = rates[1];
   double bodyRatio = V10BodyRatio(bar);
   if(bar.close >= bar.open)
      return(false);
   if(bodyRatio < V10SellMinBodyRatio(regime))
      return(false);
   if(bar.close >= emaM5)
      return(false);
   if((emaM5 - bar.close) > (atr * V10_MaxStretchATR))
      return(false);
   if(!V10DirectionalHoldOk(true, rates, atr))
      return(false);
   if(!V10HadPullback(true, rates, emaM5))
      return(false);

   int breakoutEnd = MathMin(V10_BreakoutLookback + 1, ArraySize(rates) - 1);
   double priorLow = V10LowestLow(rates, 2, breakoutEnd);
   double minBreakAtr = V10SellMinBreakATR(regime);
   double breakAtr = (priorLow - bar.close) / atr;
   if(bar.close > (priorLow - (atr * minBreakAtr)))
      return(false);

   double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   if(bid <= 0.0)
      return(false);

   bool rejectionSeen = V10BearRejectionSeen(rates, emaM5, atr);
   bool bodyStrong = bodyRatio >= (V10SellMinBodyRatio(regime) + 0.08);
   bool cleanStretch = (emaM5 - bar.close) <= (atr * 0.90);
   bool sessionCore = V10HourInSession(currentHour, 10, 17);
   int score = 40;
   if(V10RegimeIsStrong(regime))
      score += 15;
   else
      score += 8;
   if(rejectionSeen)
      score += 10;
   if(sessionCore)
      score += 10;
   if(bodyStrong)
      score += 10;
   if(breakAtr >= (minBreakAtr + 0.08))
      score += 10;
   if(cleanStretch)
      score += 5;
   if(V10_MinTradeScore > 0 && score < V10_MinTradeScore)
      return(false);

   int stopEnd = MathMin(V10_StopLookbackBars, ArraySize(rates) - 1);
   double swingHigh = V10HighestHigh(rates, 1, stopEnd);
   double stopDistance = V10Clamp((swingHigh - bid) + (atr * V10_StopBufferATR), V10_MinSLUsd, V10_MaxSLUsd);
   double stopLoss = V10NormalizePrice(bid + stopDistance);
   double rr = V10SellRRForRegime(regime);
   bool boosted = score >= V10_ScoreBoostMin;
   if(boosted)
      rr += V10_ScoreRRBonus;
   double takeProfit = V10NormalizePrice(bid - (stopDistance * rr));
   if(!V10StopsValid(true, bid, stopLoss, takeProfit))
      return(false);

   double riskUsd = V10RiskBudgetUsd(true, regime);
   if(boosted)
      riskUsd *= V10_ScoreRiskBonus;
   double lot = V10LotForRisk(true, bid, stopLoss, riskUsd);
   if(lot < SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN))
      return(false);

   signal.valid = true;
   signal.sell = true;
   signal.entry = bid;
   signal.stopLoss = stopLoss;
   signal.takeProfit = takeProfit;
   signal.lot = lot;
   signal.stopDistance = stopDistance;
   signal.rr = rr;
   string tags = V10AppendTag("", V10RegimeIsStrong(regime) ? "RG" : "WG");
   tags = V10AppendTag(tags, rejectionSeen ? "RJ" : "BR");
   tags = V10AppendTag(tags, sessionCore ? "SE" : "XH");
   if(boosted)
      tags = V10AppendTag(tags, "BX");
   string note = StringFormat("SELL score=%d breakATR=%.2f body=%.2f regime=%s rejection=%s session=%02d rr=%.2f",
                              score, breakAtr, bodyRatio, V10RegimeLabel(regime),
                              rejectionSeen ? "yes" : "no", currentHour, rr);
   V10FillSignalMeta(signal, "BE", score, tags, note);
  return(true);
  }


bool V10BuildBullSubSignal(const MqlRates &rates[], const double emaM5, const double atr, const V10Regime regime, V10Signal &signal)
  {
   if(!V10_EnableBullSubEngine)
      return(false);
   bool weakBullAllowed = V10_BullSubAllowWeakBull && regime == V10_REGIME_WEAK_BULL;
   if(regime != V10_REGIME_STRONG_BULL && !weakBullAllowed)
      return(false);

   int currentHour = V10HourOf(TimeCurrent());
   if(!V10HourInSession(currentHour, V10_BullSubSessionStartHour, V10_BullSubSessionEndHour))
      return(false);
   if(V10_BullSubOnlyOutsideCore && V10BuyHourPreferred(currentHour))
      return(false);
   if(V10BuyHourBlocked(currentHour))
      return(false);

   const MqlRates bar = rates[1];
   double bodyRatio = V10BodyRatio(bar);
   if(bar.close <= bar.open)
      return(false);
   if(bodyRatio < V10_BullSubMinBodyRatio)
      return(false);
   if(bar.close <= emaM5)
      return(false);

   int endShift = MathMin(V10_BullSubCompressionBars + 1, ArraySize(rates) - 1);
   if(endShift < 3)
      return(false);
   double boxHigh = V10HighestHigh(rates, 2, endShift);
   double boxLow = V10LowestLow(rates, 2, endShift);
   double boxRange = boxHigh - boxLow;
   if(boxRange <= 0.0 || boxRange > (atr * V10_BullSubMaxRangeATR))
      return(false);
   if(boxLow > (emaM5 + (atr * V10_BullSubTouchEmaATR)))
      return(false);

   for(int shift = 2; shift <= endShift; shift++)
     {
      if(rates[shift].close < (emaM5 - (atr * 0.10)))
         return(false);
     }

   if(bar.close < (boxHigh + (atr * V10_BullSubBreakATR)))
      return(false);

   bool compactBox = boxRange <= (atr * 1.10);
   bool bodyStrong = bodyRatio >= (V10_BullSubMinBodyRatio + 0.08);
   bool tightToEma = boxLow <= (emaM5 + (atr * 0.08));
   int score = 45;
   score += weakBullAllowed ? 8 : 15;
   if(compactBox)
      score += 10;
   if(bodyStrong)
      score += 10;
   if(tightToEma)
      score += 10;
   if(V10_MinTradeScore > 0 && score < V10_MinTradeScore)
      return(false);

   double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   if(ask <= 0.0)
      return(false);

   double stopDistance = V10Clamp((ask - boxLow) + (atr * V10_StopBufferATR), V10_MinSLUsd, V10_MaxSLUsd);
   double stopLoss = V10NormalizePrice(ask - stopDistance);
   double rr = V10_BullSubRR;
   bool boosted = score >= V10_ScoreBoostMin;
   if(boosted)
      rr += V10_ScoreRRBonus;
   double takeProfit = V10NormalizePrice(ask + (stopDistance * rr));
   if(!V10StopsValid(false, ask, stopLoss, takeProfit))
      return(false);

   double riskUsd = V10BuyRiskBudgetUsd(regime, V10_BullSubRiskMultiplier);
   if(boosted)
      riskUsd *= V10_ScoreRiskBonus;
   double lot = V10LotForRisk(false, ask, stopLoss, riskUsd);
   if(lot < SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN))
      return(false);

   signal.valid = true;
   signal.sell = false;
   signal.entry = ask;
   signal.stopLoss = stopLoss;
   signal.takeProfit = takeProfit;
   signal.lot = lot;
   signal.stopDistance = stopDistance;
   signal.rr = rr;
   string tags = V10AppendTag("", weakBullAllowed ? "WG" : "RG");
   tags = V10AppendTag(tags, compactBox ? "CM" : "BX");
   tags = V10AppendTag(tags, tightToEma ? "EM" : "BR");
   if(boosted)
      tags = V10AppendTag(tags, "BX");
   string note = StringFormat("BULL SUB score=%d boxATR=%.2f body=%.2f regime=%s hour=%02d rr=%.2f",
                              score, boxRange / atr, bodyRatio, V10RegimeLabel(regime), currentHour, rr);
   V10FillSignalMeta(signal, "SB", score, tags, note);
   return(true);
  }


bool V10BuildBearSubSignal(const MqlRates &rates[], const double emaM5, const double atr, const V10Regime regime, V10Signal &signal)
  {
   if(!V10_EnableBearSubEngine)
      return(false);
   bool weakBearAllowed = V10_BearSubAllowWeakBear && regime == V10_REGIME_WEAK_BEAR;
   if(regime != V10_REGIME_STRONG_BEAR && !weakBearAllowed)
      return(false);

   int currentHour = V10HourOf(TimeCurrent());
   if(!V10HourInSession(currentHour, V10_BearSubSessionStartHour, V10_BearSubSessionEndHour))
      return(false);

   const MqlRates bar = rates[1];
   double bodyRatio = V10BodyRatio(bar);
   if(bar.close >= bar.open)
      return(false);
   if(bodyRatio < V10_BearSubMinBodyRatio)
      return(false);
   if(bar.close >= emaM5)
      return(false);

   int endShift = MathMin(V10_BearSubCompressionBars + 1, ArraySize(rates) - 1);
   if(endShift < 3)
      return(false);
   double boxHigh = V10HighestHigh(rates, 2, endShift);
   double boxLow = V10LowestLow(rates, 2, endShift);
   double boxRange = boxHigh - boxLow;
   if(boxRange <= 0.0 || boxRange > (atr * V10_BearSubMaxRangeATR))
      return(false);
   if(boxHigh < (emaM5 - (atr * V10_BearSubTouchEmaATR)))
      return(false);

   for(int shift = 2; shift <= endShift; shift++)
     {
      if(rates[shift].close > (emaM5 + (atr * 0.10)))
         return(false);
     }

   if(bar.close > (boxLow - (atr * V10_BearSubBreakATR)))
      return(false);

   bool compactBox = boxRange <= (atr * 1.10);
   bool bodyStrong = bodyRatio >= (V10_BearSubMinBodyRatio + 0.08);
   bool tightToEma = boxHigh >= (emaM5 - (atr * 0.08));
   int score = 45;
   score += weakBearAllowed ? 8 : 15;
   if(compactBox)
      score += 10;
   if(bodyStrong)
      score += 10;
   if(tightToEma)
      score += 10;
   if(V10_MinTradeScore > 0 && score < V10_MinTradeScore)
      return(false);

   double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   if(bid <= 0.0)
      return(false);

   double stopDistance = V10Clamp((boxHigh - bid) + (atr * V10_StopBufferATR), V10_MinSLUsd, V10_MaxSLUsd);
   double stopLoss = V10NormalizePrice(bid + stopDistance);
   double rr = V10_BearSubRR;
   bool boosted = score >= V10_ScoreBoostMin;
   if(boosted)
      rr += V10_ScoreRRBonus;
   double takeProfit = V10NormalizePrice(bid - (stopDistance * rr));
   if(!V10StopsValid(true, bid, stopLoss, takeProfit))
      return(false);

   double riskUsd = V10RiskBudgetUsd(true, regime) * V10_BearSubRiskMultiplier;
   if(boosted)
      riskUsd *= V10_ScoreRiskBonus;
   double lot = V10LotForRisk(true, bid, stopLoss, riskUsd);
   if(lot < SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN))
      return(false);

   signal.valid = true;
   signal.sell = true;
   signal.entry = bid;
   signal.stopLoss = stopLoss;
   signal.takeProfit = takeProfit;
   signal.lot = lot;
   signal.stopDistance = stopDistance;
   signal.rr = rr;
   string tags = V10AppendTag("", weakBearAllowed ? "WG" : "RG");
   tags = V10AppendTag(tags, compactBox ? "CM" : "BX");
   tags = V10AppendTag(tags, tightToEma ? "EM" : "BR");
   if(boosted)
      tags = V10AppendTag(tags, "BX");
   string note = StringFormat("BEAR SUB score=%d boxATR=%.2f body=%.2f regime=%s hour=%02d rr=%.2f",
                              score, boxRange / atr, bodyRatio, V10RegimeLabel(regime), currentHour, rr);
   V10FillSignalMeta(signal, "SS", score, tags, note);
   return(true);
  }


bool V10BuildBuySignal(const MqlRates &rates[], const double emaM5, const double atr, const V10Regime regime, V10Signal &signal)
  {
   if(!V10_EnableBuys)
      return(false);
   if(!V10RegimeIsBull(regime))
      return(false);
   int currentHour = V10HourOf(TimeCurrent());
   bool strongBullExtraSession = (regime == V10_REGIME_STRONG_BULL && V10_StrongBullRelaxBuySession);
   bool strongBullExtraHours = (regime == V10_REGIME_STRONG_BULL && V10_StrongBullRelaxCoreHours);
   bool inCoreHour = V10BuyHourPreferred(currentHour);
   if(!strongBullExtraSession && !V10HourInSession(currentHour, V10_BuySessionStartHour, V10_BuySessionEndHour))
      return(false);
   if(V10_UseBuyCoreHours && !inCoreHour && !strongBullExtraHours)
      return(false);
   if(V10BuyHourBlocked(currentHour))
      return(false);

   const MqlRates bar = rates[1];
   double bodyRatio = V10BodyRatio(bar);
   if(bar.close <= bar.open)
      return(false);
   if(bodyRatio < V10BuyMinBodyRatio(regime))
      return(false);
   if(bar.close <= emaM5)
      return(false);
   if((bar.close - emaM5) > (atr * V10_BullMaxStretchATR))
      return(false);
   if(!V10DirectionalHoldOk(false, rates, atr))
      return(false);
   if(!V10HadPullback(false, rates, emaM5))
      return(false);

   int breakoutEnd = MathMin(V10_BreakoutLookback + 1, ArraySize(rates) - 1);
   double priorHigh = V10HighestHigh(rates, 2, breakoutEnd);
   double minBreakAtr = V10BuyMinBreakATR(regime);
   bool breakoutSetup = V10_AllowBreakoutBuys &&
                        (bar.close >= (priorHigh + (atr * minBreakAtr)));

   const MqlRates prev = rates[2];
   bool pullbackSeen = V10BullPullbackSeen(rates, emaM5, atr);
   bool pullbackSetup = V10_AllowPullbackBuys &&
                        pullbackSeen &&
                        (bar.close >= (prev.high + (atr * V10_BullReclaimATR)));
   if(strongBullExtraHours && !inCoreHour && V10_StrongBullPullbackOnlyOutsideCore)
      breakoutSetup = false;
   if(!breakoutSetup && !pullbackSetup)
      return(false);

   double breakAtr = (bar.close - priorHigh) / atr;
   bool bodyStrong = bodyRatio >= (V10BuyMinBodyRatio(regime) + 0.08);
   bool cleanStretch = (bar.close - emaM5) <= (atr * 0.70);
   int score = 35;
   if(V10RegimeIsStrong(regime))
      score += 15;
   else
      score += 8;
   if(inCoreHour)
      score += 10;
   if(bodyStrong)
      score += 10;
   if(cleanStretch)
      score += 5;
   if(breakoutSetup)
      score += (breakAtr >= (minBreakAtr + 0.08)) ? 15 : 10;
   if(pullbackSetup)
      score += 10;
   if(pullbackSeen)
      score += 10;
   if(V10_MinTradeScore > 0 && score < V10_MinTradeScore)
      return(false);

   double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   if(ask <= 0.0)
      return(false);

   int stopEnd = MathMin(V10_StopLookbackBars, ArraySize(rates) - 1);
   if(pullbackSetup && !breakoutSetup)
      stopEnd = MathMin(MathMax(V10_StopLookbackBars, V10_BullPullbackLookback + 1), ArraySize(rates) - 1);
   double swingLow = V10LowestLow(rates, 1, stopEnd);
   double stopDistance = V10Clamp((ask - swingLow) + (atr * V10_StopBufferATR), V10_MinSLUsd, V10_MaxSLUsd);
   double stopLoss = V10NormalizePrice(ask - stopDistance);
   double rr = V10BuyRRForRegime(regime);
   bool boosted = score >= V10_ScoreBoostMin;
   if(boosted)
      rr += V10_ScoreRRBonus;
   double takeProfit = V10NormalizePrice(ask + (stopDistance * rr));
   if(!V10StopsValid(false, ask, stopLoss, takeProfit))
      return(false);

   double riskUsd = V10BuyRiskBudgetUsd(regime);
   if(boosted)
      riskUsd *= V10_ScoreRiskBonus;
   double lot = V10LotForRisk(false, ask, stopLoss, riskUsd);
   if(lot < SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN))
      return(false);

   signal.valid = true;
   signal.sell = false;
   signal.entry = ask;
   signal.stopLoss = stopLoss;
   signal.takeProfit = takeProfit;
   signal.lot = lot;
   signal.stopDistance = stopDistance;
   signal.rr = rr;
   string engineCode = pullbackSetup && !breakoutSetup ? "PB" : "BO";
   string tags = V10AppendTag("", V10RegimeIsStrong(regime) ? "RG" : "WG");
   tags = V10AppendTag(tags, inCoreHour ? "CH" : "XH");
   tags = V10AppendTag(tags, pullbackSetup ? "RC" : "BR");
   if(boosted)
      tags = V10AppendTag(tags, "BX");
   string note = StringFormat("%s score=%d breakATR=%.2f body=%.2f regime=%s core=%s pullback=%s rr=%.2f",
                              engineCode == "PB" ? "BULL PB" : "BULL BO",
                              score, breakAtr, bodyRatio, V10RegimeLabel(regime),
                              inCoreHour ? "yes" : "no", pullbackSeen ? "yes" : "no", rr);
   V10FillSignalMeta(signal, engineCode, score, tags, note);
   return(true);
  }


bool V10BuildAddOnSignal(const MqlRates &rates[], const double emaM5, const double atr, const V10Regime regime, const bool sell, V10Signal &signal)
  {
   if(!V10_EnableAddOnEngine)
      return(false);
   if(sell && !V10_EnableSellAddOns)
      return(false);
   if(!sell && !V10_EnableBuyAddOns)
      return(false);
   if(sell)
     {
      if(!V10RegimeIsBear(regime) || (!V10RegimeIsStrong(regime) && !V10_AddOnAllowWeakRegime))
         return(false);
     }
   else
     {
      if(!V10RegimeIsBull(regime) || (!V10RegimeIsStrong(regime) && !V10_AddOnAllowWeakRegime))
         return(false);
     }

   if(V10CountOpenAddOnsByType(sell) >= V10_AddOnMaxPerSide)
      return(false);
   if(!V10HasQualifiedLeadPosition(sell, V10_AddOnMinProgressR))
      return(false);

   int currentHour = V10HourOf(TimeCurrent());
   if(sell)
     {
      if(!V10HourInSession(currentHour, V10_SellSessionStartHour, V10_SellSessionEndHour))
         return(false);
     }
   else
     {
      if(!V10HourInSession(currentHour, V10_BuySessionStartHour, V10_BuySessionEndHour))
         return(false);
      if(V10_UseBuyCoreHours && !V10BuyHourPreferred(currentHour))
         return(false);
      if(V10BuyHourBlocked(currentHour))
         return(false);
     }

   const MqlRates bar = rates[1];
   const MqlRates prev = rates[2];
   double bodyRatio = V10BodyRatio(bar);
   if(bodyRatio < V10_AddOnMinBodyRatio)
      return(false);
   if(!V10DirectionalHoldOk(sell, rates, atr))
      return(false);

   if(sell)
     {
      if(bar.close >= bar.open || bar.close >= emaM5)
         return(false);
      if(bar.close > (prev.low - (atr * V10_AddOnBreakATR)))
         return(false);
      double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
      if(bid <= 0.0)
         return(false);
      double triggerHigh = MathMax(bar.high, prev.high);
      double stopDistance = V10Clamp((triggerHigh - bid) + (atr * V10_StopBufferATR), V10_MinSLUsd, V10_MaxSLUsd);
      double stopLoss = V10NormalizePrice(bid + stopDistance);
      double takeProfit = V10NormalizePrice(bid - (stopDistance * V10_AddOnRR));
      if(!V10StopsValid(true, bid, stopLoss, takeProfit))
         return(false);
      double riskUsd = V10RiskBudgetUsd(true, regime) * V10_AddOnRiskMultiplier;
      double lot = V10LotForRisk(true, bid, stopLoss, riskUsd);
      if(lot < SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN))
         return(false);

      signal.valid = true;
      signal.sell = true;
      signal.entry = bid;
      signal.stopLoss = stopLoss;
      signal.takeProfit = takeProfit;
      signal.lot = lot;
      signal.stopDistance = stopDistance;
      signal.rr = V10_AddOnRR;
      string tags = V10AppendTag("", V10RegimeIsStrong(regime) ? "RG" : "WG");
      tags = V10AppendTag(tags, "AD");
      tags = V10AppendTag(tags, "CT");
      string note = StringFormat("SELL ADD score=%d progress>=%.2f body=%.2f regime=%s hour=%02d rr=%.2f",
                                 76, V10_AddOnMinProgressR, bodyRatio, V10RegimeLabel(regime), currentHour, V10_AddOnRR);
      V10FillSignalMeta(signal, "AS", 76, tags, note);
      return(true);
     }

   if(bar.close <= bar.open || bar.close <= emaM5)
      return(false);
   if(bar.close < (prev.high + (atr * V10_AddOnBreakATR)))
      return(false);
   double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   if(ask <= 0.0)
      return(false);
   double triggerLow = MathMin(bar.low, prev.low);
   double stopDistance = V10Clamp((ask - triggerLow) + (atr * V10_StopBufferATR), V10_MinSLUsd, V10_MaxSLUsd);
   double stopLoss = V10NormalizePrice(ask - stopDistance);
   double takeProfit = V10NormalizePrice(ask + (stopDistance * V10_AddOnRR));
   if(!V10StopsValid(false, ask, stopLoss, takeProfit))
      return(false);
   double riskUsd = V10BuyRiskBudgetUsd(regime, V10_AddOnRiskMultiplier);
   double lot = V10LotForRisk(false, ask, stopLoss, riskUsd);
   if(lot < SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN))
      return(false);

   signal.valid = true;
   signal.sell = false;
   signal.entry = ask;
   signal.stopLoss = stopLoss;
   signal.takeProfit = takeProfit;
   signal.lot = lot;
   signal.stopDistance = stopDistance;
   signal.rr = V10_AddOnRR;
   string tags = V10AppendTag("", V10RegimeIsStrong(regime) ? "RG" : "WG");
   tags = V10AppendTag(tags, "AD");
   tags = V10AppendTag(tags, "CT");
   string note = StringFormat("BUY ADD score=%d progress>=%.2f body=%.2f regime=%s hour=%02d rr=%.2f",
                              76, V10_AddOnMinProgressR, bodyRatio, V10RegimeLabel(regime), currentHour, V10_AddOnRR);
   V10FillSignalMeta(signal, "AB", 76, tags, note);
   return(true);
  }


bool V10SubmitSignal(const V10Signal &signal)
  {
   g_trade.SetExpertMagicNumber(V10_MAGIC);
   g_trade.SetDeviationInPoints(20);
   g_trade.SetTypeFillingBySymbol(_Symbol);

   PrintFormat("V10 ENTRY %s engine=%s score=%d grade=%s tags=%s lot=%.2f rr=%.2f sl=%.2f tp=%.2f note=%s",
               signal.sell ? "SELL" : "BUY",
               signal.engineCode,
               signal.score,
               signal.grade,
               signal.tags,
               signal.lot,
               signal.rr,
               signal.stopLoss,
               signal.takeProfit,
               signal.note);

   if(signal.sell)
      return(g_trade.Sell(signal.lot, _Symbol, 0.0, signal.stopLoss, signal.takeProfit, signal.comment));
   return(g_trade.Buy(signal.lot, _Symbol, 0.0, signal.stopLoss, signal.takeProfit, signal.comment));
  }


void V10ManagePositions()
  {
   V10Regime regime = V10DetectRegime();
   double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   if(bid <= 0.0 || ask <= 0.0)
      return;
   double emaM5 = V10IndicatorValue(g_emaM5, 1);
   double atrM5 = V10IndicatorValue(g_atrM5, 1);

   g_trade.SetExpertMagicNumber(V10_MAGIC);
   g_trade.SetDeviationInPoints(20);
   g_trade.SetTypeFillingBySymbol(_Symbol);

   for(int i = PositionsTotal() - 1; i >= 0; i--)
     {
      ulong ticket = PositionGetTicket(i);
      if(ticket == 0 || !PositionSelectByTicket(ticket))
         continue;
      if(PositionGetString(POSITION_SYMBOL) != _Symbol)
         continue;
      if((ulong)PositionGetInteger(POSITION_MAGIC) != V10_MAGIC)
         continue;

      ENUM_POSITION_TYPE type = (ENUM_POSITION_TYPE)PositionGetInteger(POSITION_TYPE);
      string comment = PositionGetString(POSITION_COMMENT);
      double openPrice = PositionGetDouble(POSITION_PRICE_OPEN);
      double stopLoss = PositionGetDouble(POSITION_SL);
      double takeProfit = PositionGetDouble(POSITION_TP);
	      double currentPrice = (type == POSITION_TYPE_BUY) ? bid : ask;
	      double currentVolume = PositionGetDouble(POSITION_VOLUME);
	      double riskDistance = (type == POSITION_TYPE_BUY) ? (openPrice - stopLoss) : (stopLoss - openPrice);
	      if(riskDistance <= 0.0)
	         continue;

	      double favorable = (type == POSITION_TYPE_BUY) ? (currentPrice - openPrice) : (openPrice - currentPrice);
      if(favorable >= (riskDistance * V10_BreakevenR))
        {
         double desiredSl = (type == POSITION_TYPE_BUY)
                            ? V10NormalizePrice(openPrice + V10_BreakevenLockUsd)
                            : V10NormalizePrice(openPrice - V10_BreakevenLockUsd);
         if(V10StopsValid(type == POSITION_TYPE_SELL, openPrice, desiredSl, takeProfit))
           {
            if(type == POSITION_TYPE_BUY && stopLoss < desiredSl)
               g_trade.PositionModify(ticket, desiredSl, takeProfit);
            if(type == POSITION_TYPE_SELL && stopLoss > desiredSl)
	               g_trade.PositionModify(ticket, desiredSl, takeProfit);
	           }
	        }

	      if(V10_EnableTPManager)
	        {
	         double initialVolume = V10InitialVolume(ticket, currentVolume);
	         int tpStage = V10TPStage(ticket);
	         if(tpStage < 1 && favorable >= (riskDistance * V10_TP1R))
	           {
	            bool stageAdvanced = false;
	            double closeVolume = V10PartialCloseVolume(initialVolume, currentVolume);
	            if(closeVolume > 0.0 && closeVolume < currentVolume)
	              {
	               if(g_trade.PositionClosePartial(ticket, closeVolume))
	                  stageAdvanced = true;
	              }
	            else
	              {
	               stageAdvanced = true;
	              }

	            if(stageAdvanced)
	              {
	               if(PositionSelectByTicket(ticket))
	                 {
	                  currentVolume = PositionGetDouble(POSITION_VOLUME);
	                  stopLoss = PositionGetDouble(POSITION_SL);
	                  takeProfit = PositionGetDouble(POSITION_TP);
	                  currentPrice = (type == POSITION_TYPE_BUY) ? SymbolInfoDouble(_Symbol, SYMBOL_BID) : SymbolInfoDouble(_Symbol, SYMBOL_ASK);
	                 }
	               double runnerRr = MathMax(V10_RunnerRR, takeProfit > 0.0 ? MathAbs(takeProfit - openPrice) / riskDistance : V10_RunnerRR);
	               double runnerTp = (type == POSITION_TYPE_BUY)
	                                 ? V10NormalizePrice(openPrice + (riskDistance * runnerRr))
	                                 : V10NormalizePrice(openPrice - (riskDistance * runnerRr));
	               double runnerSl = (type == POSITION_TYPE_BUY)
	                                 ? V10NormalizePrice(MathMax(stopLoss, openPrice + V10_BreakevenLockUsd))
	                                 : V10NormalizePrice(MathMin(stopLoss, openPrice - V10_BreakevenLockUsd));
		               if(V10StopFitsMarket(type, currentPrice, runnerSl) &&
		                  V10TakeProfitFitsMarket(type, currentPrice, runnerTp) &&
		                  V10StopsValid(type == POSITION_TYPE_SELL, openPrice, runnerSl, runnerTp))
		                  g_trade.PositionModify(ticket, runnerSl, runnerTp);
		               V10SetTPStage(ticket, 1);
		               PrintFormat("V10 TP1 %s ticket=%I64u closeVol=%.2f runnerRR=%.2f", comment, ticket, closeVolume, runnerRr);
		               continue;
		              }
		           }

	         if(V10TPStage(ticket) >= 1 && atrM5 > 0.0 && favorable >= (riskDistance * V10_TrailStartR))
	           {
	            if(PositionSelectByTicket(ticket))
	              {
	               stopLoss = PositionGetDouble(POSITION_SL);
	               takeProfit = PositionGetDouble(POSITION_TP);
	               currentPrice = (type == POSITION_TYPE_BUY) ? SymbolInfoDouble(_Symbol, SYMBOL_BID) : SymbolInfoDouble(_Symbol, SYMBOL_ASK);
	              }
	            double trailDistance = atrM5 * V10_TrailATR;
	            double desiredSl = stopLoss;
	            if(type == POSITION_TYPE_BUY)
	               desiredSl = V10NormalizePrice(MathMax(stopLoss, MathMax(openPrice + V10_TrailLockUsd, currentPrice - trailDistance)));
	            else
	               desiredSl = V10NormalizePrice(MathMin(stopLoss, MathMin(openPrice - V10_TrailLockUsd, currentPrice + trailDistance)));
	            if(V10StopFitsMarket(type, currentPrice, desiredSl) &&
	               V10TakeProfitFitsMarket(type, currentPrice, takeProfit) &&
	               ((type == POSITION_TYPE_BUY && desiredSl > stopLoss) || (type == POSITION_TYPE_SELL && desiredSl < stopLoss)))
	               g_trade.PositionModify(ticket, desiredSl, takeProfit);
	           }
	        }

	      int barsHeld = (int)((TimeCurrent() - (datetime)PositionGetInteger(POSITION_TIME)) / PeriodSeconds(V10_EXEC_TF));
	      if(V10_FastFailBuyGuard && type == POSITION_TYPE_BUY && barsHeld <= V10_FastFailBars && emaM5 > 0.0)
	        {
         bool scopeOk = !V10_FastFailPullbackOnly || (StringFind(comment, "|PB|") >= 0);
         double progressR = favorable / riskDistance;
         double failBuffer = (atrM5 > 0.0) ? (atrM5 * V10_HoldBufferATR) : 0.0;
         bool lostTrend = currentPrice <= (emaM5 + failBuffer);
         if(scopeOk && lostTrend && progressR < V10_FastFailMinProgressR && PositionGetDouble(POSITION_PROFIT) < 0.0)
           {
            g_trade.PositionClose(ticket);
            continue;
           }
        }
      bool regimeFlip = V10_CloseOnRegimeFlip &&
                        ((type == POSITION_TYPE_BUY && !V10RegimeIsBull(regime)) ||
                         (type == POSITION_TYPE_SELL && !V10RegimeIsBear(regime)));
      int maxHoldBars = V10_MaxHoldBars;
      if(type == POSITION_TYPE_BUY && StringFind(comment, "|SB|") >= 0)
         maxHoldBars = V10_BullSubMaxHoldBars;
      if(type == POSITION_TYPE_BUY && StringFind(comment, "|AB|") >= 0)
         maxHoldBars = V10_AddOnMaxHoldBars;
      if(type == POSITION_TYPE_SELL && StringFind(comment, "|SS|") >= 0)
         maxHoldBars = V10_BearSubMaxHoldBars;
      if(type == POSITION_TYPE_SELL && StringFind(comment, "|AS|") >= 0)
         maxHoldBars = V10_AddOnMaxHoldBars;
      bool timeExpired = barsHeld >= maxHoldBars;
      bool canTimeClose = !V10_TimeCloseProfitOnly || PositionGetDouble(POSITION_PROFIT) > 0.0;
      if(regimeFlip || (timeExpired && canTimeClose))
         g_trade.PositionClose(ticket);
     }
  }


bool V10EvaluateEntries()
  {
   V10Regime regime = V10DetectRegime();
   if(regime == V10_REGIME_NONE)
      return(false);
   if(!V10SpreadAllowed())
      return(false);
   V10Regime entryRegime = regime;
   if(regime == V10_REGIME_MIXED)
     {
      if(!V10_EnableMixedMomentumEntries)
         return(false);
      entryRegime = V10MixedBiasBull() ? V10_REGIME_WEAK_BULL : V10_REGIME_WEAK_BEAR;
     }
   if(V10CountOpenPositions() >= V10AllowedMaxPositions(entryRegime))
      return(false);

   MqlRates rates[];
   if(!V10CopyRates(rates, 80))
      return(false);

   double atr = V10IndicatorValue(g_atrM5, 1);
   double emaM5 = V10IndicatorValue(g_emaM5, 1);
   if(atr <= 0.0 || emaM5 <= 0.0)
      return(false);

   V10Signal signal;
   signal.valid = false;
   if(V10RegimeIsBear(entryRegime))
     {
      if(V10BuildBearSubSignal(rates, emaM5, atr, entryRegime, signal))
         return(V10SubmitSignal(signal));
      if(V10BuildAddOnSignal(rates, emaM5, atr, entryRegime, true, signal))
         return(V10SubmitSignal(signal));
      if(V10BuildSellSignal(rates, emaM5, atr, entryRegime, signal))
         return(V10SubmitSignal(signal));
     }
   else if(V10RegimeIsBull(entryRegime))
     {
      if(V10BuildBullSubSignal(rates, emaM5, atr, entryRegime, signal))
         return(V10SubmitSignal(signal));
      if(V10BuildAddOnSignal(rates, emaM5, atr, entryRegime, false, signal))
         return(V10SubmitSignal(signal));
      if(V10BuildBuySignal(rates, emaM5, atr, entryRegime, signal))
         return(V10SubmitSignal(signal));
     }

   return(false);
  }


int OnInit()
  {
   if(_Period != V10_EXEC_TF)
     {
      Print("InvictusForward1M15_v10 requires M5.");
      return(INIT_PARAMETERS_INCORRECT);
     }

   V10ClearState();

   g_trade.SetExpertMagicNumber(V10_MAGIC);
   g_trade.SetDeviationInPoints(20);
   g_trade.SetTypeFillingBySymbol(_Symbol);

   g_emaFastH1 = iMA(_Symbol, PERIOD_H1, V10_H1FastEMA, 0, MODE_EMA, PRICE_CLOSE);
   g_emaSlowH1 = iMA(_Symbol, PERIOD_H1, V10_H1SlowEMA, 0, MODE_EMA, PRICE_CLOSE);
   g_emaFastH4 = iMA(_Symbol, PERIOD_H4, V10_H4FastEMA, 0, MODE_EMA, PRICE_CLOSE);
   g_emaSlowH4 = iMA(_Symbol, PERIOD_H4, V10_H4SlowEMA, 0, MODE_EMA, PRICE_CLOSE);
   g_adxH1 = iADX(_Symbol, PERIOD_H1, V10_H1ADXPeriod);
   g_atrH1 = iATR(_Symbol, PERIOD_H1, V10_H1ATRPeriod);
   g_emaM5 = iMA(_Symbol, V10_EXEC_TF, V10_M5TrendEMA, 0, MODE_EMA, PRICE_CLOSE);
   g_atrM5 = iATR(_Symbol, V10_EXEC_TF, V10_M5ATRPeriod);

   if(g_emaFastH1 == INVALID_HANDLE || g_emaSlowH1 == INVALID_HANDLE ||
      g_emaFastH4 == INVALID_HANDLE || g_emaSlowH4 == INVALID_HANDLE ||
      g_adxH1 == INVALID_HANDLE || g_atrH1 == INVALID_HANDLE ||
      g_emaM5 == INVALID_HANDLE || g_atrM5 == INVALID_HANDLE)
     {
      Print("InvictusForward1M15_v10 failed to create indicators.");
      return(INIT_FAILED);
     }

   return(INIT_SUCCEEDED);
  }


void OnDeinit(const int reason)
  {
   V10ClearState();

   if(g_emaFastH1 != INVALID_HANDLE)
      IndicatorRelease(g_emaFastH1);
   if(g_emaSlowH1 != INVALID_HANDLE)
      IndicatorRelease(g_emaSlowH1);
   if(g_emaFastH4 != INVALID_HANDLE)
      IndicatorRelease(g_emaFastH4);
   if(g_emaSlowH4 != INVALID_HANDLE)
      IndicatorRelease(g_emaSlowH4);
   if(g_adxH1 != INVALID_HANDLE)
      IndicatorRelease(g_adxH1);
   if(g_atrH1 != INVALID_HANDLE)
      IndicatorRelease(g_atrH1);
   if(g_emaM5 != INVALID_HANDLE)
      IndicatorRelease(g_emaM5);
   if(g_atrM5 != INVALID_HANDLE)
      IndicatorRelease(g_atrM5);
  }


void OnTick()
  {
   V10ManagePositions();
   if(!V10NewBar())
      return;
   V10EvaluateEntries();
  }
