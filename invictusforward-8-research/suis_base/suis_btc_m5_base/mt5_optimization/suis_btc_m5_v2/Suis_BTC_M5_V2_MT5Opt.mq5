#property copyright "Suis Base"
#property version   "2.10"
#property strict
#property description "Suis_BTC_M5_V2 MT5 optimizer temporary build"
// Suis BTC M5 V2 MT5 optimizer temporary build. Do not migrate this EX5.

#include <Trade/Trade.mqh>

input double V10_RiskPercent = 15.5;
input double V11_MaxLotCap = 23.25;
const double V11_BuyPullbackRiskMultiplier = 1.0;
const double V10_BuyRiskMultiplier = 1.50;
const double V10_SellRiskMultiplier = 1.15;
const double V10_WeakBuyRiskMultiplier = 1.50;
const double V10_WeakSellRiskMultiplier = 0;
const bool   V10_EnableBuys = false;
const bool   V10_EnableSells = true;
const int    V10_MaxPositions = 10;
const int    V10_WeakRegimeMaxPositions = 0;
const int    V10_SellSessionStartHour = 0;
const int    V10_SellSessionEndHour = 23;
const int    V10_BuySessionStartHour = 0;
const int    V10_BuySessionEndHour = 23;
const bool   V10_StrongBullRelaxBuySession = true;
const bool   V10_EnableMixedMomentumEntries = true;
const bool   V11_BlockOppositeDirection = true;
const long   V11_OppositeMagic = 0;
const double V10_MaxSpreadUsd = 250;
const bool   V11_EnableDailyGuard = true;
const double V11_DailyMaxLossPct = 9.75;
const double V11_DailyProfitStopPct = 0.00;
const double V11_DailyProfitLockStartPct = 23;
const double V11_DailyMaxGivebackPct = 7.75;
const bool   V11_DailyClosePositionsOnStop = true;
const int    V11_MaxConsecutiveLosses = 4;
const int    V11_LossCooldownMinutes = 120;
const bool   V11_DailyGuardLog = true;
const bool   V12_EnablePeakEquityGuard = false;
const double V12_PeakDrawdownStopPct = 70.0;
const bool   V12_PeakClosePositionsOnStop = true;
const double V12_MinEquityFloorPct = 0.0;
const bool   V12_FloorClosePositionsOnStop = true;
const bool   V12_EnableDynamicRiskThrottle = true;
const double V12_ThrottleStartDrawdownPct = 16;
const double V12_ThrottleFullDrawdownPct = 45;
const double V12_ThrottleMinMultiplier = 0.35;
const double V12_RiskBudgetCapPctOfStartEquity = 60;
const bool   V12_EnableBootstrapRiskRamp = false;
const double V12_BootstrapStartEquityPct = 100.0;
const double V12_BootstrapFullEquityPct = 200.0;
const double V12_BootstrapMinMultiplier = 0.10;
const string V12_BlockTradeMonths = "4,7,8,9,10,12";
const bool   V12_EnableMultiSignalQueue = false;
const int    V12_MaxSignalsPerBar = 1;
const bool   V12_AllowIndependentAddOns = false;
const double V12_MaxOpenRiskPctOfEquity = 0.0;
const double V12_MaxOpenRiskPctOfStartEquity = 0.0;

const int    V10_H1FastEMA = 20;
const int    V10_H1SlowEMA = 50;
const int    V10_H4FastEMA = 20;
const int    V10_H4SlowEMA = 50;
const int    V10_H1ADXPeriod = 14;
const int    V10_H1ATRPeriod = 14;
const double V10_H1ADXMin = 7;
const double V10_H1ADXStrongMin = 13;
const double V10_StrongGapATR = 0.02;
const int    V10_M5TrendEMA = 20;
const int    V10_M5ATRPeriod = 14;

const int    V10_BreakoutLookback = 4;
const int    V10_PullbackLookback = 3;
const bool   V10_RequirePullback = false;
const bool   V10_AllowBreakoutBuys = true;
const bool   V10_AllowPullbackBuys = false;
const bool   V10_UseBuyCoreHours = false;
const bool   V10_EnableBullSubEngine = false;
const bool   V10_BullSubAllowWeakBull = true;
const int    V10_BullSubSessionStartHour = 0;
const int    V10_BullSubSessionEndHour = 23;
const bool   V10_BullSubOnlyOutsideCore = false;
const int    V10_BullSubCompressionBars = 6;
const double V10_BullSubMaxRangeATR = 1.60;
const double V10_BullSubTouchEmaATR = 0.18;
const double V10_BullSubBreakATR = 0.04;
const double V10_BullSubMinBodyRatio = 0.36;
const double V10_BullSubRiskMultiplier = 0.45;
const double V10_BullSubRR = 0.72;
const int    V10_BullSubMaxHoldBars = 4;
const bool   V10_EnableBearSubEngine = true;
const bool   V10_BearSubAllowWeakBear = false;
const int    V10_BearSubSessionStartHour = 0;
const int    V10_BearSubSessionEndHour = 23;
const int    V10_BearSubCompressionBars = 5;
const double V10_BearSubMaxRangeATR = 1.25;
const double V10_BearSubTouchEmaATR = 0.16;
const double V10_BearSubBreakATR = 0.02;
const double V10_BearSubMinBodyRatio = 0.42;
const double V10_BearSubRiskMultiplier = 0.32;
const double V10_BearSubRR = 0.8;
const int    V10_BearSubMaxHoldBars = 4;
const bool   V11_EnableBearSafeMode = true;
const int    V11_BearSafeStrongMinScore = 60;
const int    V11_BearSafeWeakMinScore = 72;
const double V11_BearSafeWeakMinBodyRatio = 0.50;
const bool   V11_BearSafeBlockWeakZone = true;
const bool   V11_BearSafeBlockWeakAddOns = true;
const bool   V11_EnableImpulsePullbackEngine = true;
const bool   V11_EnableBuyImpulsePullback = true;
const bool   V11_EnableSellImpulsePullback = true;
const bool   V11_ImpulseAllowWeakRegime = false;
const int    V11_ImpulseSessionStartHour = 0;
const int    V11_ImpulseSessionEndHour = 23;
const double V11_ImpulseMinBodyRatio = 0.42;
const double V11_ImpulseMinMoveATR = 0.45;
const double V11_ImpulsePullbackMaxATR = 0.95;
const double V11_ImpulseEntryBodyRatio = 0.32;
const double V11_ImpulseBreakATR = 0.00;
const double V11_ImpulseRiskMultiplier = 0.45;
const double V11_ImpulseRR = 0.82;
const int    V11_ImpulseMaxHoldBars = 4;
const bool   V10_EnableZoneRetestEngine = false;
const bool   V10_ZoneAllowWeakRegime = false;
const bool   V10_ZoneUseCoreHours = false;
const int    V10_ZoneLookback = 5;
const double V10_ZoneMinBodyRatio = 0.34;
const double V10_ZoneBreakATR = 0;
const double V10_ZoneMidTouchATR = 0.18;
const double V10_ZoneReclaimATR = 0.00;
const double V10_ZoneOvershootATR = 0.35;
const double V10_ZoneRiskMultiplier = 0.38;
const double V10_ZoneRR = 0.78;
const int    V10_ZoneMaxHoldBars = 4;
const bool   V10_StrongBullRelaxCoreHours = true;
const bool   V10_StrongBullPullbackOnlyOutsideCore = false;
const bool   V10_BlockBuyHour07 = false;
const bool   V10_BlockBuyHour10 = false;
const bool   V10_BlockBuyHour14 = false;
const bool   V10_BlockBuyHour17 = false;
const string V11_BlockBuyBreakHours = "";
const string V11_BlockBuyPullbackHours = "";
const string V11_BlockBuyZoneHours = "";
const string V11_BlockBuyImpulseHours = "";
const string V11_BlockBuySubHours = "";
const string V11_BlockBuyAddOnHours = "";
const string V11_BlockSellBreakHours = "0,1,2,3,4,7,8,9,10,11,12,13,14,17,18,19,20,21,22,23";
const string V11_BlockSellZoneHours = "0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23";
const string V11_BlockSellImpulseHours = "0,1,2,3,4,7,8,9,10,11,12,13,14,17,18,19,20,21,22,23";
const string V11_BlockSellSubHours = "0,1,2,3,4,7,8,9,10,11,12,13,14,17,18,19,20,21,22,23";
const string V11_BlockSellAddOnHours = "0,1,2,3,4,7,8,9,10,11,12,13,14,17,18,19,20,21,22,23";
const int    V10_BullPullbackLookback = 8;
const double V10_BullTouchATR = 0.15;
const double V10_BullReclaimATR = 0.00;
const double V10_BullMaxStretchATR = 1.9;
const int    V10_BearRejectLookback = 6;
const double V10_BearTouchATR = 0.12;
const double V10_BearBreakBelowPrevATR = 0.02;
const double V10_BearMaxStretchATR = 1.9;
const double V10_MinBreakATR = 0.02;
const double V10_BuyMinBreakATR = 0.02;
const double V10_WeakSellMinBreakATR = 0.02;
const double V10_WeakBuyMinBreakATR = 0.03;
const double V10_MinBodyRatio = 0.34;
const double V10_BuyMinBodyRatio = 0.34;
const double V10_WeakSellMinBodyRatio = 0.34;
const double V10_WeakBuyMinBodyRatio = 0.36;
const double V10_MaxStretchATR = 2.2;
const int    V10_ChopLookbackBars = 6;
const int    V10_MaxEmaFlips = 5;
const int    V10_HoldBars = 1;
const double V10_HoldBufferATR = 0.02;

