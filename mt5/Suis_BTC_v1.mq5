#property copyright "OpenAI Codex"
#property version   "1.10"
#property strict
// Suis_BTC_v1: BTCUSD multi-timeframe trend/pullback candidate.

#include <Trade/Trade.mqh>

input ENUM_TIMEFRAMES SBTC_TF = PERIOD_H1;
input double SBTC_RiskPercent = 2.00;
input double SBTC_StrongRiskMultiplier = 1.00;
input double SBTC_WeakRiskMultiplier = 0.55;
input int    SBTC_MaxPositions = 3;
input int    SBTC_MaxSameSidePositions = 2;
input int    SBTC_MinBarsBetweenEntries = 2;
input double SBTC_MaxSpreadUsd = 120.00;
input int    SBTC_DeviationPoints = 300;
input bool   SBTC_EnableBuys = true;
input bool   SBTC_EnableSells = true;
input bool   SBTC_EnableBreakoutEngine = true;
input bool   SBTC_EnablePullbackEngine = true;
input bool   SBTC_EnableReversalEngine = false;
input bool   SBTC_BlockOppositeDirection = true;
input bool   SBTC_EnableDailyGuard = true;
input double SBTC_DailyMaxLossPct = 12.00;
input bool   SBTC_CloseOnDailyStop = true;
input bool   SBTC_EnableEquityCircuit = true;
input double SBTC_MaxAccountDrawdownPct = 25.00;
input bool   SBTC_CloseOnCircuitStop = true;
input int    SBTC_FastLossCooldownAfter = 2;
input int    SBTC_CooldownBars = 8;
input int    SBTC_EMAFast = 20;
input int    SBTC_EMASlow = 50;
input int    SBTC_H1Fast = 34;
input int    SBTC_H1Slow = 89;
input int    SBTC_H4Fast = 34;
input int    SBTC_H4Slow = 89;
input int    SBTC_ATRPeriod = 14;
input int    SBTC_RSI_Period = 14;
input int    SBTC_ADXPeriod = 14;
input int    SBTC_BandsPeriod = 20;
input double SBTC_BandsDeviation = 2.00;
input int    SBTC_BreakoutLookback = 12;
input int    SBTC_StopLookback = 10;
input double SBTC_MinATRUsd = 80.00;
input double SBTC_MaxATRUsd = 2500.00;
input double SBTC_MinSLUsd = 180.00;
input double SBTC_MaxSLUsd = 1400.00;
input double SBTC_StopBufferATR = 0.25;
input double SBTC_BreakoutRR = 1.85;
input double SBTC_PullbackRR = 1.45;
input double SBTC_ReversalRR = 1.12;
input double SBTC_MinBodyRatio = 0.42;
input double SBTC_StrongBodyRatio = 0.58;
input double SBTC_MinBreakATR = 0.06;
input double SBTC_PullbackTouchATR = 0.30;
input double SBTC_MaxEmaDistanceATR = 1.80;
input int    SBTC_MinScore = 70;
input int    SBTC_StrongScore = 78;
input bool   SBTC_AllowSidewaysBreakout = false;
input bool   SBTC_AllowSidewaysPullback = false;
input double SBTC_RegimeADXMin = 17.00;
input double SBTC_SidewaysADXMin = 21.00;
input double SBTC_StrongADX = 26.00;
input double SBTC_BreakevenR = 0.85;
input double SBTC_BreakevenLockUsd = 18.00;
input double SBTC_TrailStartR = 1.25;
input double SBTC_TrailATR = 1.10;
input int    SBTC_MaxHoldBars = 48;
input int    SBTC_WeakMaxHoldBars = 24;
input bool   SBTC_CloseOnRegimeFlip = true;
input bool   SBTC_LogEntries = true;
input bool   SBTC_LogStatus = false;
input int    SBTC_StatusEveryBars = 16;

static const ulong SBTC_MAGIC = 2026050815;

enum SbtcRegime
  {
   SBTC_SIDEWAYS = 0,
   SBTC_BULL = 1,
   SBTC_BEAR = -1
  };

struct SbtcSignal
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
int g_h1Fast = INVALID_HANDLE;
int g_h1Slow = INVALID_HANDLE;
int g_h4Fast = INVALID_HANDLE;
int g_h4Slow = INVALID_HANDLE;
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
int g_fastLossStreak = 0;
int g_statusCounter = 0;


