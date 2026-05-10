#property copyright "OpenAI Codex"
#property version   "1.00"
#property strict
// AcaneM1_v1: optimizable XAUUSD M1 EA rebuilt for MT5 genetic/forward testing.

#include <Trade/Trade.mqh>

input ulong  AC_Magic = 2026051001;
input double AC_RiskPercent = 2.00;
input double AC_CoreRiskMultiplier = 1.00;
input double AC_WeakRiskMultiplier = 0.45;
input double AC_MaxLotCap = 0.06;
input int    AC_MaxPositions = 3;
input int    AC_MaxSameSidePositions = 2;
input int    AC_MinBarsBetweenEntries = 1;
input bool   AC_BlockOppositeDirection = true;
input double AC_MaxSpreadUsd = 0.85;
input int    AC_DeviationPoints = 80;
input bool   AC_EnableBuys = true;
input bool   AC_EnableSells = true;

input bool   AC_EnableDailyGuard = true;
input double AC_DailyMaxLossPct = 5.00;
input double AC_DailyMaxLossUsd = 5.00;
input bool   AC_CloseOnDailyStop = true;
input bool   AC_EnableEquityCircuit = true;
input double AC_MaxEquityDrawdownPct = 19.00;
input bool   AC_CloseOnCircuitStop = true;
input double AC_MaxOpenRiskPct = 12.00;
input double AC_BasketLossStopPct = 10.00;
input int    AC_LossCooldownBars = 8;

input bool   AC_UseSessionFilter = true;
input int    AC_SessionStartHour = 4;
input int    AC_SessionEndHour = 15;
input string AC_BlockEntryHours = "";
input int    AC_HourPreset = 8;
input bool   AC_EnableStructuralPriceGate = true;
input double AC_MinD1CloseForTrading = 2500.00;
input bool   AC_UseH1TrendGuard = true;
input int    AC_H1Fast = 18;
input int    AC_H1Slow = 54;

input int    AC_EMAFast = 9;
input int    AC_EMASlow = 34;
input int    AC_M5Fast = 12;
input int    AC_M5Slow = 36;
input int    AC_M15Fast = 12;
input int    AC_M15Slow = 36;
input int    AC_ATRPeriod = 14;
input int    AC_RSIPeriod = 9;
input int    AC_ADXPeriod = 14;
input int    AC_BBandsPeriod = 20;
input double AC_BBandsDeviation = 2.00;

input bool   AC_EnableTrendPullback = false;
input bool   AC_EnableImpulseContinuation = true;
input bool   AC_EnableCompressionBreakout = true;
input bool   AC_EnableMeanReversion = true;
input int    AC_ImpulseLookback = 6;
input double AC_ImpulseMinBreakATR = 0.06;
input int    AC_BreakLookback = 12;
input int    AC_CompressionLookback = 8;
input double AC_MinATRUsd = 0.22;
input double AC_MaxATRUsd = 6.00;
input double AC_MinBodyRatio = 0.32;
input double AC_StrongBodyRatio = 0.52;
input double AC_MinBreakATR = 0.08;
input double AC_StrongBreakATR = 0.20;
input double AC_CompressionMaxATR = 1.55;
input double AC_PullbackTouchATR = 0.30;
input double AC_MaxEmaDistanceATR = 1.45;
input double AC_TrendADXMin = 16.00;
input double AC_SidewaysADXMax = 18.00;
input double AC_StrongADX = 25.00;
input bool   AC_RequirePullbackMomentum = true;
input int    AC_MinScore = 70;
input int    AC_StrongScore = 100;

input double AC_MinSLUsd = 0.65;
input double AC_MaxSLUsd = 2.00;
input double AC_ATRStopMult = 0.70;
input double AC_StopBufferATR = 0.12;
input double AC_TrendRR = 1.15;
input double AC_ImpulseRR = 0.95;
input double AC_BreakoutRR = 1.35;
input double AC_MeanReversionRR = 0.82;
input double AC_MeanReversionRSILow = 31.00;
input double AC_MeanReversionRSIHigh = 69.00;
input double AC_MeanReversionTouchATR = 0.14;
input double AC_BreakevenR = 0.50;
input double AC_BreakevenLockUsd = 0.05;
input double AC_TrailStartR = 0.80;
input double AC_TrailATR = 0.45;
input int    AC_MaxHoldBars = 14;
input int    AC_WeakMaxHoldBars = 8;
input bool   AC_CloseOnRegimeFlip = false;

input int    AC_TesterMinTrades = 250;
input double AC_TesterMaxDDPct = 20.00;
input bool   AC_LogEntries = true;
input bool   AC_LogStatus = false;
input int    AC_StatusEveryBars = 30;

static const ENUM_TIMEFRAMES AC_TF = PERIOD_M1;

enum AcaneRegime
  {
   AC_SIDEWAYS = 0,
   AC_BULL = 1,
   AC_BEAR = -1
  };

struct AcaneSignal
  {
   bool valid;
   bool sell;
   int score;
   string engine;
   string tags;
   double stopDistance;
   double rr;
   double riskMultiplier;
   string comment;
  };

CTrade g_trade;
int g_emaFast = INVALID_HANDLE;
int g_emaSlow = INVALID_HANDLE;
int g_m5Fast = INVALID_HANDLE;
int g_m5Slow = INVALID_HANDLE;
int g_m15Fast = INVALID_HANDLE;
int g_m15Slow = INVALID_HANDLE;
int g_h1Fast = INVALID_HANDLE;
int g_h1Slow = INVALID_HANDLE;
int g_atr = INVALID_HANDLE;
int g_rsi = INVALID_HANDLE;
int g_adx = INVALID_HANDLE;
int g_bands = INVALID_HANDLE;
datetime g_lastBarTime = 0;
datetime g_lastEntryBarTime = 0;
datetime g_cooldownUntilBar = 0;
int g_dayKey = -1;
double g_dayStartEquity = 0.0;
double g_dayHighEquity = 0.0;
bool g_dailyStopped = false;
double g_accountHighEquity = 0.0;
bool g_circuitStopped = false;
int g_lastStatusBars = 0;