const int    V10_StopLookbackBars = 5;
const double V10_StopBufferATR = 0.08;
const double V10_MinSLUsd = 35;
const double V10_MaxSLUsd = 320;
input double V10_SellRR = 0.7;
const double V10_BuyRR = 0.76;
const double V10_WeakSellRR = 0;
const double V10_WeakBuyRR = 0.68;

const int    V10_MaxHoldBars = 4;
const double V10_BreakevenR = 0.35;
const double V10_BreakevenLockUsd = 10;
const bool   V10_FastFailBuyGuard = false;
const bool   V10_FastFailPullbackOnly = true;
const int    V10_FastFailBars = 6;
const double V10_FastFailMinProgressR = 0.10;
const bool   V10_WeakOutsideSellQuickExit = true;
const int    V10_WeakOutsideSellExitBars = 6;
const bool   V10_CloseOnRegimeFlip = false;
const bool   V10_TimeCloseProfitOnly = false;
const int    V10_ScoreGradeAMin = 80;
const int    V10_ScoreGradeBMin = 65;
input int V10_MinTradeScore = 38;
const int    V10_ScoreBoostMin = 90;
const double V10_ScoreRRBonus = 0.1;
const double V10_ScoreRiskBonus = 1;
const bool   V10_EnableTPManager = true;
const bool   V11_LogExitActions = true;
const bool   V11_LogRejectedSignals = false;
const int    V11_MinRejectedScoreToLog = 55;
const bool   V11_LogStatusOnNewBar = false;
const int    V11_StatusEveryBars = 12;
const double V10_TP1R = 0.45;
const double V10_TP1CloseFraction = 0.45;
const double V10_RunnerRR = 1.1;
const double V10_TrailStartR = 0.65;
const double V10_TrailATR = 0.8;
const double V10_TrailLockUsd = 5;
const bool   V10_EnableAddOnEngine = true;
const bool   V10_EnableBuyAddOns = false;
const bool   V10_EnableSellAddOns = true;
const bool   V10_AddOnAllowWeakRegime = false;
const int    V10_AddOnMaxPerSide = 2;
const double V10_AddOnMinProgressR = 0.2;
const double V10_AddOnBreakATR = 0;
const double V10_AddOnMinBodyRatio = 0.42;
const double V10_AddOnRiskMultiplier = 0.25;
const double V10_AddOnRR = 0.72;
const int    V10_AddOnMaxHoldBars = 3;
const bool   V11_BuyBreakTimeCloseProfitOnly = false;
const bool   V11_BuyImpulseTimeCloseProfitOnly = false;
const bool   V11_BuyZoneTimeCloseProfitOnly = false;
const bool   V11_BuyCompTimeCloseProfitOnly = false;
const bool   V11_BuyAddOnTimeCloseProfitOnly = false;
const bool   V11_SellBreakTimeCloseProfitOnly = false;
const bool   V11_SellImpulseTimeCloseProfitOnly = false;
const bool   V11_SellZoneTimeCloseProfitOnly = false;
const bool   V11_SellCompTimeCloseProfitOnly = false;
const bool   V11_SellAddOnTimeCloseProfitOnly = false;

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
int               g_statusBarCounter = 0;
int               g_dailyGuardDay = -1;
double            g_dailyStartEquity = 0.0;
double            g_dailyHighEquity = 0.0;
bool              g_dailyStopped = false;
int               g_consecutiveLosses = 0;
datetime          g_lossCooldownUntil = 0;
datetime          g_lastRiskGuardLogTime = 0;
string            g_lastRiskGuardLogReason = "";
double            g_initialEquity = 0.0;
double            g_peakEquity = 0.0;
bool              g_peakGuardStopped = false;
bool              g_floorGuardStopped = false;
static const ulong V10_MAGIC = 2026042499;
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


string V11EngineLabel(const string engineCode)
  {
   if(engineCode == "ZB")
      return("Zone Retest Buy");
   if(engineCode == "ZS")
      return("Zone Retest Sell");
   if(engineCode == "BE")
      return("Bearish Breakout Sell");
   if(engineCode == "BO")
      return("Bullish Breakout Buy");
   if(engineCode == "PB")
      return("Bullish Pullback Buy");
   if(engineCode == "IB")
      return("Impulse Pullback Buy");
   if(engineCode == "IS")
      return("Impulse Pullback Sell");
   if(engineCode == "BC")
      return("Bull Compression Breakout");
   if(engineCode == "SS")
      return("Bear Compression Breakdown");
   if(engineCode == "AB")
      return("Buy Add-on Continuation");
   if(engineCode == "AS")
      return("Sell Add-on Continuation");
   return(engineCode);
  }


string V11EngineComment(const string engineCode)
  {
   if(engineCode == "ZB")
      return("BUY_ZONE");
   if(engineCode == "ZS")
      return("SELL_ZONE");
   if(engineCode == "BE")
      return("SELL_BREAK");
   if(engineCode == "BO")
      return("BUY_BREAK");
   if(engineCode == "PB")
      return("BUY_PULLBACK");
   if(engineCode == "IB")
      return("BUY_IMPULSE");
   if(engineCode == "IS")
      return("SELL_IMPULSE");
   if(engineCode == "BC")
      return("BUY_COMP");
   if(engineCode == "SS")
      return("SELL_COMP");
   if(engineCode == "AB")
      return("BUY_ADDON");
   if(engineCode == "AS")
      return("SELL_ADDON");
   return(engineCode);
  }


string V11TagLabel(const string tag)
  {
   if(tag == "RG")
      return("strong-regime");
   if(tag == "WG")
      return("weak-regime");
   if(tag == "RJ")
      return("rejection");
   if(tag == "BR")
      return("breakout");
   if(tag == "SE")
      return("sell-session");
   if(tag == "CH")
      return("core-hour");
   if(tag == "XH")
      return("outside-core-hour");
   if(tag == "RC")
      return("reclaim");
   if(tag == "ZN")
      return("zone");
   if(tag == "RT")
      return("retest");
   if(tag == "BM")
      return("body-midpoint");
   if(tag == "CM")
      return("compression");
   if(tag == "EM")
      return("ema-touch");
   if(tag == "AD")
      return("add-on");
   if(tag == "CT")
      return("continuation");
   if(tag == "BX")
      return("boosted");
   if(tag == "IP")
      return("impulse");
   return(tag);
  }


string V11TagsHuman(const string tags)
  {
   if(tags == "")
      return("-");

   string parts[];
   ushort separator = StringGetCharacter("|", 0);
   int count = StringSplit(tags, separator, parts);
   string human = "";
   for(int i = 0; i < count; i++)
     {
      if(i > 0)
         human += ", ";
      human += V11TagLabel(parts[i]);
     }
   return(human);
  }


void V11RejectedSignalLog(const string direction,
                          const string engineCode,
                          const string reason,
                          const int score,
                          const V10Regime regime,
                          const int hour,
                          const double bodyRatio,
                          const double breakAtr,
                          const string note)
  {
   if(!V11_LogRejectedSignals || score < V11_MinRejectedScoreToLog)
      return;
   PrintFormat("V11 REJECT %s | engine=%s (%s) | reason=%s | score=%d min=%d | regime=%s | hour=%02d | body=%.2f breakATR=%.2f | note=%s",
               direction,
               V11EngineLabel(engineCode),
               engineCode,
               reason,
               score,
               V10_MinTradeScore,
               V10RegimeLabel(regime),
               hour,
               bodyRatio,
               breakAtr,
               note);
  }


void V11ExitActionLog(const string action,
                      const ulong ticket,
                      const string comment,
                      const string reason,
                      const int barsHeld,
                      const double progressR,
                      const double stopLoss,
                      const double takeProfit)
  {
   if(!V11_LogExitActions)
      return;
   PrintFormat("V11 EXIT %s | ticket=%I64u | %s | reason=%s | bars=%d progressR=%.2f | sl=%.2f tp=%.2f",
               action,
               ticket,
               comment,
               reason,
               barsHeld,
               progressR,
               stopLoss,
               takeProfit);
  }


