#property copyright "OpenAI Codex"
#property version   "1.00"
#property strict
// Variant: v7

#include <Trade/Trade.mqh>
#include "InvictusForward1Spec.generated.mqh"

input double V7_TrendRiskPercent = 1.80;
input double V7_SidewaysRiskPercent = 0.60;
input double V7_SellRiskMultiplier = 0.70;
input double V7_HighScoreBuyRiskMultiplier = 1.10;
input int    V7_TrendMaxPositions = 3;
input int    V7_SidewaysMaxPositions = 2;
input double V7_TrendDailyLossCapPercent = 4.0;
input double V7_SidewaysDailyLossCapPercent = 2.5;
input bool   V7_SkipTradeBelowMinLot = true;

enum IF1BiasDirection
  {
   IF1_BIAS_BEARISH = -1,
   IF1_BIAS_BULLISH = 1
  };

enum IF1BosQuality
  {
   IF1_BOS_NONE = 0,
   IF1_BOS_CORRECTIVE = 1,
   IF1_BOS_IMPULSIVE = 2
  };

struct IF1StrategyState
  {
   int               dailyWins;
   double            dailyLossUsd;
   int               consecutiveLosses;
   datetime          lastLossTime;
   datetime          dayStart;
   double            dayStartBalance;
  };

struct IF1BiasInfo
  {
   int               direction;
   int               hhCount;
   int               llCount;
  };

struct IF1BosInfo
  {
   bool              valid;
   double            swingPrice;
   int               swingShift;
   int               quality;
   double            breakDistance;
  };

struct IF1ZoneInfo
  {
   bool              valid;
   int               candleAShift;
   int               candleBShift;
   double            zoneLow;
   double            zoneHigh;
   double            entryPrice;
   double            bodyRange;
   int               priorTests;
  };

struct IF1TrendSignal
  {
   bool              valid;
   int               direction;
   int               score;
   int               maxPositions;
   double            atr;
   double            rr;
   double            lot;
   double            stopLoss;
   double            takeProfit;
   bool              useLimitOrder;
   IF1BiasInfo       bias;
   IF1BosInfo        bos;
   IF1ZoneInfo       zone;
  };

struct IF1RangeCluster
  {
   datetime          dayStart;
   double            rangeHigh;
   double            rangeLow;
   int               count;
  };

struct IF1Diagnostics
  {
   int               trendChecks;
   int               trendWeekendBlocked;
   int               trendSpreadBlocked;
   int               trendDailyWinsBlocked;
   int               trendDailyLossBlocked;
   int               trendCooldownBlocked;
   int               trendToxicHourBlocked;
   int               trendCopyRatesBlocked;
   int               trendCopyAtrBlocked;
   int               trendAtrBlocked;
   int               trendHtfBlocked;
   int               trendBearishHourBlocked;
   int               trendBosBlocked;
   int               trendZoneBlocked;
   int               trendScoreBlocked;
   int               trendOpenPositionsBlocked;
   int               trendLotBlocked;
   int               trendOrderAttempts;
   int               trendOrdersPlaced;
   int               trendOrderRejected;
   int               trendClosedWins;
   int               trendClosedLosses;
   double            trendClosedPnl;
   int               sidewaysChecks;
   int               sidewaysAdxBlocked;
   int               sidewaysWeekendBlocked;
   int               sidewaysSpreadBlocked;
   int               sidewaysDailyWinsBlocked;
   int               sidewaysDailyLossBlocked;
   int               sidewaysCooldownBlocked;
   int               sidewaysToxicHourBlocked;
   int               sidewaysOpenPositionsBlocked;
   int               sidewaysCopyRatesBlocked;
   int               sidewaysCopyAtrBlocked;
   int               sidewaysAtrBlocked;
   int               sidewaysRangeBlocked;
   int               sidewaysEntryZoneBlocked;
   int               sidewaysClusterBlocked;
   int               sidewaysAskBlocked;
   int               sidewaysTpBlocked;
   int               sidewaysLotBlocked;
   int               sidewaysOrderAttempts;
   int               sidewaysOrdersPlaced;
   int               sidewaysOrderRejected;
   int               sidewaysClosedWins;
   int               sidewaysClosedLosses;
   double            sidewaysClosedPnl;
  };

CTrade            g_trade;
int               g_atrHandle = INVALID_HANDLE;
int               g_adxHandle = INVALID_HANDLE;
datetime          g_lastBarTime = 0;
IF1StrategyState  g_trendState;
IF1StrategyState  g_sidewaysState;
double            g_lastZonePrice = 0.0;
datetime          g_lastZoneTime = 0;
IF1RangeCluster   g_sidewaysClusters[32];
int               g_sidewaysClusterCount = 0;
IF1Diagnostics    g_diag;

static const double IF1_PENDING_CANCEL_LOSS_CAP_PCT = 4.0;
static const double IF1_BREAKEVEN_LOCK_USD = 2.0;
static const int    IF1_TIMED_PROFIT_CLOSE_HOURS_OVERRIDE = 5;
static const double IF1_SIDEWAYS_TP_FRACTION_OVERRIDE = 0.50;
static const double IF1_SIDEWAYS_MIN_TP_USD = 0.0;
static const double IF1_SIDEWAYS_ADX_THRESHOLD_OVERRIDE = 28.0;
static const int    IF1_COOLDOWN_BARS_OVERRIDE = 1;
static const double IF1_REFERENCE_GOLD_CONTRACT_SIZE = 100.0;
static const double IF1_TREND_MIN_SL_OVERRIDE = 12.0;
static const double IF1_TREND_MAX_SL_OVERRIDE = 28.0;
static const int    IF1_SCORE_BUY_MIN_OVERRIDE = 70;
static const int    IF1_SCORE_SELL_MIN_OVERRIDE = 85;
static const double IF1_BUY_MIN_BREAK_ATR_OVERRIDE = 0.30;
static const bool   IF1_GOLD_HIGH_SCORE_BUY_REQUIRE_IMPULSIVE_BOS = true;
static const int    IF1_TREND_HIGH_SCORE_BUY_RR_MIN = 95;
static const double IF1_TREND_HIGH_SCORE_BUY_RR_OVERRIDE = 2.45;
static const int    V7_TREND_LOW_SCORE_SELL_MAX = 79;
static const double V7_TREND_LOW_SCORE_SELL_RR_OVERRIDE = 0.0;
static const double V7_TREND_LOW_SCORE_SELL_LOT_MULT = 1.0;
static const bool   V7_USE_LOW_SCORE_SELL_BLOCK_MASK = false;
static const ulong  V7_LOW_SCORE_SELL_BLOCK_HOURS_MASK = 341600;
static const bool   V7_GOLD_HIGH_SCORE_SELL_REQUIRE_IMPULSIVE_BOS = false;
static const int    V7_GOLD_HIGH_SCORE_SELL_MIN_LL_HH_EDGE = 0;
static const double V7_GOLD_HIGH_SCORE_SELL_MIN_BREAK_ATR_OVERRIDE = 0.0;
static const double IF1_SIDEWAYS_ENTRY_ZONE_FRACTION_OVERRIDE = 0.40;
static const int    IF1_SIDEWAYS_CLUSTER_MAX_PER_DAY_OVERRIDE = 5;
static const bool   V7_ALLOW_ALL_SELL_HOURS = false;
static const bool   V7_TREND_MARKET_ONLY = false;
static const bool   V7_ENABLE_PENDING_MANAGER = true;
static const bool   V7_ENABLE_BREAKEVEN_MANAGER = true;
static int IF1TrendToxicHoursOverride[] = {3, 7, 8, 9, 10, 17};
static int IF1SidewaysToxicHoursOverride[] = {3, 19};