double AcaneNormalizePrice(const double price)
  {
   return(NormalizeDouble(price, (int)SymbolInfoInteger(_Symbol, SYMBOL_DIGITS)));
  }

bool AcaneCopyValue(const int handle, const int buffer, const int shift, double &value)
  {
   double data[];
   ArraySetAsSeries(data, true);
   if(CopyBuffer(handle, buffer, shift, 1, data) != 1)
      return(false);
   value = data[0];
   return(true);
  }

bool AcaneLoadRates(MqlRates &rates[], const int count)
  {
   ArraySetAsSeries(rates, true);
   return(CopyRates(_Symbol, AC_TF, 0, count, rates) == count);
  }

int AcaneDayKey(const datetime ts)
  {
   MqlDateTime dt;
   TimeToStruct(ts, dt);
   return(dt.year * 1000 + dt.day_of_year);
  }

double AcaneSpread()
  {
   MqlTick tick;
   if(!SymbolInfoTick(_Symbol, tick) || tick.ask <= 0.0 || tick.bid <= 0.0)
      return(999.0);
   return(tick.ask - tick.bid);
  }

bool AcaneMarketOpenLikely()
  {
   MqlDateTime dt;
   TimeToStruct(TimeCurrent(), dt);
   if(dt.day_of_week == 6)
      return(false);
   if(dt.day_of_week == 0 && dt.hour < 23)
      return(false);
   if(dt.day_of_week == 5 && dt.hour >= 21)
      return(false);
   long mode = SymbolInfoInteger(_Symbol, SYMBOL_TRADE_MODE);
   return(mode == SYMBOL_TRADE_MODE_FULL ||
          mode == SYMBOL_TRADE_MODE_LONGONLY ||
          mode == SYMBOL_TRADE_MODE_SHORTONLY);
  }

double AcaneMinStopDistance()
  {
   long stopLevel = SymbolInfoInteger(_Symbol, SYMBOL_TRADE_STOPS_LEVEL);
   long freezeLevel = SymbolInfoInteger(_Symbol, SYMBOL_TRADE_FREEZE_LEVEL);
   return((double)MathMax(stopLevel, freezeLevel) * _Point);
  }

bool AcaneHourAllowed()
  {
   MqlDateTime dt;
   TimeToStruct(TimeCurrent(), dt);
   string hours = AC_BlockEntryHours;
   StringReplace(hours, " ", "");
   StringReplace(hours, ";", ",");
   if(StringLen(hours) > 0)
     {
      string wrapped = "," + hours + ",";
      string plainHour = "," + IntegerToString(dt.hour) + ",";
      string paddedHour = "," + StringFormat("%02d", dt.hour) + ",";
      if(StringFind(wrapped, plainHour) >= 0 || StringFind(wrapped, paddedHour) >= 0)
         return(false);
     }
   bool sessionAllowed = true;
   if(AC_SessionStartHour == AC_SessionEndHour)
      sessionAllowed = true;
   else if(AC_UseSessionFilter && AC_SessionStartHour < AC_SessionEndHour)
      sessionAllowed = (dt.hour >= AC_SessionStartHour && dt.hour < AC_SessionEndHour);
   else if(AC_UseSessionFilter)
      sessionAllowed = (dt.hour >= AC_SessionStartHour || dt.hour < AC_SessionEndHour);
   if(!sessionAllowed)
      return(false);

   switch(AC_HourPreset)
     {
      case 1:
         return(dt.hour >= 4 && dt.hour <= 10 && dt.hour != 6);
      case 2:
         return(dt.hour == 5 || dt.hour == 7 || dt.hour == 10);
      case 3:
         return(dt.hour == 5 || dt.hour == 7 || dt.hour == 9 || dt.hour == 10);
      case 4:
         return(dt.hour == 4 || dt.hour == 5 || dt.hour == 7 || dt.hour == 9 || dt.hour == 10 || dt.hour == 11);
      case 5:
         return(dt.hour >= 5 && dt.hour <= 10 && dt.hour != 6);
      case 6:
         return(dt.hour >= 7 && dt.hour <= 10);
      case 7:
         return(dt.hour >= 9 && dt.hour <= 12);
      case 8:
         return(dt.hour == 5);
      case 9:
         return(dt.hour == 5 || dt.hour == 9);
      default:
         return(true);
     }
  }

bool AcaneStructuralPriceAllowed()
  {
   if(!AC_EnableStructuralPriceGate)
      return(true);
   double close = iClose(_Symbol, PERIOD_D1, 1);
   if(close <= 0.0)
      return(false);
   return(close >= AC_MinD1CloseForTrading);
  }

int AcaneVolumePrecision()
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

double AcaneFloorVolume(const double volume)
  {
   double step = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);
   double minLot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
   double maxLot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX);
   if(step <= 0.0 || volume <= 0.0)
      return(0.0);
   double clipped = MathMin(maxLot, volume);
   if(AC_MaxLotCap > 0.0)
      clipped = MathMin(clipped, AC_MaxLotCap);
   double steps = MathFloor(clipped / step + 1e-9);
   double normalized = NormalizeDouble(steps * step, AcaneVolumePrecision());
   if(normalized < minLot)
      return(0.0);
   return(normalized);
  }