bool V11BearSafePass(const string engineCode,
                     const V10Regime regime,
                     const int score,
                     const int hour,
                     const double bodyRatio,
                     const double breakAtr)
  {
   if(!V11_EnableBearSafeMode)
      return(true);
   if(!V10RegimeIsBear(regime))
      return(true);

   bool strongBear = regime == V10_REGIME_STRONG_BEAR;
   if(strongBear)
      return(score >= V11_BearSafeStrongMinScore);

   if(score < V11_BearSafeWeakMinScore)
      return(false);
   if(bodyRatio < V11_BearSafeWeakMinBodyRatio)
      return(false);
   if(V11_BearSafeBlockWeakZone && engineCode == "ZS")
      return(false);
   if(V11_BearSafeBlockWeakAddOns && engineCode == "AS")
      return(false);
   return(true);
  }


bool V11EngineTimeCloseProfitOnly(const ENUM_POSITION_TYPE type, const string comment)
  {
   if(type == POSITION_TYPE_BUY)
     {
      if(StringFind(comment, "|ZB|") >= 0)
         return(V11_BuyZoneTimeCloseProfitOnly);
      if(StringFind(comment, "|IB|") >= 0)
         return(V11_BuyImpulseTimeCloseProfitOnly);
      if(StringFind(comment, "|BC|") >= 0)
         return(V11_BuyCompTimeCloseProfitOnly);
      if(StringFind(comment, "|AB|") >= 0)
         return(V11_BuyAddOnTimeCloseProfitOnly);
      return(V11_BuyBreakTimeCloseProfitOnly);
     }

   if(StringFind(comment, "|ZS|") >= 0)
      return(V11_SellZoneTimeCloseProfitOnly);
   if(StringFind(comment, "|IS|") >= 0)
      return(V11_SellImpulseTimeCloseProfitOnly);
   if(StringFind(comment, "|SS|") >= 0)
      return(V11_SellCompTimeCloseProfitOnly);
   if(StringFind(comment, "|AS|") >= 0)
      return(V11_SellAddOnTimeCloseProfitOnly);
   return(V11_SellBreakTimeCloseProfitOnly);
  }