double SbtcNormalizePrice(const double price)
  {
   return(NormalizeDouble(price, (int)SymbolInfoInteger(_Symbol, SYMBOL_DIGITS)));
  }


double SbtcMinStopDistance()
  {
   long stopLevel = SymbolInfoInteger(_Symbol, SYMBOL_TRADE_STOPS_LEVEL);
   long freezeLevel = SymbolInfoInteger(_Symbol, SYMBOL_TRADE_FREEZE_LEVEL);
   return((double)MathMax(stopLevel, freezeLevel) * _Point);
  }


bool SbtcCopyBufferValue(const int handle, const int buffer, const int shift, double &value)
  {
   double data[];
   ArraySetAsSeries(data, true);
   if(CopyBuffer(handle, buffer, shift, 1, data) != 1)
      return(false);
   value = data[0];
   return(true);
  }


bool SbtcLoadRates(MqlRates &rates[], const int count)
  {
   ArraySetAsSeries(rates, true);
   return(CopyRates(_Symbol, SBTC_TF, 0, count, rates) == count);
  }


int SbtcDayKey(const datetime ts)
  {
   MqlDateTime dt;
   TimeToStruct(ts, dt);
   return(dt.year * 1000 + dt.day_of_year);
  }


double SbtcSpreadUsd()
  {
   MqlTick tick;
   if(!SymbolInfoTick(_Symbol, tick))
      return(999999.0);
   return(tick.ask - tick.bid);
  }


double SbtcCandleBodyRatio(const MqlRates &bar)
  {
   const double range = bar.high - bar.low;
   if(range <= 0.0)
      return(0.0);
   return(MathAbs(bar.close - bar.open) / range);
  }


int SbtcCountPositions(const int side)
  {
   int count = 0;
   for(int i = PositionsTotal() - 1; i >= 0; --i)
     {
      ulong ticket = PositionGetTicket(i);
      if(ticket == 0 || !PositionSelectByTicket(ticket))
         continue;
      if(PositionGetString(POSITION_SYMBOL) != _Symbol)
         continue;
      if((ulong)PositionGetInteger(POSITION_MAGIC) != SBTC_MAGIC)
         continue;
      long type = PositionGetInteger(POSITION_TYPE);
      if(side == 0 || (side > 0 && type == POSITION_TYPE_BUY) || (side < 0 && type == POSITION_TYPE_SELL))
         count++;
     }
   return(count);
  }


void SbtcCloseAll(const string reason)
  {
   for(int i = PositionsTotal() - 1; i >= 0; --i)
     {
      ulong ticket = PositionGetTicket(i);
      if(ticket == 0 || !PositionSelectByTicket(ticket))
         continue;
      if(PositionGetString(POSITION_SYMBOL) != _Symbol)
         continue;
      if((ulong)PositionGetInteger(POSITION_MAGIC) != SBTC_MAGIC)
         continue;
      if(g_trade.PositionClose(ticket))
         Print("SUIS_BTC EXIT RISK | ticket=", ticket, " reason=", reason);
     }
  }


void SbtcResetGuards()
  {
   const datetime now = TimeCurrent();
   const int dayKey = SbtcDayKey(now);
   const double equity = AccountInfoDouble(ACCOUNT_EQUITY);

   if(g_dayKey != dayKey)
     {
      g_dayKey = dayKey;
      g_dayStartEquity = equity;
      g_dayHighEquity = equity;
      g_dailyStopped = false;
      g_fastLossStreak = 0;
      g_cooldownUntilBar = 0;
      Print("SUIS_BTC GUARD | new day | equity=", DoubleToString(equity, 2));
     }

   if(g_dayHighEquity <= 0.0 || equity > g_dayHighEquity)
      g_dayHighEquity = equity;
   if(g_accountHighEquity <= 0.0 || equity > g_accountHighEquity)
      g_accountHighEquity = equity;
  }


