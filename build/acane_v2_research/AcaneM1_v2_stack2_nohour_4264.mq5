#property copyright "OpenAI Codex"
#property version   "2.00"
#property strict
// Acane v2 research variant AcaneM1_v2_stack2_nohour_4264.

#include <Trade/Trade.mqh>

const double ACANE_RiskPercent = 30.00;
const double ACANE_CoreRiskMultiplier = 0.00;
const double ACANE_WeakRiskMultiplier = 0.00;
const int    ACANE_MaxPositions = 4;
const int    ACANE_MaxSameSidePositions = 2;
const int    ACANE_MinSecondsBetweenEntries = 60;
const int    ACANE_MinHoldSeconds = 6;
const int    ACANE_MaxHoldSeconds = 100;
const int    ACANE_MicroCloseProfitSeconds = 999;
const double ACANE_MaxSpreadUsd = 1.10;
const int    ACANE_DeviationPoints = 60;
const bool   ACANE_EnableBuys = true;
const bool   ACANE_EnableSells = true;
const bool   ACANE_BlockOppositeDirection = true;
const bool   ACANE_EnableDailyGuard = true;
const double ACANE_DailyMaxLossPct = 12.00;
const bool   ACANE_CloseOnDailyStop = true;
const bool   ACANE_EnableWeeklyGuard = false;
const double ACANE_WeeklyMaxLossPct = 30.00;
const double ACANE_WeeklyMaxGivebackPct = 35.00;
const bool   ACANE_CloseOnWeeklyStop = true;
const bool   ACANE_EnableMonthlyGuard = false;
const double ACANE_MonthlyMaxLossPct = 30.00;
const double ACANE_MonthlyMaxGivebackPct = 35.00;
const bool   ACANE_CloseOnMonthlyStop = true;
const bool   ACANE_EnableEquityCircuit = true;
const double ACANE_MaxAccountDrawdownPct = 15.00;
const bool   ACANE_CloseOnCircuitStop = true;
const double ACANE_MaxOpenRiskPct = 10.00;
const double ACANE_MaxSameSideOpenRiskPct = 8.00;
const double ACANE_BasketLossStopPct = 7.00;
const bool   ACANE_StopDayOnBasketLoss = true;
const int    ACANE_FastLossCooldownAfter = 1;
const int    ACANE_FastLossCooldownSeconds = 1800;
const double ACANE_MrvMaxImpulseATR = 1.10;
const double ACANE_MrvMaxEmaDistanceATR = 1.25;
const bool   ACANE_EnableStructuralPriceGate = true;
const double ACANE_MinD1CloseForTrading = 2500.00;
const bool   ACANE_CloseOnStructuralBlock = false;
const double ACANE_MinSLUsd = 0.90;
const double ACANE_MaxSLUsd = 3.60;
const double ACANE_ATRStopMult = 0.62;
const double ACANE_TakeProfitR = 0.45;
const double ACANE_ScalpProfitUsd = 0.30;
const double ACANE_FastLossR = 0.24;
const double ACANE_BreakevenR = 0.18;
const double ACANE_BreakevenLockUsd = 0.05;
const double ACANE_TrailStartR = 0.38;
const double ACANE_TrailATR = 0.28;
const int    ACANE_EMAFast = 9;
const int    ACANE_EMASlow = 34;
const int    ACANE_M5Fast = 12;
const int    ACANE_M5Slow = 36;
const int    ACANE_ATRPeriod = 14;
const int    ACANE_RSI_Period = 7;
const int    ACANE_BBandsPeriod = 20;
const double ACANE_BBandsDeviation = 2.00;
const int    ACANE_BreakLookback = 4;
const int    ACANE_CompressionLookback = 5;
const double ACANE_MinBodyRatio = 0.34;
const double ACANE_StrongBodyRatio = 0.52;
const double ACANE_MinBreakATR = 0.015;
const double ACANE_StrongBreakATR = 0.045;
const double ACANE_MaxChaseATR = 1.65;
const double ACANE_MinATRUsd = 0.18;
const double ACANE_MaxATRUsd = 8.00;
const int    ACANE_MinScore = 52;
const int    ACANE_StrongScore = 73;
const bool   ACANE_UseSessionFilter = false;
const int    ACANE_SessionStartHour = 0;
const int    ACANE_SessionEndHour = 23;
const string ACANE_BlockEntryHours = "";
const bool   ACANE_EnableMomentumEngine = false;
const bool   ACANE_EnableReclaimEngine = false;
const bool   ACANE_EnableCompressionEngine = false;
const bool   ACANE_EnableMeanReversionEngine = true;
const double ACANE_MeanReversionRSILow = 42.0;
const double ACANE_MeanReversionRSIHigh = 58.0;
const double ACANE_MeanReversionTouchATR = 0.04;
const double ACANE_MeanReversionRiskMultiplier = 0.12;
const double ACANE_MeanReversionRR = 0.72;
const bool   ACANE_EnableMinLotFallback = true;
const double ACANE_MinLotFallbackMaxRiskPct = 7.00;
const bool   ACANE_LogEntries = true;
const bool   ACANE_LogStatus = true;
const bool   ACANE_DebugReasons = true;
const int    ACANE_StatusEverySeconds = 60;
const int    ACANE_DebugEverySeconds = 60;

static const ulong ACANE_MAGIC = 2026050701;
static const ENUM_TIMEFRAMES ACANE_TF = PERIOD_M1;

enum AcaneRegime
  {
   ACANE_SIDEWAYS = 0,
   ACANE_BULL = 1,
   ACANE_BEAR = -1
  };

struct AcaneSignal
  {
   bool   valid;
   bool   sell;
   int    score;
   string engine;
   string tags;
   double stopDistance;
   double rr;
   double riskMultiplier;
   string comment;
  };