void V11StatusLog(const bool entered)
  {
   if(!V11_LogStatusOnNewBar)
      return;
   g_statusBarCounter++;
   if(V11_StatusEveryBars > 1 && (g_statusBarCounter % V11_StatusEveryBars) != 0)
      return;

   double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   double spread = (ask > 0.0 && bid > 0.0) ? (ask - bid) : 0.0;
   V10Regime regime = V10DetectRegime();
   PrintFormat("V11 STATUS | symbol=%s tf=M5 | regime=%s | open=%d buy=%d sell=%d | spread=%.2f | equity=%.2f | entered=%s | rejectLog=%s",
               _Symbol,
               V10RegimeLabel(regime),
               V10CountOpenPositions(),
               V10CountOpenPositionsByType(false),
               V10CountOpenPositionsByType(true),
               spread,
               AccountInfoDouble(ACCOUNT_EQUITY),
               entered ? "yes" : "no",
               V11_LogRejectedSignals ? "on" : "off");
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
   string comment = "SUI|" + V11EngineComment(engineCode) + "|" + engineCode + "|S" + IntegerToString(score) + "|" + grade;
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


bool V11HourListContains(string hours, const int hour)
  {
   StringReplace(hours, " ", "");
   StringReplace(hours, ";", ",");
   if(StringLen(hours) == 0)
      return(false);
   string wrapped = "," + hours + ",";
   string plainHour = "," + IntegerToString(hour) + ",";
   string paddedHour = "," + StringFormat("%02d", hour) + ",";
   return(StringFind(wrapped, plainHour) >= 0 || StringFind(wrapped, paddedHour) >= 0);
  }


bool V11EngineHourBlocked(const string engineCode, const int hour)
  {
   if(engineCode == "BO")
      return(V11HourListContains(V11_BlockBuyBreakHours, hour));
   if(engineCode == "PB")
      return(V11HourListContains(V11_BlockBuyPullbackHours, hour));
   if(engineCode == "ZB")
      return(V11HourListContains(V11_BlockBuyZoneHours, hour));
   if(engineCode == "IB")
      return(V11HourListContains(V11_BlockBuyImpulseHours, hour));
   if(engineCode == "BC")
      return(V11HourListContains(V11_BlockBuySubHours, hour));
   if(engineCode == "AB")
      return(V11HourListContains(V11_BlockBuyAddOnHours, hour));
   if(engineCode == "BE")
      return(V11HourListContains(V11_BlockSellBreakHours, hour));
   if(engineCode == "ZS")
      return(V11HourListContains(V11_BlockSellZoneHours, hour));
   if(engineCode == "IS")
      return(V11HourListContains(V11_BlockSellImpulseHours, hour));
   if(engineCode == "SS")
      return(V11HourListContains(V11_BlockSellSubHours, hour));
   if(engineCode == "AS")
      return(V11HourListContains(V11_BlockSellAddOnHours, hour));
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


bool V11TradeSessionLikelyOpen()
  {
   MqlDateTime dt;
   TimeToStruct(TimeCurrent(), dt);
   if(dt.day_of_week == 6)
      return(false);
   if(dt.day_of_week == 0 && dt.hour < 23)
      return(false);
   if(dt.day_of_week == 5 && dt.hour >= 21)
      return(false);
   long tradeMode = SymbolInfoInteger(_Symbol, SYMBOL_TRADE_MODE);
   return(tradeMode == SYMBOL_TRADE_MODE_FULL ||
          tradeMode == SYMBOL_TRADE_MODE_LONGONLY ||
          tradeMode == SYMBOL_TRADE_MODE_SHORTONLY ||
          tradeMode == SYMBOL_TRADE_MODE_CLOSEONLY);
  }


int V11DayKey(const datetime ts)
  {
   MqlDateTime dt;
   TimeToStruct(ts, dt);
   return((dt.year * 1000) + dt.day_of_year);
  }


void V11RiskGuardLog(const string reason, const bool force = false)
  {
   if(!V11_DailyGuardLog)
      return;
   datetime now = TimeCurrent();
   if(!force && reason == g_lastRiskGuardLogReason && (now - g_lastRiskGuardLogTime) < 3600)
      return;
   g_lastRiskGuardLogReason = reason;
   g_lastRiskGuardLogTime = now;
   PrintFormat("V11 RISK GUARD | %s | dayStart=%.2f dayHigh=%.2f equity=%.2f consecutiveLosses=%d cooldownUntil=%s",
               reason,
               g_dailyStartEquity,
               g_dailyHighEquity,
               AccountInfoDouble(ACCOUNT_EQUITY),
               g_consecutiveLosses,
               TimeToString(g_lossCooldownUntil, TIME_DATE | TIME_MINUTES));
  }


void V11ResetDailyGuardIfNeeded()
  {
   int dayKey = V11DayKey(TimeCurrent());
   if(dayKey == g_dailyGuardDay)
      return;
   g_dailyGuardDay = dayKey;
   g_dailyStartEquity = AccountInfoDouble(ACCOUNT_EQUITY);
   g_dailyHighEquity = g_dailyStartEquity;
   g_dailyStopped = false;
   g_consecutiveLosses = 0;
   g_lossCooldownUntil = 0;
   V11RiskGuardLog("new trading day reset", true);
  }


void V12InitEquityState()
  {
   double equity = AccountInfoDouble(ACCOUNT_EQUITY);
   if(g_initialEquity <= 0.0)
      g_initialEquity = equity;
   if(g_peakEquity <= 0.0)
      g_peakEquity = equity;
   g_peakEquity = MathMax(g_peakEquity, equity);
  }


double V12PeakDrawdownPct()
  {
   V12InitEquityState();
   double equity = AccountInfoDouble(ACCOUNT_EQUITY);
   if(g_peakEquity <= 0.0)
      return(0.0);
   return(MathMax(0.0, (g_peakEquity - equity) / g_peakEquity * 100.0));
  }


double V12RiskThrottleMultiplier()
  {
   if(!V12_EnableDynamicRiskThrottle)
      return(1.0);
   double full = MathMax(V12_ThrottleFullDrawdownPct, V12_ThrottleStartDrawdownPct + 0.01);
   double drawdown = V12PeakDrawdownPct();
   if(drawdown <= V12_ThrottleStartDrawdownPct)
      return(1.0);
   if(drawdown >= full)
      return(V12_ThrottleMinMultiplier);
   double progress = (drawdown - V12_ThrottleStartDrawdownPct) / (full - V12_ThrottleStartDrawdownPct);
   return(1.0 - ((1.0 - V12_ThrottleMinMultiplier) * progress));
  }


double V12BootstrapRiskMultiplier()
  {
   if(!V12_EnableBootstrapRiskRamp)
      return(1.0);
   V12InitEquityState();
   if(g_initialEquity <= 0.0)
      return(1.0);

   double equityPct = AccountInfoDouble(ACCOUNT_EQUITY) / g_initialEquity * 100.0;
   double full = MathMax(V12_BootstrapFullEquityPct, V12_BootstrapStartEquityPct + 0.01);
   if(equityPct <= V12_BootstrapStartEquityPct)
      return(V12_BootstrapMinMultiplier);
   if(equityPct >= full)
      return(1.0);

   double progress = (equityPct - V12_BootstrapStartEquityPct) / (full - V12_BootstrapStartEquityPct);
   return(V12_BootstrapMinMultiplier + ((1.0 - V12_BootstrapMinMultiplier) * progress));
  }


double V12ApplyRiskControls(const double rawRiskUsd)
  {
   double riskUsd = rawRiskUsd * V12BootstrapRiskMultiplier() * V12RiskThrottleMultiplier();
   if(V12_RiskBudgetCapPctOfStartEquity > 0.0)
     {
      V12InitEquityState();
      double cap = g_initialEquity * (V12_RiskBudgetCapPctOfStartEquity / 100.0);
      if(cap > 0.0)
         riskUsd = MathMin(riskUsd, cap);
     }
   return(MathMax(0.0, riskUsd));
  }


void V11CloseOwnPositions(const string reason)
  {
   if(!V11TradeSessionLikelyOpen())
      return;

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

      string comment = PositionGetString(POSITION_COMMENT);
      double stopLoss = PositionGetDouble(POSITION_SL);
      double takeProfit = PositionGetDouble(POSITION_TP);
      if(g_trade.PositionClose(ticket))
         V11ExitActionLog("RISK_GUARD_CLOSE", ticket, comment, reason, 0, 0.0, stopLoss, takeProfit);
     }
  }


bool V11RiskGuardAllowsTrading(const bool allowClose)
  {
   if(!V11_EnableDailyGuard &&
      (V11_MaxConsecutiveLosses <= 0 || V11_LossCooldownMinutes <= 0) &&
      !V12_EnablePeakEquityGuard &&
      V12_MinEquityFloorPct <= 0.0)
      return(true);

   V12InitEquityState();
   V11ResetDailyGuardIfNeeded();
   datetime now = TimeCurrent();
   bool blocked = false;
   string reason = "";
   double equity = AccountInfoDouble(ACCOUNT_EQUITY);

   if(V11_EnableDailyGuard)
     {
      if(g_dailyStartEquity <= 0.0)
         g_dailyStartEquity = equity;
      g_dailyHighEquity = MathMax(g_dailyHighEquity, equity);

      double dayPct = (g_dailyStartEquity > 0.0) ? ((equity - g_dailyStartEquity) / g_dailyStartEquity * 100.0) : 0.0;
      double highPct = (g_dailyStartEquity > 0.0) ? ((g_dailyHighEquity - g_dailyStartEquity) / g_dailyStartEquity * 100.0) : 0.0;
      bool hitLoss = V11_DailyMaxLossPct > 0.0 && dayPct <= -V11_DailyMaxLossPct;
      bool hitProfit = V11_DailyProfitStopPct > 0.0 && dayPct >= V11_DailyProfitStopPct;
      bool hitGiveback = V11_DailyProfitLockStartPct > 0.0 &&
                         V11_DailyMaxGivebackPct > 0.0 &&
                         highPct >= V11_DailyProfitLockStartPct &&
                         (highPct - dayPct) >= V11_DailyMaxGivebackPct;

      if((hitLoss || hitProfit || hitGiveback) && !g_dailyStopped)
        {
         g_dailyStopped = true;
         if(hitLoss)
            reason = StringFormat("daily max loss hit %.2f%% <= -%.2f%%", dayPct, V11_DailyMaxLossPct);
         else if(hitProfit)
            reason = StringFormat("daily profit stop hit %.2f%% >= %.2f%%", dayPct, V11_DailyProfitStopPct);
         else
            reason = StringFormat("daily giveback hit high %.2f%% now %.2f%% giveback %.2f%%", highPct, dayPct, highPct - dayPct);
         V11RiskGuardLog(reason, true);
         if(allowClose && V11_DailyClosePositionsOnStop)
            V11CloseOwnPositions(reason);
        }

      if(g_dailyStopped)
        {
         blocked = true;
         reason = "daily guard stopped trading until next day";
        }
     }

   if(V12_EnablePeakEquityGuard)
     {
      double peakDd = V12PeakDrawdownPct();
      bool hitPeakGuard = V12_PeakDrawdownStopPct > 0.0 && peakDd >= V12_PeakDrawdownStopPct;
      if(hitPeakGuard && !g_peakGuardStopped)
        {
         g_peakGuardStopped = true;
         reason = StringFormat("peak equity drawdown hit %.2f%% >= %.2f%%", peakDd, V12_PeakDrawdownStopPct);
         V11RiskGuardLog(reason, true);
         if(allowClose && V12_PeakClosePositionsOnStop)
            V11CloseOwnPositions(reason);
        }
      if(g_peakGuardStopped)
        {
         blocked = true;
         reason = "peak equity guard stopped trading";
        }
     }

   if(V12_MinEquityFloorPct > 0.0 && g_initialEquity > 0.0)
     {
      double floorEquity = g_initialEquity * (V12_MinEquityFloorPct / 100.0);
      if(equity <= floorEquity && !g_floorGuardStopped)
        {
         g_floorGuardStopped = true;
         reason = StringFormat("initial equity floor hit %.2f <= %.2f", equity, floorEquity);
         V11RiskGuardLog(reason, true);
         if(allowClose && V12_FloorClosePositionsOnStop)
            V11CloseOwnPositions(reason);
        }
      if(g_floorGuardStopped)
        {
         blocked = true;
         reason = "initial equity floor guard stopped trading";
        }
     }

   if(V11_LossCooldownMinutes > 0 && now < g_lossCooldownUntil)
     {
      blocked = true;
      reason = "loss streak cooldown active";
     }

   if(blocked)
      V11RiskGuardLog("entry blocked: " + reason);
   return(!blocked);
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


bool V11HasOpenPositionByMagicType(const bool sell, const ulong magic)
  {
   for(int i = PositionsTotal() - 1; i >= 0; i--)
     {
      ulong ticket = PositionGetTicket(i);
      if(ticket == 0 || !PositionSelectByTicket(ticket))
         continue;
      if(PositionGetString(POSITION_SYMBOL) != _Symbol)
         continue;
      if((ulong)PositionGetInteger(POSITION_MAGIC) != magic)
         continue;
      ENUM_POSITION_TYPE type = (ENUM_POSITION_TYPE)PositionGetInteger(POSITION_TYPE);
      if((sell && type == POSITION_TYPE_SELL) || (!sell && type == POSITION_TYPE_BUY))
         return(true);
     }
   return(false);
  }

bool V11OppositePositionBlocks(const bool wantSell)
  {
   if(!V11_BlockOppositeDirection)
      return(false);
   bool oppositeSell = !wantSell;
   if(V11HasOpenPositionByMagicType(oppositeSell, V10_MAGIC))
      return(true);
   if(V11_OppositeMagic > 0 && V11HasOpenPositionByMagicType(oppositeSell, (ulong)V11_OppositeMagic))
      return(true);
   return(false);
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
   if(V11_MaxLotCap > 0.0)
      maxLot = MathMin(maxLot, V11_MaxLotCap);
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

double V12RiskUsdForLot(const double entry, const double stopLoss, const double lot)
  {
   double tickSize = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);
   double tickValue = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE_LOSS);
   if(tickValue <= 0.0)
      tickValue = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE);
   if(tickSize <= 0.0 || tickValue <= 0.0 || lot <= 0.0)
      return(0.0);

   double distance = MathAbs(entry - stopLoss);
   if(distance <= 0.0)
      return(0.0);
   return((distance / tickSize) * tickValue * lot);
  }


double V12OpenRiskUsd()
  {
   double total = 0.0;
   for(int i = PositionsTotal() - 1; i >= 0; i--)
     {
      ulong ticket = PositionGetTicket(i);
      if(ticket == 0 || !PositionSelectByTicket(ticket))
         continue;
      if(PositionGetString(POSITION_SYMBOL) != _Symbol)
         continue;
      if((ulong)PositionGetInteger(POSITION_MAGIC) != V10_MAGIC)
         continue;

      double openPrice = PositionGetDouble(POSITION_PRICE_OPEN);
      double stopLoss = PositionGetDouble(POSITION_SL);
      double volume = PositionGetDouble(POSITION_VOLUME);
      if(stopLoss <= 0.0)
         continue;
      total += V12RiskUsdForLot(openPrice, stopLoss, volume);
     }
   return(total);
  }