bool SbtcGuardAllowsTrading()
  {
   SbtcResetGuards();
   const double equity = AccountInfoDouble(ACCOUNT_EQUITY);

   if(SBTC_EnableDailyGuard && g_dayStartEquity > 0.0)
     {
      const double dayLoss = 100.0 * (g_dayStartEquity - equity) / g_dayStartEquity;
      if(dayLoss >= SBTC_DailyMaxLossPct)
        {
         if(!g_dailyStopped)
           {
            Print("SUIS_BTC GUARD | daily loss ", DoubleToString(dayLoss, 2), "% >= ", DoubleToString(SBTC_DailyMaxLossPct, 2), "%");
            if(SBTC_CloseOnDailyStop)
               SbtcCloseAll("daily_loss");
           }
         g_dailyStopped = true;
         return(false);
        }
     }

   if(SBTC_EnableEquityCircuit && g_accountHighEquity > 0.0)
     {
      const double dd = 100.0 * (g_accountHighEquity - equity) / g_accountHighEquity;
      if(dd >= SBTC_MaxAccountDrawdownPct)
        {
         if(!g_circuitStopped)
           {
            Print("SUIS_BTC GUARD | account dd ", DoubleToString(dd, 2), "% >= ", DoubleToString(SBTC_MaxAccountDrawdownPct, 2), "%");
            if(SBTC_CloseOnCircuitStop)
               SbtcCloseAll("account_dd");
           }
         g_circuitStopped = true;
         return(false);
        }
     }

   if(g_dailyStopped || g_circuitStopped)
      return(false);

   MqlRates rates[];
   if(SbtcLoadRates(rates, 3) && g_cooldownUntilBar > 0 && rates[0].time <= g_cooldownUntilBar)
      return(false);

   return(true);
  }


SbtcRegime SbtcDetectRegime(const double h1Fast, const double h1Slow, const double h4Fast, const double h4Slow, const double adx)
  {
   const bool h1Bull = h1Fast > h1Slow;
   const bool h4Bull = h4Fast >= h4Slow;
   const bool h1Bear = h1Fast < h1Slow;
   const bool h4Bear = h4Fast <= h4Slow;

   if(h1Bull && h4Bull && adx >= SBTC_RegimeADXMin)
      return(SBTC_BULL);
   if(h1Bear && h4Bear && adx >= SBTC_RegimeADXMin)
      return(SBTC_BEAR);
   return(SBTC_SIDEWAYS);
  }


double SbtcHighestHigh(MqlRates &rates[], const int start, const int count)
  {
   double value = rates[start].high;
   for(int i = start; i < start + count; ++i)
      value = MathMax(value, rates[i].high);
   return(value);
  }


double SbtcLowestLow(MqlRates &rates[], const int start, const int count)
  {
   double value = rates[start].low;
   for(int i = start; i < start + count; ++i)
      value = MathMin(value, rates[i].low);
   return(value);
  }


double SbtcClampStop(const double stop)
  {
   double output = MathMax(SBTC_MinSLUsd, MathMin(SBTC_MaxSLUsd, stop));
   output = MathMax(output, SbtcMinStopDistance() * 1.3);
   return(output);
  }


SbtcSignal SbtcEmptySignal()
  {
   SbtcSignal signal;
   signal.valid = false;
   signal.sell = false;
   signal.score = 0;
   signal.engine = "";
   signal.tags = "";
   signal.stopDistance = 0.0;
   signal.rr = 0.0;
   signal.riskMultiplier = 0.0;
   signal.comment = "";
   return(signal);
  }