double AcaneValuePerPriceUnit()
  {
   double tickSize = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);
   double tickValue = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE);
   if(tickSize > 0.0 && tickValue > 0.0)
      return(tickValue / tickSize);
   double contract = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_CONTRACT_SIZE);
   return(contract > 0.0 ? contract : 100.0);
  }

double AcaneLotForRisk(const double stopDistance, const double riskMultiplier)
  {
   double equity = AccountInfoDouble(ACCOUNT_EQUITY);
   if(stopDistance <= 0.0 || equity <= 0.0 || riskMultiplier <= 0.0)
      return(0.0);
   double riskCash = equity * AC_RiskPercent / 100.0 * riskMultiplier;
   double valuePerPrice = AcaneValuePerPriceUnit();
   double raw = riskCash / (stopDistance * valuePerPrice);
   double lot = AcaneFloorVolume(raw);
   if(lot > 0.0)
      return(lot);
   double minLot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
   double minLotRiskPct = stopDistance * valuePerPrice * minLot / equity * 100.0;
   if(minLotRiskPct <= AC_MaxOpenRiskPct * 0.75)
      return(AcaneFloorVolume(minLot));
   return(0.0);
  }

int AcaneCountPositions(const int side = 0)
  {
   int count = 0;
   for(int i = PositionsTotal() - 1; i >= 0; i--)
     {
      ulong ticket = PositionGetTicket(i);
      if(ticket == 0 || !PositionSelectByTicket(ticket))
         continue;
      if(PositionGetString(POSITION_SYMBOL) != _Symbol)
         continue;
      if((ulong)PositionGetInteger(POSITION_MAGIC) != AC_Magic)
         continue;
      ENUM_POSITION_TYPE type = (ENUM_POSITION_TYPE)PositionGetInteger(POSITION_TYPE);
      if(side == 1 && type != POSITION_TYPE_BUY)
         continue;
      if(side == -1 && type != POSITION_TYPE_SELL)
         continue;
      count++;
     }
   return(count);
  }

double AcaneOwnFloatingProfit()
  {
   double profit = 0.0;
   for(int i = PositionsTotal() - 1; i >= 0; i--)
     {
      ulong ticket = PositionGetTicket(i);
      if(ticket == 0 || !PositionSelectByTicket(ticket))
         continue;
      if(PositionGetString(POSITION_SYMBOL) != _Symbol)
         continue;
      if((ulong)PositionGetInteger(POSITION_MAGIC) != AC_Magic)
         continue;
      profit += PositionGetDouble(POSITION_PROFIT) + PositionGetDouble(POSITION_SWAP);
     }
   return(profit);
  }

double AcaneOpenRiskCash()
  {
   double risk = 0.0;
   double valuePerPrice = AcaneValuePerPriceUnit();
   for(int i = PositionsTotal() - 1; i >= 0; i--)
     {
      ulong ticket = PositionGetTicket(i);
      if(ticket == 0 || !PositionSelectByTicket(ticket))
         continue;
      if(PositionGetString(POSITION_SYMBOL) != _Symbol)
         continue;
      if((ulong)PositionGetInteger(POSITION_MAGIC) != AC_Magic)
         continue;
      double open = PositionGetDouble(POSITION_PRICE_OPEN);
      double sl = PositionGetDouble(POSITION_SL);
      double volume = PositionGetDouble(POSITION_VOLUME);
      double distance = MathAbs(open - sl);
      if(distance <= 0.0)
         distance = AC_MinSLUsd;
      risk += distance * valuePerPrice * volume;
     }
   return(risk);
  }

void AcaneCloseOwnPositions(const string reason)
  {
   if(!AcaneMarketOpenLikely())
      return;
   g_trade.SetExpertMagicNumber(AC_Magic);
   g_trade.SetDeviationInPoints(AC_DeviationPoints);
   g_trade.SetTypeFillingBySymbol(_Symbol);
   for(int i = PositionsTotal() - 1; i >= 0; i--)
     {
      ulong ticket = PositionGetTicket(i);
      if(ticket == 0 || !PositionSelectByTicket(ticket))
         continue;
      if(PositionGetString(POSITION_SYMBOL) != _Symbol)
         continue;
      if((ulong)PositionGetInteger(POSITION_MAGIC) != AC_Magic)
         continue;
      if(g_trade.PositionClose(ticket) && AC_LogEntries)
         PrintFormat("ACANE EXIT GUARD | ticket=%I64u reason=%s", ticket, reason);
     }
  }

void AcaneResetDailyGuardIfNeeded()
  {
   int key = AcaneDayKey(TimeCurrent());
   if(key == g_dayKey)
      return;
   g_dayKey = key;
   g_dayStartEquity = AccountInfoDouble(ACCOUNT_EQUITY);
   g_dayHighEquity = g_dayStartEquity;
   g_accountHighEquity = g_dayStartEquity;
   g_dailyStopped = false;
   g_circuitStopped = false;
  }