bool V12SignalFitsOpenRisk(const V10Signal &signal)
  {
   double cap = 0.0;
   double equity = AccountInfoDouble(ACCOUNT_EQUITY);
   if(V12_MaxOpenRiskPctOfEquity > 0.0 && equity > 0.0)
      cap = equity * (V12_MaxOpenRiskPctOfEquity / 100.0);
   if(V12_MaxOpenRiskPctOfStartEquity > 0.0)
     {
      V12InitEquityState();
      if(g_initialEquity > 0.0)
        {
         double startCap = g_initialEquity * (V12_MaxOpenRiskPctOfStartEquity / 100.0);
         cap = (cap > 0.0) ? MathMin(cap, startCap) : startCap;
        }
     }
   if(cap <= 0.0)
      return(true);

   double signalRisk = V12RiskUsdForLot(signal.entry, signal.stopLoss, signal.lot);
   return((V12OpenRiskUsd() + signalRisk) <= cap);
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
   return(V12ApplyRiskControls(riskUsd));
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
   return(V12ApplyRiskControls(riskUsd * multiplier));
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
   if(V11EngineHourBlocked("BE", currentHour))
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
     {
      V11RejectedSignalLog("SELL", "BE", "score below gate", score, regime, currentHour, bodyRatio, breakAtr,
                           StringFormat("minBreakATR=%.2f rejection=%s coreSession=%s", minBreakAtr, rejectionSeen ? "yes" : "no", sessionCore ? "yes" : "no"));
      return(false);
     }
   if(!V11BearSafePass("BE", regime, score, currentHour, bodyRatio, breakAtr))
     {
      V11RejectedSignalLog("SELL", "BE", "bear safe mode", score, regime, currentHour, bodyRatio, breakAtr,
                           StringFormat("weakMinScore=%d weakMinBody=%.2f", V11_BearSafeWeakMinScore, V11_BearSafeWeakMinBodyRatio));
      return(false);
     }

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
   if(V11EngineHourBlocked("BC", currentHour))
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
     {
      V11RejectedSignalLog("BUY", "BC", "score below gate", score, regime, currentHour, bodyRatio, boxRange / atr,
                           StringFormat("compressionBoxATR=%.2f compact=%s tightToEma=%s", boxRange / atr, compactBox ? "yes" : "no", tightToEma ? "yes" : "no"));
      return(false);
     }

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
   V10FillSignalMeta(signal, "BC", score, tags, note);
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
   if(V11EngineHourBlocked("SS", currentHour))
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
     {
      V11RejectedSignalLog("SELL", "SS", "score below gate", score, regime, currentHour, bodyRatio, boxRange / atr,
                           StringFormat("compressionBoxATR=%.2f compact=%s tightToEma=%s", boxRange / atr, compactBox ? "yes" : "no", tightToEma ? "yes" : "no"));
      return(false);
     }
   if(!V11BearSafePass("SS", regime, score, currentHour, bodyRatio, boxRange / atr))
     {
      V11RejectedSignalLog("SELL", "SS", "bear safe mode", score, regime, currentHour, bodyRatio, boxRange / atr,
                           StringFormat("compressionBoxATR=%.2f", boxRange / atr));
      return(false);
     }

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


bool V11BuildImpulsePullbackSignal(const MqlRates &rates[], const double emaM5, const double atr, const V10Regime regime, const bool sell, V10Signal &signal)
  {
   if(!V11_EnableImpulsePullbackEngine)
      return(false);
   if(sell && !V11_EnableSellImpulsePullback)
      return(false);
   if(!sell && !V11_EnableBuyImpulsePullback)
      return(false);
   if(atr <= 0.0 || emaM5 <= 0.0 || ArraySize(rates) < 6)
      return(false);
   if(sell)
     {
      if(!V10_EnableSells || !V10RegimeIsBear(regime))
         return(false);
     }
   else
     {
      if(!V10_EnableBuys || !V10RegimeIsBull(regime))
         return(false);
     }
   if(!V11_ImpulseAllowWeakRegime && !V10RegimeIsStrong(regime))
      return(false);

   int currentHour = V10HourOf(TimeCurrent());
   if(!V10HourInSession(currentHour, V11_ImpulseSessionStartHour, V11_ImpulseSessionEndHour))
      return(false);
   if(!sell && V10BuyHourBlocked(currentHour))
      return(false);
   if(V11EngineHourBlocked(sell ? "IS" : "IB", currentHour))
      return(false);

   const MqlRates trigger = rates[1];
   const MqlRates pullback = rates[2];
   const MqlRates impulse = rates[3];
   double impulseBody = V10BodyRatio(impulse);
   double triggerBody = V10BodyRatio(trigger);
   double impulseMoveAtr = MathAbs(impulse.close - impulse.open) / atr;
   double pullbackRangeAtr = (pullback.high - pullback.low) / atr;
   if(impulseBody < V11_ImpulseMinBodyRatio || impulseMoveAtr < V11_ImpulseMinMoveATR)
      return(false);
   if(triggerBody < V11_ImpulseEntryBodyRatio || pullbackRangeAtr > V11_ImpulsePullbackMaxATR)
      return(false);
   if(!V10DirectionalHoldOk(sell, rates, atr))
      return(false);

   if(sell)
     {
      if(impulse.close >= impulse.open || trigger.close >= trigger.open)
         return(false);
      if(pullback.high > (impulse.open + (atr * V11_ImpulsePullbackMaxATR)))
         return(false);
      if(trigger.close >= emaM5)
         return(false);
      if(trigger.close > (pullback.low - (atr * V11_ImpulseBreakATR)))
         return(false);
      if((emaM5 - trigger.close) > (atr * V10_MaxStretchATR))
         return(false);

      bool brokeImpulse = trigger.close <= impulse.close;
      bool compactPullback = pullbackRangeAtr <= 0.55;
      int score = 42;
      score += V10RegimeIsStrong(regime) ? 15 : 8;
      if(triggerBody >= (V11_ImpulseEntryBodyRatio + 0.10))
         score += 10;
      if(impulseMoveAtr >= (V11_ImpulseMinMoveATR + 0.35))
         score += 10;
      if(compactPullback)
         score += 8;
      if(brokeImpulse)
         score += 8;
      if(V10_MinTradeScore > 0 && score < V10_MinTradeScore)
        {
         V11RejectedSignalLog("SELL", "IS", "score below gate", score, regime, currentHour, triggerBody, impulseMoveAtr,
                              StringFormat("impulseBody=%.2f pullbackATR=%.2f brokeImpulse=%s", impulseBody, pullbackRangeAtr, brokeImpulse ? "yes" : "no"));
         return(false);
        }
      if(!V11BearSafePass("IS", regime, score, currentHour, triggerBody, impulseMoveAtr))
        {
         V11RejectedSignalLog("SELL", "IS", "bear safe mode", score, regime, currentHour, triggerBody, impulseMoveAtr,
                              StringFormat("impulseBody=%.2f pullbackATR=%.2f", impulseBody, pullbackRangeAtr));
         return(false);
        }

      double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
      if(bid <= 0.0)
         return(false);
      double stopAnchor = MathMax(MathMax(impulse.high, pullback.high), trigger.high);
      double stopDistance = V10Clamp((stopAnchor - bid) + (atr * V10_StopBufferATR), V10_MinSLUsd, V10_MaxSLUsd);
      double stopLoss = V10NormalizePrice(bid + stopDistance);
      double takeProfit = V10NormalizePrice(bid - (stopDistance * V11_ImpulseRR));
      if(!V10StopsValid(true, bid, stopLoss, takeProfit))
         return(false);
      double riskUsd = V10RiskBudgetUsd(true, regime) * V11_ImpulseRiskMultiplier;
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
      signal.rr = V11_ImpulseRR;
      string tags = V10AppendTag("", V10RegimeIsStrong(regime) ? "RG" : "WG");
      tags = V10AppendTag(tags, "IP");
      tags = V10AppendTag(tags, "RT");
      tags = V10AppendTag(tags, brokeImpulse ? "BR" : "CT");
      string note = StringFormat("IMPULSE SELL score=%d impulseATR=%.2f impulseBody=%.2f triggerBody=%.2f pullbackATR=%.2f regime=%s hour=%02d rr=%.2f",
                                 score, impulseMoveAtr, impulseBody, triggerBody, pullbackRangeAtr, V10RegimeLabel(regime), currentHour, V11_ImpulseRR);
      V10FillSignalMeta(signal, "IS", score, tags, note);
      return(true);
     }

   if(impulse.close <= impulse.open || trigger.close <= trigger.open)
      return(false);
   if(pullback.low < (impulse.open - (atr * V11_ImpulsePullbackMaxATR)))
      return(false);
   if(trigger.close <= emaM5)
      return(false);
   if(trigger.close < (pullback.high + (atr * V11_ImpulseBreakATR)))
      return(false);
   if((trigger.close - emaM5) > (atr * V10_BullMaxStretchATR))
      return(false);

   bool brokeImpulse = trigger.close >= impulse.close;
   bool compactPullback = pullbackRangeAtr <= 0.55;
   int score = 42;
   score += V10RegimeIsStrong(regime) ? 15 : 8;
   if(triggerBody >= (V11_ImpulseEntryBodyRatio + 0.10))
      score += 10;
   if(impulseMoveAtr >= (V11_ImpulseMinMoveATR + 0.35))
      score += 10;
   if(compactPullback)
      score += 8;
   if(brokeImpulse)
      score += 8;
   if(V10_MinTradeScore > 0 && score < V10_MinTradeScore)
     {
      V11RejectedSignalLog("BUY", "IB", "score below gate", score, regime, currentHour, triggerBody, impulseMoveAtr,
                           StringFormat("impulseBody=%.2f pullbackATR=%.2f brokeImpulse=%s", impulseBody, pullbackRangeAtr, brokeImpulse ? "yes" : "no"));
      return(false);
     }

   double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   if(ask <= 0.0)
      return(false);
   double stopAnchor = MathMin(MathMin(impulse.low, pullback.low), trigger.low);
   double stopDistance = V10Clamp((ask - stopAnchor) + (atr * V10_StopBufferATR), V10_MinSLUsd, V10_MaxSLUsd);
   double stopLoss = V10NormalizePrice(ask - stopDistance);
   double takeProfit = V10NormalizePrice(ask + (stopDistance * V11_ImpulseRR));
   if(!V10StopsValid(false, ask, stopLoss, takeProfit))
      return(false);
   double riskUsd = V10BuyRiskBudgetUsd(regime, V11_ImpulseRiskMultiplier);
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
   signal.rr = V11_ImpulseRR;
   string tags = V10AppendTag("", V10RegimeIsStrong(regime) ? "RG" : "WG");
   tags = V10AppendTag(tags, "IP");
   tags = V10AppendTag(tags, "RT");
   tags = V10AppendTag(tags, brokeImpulse ? "BR" : "CT");
   string note = StringFormat("IMPULSE BUY score=%d impulseATR=%.2f impulseBody=%.2f triggerBody=%.2f pullbackATR=%.2f regime=%s hour=%02d rr=%.2f",
                              score, impulseMoveAtr, impulseBody, triggerBody, pullbackRangeAtr, V10RegimeLabel(regime), currentHour, V11_ImpulseRR);
   V10FillSignalMeta(signal, "IB", score, tags, note);
   return(true);
  }


bool V10BuildZoneRetestSignal(const MqlRates &rates[], const double emaM5, const double atr, const V10Regime regime, const bool sell, V10Signal &signal)
  {
   if(!V10_EnableZoneRetestEngine)
      return(false);
   if(sell)
     {
      if(!V10_EnableSells || !V10RegimeIsBear(regime))
         return(false);
      if(!V10_ZoneAllowWeakRegime && !V10RegimeIsStrong(regime))
         return(false);
     }
   else
     {
      if(!V10_EnableBuys || !V10RegimeIsBull(regime))
         return(false);
      if(!V10_ZoneAllowWeakRegime && !V10RegimeIsStrong(regime))
         return(false);
     }

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
      if(V10_ZoneUseCoreHours && !V10BuyHourPreferred(currentHour))
         return(false);
      if(V10BuyHourBlocked(currentHour))
         return(false);
     }
   if(V11EngineHourBlocked(sell ? "ZS" : "ZB", currentHour))
      return(false);

   const MqlRates retest = rates[1];
   const MqlRates anchor = rates[2];
   if(V10BodyRatio(anchor) < V10_ZoneMinBodyRatio)
      return(false);
   if(V10BodyRatio(retest) < 0.35)
      return(false);
   if(!V10DirectionalHoldOk(sell, rates, atr))
      return(false);

   int lookbackEnd = MathMin(V10_ZoneLookback + 2, ArraySize(rates) - 1);
   if(lookbackEnd <= 3)
      return(false);

   if(sell)
     {
      if(anchor.close >= anchor.open || retest.close >= retest.open)
         return(false);
      double priorLow = V10LowestLow(rates, 3, lookbackEnd);
      double breakAtr = (priorLow - anchor.close) / atr;
      if(anchor.close > (priorLow - (atr * V10_ZoneBreakATR)))
         return(false);
      if(retest.close >= emaM5)
         return(false);

      double zoneHigh = MathMax(anchor.open, anchor.close);
      double zoneLow = MathMin(anchor.open, anchor.close);
      double zoneMid = (zoneHigh + zoneLow) * 0.5;
      bool touchedMid = retest.high >= (zoneMid - (atr * V10_ZoneMidTouchATR));
      bool overshootOk = retest.high <= (zoneHigh + (atr * V10_ZoneOvershootATR));
      bool reclaimed = retest.close <= (zoneMid - (atr * V10_ZoneReclaimATR));
      if(!touchedMid || !overshootOk || !reclaimed)
         return(false);

      double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
      if(bid <= 0.0)
         return(false);
      double stopAnchor = MathMax(anchor.high, retest.high);
      double stopDistance = V10Clamp((stopAnchor - bid) + (atr * V10_StopBufferATR), V10_MinSLUsd, V10_MaxSLUsd);
      double stopLoss = V10NormalizePrice(bid + stopDistance);
      double rr = V10_ZoneRR;
      int score = 45;
      if(V10RegimeIsStrong(regime))
         score += 15;
      else
         score += 8;
      score += 12;
      if(V10BodyRatio(anchor) >= (V10_ZoneMinBodyRatio + 0.08))
         score += 8;
      if(breakAtr >= (V10_ZoneBreakATR + 0.06))
         score += 10;
      if(touchedMid)
         score += 8;
      if(reclaimed)
         score += 6;
      if(V10_MinTradeScore > 0 && score < V10_MinTradeScore)
        {
         V11RejectedSignalLog("SELL", "ZS", "score below gate", score, regime, currentHour, V10BodyRatio(retest), breakAtr,
                              StringFormat("anchorBody=%.2f touchedMid=%s reclaimed=%s", V10BodyRatio(anchor), touchedMid ? "yes" : "no", reclaimed ? "yes" : "no"));
         return(false);
        }
      if(!V11BearSafePass("ZS", regime, score, currentHour, V10BodyRatio(retest), breakAtr))
        {
         V11RejectedSignalLog("SELL", "ZS", "bear safe mode", score, regime, currentHour, V10BodyRatio(retest), breakAtr,
                              StringFormat("anchorBody=%.2f blockWeakZone=%s", V10BodyRatio(anchor), V11_BearSafeBlockWeakZone ? "yes" : "no"));
         return(false);
        }

      double takeProfit = V10NormalizePrice(bid - (stopDistance * rr));
      if(!V10StopsValid(true, bid, stopLoss, takeProfit))
         return(false);
      double riskUsd = V10RiskBudgetUsd(true, regime) * V10_ZoneRiskMultiplier;
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
      tags = V10AppendTag(tags, "ZN");
      tags = V10AppendTag(tags, "RT");
      tags = V10AppendTag(tags, "BM");
      string note = StringFormat("ZONE SELL score=%d breakATR=%.2f anchorBody=%.2f retestBody=%.2f regime=%s hour=%02d rr=%.2f",
                                 score, breakAtr, V10BodyRatio(anchor), V10BodyRatio(retest), V10RegimeLabel(regime), currentHour, rr);
      V10FillSignalMeta(signal, "ZS", score, tags, note);
      return(true);
     }

   if(anchor.close <= anchor.open || retest.close <= retest.open)
      return(false);
   double priorHigh = V10HighestHigh(rates, 3, lookbackEnd);
   double breakAtr = (anchor.close - priorHigh) / atr;
   if(anchor.close < (priorHigh + (atr * V10_ZoneBreakATR)))
      return(false);
   if(retest.close <= emaM5)
      return(false);

   double zoneHigh = MathMax(anchor.open, anchor.close);
   double zoneLow = MathMin(anchor.open, anchor.close);
   double zoneMid = (zoneHigh + zoneLow) * 0.5;
   bool touchedMid = retest.low <= (zoneMid + (atr * V10_ZoneMidTouchATR));
   bool overshootOk = retest.low >= (zoneLow - (atr * V10_ZoneOvershootATR));
   bool reclaimed = retest.close >= (zoneMid + (atr * V10_ZoneReclaimATR));
   if(!touchedMid || !overshootOk || !reclaimed)
      return(false);

   double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   if(ask <= 0.0)
      return(false);
   double stopAnchor = MathMin(anchor.low, retest.low);
   double stopDistance = V10Clamp((ask - stopAnchor) + (atr * V10_StopBufferATR), V10_MinSLUsd, V10_MaxSLUsd);
   double stopLoss = V10NormalizePrice(ask - stopDistance);
   double rr = V10_ZoneRR;
   int score = 45;
   if(V10RegimeIsStrong(regime))
      score += 15;
   else
      score += 8;
   score += 12;
   if(V10BodyRatio(anchor) >= (V10_ZoneMinBodyRatio + 0.08))
      score += 8;
   if(breakAtr >= (V10_ZoneBreakATR + 0.06))
      score += 10;
   if(touchedMid)
      score += 8;
   if(reclaimed)
      score += 6;
   if(V10_MinTradeScore > 0 && score < V10_MinTradeScore)
     {
      V11RejectedSignalLog("BUY", "ZB", "score below gate", score, regime, currentHour, V10BodyRatio(retest), breakAtr,
                           StringFormat("anchorBody=%.2f touchedMid=%s reclaimed=%s", V10BodyRatio(anchor), touchedMid ? "yes" : "no", reclaimed ? "yes" : "no"));
      return(false);
     }

   double takeProfit = V10NormalizePrice(ask + (stopDistance * rr));
   if(!V10StopsValid(false, ask, stopLoss, takeProfit))
      return(false);
   double riskUsd = V10BuyRiskBudgetUsd(regime, V10_ZoneRiskMultiplier);
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
   string tags = V10AppendTag("", V10RegimeIsStrong(regime) ? "RG" : "WG");
   tags = V10AppendTag(tags, "ZN");
   tags = V10AppendTag(tags, "RT");
   tags = V10AppendTag(tags, "BM");
   string note = StringFormat("ZONE BUY score=%d breakATR=%.2f anchorBody=%.2f retestBody=%.2f regime=%s hour=%02d rr=%.2f",
                              score, breakAtr, V10BodyRatio(anchor), V10BodyRatio(retest), V10RegimeLabel(regime), currentHour, rr);
   V10FillSignalMeta(signal, "ZB", score, tags, note);
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
     {
      string rejectEngine = pullbackSetup && !breakoutSetup ? "PB" : "BO";
      V11RejectedSignalLog("BUY", rejectEngine, "score below gate", score, regime, currentHour, bodyRatio, breakAtr,
                           StringFormat("core=%s pullbackSeen=%s breakout=%s pullback=%s", inCoreHour ? "yes" : "no", pullbackSeen ? "yes" : "no", breakoutSetup ? "yes" : "no", pullbackSetup ? "yes" : "no"));
      return(false);
     }

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
   string engineCode = pullbackSetup && !breakoutSetup ? "PB" : "BO";
   double takeProfit = V10NormalizePrice(ask + (stopDistance * rr));
   if(!V10StopsValid(false, ask, stopLoss, takeProfit))
      return(false);

   double riskUsd = V10BuyRiskBudgetUsd(regime);
   if(engineCode == "PB")
      riskUsd *= V11_BuyPullbackRiskMultiplier;
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
   if(V11EngineHourBlocked(engineCode, currentHour))
      return(false);
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
   if(!V12_AllowIndependentAddOns && !V10HasQualifiedLeadPosition(sell, V10_AddOnMinProgressR))
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
   if(V11EngineHourBlocked(sell ? "AS" : "AB", currentHour))
      return(false);

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
      if(!V11BearSafePass("AS", regime, 76, currentHour, bodyRatio, 0.0))
        {
         V11RejectedSignalLog("SELL", "AS", "bear safe mode", 76, regime, currentHour, bodyRatio, 0.0,
                              StringFormat("blockWeakAddOns=%s", V11_BearSafeBlockWeakAddOns ? "yes" : "no"));
         return(false);
        }
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
   if(!V12SignalFitsOpenRisk(signal))
     {
      PrintFormat("V12 RISK SKIP %s | engine=%s | lot=%.2f openRisk=%.2f",
                  signal.sell ? "SELL" : "BUY",
                  signal.engineCode,
                  signal.lot,
                  V12OpenRiskUsd());
      return(false);
     }

   g_trade.SetExpertMagicNumber(V10_MAGIC);
   g_trade.SetDeviationInPoints(20);
   g_trade.SetTypeFillingBySymbol(_Symbol);

   PrintFormat("V11 ENTRY %s | engine=%s (%s) | score=%d grade=%s | tags=%s | lot=%.2f rr=%.2f sl=%.2f tp=%.2f | note=%s",
               signal.sell ? "SELL" : "BUY",
               V11EngineLabel(signal.engineCode),
               signal.engineCode,
               signal.score,
               signal.grade,
               V11TagsHuman(signal.tags),
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
   bool canSendTradeRequest = V11TradeSessionLikelyOpen();

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
      int barsHeld = (int)((TimeCurrent() - (datetime)PositionGetInteger(POSITION_TIME)) / PeriodSeconds(V10_EXEC_TF));
      double progressR = favorable / riskDistance;
      if(favorable >= (riskDistance * V10_BreakevenR))
        {
         double desiredSl = (type == POSITION_TYPE_BUY)
                            ? V10NormalizePrice(openPrice + V10_BreakevenLockUsd)
                            : V10NormalizePrice(openPrice - V10_BreakevenLockUsd);
         if(V10StopsValid(type == POSITION_TYPE_SELL, openPrice, desiredSl, takeProfit))
           {
            if(type == POSITION_TYPE_BUY && stopLoss < desiredSl)
              {
               if(canSendTradeRequest && g_trade.PositionModify(ticket, desiredSl, takeProfit))
                  V11ExitActionLog("MOVE_SL_TO_BE", ticket, comment, "progress reached breakeven threshold", barsHeld, progressR, desiredSl, takeProfit);
              }
            if(type == POSITION_TYPE_SELL && stopLoss > desiredSl)
              {
               if(canSendTradeRequest && g_trade.PositionModify(ticket, desiredSl, takeProfit))
                  V11ExitActionLog("MOVE_SL_TO_BE", ticket, comment, "progress reached breakeven threshold", barsHeld, progressR, desiredSl, takeProfit);
              }
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
	               if(canSendTradeRequest && g_trade.PositionClosePartial(ticket, closeVolume))
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
                            {
			                  if(canSendTradeRequest && g_trade.PositionModify(ticket, runnerSl, runnerTp))
                              V11ExitActionLog("TP1_RUNNER_SET", ticket, comment, "partial close done; runner TP/SL adjusted", barsHeld, progressR, runnerSl, runnerTp);
                            }
			               V10SetTPStage(ticket, 1);
			               PrintFormat("V11 TP1 | ticket=%I64u | %s | closedVolume=%.2f runnerRR=%.2f", ticket, comment, closeVolume, runnerRr);
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
                 {
	               if(canSendTradeRequest && g_trade.PositionModify(ticket, desiredSl, takeProfit))
                     V11ExitActionLog("TRAIL_SL", ticket, comment, "ATR trailing after TP1", barsHeld, progressR, desiredSl, takeProfit);
                 }
	           }
	        }

	      bool weakOutsideBaseSell = V10_WeakOutsideSellQuickExit &&
	                                 type == POSITION_TYPE_SELL &&
	                                 StringFind(comment, "|BE|") >= 0 &&
	                                 StringFind(comment, "|WG|") >= 0 &&
	                                 StringFind(comment, "|XH|") >= 0;
	      if(weakOutsideBaseSell &&
	         barsHeld >= V10_WeakOutsideSellExitBars &&
	         PositionGetDouble(POSITION_PROFIT) < 0.0)
	        {
	         if(canSendTradeRequest && g_trade.PositionClose(ticket))
               V11ExitActionLog("WEAK_SELL_QUICK_EXIT", ticket, comment, "weak outside-session sell stayed negative", barsHeld, progressR, stopLoss, takeProfit);
	         continue;
	        }
	      if(V10_FastFailBuyGuard && type == POSITION_TYPE_BUY && barsHeld <= V10_FastFailBars && emaM5 > 0.0)
	        {
         bool scopeOk = !V10_FastFailPullbackOnly || (StringFind(comment, "|PB|") >= 0);
	         progressR = favorable / riskDistance;
         double failBuffer = (atrM5 > 0.0) ? (atrM5 * V10_HoldBufferATR) : 0.0;
         bool lostTrend = currentPrice <= (emaM5 + failBuffer);
	         if(scopeOk && lostTrend && progressR < V10_FastFailMinProgressR && PositionGetDouble(POSITION_PROFIT) < 0.0)
	           {
	            if(canSendTradeRequest && g_trade.PositionClose(ticket))
                  V11ExitActionLog("FAST_FAIL_CLOSE", ticket, comment, "buy lost EMA before progress", barsHeld, progressR, stopLoss, takeProfit);
	            continue;
	           }
        }
      bool regimeFlip = V10_CloseOnRegimeFlip &&
                        ((type == POSITION_TYPE_BUY && !V10RegimeIsBull(regime)) ||
                         (type == POSITION_TYPE_SELL && !V10RegimeIsBear(regime)));
      int maxHoldBars = V10_MaxHoldBars;
      if(type == POSITION_TYPE_BUY && StringFind(comment, "|BC|") >= 0)
         maxHoldBars = V10_BullSubMaxHoldBars;
      if(type == POSITION_TYPE_BUY && StringFind(comment, "|IB|") >= 0)
         maxHoldBars = V11_ImpulseMaxHoldBars;
      if(type == POSITION_TYPE_BUY && StringFind(comment, "|ZB|") >= 0)
         maxHoldBars = V10_ZoneMaxHoldBars;
      if(type == POSITION_TYPE_BUY && StringFind(comment, "|AB|") >= 0)
         maxHoldBars = V10_AddOnMaxHoldBars;
      if(type == POSITION_TYPE_SELL && StringFind(comment, "|SS|") >= 0)
         maxHoldBars = V10_BearSubMaxHoldBars;
      if(type == POSITION_TYPE_SELL && StringFind(comment, "|IS|") >= 0)
         maxHoldBars = V11_ImpulseMaxHoldBars;
      if(type == POSITION_TYPE_SELL && StringFind(comment, "|ZS|") >= 0)
         maxHoldBars = V10_ZoneMaxHoldBars;
      if(type == POSITION_TYPE_SELL && StringFind(comment, "|AS|") >= 0)
         maxHoldBars = V10_AddOnMaxHoldBars;
	      bool timeExpired = barsHeld >= maxHoldBars;
	      bool timeCloseProfitOnly = V11EngineTimeCloseProfitOnly(type, comment);
	      bool canTimeClose = !timeCloseProfitOnly || PositionGetDouble(POSITION_PROFIT) > 0.0;
	      if(regimeFlip || (timeExpired && canTimeClose))
        {
         string closeReason = regimeFlip ? "regime flipped against position" : "max hold bars reached";
         if(canSendTradeRequest && g_trade.PositionClose(ticket))
            V11ExitActionLog(regimeFlip ? "REGIME_FLIP_CLOSE" : "TIME_CLOSE", ticket, comment, closeReason, barsHeld, progressR, stopLoss, takeProfit);
        }
     }
  }