SbtcSignal SbtcBuildSignal()
  {
   SbtcSignal best = SbtcEmptySignal();
   MqlRates rates[];
   const int needed = MathMax(SBTC_BreakoutLookback + 8, SBTC_StopLookback + 8);
   if(!SbtcLoadRates(rates, needed))
      return(best);

   double emaFast = 0.0, emaSlow = 0.0, h1Fast = 0.0, h1Slow = 0.0, h4Fast = 0.0, h4Slow = 0.0;
   double atr = 0.0, rsi = 0.0, adx = 0.0, upper = 0.0, lower = 0.0;
   if(!SbtcCopyBufferValue(g_emaFast, 0, 1, emaFast) || !SbtcCopyBufferValue(g_emaSlow, 0, 1, emaSlow) ||
      !SbtcCopyBufferValue(g_h1Fast, 0, 1, h1Fast) || !SbtcCopyBufferValue(g_h1Slow, 0, 1, h1Slow) ||
      !SbtcCopyBufferValue(g_h4Fast, 0, 1, h4Fast) || !SbtcCopyBufferValue(g_h4Slow, 0, 1, h4Slow) ||
      !SbtcCopyBufferValue(g_atr, 0, 1, atr) || !SbtcCopyBufferValue(g_rsi, 0, 1, rsi) ||
      !SbtcCopyBufferValue(g_adx, 0, 1, adx) || !SbtcCopyBufferValue(g_bands, 1, 1, upper) ||
      !SbtcCopyBufferValue(g_bands, 2, 1, lower))
      return(best);

   if(atr < SBTC_MinATRUsd || atr > SBTC_MaxATRUsd)
      return(best);

   const MqlRates bar = rates[1];
   const MqlRates prev = rates[2];
   const SbtcRegime regime = SbtcDetectRegime(h1Fast, h1Slow, h4Fast, h4Slow, adx);
   const double body = SbtcCandleBodyRatio(bar);
   const double highest = SbtcHighestHigh(rates, 2, SBTC_BreakoutLookback);
   const double lowest = SbtcLowestLow(rates, 2, SBTC_BreakoutLookback);
   const double distEmaAtr = MathAbs(bar.close - emaFast) / MathMax(atr, 0.01);
   const bool candleBull = bar.close > bar.open;
   const bool candleBear = bar.close < bar.open;
   const bool m15Bull = emaFast > emaSlow;
   const bool m15Bear = emaFast < emaSlow;

   const bool buyBreak = SBTC_EnableBreakoutEngine && SBTC_EnableBuys && candleBull && body >= SBTC_MinBodyRatio &&
                         bar.close > highest + atr * SBTC_MinBreakATR && m15Bull && rsi <= 76.0 &&
                         (regime == SBTC_BULL || (SBTC_AllowSidewaysBreakout && regime == SBTC_SIDEWAYS && adx >= SBTC_SidewaysADXMin));
   const bool sellBreak = SBTC_EnableBreakoutEngine && SBTC_EnableSells && candleBear && body >= SBTC_MinBodyRatio &&
                          bar.close < lowest - atr * SBTC_MinBreakATR && m15Bear && rsi >= 24.0 &&
                          (regime == SBTC_BEAR || (SBTC_AllowSidewaysBreakout && regime == SBTC_SIDEWAYS && adx >= SBTC_SidewaysADXMin));

   const bool buyPullback = SBTC_EnablePullbackEngine && SBTC_EnableBuys && candleBull && m15Bull && bar.low <= emaFast + atr * SBTC_PullbackTouchATR &&
                            bar.close > emaFast && prev.close >= emaSlow && rsi >= 43.0 && rsi <= 70.0 &&
                            distEmaAtr <= SBTC_MaxEmaDistanceATR && (regime == SBTC_BULL || (SBTC_AllowSidewaysPullback && regime == SBTC_SIDEWAYS));
   const bool sellPullback = SBTC_EnablePullbackEngine && SBTC_EnableSells && candleBear && m15Bear && bar.high >= emaFast - atr * SBTC_PullbackTouchATR &&
                             bar.close < emaFast && prev.close <= emaSlow && rsi <= 57.0 && rsi >= 30.0 &&
                             distEmaAtr <= SBTC_MaxEmaDistanceATR && (regime == SBTC_BEAR || (SBTC_AllowSidewaysPullback && regime == SBTC_SIDEWAYS));

   const bool buyReversal = SBTC_EnableReversalEngine && SBTC_EnableBuys && candleBull && bar.low <= lower + atr * 0.10 && rsi <= 38.0 &&
                            bar.close > bar.low + (bar.high - bar.low) * 0.55 && regime != SBTC_BEAR;
   const bool sellReversal = SBTC_EnableReversalEngine && SBTC_EnableSells && candleBear && bar.high >= upper - atr * 0.10 && rsi >= 62.0 &&
                             bar.close < bar.high - (bar.high - bar.low) * 0.55 && regime != SBTC_BULL;

   SbtcSignal candidate = SbtcEmptySignal();
   if(buyBreak || sellBreak)
     {
      candidate.valid = true;
      candidate.sell = sellBreak;
      candidate.engine = "BO";
      candidate.rr = SBTC_BreakoutRR;
      candidate.riskMultiplier = (body >= SBTC_StrongBodyRatio && regime != SBTC_SIDEWAYS) ? SBTC_StrongRiskMultiplier : SBTC_WeakRiskMultiplier;
      candidate.score = 66 + (int)MathRound(body * 18.0) + (adx >= SBTC_StrongADX ? 8 : 0) + (regime != SBTC_SIDEWAYS ? 6 : 0);
     }
   else if(buyPullback || sellPullback)
     {
      candidate.valid = true;
      candidate.sell = sellPullback;
      candidate.engine = "PB";
      candidate.rr = SBTC_PullbackRR;
      candidate.riskMultiplier = (regime != SBTC_SIDEWAYS) ? SBTC_StrongRiskMultiplier * 0.85 : SBTC_WeakRiskMultiplier;
      candidate.score = 64 + (int)MathRound(body * 14.0) + (regime != SBTC_SIDEWAYS ? 7 : 0) + (distEmaAtr <= 0.65 ? 4 : 0);
     }
   else if(buyReversal || sellReversal)
     {
      candidate.valid = true;
      candidate.sell = sellReversal;
      candidate.engine = "RV";
      candidate.rr = SBTC_ReversalRR;
      candidate.riskMultiplier = SBTC_WeakRiskMultiplier;
      candidate.score = 62 + (int)MathRound(body * 14.0) + (regime == SBTC_SIDEWAYS ? 6 : 0);
     }

   if(!candidate.valid || candidate.score < SBTC_MinScore)
      return(best);

   const double swingStop = candidate.sell
      ? SbtcHighestHigh(rates, 1, SBTC_StopLookback) - bar.close + atr * SBTC_StopBufferATR
      : bar.close - SbtcLowestLow(rates, 1, SBTC_StopLookback) + atr * SBTC_StopBufferATR;
   candidate.stopDistance = SbtcClampStop(MathMax(swingStop, atr * 0.95));
   candidate.tags = StringFormat("%s|%s|%s|RSI%.0f|ADX%.0f",
                                 candidate.engine,
                                 candidate.sell ? "SELL" : "BUY",
                                 regime == SBTC_BULL ? "BULL" : (regime == SBTC_BEAR ? "BEAR" : "SIDE"),
                                 rsi,
                                 adx);
   candidate.comment = StringFormat("SBTC|%s|S%d|%s", candidate.engine, candidate.score, candidate.sell ? "S" : "B");
   return(candidate);
  }