bool AcaneRiskAllowsTrading()
  {
   AcaneResetDailyGuardIfNeeded();
   double equity = AccountInfoDouble(ACCOUNT_EQUITY);
   if(equity <= 0.0)
      return(false);
   if(g_accountHighEquity <= 0.0)
      g_accountHighEquity = equity;
   g_accountHighEquity = MathMax(g_accountHighEquity, equity);
   g_dayHighEquity = MathMax(g_dayHighEquity, equity);

   if(!AcaneStructuralPriceAllowed())
      return(false);

   if(AC_EnableDailyGuard && !g_dailyStopped && g_dayStartEquity > 0.0)
     {
      double lossCash = g_dayStartEquity - equity;
      double lossPct = lossCash / g_dayStartEquity * 100.0;
      if(lossPct >= AC_DailyMaxLossPct || (AC_DailyMaxLossUsd > 0.0 && lossCash >= AC_DailyMaxLossUsd))
        {
         g_dailyStopped = true;
         if(AC_CloseOnDailyStop)
            AcaneCloseOwnPositions("daily stop");
        }
     }
   if(g_dailyStopped)
      return(false);

   if(AC_EnableEquityCircuit && !g_circuitStopped && g_accountHighEquity > 0.0)
     {
      double ddPct = (g_accountHighEquity - equity) / g_accountHighEquity * 100.0;
      if(ddPct >= AC_MaxEquityDrawdownPct)
        {
         g_circuitStopped = true;
         if(AC_CloseOnCircuitStop)
            AcaneCloseOwnPositions("equity circuit");
        }
     }
   if(g_circuitStopped)
      return(false);

   if(AcaneOwnFloatingProfit() < 0.0 && -AcaneOwnFloatingProfit() / equity * 100.0 >= AC_BasketLossStopPct)
     {
      g_cooldownUntilBar = iTime(_Symbol, AC_TF, 0) + PeriodSeconds(AC_TF) * AC_LossCooldownBars;
      AcaneCloseOwnPositions("basket stop");
      return(false);
     }

   if(AcaneOpenRiskCash() / equity * 100.0 >= AC_MaxOpenRiskPct)
      return(false);

   return(true);
  }

double AcaneBodyRatio(const MqlRates &bar)
  {
   double range = bar.high - bar.low;
   if(range <= 0.0)
      return(0.0);
   return(MathAbs(bar.close - bar.open) / range);
  }

double AcaneHighestHigh(const MqlRates &rates[], const int fromShift, const int count)
  {
   double value = rates[fromShift].high;
   for(int i = fromShift + 1; i < fromShift + count; i++)
      value = MathMax(value, rates[i].high);
   return(value);
  }

double AcaneLowestLow(const MqlRates &rates[], const int fromShift, const int count)
  {
   double value = rates[fromShift].low;
   for(int i = fromShift + 1; i < fromShift + count; i++)
      value = MathMin(value, rates[i].low);
   return(value);
  }

double AcaneRange(const MqlRates &rates[], const int fromShift, const int count)
  {
   return(AcaneHighestHigh(rates, fromShift, count) - AcaneLowestLow(rates, fromShift, count));
  }

AcaneRegime AcaneDetectRegime()
  {
   double f1, s1, f5, s5, f15, s15, adx;
   if(!AcaneCopyValue(g_emaFast, 0, 1, f1) ||
      !AcaneCopyValue(g_emaSlow, 0, 1, s1) ||
      !AcaneCopyValue(g_m5Fast, 0, 1, f5) ||
      !AcaneCopyValue(g_m5Slow, 0, 1, s5) ||
      !AcaneCopyValue(g_m15Fast, 0, 1, f15) ||
      !AcaneCopyValue(g_m15Slow, 0, 1, s15) ||
      !AcaneCopyValue(g_adx, 0, 1, adx))
      return(AC_SIDEWAYS);

   if(adx >= AC_TrendADXMin && f1 > s1 && f5 >= s5 && f15 >= s15)
      return(AC_BULL);
   if(adx >= AC_TrendADXMin && f1 < s1 && f5 <= s5 && f15 <= s15)
      return(AC_BEAR);
   return(AC_SIDEWAYS);
  }

bool AcaneH1Allows(const bool sell)
  {
   if(!AC_UseH1TrendGuard)
      return(true);
   double fast, slow;
   if(!AcaneCopyValue(g_h1Fast, 0, 1, fast) ||
      !AcaneCopyValue(g_h1Slow, 0, 1, slow))
      return(false);
   if(sell)
      return(fast <= slow);
   return(fast >= slow);
  }

string AcaneComment(const string engine, const int score, const string tags)
  {
   string grade = score >= AC_StrongScore ? "A" : "B";
   string comment = "AC1|" + engine + "|S" + IntegerToString(score) + "|" + grade;
   if(tags != "")
      comment += "|" + tags;
   if(StringLen(comment) > 31)
      comment = StringSubstr(comment, 0, 31);
   return(comment);
  }

void AcaneMaybeSetSignal(AcaneSignal &best,
                         const bool sell,
                         const int score,
                         const string engine,
                         const string tags,
                         const double stopDistance,
                         const double rr,
                         const double riskMultiplier)
  {
   if(score < AC_MinScore)
      return;
   if(best.valid && score <= best.score)
      return;
   best.valid = true;
   best.sell = sell;
   best.score = score;
   best.engine = engine;
   best.tags = tags;
   best.stopDistance = stopDistance;
   best.rr = rr;
   best.riskMultiplier = riskMultiplier;
   best.comment = AcaneComment(engine, score, tags);
  }