string IF1TrimSymbol(const string symbol)
  {
   string normalized = symbol;
   StringToUpper(normalized);
   return(normalized);
  }


bool IF1IsGoldSymbol()
  {
   string symbol = IF1TrimSymbol(_Symbol);
   return(StringFind(symbol, "XAUUSD") == 0);
  }


datetime IF1DayStart(const datetime ts)
  {
   return(StringToTime(TimeToString(ts, TIME_DATE)));
  }


int IF1HourOf(const datetime ts)
  {
   MqlDateTime dt;
   TimeToStruct(ts, dt);
   return(dt.hour);
  }


int IF1DayOfWeek(const datetime ts)
  {
   MqlDateTime dt;
   TimeToStruct(ts, dt);
   return(dt.day_of_week);
  }


bool IF1HourInArray(const int value, const int &values[])
  {
   for(int i = 0; i < ArraySize(values); i++)
      if(values[i] == value)
         return(true);
   return(false);
  }


bool IF1HourBlockedByMask(const int hour, const ulong mask)
  {
   if(hour < 0 || hour > 23)
      return(false);
   return(((mask >> hour) & 1) != 0);
  }


double IF1NormalizePrice(const double price)
  {
   return(NormalizeDouble(price, (int)SymbolInfoInteger(_Symbol, SYMBOL_DIGITS)));
  }


double IF1Clamp(const double value, const double minValue, const double maxValue)
  {
   return(MathMax(minValue, MathMin(maxValue, value)));
  }


double IF1NormalizeVolume(double volume)
  {
   const double minLot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
   const double maxLot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX);
   const double step   = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);

   if(step <= 0.0)
      return(0.0);

   volume = MathMax(volume, minLot);
   volume = MathMin(volume, maxLot);
   volume = MathFloor(volume / step) * step;
   volume = NormalizeDouble(volume, 2);
   if(volume < minLot)
      volume = minLot;
   return(volume);
  }


double IF1CurrentBalance()
  {
   return(AccountInfoDouble(ACCOUNT_BALANCE));
  }


double IF1CurrentRiskCapital()
  {
   double equity = AccountInfoDouble(ACCOUNT_EQUITY);
   if(equity > 0.0)
      return(equity);
   return(IF1CurrentBalance());
  }


void IF1InitState(IF1StrategyState &state)
  {
   state.dailyWins = 0;
   state.dailyLossUsd = 0.0;
   state.consecutiveLosses = 0;
   state.lastLossTime = 0;
   state.dayStart = IF1DayStart(TimeCurrent());
   state.dayStartBalance = IF1CurrentBalance();
  }


void IF1ResetDailyState(IF1StrategyState &state)
  {
   state.dailyWins = 0;
   state.dailyLossUsd = 0.0;
   state.dayStart = IF1DayStart(TimeCurrent());
   state.dayStartBalance = IF1CurrentBalance();
  }


void IF1RefreshDayStates()
  {
   datetime nowDay = IF1DayStart(TimeCurrent());
   if(g_trendState.dayStart != nowDay)
     {
      IF1ResetDailyState(g_trendState);
      g_lastZonePrice = 0.0;
      g_lastZoneTime = 0;
     }
   if(g_sidewaysState.dayStart != nowDay)
     {
      IF1ResetDailyState(g_sidewaysState);
      g_lastZonePrice = 0.0;
      g_lastZoneTime = 0;
      g_sidewaysClusterCount = 0;
      for(int i = 0; i < ArraySize(g_sidewaysClusters); i++)
        {
         g_sidewaysClusters[i].dayStart = 0;
         g_sidewaysClusters[i].rangeHigh = 0.0;
         g_sidewaysClusters[i].rangeLow = 0.0;
         g_sidewaysClusters[i].count = 0;
        }
     }
  }


bool IF1InCooldown(const IF1StrategyState &state)
  {
   if(state.lastLossTime <= 0)
      return(false);
   return((TimeCurrent() - state.lastLossTime) < (IF1_COOLDOWN_BARS_OVERRIDE * PeriodSeconds(PERIOD_M15)));
  }


bool IF1WeekendBlocked()
  {
   datetime now = TimeCurrent();
   int day = IF1DayOfWeek(now);
   int hour = IF1HourOf(now);

   if(day == 0 || day == 6)
      return(true);

   if(day == 5 && hour >= IF1_FRIDAY_CUTOFF_HOUR)
      return(true);

   return(false);
  }


bool IF1NewBar()
  {
   datetime currentBarTime = iTime(_Symbol, PERIOD_M15, 0);
   if(currentBarTime == 0 || currentBarTime == g_lastBarTime)
      return(false);
   g_lastBarTime = currentBarTime;
   return(true);
  }


bool IF1CopyRates(MqlRates &rates[], const int bars)
  {
   ArraySetAsSeries(rates, true);
   return(CopyRates(_Symbol, PERIOD_M15, 0, bars, rates) >= bars);
  }


bool IF1CopyRatesTf(MqlRates &rates[], const ENUM_TIMEFRAMES timeframe, const int bars)
  {
   ArraySetAsSeries(rates, true);
   return(CopyRates(_Symbol, timeframe, 0, bars, rates) >= bars);
  }


bool IF1CopyAtr(double &atrBuffer[], const int bars)
  {
   ArraySetAsSeries(atrBuffer, true);
   return(CopyBuffer(g_atrHandle, 0, 0, bars, atrBuffer) >= bars);
  }


double IF1GetAdxH4()
  {
   double values[2];
   ArraySetAsSeries(values, true);
   if(CopyBuffer(g_adxHandle, 0, 0, 2, values) < 1)
      return(-1.0);
   return(values[0]);
  }


int IF1CountOpenPositions(const ulong magic)
  {
   int count = 0;
   for(int i = PositionsTotal() - 1; i >= 0; i--)
     {
      ulong ticket = PositionGetTicket(i);
      if(ticket == 0 || !PositionSelectByTicket(ticket))
         continue;
      if(PositionGetString(POSITION_SYMBOL) != _Symbol)
         continue;
      if((ulong)PositionGetInteger(POSITION_MAGIC) != magic)
         continue;
      count++;
     }
   return(count);
  }


int IF1MaxTrendingPositions(const double balance)
  {
   return(V7_TrendMaxPositions);
  }


double IF1BaseCompoundingLot(const double balance)
  {
   double lot = 0.01;
   if(balance <= 20000.0)
      lot = MathFloor(balance / 500.0) * 0.01;
   else if(balance <= 50000.0)
      lot = 0.40 + MathFloor((balance - 20000.0) / 750.0) * 0.01;
   else
      lot = 0.80 + MathFloor((balance - 50000.0) / 1500.0) * 0.01;

   if(lot < IF1_MIN_LOT)
      lot = IF1_MIN_LOT;
  return(lot);
  }


double IF1RiskBudgetUsd(const bool sideways, const bool sell, const int score, const IF1StrategyState &state)
  {
   double riskPct = sideways ? V7_SidewaysRiskPercent : V7_TrendRiskPercent;
   riskPct *= IF1LossModifier(state.consecutiveLosses);

   if(sell)
      riskPct *= V7_SellRiskMultiplier;
   if(!sideways && !sell && score >= IF1_TREND_HIGH_SCORE_BUY_RR_MIN)
      riskPct *= V7_HighScoreBuyRiskMultiplier;

   riskPct = MathMax(riskPct, 0.0);
   return(IF1CurrentRiskCapital() * (riskPct / 100.0));
  }