CTrade   g_trade;
int      g_emaFast = INVALID_HANDLE;
int      g_emaSlow = INVALID_HANDLE;
int      g_m5Fast = INVALID_HANDLE;
int      g_m5Slow = INVALID_HANDLE;
int      g_atr = INVALID_HANDLE;
int      g_rsi = INVALID_HANDLE;
int      g_bands = INVALID_HANDLE;
datetime g_lastEntryTime = 0;
datetime g_lastStatusTime = 0;
datetime g_lastDebugReasonTime = 0;
string   g_lastDebugReason = "";
int      g_dayKey = -1;
double   g_dayStartEquity = 0.0;
double   g_dayHighEquity = 0.0;
bool     g_dailyStopped = false;
int      g_weekKey = -1;
double   g_weekStartEquity = 0.0;
double   g_weekHighEquity = 0.0;
bool     g_weeklyStopped = false;
int      g_monthKey = -1;
double   g_monthStartEquity = 0.0;
double   g_monthHighEquity = 0.0;
bool     g_monthlyStopped = false;
double   g_accountHighEquity = 0.0;
bool     g_circuitStopped = false;
int      g_fastLossStreak = 0;
datetime g_cooldownUntil = 0;


double AcaneNormalizePrice(const double price)
  {
   return(NormalizeDouble(price, (int)SymbolInfoInteger(_Symbol, SYMBOL_DIGITS)));
  }


double AcaneMinStopDistance()
  {
   long stopLevel = SymbolInfoInteger(_Symbol, SYMBOL_TRADE_STOPS_LEVEL);
   long freezeLevel = SymbolInfoInteger(_Symbol, SYMBOL_TRADE_FREEZE_LEVEL);
   return((double)MathMax(stopLevel, freezeLevel) * _Point);
  }


bool AcaneCopyBufferValue(const int handle, const int buffer, const int shift, double &value)
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
   return(CopyRates(_Symbol, ACANE_TF, 0, count, rates) == count);
  }


int AcaneDayKey(const datetime ts)
  {
   MqlDateTime dt;
   TimeToStruct(ts, dt);
   return(dt.year * 1000 + dt.day_of_year);
  }


int AcaneWeekKey(const datetime ts)
  {
   MqlDateTime dt;
   TimeToStruct(ts, dt);
   int bucket = (dt.day_of_year - 1) / 7;
   return(dt.year * 100 + bucket);
  }


int AcaneMonthKey(const datetime ts)
  {
   MqlDateTime dt;
   TimeToStruct(ts, dt);
   return(dt.year * 100 + dt.mon);
  }


bool AcaneStructuralPriceAllowed()
  {
   if(!ACANE_EnableStructuralPriceGate)
      return(true);
   double d1Close = iClose(_Symbol, PERIOD_D1, 1);
   if(d1Close <= 0.0)
      return(false);
   return(d1Close >= ACANE_MinD1CloseForTrading);
  }