AcaneSignal AcaneBuildSignal()
  {
   AcaneSignal best;
   best.valid = false;
   best.sell = false;
   best.score = 0;
   best.engine = "";
   best.tags = "";
   best.stopDistance = 0.0;
   best.rr = AC_TrendRR;
   best.riskMultiplier = AC_WeakRiskMultiplier;
   best.comment = "";

   if(!AcaneHourAllowed())
      return(best);

   int barsNeeded = MathMax(MathMax(AC_BreakLookback + 8, AC_CompressionLookback + 8), AC_ImpulseLookback + 8);
   MqlRates rates[];
   if(!AcaneLoadRates(rates, barsNeeded))
      return(best);

   double emaFast, emaSlow, emaFastPrev, atr, rsi, adx, bandMid, bandUpper, bandLower;
   if(!AcaneCopyValue(g_emaFast, 0, 1, emaFast) ||
      !AcaneCopyValue(g_emaSlow, 0, 1, emaSlow) ||
      !AcaneCopyValue(g_emaFast, 0, 4, emaFastPrev) ||
      !AcaneCopyValue(g_atr, 0, 1, atr) ||
      !AcaneCopyValue(g_rsi, 0, 1, rsi) ||
      !AcaneCopyValue(g_adx, 0, 1, adx) ||
      !AcaneCopyValue(g_bands, 0, 1, bandMid) ||
      !AcaneCopyValue(g_bands, 1, 1, bandUpper) ||
      !AcaneCopyValue(g_bands, 2, 1, bandLower))
      return(best);

   if(atr < AC_MinATRUsd || atr > AC_MaxATRUsd)
      return(best);

   AcaneRegime regime = AcaneDetectRegime();
   MqlRates bar = rates[1];
   double close = bar.close;
   double open = bar.open;
   double body = AcaneBodyRatio(bar);
   double prevHigh = AcaneHighestHigh(rates, 2, AC_BreakLookback);
   double prevLow = AcaneLowestLow(rates, 2, AC_BreakLookback);
   double compression = AcaneRange(rates, 2, AC_CompressionLookback) / atr;
   double breakUp = (close - prevHigh) / atr;
   double breakDown = (prevLow - close) / atr;
   double emaDistance = MathAbs(close - emaSlow) / atr;
   double emaSlope = (emaFast - emaFastPrev) / atr;
   double spread = AcaneSpread();
   double stopDistance = MathMax(AC_MinSLUsd, MathMin(AC_MaxSLUsd, atr * AC_ATRStopMult + atr * AC_StopBufferATR));
   stopDistance = MathMax(stopDistance, AcaneMinStopDistance() + spread + _Point);
   bool narrowSpread = spread <= AC_MaxSpreadUsd * 0.72;
   bool strongBody = body >= AC_StrongBodyRatio;
   bool bodyOk = body >= AC_MinBodyRatio;
   int base = 42 + (narrowSpread ? 5 : 0) + (bodyOk ? 7 : 0) + (strongBody ? 6 : 0);
   if(adx >= AC_StrongADX)
      base += 5;

   if(AC_EnableImpulseContinuation)
     {
      double impulseHigh = AcaneHighestHigh(rates, 2, AC_ImpulseLookback);
      double impulseLow = AcaneLowestLow(rates, 2, AC_ImpulseLookback);
      double impulseUp = (close - impulseHigh) / atr;
      double impulseDown = (impulseLow - close) / atr;
      bool buyImpulse = AC_EnableBuys &&
                        regime == AC_BULL &&
                        AcaneH1Allows(false) &&
                        close > impulseHigh &&
                        impulseUp >= AC_ImpulseMinBreakATR &&
                        close > open &&
                        bodyOk &&
                        rsi >= 50.0 && rsi <= 78.0 &&
                        emaSlope > 0.0;
      int buyScore = base + (buyImpulse ? 20 : 0) + (strongBody ? 6 : 0) + (impulseUp >= AC_StrongBreakATR ? 7 : 0);
      if(buyImpulse)
         AcaneMaybeSetSignal(best, false, buyScore, "IMP", "BULL", stopDistance, AC_ImpulseRR,
                             buyScore >= AC_StrongScore ? AC_CoreRiskMultiplier : AC_WeakRiskMultiplier);

      bool sellImpulse = AC_EnableSells &&
                         regime == AC_BEAR &&
                         AcaneH1Allows(true) &&
                         close < impulseLow &&
                         impulseDown >= AC_ImpulseMinBreakATR &&
                         close < open &&
                         bodyOk &&
                         rsi <= 50.0 && rsi >= 22.0 &&
                         emaSlope < 0.0;
      int sellScore = base + (sellImpulse ? 20 : 0) + (strongBody ? 6 : 0) + (impulseDown >= AC_StrongBreakATR ? 7 : 0);
      if(sellImpulse)
         AcaneMaybeSetSignal(best, true, sellScore, "IMP", "BEAR", stopDistance, AC_ImpulseRR,
                             sellScore >= AC_StrongScore ? AC_CoreRiskMultiplier : AC_WeakRiskMultiplier);
     }

   if(AC_EnableTrendPullback)
     {
      bool buyPull = AC_EnableBuys &&
                     regime == AC_BULL &&
                     AcaneH1Allows(false) &&
                     rates[1].low <= emaFast + atr * AC_PullbackTouchATR &&
                     close > emaFast &&
                     close > open &&
                     (!AC_RequirePullbackMomentum || (bodyOk && close > rates[2].close)) &&
                     rsi >= 42.0 && rsi <= 72.0 &&
                     emaDistance <= AC_MaxEmaDistanceATR &&
                     emaSlope >= -0.03;
      int buyScore = base + (buyPull ? 20 : 0) + (adx >= AC_TrendADXMin ? 8 : 0) + (close > rates[2].close ? 4 : 0);
      if(buyPull)
         AcaneMaybeSetSignal(best, false, buyScore, "TPL", "BULL", stopDistance, AC_TrendRR,
                             buyScore >= AC_StrongScore ? AC_CoreRiskMultiplier : AC_WeakRiskMultiplier);

      bool sellPull = AC_EnableSells &&
                      regime == AC_BEAR &&
                      AcaneH1Allows(true) &&
                      rates[1].high >= emaFast - atr * AC_PullbackTouchATR &&
                      close < emaFast &&
                      close < open &&
                      (!AC_RequirePullbackMomentum || (bodyOk && close < rates[2].close)) &&
                      rsi <= 58.0 && rsi >= 28.0 &&
                      emaDistance <= AC_MaxEmaDistanceATR &&
                      emaSlope <= 0.03;
      int sellScore = base + (sellPull ? 20 : 0) + (adx >= AC_TrendADXMin ? 8 : 0) + (close < rates[2].close ? 4 : 0);
      if(sellPull)
         AcaneMaybeSetSignal(best, true, sellScore, "TPL", "BEAR", stopDistance, AC_TrendRR,
                             sellScore >= AC_StrongScore ? AC_CoreRiskMultiplier : AC_WeakRiskMultiplier);
     }

   if(AC_EnableCompressionBreakout && compression <= AC_CompressionMaxATR)
     {
      bool buyBreak = AC_EnableBuys &&
                      regime != AC_BEAR &&
                      AcaneH1Allows(false) &&
                      close > prevHigh &&
                      breakUp >= AC_MinBreakATR &&
                      close > open &&
                      rsi >= 50.0 && rsi <= 78.0;
      int buyScore = base + (buyBreak ? 18 : 0) + (regime == AC_BULL ? 8 : 2) +
                     (breakUp >= AC_StrongBreakATR ? 7 : 0);
      if(buyBreak)
         AcaneMaybeSetSignal(best, false, buyScore, "CBK", regime == AC_BULL ? "RG" : "WG",
                             stopDistance, AC_BreakoutRR,
                             buyScore >= AC_StrongScore ? AC_CoreRiskMultiplier : AC_WeakRiskMultiplier);

      bool sellBreak = AC_EnableSells &&
                       regime != AC_BULL &&
                       AcaneH1Allows(true) &&
                       close < prevLow &&
                       breakDown >= AC_MinBreakATR &&
                       close < open &&
                       rsi <= 50.0 && rsi >= 22.0;
      int sellScore = base + (sellBreak ? 18 : 0) + (regime == AC_BEAR ? 8 : 2) +
                      (breakDown >= AC_StrongBreakATR ? 7 : 0);
      if(sellBreak)
         AcaneMaybeSetSignal(best, true, sellScore, "CBK", regime == AC_BEAR ? "RG" : "WG",
                             stopDistance, AC_BreakoutRR,
                             sellScore >= AC_StrongScore ? AC_CoreRiskMultiplier : AC_WeakRiskMultiplier);
     }

   if(AC_EnableMeanReversion && adx <= AC_SidewaysADXMax)
     {
      bool buyReversal = AC_EnableBuys &&
                         rates[1].low <= bandLower - atr * AC_MeanReversionTouchATR &&
                         close > bandLower &&
                         close > open &&
                         rsi <= AC_MeanReversionRSILow &&
                         regime != AC_BEAR;
      int buyScore = 50 + (buyReversal ? 20 : 0) + (bodyOk ? 6 : 0) + (narrowSpread ? 4 : 0);
      if(buyReversal)
         AcaneMaybeSetSignal(best, false, buyScore, "MRV", "BB", stopDistance,
                             AC_MeanReversionRR, AC_WeakRiskMultiplier);

      bool sellReversal = AC_EnableSells &&
                          rates[1].high >= bandUpper + atr * AC_MeanReversionTouchATR &&
                          close < bandUpper &&
                          close < open &&
                          rsi >= AC_MeanReversionRSIHigh &&
                          regime != AC_BULL;
      int sellScore = 50 + (sellReversal ? 20 : 0) + (bodyOk ? 6 : 0) + (narrowSpread ? 4 : 0);
      if(sellReversal)
         AcaneMaybeSetSignal(best, true, sellScore, "MRV", "BB", stopDistance,
                             AC_MeanReversionRR, AC_WeakRiskMultiplier);
     }

   return(best);
  }