double IF1LotForRisk(const ENUM_ORDER_TYPE orderType, const double entryPrice, const double stopLoss, const double riskUsd)
  {
   if(riskUsd <= 0.0 || entryPrice <= 0.0 || stopLoss <= 0.0 || MathAbs(entryPrice - stopLoss) <= 0.0)
      return(0.0);

   double lossPerLot = 0.0;
   if(!OrderCalcProfit(orderType, _Symbol, 1.0, entryPrice, stopLoss, lossPerLot))
      return(0.0);

   lossPerLot = MathAbs(lossPerLot);
   if(lossPerLot <= 0.0)
      return(0.0);

   double rawLot = riskUsd / lossPerLot;
   double minLot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
   if(V7_SkipTradeBelowMinLot && rawLot < minLot)
      return(0.0);

   double normalizedLot = IF1NormalizeVolume(rawLot);
   if(normalizedLot < minLot)
      return(0.0);
   return(normalizedLot);
  }


double IF1LossModifier(const int consecutiveLosses)
  {
   if(consecutiveLosses >= 7)
      return(0.10);
   if(consecutiveLosses >= 5)
      return(0.25);
   if(consecutiveLosses >= 3)
      return(0.50);
   return(1.0);
  }


double IF1StrategyLot(const bool sideways, const bool sell, const IF1StrategyState &state)
  {
   double lot = IF1BaseCompoundingLot(IF1CurrentBalance());
   lot *= IF1LossModifier(state.consecutiveLosses);
   if(sideways)
      lot *= IF1_SIDEWAYS_LOT_MODIFIER;
   if(sell)
      lot *= IF1_SELL_LOT_MODIFIER;

   if(IF1IsGoldSymbol())
     {
      double contractSize = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_CONTRACT_SIZE);
      if(contractSize > 0.0)
         lot *= (IF1_REFERENCE_GOLD_CONTRACT_SIZE / contractSize);
     }

   return(IF1NormalizeVolume(lot));
  }


bool IF1SpreadAllowed()
  {
   double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   return(ask > 0.0 && bid > 0.0);
  }


void IF1PrintDiagnostics()
  {
   PrintFormat("IF1 diag trend: checks=%d weekend=%d spread=%d dailyWins=%d dailyLoss=%d cooldown=%d toxic=%d copyRates=%d copyAtr=%d atr=%d htf=%d sellHour=%d bos=%d zone=%d score=%d openPos=%d lot=%d attempts=%d placed=%d rejected=%d closedWins=%d closedLosses=%d closedPnl=%.2f",
               g_diag.trendChecks,
               g_diag.trendWeekendBlocked,
               g_diag.trendSpreadBlocked,
               g_diag.trendDailyWinsBlocked,
               g_diag.trendDailyLossBlocked,
               g_diag.trendCooldownBlocked,
               g_diag.trendToxicHourBlocked,
               g_diag.trendCopyRatesBlocked,
               g_diag.trendCopyAtrBlocked,
               g_diag.trendAtrBlocked,
               g_diag.trendHtfBlocked,
               g_diag.trendBearishHourBlocked,
               g_diag.trendBosBlocked,
               g_diag.trendZoneBlocked,
               g_diag.trendScoreBlocked,
               g_diag.trendOpenPositionsBlocked,
               g_diag.trendLotBlocked,
               g_diag.trendOrderAttempts,
               g_diag.trendOrdersPlaced,
               g_diag.trendOrderRejected,
               g_diag.trendClosedWins,
               g_diag.trendClosedLosses,
               g_diag.trendClosedPnl);

   PrintFormat("IF1 diag sideways: checks=%d adx=%d weekend=%d spread=%d dailyWins=%d dailyLoss=%d cooldown=%d toxic=%d openPos=%d copyRates=%d copyAtr=%d atr=%d range=%d entryZone=%d cluster=%d ask=%d tp=%d lot=%d attempts=%d placed=%d rejected=%d closedWins=%d closedLosses=%d closedPnl=%.2f",
               g_diag.sidewaysChecks,
               g_diag.sidewaysAdxBlocked,
               g_diag.sidewaysWeekendBlocked,
               g_diag.sidewaysSpreadBlocked,
               g_diag.sidewaysDailyWinsBlocked,
               g_diag.sidewaysDailyLossBlocked,
               g_diag.sidewaysCooldownBlocked,
               g_diag.sidewaysToxicHourBlocked,
               g_diag.sidewaysOpenPositionsBlocked,
               g_diag.sidewaysCopyRatesBlocked,
               g_diag.sidewaysCopyAtrBlocked,
               g_diag.sidewaysAtrBlocked,
               g_diag.sidewaysRangeBlocked,
               g_diag.sidewaysEntryZoneBlocked,
               g_diag.sidewaysClusterBlocked,
               g_diag.sidewaysAskBlocked,
               g_diag.sidewaysTpBlocked,
               g_diag.sidewaysLotBlocked,
               g_diag.sidewaysOrderAttempts,
               g_diag.sidewaysOrdersPlaced,
               g_diag.sidewaysOrderRejected,
               g_diag.sidewaysClosedWins,
               g_diag.sidewaysClosedLosses,
               g_diag.sidewaysClosedPnl);
  }


void IF1PrintSymbolSpec()
  {
   PrintFormat("IF1 symbol spec: symbol=%s digits=%d point=%.5f tickSize=%.5f tickValue=%.5f contract=%.2f minLot=%.2f step=%.2f",
               _Symbol,
               (int)SymbolInfoInteger(_Symbol, SYMBOL_DIGITS),
               _Point,
               SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE),
               SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE),
               SymbolInfoDouble(_Symbol, SYMBOL_TRADE_CONTRACT_SIZE),
               SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN),
               SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP));
  }


void IF1ManagePendingOrders()
  {
   MqlRates rates[];
   double atrBuffer[];
   bool haveRates = IF1CopyRates(rates, 120);
   bool haveAtr = IF1CopyAtr(atrBuffer, 60);
   IF1BiasInfo bias;
   bias.direction = IF1_BIAS_BULLISH;
   if(haveRates && haveAtr && atrBuffer[1] > 0.0)
      bias = IF1DetectBias(rates);

   CTrade manager;
   manager.SetDeviationInPoints(IF1_SLIPPAGE_POINTS);
   manager.SetTypeFillingBySymbol(_Symbol);

   for(int i = OrdersTotal() - 1; i >= 0; i--)
     {
      ulong ticket = OrderGetTicket(i);
      if(ticket == 0 || !OrderSelect(ticket))
         continue;
      if(OrderGetString(ORDER_SYMBOL) != _Symbol)
         continue;

      ENUM_ORDER_TYPE type = (ENUM_ORDER_TYPE)OrderGetInteger(ORDER_TYPE);
      if(type != ORDER_TYPE_BUY_LIMIT && type != ORDER_TYPE_SELL_LIMIT)
         continue;

      ulong magic = (ulong)OrderGetInteger(ORDER_MAGIC);
      if(magic != IF1_TREND_MAGIC)
         continue;

      bool cancel = false;
      if(g_trendState.dayStartBalance > 0.0 && g_trendState.dailyLossUsd > (g_trendState.dayStartBalance * IF1_PENDING_CANCEL_LOSS_CAP_PCT / 100.0))
         cancel = true;

      if(!cancel && haveRates && haveAtr && atrBuffer[1] > 0.0)
        {
         if(type == ORDER_TYPE_BUY_LIMIT && bias.direction == IF1_BIAS_BEARISH)
            cancel = true;
         if(type == ORDER_TYPE_SELL_LIMIT && bias.direction == IF1_BIAS_BULLISH)
            cancel = true;
        }

      if(cancel && !manager.OrderDelete(ticket))
         PrintFormat("IF1 pending delete rejected: ticket=%I64u retcode=%d comment=%s", ticket, manager.ResultRetcode(), manager.ResultRetcodeDescription());
     }
  }