double SbtcNormalizeVolume(const double volume)
  {
   const double minVol = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
   const double maxVol = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX);
   const double step = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);
   if(step <= 0.0)
      return(0.0);
   double output = MathFloor(volume / step) * step;
   output = MathMax(minVol, MathMin(maxVol, output));
   int digits = 2;
   if(step < 0.01)
      digits = 3;
   if(step < 0.001)
      digits = 4;
   return(NormalizeDouble(output, digits));
  }


double SbtcVolumeForRisk(const double stopDistance, const double riskMultiplier)
  {
   const double equity = AccountInfoDouble(ACCOUNT_EQUITY);
   const double riskMoney = equity * SBTC_RiskPercent / 100.0 * riskMultiplier;
   const double tickSize = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);
   double tickValue = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE_LOSS);
   if(tickValue <= 0.0)
      tickValue = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE);
   if(riskMoney <= 0.0 || stopDistance <= 0.0 || tickSize <= 0.0 || tickValue <= 0.0)
      return(0.0);
   const double moneyPerLot = stopDistance / tickSize * tickValue;
   if(moneyPerLot <= 0.0)
      return(0.0);
   return(SbtcNormalizeVolume(riskMoney / moneyPerLot));
  }


bool SbtcCanOpen(const SbtcSignal &signal)
  {
   if(SbtcSpreadUsd() > SBTC_MaxSpreadUsd)
      return(false);
   if(SbtcCountPositions(0) >= SBTC_MaxPositions)
      return(false);
   if(signal.sell && SbtcCountPositions(-1) >= SBTC_MaxSameSidePositions)
      return(false);
   if(!signal.sell && SbtcCountPositions(1) >= SBTC_MaxSameSidePositions)
      return(false);
   if(SBTC_BlockOppositeDirection)
     {
      if(signal.sell && SbtcCountPositions(1) > 0)
         return(false);
      if(!signal.sell && SbtcCountPositions(-1) > 0)
         return(false);
     }
   MqlRates rates[];
   if(SbtcLoadRates(rates, 3) && g_lastEntryBarTime > 0)
     {
      const int seconds = PeriodSeconds(SBTC_TF) * SBTC_MinBarsBetweenEntries;
      if((int)(rates[0].time - g_lastEntryBarTime) < seconds)
         return(false);
     }
   return(true);
  }