bool AcaneStopFits(const bool sell, const double price, const double sl)
  {
   double minDistance = AcaneMinStopDistance();
   if(sell)
      return(sl > price + minDistance);
   return(sl < price - minDistance);
  }

bool AcaneTakeProfitFits(const bool sell, const double price, const double tp)
  {
   double minDistance = AcaneMinStopDistance();
   if(sell)
      return(tp < price - minDistance);
   return(tp > price + minDistance);
  }

void AcaneTryEntry()
  {
   if(!AcaneRiskAllowsTrading())
      return;
   if(!AcaneMarketOpenLikely())
      return;
   if(AcaneSpread() > AC_MaxSpreadUsd)
      return;
   if(g_cooldownUntilBar > 0 && iTime(_Symbol, AC_TF, 0) < g_cooldownUntilBar)
      return;
   if(AcaneCountPositions() >= AC_MaxPositions)
      return;
   if(g_lastEntryBarTime > 0)
     {
      int seconds = (int)(iTime(_Symbol, AC_TF, 0) - g_lastEntryBarTime);
      if(seconds < PeriodSeconds(AC_TF) * AC_MinBarsBetweenEntries)
         return;
     }

   AcaneSignal signal = AcaneBuildSignal();
   if(!signal.valid)
      return;
   if(AC_BlockOppositeDirection && AcaneCountPositions(signal.sell ? 1 : -1) > 0)
      return;
   if(AcaneCountPositions(signal.sell ? -1 : 1) >= AC_MaxSameSidePositions)
      return;

   double lot = AcaneLotForRisk(signal.stopDistance, signal.riskMultiplier);
   if(lot <= 0.0)
      return;

   double equity = AccountInfoDouble(ACCOUNT_EQUITY);
   double addedRiskPct = signal.stopDistance * AcaneValuePerPriceUnit() * lot / equity * 100.0;
   if(addedRiskPct + AcaneOpenRiskCash() / equity * 100.0 > AC_MaxOpenRiskPct)
      return;

   MqlTick tick;
   if(!SymbolInfoTick(_Symbol, tick))
      return;
   double price = signal.sell ? tick.bid : tick.ask;
   double tpDistance = signal.stopDistance * signal.rr;
   double sl = signal.sell ? price + signal.stopDistance : price - signal.stopDistance;
   double tp = signal.sell ? price - tpDistance : price + tpDistance;
   sl = AcaneNormalizePrice(sl);
   tp = AcaneNormalizePrice(tp);
   if(!AcaneStopFits(signal.sell, price, sl) || !AcaneTakeProfitFits(signal.sell, price, tp))
      return;

   g_trade.SetExpertMagicNumber(AC_Magic);
   g_trade.SetDeviationInPoints(AC_DeviationPoints);
   g_trade.SetTypeFillingBySymbol(_Symbol);
   bool ok = signal.sell ? g_trade.Sell(lot, _Symbol, 0.0, sl, tp, signal.comment)
                         : g_trade.Buy(lot, _Symbol, 0.0, sl, tp, signal.comment);
   if(ok)
     {
      g_lastEntryBarTime = iTime(_Symbol, AC_TF, 0);
      if(AC_LogEntries)
         PrintFormat("ACANE ENTRY %s | %s score=%d lot=%.2f sl=%.2f tp=%.2f spread=%.2f",
                     signal.sell ? "SELL" : "BUY", signal.engine, signal.score, lot, sl, tp, AcaneSpread());
     }
  }