void IF1ManageBreakeven()
  {
   CTrade manager;
   manager.SetDeviationInPoints(IF1_SLIPPAGE_POINTS);
   manager.SetTypeFillingBySymbol(_Symbol);

   for(int i = PositionsTotal() - 1; i >= 0; i--)
     {
      ulong ticket = PositionGetTicket(i);
      if(ticket == 0 || !PositionSelectByTicket(ticket))
         continue;
      if(PositionGetString(POSITION_SYMBOL) != _Symbol)
         continue;

      ulong magic = (ulong)PositionGetInteger(POSITION_MAGIC);
      if(magic != IF1_TREND_MAGIC)
         continue;

      ENUM_POSITION_TYPE type = (ENUM_POSITION_TYPE)PositionGetInteger(POSITION_TYPE);
      double openPrice = PositionGetDouble(POSITION_PRICE_OPEN);
      double stopLoss = PositionGetDouble(POSITION_SL);
      double takeProfit = PositionGetDouble(POSITION_TP);
      if(stopLoss <= 0.0)
         continue;

      double currentPrice = (type == POSITION_TYPE_BUY) ? SymbolInfoDouble(_Symbol, SYMBOL_BID) : SymbolInfoDouble(_Symbol, SYMBOL_ASK);
      if(currentPrice <= 0.0)
         continue;

      double riskDistance = (type == POSITION_TYPE_BUY) ? (openPrice - stopLoss) : (stopLoss - openPrice);
      if(riskDistance <= 0.0)
         continue;

      double favorableMove = (type == POSITION_TYPE_BUY) ? (currentPrice - openPrice) : (openPrice - currentPrice);
      if(favorableMove < riskDistance)
         continue;

      double desiredSl = (type == POSITION_TYPE_BUY) ? (openPrice + IF1_BREAKEVEN_LOCK_USD) : (openPrice - IF1_BREAKEVEN_LOCK_USD);
      desiredSl = IF1NormalizePrice(desiredSl);

      if(type == POSITION_TYPE_BUY && stopLoss >= desiredSl)
         continue;
      if(type == POSITION_TYPE_SELL && stopLoss <= desiredSl)
         continue;

      if(!manager.PositionModify(ticket, desiredSl, takeProfit))
         PrintFormat("IF1 breakeven modify rejected: ticket=%I64u retcode=%d comment=%s", ticket, manager.ResultRetcode(), manager.ResultRetcodeDescription());
     }
  }


bool IF1IsSwingHigh(const MqlRates &rates[], const int shift)
  {
   if(shift < IF1_SWING_LOOKBACK || shift + IF1_SWING_LOOKBACK >= ArraySize(rates))
      return(false);

   for(int i = 1; i <= IF1_SWING_LOOKBACK; i++)
     {
      if(rates[shift].high <= rates[shift - i].high)
         return(false);
      if(rates[shift].high <= rates[shift + i].high)
         return(false);
     }
   return(true);
  }


bool IF1IsSwingLow(const MqlRates &rates[], const int shift)
  {
   if(shift < IF1_SWING_LOOKBACK || shift + IF1_SWING_LOOKBACK >= ArraySize(rates))
      return(false);

   for(int i = 1; i <= IF1_SWING_LOOKBACK; i++)
     {
      if(rates[shift].low >= rates[shift - i].low)
         return(false);
      if(rates[shift].low >= rates[shift + i].low)
         return(false);
     }
   return(true);
  }


double IF1CandleBodyRatio(const MqlRates &bar)
  {
   double range = bar.high - bar.low;
   if(range <= 0.0)
      return(0.0);
   return(MathAbs(bar.close - bar.open) / range);
  }


double IF1LowerWickRatio(const MqlRates &bar)
  {
   double range = bar.high - bar.low;
   if(range <= 0.0)
      return(1.0);
   double bodyLow = MathMin(bar.open, bar.close);
   return((bodyLow - bar.low) / range);
  }


double IF1UpperWickRatio(const MqlRates &bar)
  {
   double range = bar.high - bar.low;
   if(range <= 0.0)
      return(1.0);
   double bodyHigh = MathMax(bar.open, bar.close);
   return((bar.high - bodyHigh) / range);
  }


int IF1BosCandleQuality(const int direction, const MqlRates &rates[])
  {
   const MqlRates bosBar = rates[1];
   bool directionalBody = (direction > 0) ? (bosBar.close > bosBar.open) : (bosBar.close < bosBar.open);
   bool bodyStrong = IF1CandleBodyRatio(bosBar) >= IF1_MIN_BODY_RATIO;
   bool wickOkay = (direction > 0) ? (IF1UpperWickRatio(bosBar) <= 0.40) : (IF1LowerWickRatio(bosBar) <= 0.40);
   bool momentum = false;

   for(int i = 2; i <= 4 && i < ArraySize(rates); i++)
     {
      if(direction > 0 && rates[i].close > rates[i].open)
        {
         momentum = true;
         break;
        }
      if(direction < 0 && rates[i].close < rates[i].open)
        {
         momentum = true;
         break;
        }
     }

   if(directionalBody && bodyStrong && wickOkay && momentum)
      return(IF1_BOS_IMPULSIVE);
   if(directionalBody)
      return(IF1_BOS_CORRECTIVE);
   return(IF1_BOS_NONE);
  }


IF1BiasInfo IF1DetectBias(const MqlRates &rates[])
  {
   IF1BiasInfo info;
   info.hhCount = 0;
   info.llCount = 0;
   info.direction = IF1_BIAS_BULLISH;

   for(int k = 1; k <= 8; k++)
     {
      if(rates[k].high > rates[k + 1].high)
         info.hhCount++;
      if(rates[k].low < rates[k + 1].low)
         info.llCount++;
     }

   if(info.hhCount >= IF1_BULLISH_HH_MIN)
      info.direction = IF1_BIAS_BULLISH;
   else if(info.llCount >= IF1_BEARISH_LL_MIN)
      info.direction = IF1_BIAS_BEARISH;
   else if(info.llCount > info.hhCount)
      info.direction = IF1_BIAS_BEARISH;
   else
      info.direction = IF1_BIAS_BULLISH;

   return(info);
  }


IF1BosInfo IF1FindBos(const int direction, const MqlRates &rates[], const double atr)
  {
   IF1BosInfo info;
   info.valid = false;
   info.swingPrice = 0.0;
   info.swingShift = -1;
   info.quality = IF1_BOS_NONE;
   info.breakDistance = 0.0;

   const double closePrice = rates[1].close;
   const double minBreakDistance = atr * IF1_MIN_BREAK_ATR;
   const int maxShift = MathMin(ArraySize(rates) - IF1_SWING_LOOKBACK - 1, IF1_MAX_BOS_BARS_BACK);

   for(int shift = IF1_SWING_LOOKBACK + 1; shift <= maxShift; shift++)
     {
      if(direction > 0 && IF1IsSwingHigh(rates, shift))
        {
         const double swing = rates[shift].high;
         if(closePrice > swing && (closePrice - swing) >= minBreakDistance)
           {
            info.valid = true;
            info.swingPrice = swing;
            info.swingShift = shift;
            info.breakDistance = closePrice - swing;
            info.quality = IF1BosCandleQuality(direction, rates);
            return(info);
           }
        }

      if(direction < 0 && IF1IsSwingLow(rates, shift))
        {
         const double swing = rates[shift].low;
         if(closePrice < swing && (swing - closePrice) >= minBreakDistance)
           {
            info.valid = true;
            info.swingPrice = swing;
            info.swingShift = shift;
            info.breakDistance = swing - closePrice;
            info.quality = IF1BosCandleQuality(direction, rates);
            return(info);
           }
        }
     }

   return(info);
  }