void SbtcOpenSignal(const SbtcSignal &signal)
  {
   if(!SbtcCanOpen(signal))
      return;

   MqlTick tick;
   if(!SymbolInfoTick(_Symbol, tick))
      return;

   const double entry = signal.sell ? tick.bid : tick.ask;
   const double stopDistance = MathMax(signal.stopDistance, SbtcMinStopDistance() * 1.3);
   const double volume = SbtcVolumeForRisk(stopDistance, signal.riskMultiplier);
   if(volume <= 0.0)
      return;

   const double sl = SbtcNormalizePrice(signal.sell ? entry + stopDistance : entry - stopDistance);
   const double tp = SbtcNormalizePrice(signal.sell ? entry - stopDistance * signal.rr : entry + stopDistance * signal.rr);

   g_trade.SetExpertMagicNumber(SBTC_MAGIC);
   g_trade.SetDeviationInPoints(SBTC_DeviationPoints);
   bool ok = signal.sell
      ? g_trade.Sell(volume, _Symbol, 0.0, sl, tp, signal.comment)
      : g_trade.Buy(volume, _Symbol, 0.0, sl, tp, signal.comment);
   if(ok)
     {
      MqlRates rates[];
      if(SbtcLoadRates(rates, 3))
         g_lastEntryBarTime = rates[0].time;
      if(SBTC_LogEntries)
         Print("SUIS_BTC ENTRY ", signal.sell ? "SELL" : "BUY",
               " engine=", signal.engine,
               " score=", signal.score,
               " lot=", DoubleToString(volume, 2),
               " sl=", DoubleToString(sl, _Digits),
               " tp=", DoubleToString(tp, _Digits),
               " rr=", DoubleToString(signal.rr, 2),
               " spread=", DoubleToString(SbtcSpreadUsd(), 2),
               " tags=", signal.tags);
     }
  }


string SbtcEngineFromComment(const string comment)
  {
   string parts[];
   int count = StringSplit(comment, '|', parts);
   if(count >= 2)
      return(parts[1]);
   return("");
  }


double SbtcInitialRiskFromPosition(const bool sell, const double openPrice, const double sl)
  {
   if(sl <= 0.0)
      return(0.0);
   return(sell ? sl - openPrice : openPrice - sl);
  }