void AcaneManagePositions()
  {
   if(!AcaneMarketOpenLikely())
      return;
   g_trade.SetExpertMagicNumber(AC_Magic);
   g_trade.SetDeviationInPoints(AC_DeviationPoints);
   g_trade.SetTypeFillingBySymbol(_Symbol);

   double atr;
   if(!AcaneCopyValue(g_atr, 0, 1, atr))
      atr = AC_MinATRUsd;
   atr = MathMax(atr, AC_MinATRUsd);
   AcaneRegime regime = AcaneDetectRegime();

   for(int i = PositionsTotal() - 1; i >= 0; i--)
     {
      ulong ticket = PositionGetTicket(i);
      if(ticket == 0 || !PositionSelectByTicket(ticket))
         continue;
      if(PositionGetString(POSITION_SYMBOL) != _Symbol)
         continue;
      if((ulong)PositionGetInteger(POSITION_MAGIC) != AC_Magic)
         continue;

      ENUM_POSITION_TYPE type = (ENUM_POSITION_TYPE)PositionGetInteger(POSITION_TYPE);
      bool sell = type == POSITION_TYPE_SELL;
      double open = PositionGetDouble(POSITION_PRICE_OPEN);
      double sl = PositionGetDouble(POSITION_SL);
      double tp = PositionGetDouble(POSITION_TP);
      double current = sell ? SymbolInfoDouble(_Symbol, SYMBOL_ASK) : SymbolInfoDouble(_Symbol, SYMBOL_BID);
      double progress = sell ? open - current : current - open;
      double risk = MathAbs(open - sl);
      if(risk <= 0.0)
         risk = AC_MinSLUsd;
      double progressR = progress / risk;
      datetime openTime = (datetime)PositionGetInteger(POSITION_TIME);
      int heldBars = (int)MathFloor((TimeCurrent() - openTime) / PeriodSeconds(AC_TF));
      string comment = PositionGetString(POSITION_COMMENT);
      int maxHold = StringFind(comment, "|A") >= 0 ? AC_MaxHoldBars : AC_WeakMaxHoldBars;

      if(AC_CloseOnRegimeFlip && ((sell && regime == AC_BULL) || (!sell && regime == AC_BEAR)) && heldBars >= 2)
        {
         g_trade.PositionClose(ticket);
         continue;
        }
      if(heldBars >= maxHold)
        {
         g_trade.PositionClose(ticket);
         continue;
        }

      double newSl = sl;
      if(progressR >= AC_BreakevenR)
        {
         double be = sell ? open - AC_BreakevenLockUsd : open + AC_BreakevenLockUsd;
         if((sell && (sl <= 0.0 || be < sl)) || (!sell && (sl <= 0.0 || be > sl)))
            newSl = be;
        }
      if(progressR >= AC_TrailStartR)
        {
         double trail = sell ? current + atr * AC_TrailATR : current - atr * AC_TrailATR;
         if((sell && (newSl <= 0.0 || trail < newSl)) || (!sell && (newSl <= 0.0 || trail > newSl)))
            newSl = trail;
        }
      if(MathAbs(newSl - sl) >= _Point * 2.0 && AcaneStopFits(sell, current, newSl))
         g_trade.PositionModify(ticket, AcaneNormalizePrice(newSl), tp);
     }
  }

bool AcaneIsNewBar()
  {
   datetime barTime = iTime(_Symbol, AC_TF, 0);
   if(barTime <= 0)
      return(false);
   if(barTime == g_lastBarTime)
      return(false);
   g_lastBarTime = barTime;
   return(true);
  }

void AcaneStatusLog()
  {
   if(!AC_LogStatus)
      return;
   int bars = Bars(_Symbol, AC_TF);
   if(g_lastStatusBars > 0 && bars - g_lastStatusBars < AC_StatusEveryBars)
      return;
   g_lastStatusBars = bars;
   PrintFormat("ACANE STATUS | open=%d spread=%.2f equity=%.2f dayStop=%s circuit=%s",
               AcaneCountPositions(),
               AcaneSpread(),
               AccountInfoDouble(ACCOUNT_EQUITY),
               g_dailyStopped ? "yes" : "no",
               g_circuitStopped ? "yes" : "no");
  }