bool AcaneHourAllowed()
  {
   MqlDateTime dt;
   TimeToStruct(TimeCurrent(), dt);
   string hours = ACANE_BlockEntryHours;
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

   if(!ACANE_UseSessionFilter)
      return(true);
   if(ACANE_SessionStartHour == ACANE_SessionEndHour)
      return(true);
   if(ACANE_SessionStartHour < ACANE_SessionEndHour)
      return(dt.hour >= ACANE_SessionStartHour && dt.hour < ACANE_SessionEndHour);
   return(dt.hour >= ACANE_SessionStartHour || dt.hour < ACANE_SessionEndHour);
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


double AcaneSpread()
  {
   double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   if(ask <= 0.0 || bid <= 0.0)
      return(999.0);
   return(ask - bid);
  }


bool AcaneSpreadAllowed()
  {
   return(AcaneSpread() <= ACANE_MaxSpreadUsd);
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
      if((ulong)PositionGetInteger(POSITION_MAGIC) != ACANE_MAGIC)
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


bool AcaneHasOpposite(const bool sell)
  {
   if(!ACANE_BlockOppositeDirection)
      return(false);
   return(AcaneCountPositions(sell ? 1 : -1) > 0);
  }


void AcaneCloseOwnPositions(const string reason)
  {
   if(!AcaneMarketOpenLikely())
      return;

   g_trade.SetExpertMagicNumber(ACANE_MAGIC);
   g_trade.SetDeviationInPoints(ACANE_DeviationPoints);
   g_trade.SetTypeFillingBySymbol(_Symbol);

   for(int i = PositionsTotal() - 1; i >= 0; i--)
     {
      ulong ticket = PositionGetTicket(i);
      if(ticket == 0 || !PositionSelectByTicket(ticket))
         continue;
      if(PositionGetString(POSITION_SYMBOL) != _Symbol)
         continue;
      if((ulong)PositionGetInteger(POSITION_MAGIC) != ACANE_MAGIC)
         continue;
      if(g_trade.PositionClose(ticket))
         PrintFormat("ACANE EXIT RISK | ticket=%I64u reason=%s", ticket, reason);
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
   g_dailyStopped = false;
   g_fastLossStreak = 0;
   g_cooldownUntil = 0;
   PrintFormat("ACANE GUARD | new day | equity=%.2f", g_dayStartEquity);
  }


void AcaneResetWeeklyGuardIfNeeded()
  {
   int key = AcaneWeekKey(TimeCurrent());
   if(key == g_weekKey)
      return;
   g_weekKey = key;
   g_weekStartEquity = AccountInfoDouble(ACCOUNT_EQUITY);
   g_weekHighEquity = g_weekStartEquity;
   g_weeklyStopped = false;
   PrintFormat("ACANE GUARD | new week | equity=%.2f", g_weekStartEquity);
  }


void AcaneResetMonthlyGuardIfNeeded()
  {
   int key = AcaneMonthKey(TimeCurrent());
   if(key == g_monthKey)
      return;
   g_monthKey = key;
   g_monthStartEquity = AccountInfoDouble(ACCOUNT_EQUITY);
   g_monthHighEquity = g_monthStartEquity;
   g_monthlyStopped = false;
   PrintFormat("ACANE GUARD | new month | equity=%.2f", g_monthStartEquity);
  }


bool AcaneRiskAllowsTrading()
  {
   double equity = AccountInfoDouble(ACCOUNT_EQUITY);
   if(g_accountHighEquity <= 0.0)
      g_accountHighEquity = equity;
   g_accountHighEquity = MathMax(g_accountHighEquity, equity);

   if(!AcaneStructuralPriceAllowed())
     {
      string reason = StringFormat("structural price gate d1 close below %.2f", ACANE_MinD1CloseForTrading);
      if(ACANE_CloseOnStructuralBlock)
         AcaneCloseOwnPositions(reason);
      return(false);
     }

   if(ACANE_EnableDailyGuard)
     {
      AcaneResetDailyGuardIfNeeded();
      g_dayHighEquity = MathMax(g_dayHighEquity, equity);
      if(!g_dailyStopped && g_dayStartEquity > 0.0)
        {
         double dayLossPct = (g_dayStartEquity - equity) / g_dayStartEquity * 100.0;
         if(dayLossPct >= ACANE_DailyMaxLossPct)
           {
            g_dailyStopped = true;
            string reason = StringFormat("daily loss %.2f%% >= %.2f%%", dayLossPct, ACANE_DailyMaxLossPct);
            PrintFormat("ACANE GUARD | %s", reason);
            if(ACANE_CloseOnDailyStop)
               AcaneCloseOwnPositions(reason);
           }
        }
      if(g_dailyStopped)
        {
         if(ACANE_CloseOnDailyStop)
            AcaneCloseOwnPositions("daily stop active retry");
         return(false);
        }
     }

   if(ACANE_EnableWeeklyGuard)
     {
      AcaneResetWeeklyGuardIfNeeded();
      g_weekHighEquity = MathMax(g_weekHighEquity, equity);
      if(!g_weeklyStopped && g_weekStartEquity > 0.0)
        {
         double weekLossPct = (g_weekStartEquity - equity) / g_weekStartEquity * 100.0;
         double weekGivebackPct = (g_weekHighEquity - equity) / g_weekHighEquity * 100.0;
         if((ACANE_WeeklyMaxLossPct > 0.0 && weekLossPct >= ACANE_WeeklyMaxLossPct) ||
            (ACANE_WeeklyMaxGivebackPct > 0.0 && weekGivebackPct >= ACANE_WeeklyMaxGivebackPct))
           {
            g_weeklyStopped = true;
            string reason = StringFormat("weekly guard loss %.2f%% giveback %.2f%%", weekLossPct, weekGivebackPct);
            PrintFormat("ACANE GUARD | %s", reason);
            if(ACANE_CloseOnWeeklyStop)
               AcaneCloseOwnPositions(reason);
           }
        }
      if(g_weeklyStopped)
         return(false);
     }

   if(ACANE_EnableMonthlyGuard)
     {
      AcaneResetMonthlyGuardIfNeeded();
      g_monthHighEquity = MathMax(g_monthHighEquity, equity);
      if(!g_monthlyStopped && g_monthStartEquity > 0.0)
        {
         double monthLossPct = (g_monthStartEquity - equity) / g_monthStartEquity * 100.0;
         double monthGivebackPct = (g_monthHighEquity - equity) / g_monthHighEquity * 100.0;
         if((ACANE_MonthlyMaxLossPct > 0.0 && monthLossPct >= ACANE_MonthlyMaxLossPct) ||
            (ACANE_MonthlyMaxGivebackPct > 0.0 && monthGivebackPct >= ACANE_MonthlyMaxGivebackPct))
           {
            g_monthlyStopped = true;
            string reason = StringFormat("monthly guard loss %.2f%% giveback %.2f%%", monthLossPct, monthGivebackPct);
            PrintFormat("ACANE GUARD | %s", reason);
            if(ACANE_CloseOnMonthlyStop)
               AcaneCloseOwnPositions(reason);
           }
        }
      if(g_monthlyStopped)
         return(false);
     }

   if(ACANE_EnableEquityCircuit && !g_circuitStopped && g_accountHighEquity > 0.0)
     {
      double ddPct = (g_accountHighEquity - equity) / g_accountHighEquity * 100.0;
      if(ddPct >= ACANE_MaxAccountDrawdownPct)
        {
         g_circuitStopped = true;
         string reason = StringFormat("account dd %.2f%% >= %.2f%%", ddPct, ACANE_MaxAccountDrawdownPct);
         PrintFormat("ACANE GUARD | %s", reason);
         if(ACANE_CloseOnCircuitStop)
            AcaneCloseOwnPositions(reason);
        }
     }
   if(g_circuitStopped)
     {
      if(ACANE_CloseOnCircuitStop)
         AcaneCloseOwnPositions("account circuit active retry");
      return(false);
     }
   return(true);
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


double AcaneOpenRiskCash(const int side = 0)
  {
   double valuePerPrice = AcaneValuePerPriceUnit();
   double riskCash = 0.0;
   for(int i = PositionsTotal() - 1; i >= 0; i--)
     {
      ulong ticket = PositionGetTicket(i);
      if(ticket == 0 || !PositionSelectByTicket(ticket))
         continue;
      if(PositionGetString(POSITION_SYMBOL) != _Symbol)
         continue;
      if((ulong)PositionGetInteger(POSITION_MAGIC) != ACANE_MAGIC)
         continue;
      ENUM_POSITION_TYPE type = (ENUM_POSITION_TYPE)PositionGetInteger(POSITION_TYPE);
      if(side == 1 && type != POSITION_TYPE_BUY)
         continue;
      if(side == -1 && type != POSITION_TYPE_SELL)
         continue;
      double openPrice = PositionGetDouble(POSITION_PRICE_OPEN);
      double sl = PositionGetDouble(POSITION_SL);
      double volume = PositionGetDouble(POSITION_VOLUME);
      double distance = MathAbs(openPrice - sl);
      if(distance <= 0.0)
         distance = ACANE_MinSLUsd;
      riskCash += distance * valuePerPrice * volume;
     }
   return(riskCash);
  }


double AcaneOpenRiskPct(const int side = 0)
  {
   double equity = AccountInfoDouble(ACCOUNT_EQUITY);
   if(equity <= 0.0)
      return(999.0);
   return(AcaneOpenRiskCash(side) / equity * 100.0);
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
      if((ulong)PositionGetInteger(POSITION_MAGIC) != ACANE_MAGIC)
         continue;
      profit += PositionGetDouble(POSITION_PROFIT) + PositionGetDouble(POSITION_SWAP);
     }
   return(profit);
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
   double steps = MathFloor(clipped / step + 1e-9);
   double normalized = NormalizeDouble(steps * step, AcaneVolumePrecision());
   if(normalized < minLot)
      return(0.0);
   return(normalized);
  }


double AcaneLotForRisk(const double stopDistance, const double riskMultiplier)
  {
   if(stopDistance <= 0.0)
      return(0.0);
   double equity = AccountInfoDouble(ACCOUNT_EQUITY);
   if(equity <= 0.0)
      return(0.0);
   double riskCash = equity * ACANE_RiskPercent / 100.0 * riskMultiplier;
   double valuePerPrice = AcaneValuePerPriceUnit();
   double raw = riskCash / (stopDistance * valuePerPrice);
   double floored = AcaneFloorVolume(raw);
   if(floored > 0.0)
      return(floored);

   if(!ACANE_EnableMinLotFallback)
      return(0.0);

   double minLot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
   if(minLot <= 0.0)
      return(0.0);
   double fallbackRiskPct = stopDistance * valuePerPrice * minLot / equity * 100.0;
   if(fallbackRiskPct > ACANE_MinLotFallbackMaxRiskPct)
      return(0.0);
   return(AcaneFloorVolume(minLot));
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
   double high = rates[fromShift].high;
   for(int i = fromShift + 1; i < fromShift + count; i++)
      high = MathMax(high, rates[i].high);
   return(high);
  }


double AcaneLowestLow(const MqlRates &rates[], const int fromShift, const int count)
  {
   double low = rates[fromShift].low;
   for(int i = fromShift + 1; i < fromShift + count; i++)
      low = MathMin(low, rates[i].low);
   return(low);
  }


double AcaneRange(const MqlRates &rates[], const int fromShift, const int count)
  {
   return(AcaneHighestHigh(rates, fromShift, count) - AcaneLowestLow(rates, fromShift, count));
  }


AcaneRegime AcaneDetectRegime()
  {
   double f1, s1, f5, s5;
   if(!AcaneCopyBufferValue(g_emaFast, 0, 1, f1) ||
      !AcaneCopyBufferValue(g_emaSlow, 0, 1, s1) ||
      !AcaneCopyBufferValue(g_m5Fast, 0, 1, f5) ||
      !AcaneCopyBufferValue(g_m5Slow, 0, 1, s5))
      return(ACANE_SIDEWAYS);

   if(f1 > s1 && f5 >= s5)
      return(ACANE_BULL);
   if(f1 < s1 && f5 <= s5)
      return(ACANE_BEAR);
   return(ACANE_SIDEWAYS);
  }


string AcaneComment(const string engine, const int score, const bool sell, const string tags)
  {
   string grade = score >= ACANE_StrongScore ? "A" : "B";
   string comment = "AC1|" + engine + "|" + engine + "|S" + IntegerToString(score) + "|" + grade;
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
   if(score < ACANE_MinScore)
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
   best.comment = AcaneComment(engine, score, sell, tags);
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
   best.rr = ACANE_TakeProfitR;
   best.riskMultiplier = ACANE_WeakRiskMultiplier;
   best.comment = "";

   if(!AcaneHourAllowed())
      return(best);

   MqlRates rates[];
   if(!AcaneLoadRates(rates, MathMax(ACANE_BreakLookback + 5, ACANE_CompressionLookback + 5)))
      return(best);

   double emaFast, emaSlow, atr, rsi;
   double bandMiddle, bandUpper, bandLower;
   if(!AcaneCopyBufferValue(g_emaFast, 0, 0, emaFast) ||
      !AcaneCopyBufferValue(g_emaSlow, 0, 0, emaSlow) ||
      !AcaneCopyBufferValue(g_atr, 0, 1, atr) ||
      !AcaneCopyBufferValue(g_rsi, 0, 0, rsi) ||
      !AcaneCopyBufferValue(g_bands, 0, 0, bandMiddle) ||
      !AcaneCopyBufferValue(g_bands, 1, 0, bandUpper) ||
      !AcaneCopyBufferValue(g_bands, 2, 0, bandLower))
      return(best);

   if(atr < ACANE_MinATRUsd || atr > ACANE_MaxATRUsd)
      return(best);

   AcaneRegime regime = AcaneDetectRegime();
   MqlRates bar = rates[0];
   double body = AcaneBodyRatio(bar);
   double previousHigh = AcaneHighestHigh(rates, 1, ACANE_BreakLookback);
   double previousLow = AcaneLowestLow(rates, 1, ACANE_BreakLookback);
   double compressionRange = AcaneRange(rates, 1, ACANE_CompressionLookback);
   double stopDistance = MathMax(ACANE_MinSLUsd, MathMin(ACANE_MaxSLUsd, atr * ACANE_ATRStopMult));
   stopDistance = MathMax(stopDistance, AcaneMinStopDistance() + AcaneSpread() + _Point);
   double close = bar.close;
   double open = bar.open;
   double recentImpulse = MathAbs(close - rates[3].close) / atr;
   double emaDistance = MathAbs(close - emaSlow) / atr;
   double breakUp = (close - previousHigh) / atr;
   double breakDown = (previousLow - close) / atr;
   double stretchUp = MathAbs(close - emaFast) / atr;
   double compression = compressionRange / atr;
   int base = 44;

   if(regime == ACANE_BULL)
      base += 12;
   else if(regime == ACANE_BEAR)
      base += 12;
   else
      base += 2;

   if(AcaneSpread() <= ACANE_MaxSpreadUsd * 0.55)
      base += 5;
   if(body >= ACANE_MinBodyRatio)
      base += 7;
   if(body >= ACANE_StrongBodyRatio)
      base += 6;

   if(ACANE_EnableMeanReversionEngine)
     {
      bool buyReclaim = rates[0].low <= bandLower - atr * ACANE_MeanReversionTouchATR &&
                        close > bandLower &&
                        close > open &&
                        rsi <= ACANE_MeanReversionRSILow &&
                        !(close < rates[3].close && recentImpulse > ACANE_MrvMaxImpulseATR) &&
                        emaDistance <= ACANE_MrvMaxEmaDistanceATR;
      int buyScore = 48 + (buyReclaim ? 20 : 0) + (regime != ACANE_BEAR ? 8 : 0) + (body >= ACANE_MinBodyRatio ? 6 : 0);
      if(ACANE_EnableBuys && buyReclaim)
         AcaneMaybeSetSignal(best,
                             false,
                             buyScore,
                             "MRV",
                             (regime == ACANE_BULL ? "RG|BB" : "WG|BB"),
                             stopDistance,
                             ACANE_MeanReversionRR,
                             ACANE_MeanReversionRiskMultiplier);

      bool sellReject = rates[0].high >= bandUpper + atr * ACANE_MeanReversionTouchATR &&
                        close < bandUpper &&
                        close < open &&
                        rsi >= ACANE_MeanReversionRSIHigh &&
                        !(close > rates[3].close && recentImpulse > ACANE_MrvMaxImpulseATR) &&
                        emaDistance <= ACANE_MrvMaxEmaDistanceATR;
      int sellScore = 48 + (sellReject ? 20 : 0) + (regime != ACANE_BULL ? 8 : 0) + (body >= ACANE_MinBodyRatio ? 6 : 0);
      if(ACANE_EnableSells && sellReject)
         AcaneMaybeSetSignal(best,
                             true,
                             sellScore,
                             "MRV",
                             (regime == ACANE_BEAR ? "RG|BB" : "WG|BB"),
                             stopDistance,
                             ACANE_MeanReversionRR,
                             ACANE_MeanReversionRiskMultiplier);
     }

   if(ACANE_EnableBuys)
     {
      int score = base;
      if(regime == ACANE_BULL)
         score += 8;
      if(close > emaFast && emaFast >= emaSlow)
         score += 8;
      if(close > open)
         score += 5;
      if(breakUp >= ACANE_MinBreakATR)
         score += 7;
      if(breakUp >= ACANE_StrongBreakATR)
         score += 8;
      if(rsi >= 52.0 && rsi <= 78.0)
         score += 5;
      if(stretchUp <= ACANE_MaxChaseATR)
         score += 4;
      double risk = (score >= ACANE_StrongScore ? ACANE_CoreRiskMultiplier : ACANE_WeakRiskMultiplier);
      string regimeTag = (regime == ACANE_BULL ? "RG" : "WG");
      if(ACANE_EnableMomentumEngine)
         AcaneMaybeSetSignal(best, false, score, "MOM", regimeTag + "|BRK", stopDistance, ACANE_TakeProfitR, risk);

      bool reclaimed = rates[0].low <= emaFast + atr * 0.18 && close > emaFast && close > open;
      int pbScore = base + (regime == ACANE_BULL ? 12 : 0) + (reclaimed ? 16 : 0) + (rsi >= 48.0 ? 5 : 0);
      if(reclaimed && ACANE_EnableReclaimEngine)
        {
         double pbRisk = (pbScore >= ACANE_StrongScore ? ACANE_CoreRiskMultiplier : ACANE_WeakRiskMultiplier);
         AcaneMaybeSetSignal(best, false, pbScore, "RCL", regimeTag + "|EMA", stopDistance, ACANE_TakeProfitR * 0.92, pbRisk);
        }

      bool compressedBreak = compression <= 1.60 && close > previousHigh && body >= ACANE_MinBodyRatio;
      int compScore = base + (regime != ACANE_BEAR ? 8 : 0) + (compressedBreak ? 17 : 0);
      if(compressedBreak && ACANE_EnableCompressionEngine)
        {
         double compRisk = (compScore >= ACANE_StrongScore ? ACANE_CoreRiskMultiplier : ACANE_WeakRiskMultiplier);
         AcaneMaybeSetSignal(best, false, compScore, "CMP", regimeTag + "|SQZ", stopDistance, ACANE_TakeProfitR * 0.82, compRisk);
        }
     }

   if(ACANE_EnableSells)
     {
      int score = base;
      if(regime == ACANE_BEAR)
         score += 8;
      if(close < emaFast && emaFast <= emaSlow)
         score += 8;
      if(close < open)
         score += 5;
      if(breakDown >= ACANE_MinBreakATR)
         score += 7;
      if(breakDown >= ACANE_StrongBreakATR)
         score += 8;
      if(rsi <= 48.0 && rsi >= 22.0)
         score += 5;
      if(stretchUp <= ACANE_MaxChaseATR)
         score += 4;
      double risk = (score >= ACANE_StrongScore ? ACANE_CoreRiskMultiplier : ACANE_WeakRiskMultiplier);
      string regimeTag = (regime == ACANE_BEAR ? "RG" : "WG");
      if(ACANE_EnableMomentumEngine)
         AcaneMaybeSetSignal(best, true, score, "MOM", regimeTag + "|BRK", stopDistance, ACANE_TakeProfitR, risk);

      bool rejected = rates[0].high >= emaFast - atr * 0.18 && close < emaFast && close < open;
      int rjScore = base + (regime == ACANE_BEAR ? 12 : 0) + (rejected ? 16 : 0) + (rsi <= 52.0 ? 5 : 0);
      if(rejected && ACANE_EnableReclaimEngine)
        {
         double rjRisk = (rjScore >= ACANE_StrongScore ? ACANE_CoreRiskMultiplier : ACANE_WeakRiskMultiplier);
         AcaneMaybeSetSignal(best, true, rjScore, "RJT", regimeTag + "|EMA", stopDistance, ACANE_TakeProfitR * 0.92, rjRisk);
        }

      bool compressedBreak = compression <= 1.60 && close < previousLow && body >= ACANE_MinBodyRatio;
      int compScore = base + (regime != ACANE_BULL ? 8 : 0) + (compressedBreak ? 17 : 0);
      if(compressedBreak && ACANE_EnableCompressionEngine)
        {
         double compRisk = (compScore >= ACANE_StrongScore ? ACANE_CoreRiskMultiplier : ACANE_WeakRiskMultiplier);
         AcaneMaybeSetSignal(best, true, compScore, "CMP", regimeTag + "|SQZ", stopDistance, ACANE_TakeProfitR * 0.82, compRisk);
        }
     }

   return(best);
  }


bool AcaneStopFits(const bool sell, const double price, const double stopLoss)
  {
   double minDistance = AcaneMinStopDistance();
   if(sell)
      return(stopLoss > price + minDistance);
   return(stopLoss < price - minDistance);
  }


bool AcaneTakeProfitFits(const bool sell, const double price, const double takeProfit)
  {
   double minDistance = AcaneMinStopDistance();
   if(sell)
      return(takeProfit < price - minDistance);
   return(takeProfit > price + minDistance);
  }


void AcaneDebugBlock(const string reason)
  {
   if(!ACANE_DebugReasons)
      return;
   datetime now = TimeCurrent();
   if(g_lastDebugReason == reason &&
      g_lastDebugReasonTime > 0 &&
      (now - g_lastDebugReasonTime) < ACANE_DebugEverySeconds)
      return;

   g_lastDebugReason = reason;
   g_lastDebugReasonTime = now;
   PrintFormat("ACANE DEBUG BLOCK | %s | spread=%.2f equity=%.2f open=%d buy=%d sell=%d openRisk=%.2f dailyStop=%s circuit=%s cooldown=%s",
               reason,
               AcaneSpread(),
               AccountInfoDouble(ACCOUNT_EQUITY),
               AcaneCountPositions(),
               AcaneCountPositions(1),
               AcaneCountPositions(-1),
               AcaneOpenRiskPct(),
               g_dailyStopped ? "yes" : "no",
               g_circuitStopped ? "yes" : "no",
               (g_cooldownUntil > TimeCurrent()) ? "yes" : "no");
  }


void AcaneTryEntry()
  {
   if(!AcaneRiskAllowsTrading())
     {
      AcaneDebugBlock("risk guard blocked");
      return;
     }
   if(g_cooldownUntil > 0 && TimeCurrent() < g_cooldownUntil)
     {
      AcaneDebugBlock("fast-loss cooldown active");
      return;
     }
   if(!AcaneMarketOpenLikely())
     {
      AcaneDebugBlock("market closed or trade mode not full");
      return;
     }
   if(!AcaneSpreadAllowed())
     {
      AcaneDebugBlock("spread above max");
      return;
     }
   if(AcaneCountPositions() >= ACANE_MaxPositions)
     {
      AcaneDebugBlock("max positions reached");
      return;
     }

   datetime now = TimeCurrent();
   if(g_lastEntryTime > 0 && (now - g_lastEntryTime) < ACANE_MinSecondsBetweenEntries)
     {
      AcaneDebugBlock("min entry spacing active");
      return;
     }

   AcaneSignal signal = AcaneBuildSignal();
   if(!signal.valid)
     {
      AcaneDebugBlock("no valid signal");
      return;
     }
   if(AcaneHasOpposite(signal.sell))
     {
      AcaneDebugBlock("opposite position exists");
      return;
     }
   if(AcaneCountPositions(signal.sell ? -1 : 1) >= ACANE_MaxSameSidePositions)
     {
      AcaneDebugBlock("max same-side positions reached");
      return;
     }

   double lot = AcaneLotForRisk(signal.stopDistance, signal.riskMultiplier);
   if(lot <= 0.0)
     {
      AcaneDebugBlock("lot calculation returned zero");
      return;
     }

   double equity = AccountInfoDouble(ACCOUNT_EQUITY);
   if(equity <= 0.0)
     {
      AcaneDebugBlock("equity is zero");
      return;
     }
   double addedRiskPct = signal.stopDistance * AcaneValuePerPriceUnit() * lot / equity * 100.0;
   int side = signal.sell ? -1 : 1;
   if(AcaneOpenRiskPct() + addedRiskPct > ACANE_MaxOpenRiskPct)
     {
      AcaneDebugBlock("total open risk limit");
      return;
     }
   if(AcaneOpenRiskPct(side) + addedRiskPct > ACANE_MaxSameSideOpenRiskPct)
     {
      AcaneDebugBlock("same-side open risk limit");
      return;
     }

   double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   double price = signal.sell ? bid : ask;
   double tpDistance = MathMax(signal.stopDistance * signal.rr, ACANE_ScalpProfitUsd + AcaneSpread());
   double sl = signal.sell ? price + signal.stopDistance : price - signal.stopDistance;
   double tp = signal.sell ? price - tpDistance : price + tpDistance;
   sl = AcaneNormalizePrice(sl);
   tp = AcaneNormalizePrice(tp);
   if(!AcaneStopFits(signal.sell, price, sl))
     {
      AcaneDebugBlock("stop-loss distance invalid");
      return;
     }
   if(!AcaneTakeProfitFits(signal.sell, price, tp))
     {
      AcaneDebugBlock("take-profit distance invalid");
      return;
     }

   g_trade.SetExpertMagicNumber(ACANE_MAGIC);
   g_trade.SetDeviationInPoints(ACANE_DeviationPoints);
   g_trade.SetTypeFillingBySymbol(_Symbol);

   bool ok = signal.sell ? g_trade.Sell(lot, _Symbol, 0.0, sl, tp, signal.comment)
                         : g_trade.Buy(lot, _Symbol, 0.0, sl, tp, signal.comment);
   if(ok)
     {
      g_lastEntryTime = now;
      if(ACANE_LogEntries)
         PrintFormat("ACANE ENTRY %s | engine=%s score=%d lot=%.2f sl=%.2f tp=%.2f stop=%.2f rr=%.2f spread=%.2f comment=%s",
                     signal.sell ? "SELL" : "BUY",
                     signal.engine,
                     signal.score,
                     lot,
                     sl,
                     tp,
                     signal.stopDistance,
                     signal.rr,
                     AcaneSpread(),
                     signal.comment);
     }
   else
     {
      AcaneDebugBlock(StringFormat("order send failed retcode=%d %s",
                                   g_trade.ResultRetcode(),
                                   g_trade.ResultRetcodeDescription()));
     }
  }


void AcaneManagePositions()
  {
   if(!AcaneMarketOpenLikely())
      return;

   g_trade.SetExpertMagicNumber(ACANE_MAGIC);
   g_trade.SetDeviationInPoints(ACANE_DeviationPoints);
   g_trade.SetTypeFillingBySymbol(_Symbol);

   double atr;
   if(!AcaneCopyBufferValue(g_atr, 0, 1, atr))
      atr = 1.0;
   atr = MathMax(atr, ACANE_MinATRUsd);

   int openCount = AcaneCountPositions();
   double equity = AccountInfoDouble(ACCOUNT_EQUITY);
   if(openCount > 0 && equity > 0.0)
     {
      double floatingLossPct = -AcaneOwnFloatingProfit() / equity * 100.0;
      if(floatingLossPct >= ACANE_BasketLossStopPct)
        {
         PrintFormat("ACANE GUARD | basket floating loss %.2f%% >= %.2f%%", floatingLossPct, ACANE_BasketLossStopPct);
         if(ACANE_StopDayOnBasketLoss)
            g_dailyStopped = true;
         g_cooldownUntil = TimeCurrent() + ACANE_FastLossCooldownSeconds;
         AcaneCloseOwnPositions("basket loss stop");
         return;
        }
     }

   for(int i = PositionsTotal() - 1; i >= 0; i--)
     {
      ulong ticket = PositionGetTicket(i);
      if(ticket == 0 || !PositionSelectByTicket(ticket))
         continue;
      if(PositionGetString(POSITION_SYMBOL) != _Symbol)
         continue;
      if((ulong)PositionGetInteger(POSITION_MAGIC) != ACANE_MAGIC)
         continue;

      ENUM_POSITION_TYPE type = (ENUM_POSITION_TYPE)PositionGetInteger(POSITION_TYPE);
      bool sell = (type == POSITION_TYPE_SELL);
      double openPrice = PositionGetDouble(POSITION_PRICE_OPEN);
      double sl = PositionGetDouble(POSITION_SL);
      double tp = PositionGetDouble(POSITION_TP);
      double current = sell ? SymbolInfoDouble(_Symbol, SYMBOL_ASK) : SymbolInfoDouble(_Symbol, SYMBOL_BID);
      double progress = sell ? (openPrice - current) : (current - openPrice);
      double risk = MathAbs(openPrice - sl);
      if(risk <= 0.0)
         risk = ACANE_MinSLUsd;
      double progressR = progress / risk;
      datetime openTime = (datetime)PositionGetInteger(POSITION_TIME);
      int secondsHeld = (int)(TimeCurrent() - openTime);

      if(secondsHeld >= ACANE_MicroCloseProfitSeconds && progress >= ACANE_ScalpProfitUsd)
        {
         if(g_trade.PositionClose(ticket))
           {
            g_fastLossStreak = 0;
            PrintFormat("ACANE EXIT MICRO_TP | ticket=%I64u seconds=%d r=%.2f", ticket, secondsHeld, progressR);
           }
         continue;
        }

      if(secondsHeld >= ACANE_MinHoldSeconds && progressR <= -ACANE_FastLossR)
        {
         if(g_trade.PositionClose(ticket))
           {
            g_fastLossStreak++;
            PrintFormat("ACANE EXIT FAST_LOSS | ticket=%I64u seconds=%d r=%.2f streak=%d", ticket, secondsHeld, progressR, g_fastLossStreak);
            if(g_fastLossStreak >= ACANE_FastLossCooldownAfter)
              {
               g_cooldownUntil = TimeCurrent() + ACANE_FastLossCooldownSeconds;
               PrintFormat("ACANE GUARD | fast-loss cooldown until %s after %d losses",
                           TimeToString(g_cooldownUntil, TIME_DATE | TIME_SECONDS),
                           g_fastLossStreak);
              }
           }
         continue;
        }

      if(secondsHeld >= ACANE_MaxHoldSeconds)
        {
         if(g_trade.PositionClose(ticket))
           {
            if(progressR >= 0.0)
               g_fastLossStreak = 0;
            PrintFormat("ACANE EXIT TIME | ticket=%I64u seconds=%d r=%.2f", ticket, secondsHeld, progressR);
           }
         continue;
        }

      double newSl = sl;
      if(progressR >= ACANE_BreakevenR)
        {
         double be = sell ? openPrice - ACANE_BreakevenLockUsd : openPrice + ACANE_BreakevenLockUsd;
         if((sell && (sl <= 0.0 || be < sl)) || (!sell && (sl <= 0.0 || be > sl)))
            newSl = be;
        }
      if(progressR >= ACANE_TrailStartR)
        {
         double trail = sell ? current + atr * ACANE_TrailATR : current - atr * ACANE_TrailATR;
         if((sell && (newSl <= 0.0 || trail < newSl)) || (!sell && (newSl <= 0.0 || trail > newSl)))
            newSl = trail;
        }

      if(MathAbs(newSl - sl) >= _Point * 2.0 &&
         AcaneStopFits(sell, current, newSl))
        {
         g_trade.PositionModify(ticket, AcaneNormalizePrice(newSl), tp);
        }
     }
  }


void AcaneStatusLog()
  {
   if(!ACANE_LogStatus)
      return;
   datetime now = TimeCurrent();
   if(g_lastStatusTime > 0 && (now - g_lastStatusTime) < ACANE_StatusEverySeconds)
      return;
   g_lastStatusTime = now;
   PrintFormat("ACANE STATUS | tf=M1 open=%d buy=%d sell=%d spread=%.2f equity=%.2f openRisk=%.2f dailyStop=%s circuit=%s cooldown=%s",
               AcaneCountPositions(),
               AcaneCountPositions(1),
               AcaneCountPositions(-1),
               AcaneSpread(),
               AccountInfoDouble(ACCOUNT_EQUITY),
               AcaneOpenRiskPct(),
               g_dailyStopped ? "yes" : "no",
               g_circuitStopped ? "yes" : "no",
               (g_cooldownUntil > TimeCurrent()) ? "yes" : "no");
  }


int OnInit()
  {
   g_emaFast = iMA(_Symbol, ACANE_TF, ACANE_EMAFast, 0, MODE_EMA, PRICE_CLOSE);
   g_emaSlow = iMA(_Symbol, ACANE_TF, ACANE_EMASlow, 0, MODE_EMA, PRICE_CLOSE);
   g_m5Fast = iMA(_Symbol, PERIOD_M5, ACANE_M5Fast, 0, MODE_EMA, PRICE_CLOSE);
   g_m5Slow = iMA(_Symbol, PERIOD_M5, ACANE_M5Slow, 0, MODE_EMA, PRICE_CLOSE);
   g_atr = iATR(_Symbol, ACANE_TF, ACANE_ATRPeriod);
   g_rsi = iRSI(_Symbol, ACANE_TF, ACANE_RSI_Period, PRICE_CLOSE);
   g_bands = iBands(_Symbol, ACANE_TF, ACANE_BBandsPeriod, 0, ACANE_BBandsDeviation, PRICE_CLOSE);
   if(g_emaFast == INVALID_HANDLE || g_emaSlow == INVALID_HANDLE ||
      g_m5Fast == INVALID_HANDLE || g_m5Slow == INVALID_HANDLE ||
      g_atr == INVALID_HANDLE || g_rsi == INVALID_HANDLE ||
      g_bands == INVALID_HANDLE)
      return(INIT_FAILED);
   g_trade.SetExpertMagicNumber(ACANE_MAGIC);
   g_trade.SetDeviationInPoints(ACANE_DeviationPoints);
   g_trade.SetTypeFillingBySymbol(_Symbol);
   g_dayKey = -1;
   g_weekKey = -1;
   g_monthKey = -1;
   g_accountHighEquity = AccountInfoDouble(ACCOUNT_EQUITY);
   AcaneResetDailyGuardIfNeeded();
   AcaneResetWeeklyGuardIfNeeded();
   AcaneResetMonthlyGuardIfNeeded();
   PrintFormat("ACANE V2 RESEARCH AcaneM1_v2_stack2_nohour_4264 | symbol=%s tf=M1 risk=%.2f maxPos=%d sameSide=%d dailyLoss=%.2f accountCircuit=%.2f openRisk=%.2f basketStop=%.2f spreadMax=%.2f statusEvery=%d debugEvery=%d",
               _Symbol,
               ACANE_RiskPercent,
               ACANE_MaxPositions,
               ACANE_MaxSameSidePositions,
               ACANE_DailyMaxLossPct,
               ACANE_MaxAccountDrawdownPct,
               ACANE_MaxOpenRiskPct,
               ACANE_BasketLossStopPct,
               ACANE_MaxSpreadUsd,
               ACANE_StatusEverySeconds,
               ACANE_DebugEverySeconds);
   return(INIT_SUCCEEDED);
  }


void OnDeinit(const int reason)
  {
   if(g_emaFast != INVALID_HANDLE)
      IndicatorRelease(g_emaFast);
   if(g_emaSlow != INVALID_HANDLE)
      IndicatorRelease(g_emaSlow);
   if(g_m5Fast != INVALID_HANDLE)
      IndicatorRelease(g_m5Fast);
   if(g_m5Slow != INVALID_HANDLE)
      IndicatorRelease(g_m5Slow);
   if(g_atr != INVALID_HANDLE)
      IndicatorRelease(g_atr);
   if(g_rsi != INVALID_HANDLE)
      IndicatorRelease(g_rsi);
   if(g_bands != INVALID_HANDLE)
      IndicatorRelease(g_bands);
  }


void OnTick()
  {
   AcaneManagePositions();
   AcaneStatusLog();
   AcaneTryEntry();
  }