void V12QueueSignal(V10Signal &signals[], int &signalCount, const V10Signal &signal)
  {
   if(!signal.valid)
      return;
   int nextCount = signalCount + 1;
   ArrayResize(signals, nextCount);
   signals[signalCount] = signal;
   signalCount = nextCount;
  }


bool V12SubmitQueuedSignals(V10Signal &signals[], const int signalCount, const V10Regime entryRegime)
  {
   if(signalCount <= 0)
      return(false);

   int submitted = 0;
   int maxSignals = signalCount;
   if(V12_MaxSignalsPerBar > 0)
      maxSignals = MathMin(signalCount, V12_MaxSignalsPerBar);

   for(int i = 0; i < signalCount && submitted < maxSignals; i++)
     {
      if(V10CountOpenPositions() >= V10AllowedMaxPositions(entryRegime))
         break;
      if(V10SubmitSignal(signals[i]))
         submitted++;
     }
   return(submitted > 0);
  }


bool V12HandleBuiltSignal(V10Signal &signals[], int &signalCount, const V10Signal &signal)
  {
   if(!V12_EnableMultiSignalQueue)
      return(V10SubmitSignal(signal));
   V12QueueSignal(signals, signalCount, signal);
   return(false);
  }


bool V10EvaluateEntries()
  {
   V10Regime regime = V10DetectRegime();
   if(regime == V10_REGIME_NONE)
      return(false);
   if(!V10SpreadAllowed())
      return(false);
   if(!V11RiskGuardAllowsTrading(false))
      return(false);
   MqlDateTime nowParts;
   TimeToStruct(TimeCurrent(), nowParts);
   if(V11HourListContains(V12_BlockTradeMonths, nowParts.mon))
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

   V10Signal signals[];
   int signalCount = 0;
   if(V10RegimeIsBear(entryRegime))
     {
      if(V11OppositePositionBlocks(true))
         return(false);
      V10Signal signal;
      if(V10BuildBearSubSignal(rates, emaM5, atr, entryRegime, signal))
        {
         if(V12HandleBuiltSignal(signals, signalCount, signal))
            return(true);
        }
      signal.valid = false;
      if(V11BuildImpulsePullbackSignal(rates, emaM5, atr, entryRegime, true, signal))
        {
         if(V12HandleBuiltSignal(signals, signalCount, signal))
            return(true);
        }
      signal.valid = false;
      if(V10BuildZoneRetestSignal(rates, emaM5, atr, entryRegime, true, signal))
        {
         if(V12HandleBuiltSignal(signals, signalCount, signal))
            return(true);
        }
      signal.valid = false;
      if(V10BuildAddOnSignal(rates, emaM5, atr, entryRegime, true, signal))
        {
         if(V12HandleBuiltSignal(signals, signalCount, signal))
            return(true);
        }
      signal.valid = false;
      if(V10BuildSellSignal(rates, emaM5, atr, entryRegime, signal))
        {
         if(V12HandleBuiltSignal(signals, signalCount, signal))
            return(true);
        }
     }
   else if(V10RegimeIsBull(entryRegime))
     {
      if(V11OppositePositionBlocks(false))
         return(false);
      V10Signal signal;
      if(V10BuildBullSubSignal(rates, emaM5, atr, entryRegime, signal))
        {
         if(V12HandleBuiltSignal(signals, signalCount, signal))
            return(true);
        }
      signal.valid = false;
      if(V11BuildImpulsePullbackSignal(rates, emaM5, atr, entryRegime, false, signal))
        {
         if(V12HandleBuiltSignal(signals, signalCount, signal))
            return(true);
        }
      signal.valid = false;
      if(V10BuildZoneRetestSignal(rates, emaM5, atr, entryRegime, false, signal))
        {
         if(V12HandleBuiltSignal(signals, signalCount, signal))
            return(true);
        }
      signal.valid = false;
      if(V10BuildAddOnSignal(rates, emaM5, atr, entryRegime, false, signal))
        {
         if(V12HandleBuiltSignal(signals, signalCount, signal))
            return(true);
        }
      signal.valid = false;
      if(V10BuildBuySignal(rates, emaM5, atr, entryRegime, signal))
        {
         if(V12HandleBuiltSignal(signals, signalCount, signal))
            return(true);
        }
     }

   if(V12_EnableMultiSignalQueue)
      return(V12SubmitQueuedSignals(signals, signalCount, entryRegime));
   return(false);
  }