int IF1CountZoneTests(const MqlRates &rates[], const int newerShiftStart, const double zoneLow, const double zoneHigh)
  {
   int touches = 0;
   for(int shift = newerShiftStart; shift >= 1; shift--)
     {
      if(rates[shift].low <= zoneHigh && rates[shift].high >= zoneLow)
         touches++;
     }
   return(touches);
  }


bool IF1BodyEngulfs(const MqlRates &candleA, const MqlRates &candleB)
  {
   double aHigh = MathMax(candleA.open, candleA.close);
   double aLow  = MathMin(candleA.open, candleA.close);
   double bHigh = MathMax(candleB.open, candleB.close);
   double bLow  = MathMin(candleB.open, candleB.close);
   return(bHigh > aHigh && bLow < aLow);
  }


IF1ZoneInfo IF1FindZone(const int direction, const MqlRates &rates[])
  {
   IF1ZoneInfo info;
   info.valid = false;
   info.candleAShift = -1;
   info.candleBShift = -1;
   info.zoneLow = 0.0;
   info.zoneHigh = 0.0;
   info.entryPrice = 0.0;
   info.bodyRange = 0.0;
   info.priorTests = 0;

   const int maxShift = MathMin(ArraySize(rates) - 2, IF1_ZONE_SEARCH_WINDOW + 1);
   for(int bShift = 2; bShift <= maxShift; bShift++)
     {
      int aShift = bShift + 1;
      if(aShift >= ArraySize(rates))
         break;

      const MqlRates candleA = rates[aShift];
      const MqlRates candleB = rates[bShift];
      if(!IF1BodyEngulfs(candleA, candleB))
         continue;

      if(direction > 0 && !(candleB.close > candleB.open))
         continue;
      if(direction < 0 && !(candleB.close < candleB.open))
         continue;

      double zoneLow = MathMin(candleB.open, candleB.close);
      double zoneHigh = MathMax(candleB.open, candleB.close);
      double bodyRange = zoneHigh - zoneLow;
      if(bodyRange <= 0.0 || bodyRange > IF1_MAX_ZONE_RANGE_USD)
         continue;

      int priorTests = IF1CountZoneTests(rates, bShift - 1, zoneLow, zoneHigh);
      if(priorTests > IF1_MAX_ZONE_PRIOR_TESTS)
         continue;

      info.valid = true;
      info.candleAShift = aShift;
      info.candleBShift = bShift;
      info.zoneLow = zoneLow;
      info.zoneHigh = zoneHigh;
      info.bodyRange = bodyRange;
      info.priorTests = priorTests;
      if(direction > 0)
         info.entryPrice = zoneLow + (bodyRange * IF1_ENTRY_BODY_RATIO);
      else
         info.entryPrice = zoneHigh - (bodyRange * IF1_ENTRY_BODY_RATIO);
      return(info);
     }
   return(info);
  }


bool IF1ZoneCooldownBlocked(const IF1ZoneInfo &zone)
  {
   if(g_lastZoneTime <= 0)
      return(false);
   if(MathAbs(g_lastZonePrice - zone.entryPrice) > IF1_ZONE_COOLDOWN_TOLERANCE_USD)
      return(false);
   return((TimeCurrent() - g_lastZoneTime) <= (IF1_ZONE_COOLDOWN_BARS * PeriodSeconds(PERIOD_M15)));
  }


double IF1AverageAtr50(const double &atrBuffer[])
  {
   double total = 0.0;
   int count = 0;
   for(int i = 1; i <= 50 && i < ArraySize(atrBuffer); i++)
     {
      total += atrBuffer[i];
      count++;
     }
   if(count == 0)
      return(0.0);
   return(total / count);
  }


bool IF1HasFvg(const int direction, const MqlRates &rates[])
  {
   if(ArraySize(rates) < 4)
      return(false);
   if(direction > 0)
      return(rates[1].low > rates[3].high);
   return(rates[1].high < rates[3].low);
  }


bool IF1HasRetest(const int direction, const MqlRates &rates[], const double swingPrice)
  {
   const MqlRates bar = rates[1];
   if(direction > 0)
     {
      bool touched = bar.low <= swingPrice && bar.close > swingPrice;
      bool rejection = IF1LowerWickRatio(bar) >= 0.50 || bar.close > bar.open;
      return(touched && rejection);
     }

   bool touched = bar.high >= swingPrice && bar.close < swingPrice;
   bool rejection = IF1UpperWickRatio(bar) >= 0.50 || bar.close < bar.open;
   return(touched && rejection);
  }


bool IF1HasSweep(const int direction, const MqlRates &rates[], const double swingPrice)
  {
   for(int shift = 1; shift <= 5 && shift < ArraySize(rates); shift++)
     {
      if(direction > 0 && rates[shift].low < swingPrice && rates[shift].close > swingPrice)
         return(true);
      if(direction < 0 && rates[shift].high > swingPrice && rates[shift].close < swingPrice)
         return(true);
     }
   return(false);
  }


int IF1ScoreTrendSignal(const int direction, const IF1BiasInfo &bias, const IF1BosInfo &bos, const double atr, const double avgAtr, const MqlRates &rates[])
  {
   int score = IF1_SCORE_ZONE;

   if(avgAtr > 0.0 && atr < (avgAtr * 1.30))
      score += IF1_SCORE_VOLATILITY;
   if(IF1HasFvg(direction, rates))
      score += IF1_SCORE_FVG;
   if(IF1HasRetest(direction, rates, bos.swingPrice))
      score += IF1_SCORE_RETEST;
   if(IF1HasSweep(direction, rates, bos.swingPrice))
      score += IF1_SCORE_SWEEP;
   if(direction > 0 && bias.hhCount >= IF1_BULLISH_HH_MIN)
      score += IF1_SCORE_TREND;
   if(direction < 0 && bias.llCount >= IF1_BEARISH_LL_MIN)
      score += IF1_SCORE_TREND;
   if(direction > 0 && IF1IsGoldSymbol())
      score += IF1_SCORE_GOLD_BUY_BONUS;

   return(score);
  }


bool IF1SubmitTrendOrder(IF1TrendSignal &signal)
  {
   double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   if(ask <= 0.0 || bid <= 0.0)
      return(false);

   const bool sell = signal.direction < 0;
   const string comment = StringFormat("IF1 Trend %s S%d", sell ? "SELL" : "BUY", signal.score);

   g_trade.SetExpertMagicNumber(IF1_TREND_MAGIC);
   g_trade.SetDeviationInPoints(IF1_SLIPPAGE_POINTS);
   g_trade.SetTypeFillingBySymbol(_Symbol);
   g_diag.trendOrderAttempts++;

   bool ok = false;
   if(!sell)
     {
      signal.useLimitOrder = !V7_TREND_MARKET_ONLY && ask > signal.zone.entryPrice;
      if(signal.useLimitOrder)
         ok = g_trade.BuyLimit(signal.lot, IF1NormalizePrice(signal.zone.entryPrice), _Symbol, signal.stopLoss, signal.takeProfit,
                               ORDER_TIME_SPECIFIED, TimeCurrent() + IF1_PENDING_EXPIRY_SECONDS, comment);
      else
         ok = g_trade.Buy(signal.lot, _Symbol, 0.0, signal.stopLoss, signal.takeProfit, comment);
     }
   else
     {
      signal.useLimitOrder = !V7_TREND_MARKET_ONLY && bid < signal.zone.entryPrice;
      if(signal.useLimitOrder)
         ok = g_trade.SellLimit(signal.lot, IF1NormalizePrice(signal.zone.entryPrice), _Symbol, signal.stopLoss, signal.takeProfit,
                                ORDER_TIME_SPECIFIED, TimeCurrent() + IF1_PENDING_EXPIRY_SECONDS, comment);
      else
         ok = g_trade.Sell(signal.lot, _Symbol, 0.0, signal.stopLoss, signal.takeProfit, comment);
     }

   if(ok)
     {
      g_diag.trendOrdersPlaced++;
      g_lastZonePrice = signal.zone.entryPrice;
      g_lastZoneTime = TimeCurrent();
     }
   else
     {
      g_diag.trendOrderRejected++;
      PrintFormat("IF1 trend order rejected: retcode=%d comment=%s", g_trade.ResultRetcode(), g_trade.ResultRetcodeDescription());
     }

   return(ok);
  }