void SbtcManagePositions()
  {
   MqlRates rates[];
   if(!SbtcLoadRates(rates, 12))
      return;

   double atr = 0.0, h1Fast = 0.0, h1Slow = 0.0, h4Fast = 0.0, h4Slow = 0.0, adx = 0.0;
   if(!SbtcCopyBufferValue(g_atr, 0, 1, atr) || !SbtcCopyBufferValue(g_h1Fast, 0, 1, h1Fast) ||
      !SbtcCopyBufferValue(g_h1Slow, 0, 1, h1Slow) || !SbtcCopyBufferValue(g_h4Fast, 0, 1, h4Fast) ||
      !SbtcCopyBufferValue(g_h4Slow, 0, 1, h4Slow) || !SbtcCopyBufferValue(g_adx, 0, 1, adx))
      return;

   const SbtcRegime regime = SbtcDetectRegime(h1Fast, h1Slow, h4Fast, h4Slow, adx);
   MqlTick tick;
   if(!SymbolInfoTick(_Symbol, tick))
      return;

   for(int i = PositionsTotal() - 1; i >= 0; --i)
     {
      ulong ticket = PositionGetTicket(i);
      if(ticket == 0 || !PositionSelectByTicket(ticket))
         continue;
      if(PositionGetString(POSITION_SYMBOL) != _Symbol)
         continue;
      if((ulong)PositionGetInteger(POSITION_MAGIC) != SBTC_MAGIC)
         continue;

      const bool sell = PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_SELL;
      const double openPrice = PositionGetDouble(POSITION_PRICE_OPEN);
      const double sl = PositionGetDouble(POSITION_SL);
      const double tp = PositionGetDouble(POSITION_TP);
      const double current = sell ? tick.ask : tick.bid;
      const double profitDistance = sell ? openPrice - current : current - openPrice;
      const double initialRisk = MathMax(SbtcInitialRiskFromPosition(sell, openPrice, sl), SBTC_MinSLUsd);
      const double progressR = profitDistance / MathMax(initialRisk, 0.01);
      const datetime openTime = (datetime)PositionGetInteger(POSITION_TIME);
      const int holdBars = (int)((rates[0].time - openTime) / PeriodSeconds(SBTC_TF));
      const string engine = SbtcEngineFromComment(PositionGetString(POSITION_COMMENT));
      const int maxHold = (engine == "RV") ? SBTC_WeakMaxHoldBars : SBTC_MaxHoldBars;

      if(SBTC_CloseOnRegimeFlip && progressR < 0.15)
        {
         if(!sell && regime == SBTC_BEAR)
           {
            g_trade.PositionClose(ticket);
            Print("SUIS_BTC EXIT FLIP | ticket=", ticket, " side=BUY r=", DoubleToString(progressR, 2));
            continue;
           }
         if(sell && regime == SBTC_BULL)
           {
            g_trade.PositionClose(ticket);
            Print("SUIS_BTC EXIT FLIP | ticket=", ticket, " side=SELL r=", DoubleToString(progressR, 2));
            continue;
           }
        }

      if(holdBars >= maxHold && progressR < 0.35)
        {
         g_trade.PositionClose(ticket);
         Print("SUIS_BTC EXIT TIME | ticket=", ticket, " holdBars=", holdBars, " r=", DoubleToString(progressR, 2));
         continue;
        }

      double newSl = sl;
      if(progressR >= SBTC_BreakevenR)
        {
         const double be = sell ? openPrice - SBTC_BreakevenLockUsd : openPrice + SBTC_BreakevenLockUsd;
         if((sell && (newSl <= 0.0 || be < newSl)) || (!sell && be > newSl))
            newSl = be;
        }
      if(progressR >= SBTC_TrailStartR)
        {
         const double trail = sell ? current + atr * SBTC_TrailATR : current - atr * SBTC_TrailATR;
         if((sell && (newSl <= 0.0 || trail < newSl)) || (!sell && trail > newSl))
            newSl = trail;
        }

      if(newSl > 0.0)
        {
         newSl = SbtcNormalizePrice(newSl);
         const bool improves = sell ? (sl <= 0.0 || newSl < sl - _Point) : (newSl > sl + _Point);
         if(improves)
            g_trade.PositionModify(ticket, newSl, tp);
        }
     }
  }


bool SbtcIsNewBar()
  {
   MqlRates rates[];
   if(!SbtcLoadRates(rates, 3))
      return(false);
   if(rates[0].time == g_lastBarTime)
      return(false);
   g_lastBarTime = rates[0].time;
   return(true);
  }


int OnInit()
  {
   g_trade.SetExpertMagicNumber(SBTC_MAGIC);
   g_trade.SetDeviationInPoints(SBTC_DeviationPoints);

   g_emaFast = iMA(_Symbol, SBTC_TF, SBTC_EMAFast, 0, MODE_EMA, PRICE_CLOSE);
   g_emaSlow = iMA(_Symbol, SBTC_TF, SBTC_EMASlow, 0, MODE_EMA, PRICE_CLOSE);
   g_h1Fast = iMA(_Symbol, PERIOD_H1, SBTC_H1Fast, 0, MODE_EMA, PRICE_CLOSE);
   g_h1Slow = iMA(_Symbol, PERIOD_H1, SBTC_H1Slow, 0, MODE_EMA, PRICE_CLOSE);
   g_h4Fast = iMA(_Symbol, PERIOD_H4, SBTC_H4Fast, 0, MODE_EMA, PRICE_CLOSE);
   g_h4Slow = iMA(_Symbol, PERIOD_H4, SBTC_H4Slow, 0, MODE_EMA, PRICE_CLOSE);
   g_atr = iATR(_Symbol, SBTC_TF, SBTC_ATRPeriod);
   g_rsi = iRSI(_Symbol, SBTC_TF, SBTC_RSI_Period, PRICE_CLOSE);
   g_adx = iADX(_Symbol, SBTC_TF, SBTC_ADXPeriod);
   g_bands = iBands(_Symbol, SBTC_TF, SBTC_BandsPeriod, 0, SBTC_BandsDeviation, PRICE_CLOSE);

   if(g_emaFast == INVALID_HANDLE || g_emaSlow == INVALID_HANDLE || g_h1Fast == INVALID_HANDLE ||
      g_h1Slow == INVALID_HANDLE || g_h4Fast == INVALID_HANDLE || g_h4Slow == INVALID_HANDLE ||
      g_atr == INVALID_HANDLE || g_rsi == INVALID_HANDLE || g_adx == INVALID_HANDLE || g_bands == INVALID_HANDLE)
      return(INIT_FAILED);

   Print("Suis_BTC_v1 loaded | symbol=", _Symbol, " tf=", EnumToString(SBTC_TF), " risk=", DoubleToString(SBTC_RiskPercent, 2),
         " maxPos=", SBTC_MaxPositions, " spreadMax=", DoubleToString(SBTC_MaxSpreadUsd, 2));
   SbtcResetGuards();
   return(INIT_SUCCEEDED);
  }