int OnInit()
  {
   if(_Period != V10_EXEC_TF)
     {
      Print("Suis_BTC_M5_V2 requires M5.");
      return(INIT_PARAMETERS_INCORRECT);
     }

   V10ClearState();
   V12InitEquityState();
   V11ResetDailyGuardIfNeeded();

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
      Print("Suis_BTC_M5_Base failed to create indicators.");
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
   V11RiskGuardAllowsTrading(true);
   V10ManagePositions();
   if(!V10NewBar())
      return;
   bool entered = V10EvaluateEntries();
   V11StatusLog(entered);
  }


void OnTradeTransaction(const MqlTradeTransaction &trans,
                        const MqlTradeRequest &request,
                        const MqlTradeResult &result)
  {
   if(V11_MaxConsecutiveLosses <= 0 || V11_LossCooldownMinutes <= 0)
      return;
   if(trans.type != TRADE_TRANSACTION_DEAL_ADD)
      return;
   if(!HistoryDealSelect(trans.deal))
      return;
   if(HistoryDealGetString(trans.deal, DEAL_SYMBOL) != _Symbol)
      return;
   if((ulong)HistoryDealGetInteger(trans.deal, DEAL_MAGIC) != V10_MAGIC)
      return;

   long entry = HistoryDealGetInteger(trans.deal, DEAL_ENTRY);
   if(entry != DEAL_ENTRY_OUT && entry != DEAL_ENTRY_OUT_BY && entry != DEAL_ENTRY_INOUT)
      return;

   double pnl = HistoryDealGetDouble(trans.deal, DEAL_PROFIT) +
                HistoryDealGetDouble(trans.deal, DEAL_SWAP) +
                HistoryDealGetDouble(trans.deal, DEAL_COMMISSION);
   if(pnl < -0.01)
      g_consecutiveLosses++;
   else if(pnl > 0.01)
      g_consecutiveLosses = 0;

   if(g_consecutiveLosses >= V11_MaxConsecutiveLosses)
     {
      g_lossCooldownUntil = TimeCurrent() + (V11_LossCooldownMinutes * 60);
      V11RiskGuardLog(StringFormat("loss streak cooldown start losses=%d pnl=%.2f", g_consecutiveLosses, pnl), true);
      g_consecutiveLosses = 0;
     }
  }