bool IF1EvaluateTrending()
  {
   g_diag.trendChecks++;
   if(IF1WeekendBlocked())
     {
      g_diag.trendWeekendBlocked++;
      return(false);
     }
   if(!IF1SpreadAllowed())
     {
      g_diag.trendSpreadBlocked++;
      return(false);
     }
   if(g_trendState.dailyWins >= IF1_TREND_KILLSWITCH_WINS)
     {
      g_diag.trendDailyWinsBlocked++;
      return(false);
     }
   if(g_trendState.dayStartBalance > 0.0 && g_trendState.dailyLossUsd > (g_trendState.dayStartBalance * V7_TrendDailyLossCapPercent / 100.0))
     {
      g_diag.trendDailyLossBlocked++;
      return(false);
     }
   if(IF1InCooldown(g_trendState))
     {
      g_diag.trendCooldownBlocked++;
      return(false);
     }
   if(IF1HourInArray(IF1HourOf(TimeCurrent()), IF1TrendToxicHoursOverride))
     {
      g_diag.trendToxicHourBlocked++;
      return(false);
     }

   MqlRates rates[];
   double atrBuffer[];
   if(!IF1CopyRates(rates, 120))
     {
      g_diag.trendCopyRatesBlocked++;
      return(false);
     }
   if(!IF1CopyAtr(atrBuffer, 60))
     {
      g_diag.trendCopyAtrBlocked++;
      return(false);
     }

   double atr = atrBuffer[1];
   double avgAtr = IF1AverageAtr50(atrBuffer);
   if(atr <= 0.0)
     {
      g_diag.trendAtrBlocked++;
      return(false);
     }

   IF1BiasInfo bias = IF1DetectBias(rates);
   if(bias.direction == IF1_BIAS_BEARISH && !V7_ALLOW_ALL_SELL_HOURS && !IF1HourInArray(IF1HourOf(TimeCurrent()), IF1TrendSellHours))
     {
      g_diag.trendBearishHourBlocked++;
      return(false);
     }

   IF1BosInfo bos = IF1FindBos(bias.direction, rates, atr);
   if(!bos.valid || bos.quality == IF1_BOS_NONE)
     {
      g_diag.trendBosBlocked++;
      return(false);
     }

   IF1ZoneInfo zone = IF1FindZone(bias.direction, rates);
   if(!zone.valid || IF1ZoneCooldownBlocked(zone))
     {
      g_diag.trendZoneBlocked++;
      return(false);
     }

   int score = IF1ScoreTrendSignal(bias.direction, bias, bos, atr, avgAtr, rates);
   if(bias.direction > 0 && score < IF1_SCORE_BUY_MIN_OVERRIDE)
     {
      g_diag.trendScoreBlocked++;
      return(false);
     }
   if(bias.direction < 0 && (score < IF1_SCORE_SELL_MIN_OVERRIDE || bos.quality != IF1_BOS_IMPULSIVE))
     {
      g_diag.trendScoreBlocked++;
      return(false);
     }

   if(bias.direction < 0 &&
      V7_USE_LOW_SCORE_SELL_BLOCK_MASK &&
      score <= V7_TREND_LOW_SCORE_SELL_MAX &&
      IF1HourBlockedByMask(IF1HourOf(TimeCurrent()), V7_LOW_SCORE_SELL_BLOCK_HOURS_MASK))
     {
      g_diag.trendScoreBlocked++;
      return(false);
     }

   if(bias.direction < 0 &&
      V7_GOLD_HIGH_SCORE_SELL_REQUIRE_IMPULSIVE_BOS &&
      IF1IsGoldSymbol() &&
      score >= IF1_TREND_HIGH_SCORE_BUY_RR_MIN)
     {
      if(bos.quality != IF1_BOS_IMPULSIVE ||
         (bias.llCount - bias.hhCount) < V7_GOLD_HIGH_SCORE_SELL_MIN_LL_HH_EDGE ||
         (V7_GOLD_HIGH_SCORE_SELL_MIN_BREAK_ATR_OVERRIDE > 0.0 &&
          bos.breakDistance < (atr * V7_GOLD_HIGH_SCORE_SELL_MIN_BREAK_ATR_OVERRIDE)))
        {
         g_diag.trendScoreBlocked++;
         return(false);
        }
     }

   if(bias.direction > 0 && IF1_BUY_MIN_BREAK_ATR_OVERRIDE > 0.0 && bos.breakDistance < (atr * IF1_BUY_MIN_BREAK_ATR_OVERRIDE))
     {
      g_diag.trendScoreBlocked++;
      return(false);
     }

   if(bias.direction > 0 &&
      IF1_GOLD_HIGH_SCORE_BUY_REQUIRE_IMPULSIVE_BOS &&
      score >= IF1_TREND_HIGH_SCORE_BUY_RR_MIN &&
      bos.quality != IF1_BOS_IMPULSIVE)
     {
      g_diag.trendScoreBlocked++;
      return(false);
     }

   int openPositions = IF1CountOpenPositions(IF1_TREND_MAGIC);
   int maxPositions = IF1MaxTrendingPositions(IF1CurrentBalance());
   if(openPositions >= maxPositions)
     {
      g_diag.trendOpenPositionsBlocked++;
      return(false);
     }

   double stopDistance = IF1Clamp(MathAbs(zone.entryPrice - ((bias.direction > 0 ? zone.zoneLow : zone.zoneHigh))) + (atr * IF1_TREND_SL_ATR_BUFFER),
                                  IF1_TREND_MIN_SL_OVERRIDE, IF1_TREND_MAX_SL_OVERRIDE);
   double rr = (score >= IF1_SCORE_RR_BOOST_MIN) ? IF1_TREND_TP_RR_BOOST : IF1_TREND_TP_RR_DEFAULT;
   if(bias.direction > 0 && score >= IF1_TREND_HIGH_SCORE_BUY_RR_MIN)
      rr = MathMax(rr, IF1_TREND_HIGH_SCORE_BUY_RR_OVERRIDE);
   if(bias.direction < 0 && score <= V7_TREND_LOW_SCORE_SELL_MAX && V7_TREND_LOW_SCORE_SELL_RR_OVERRIDE > 0.0)
      rr = MathMin(rr, V7_TREND_LOW_SCORE_SELL_RR_OVERRIDE);

   IF1TrendSignal signal;
   signal.valid = true;
   signal.direction = bias.direction;
   signal.score = score;
   signal.maxPositions = maxPositions;
   signal.atr = atr;
   signal.rr = rr;
   signal.bias = bias;
   signal.bos = bos;
   signal.zone = zone;
   signal.useLimitOrder = false;

   double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   if(ask <= 0.0 || bid <= 0.0)
     {
      g_diag.trendSpreadBlocked++;
      return(false);
     }

   double entryPrice = 0.0;
   bool sell = (signal.direction < 0);
   if(signal.direction > 0)
     {
      signal.useLimitOrder = ask > signal.zone.entryPrice;
      entryPrice = signal.useLimitOrder ? signal.zone.entryPrice : ask;
      signal.stopLoss = IF1NormalizePrice(entryPrice - stopDistance);
      signal.takeProfit = IF1NormalizePrice(entryPrice + (stopDistance * rr));
     }
   else
     {
      signal.useLimitOrder = bid < signal.zone.entryPrice;
      entryPrice = signal.useLimitOrder ? signal.zone.entryPrice : bid;
      signal.stopLoss = IF1NormalizePrice(entryPrice + stopDistance);
      signal.takeProfit = IF1NormalizePrice(entryPrice - (stopDistance * rr));
     }

   double riskUsd = IF1RiskBudgetUsd(false, sell, score, g_trendState);
   if(sell && score <= V7_TREND_LOW_SCORE_SELL_MAX)
      riskUsd *= V7_TREND_LOW_SCORE_SELL_LOT_MULT;
   signal.lot = IF1LotForRisk(sell ? ORDER_TYPE_SELL : ORDER_TYPE_BUY, entryPrice, signal.stopLoss, riskUsd);
   if(signal.lot < IF1_MIN_LOT)
     {
      g_diag.trendLotBlocked++;
      return(false);
     }

   return(IF1SubmitTrendOrder(signal));
  }