void OnDeinit(const int reason)
  {
   if(g_emaFast != INVALID_HANDLE) IndicatorRelease(g_emaFast);
   if(g_emaSlow != INVALID_HANDLE) IndicatorRelease(g_emaSlow);
   if(g_h1Fast != INVALID_HANDLE) IndicatorRelease(g_h1Fast);
   if(g_h1Slow != INVALID_HANDLE) IndicatorRelease(g_h1Slow);
   if(g_h4Fast != INVALID_HANDLE) IndicatorRelease(g_h4Fast);
   if(g_h4Slow != INVALID_HANDLE) IndicatorRelease(g_h4Slow);
   if(g_atr != INVALID_HANDLE) IndicatorRelease(g_atr);
   if(g_rsi != INVALID_HANDLE) IndicatorRelease(g_rsi);
   if(g_adx != INVALID_HANDLE) IndicatorRelease(g_adx);
   if(g_bands != INVALID_HANDLE) IndicatorRelease(g_bands);
  }


void OnTick()
  {
   SbtcResetGuards();
   SbtcManagePositions();
   if(!SbtcIsNewBar())
      return;

   if(SBTC_LogStatus && (++g_statusCounter % MathMax(SBTC_StatusEveryBars, 1) == 0))
      Print("SUIS_BTC STATUS | equity=", DoubleToString(AccountInfoDouble(ACCOUNT_EQUITY), 2),
            " pos=", SbtcCountPositions(0), " spread=", DoubleToString(SbtcSpreadUsd(), 2));

   if(!SbtcGuardAllowsTrading())
      return;

   SbtcSignal signal = SbtcBuildSignal();
   if(signal.valid)
      SbtcOpenSignal(signal);
  }


void OnTradeTransaction(const MqlTradeTransaction &trans,
                        const MqlTradeRequest &request,
                        const MqlTradeResult &result)
  {
   if(trans.type != TRADE_TRANSACTION_DEAL_ADD)
      return;
   if(!HistoryDealSelect(trans.deal))
      return;
   if((ulong)HistoryDealGetInteger(trans.deal, DEAL_MAGIC) != SBTC_MAGIC)
      return;
   if(HistoryDealGetString(trans.deal, DEAL_SYMBOL) != _Symbol)
      return;
   if((ENUM_DEAL_ENTRY)HistoryDealGetInteger(trans.deal, DEAL_ENTRY) != DEAL_ENTRY_OUT)
      return;

   const double profit = HistoryDealGetDouble(trans.deal, DEAL_PROFIT) +
                         HistoryDealGetDouble(trans.deal, DEAL_SWAP) +
                         HistoryDealGetDouble(trans.deal, DEAL_COMMISSION);
   if(profit < 0.0)
     {
      g_fastLossStreak++;
      if(g_fastLossStreak >= SBTC_FastLossCooldownAfter)
        {
         MqlRates rates[];
         if(SbtcLoadRates(rates, 3))
            g_cooldownUntilBar = rates[0].time + PeriodSeconds(SBTC_TF) * SBTC_CooldownBars;
         Print("SUIS_BTC GUARD | cooldown after losses=", g_fastLossStreak, " until=", TimeToString(g_cooldownUntilBar));
         g_fastLossStreak = 0;
        }
     }
   else if(profit > 0.0)
      g_fastLossStreak = 0;
  }