int OnInit()
  {
   g_emaFast = iMA(_Symbol, AC_TF, AC_EMAFast, 0, MODE_EMA, PRICE_CLOSE);
   g_emaSlow = iMA(_Symbol, AC_TF, AC_EMASlow, 0, MODE_EMA, PRICE_CLOSE);
   g_m5Fast = iMA(_Symbol, PERIOD_M5, AC_M5Fast, 0, MODE_EMA, PRICE_CLOSE);
   g_m5Slow = iMA(_Symbol, PERIOD_M5, AC_M5Slow, 0, MODE_EMA, PRICE_CLOSE);
   g_m15Fast = iMA(_Symbol, PERIOD_M15, AC_M15Fast, 0, MODE_EMA, PRICE_CLOSE);
   g_m15Slow = iMA(_Symbol, PERIOD_M15, AC_M15Slow, 0, MODE_EMA, PRICE_CLOSE);
   g_h1Fast = iMA(_Symbol, PERIOD_H1, AC_H1Fast, 0, MODE_EMA, PRICE_CLOSE);
   g_h1Slow = iMA(_Symbol, PERIOD_H1, AC_H1Slow, 0, MODE_EMA, PRICE_CLOSE);
   g_atr = iATR(_Symbol, AC_TF, AC_ATRPeriod);
   g_rsi = iRSI(_Symbol, AC_TF, AC_RSIPeriod, PRICE_CLOSE);
   g_adx = iADX(_Symbol, AC_TF, AC_ADXPeriod);
   g_bands = iBands(_Symbol, AC_TF, AC_BBandsPeriod, 0, AC_BBandsDeviation, PRICE_CLOSE);
   if(g_emaFast == INVALID_HANDLE || g_emaSlow == INVALID_HANDLE ||
      g_m5Fast == INVALID_HANDLE || g_m5Slow == INVALID_HANDLE ||
      g_m15Fast == INVALID_HANDLE || g_m15Slow == INVALID_HANDLE ||
      g_h1Fast == INVALID_HANDLE || g_h1Slow == INVALID_HANDLE ||
      g_atr == INVALID_HANDLE || g_rsi == INVALID_HANDLE ||
      g_adx == INVALID_HANDLE || g_bands == INVALID_HANDLE)
      return(INIT_FAILED);
   g_trade.SetExpertMagicNumber(AC_Magic);
   g_trade.SetDeviationInPoints(AC_DeviationPoints);
   g_trade.SetTypeFillingBySymbol(_Symbol);
   g_dayKey = -1;
   g_accountHighEquity = AccountInfoDouble(ACCOUNT_EQUITY);
   AcaneResetDailyGuardIfNeeded();
   PrintFormat("ACANE PROFILE v1.00 OPTIMIZABLE | symbol=%s tf=M1 balance=%.2f leverage=%d",
               _Symbol,
               AccountInfoDouble(ACCOUNT_BALANCE),
               (int)AccountInfoInteger(ACCOUNT_LEVERAGE));
   return(INIT_SUCCEEDED);
  }

void OnDeinit(const int reason)
  {
   if(g_emaFast != INVALID_HANDLE) IndicatorRelease(g_emaFast);
   if(g_emaSlow != INVALID_HANDLE) IndicatorRelease(g_emaSlow);
   if(g_m5Fast != INVALID_HANDLE) IndicatorRelease(g_m5Fast);
   if(g_m5Slow != INVALID_HANDLE) IndicatorRelease(g_m5Slow);
   if(g_m15Fast != INVALID_HANDLE) IndicatorRelease(g_m15Fast);
   if(g_m15Slow != INVALID_HANDLE) IndicatorRelease(g_m15Slow);
   if(g_h1Fast != INVALID_HANDLE) IndicatorRelease(g_h1Fast);
   if(g_h1Slow != INVALID_HANDLE) IndicatorRelease(g_h1Slow);
   if(g_atr != INVALID_HANDLE) IndicatorRelease(g_atr);
   if(g_rsi != INVALID_HANDLE) IndicatorRelease(g_rsi);
   if(g_adx != INVALID_HANDLE) IndicatorRelease(g_adx);
   if(g_bands != INVALID_HANDLE) IndicatorRelease(g_bands);
  }

void OnTick()
  {
   AcaneResetDailyGuardIfNeeded();
   AcaneManagePositions();
   AcaneStatusLog();
   if(AcaneIsNewBar())
      AcaneTryEntry();
  }

double OnTester()
  {
   double profit = TesterStatistics(STAT_PROFIT);
   double pf = TesterStatistics(STAT_PROFIT_FACTOR);
   double recovery = TesterStatistics(STAT_RECOVERY_FACTOR);
   double trades = TesterStatistics(STAT_TRADES);
   double ddPct = TesterStatistics(STAT_EQUITY_DDREL_PERCENT);
   if(pf <= 0.0)
      pf = 0.01;
   double score = profit + pf * 20.0 + recovery * 8.0 + MathMin(trades, 1200.0) * 0.015;
   if(ddPct > AC_TesterMaxDDPct)
      score -= (ddPct - AC_TesterMaxDDPct) * 100.0;
   if(ddPct > 35.0)
      score -= (ddPct - 35.0) * 250.0;
   if(trades < AC_TesterMinTrades)
      score -= (AC_TesterMinTrades - trades) * 0.20;
   if(profit <= 0.0)
      score += profit * 2.0;
   return(score);
  }