int IF1FindSidewaysCluster(const double rangeHigh, const double rangeLow, const datetime dayStart)
  {
   for(int i = 0; i < g_sidewaysClusterCount; i++)
     {
      if(g_sidewaysClusters[i].dayStart != dayStart)
         continue;
      if(MathAbs(g_sidewaysClusters[i].rangeHigh - rangeHigh) < IF1_SIDEWAYS_CLUSTER_TOLERANCE_USD &&
         MathAbs(g_sidewaysClusters[i].rangeLow - rangeLow) < IF1_SIDEWAYS_CLUSTER_TOLERANCE_USD)
         return(i);
     }
   return(-1);
  }


void IF1RegisterSidewaysCluster(const double rangeHigh, const double rangeLow)
  {
   datetime dayStart = IF1DayStart(TimeCurrent());
   int index = IF1FindSidewaysCluster(rangeHigh, rangeLow, dayStart);
   if(index >= 0)
     {
      g_sidewaysClusters[index].count++;
      return;
     }

   if(g_sidewaysClusterCount >= ArraySize(g_sidewaysClusters))
      return;

   g_sidewaysClusters[g_sidewaysClusterCount].dayStart = dayStart;
   g_sidewaysClusters[g_sidewaysClusterCount].rangeHigh = rangeHigh;
   g_sidewaysClusters[g_sidewaysClusterCount].rangeLow = rangeLow;
   g_sidewaysClusters[g_sidewaysClusterCount].count = 1;
   g_sidewaysClusterCount++;
  }


int IF1SidewaysClusterCount(const double rangeHigh, const double rangeLow)
  {
   int index = IF1FindSidewaysCluster(rangeHigh, rangeLow, IF1DayStart(TimeCurrent()));
   if(index < 0)
      return(0);
   return(g_sidewaysClusters[index].count);
  }


bool IF1SubmitSidewaysOrder(const double lot, const double stopLoss, const double takeProfit, const double rangeHigh, const double rangeLow)
  {
   const string comment = "IF1 Sideways BUY";
   g_trade.SetExpertMagicNumber(IF1_SIDEWAYS_MAGIC);
   g_trade.SetDeviationInPoints(IF1_SLIPPAGE_POINTS);
   g_trade.SetTypeFillingBySymbol(_Symbol);
   g_diag.sidewaysOrderAttempts++;

   bool ok = g_trade.Buy(lot, _Symbol, 0.0, stopLoss, takeProfit, comment);
   if(ok)
     {
      g_diag.sidewaysOrdersPlaced++;
      IF1RegisterSidewaysCluster(rangeHigh, rangeLow);
     }
   else
     {
      g_diag.sidewaysOrderRejected++;
      PrintFormat("IF1 sideways order rejected: retcode=%d comment=%s", g_trade.ResultRetcode(), g_trade.ResultRetcodeDescription());
     }
   return(ok);
  }


bool IF1EvaluateSideways()
  {
   g_diag.sidewaysChecks++;
   if(IF1GetAdxH4() >= IF1_SIDEWAYS_ADX_THRESHOLD_OVERRIDE)
     {
      g_diag.sidewaysAdxBlocked++;
      return(false);
     }
   if(IF1WeekendBlocked())
     {
      g_diag.sidewaysWeekendBlocked++;
      return(false);
     }
   if(!IF1SpreadAllowed())
     {
      g_diag.sidewaysSpreadBlocked++;
      return(false);
     }
   if(g_sidewaysState.dailyWins >= IF1_SIDEWAYS_WINS_CAP)
     {
      g_diag.sidewaysDailyWinsBlocked++;
      return(false);
     }
   if(g_sidewaysState.dayStartBalance > 0.0 && g_sidewaysState.dailyLossUsd > (g_sidewaysState.dayStartBalance * V7_SidewaysDailyLossCapPercent / 100.0))
     {
      g_diag.sidewaysDailyLossBlocked++;
      return(false);
     }
   if(IF1InCooldown(g_sidewaysState))
     {
      g_diag.sidewaysCooldownBlocked++;
      return(false);
     }
   if(IF1HourInArray(IF1HourOf(TimeCurrent()), IF1SidewaysToxicHoursOverride))
     {
      g_diag.sidewaysToxicHourBlocked++;
      return(false);
     }
   if(IF1CountOpenPositions(IF1_SIDEWAYS_MAGIC) >= V7_SidewaysMaxPositions)
     {
      g_diag.sidewaysOpenPositionsBlocked++;
      return(false);
     }

   MqlRates rates[];
   double atrBuffer[];
   if(!IF1CopyRates(rates, 64))
     {
      g_diag.sidewaysCopyRatesBlocked++;
      return(false);
     }
   if(!IF1CopyAtr(atrBuffer, 20))
     {
      g_diag.sidewaysCopyAtrBlocked++;
      return(false);
     }

   double atr = atrBuffer[1];
   if(atr <= 0.0)
     {
      g_diag.sidewaysAtrBlocked++;
      return(false);
     }

   double rangeHigh = rates[1].high;
   double rangeLow = rates[1].low;
   for(int i = 1; i <= IF1_SIDEWAYS_RANGE_BARS && i < ArraySize(rates); i++)
     {
      rangeHigh = MathMax(rangeHigh, rates[i].high);
      rangeLow = MathMin(rangeLow, rates[i].low);
     }

   double rangeSize = rangeHigh - rangeLow;
   if(rangeSize < IF1_SIDEWAYS_MIN_RANGE_USD || rangeSize > (atr * IF1_SIDEWAYS_MAX_RANGE_ATR_MULT))
     {
      g_diag.sidewaysRangeBlocked++;
      return(false);
     }

   double buyZoneTop = rangeLow + (rangeSize * IF1_SIDEWAYS_ENTRY_ZONE_FRACTION_OVERRIDE);
   if(rates[1].close > buyZoneTop)
     {
      g_diag.sidewaysEntryZoneBlocked++;
      return(false);
     }

   if(IF1SidewaysClusterCount(rangeHigh, rangeLow) >= IF1_SIDEWAYS_CLUSTER_MAX_PER_DAY_OVERRIDE)
     {
      g_diag.sidewaysClusterBlocked++;
      return(false);
     }

   double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   if(ask <= 0.0)
     {
      g_diag.sidewaysAskBlocked++;
      return(false);
     }

   double rawStopDistance = ask - (rangeLow - (atr * IF1_SIDEWAYS_SL_ATR_BUFFER));
   double stopDistance = IF1Clamp(rawStopDistance, IF1_SIDEWAYS_SL_MIN_USD, IF1_SIDEWAYS_SL_MAX_USD);
   double stopLoss = IF1NormalizePrice(ask - stopDistance);
   double targetDistance = MathMax(rangeSize * IF1_SIDEWAYS_TP_FRACTION_OVERRIDE, IF1_SIDEWAYS_MIN_TP_USD);
   double takeProfit = IF1NormalizePrice(rangeLow + targetDistance);
   if(takeProfit <= ask)
     {
      g_diag.sidewaysTpBlocked++;
      return(false);
     }

   double riskUsd = IF1RiskBudgetUsd(true, false, 0, g_sidewaysState);
   double lot = IF1LotForRisk(ORDER_TYPE_BUY, ask, stopLoss, riskUsd);
   if(lot < IF1_MIN_LOT)
     {
      g_diag.sidewaysLotBlocked++;
      return(false);
     }

   return(IF1SubmitSidewaysOrder(lot, stopLoss, takeProfit, rangeHigh, rangeLow));
  }


void IF1ManageTimedProfitClose()
  {
   CTrade closer;
   closer.SetDeviationInPoints(IF1_SLIPPAGE_POINTS);
   closer.SetTypeFillingBySymbol(_Symbol);

   for(int i = PositionsTotal() - 1; i >= 0; i--)
     {
      ulong ticket = PositionGetTicket(i);
      if(ticket == 0 || !PositionSelectByTicket(ticket))
         continue;
      if(PositionGetString(POSITION_SYMBOL) != _Symbol)
         continue;

      ulong magic = (ulong)PositionGetInteger(POSITION_MAGIC);
      if(magic != IF1_TREND_MAGIC && magic != IF1_SIDEWAYS_MAGIC)
         continue;

      datetime openTime = (datetime)PositionGetInteger(POSITION_TIME);
      if((TimeCurrent() - openTime) < (IF1_TIMED_PROFIT_CLOSE_HOURS_OVERRIDE * 3600))
         continue;

      double volume = PositionGetDouble(POSITION_VOLUME);
      double profit = PositionGetDouble(POSITION_PROFIT) + PositionGetDouble(POSITION_SWAP);
      double threshold = (volume / 0.01) * IF1_TIMED_PROFIT_USD_PER_001;
      if(profit >= threshold)
         closer.PositionClose(ticket);
     }
  }


void IF1UpdateStateFromClosedDeal(const ulong deal)
  {
   if(!HistoryDealSelect(deal))
      return;

   if(HistoryDealGetString(deal, DEAL_SYMBOL) != _Symbol)
      return;
   if((ENUM_DEAL_ENTRY)HistoryDealGetInteger(deal, DEAL_ENTRY) != DEAL_ENTRY_OUT)
      return;

   ulong magic = (ulong)HistoryDealGetInteger(deal, DEAL_MAGIC);
   double pnl = HistoryDealGetDouble(deal, DEAL_PROFIT) + HistoryDealGetDouble(deal, DEAL_SWAP) + HistoryDealGetDouble(deal, DEAL_COMMISSION);
   datetime dealTime = (datetime)HistoryDealGetInteger(deal, DEAL_TIME);
   datetime dayStart = IF1DayStart(dealTime);

   if(magic == IF1_TREND_MAGIC)
     {
      g_diag.trendClosedPnl += pnl;
      if(g_trendState.dayStart != dayStart)
        {
         g_trendState.dayStart = dayStart;
         g_trendState.dailyWins = 0;
         g_trendState.dailyLossUsd = 0.0;
         g_trendState.dayStartBalance = IF1CurrentBalance();
        }

      if(pnl > 0.0)
        {
         g_diag.trendClosedWins++;
         g_trendState.dailyWins++;
         g_trendState.consecutiveLosses = 0;
        }
      else if(pnl < 0.0)
        {
         g_diag.trendClosedLosses++;
         g_trendState.dailyLossUsd += MathAbs(pnl);
         g_trendState.consecutiveLosses++;
         g_trendState.lastLossTime = dealTime;
        }
      return;
     }

   if(magic == IF1_SIDEWAYS_MAGIC)
     {
      g_diag.sidewaysClosedPnl += pnl;
      if(g_sidewaysState.dayStart != dayStart)
        {
         g_sidewaysState.dayStart = dayStart;
         g_sidewaysState.dailyWins = 0;
         g_sidewaysState.dailyLossUsd = 0.0;
         g_sidewaysState.dayStartBalance = IF1CurrentBalance();
        }

      if(pnl > 0.0)
        {
         g_diag.sidewaysClosedWins++;
         g_sidewaysState.dailyWins++;
         g_sidewaysState.consecutiveLosses = 0;
        }
      else if(pnl < 0.0)
        {
         g_diag.sidewaysClosedLosses++;
         g_sidewaysState.dailyLossUsd += MathAbs(pnl);
         g_sidewaysState.consecutiveLosses++;
         g_sidewaysState.lastLossTime = dealTime;
        }
     }
  }


int OnInit()
  {
   if(_Period != IF1_REQUIRED_TF)
     {
      Print("InvictusForward1M15 requires M15.");
      return(INIT_PARAMETERS_INCORRECT);
     }

   if(!IF1IsGoldSymbol())
      Print("Warning: this EA is tuned for XAUUSD variants. Current symbol=", _Symbol);

   if(AccountInfoInteger(ACCOUNT_MARGIN_MODE) != ACCOUNT_MARGIN_MODE_RETAIL_HEDGING)
      Print("Warning: multiple independent positions require a hedging account mode.");

   g_atrHandle = iATR(_Symbol, PERIOD_M15, 14);
   g_adxHandle = iADX(_Symbol, PERIOD_H4, 14);
   if(g_atrHandle == INVALID_HANDLE || g_adxHandle == INVALID_HANDLE)
     {
      Print("Failed to create indicator handles.");
      return(INIT_FAILED);
     }

   IF1InitState(g_trendState);
   IF1InitState(g_sidewaysState);
   IF1PrintSymbolSpec();
   g_trade.SetDeviationInPoints(IF1_SLIPPAGE_POINTS);
   g_trade.SetTypeFillingBySymbol(_Symbol);
   return(INIT_SUCCEEDED);
  }


void OnDeinit(const int reason)
  {
   if(MQLInfoInteger(MQL_TESTER))
      IF1PrintDiagnostics();
   if(g_atrHandle != INVALID_HANDLE)
      IndicatorRelease(g_atrHandle);
   if(g_adxHandle != INVALID_HANDLE)
      IndicatorRelease(g_adxHandle);
  }


void OnTick()
  {
   IF1RefreshDayStates();
   if(V7_ENABLE_PENDING_MANAGER)
      IF1ManagePendingOrders();
   if(V7_ENABLE_BREAKEVEN_MANAGER)
      IF1ManageBreakeven();
   IF1ManageTimedProfitClose();

   if(!IF1NewBar())
      return;

   IF1EvaluateTrending();
   IF1EvaluateSideways();
  }


void OnTradeTransaction(const MqlTradeTransaction &trans, const MqlTradeRequest &request, const MqlTradeResult &result)
  {
   if(trans.type == TRADE_TRANSACTION_DEAL_ADD)
      IF1UpdateStateFromClosedDeal(trans.deal);
  }
