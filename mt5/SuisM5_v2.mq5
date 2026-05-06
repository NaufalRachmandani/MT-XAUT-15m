#property copyright "OpenAI Codex"
#property version   "4.01"
#property strict
// Variant: Suis M5 aggressive frequency profile

#include <Trade/Trade.mqh>

const double SUIS_RiskPercent = 30.00;
const double SUIS_BuyRiskMultiplier = 0.30;
const double SUIS_SellRiskMultiplier = 0.16;
const double SUIS_WeakBuyRiskMultiplier = 0.10;
const double SUIS_WeakSellRiskMultiplier = 0.08;
const bool   SUIS_EnableBuys = true;
const bool   SUIS_EnableSells = true;
const int    SUIS_MaxPositions = 8;
const int    SUIS_WeakRegimeMaxPositions = 3;
const int    SUIS_SellSessionStartHour = 0;
const int    SUIS_SellSessionEndHour = 23;
const int    SUIS_BuySessionStartHour = 0;
const int    SUIS_BuySessionEndHour = 23;
const bool   SUIS_StrongBullRelaxBuySession = false;
const bool   SUIS_EnableMixedMomentumEntries = false;
const bool   SUIS_BlockOppositeDirection = true;
const long   SUIS_OppositeMagic = 2026042412;
const double SUIS_MaxSpreadUsd = 1.20;
const bool   SUIS_EnableDailyGuard = true;
const double SUIS_DailyMaxLossPct = 30.00;
const double SUIS_DailyProfitStopPct = 0.00;
const double SUIS_DailyProfitLockStartPct = 0.00;
const double SUIS_DailyMaxGivebackPct = 0.00;
const bool   SUIS_DailyClosePositionsOnStop = true;
const int    SUIS_MaxConsecutiveLosses = 3;
const int    SUIS_LossCooldownMinutes = 180;
const bool   SUIS_DailyGuardLog = true;
const bool   SUIS_EnableWeeklyGuard = true;
const double SUIS_WeeklyMaxLossPct = 95.00;
const double SUIS_WeeklyProfitLockStartPct = 1000.00;
const double SUIS_WeeklyMaxGivebackPct = 400.00;
const bool   SUIS_EnableEquityCircuitBreaker = true;
const double SUIS_MaxEquityDrawdownPct = 95.00;
const bool   SUIS_ClosePositionsOnSafetyStop = false;
const bool   SUIS_EnableEngineFailGuard = false;
const int    SUIS_EngineFailMinScore = 85;
const int    SUIS_BuyZoneDailyLossLimit = 2;
const int    SUIS_BuyPullbackDailyLossLimit = 2;
const bool   SUIS_EnableOverextensionGuard = true;
const int    SUIS_D1ATRPeriod = 14;
const double SUIS_MaxBuyD1FastDistanceATR = 2.60;
const double SUIS_MaxBuyH1FastDistanceATR = 0.00;
const bool   SUIS_OverextensionGuardBlocksZone = false;
const bool   SUIS_OverextensionGuardBlocksPullback = false;
const bool   SUIS_OverextensionGuardBlocksBreak = false;

const int    SUIS_H1FastEMA = 20;
const int    SUIS_H1SlowEMA = 50;
const int    SUIS_H4FastEMA = 20;
const int    SUIS_H4SlowEMA = 50;
const int    SUIS_H1ADXPeriod = 14;
const int    SUIS_H1ATRPeriod = 14;
const double SUIS_H1ADXMin = 20.0;
const double SUIS_H1ADXStrongMin = 26.0;
const double SUIS_StrongGapATR = 0.10;
const int    SUIS_M5TrendEMA = 20;
const int    SUIS_M5ATRPeriod = 14;

const int    SUIS_BreakoutLookback = 12;
const int    SUIS_PullbackLookback = 6;
const bool   SUIS_RequirePullback = false;
const bool   SUIS_AllowBreakoutBuys = true;
const bool   SUIS_AllowPullbackBuys = true;
const bool   SUIS_UseBuyCoreHours = false;
const bool   SUIS_EnableBullSubEngine = false;
const bool   SUIS_BullSubAllowWeakBull = false;
const int    SUIS_BullSubSessionStartHour = 0;
const int    SUIS_BullSubSessionEndHour = 23;
const bool   SUIS_BullSubOnlyOutsideCore = true;
const int    SUIS_BullSubCompressionBars = 6;
const double SUIS_BullSubMaxRangeATR = 1.60;
const double SUIS_BullSubTouchEmaATR = 0.18;
const double SUIS_BullSubBreakATR = 0.04;
const double SUIS_BullSubMinBodyRatio = 0.58;
const double SUIS_BullSubRiskMultiplier = 0.28;
const double SUIS_BullSubRR = 1.85;
const int    SUIS_BullSubMaxHoldBars = 24;
const bool   SUIS_EnableBearSubEngine = true;
const bool   SUIS_BearSubAllowWeakBear = true;
const int    SUIS_BearSubSessionStartHour = 0;
const int    SUIS_BearSubSessionEndHour = 23;
const int    SUIS_BearSubCompressionBars = 6;
const double SUIS_BearSubMaxRangeATR = 1.60;
const double SUIS_BearSubTouchEmaATR = 0.18;
const double SUIS_BearSubBreakATR = 0.04;
const double SUIS_BearSubMinBodyRatio = 0.58;
const double SUIS_BearSubRiskMultiplier = 0.16;
const double SUIS_BearSubRR = 1.20;
const int    SUIS_BearSubMaxHoldBars = 24;
const bool   SUIS_EnableBearSafeMode = true;
const int    SUIS_BearSafeStrongMinScore = 72;
const int    SUIS_BearSafeWeakMinScore = 82;
const double SUIS_BearSafeWeakMinBodyRatio = 0.58;
const bool   SUIS_BearSafeBlockWeakZone = false;
const bool   SUIS_BearSafeBlockWeakAddOns = true;
const bool   SUIS_EnableImpulsePullbackEngine = true;
const bool   SUIS_EnableBuyImpulsePullback = false;
const bool   SUIS_EnableSellImpulsePullback = true;
const bool   SUIS_ImpulseAllowWeakRegime = true;
const int    SUIS_ImpulseSessionStartHour = 0;
const int    SUIS_ImpulseSessionEndHour = 23;
const double SUIS_ImpulseMinBodyRatio = 0.52;
const double SUIS_ImpulseMinMoveATR = 0.65;
const double SUIS_ImpulsePullbackMaxATR = 0.80;
const double SUIS_ImpulseEntryBodyRatio = 0.38;
const double SUIS_ImpulseBreakATR = 0.00;
const double SUIS_ImpulseRiskMultiplier = 0.16;
const double SUIS_ImpulseRR = 1.10;
const int    SUIS_ImpulseMaxHoldBars = 10;
const bool   SUIS_EnableZoneRetestEngine = true;
const bool   SUIS_ZoneAllowWeakRegime = false;
const bool   SUIS_ZoneUseCoreHours = false;
const int    SUIS_ZoneLookback = 8;
const double SUIS_ZoneMinBodyRatio = 0.46;
const double SUIS_ZoneBreakATR = 0.02;
const double SUIS_ZoneMidTouchATR = 0.10;
const double SUIS_ZoneReclaimATR = 0.00;
const double SUIS_ZoneOvershootATR = 0.35;
const double SUIS_ZoneRiskMultiplier = 0.35;
const double SUIS_ZoneRR = 1.20;
const int    SUIS_ZoneMaxHoldBars = 12;
const bool   SUIS_StrongBullRelaxCoreHours = false;
const bool   SUIS_StrongBullPullbackOnlyOutsideCore = true;
const bool   SUIS_BlockBuyHour07 = false;
const bool   SUIS_BlockBuyHour10 = false;
const bool   SUIS_BlockBuyHour14 = false;
const bool   SUIS_BlockBuyHour17 = false;
const string SUIS_BlockBuyBreakHours = "1,2,4,5,7,10,20";
const string SUIS_BlockBuyPullbackHours = "1,2,3,5,7,8,9,10,12,14,16,17,18";
const string SUIS_BlockBuyZoneHours = "7,10,13,15,20";
const string SUIS_BlockBuyImpulseHours = "";
const string SUIS_BlockBuySubHours = "";
const string SUIS_BlockBuyAddOnHours = "9,16";
const string SUIS_BlockSellBreakHours = "5,6,14,16,19,20";
const string SUIS_BlockSellZoneHours = "0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23";
const string SUIS_BlockSellImpulseHours = "";
const string SUIS_BlockSellSubHours = "";
const string SUIS_BlockSellAddOnHours = "";
const int    SUIS_BullPullbackLookback = 8;
const double SUIS_BullTouchATR = 0.15;
const double SUIS_BullReclaimATR = 0.00;
const double SUIS_BullMaxStretchATR = 1.10;
const int    SUIS_BearRejectLookback = 6;
const double SUIS_BearTouchATR = 0.12;
const double SUIS_BearBreakBelowPrevATR = 0.02;
const double SUIS_BearMaxStretchATR = 1.30;
const double SUIS_MinBreakATR = 0.05;
const double SUIS_BuyMinBreakATR = 0.08;
const double SUIS_WeakSellMinBreakATR = 0.08;
const double SUIS_WeakBuyMinBreakATR = 0.12;
const double SUIS_MinBodyRatio = 0.48;
const double SUIS_BuyMinBodyRatio = 0.50;
const double SUIS_WeakSellMinBodyRatio = 0.50;
const double SUIS_WeakBuyMinBodyRatio = 0.56;
const double SUIS_MaxStretchATR = 1.50;
const int    SUIS_ChopLookbackBars = 10;
const int    SUIS_MaxEmaFlips = 3;
const int    SUIS_HoldBars = 2;
const double SUIS_HoldBufferATR = 0.05;

const int    SUIS_StopLookbackBars = 10;
const double SUIS_StopBufferATR = 0.25;
const double SUIS_MinSLUsd = 3.00;
const double SUIS_MaxSLUsd = 10.00;
const double SUIS_SellRR = 1.30;
const double SUIS_BuyRR = 1.55;
const double SUIS_WeakSellRR = 1.10;
const double SUIS_WeakBuyRR = 1.30;

const int    SUIS_MaxHoldBars = 24;
const double SUIS_BreakevenR = 0.80;
const double SUIS_BreakevenLockUsd = 0.20;
const bool   SUIS_FastFailBuyGuard = false;
const bool   SUIS_FastFailPullbackOnly = true;
const int    SUIS_FastFailBars = 6;
const double SUIS_FastFailMinProgressR = 0.10;
const bool   SUIS_WeakOutsideSellQuickExit = true;
const int    SUIS_WeakOutsideSellExitBars = 6;
const bool   SUIS_CloseOnRegimeFlip = true;
const bool   SUIS_TimeCloseProfitOnly = false;
const int    SUIS_ScoreGradeAMin = 85;
const int    SUIS_ScoreGradeBMin = 72;
const int    SUIS_MinTradeScore = 68;
const int    SUIS_ScoreBoostMin = 85;
const double SUIS_ScoreRRBonus = 0.35;
const double SUIS_ScoreRiskBonus = 1.25;
const bool   SUIS_EnableTPManager = false;
const bool   SUIS_LogExitActions = true;
const bool   SUIS_LogRejectedSignals = false;
const int    SUIS_MinRejectedScoreToLog = 55;
const bool   SUIS_LogStatusOnNewBar = false;
const int    SUIS_StatusEveryBars = 12;
const bool   SUIS_EnableTelemetryLogs = true;
const bool   SUIS_EnableMacroRegimeSwitch = true;
const int    SUIS_D1FastEMA = 20;
const int    SUIS_D1SlowEMA = 50;
const int    SUIS_D1SlopeBars = 3;
const bool   SUIS_EnableStructuralPriceGate = true;
const double SUIS_MinD1CloseForTrading = 2500.00;
const bool   SUIS_AllowBuyInMacroBull = true;
const bool   SUIS_AllowBuyInMacroSideways = false;
const bool   SUIS_AllowStrongBullBuyInMacroSideways = true;
const int    SUIS_MacroSidewaysMinScore = 82;
const bool   SUIS_AllowBuyInMacroBear = true;
const int    SUIS_MacroBearMinScore = 97;
const bool   SUIS_BlockAddOnOutsideMacroBull = true;
const double SUIS_TP1R = 1.15;
const double SUIS_TP1CloseFraction = 0.50;
const double SUIS_RunnerRR = 2.40;
const double SUIS_TrailStartR = 1.50;
const double SUIS_TrailATR = 1.20;
const double SUIS_TrailLockUsd = 0.40;
const bool   SUIS_EnableAddOnEngine = true;
const bool   SUIS_EnableBuyAddOns = false;
const bool   SUIS_EnableSellAddOns = true;
const bool   SUIS_AddOnAllowWeakRegime = true;
const int    SUIS_AddOnMaxPerSide = 2;
const double SUIS_AddOnMinProgressR = 0.30;
const double SUIS_AddOnBreakATR = 0.02;
const double SUIS_AddOnMinBodyRatio = 0.58;
const double SUIS_AddOnRiskMultiplier = 0.16;
const double SUIS_AddOnRR = 1.05;
const int    SUIS_AddOnMaxHoldBars = 8;
const bool   SUIS_BuyBreakTimeCloseProfitOnly = false;
const bool   SUIS_BuyImpulseTimeCloseProfitOnly = false;
const bool   SUIS_BuyZoneTimeCloseProfitOnly = false;
const bool   SUIS_BuyCompTimeCloseProfitOnly = false;
const bool   SUIS_BuyAddOnTimeCloseProfitOnly = false;
const bool   SUIS_SellBreakTimeCloseProfitOnly = true;
const bool   SUIS_SellImpulseTimeCloseProfitOnly = true;
const bool   SUIS_SellZoneTimeCloseProfitOnly = true;
const bool   SUIS_SellCompTimeCloseProfitOnly = true;
const bool   SUIS_SellAddOnTimeCloseProfitOnly = true;

enum SUISRegime
  {
   SUIS_REGIME_NONE = 0,
   SUIS_REGIME_WEAK_BULL = 1,
   SUIS_REGIME_STRONG_BULL = 2,
   SUIS_REGIME_WEAK_BEAR = -1,
   SUIS_REGIME_STRONG_BEAR = -2,
   SUIS_REGIME_MIXED = 9
  };

enum SUISMacroRegime
  {
   SUIS_MACRO_UNKNOWN = 0,
   SUIS_MACRO_BULL = 1,
   SUIS_MACRO_SIDEWAYS = 2,
   SUIS_MACRO_BEAR = 3
  };

struct SUISSignal
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
int               g_emaFastD1 = INVALID_HANDLE;
int               g_emaSlowD1 = INVALID_HANDLE;
int               g_atrD1 = INVALID_HANDLE;
int               g_emaM5 = INVALID_HANDLE;
int               g_atrM5 = INVALID_HANDLE;
datetime          g_lastBarTime = 0;
int               g_statusBarCounter = 0;
int               g_dailyGuardDay = -1;
double            g_dailyStartEquity = 0.0;
double            g_dailyHighEquity = 0.0;
bool              g_dailyStopped = false;
int               g_weekGuardKey = -1;
double            g_weeklyStartEquity = 0.0;
double            g_weeklyHighEquity = 0.0;
bool              g_weeklyStopped = false;
double            g_accountStartEquity = 0.0;
double            g_accountHighEquity = 0.0;
bool              g_equityCircuitStopped = false;
int               g_dailyBuyZoneHighScoreLosses = 0;
int               g_dailyBuyPullbackHighScoreLosses = 0;
bool              g_dailyBuyZoneStopped = false;
bool              g_dailyBuyPullbackStopped = false;
int               g_consecutiveLosses = 0;
datetime          g_lossCooldownUntil = 0;
datetime          g_lastRiskGuardLogTime = 0;
string            g_lastRiskGuardLogReason = "";
static const ulong SUIS_MAGIC = 2026050613;
static const ENUM_TIMEFRAMES SUIS_EXEC_TF = PERIOD_M5;


double SUISNormalizePrice(const double price)
  {
   return(NormalizeDouble(price, (int)SymbolInfoInteger(_Symbol, SYMBOL_DIGITS)));
  }


bool SUISNewBar()
  {
   datetime times[];
   if(CopyTime(_Symbol, SUIS_EXEC_TF, 0, 1, times) != 1)
      return(false);
   if(times[0] == g_lastBarTime)
      return(false);
   g_lastBarTime = times[0];
   return(true);
  }


int SUISHourOf(const datetime ts)
  {
   MqlDateTime dt;
   TimeToStruct(ts, dt);
   return(dt.hour);
  }


bool SUISHourInSession(const int hour, const int startHour, const int endHour)
  {
   if(startHour == endHour)
      return(true);
   if(startHour < endHour)
      return(hour >= startHour && hour < endHour);
  return(hour >= startHour || hour < endHour);
  }


string SUISRegimeLabel(const SUISRegime regime)
  {
   switch(regime)
     {
      case SUIS_REGIME_STRONG_BULL:
         return("SBULL");
      case SUIS_REGIME_WEAK_BULL:
         return("WBULL");
      case SUIS_REGIME_STRONG_BEAR:
         return("SBEAR");
      case SUIS_REGIME_WEAK_BEAR:
         return("WBEAR");
      case SUIS_REGIME_MIXED:
         return("MIXED");
     }
   return("NONE");
  }


string SUISMacroRegimeLabel(const SUISMacroRegime regime)
  {
   switch(regime)
     {
      case SUIS_MACRO_BULL:
         return("D1_BULL");
      case SUIS_MACRO_SIDEWAYS:
         return("D1_SIDEWAYS");
      case SUIS_MACRO_BEAR:
         return("D1_BEAR");
     }
   return("D1_UNKNOWN");
  }


int SUISClampScore(const int score)
  {
   return((int)MathMax(0, MathMin(99, score)));
  }


string SUISGradeForScore(const int score)
  {
   if(score >= SUIS_ScoreGradeAMin)
      return("A");
   if(score >= SUIS_ScoreGradeBMin)
      return("B");
   return("R");
  }


string SUISEngineLabel(const string engineCode)
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
   if(engineCode == "SB")
      return("Bull Compression Breakout");
   if(engineCode == "SS")
      return("Bear Compression Breakdown");
   if(engineCode == "AB")
      return("Buy Add-on Continuation");
   if(engineCode == "AS")
      return("Sell Add-on Continuation");
   return(engineCode);
  }


string SUISEngineComment(const string engineCode)
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
   if(engineCode == "SB")
      return("BUY_COMP");
   if(engineCode == "SS")
      return("SELL_COMP");
   if(engineCode == "AB")
      return("BUY_ADDON");
   if(engineCode == "AS")
      return("SELL_ADDON");
   return(engineCode);
  }


string SUISTagLabel(const string tag)
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


string SUISTagsHuman(const string tags)
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
      human += SUISTagLabel(parts[i]);
     }
   return(human);
  }


void SUISRejectedSignalLog(const string direction,
                          const string engineCode,
                          const string reason,
                          const int score,
                          const SUISRegime regime,
                          const int hour,
                          const double bodyRatio,
                          const double breakAtr,
                          const string note)
  {
   if(!SUIS_LogRejectedSignals || score < SUIS_MinRejectedScoreToLog)
      return;
   PrintFormat("SUIS REJECT %s | engine=%s (%s) | reason=%s | score=%d min=%d | regime=%s | hour=%02d | body=%.2f breakATR=%.2f | note=%s",
               direction,
               SUISEngineLabel(engineCode),
               engineCode,
               reason,
               score,
               SUIS_MinTradeScore,
               SUISRegimeLabel(regime),
               hour,
               bodyRatio,
               breakAtr,
               note);
  }


void SUISExitActionLog(const string action,
                      const ulong ticket,
                      const string comment,
                      const string reason,
                      const int barsHeld,
                      const double progressR,
                      const double stopLoss,
                      const double takeProfit)
  {
   if(!SUIS_LogExitActions)
      return;
   PrintFormat("SUIS EXIT %s | ticket=%I64u | %s | reason=%s | bars=%d progressR=%.2f | sl=%.2f tp=%.2f",
               action,
               ticket,
               comment,
               reason,
               barsHeld,
               progressR,
               stopLoss,
               takeProfit);
  }


bool SUISBearSafePass(const string engineCode,
                     const SUISRegime regime,
                     const int score,
                     const int hour,
                     const double bodyRatio,
                     const double breakAtr)
  {
   if(!SUIS_EnableBearSafeMode)
      return(true);
   if(!SUISRegimeIsBear(regime))
      return(true);

   bool strongBear = regime == SUIS_REGIME_STRONG_BEAR;
   if(strongBear)
      return(score >= SUIS_BearSafeStrongMinScore);

   if(score < SUIS_BearSafeWeakMinScore)
      return(false);
   if(bodyRatio < SUIS_BearSafeWeakMinBodyRatio)
      return(false);
   if(SUIS_BearSafeBlockWeakZone && engineCode == "ZS")
      return(false);
   if(SUIS_BearSafeBlockWeakAddOns && engineCode == "AS")
      return(false);
   return(true);
  }


bool SUISEngineTimeCloseProfitOnly(const ENUM_POSITION_TYPE type, const string comment)
  {
   if(type == POSITION_TYPE_BUY)
     {
      if(StringFind(comment, "|ZB|") >= 0)
         return(SUIS_BuyZoneTimeCloseProfitOnly);
      if(StringFind(comment, "|IB|") >= 0)
         return(SUIS_BuyImpulseTimeCloseProfitOnly);
      if(StringFind(comment, "|SB|") >= 0)
         return(SUIS_BuyCompTimeCloseProfitOnly);
      if(StringFind(comment, "|AB|") >= 0)
         return(SUIS_BuyAddOnTimeCloseProfitOnly);
      return(SUIS_BuyBreakTimeCloseProfitOnly);
     }

   if(StringFind(comment, "|ZS|") >= 0)
      return(SUIS_SellZoneTimeCloseProfitOnly);
   if(StringFind(comment, "|IS|") >= 0)
      return(SUIS_SellImpulseTimeCloseProfitOnly);
   if(StringFind(comment, "|SS|") >= 0)
      return(SUIS_SellCompTimeCloseProfitOnly);
   if(StringFind(comment, "|AS|") >= 0)
      return(SUIS_SellAddOnTimeCloseProfitOnly);
   return(SUIS_SellBreakTimeCloseProfitOnly);
  }


void SUISStatusLog(const bool entered)
  {
   if(!SUIS_LogStatusOnNewBar)
      return;
   g_statusBarCounter++;
   if(SUIS_StatusEveryBars > 1 && (g_statusBarCounter % SUIS_StatusEveryBars) != 0)
      return;

   double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   double spread = (ask > 0.0 && bid > 0.0) ? (ask - bid) : 0.0;
   SUISRegime regime = SUISDetectRegime();
   SUISMacroRegime macroRegime = SUISDetectMacroRegime();
   PrintFormat("SUIS STATUS | symbol=%s tf=M5 | regime=%s macro=%s | open=%d buy=%d sell=%d | spread=%.2f | equity=%.2f | entered=%s | rejectLog=%s telemetry=%s",
               _Symbol,
               SUISRegimeLabel(regime),
               SUISMacroRegimeLabel(macroRegime),
               SUISCountOpenPositions(),
               SUISCountOpenPositionsByType(false),
               SUISCountOpenPositionsByType(true),
               spread,
               AccountInfoDouble(ACCOUNT_EQUITY),
               entered ? "yes" : "no",
               SUIS_LogRejectedSignals ? "on" : "off",
               SUIS_EnableTelemetryLogs ? "on" : "off");
  }


string SUISAppendTag(const string tags, const string tag)
  {
   if(tag == "")
      return(tags);
   if(tags == "")
      return(tag);
   return(tags + "|" + tag);
  }


string SUISBuildComment(const string engineCode, const int score, const string grade, const string tags)
  {
   string comment = "SV2|" + SUISEngineComment(engineCode) + "|" + engineCode + "|S" + IntegerToString(score) + "|" + grade;
   if(tags != "")
      comment += "|" + tags;
   if(StringLen(comment) > 31)
      comment = StringSubstr(comment, 0, 31);
   return(comment);
  }


void SUISFillSignalMeta(SUISSignal &signal,
                       const string engineCode,
                       const int score,
                       const string tags,
                       const string note)
  {
   signal.score = SUISClampScore(score);
   signal.grade = SUISGradeForScore(signal.score);
   signal.engineCode = engineCode;
   signal.tags = tags;
   signal.note = note;
   signal.comment = SUISBuildComment(engineCode, signal.score, signal.grade, tags);
  }


string SUISStatePrefix()
  {
   return("InvSUIS.");
  }


string SUISStateKey(const ulong ticket, const string suffix)
  {
   return(SUISStatePrefix() + StringFormat("%I64u", ticket) + "." + suffix);
  }


double SUISStateGet(const ulong ticket, const string suffix, const double fallback)
  {
   string key = SUISStateKey(ticket, suffix);
   if(GlobalVariableCheck(key))
      return(GlobalVariableGet(key));
   return(fallback);
  }


void SUISStateSet(const ulong ticket, const string suffix, const double value)
  {
   GlobalVariableSet(SUISStateKey(ticket, suffix), value);
  }


void SUISClearState()
  {
   string prefix = SUISStatePrefix();
   for(int i = GlobalVariablesTotal() - 1; i >= 0; i--)
     {
      string name = GlobalVariableName(i);
      if(StringFind(name, prefix) == 0)
         GlobalVariableDel(name);
     }
  }


int SUISVolumePrecision()
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


double SUISFloorVolume(const double rawVolume)
  {
   double step = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);
   double maxLot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX);
   if(step <= 0.0 || rawVolume <= 0.0)
      return(0.0);
   double clipped = MathMin(maxLot, rawVolume);
   double steps = MathFloor((clipped / step) + 1e-9);
   return(NormalizeDouble(steps * step, SUISVolumePrecision()));
  }


double SUISInitialVolume(const ulong ticket, const double currentVolume)
  {
   double stored = SUISStateGet(ticket, "initvol", 0.0);
   if(stored > 0.0)
      return(stored);
   SUISStateSet(ticket, "initvol", currentVolume);
   return(currentVolume);
  }


int SUISTPStage(const ulong ticket)
  {
   return((int)SUISStateGet(ticket, "tpstage", 0.0));
  }


void SUISSetTPStage(const ulong ticket, const int stage)
  {
   SUISStateSet(ticket, "tpstage", (double)stage);
  }


bool SUISStopFitsMarket(const ENUM_POSITION_TYPE type, const double currentPrice, const double stopLoss)
  {
   double minDistance = SUISMinStopDistance();
   if(type == POSITION_TYPE_BUY)
      return(stopLoss < (currentPrice - minDistance));
   return(stopLoss > (currentPrice + minDistance));
  }


bool SUISTakeProfitFitsMarket(const ENUM_POSITION_TYPE type, const double currentPrice, const double takeProfit)
  {
   if(takeProfit <= 0.0)
      return(true);
   double minDistance = SUISMinStopDistance();
   if(type == POSITION_TYPE_BUY)
      return(takeProfit > (currentPrice + minDistance));
   return(takeProfit < (currentPrice - minDistance));
  }


double SUISPartialCloseVolume(const double initialVolume, const double currentVolume)
  {
   double minLot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
   double targetClose = SUISFloorVolume(initialVolume * SUIS_TP1CloseFraction);
   if(targetClose < minLot)
      return(0.0);
   double remaining = SUISFloorVolume(currentVolume - targetClose);
   if(remaining < minLot)
     {
      double maxClose = SUISFloorVolume(currentVolume - minLot);
      if(maxClose < minLot)
         return(0.0);
      return(maxClose);
     }
   return(targetClose);
  }


bool SUISBuyHourBlocked(const int hour)
  {
   if(SUIS_BlockBuyHour07 && hour == 7)
      return(true);
   if(SUIS_BlockBuyHour10 && hour == 10)
      return(true);
   if(SUIS_BlockBuyHour14 && hour == 14)
      return(true);
   if(SUIS_BlockBuyHour17 && hour == 17)
      return(true);
   return(false);
  }


bool SUISHourListContains(string hours, const int hour)
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


bool SUISEngineHourBlocked(const string engineCode, const int hour)
  {
   if(engineCode == "BO")
      return(SUISHourListContains(SUIS_BlockBuyBreakHours, hour));
   if(engineCode == "PB")
      return(SUISHourListContains(SUIS_BlockBuyPullbackHours, hour));
   if(engineCode == "ZB")
      return(SUISHourListContains(SUIS_BlockBuyZoneHours, hour));
   if(engineCode == "IB")
      return(SUISHourListContains(SUIS_BlockBuyImpulseHours, hour));
   if(engineCode == "SB")
      return(SUISHourListContains(SUIS_BlockBuySubHours, hour));
   if(engineCode == "AB")
      return(SUISHourListContains(SUIS_BlockBuyAddOnHours, hour));
   if(engineCode == "BE")
      return(SUISHourListContains(SUIS_BlockSellBreakHours, hour));
   if(engineCode == "ZS")
      return(SUISHourListContains(SUIS_BlockSellZoneHours, hour));
   if(engineCode == "IS")
      return(SUISHourListContains(SUIS_BlockSellImpulseHours, hour));
   if(engineCode == "SS")
      return(SUISHourListContains(SUIS_BlockSellSubHours, hour));
   if(engineCode == "AS")
      return(SUISHourListContains(SUIS_BlockSellAddOnHours, hour));
   return(false);
  }


bool SUISBuyHourPreferred(const int hour)
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


bool SUISSpreadAllowed()
  {
   double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   if(ask <= 0.0 || bid <= 0.0)
      return(false);
   return((ask - bid) <= SUIS_MaxSpreadUsd);
  }


bool SUISTradeSessionLikelyOpen()
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


int SUISDayKey(const datetime ts)
  {
   MqlDateTime dt;
   TimeToStruct(ts, dt);
   return((dt.year * 1000) + dt.day_of_year);
  }


int SUISWeekKey(const datetime ts)
  {
   MqlDateTime dt;
   TimeToStruct(ts, dt);
   int weekBucket = (dt.day_of_year - 1) / 7;
   return((dt.year * 100) + weekBucket);
  }


void SUISRiskGuardLog(const string reason, const bool force = false)
  {
   if(!SUIS_DailyGuardLog)
      return;
   datetime now = TimeCurrent();
   if(!force && reason == g_lastRiskGuardLogReason && (now - g_lastRiskGuardLogTime) < 3600)
      return;
   g_lastRiskGuardLogReason = reason;
   g_lastRiskGuardLogTime = now;
   PrintFormat("SUIS RISK GUARD | %s | dayStart=%.2f dayHigh=%.2f weekStart=%.2f weekHigh=%.2f accountHigh=%.2f equity=%.2f consecutiveLosses=%d cooldownUntil=%s",
               reason,
               g_dailyStartEquity,
               g_dailyHighEquity,
               g_weeklyStartEquity,
               g_weeklyHighEquity,
               g_accountHighEquity,
               AccountInfoDouble(ACCOUNT_EQUITY),
               g_consecutiveLosses,
               TimeToString(g_lossCooldownUntil, TIME_DATE | TIME_MINUTES));
  }


void SUISResetDailyGuardIfNeeded()
  {
   int dayKey = SUISDayKey(TimeCurrent());
   if(dayKey == g_dailyGuardDay)
      return;
   g_dailyGuardDay = dayKey;
   g_dailyStartEquity = AccountInfoDouble(ACCOUNT_EQUITY);
   g_dailyHighEquity = g_dailyStartEquity;
   g_dailyStopped = false;
   g_dailyBuyZoneHighScoreLosses = 0;
   g_dailyBuyPullbackHighScoreLosses = 0;
   g_dailyBuyZoneStopped = false;
   g_dailyBuyPullbackStopped = false;
   g_consecutiveLosses = 0;
   g_lossCooldownUntil = 0;
   SUISRiskGuardLog("new trading day reset", true);
  }


void SUISResetWeeklyGuardIfNeeded()
  {
   int weekKey = SUISWeekKey(TimeCurrent());
   if(weekKey == g_weekGuardKey)
      return;
   g_weekGuardKey = weekKey;
   g_weeklyStartEquity = AccountInfoDouble(ACCOUNT_EQUITY);
   g_weeklyHighEquity = g_weeklyStartEquity;
   g_weeklyStopped = false;
   SUISRiskGuardLog("new trading week reset", true);
  }


void SUISCloseOwnPositions(const string reason)
  {
   if(!SUISTradeSessionLikelyOpen())
      return;

   g_trade.SetExpertMagicNumber(SUIS_MAGIC);
   g_trade.SetDeviationInPoints(20);
   g_trade.SetTypeFillingBySymbol(_Symbol);

   for(int i = PositionsTotal() - 1; i >= 0; i--)
     {
      ulong ticket = PositionGetTicket(i);
      if(ticket == 0 || !PositionSelectByTicket(ticket))
         continue;
      if(PositionGetString(POSITION_SYMBOL) != _Symbol)
         continue;
      if((ulong)PositionGetInteger(POSITION_MAGIC) != SUIS_MAGIC)
         continue;

      string comment = PositionGetString(POSITION_COMMENT);
      double stopLoss = PositionGetDouble(POSITION_SL);
      double takeProfit = PositionGetDouble(POSITION_TP);
      if(g_trade.PositionClose(ticket))
         SUISExitActionLog("RISK_GUARD_CLOSE", ticket, comment, reason, 0, 0.0, stopLoss, takeProfit);
     }
  }


bool SUISRiskGuardAllowsTrading(const bool allowClose)
  {
   if(!SUIS_EnableDailyGuard &&
      !SUIS_EnableWeeklyGuard &&
      !SUIS_EnableEquityCircuitBreaker &&
      (SUIS_MaxConsecutiveLosses <= 0 || SUIS_LossCooldownMinutes <= 0))
      return(true);

   SUISResetDailyGuardIfNeeded();
   SUISResetWeeklyGuardIfNeeded();
   datetime now = TimeCurrent();
   bool blocked = false;
   string reason = "";
   double equity = AccountInfoDouble(ACCOUNT_EQUITY);

   if(g_accountStartEquity <= 0.0)
      g_accountStartEquity = equity;
   if(g_accountHighEquity <= 0.0)
      g_accountHighEquity = equity;
   g_accountHighEquity = MathMax(g_accountHighEquity, equity);

   if(SUIS_EnableEquityCircuitBreaker && !g_equityCircuitStopped && g_accountHighEquity > 0.0)
     {
      double accountDdPct = (g_accountHighEquity - equity) / g_accountHighEquity * 100.0;
      if(SUIS_MaxEquityDrawdownPct > 0.0 && accountDdPct >= SUIS_MaxEquityDrawdownPct)
        {
         g_equityCircuitStopped = true;
         reason = StringFormat("equity circuit breaker hit dd %.2f%% >= %.2f%%", accountDdPct, SUIS_MaxEquityDrawdownPct);
         SUISRiskGuardLog(reason, true);
         if(allowClose && SUIS_ClosePositionsOnSafetyStop)
            SUISCloseOwnPositions(reason);
        }
     }

   if(g_equityCircuitStopped)
     {
      blocked = true;
      reason = "equity circuit breaker stopped trading";
     }

   if(SUIS_EnableDailyGuard)
     {
      if(g_dailyStartEquity <= 0.0)
         g_dailyStartEquity = equity;
      g_dailyHighEquity = MathMax(g_dailyHighEquity, equity);

      double dayPct = (g_dailyStartEquity > 0.0) ? ((equity - g_dailyStartEquity) / g_dailyStartEquity * 100.0) : 0.0;
      double highPct = (g_dailyStartEquity > 0.0) ? ((g_dailyHighEquity - g_dailyStartEquity) / g_dailyStartEquity * 100.0) : 0.0;
      bool hitLoss = SUIS_DailyMaxLossPct > 0.0 && dayPct <= -SUIS_DailyMaxLossPct;
      bool hitProfit = SUIS_DailyProfitStopPct > 0.0 && dayPct >= SUIS_DailyProfitStopPct;
      bool hitGiveback = SUIS_DailyProfitLockStartPct > 0.0 &&
                         SUIS_DailyMaxGivebackPct > 0.0 &&
                         highPct >= SUIS_DailyProfitLockStartPct &&
                         (highPct - dayPct) >= SUIS_DailyMaxGivebackPct;

      if((hitLoss || hitProfit || hitGiveback) && !g_dailyStopped)
        {
         g_dailyStopped = true;
         if(hitLoss)
            reason = StringFormat("daily max loss hit %.2f%% <= -%.2f%%", dayPct, SUIS_DailyMaxLossPct);
         else if(hitProfit)
            reason = StringFormat("daily profit stop hit %.2f%% >= %.2f%%", dayPct, SUIS_DailyProfitStopPct);
         else
            reason = StringFormat("daily giveback hit high %.2f%% now %.2f%% giveback %.2f%%", highPct, dayPct, highPct - dayPct);
         SUISRiskGuardLog(reason, true);
         if(allowClose && (SUIS_DailyClosePositionsOnStop || SUIS_ClosePositionsOnSafetyStop))
            SUISCloseOwnPositions(reason);
        }

      if(g_dailyStopped)
        {
         blocked = true;
         reason = "daily guard stopped trading until next day";
        }
     }

   if(SUIS_EnableWeeklyGuard)
     {
      if(g_weeklyStartEquity <= 0.0)
         g_weeklyStartEquity = equity;
      g_weeklyHighEquity = MathMax(g_weeklyHighEquity, equity);

      double weekPct = (g_weeklyStartEquity > 0.0) ? ((equity - g_weeklyStartEquity) / g_weeklyStartEquity * 100.0) : 0.0;
      double weekHighPct = (g_weeklyStartEquity > 0.0) ? ((g_weeklyHighEquity - g_weeklyStartEquity) / g_weeklyStartEquity * 100.0) : 0.0;
      bool hitWeekLoss = SUIS_WeeklyMaxLossPct > 0.0 && weekPct <= -SUIS_WeeklyMaxLossPct;
      bool hitWeekGiveback = SUIS_WeeklyProfitLockStartPct > 0.0 &&
                             SUIS_WeeklyMaxGivebackPct > 0.0 &&
                             weekHighPct >= SUIS_WeeklyProfitLockStartPct &&
                             (weekHighPct - weekPct) >= SUIS_WeeklyMaxGivebackPct;

      if((hitWeekLoss || hitWeekGiveback) && !g_weeklyStopped)
        {
         g_weeklyStopped = true;
         if(hitWeekLoss)
            reason = StringFormat("weekly max loss hit %.2f%% <= -%.2f%%", weekPct, SUIS_WeeklyMaxLossPct);
         else
            reason = StringFormat("weekly giveback hit high %.2f%% now %.2f%% giveback %.2f%%", weekHighPct, weekPct, weekHighPct - weekPct);
         SUISRiskGuardLog(reason, true);
         if(allowClose && SUIS_ClosePositionsOnSafetyStop)
            SUISCloseOwnPositions(reason);
        }

      if(g_weeklyStopped)
        {
         blocked = true;
         reason = "weekly guard stopped trading until next week";
        }
     }

   if(SUIS_LossCooldownMinutes > 0 && now < g_lossCooldownUntil)
     {
      blocked = true;
      reason = "loss streak cooldown active";
     }

   if(blocked)
      SUISRiskGuardLog("entry blocked: " + reason);
   return(!blocked);
  }


bool SUISCopyRates(MqlRates &rates[], const int count)
  {
   ArraySetAsSeries(rates, true);
   return(CopyRates(_Symbol, SUIS_EXEC_TF, 0, count, rates) == count);
  }


double SUISIndicatorValue(const int handle, const int shift)
  {
   double buffer[];
   ArraySetAsSeries(buffer, true);
   if(CopyBuffer(handle, 0, 0, shift + 1, buffer) < (shift + 1))
      return(0.0);
   return(buffer[shift]);
  }


double SUISIndicatorValueFromBuffer(const int handle, const int bufferIndex, const int shift)
  {
   double buffer[];
   ArraySetAsSeries(buffer, true);
   if(CopyBuffer(handle, bufferIndex, 0, shift + 1, buffer) < (shift + 1))
      return(0.0);
   return(buffer[shift]);
  }


bool SUISRegimeIsBull(const SUISRegime regime)
  {
   return(regime == SUIS_REGIME_WEAK_BULL || regime == SUIS_REGIME_STRONG_BULL);
  }


bool SUISRegimeIsBear(const SUISRegime regime)
  {
   return(regime == SUIS_REGIME_WEAK_BEAR || regime == SUIS_REGIME_STRONG_BEAR);
  }


bool SUISRegimeIsStrong(const SUISRegime regime)
  {
   return(regime == SUIS_REGIME_STRONG_BULL || regime == SUIS_REGIME_STRONG_BEAR);
  }


SUISMacroRegime SUISDetectMacroRegime()
  {
   if(!SUIS_EnableMacroRegimeSwitch)
      return(SUIS_MACRO_UNKNOWN);

   double fastD1 = SUISIndicatorValue(g_emaFastD1, 1);
   double slowD1 = SUISIndicatorValue(g_emaSlowD1, 1);
   int slopeBars = (int)MathMax(1, SUIS_D1SlopeBars);
   double fastD1Past = SUISIndicatorValue(g_emaFastD1, 1 + slopeBars);
   double closeD1 = iClose(_Symbol, PERIOD_D1, 1);
   if(fastD1 <= 0.0 || slowD1 <= 0.0 || fastD1Past <= 0.0 || closeD1 <= 0.0)
      return(SUIS_MACRO_UNKNOWN);

   bool slopeUp = fastD1 > fastD1Past;
   bool slopeDown = fastD1 < fastD1Past;
   bool bull = fastD1 > slowD1 && slopeUp && closeD1 > fastD1;
   bool bear = fastD1 < slowD1 && slopeDown && closeD1 < fastD1;
   if(bull)
      return(SUIS_MACRO_BULL);
   if(bear)
      return(SUIS_MACRO_BEAR);
   return(SUIS_MACRO_SIDEWAYS);
  }


void SUISTelemetryLog(const string eventName,
                     const SUISSignal &signal,
                     const SUISRegime entryRegime,
                     const SUISMacroRegime macroRegime,
                     const string reason)
  {
   if(!SUIS_EnableTelemetryLogs)
      return;
   double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   double spread = (ask > 0.0 && bid > 0.0) ? (ask - bid) : 0.0;
   double atrM5 = SUISIndicatorValue(g_atrM5, 1);
   double fastD1 = SUISIndicatorValue(g_emaFastD1, 1);
   double slowD1 = SUISIndicatorValue(g_emaSlowD1, 1);
   PrintFormat("SUIS TELEMETRY | event=%s | side=%s | engine=%s (%s) | score=%d grade=%s tags=%s | h1h4=%s macro=%s | hour=%02d spread=%.2f atrM5=%.2f d1Fast=%.2f d1Slow=%.2f | reason=%s | comment=%s",
               eventName,
               signal.sell ? "SELL" : "BUY",
               SUISEngineComment(signal.engineCode),
               signal.engineCode,
               signal.score,
               signal.grade,
               signal.tags,
               SUISRegimeLabel(entryRegime),
               SUISMacroRegimeLabel(macroRegime),
               SUISHourOf(TimeCurrent()),
               spread,
               atrM5,
               fastD1,
               slowD1,
               reason,
               signal.comment);
  }


bool SUISMacroAllowsSignal(const SUISSignal &signal,
                          const SUISRegime entryRegime,
                          string &reason)
  {
   reason = "macro switch disabled";
   if(!SUIS_EnableMacroRegimeSwitch)
      return(true);

   SUISMacroRegime macroRegime = SUISDetectMacroRegime();
   if(macroRegime == SUIS_MACRO_UNKNOWN)
     {
      reason = "macro unknown";
  return(false);
  }

   if(signal.sell)
     {
      reason = "sell path unchanged";
      return(true);
     }

   if(SUIS_BlockAddOnOutsideMacroBull && signal.engineCode == "AB" && macroRegime != SUIS_MACRO_BULL)
     {
      reason = "buy add-on blocked outside D1 bull";
      return(false);
     }

   if(macroRegime == SUIS_MACRO_BULL)
     {
      reason = "D1 bull";
      return(SUIS_AllowBuyInMacroBull);
     }

   if(macroRegime == SUIS_MACRO_SIDEWAYS)
     {
      if(SUIS_AllowBuyInMacroSideways && signal.score >= SUIS_MacroSidewaysMinScore)
        {
         reason = "D1 sideways high-score buy";
         return(true);
        }
      if(SUIS_AllowStrongBullBuyInMacroSideways && entryRegime == SUIS_REGIME_STRONG_BULL && signal.score >= SUIS_MacroSidewaysMinScore)
        {
         reason = "D1 sideways strong-H1/H4 buy";
         return(true);
        }
      reason = "D1 sideways buy blocked";
      return(false);
     }

   if(macroRegime == SUIS_MACRO_BEAR)
     {
      if(SUIS_AllowBuyInMacroBear && entryRegime == SUIS_REGIME_STRONG_BULL && signal.score >= SUIS_MacroBearMinScore)
        {
         reason = "D1 bear emergency high-score buy";
         return(true);
        }
      reason = "D1 bear buy blocked";
      return(false);
     }

   reason = "macro regime not allowed";
   return(false);
  }


bool SUISStructuralPriceGateAllowsTrading(string &reason)
  {
   reason = "structural price gate disabled";
   if(!SUIS_EnableStructuralPriceGate)
      return(true);

   double closeD1 = iClose(_Symbol, PERIOD_D1, 1);
   if(closeD1 <= 0.0)
     {
      reason = "D1 close unavailable for structural price gate";
      return(false);
     }

   if(closeD1 < SUIS_MinD1CloseForTrading)
     {
      reason = StringFormat("D1 close %.2f below structural gate %.2f", closeD1, SUIS_MinD1CloseForTrading);
      return(false);
     }

   reason = StringFormat("D1 close %.2f above structural gate %.2f", closeD1, SUIS_MinD1CloseForTrading);
   return(true);
  }


bool SUISEngineFailGuardAllowsSignal(const SUISSignal &signal, string &reason)
  {
   reason = "engine fail guard disabled";
   if(!SUIS_EnableEngineFailGuard || signal.sell)
      return(true);

   if(signal.engineCode == "ZB" && g_dailyBuyZoneStopped)
     {
      reason = StringFormat("BUY_ZONE paused after %d high-score daily losses", g_dailyBuyZoneHighScoreLosses);
      return(false);
     }
   if(signal.engineCode == "PB" && g_dailyBuyPullbackStopped)
     {
      reason = StringFormat("BUY_PULLBACK paused after %d high-score daily losses", g_dailyBuyPullbackHighScoreLosses);
      return(false);
     }

   reason = "engine fail guard pass";
   return(true);
  }


bool SUISOverextensionGuardAppliesToSignal(const SUISSignal &signal)
  {
   if(signal.sell)
      return(false);
   if(signal.engineCode == "ZB")
      return(SUIS_OverextensionGuardBlocksZone);
   if(signal.engineCode == "PB")
      return(SUIS_OverextensionGuardBlocksPullback);
   if(signal.engineCode == "BO")
      return(SUIS_OverextensionGuardBlocksBreak);
   return(false);
  }


bool SUISOverextensionGuardAllowsSignal(const SUISSignal &signal, string &reason)
  {
   reason = "overextension guard disabled";
   if(!SUIS_EnableOverextensionGuard || !SUISOverextensionGuardAppliesToSignal(signal))
      return(true);

   double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   double fastD1 = SUISIndicatorValue(g_emaFastD1, 1);
   double atrD1 = SUISIndicatorValue(g_atrD1, 1);
   double fastH1 = SUISIndicatorValue(g_emaFastH1, 1);
   double atrH1 = SUISIndicatorValue(g_atrH1, 1);
   if(ask <= 0.0 || fastD1 <= 0.0 || atrD1 <= 0.0 || fastH1 <= 0.0 || atrH1 <= 0.0)
     {
      reason = "overextension guard indicator unavailable";
      return(true);
     }

   double d1Distance = (ask - fastD1) / atrD1;
   double h1Distance = (ask - fastH1) / atrH1;
   bool d1TooExtended = SUIS_MaxBuyD1FastDistanceATR > 0.0 && d1Distance >= SUIS_MaxBuyD1FastDistanceATR;
   bool h1TooExtended = SUIS_MaxBuyH1FastDistanceATR > 0.0 && h1Distance >= SUIS_MaxBuyH1FastDistanceATR;
   if(d1TooExtended || h1TooExtended)
     {
      reason = StringFormat("buy overextended d1=%.2f/%.2f h1=%.2f/%.2f",
                            d1Distance,
                            SUIS_MaxBuyD1FastDistanceATR,
                            h1Distance,
                            SUIS_MaxBuyH1FastDistanceATR);
      return(false);
     }

   reason = StringFormat("extension ok d1=%.2f h1=%.2f", d1Distance, h1Distance);
   return(true);
  }


bool SUISSubmitSignal(const SUISSignal &signal, const SUISRegime entryRegime)
  {
   SUISMacroRegime macroRegime = SUISDetectMacroRegime();
   string reason = "";
   if(!SUISEngineFailGuardAllowsSignal(signal, reason))
     {
      SUISTelemetryLog("REJECT_ENGINE_FAIL_GUARD", signal, entryRegime, macroRegime, reason);
      SUISRiskGuardLog("entry blocked: " + reason);
      return(false);
     }
   if(!SUISOverextensionGuardAllowsSignal(signal, reason))
     {
      SUISTelemetryLog("REJECT_OVEREXTENSION", signal, entryRegime, macroRegime, reason);
      SUISRiskGuardLog("entry blocked: " + reason);
      return(false);
     }
   if(!SUISMacroAllowsSignal(signal, entryRegime, reason))
     {
      SUISTelemetryLog("REJECT_MACRO", signal, entryRegime, macroRegime, reason);
      return(false);
     }
   SUISTelemetryLog("ENTRY_APPROVED", signal, entryRegime, macroRegime, reason);
   return(SUISSubmitSignal(signal));
  }


SUISRegime SUISDetectRegime()
  {
   double fastH1 = SUISIndicatorValue(g_emaFastH1, 1);
   double slowH1 = SUISIndicatorValue(g_emaSlowH1, 1);
   double fastH4 = SUISIndicatorValue(g_emaFastH4, 1);
   double slowH4 = SUISIndicatorValue(g_emaSlowH4, 1);
   double adxH1 = SUISIndicatorValueFromBuffer(g_adxH1, 0, 1);
   double atrH1 = SUISIndicatorValue(g_atrH1, 1);
   if(fastH1 == 0.0 || slowH1 == 0.0 || fastH4 == 0.0 || slowH4 == 0.0 || adxH1 == 0.0 || atrH1 == 0.0)
      return(SUIS_REGIME_NONE);

   bool bullAligned = fastH1 > slowH1 && fastH4 > slowH4;
   bool bearAligned = fastH1 < slowH1 && fastH4 < slowH4;
   if(!bullAligned && !bearAligned)
      return(SUIS_REGIME_MIXED);
   if(adxH1 < SUIS_H1ADXMin)
      return(SUIS_REGIME_MIXED);

   double gapAtr = MathAbs(fastH1 - slowH1) / atrH1;
   bool strong = adxH1 >= SUIS_H1ADXStrongMin && gapAtr >= SUIS_StrongGapATR;
   if(bullAligned)
      return(strong ? SUIS_REGIME_STRONG_BULL : SUIS_REGIME_WEAK_BULL);
   return(strong ? SUIS_REGIME_STRONG_BEAR : SUIS_REGIME_WEAK_BEAR);
  }


bool SUISMixedBiasBull()
  {
   double fastH1 = SUISIndicatorValue(g_emaFastH1, 1);
   double slowH1 = SUISIndicatorValue(g_emaSlowH1, 1);
   if(fastH1 == 0.0 || slowH1 == 0.0)
      return(true);
   return(fastH1 >= slowH1);
  }


int SUISCountOpenPositions()
  {
   int count = 0;
   for(int i = PositionsTotal() - 1; i >= 0; i--)
     {
      ulong ticket = PositionGetTicket(i);
      if(ticket == 0 || !PositionSelectByTicket(ticket))
         continue;
      if(PositionGetString(POSITION_SYMBOL) != _Symbol)
         continue;
      if((ulong)PositionGetInteger(POSITION_MAGIC) != SUIS_MAGIC)
         continue;
      count++;
     }
   return(count);
  }


int SUISCountOpenPositionsByType(const bool sell)
  {
   int count = 0;
   for(int i = PositionsTotal() - 1; i >= 0; i--)
     {
      ulong ticket = PositionGetTicket(i);
      if(ticket == 0 || !PositionSelectByTicket(ticket))
         continue;
      if(PositionGetString(POSITION_SYMBOL) != _Symbol)
         continue;
      if((ulong)PositionGetInteger(POSITION_MAGIC) != SUIS_MAGIC)
         continue;
      ENUM_POSITION_TYPE type = (ENUM_POSITION_TYPE)PositionGetInteger(POSITION_TYPE);
      if((sell && type == POSITION_TYPE_SELL) || (!sell && type == POSITION_TYPE_BUY))
         count++;
     }
   return(count);
  }


bool SUISHasOpenPositionByMagicType(const bool sell, const ulong magic)
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

bool SUISOppositePositionBlocks(const bool wantSell)
  {
   if(!SUIS_BlockOppositeDirection)
      return(false);
   bool oppositeSell = !wantSell;
   if(SUISHasOpenPositionByMagicType(oppositeSell, SUIS_MAGIC))
      return(true);
   if(SUIS_OppositeMagic > 0 && SUISHasOpenPositionByMagicType(oppositeSell, (ulong)SUIS_OppositeMagic))
      return(true);
   return(false);
  }


int SUISCountOpenAddOnsByType(const bool sell)
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
      if((ulong)PositionGetInteger(POSITION_MAGIC) != SUIS_MAGIC)
         continue;
      ENUM_POSITION_TYPE type = (ENUM_POSITION_TYPE)PositionGetInteger(POSITION_TYPE);
      if(((sell && type == POSITION_TYPE_SELL) || (!sell && type == POSITION_TYPE_BUY)) &&
         StringFind(PositionGetString(POSITION_COMMENT), marker) >= 0)
         count++;
     }
   return(count);
  }


bool SUISHasQualifiedLeadPosition(const bool sell, const double minProgressR)
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
      if((ulong)PositionGetInteger(POSITION_MAGIC) != SUIS_MAGIC)
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


double SUISClamp(const double value, const double lower, const double upper)
  {
   return(MathMax(lower, MathMin(upper, value)));
  }


double SUISMinStopDistance()
  {
   double point = SymbolInfoDouble(_Symbol, SYMBOL_POINT);
   double stops = (double)SymbolInfoInteger(_Symbol, SYMBOL_TRADE_STOPS_LEVEL) * point;
   double freeze = (double)SymbolInfoInteger(_Symbol, SYMBOL_TRADE_FREEZE_LEVEL) * point;
   double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   double spread = (ask > 0.0 && bid > 0.0) ? (ask - bid) : 0.0;
   return(MathMax(stops, freeze) + (spread * 2.0) + (point * 10.0));
  }


bool SUISStopsValid(const bool sell, const double entry, const double stopLoss, const double takeProfit)
  {
   double minDistance = SUISMinStopDistance();
   if(sell)
      return((stopLoss - entry) > minDistance && (entry - takeProfit) > minDistance);
   return((entry - stopLoss) > minDistance && (takeProfit - entry) > minDistance);
  }


double SUISNormalizeVolume(const double rawLot)
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


double SUISLotForRisk(const bool sell, const double entry, const double stopLoss, const double riskUsd)
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

   return(SUISNormalizeVolume(riskUsd / lossPerLot));
  }


double SUISRiskBudgetUsd(const bool sell)
  {
   return(SUISRiskBudgetUsd(sell, SUIS_REGIME_NONE));
  }


double SUISRiskBudgetUsd(const bool sell, const SUISRegime regime)
  {
   double equity = AccountInfoDouble(ACCOUNT_EQUITY);
   double riskUsd = equity * (SUIS_RiskPercent / 100.0);
   double multiplier = 0.0;

   if(sell)
     {
      if(regime == SUIS_REGIME_STRONG_BEAR)
         multiplier = SUIS_SellRiskMultiplier;
      else if(regime == SUIS_REGIME_WEAK_BEAR)
         multiplier = SUIS_WeakSellRiskMultiplier;
     }
   else
     {
      if(regime == SUIS_REGIME_STRONG_BULL)
         multiplier = SUIS_BuyRiskMultiplier;
      else if(regime == SUIS_REGIME_WEAK_BULL)
         multiplier = SUIS_WeakBuyRiskMultiplier;
     }

   riskUsd *= multiplier;
   return(riskUsd);
  }


double SUISBodyRatio(const MqlRates &bar)
  {
   double range = bar.high - bar.low;
   if(range <= 0.0)
      return(0.0);
   return(MathAbs(bar.close - bar.open) / range);
  }


double SUISHighestHigh(const MqlRates &rates[], const int startShift, const int endShift)
  {
   double value = rates[startShift].high;
   for(int shift = startShift + 1; shift <= endShift; shift++)
      value = MathMax(value, rates[shift].high);
   return(value);
  }


double SUISLowestLow(const MqlRates &rates[], const int startShift, const int endShift)
  {
   double value = rates[startShift].low;
   for(int shift = startShift + 1; shift <= endShift; shift++)
      value = MathMin(value, rates[shift].low);
   return(value);
  }


bool SUISHadPullback(const bool sell, const MqlRates &rates[], const double emaValue)
  {
   if(!SUIS_RequirePullback)
      return(true);
   int maxShift = MathMin(SUIS_PullbackLookback + 1, ArraySize(rates) - 1);
   for(int shift = 2; shift <= maxShift; shift++)
     {
      if(sell && (rates[shift].close > rates[shift].open || rates[shift].high >= emaValue))
         return(true);
      if(!sell && (rates[shift].close < rates[shift].open || rates[shift].low <= emaValue))
         return(true);
     }
   return(false);
  }


bool SUISBullPullbackSeen(const MqlRates &rates[], const double emaValue, const double atr)
  {
   int maxShift = MathMin(SUIS_BullPullbackLookback + 1, ArraySize(rates) - 1);
   double touchLevel = emaValue + (atr * SUIS_BullTouchATR);
   for(int shift = 2; shift <= maxShift; shift++)
     {
      if(rates[shift].low <= touchLevel && rates[shift].close < rates[shift].open)
         return(true);
     }
   return(false);
  }


bool SUISBearRejectionSeen(const MqlRates &rates[], const double emaValue, const double atr)
  {
   int maxShift = MathMin(SUIS_BearRejectLookback + 1, ArraySize(rates) - 1);
   double touchLevel = emaValue - (atr * SUIS_BearTouchATR);
   for(int shift = 2; shift <= maxShift; shift++)
     {
      if(rates[shift].high >= touchLevel && rates[shift].close > rates[shift].open)
         return(true);
     }
   return(false);
  }


bool SUISDirectionalHoldOk(const bool sell, const MqlRates &rates[], const double atr)
  {
   int bars = MathMax(1, SUIS_HoldBars);
   int lookback = MathMax(bars + 1, SUIS_ChopLookbackBars);
   double emaBuffer[];
   ArraySetAsSeries(emaBuffer, true);
   if(CopyBuffer(g_emaM5, 0, 0, lookback + 3, emaBuffer) < (lookback + 2))
      return(false);

   double holdBuffer = atr * SUIS_HoldBufferATR;
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

   if(flips > SUIS_MaxEmaFlips)
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


double SUISSellMinBreakATR(const SUISRegime regime)
  {
   return(SUISRegimeIsStrong(regime) ? SUIS_MinBreakATR : SUIS_WeakSellMinBreakATR);
  }


double SUISBuyMinBreakATR(const SUISRegime regime)
  {
   return(SUISRegimeIsStrong(regime) ? SUIS_BuyMinBreakATR : SUIS_WeakBuyMinBreakATR);
  }


double SUISSellMinBodyRatio(const SUISRegime regime)
  {
   return(SUISRegimeIsStrong(regime) ? SUIS_MinBodyRatio : SUIS_WeakSellMinBodyRatio);
  }


double SUISBuyMinBodyRatio(const SUISRegime regime)
  {
   return(SUISRegimeIsStrong(regime) ? SUIS_BuyMinBodyRatio : SUIS_WeakBuyMinBodyRatio);
  }


double SUISSellRRForRegime(const SUISRegime regime)
  {
   return(SUISRegimeIsStrong(regime) ? SUIS_SellRR : SUIS_WeakSellRR);
  }


double SUISBuyRRForRegime(const SUISRegime regime)
  {
   return(SUISRegimeIsStrong(regime) ? SUIS_BuyRR : SUIS_WeakBuyRR);
  }


double SUISBuyRiskMultiplierForRegime(const SUISRegime regime)
  {
   return(SUISRegimeIsStrong(regime) ? SUIS_BuyRiskMultiplier : SUIS_WeakBuyRiskMultiplier);
  }


double SUISBuyRiskBudgetUsd(const SUISRegime regime, const double overrideMultiplier = -1.0)
  {
   double equity = AccountInfoDouble(ACCOUNT_EQUITY);
   double riskUsd = equity * (SUIS_RiskPercent / 100.0);
   double multiplier = (overrideMultiplier >= 0.0) ? overrideMultiplier : SUISBuyRiskMultiplierForRegime(regime);
   return(riskUsd * multiplier);
  }


int SUISAllowedMaxPositions(const SUISRegime regime)
  {
   return(SUISRegimeIsStrong(regime) ? SUIS_MaxPositions : SUIS_WeakRegimeMaxPositions);
  }


bool SUISBuildSellSignal(const MqlRates &rates[], const double emaM5, const double atr, const SUISRegime regime, SUISSignal &signal)
  {
   if(!SUIS_EnableSells)
      return(false);
   if(!SUISRegimeIsBear(regime))
      return(false);
   int currentHour = SUISHourOf(TimeCurrent());
   if(!SUISHourInSession(currentHour, SUIS_SellSessionStartHour, SUIS_SellSessionEndHour))
      return(false);
   if(SUISEngineHourBlocked("BE", currentHour))
      return(false);

   const MqlRates bar = rates[1];
   double bodyRatio = SUISBodyRatio(bar);
   if(bar.close >= bar.open)
      return(false);
   if(bodyRatio < SUISSellMinBodyRatio(regime))
      return(false);
   if(bar.close >= emaM5)
      return(false);
   if((emaM5 - bar.close) > (atr * SUIS_MaxStretchATR))
      return(false);
   if(!SUISDirectionalHoldOk(true, rates, atr))
      return(false);
   if(!SUISHadPullback(true, rates, emaM5))
      return(false);

   int breakoutEnd = MathMin(SUIS_BreakoutLookback + 1, ArraySize(rates) - 1);
   double priorLow = SUISLowestLow(rates, 2, breakoutEnd);
   double minBreakAtr = SUISSellMinBreakATR(regime);
   double breakAtr = (priorLow - bar.close) / atr;
   if(bar.close > (priorLow - (atr * minBreakAtr)))
      return(false);

   double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   if(bid <= 0.0)
      return(false);

   bool rejectionSeen = SUISBearRejectionSeen(rates, emaM5, atr);
   bool bodyStrong = bodyRatio >= (SUISSellMinBodyRatio(regime) + 0.08);
   bool cleanStretch = (emaM5 - bar.close) <= (atr * 0.90);
   bool sessionCore = SUISHourInSession(currentHour, 10, 17);
   int score = 40;
   if(SUISRegimeIsStrong(regime))
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
   if(SUIS_MinTradeScore > 0 && score < SUIS_MinTradeScore)
     {
      SUISRejectedSignalLog("SELL", "BE", "score below gate", score, regime, currentHour, bodyRatio, breakAtr,
                           StringFormat("minBreakATR=%.2f rejection=%s coreSession=%s", minBreakAtr, rejectionSeen ? "yes" : "no", sessionCore ? "yes" : "no"));
      return(false);
     }
   if(!SUISBearSafePass("BE", regime, score, currentHour, bodyRatio, breakAtr))
     {
      SUISRejectedSignalLog("SELL", "BE", "bear safe mode", score, regime, currentHour, bodyRatio, breakAtr,
                           StringFormat("weakMinScore=%d weakMinBody=%.2f", SUIS_BearSafeWeakMinScore, SUIS_BearSafeWeakMinBodyRatio));
      return(false);
     }

   int stopEnd = MathMin(SUIS_StopLookbackBars, ArraySize(rates) - 1);
   double swingHigh = SUISHighestHigh(rates, 1, stopEnd);
   double stopDistance = SUISClamp((swingHigh - bid) + (atr * SUIS_StopBufferATR), SUIS_MinSLUsd, SUIS_MaxSLUsd);
   double stopLoss = SUISNormalizePrice(bid + stopDistance);
   double rr = SUISSellRRForRegime(regime);
   bool boosted = score >= SUIS_ScoreBoostMin;
   if(boosted)
      rr += SUIS_ScoreRRBonus;
   double takeProfit = SUISNormalizePrice(bid - (stopDistance * rr));
   if(!SUISStopsValid(true, bid, stopLoss, takeProfit))
      return(false);

   double riskUsd = SUISRiskBudgetUsd(true, regime);
   if(boosted)
      riskUsd *= SUIS_ScoreRiskBonus;
   double lot = SUISLotForRisk(true, bid, stopLoss, riskUsd);
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
   string tags = SUISAppendTag("", SUISRegimeIsStrong(regime) ? "RG" : "WG");
   tags = SUISAppendTag(tags, rejectionSeen ? "RJ" : "BR");
   tags = SUISAppendTag(tags, sessionCore ? "SE" : "XH");
   if(boosted)
      tags = SUISAppendTag(tags, "BX");
   string note = StringFormat("SELL score=%d breakATR=%.2f body=%.2f regime=%s rejection=%s session=%02d rr=%.2f",
                              score, breakAtr, bodyRatio, SUISRegimeLabel(regime),
                              rejectionSeen ? "yes" : "no", currentHour, rr);
   SUISFillSignalMeta(signal, "BE", score, tags, note);
  return(true);
  }


bool SUISBuildBullSubSignal(const MqlRates &rates[], const double emaM5, const double atr, const SUISRegime regime, SUISSignal &signal)
  {
   if(!SUIS_EnableBullSubEngine)
      return(false);
   bool weakBullAllowed = SUIS_BullSubAllowWeakBull && regime == SUIS_REGIME_WEAK_BULL;
   if(regime != SUIS_REGIME_STRONG_BULL && !weakBullAllowed)
      return(false);

   int currentHour = SUISHourOf(TimeCurrent());
   if(!SUISHourInSession(currentHour, SUIS_BullSubSessionStartHour, SUIS_BullSubSessionEndHour))
      return(false);
   if(SUIS_BullSubOnlyOutsideCore && SUISBuyHourPreferred(currentHour))
      return(false);
   if(SUISBuyHourBlocked(currentHour))
      return(false);
   if(SUISEngineHourBlocked("SB", currentHour))
      return(false);

   const MqlRates bar = rates[1];
   double bodyRatio = SUISBodyRatio(bar);
   if(bar.close <= bar.open)
      return(false);
   if(bodyRatio < SUIS_BullSubMinBodyRatio)
      return(false);
   if(bar.close <= emaM5)
      return(false);

   int endShift = MathMin(SUIS_BullSubCompressionBars + 1, ArraySize(rates) - 1);
   if(endShift < 3)
      return(false);
   double boxHigh = SUISHighestHigh(rates, 2, endShift);
   double boxLow = SUISLowestLow(rates, 2, endShift);
   double boxRange = boxHigh - boxLow;
   if(boxRange <= 0.0 || boxRange > (atr * SUIS_BullSubMaxRangeATR))
      return(false);
   if(boxLow > (emaM5 + (atr * SUIS_BullSubTouchEmaATR)))
      return(false);

   for(int shift = 2; shift <= endShift; shift++)
     {
      if(rates[shift].close < (emaM5 - (atr * 0.10)))
         return(false);
     }

   if(bar.close < (boxHigh + (atr * SUIS_BullSubBreakATR)))
      return(false);

   bool compactBox = boxRange <= (atr * 1.10);
   bool bodyStrong = bodyRatio >= (SUIS_BullSubMinBodyRatio + 0.08);
   bool tightToEma = boxLow <= (emaM5 + (atr * 0.08));
   int score = 45;
   score += weakBullAllowed ? 8 : 15;
   if(compactBox)
      score += 10;
   if(bodyStrong)
      score += 10;
   if(tightToEma)
      score += 10;
   if(SUIS_MinTradeScore > 0 && score < SUIS_MinTradeScore)
     {
      SUISRejectedSignalLog("BUY", "SB", "score below gate", score, regime, currentHour, bodyRatio, boxRange / atr,
                           StringFormat("compressionBoxATR=%.2f compact=%s tightToEma=%s", boxRange / atr, compactBox ? "yes" : "no", tightToEma ? "yes" : "no"));
      return(false);
     }

   double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   if(ask <= 0.0)
      return(false);

   double stopDistance = SUISClamp((ask - boxLow) + (atr * SUIS_StopBufferATR), SUIS_MinSLUsd, SUIS_MaxSLUsd);
   double stopLoss = SUISNormalizePrice(ask - stopDistance);
   double rr = SUIS_BullSubRR;
   bool boosted = score >= SUIS_ScoreBoostMin;
   if(boosted)
      rr += SUIS_ScoreRRBonus;
   double takeProfit = SUISNormalizePrice(ask + (stopDistance * rr));
   if(!SUISStopsValid(false, ask, stopLoss, takeProfit))
      return(false);

   double riskUsd = SUISBuyRiskBudgetUsd(regime, SUIS_BullSubRiskMultiplier);
   if(boosted)
      riskUsd *= SUIS_ScoreRiskBonus;
   double lot = SUISLotForRisk(false, ask, stopLoss, riskUsd);
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
   string tags = SUISAppendTag("", weakBullAllowed ? "WG" : "RG");
   tags = SUISAppendTag(tags, compactBox ? "CM" : "BX");
   tags = SUISAppendTag(tags, tightToEma ? "EM" : "BR");
   if(boosted)
      tags = SUISAppendTag(tags, "BX");
   string note = StringFormat("BULL SUB score=%d boxATR=%.2f body=%.2f regime=%s hour=%02d rr=%.2f",
                              score, boxRange / atr, bodyRatio, SUISRegimeLabel(regime), currentHour, rr);
   SUISFillSignalMeta(signal, "SB", score, tags, note);
   return(true);
  }


bool SUISBuildBearSubSignal(const MqlRates &rates[], const double emaM5, const double atr, const SUISRegime regime, SUISSignal &signal)
  {
   if(!SUIS_EnableBearSubEngine)
      return(false);
   bool weakBearAllowed = SUIS_BearSubAllowWeakBear && regime == SUIS_REGIME_WEAK_BEAR;
   if(regime != SUIS_REGIME_STRONG_BEAR && !weakBearAllowed)
      return(false);

   int currentHour = SUISHourOf(TimeCurrent());
   if(!SUISHourInSession(currentHour, SUIS_BearSubSessionStartHour, SUIS_BearSubSessionEndHour))
      return(false);
   if(SUISEngineHourBlocked("SS", currentHour))
      return(false);

   const MqlRates bar = rates[1];
   double bodyRatio = SUISBodyRatio(bar);
   if(bar.close >= bar.open)
      return(false);
   if(bodyRatio < SUIS_BearSubMinBodyRatio)
      return(false);
   if(bar.close >= emaM5)
      return(false);

   int endShift = MathMin(SUIS_BearSubCompressionBars + 1, ArraySize(rates) - 1);
   if(endShift < 3)
      return(false);
   double boxHigh = SUISHighestHigh(rates, 2, endShift);
   double boxLow = SUISLowestLow(rates, 2, endShift);
   double boxRange = boxHigh - boxLow;
   if(boxRange <= 0.0 || boxRange > (atr * SUIS_BearSubMaxRangeATR))
      return(false);
   if(boxHigh < (emaM5 - (atr * SUIS_BearSubTouchEmaATR)))
      return(false);

   for(int shift = 2; shift <= endShift; shift++)
     {
      if(rates[shift].close > (emaM5 + (atr * 0.10)))
         return(false);
     }

   if(bar.close > (boxLow - (atr * SUIS_BearSubBreakATR)))
      return(false);

   bool compactBox = boxRange <= (atr * 1.10);
   bool bodyStrong = bodyRatio >= (SUIS_BearSubMinBodyRatio + 0.08);
   bool tightToEma = boxHigh >= (emaM5 - (atr * 0.08));
   int score = 45;
   score += weakBearAllowed ? 8 : 15;
   if(compactBox)
      score += 10;
   if(bodyStrong)
      score += 10;
   if(tightToEma)
      score += 10;
   if(SUIS_MinTradeScore > 0 && score < SUIS_MinTradeScore)
     {
      SUISRejectedSignalLog("SELL", "SS", "score below gate", score, regime, currentHour, bodyRatio, boxRange / atr,
                           StringFormat("compressionBoxATR=%.2f compact=%s tightToEma=%s", boxRange / atr, compactBox ? "yes" : "no", tightToEma ? "yes" : "no"));
      return(false);
     }
   if(!SUISBearSafePass("SS", regime, score, currentHour, bodyRatio, boxRange / atr))
     {
      SUISRejectedSignalLog("SELL", "SS", "bear safe mode", score, regime, currentHour, bodyRatio, boxRange / atr,
                           StringFormat("compressionBoxATR=%.2f", boxRange / atr));
      return(false);
     }

   double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   if(bid <= 0.0)
      return(false);

   double stopDistance = SUISClamp((boxHigh - bid) + (atr * SUIS_StopBufferATR), SUIS_MinSLUsd, SUIS_MaxSLUsd);
   double stopLoss = SUISNormalizePrice(bid + stopDistance);
   double rr = SUIS_BearSubRR;
   bool boosted = score >= SUIS_ScoreBoostMin;
   if(boosted)
      rr += SUIS_ScoreRRBonus;
   double takeProfit = SUISNormalizePrice(bid - (stopDistance * rr));
   if(!SUISStopsValid(true, bid, stopLoss, takeProfit))
      return(false);

   double riskUsd = SUISRiskBudgetUsd(true, regime) * SUIS_BearSubRiskMultiplier;
   if(boosted)
      riskUsd *= SUIS_ScoreRiskBonus;
   double lot = SUISLotForRisk(true, bid, stopLoss, riskUsd);
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
   string tags = SUISAppendTag("", weakBearAllowed ? "WG" : "RG");
   tags = SUISAppendTag(tags, compactBox ? "CM" : "BX");
   tags = SUISAppendTag(tags, tightToEma ? "EM" : "BR");
   if(boosted)
      tags = SUISAppendTag(tags, "BX");
   string note = StringFormat("BEAR SUB score=%d boxATR=%.2f body=%.2f regime=%s hour=%02d rr=%.2f",
                              score, boxRange / atr, bodyRatio, SUISRegimeLabel(regime), currentHour, rr);
   SUISFillSignalMeta(signal, "SS", score, tags, note);
  return(true);
  }


bool SUISBuildImpulsePullbackSignal(const MqlRates &rates[], const double emaM5, const double atr, const SUISRegime regime, const bool sell, SUISSignal &signal)
  {
   if(!SUIS_EnableImpulsePullbackEngine)
      return(false);
   if(sell && !SUIS_EnableSellImpulsePullback)
      return(false);
   if(!sell && !SUIS_EnableBuyImpulsePullback)
      return(false);
   if(atr <= 0.0 || emaM5 <= 0.0 || ArraySize(rates) < 6)
      return(false);
   if(sell)
     {
      if(!SUIS_EnableSells || !SUISRegimeIsBear(regime))
         return(false);
     }
   else
     {
      if(!SUIS_EnableBuys || !SUISRegimeIsBull(regime))
         return(false);
     }
   if(!SUIS_ImpulseAllowWeakRegime && !SUISRegimeIsStrong(regime))
      return(false);

   int currentHour = SUISHourOf(TimeCurrent());
   if(!SUISHourInSession(currentHour, SUIS_ImpulseSessionStartHour, SUIS_ImpulseSessionEndHour))
      return(false);
   if(!sell && SUISBuyHourBlocked(currentHour))
      return(false);
   if(SUISEngineHourBlocked(sell ? "IS" : "IB", currentHour))
      return(false);

   const MqlRates trigger = rates[1];
   const MqlRates pullback = rates[2];
   const MqlRates impulse = rates[3];
   double impulseBody = SUISBodyRatio(impulse);
   double triggerBody = SUISBodyRatio(trigger);
   double impulseMoveAtr = MathAbs(impulse.close - impulse.open) / atr;
   double pullbackRangeAtr = (pullback.high - pullback.low) / atr;
   if(impulseBody < SUIS_ImpulseMinBodyRatio || impulseMoveAtr < SUIS_ImpulseMinMoveATR)
      return(false);
   if(triggerBody < SUIS_ImpulseEntryBodyRatio || pullbackRangeAtr > SUIS_ImpulsePullbackMaxATR)
      return(false);
   if(!SUISDirectionalHoldOk(sell, rates, atr))
      return(false);

   if(sell)
     {
      if(impulse.close >= impulse.open || trigger.close >= trigger.open)
         return(false);
      if(pullback.high > (impulse.open + (atr * SUIS_ImpulsePullbackMaxATR)))
         return(false);
      if(trigger.close >= emaM5)
         return(false);
      if(trigger.close > (pullback.low - (atr * SUIS_ImpulseBreakATR)))
         return(false);
      if((emaM5 - trigger.close) > (atr * SUIS_MaxStretchATR))
         return(false);

      bool brokeImpulse = trigger.close <= impulse.close;
      bool compactPullback = pullbackRangeAtr <= 0.55;
      int score = 42;
      score += SUISRegimeIsStrong(regime) ? 15 : 8;
      if(triggerBody >= (SUIS_ImpulseEntryBodyRatio + 0.10))
         score += 10;
      if(impulseMoveAtr >= (SUIS_ImpulseMinMoveATR + 0.35))
         score += 10;
      if(compactPullback)
         score += 8;
      if(brokeImpulse)
         score += 8;
      if(SUIS_MinTradeScore > 0 && score < SUIS_MinTradeScore)
        {
         SUISRejectedSignalLog("SELL", "IS", "score below gate", score, regime, currentHour, triggerBody, impulseMoveAtr,
                              StringFormat("impulseBody=%.2f pullbackATR=%.2f brokeImpulse=%s", impulseBody, pullbackRangeAtr, brokeImpulse ? "yes" : "no"));
         return(false);
        }
      if(!SUISBearSafePass("IS", regime, score, currentHour, triggerBody, impulseMoveAtr))
        {
         SUISRejectedSignalLog("SELL", "IS", "bear safe mode", score, regime, currentHour, triggerBody, impulseMoveAtr,
                              StringFormat("impulseBody=%.2f pullbackATR=%.2f", impulseBody, pullbackRangeAtr));
         return(false);
        }

      double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
      if(bid <= 0.0)
         return(false);
      double stopAnchor = MathMax(MathMax(impulse.high, pullback.high), trigger.high);
      double stopDistance = SUISClamp((stopAnchor - bid) + (atr * SUIS_StopBufferATR), SUIS_MinSLUsd, SUIS_MaxSLUsd);
      double stopLoss = SUISNormalizePrice(bid + stopDistance);
      double takeProfit = SUISNormalizePrice(bid - (stopDistance * SUIS_ImpulseRR));
      if(!SUISStopsValid(true, bid, stopLoss, takeProfit))
         return(false);
      double riskUsd = SUISRiskBudgetUsd(true, regime) * SUIS_ImpulseRiskMultiplier;
      double lot = SUISLotForRisk(true, bid, stopLoss, riskUsd);
      if(lot < SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN))
         return(false);

      signal.valid = true;
      signal.sell = true;
      signal.entry = bid;
      signal.stopLoss = stopLoss;
      signal.takeProfit = takeProfit;
      signal.lot = lot;
      signal.stopDistance = stopDistance;
      signal.rr = SUIS_ImpulseRR;
      string tags = SUISAppendTag("", SUISRegimeIsStrong(regime) ? "RG" : "WG");
      tags = SUISAppendTag(tags, "IP");
      tags = SUISAppendTag(tags, "RT");
      tags = SUISAppendTag(tags, brokeImpulse ? "BR" : "CT");
      string note = StringFormat("IMPULSE SELL score=%d impulseATR=%.2f impulseBody=%.2f triggerBody=%.2f pullbackATR=%.2f regime=%s hour=%02d rr=%.2f",
                                 score, impulseMoveAtr, impulseBody, triggerBody, pullbackRangeAtr, SUISRegimeLabel(regime), currentHour, SUIS_ImpulseRR);
      SUISFillSignalMeta(signal, "IS", score, tags, note);
      return(true);
     }

   if(impulse.close <= impulse.open || trigger.close <= trigger.open)
      return(false);
   if(pullback.low < (impulse.open - (atr * SUIS_ImpulsePullbackMaxATR)))
      return(false);
   if(trigger.close <= emaM5)
      return(false);
   if(trigger.close < (pullback.high + (atr * SUIS_ImpulseBreakATR)))
      return(false);
   if((trigger.close - emaM5) > (atr * SUIS_BullMaxStretchATR))
      return(false);

   bool brokeImpulse = trigger.close >= impulse.close;
   bool compactPullback = pullbackRangeAtr <= 0.55;
   int score = 42;
   score += SUISRegimeIsStrong(regime) ? 15 : 8;
   if(triggerBody >= (SUIS_ImpulseEntryBodyRatio + 0.10))
      score += 10;
   if(impulseMoveAtr >= (SUIS_ImpulseMinMoveATR + 0.35))
      score += 10;
   if(compactPullback)
      score += 8;
   if(brokeImpulse)
      score += 8;
   if(SUIS_MinTradeScore > 0 && score < SUIS_MinTradeScore)
     {
      SUISRejectedSignalLog("BUY", "IB", "score below gate", score, regime, currentHour, triggerBody, impulseMoveAtr,
                           StringFormat("impulseBody=%.2f pullbackATR=%.2f brokeImpulse=%s", impulseBody, pullbackRangeAtr, brokeImpulse ? "yes" : "no"));
      return(false);
     }

   double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   if(ask <= 0.0)
      return(false);
   double stopAnchor = MathMin(MathMin(impulse.low, pullback.low), trigger.low);
   double stopDistance = SUISClamp((ask - stopAnchor) + (atr * SUIS_StopBufferATR), SUIS_MinSLUsd, SUIS_MaxSLUsd);
   double stopLoss = SUISNormalizePrice(ask - stopDistance);
   double takeProfit = SUISNormalizePrice(ask + (stopDistance * SUIS_ImpulseRR));
   if(!SUISStopsValid(false, ask, stopLoss, takeProfit))
      return(false);
   double riskUsd = SUISBuyRiskBudgetUsd(regime, SUIS_ImpulseRiskMultiplier);
   double lot = SUISLotForRisk(false, ask, stopLoss, riskUsd);
   if(lot < SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN))
      return(false);

   signal.valid = true;
   signal.sell = false;
   signal.entry = ask;
   signal.stopLoss = stopLoss;
   signal.takeProfit = takeProfit;
   signal.lot = lot;
   signal.stopDistance = stopDistance;
   signal.rr = SUIS_ImpulseRR;
   string tags = SUISAppendTag("", SUISRegimeIsStrong(regime) ? "RG" : "WG");
   tags = SUISAppendTag(tags, "IP");
   tags = SUISAppendTag(tags, "RT");
   tags = SUISAppendTag(tags, brokeImpulse ? "BR" : "CT");
   string note = StringFormat("IMPULSE BUY score=%d impulseATR=%.2f impulseBody=%.2f triggerBody=%.2f pullbackATR=%.2f regime=%s hour=%02d rr=%.2f",
                              score, impulseMoveAtr, impulseBody, triggerBody, pullbackRangeAtr, SUISRegimeLabel(regime), currentHour, SUIS_ImpulseRR);
   SUISFillSignalMeta(signal, "IB", score, tags, note);
   return(true);
  }


bool SUISBuildZoneRetestSignal(const MqlRates &rates[], const double emaM5, const double atr, const SUISRegime regime, const bool sell, SUISSignal &signal)
  {
   if(!SUIS_EnableZoneRetestEngine)
      return(false);
   if(sell)
     {
      if(!SUIS_EnableSells || !SUISRegimeIsBear(regime))
         return(false);
      if(!SUIS_ZoneAllowWeakRegime && !SUISRegimeIsStrong(regime))
         return(false);
     }
   else
     {
      if(!SUIS_EnableBuys || !SUISRegimeIsBull(regime))
         return(false);
      if(!SUIS_ZoneAllowWeakRegime && !SUISRegimeIsStrong(regime))
         return(false);
     }

   int currentHour = SUISHourOf(TimeCurrent());
   if(sell)
     {
      if(!SUISHourInSession(currentHour, SUIS_SellSessionStartHour, SUIS_SellSessionEndHour))
         return(false);
     }
   else
     {
      if(!SUISHourInSession(currentHour, SUIS_BuySessionStartHour, SUIS_BuySessionEndHour))
         return(false);
      if(SUIS_ZoneUseCoreHours && !SUISBuyHourPreferred(currentHour))
         return(false);
      if(SUISBuyHourBlocked(currentHour))
         return(false);
     }
   if(SUISEngineHourBlocked(sell ? "ZS" : "ZB", currentHour))
      return(false);

   const MqlRates retest = rates[1];
   const MqlRates anchor = rates[2];
   if(SUISBodyRatio(anchor) < SUIS_ZoneMinBodyRatio)
      return(false);
   if(SUISBodyRatio(retest) < 0.35)
      return(false);
   if(!SUISDirectionalHoldOk(sell, rates, atr))
      return(false);

   int lookbackEnd = MathMin(SUIS_ZoneLookback + 2, ArraySize(rates) - 1);
   if(lookbackEnd <= 3)
      return(false);

   if(sell)
     {
      if(anchor.close >= anchor.open || retest.close >= retest.open)
         return(false);
      double priorLow = SUISLowestLow(rates, 3, lookbackEnd);
      double breakAtr = (priorLow - anchor.close) / atr;
      if(anchor.close > (priorLow - (atr * SUIS_ZoneBreakATR)))
         return(false);
      if(retest.close >= emaM5)
         return(false);

      double zoneHigh = MathMax(anchor.open, anchor.close);
      double zoneLow = MathMin(anchor.open, anchor.close);
      double zoneMid = (zoneHigh + zoneLow) * 0.5;
      bool touchedMid = retest.high >= (zoneMid - (atr * SUIS_ZoneMidTouchATR));
      bool overshootOk = retest.high <= (zoneHigh + (atr * SUIS_ZoneOvershootATR));
      bool reclaimed = retest.close <= (zoneMid - (atr * SUIS_ZoneReclaimATR));
      if(!touchedMid || !overshootOk || !reclaimed)
         return(false);

      double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
      if(bid <= 0.0)
         return(false);
      double stopAnchor = MathMax(anchor.high, retest.high);
      double stopDistance = SUISClamp((stopAnchor - bid) + (atr * SUIS_StopBufferATR), SUIS_MinSLUsd, SUIS_MaxSLUsd);
      double stopLoss = SUISNormalizePrice(bid + stopDistance);
      double rr = SUIS_ZoneRR;
      int score = 45;
      if(SUISRegimeIsStrong(regime))
         score += 15;
      else
         score += 8;
      score += 12;
      if(SUISBodyRatio(anchor) >= (SUIS_ZoneMinBodyRatio + 0.08))
         score += 8;
      if(breakAtr >= (SUIS_ZoneBreakATR + 0.06))
         score += 10;
      if(touchedMid)
         score += 8;
      if(reclaimed)
         score += 6;
      if(SUIS_MinTradeScore > 0 && score < SUIS_MinTradeScore)
        {
         SUISRejectedSignalLog("SELL", "ZS", "score below gate", score, regime, currentHour, SUISBodyRatio(retest), breakAtr,
                              StringFormat("anchorBody=%.2f touchedMid=%s reclaimed=%s", SUISBodyRatio(anchor), touchedMid ? "yes" : "no", reclaimed ? "yes" : "no"));
         return(false);
        }
      if(!SUISBearSafePass("ZS", regime, score, currentHour, SUISBodyRatio(retest), breakAtr))
        {
         SUISRejectedSignalLog("SELL", "ZS", "bear safe mode", score, regime, currentHour, SUISBodyRatio(retest), breakAtr,
                              StringFormat("anchorBody=%.2f blockWeakZone=%s", SUISBodyRatio(anchor), SUIS_BearSafeBlockWeakZone ? "yes" : "no"));
         return(false);
        }

      double takeProfit = SUISNormalizePrice(bid - (stopDistance * rr));
      if(!SUISStopsValid(true, bid, stopLoss, takeProfit))
         return(false);
      double riskUsd = SUISRiskBudgetUsd(true, regime) * SUIS_ZoneRiskMultiplier;
      double lot = SUISLotForRisk(true, bid, stopLoss, riskUsd);
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
      string tags = SUISAppendTag("", SUISRegimeIsStrong(regime) ? "RG" : "WG");
      tags = SUISAppendTag(tags, "ZN");
      tags = SUISAppendTag(tags, "RT");
      tags = SUISAppendTag(tags, "BM");
      string note = StringFormat("ZONE SELL score=%d breakATR=%.2f anchorBody=%.2f retestBody=%.2f regime=%s hour=%02d rr=%.2f",
                                 score, breakAtr, SUISBodyRatio(anchor), SUISBodyRatio(retest), SUISRegimeLabel(regime), currentHour, rr);
      SUISFillSignalMeta(signal, "ZS", score, tags, note);
      return(true);
     }

   if(anchor.close <= anchor.open || retest.close <= retest.open)
      return(false);
   double priorHigh = SUISHighestHigh(rates, 3, lookbackEnd);
   double breakAtr = (anchor.close - priorHigh) / atr;
   if(anchor.close < (priorHigh + (atr * SUIS_ZoneBreakATR)))
      return(false);
   if(retest.close <= emaM5)
      return(false);

   double zoneHigh = MathMax(anchor.open, anchor.close);
   double zoneLow = MathMin(anchor.open, anchor.close);
   double zoneMid = (zoneHigh + zoneLow) * 0.5;
   bool touchedMid = retest.low <= (zoneMid + (atr * SUIS_ZoneMidTouchATR));
   bool overshootOk = retest.low >= (zoneLow - (atr * SUIS_ZoneOvershootATR));
   bool reclaimed = retest.close >= (zoneMid + (atr * SUIS_ZoneReclaimATR));
   if(!touchedMid || !overshootOk || !reclaimed)
      return(false);

   double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   if(ask <= 0.0)
      return(false);
   double stopAnchor = MathMin(anchor.low, retest.low);
   double stopDistance = SUISClamp((ask - stopAnchor) + (atr * SUIS_StopBufferATR), SUIS_MinSLUsd, SUIS_MaxSLUsd);
   double stopLoss = SUISNormalizePrice(ask - stopDistance);
   double rr = SUIS_ZoneRR;
   int score = 45;
   if(SUISRegimeIsStrong(regime))
      score += 15;
   else
      score += 8;
   score += 12;
   if(SUISBodyRatio(anchor) >= (SUIS_ZoneMinBodyRatio + 0.08))
      score += 8;
   if(breakAtr >= (SUIS_ZoneBreakATR + 0.06))
      score += 10;
   if(touchedMid)
      score += 8;
   if(reclaimed)
      score += 6;
   if(SUIS_MinTradeScore > 0 && score < SUIS_MinTradeScore)
     {
      SUISRejectedSignalLog("BUY", "ZB", "score below gate", score, regime, currentHour, SUISBodyRatio(retest), breakAtr,
                           StringFormat("anchorBody=%.2f touchedMid=%s reclaimed=%s", SUISBodyRatio(anchor), touchedMid ? "yes" : "no", reclaimed ? "yes" : "no"));
      return(false);
     }

   double takeProfit = SUISNormalizePrice(ask + (stopDistance * rr));
   if(!SUISStopsValid(false, ask, stopLoss, takeProfit))
      return(false);
   double riskUsd = SUISBuyRiskBudgetUsd(regime, SUIS_ZoneRiskMultiplier);
   double lot = SUISLotForRisk(false, ask, stopLoss, riskUsd);
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
   string tags = SUISAppendTag("", SUISRegimeIsStrong(regime) ? "RG" : "WG");
   tags = SUISAppendTag(tags, "ZN");
   tags = SUISAppendTag(tags, "RT");
   tags = SUISAppendTag(tags, "BM");
   string note = StringFormat("ZONE BUY score=%d breakATR=%.2f anchorBody=%.2f retestBody=%.2f regime=%s hour=%02d rr=%.2f",
                              score, breakAtr, SUISBodyRatio(anchor), SUISBodyRatio(retest), SUISRegimeLabel(regime), currentHour, rr);
   SUISFillSignalMeta(signal, "ZB", score, tags, note);
   return(true);
  }


bool SUISBuildBuySignal(const MqlRates &rates[], const double emaM5, const double atr, const SUISRegime regime, SUISSignal &signal)
  {
   if(!SUIS_EnableBuys)
      return(false);
   if(!SUISRegimeIsBull(regime))
      return(false);
   int currentHour = SUISHourOf(TimeCurrent());
   bool strongBullExtraSession = (regime == SUIS_REGIME_STRONG_BULL && SUIS_StrongBullRelaxBuySession);
   bool strongBullExtraHours = (regime == SUIS_REGIME_STRONG_BULL && SUIS_StrongBullRelaxCoreHours);
   bool inCoreHour = SUISBuyHourPreferred(currentHour);
   if(!strongBullExtraSession && !SUISHourInSession(currentHour, SUIS_BuySessionStartHour, SUIS_BuySessionEndHour))
      return(false);
   if(SUIS_UseBuyCoreHours && !inCoreHour && !strongBullExtraHours)
      return(false);
   if(SUISBuyHourBlocked(currentHour))
      return(false);

   const MqlRates bar = rates[1];
   double bodyRatio = SUISBodyRatio(bar);
   if(bar.close <= bar.open)
      return(false);
   if(bodyRatio < SUISBuyMinBodyRatio(regime))
      return(false);
   if(bar.close <= emaM5)
      return(false);
   if((bar.close - emaM5) > (atr * SUIS_BullMaxStretchATR))
      return(false);
   if(!SUISDirectionalHoldOk(false, rates, atr))
      return(false);
   if(!SUISHadPullback(false, rates, emaM5))
      return(false);

   int breakoutEnd = MathMin(SUIS_BreakoutLookback + 1, ArraySize(rates) - 1);
   double priorHigh = SUISHighestHigh(rates, 2, breakoutEnd);
   double minBreakAtr = SUISBuyMinBreakATR(regime);
   bool breakoutSetup = SUIS_AllowBreakoutBuys &&
                        (bar.close >= (priorHigh + (atr * minBreakAtr)));

   const MqlRates prev = rates[2];
   bool pullbackSeen = SUISBullPullbackSeen(rates, emaM5, atr);
   bool pullbackSetup = SUIS_AllowPullbackBuys &&
                        pullbackSeen &&
                        (bar.close >= (prev.high + (atr * SUIS_BullReclaimATR)));
   if(strongBullExtraHours && !inCoreHour && SUIS_StrongBullPullbackOnlyOutsideCore)
      breakoutSetup = false;
   if(!breakoutSetup && !pullbackSetup)
      return(false);

   double breakAtr = (bar.close - priorHigh) / atr;
   bool bodyStrong = bodyRatio >= (SUISBuyMinBodyRatio(regime) + 0.08);
   bool cleanStretch = (bar.close - emaM5) <= (atr * 0.70);
   int score = 35;
   if(SUISRegimeIsStrong(regime))
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
   if(SUIS_MinTradeScore > 0 && score < SUIS_MinTradeScore)
     {
      string rejectEngine = pullbackSetup && !breakoutSetup ? "PB" : "BO";
      SUISRejectedSignalLog("BUY", rejectEngine, "score below gate", score, regime, currentHour, bodyRatio, breakAtr,
                           StringFormat("core=%s pullbackSeen=%s breakout=%s pullback=%s", inCoreHour ? "yes" : "no", pullbackSeen ? "yes" : "no", breakoutSetup ? "yes" : "no", pullbackSetup ? "yes" : "no"));
      return(false);
     }

   double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   if(ask <= 0.0)
      return(false);

   int stopEnd = MathMin(SUIS_StopLookbackBars, ArraySize(rates) - 1);
   if(pullbackSetup && !breakoutSetup)
      stopEnd = MathMin(MathMax(SUIS_StopLookbackBars, SUIS_BullPullbackLookback + 1), ArraySize(rates) - 1);
   double swingLow = SUISLowestLow(rates, 1, stopEnd);
   double stopDistance = SUISClamp((ask - swingLow) + (atr * SUIS_StopBufferATR), SUIS_MinSLUsd, SUIS_MaxSLUsd);
   double stopLoss = SUISNormalizePrice(ask - stopDistance);
   double rr = SUISBuyRRForRegime(regime);
   bool boosted = score >= SUIS_ScoreBoostMin;
   if(boosted)
      rr += SUIS_ScoreRRBonus;
   double takeProfit = SUISNormalizePrice(ask + (stopDistance * rr));
   if(!SUISStopsValid(false, ask, stopLoss, takeProfit))
      return(false);

   double riskUsd = SUISBuyRiskBudgetUsd(regime);
   if(boosted)
      riskUsd *= SUIS_ScoreRiskBonus;
   double lot = SUISLotForRisk(false, ask, stopLoss, riskUsd);
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
   if(SUISEngineHourBlocked(engineCode, currentHour))
      return(false);
   string tags = SUISAppendTag("", SUISRegimeIsStrong(regime) ? "RG" : "WG");
   tags = SUISAppendTag(tags, inCoreHour ? "CH" : "XH");
   tags = SUISAppendTag(tags, pullbackSetup ? "RC" : "BR");
   if(boosted)
      tags = SUISAppendTag(tags, "BX");
   string note = StringFormat("%s score=%d breakATR=%.2f body=%.2f regime=%s core=%s pullback=%s rr=%.2f",
                              engineCode == "PB" ? "BULL PB" : "BULL BO",
                              score, breakAtr, bodyRatio, SUISRegimeLabel(regime),
                              inCoreHour ? "yes" : "no", pullbackSeen ? "yes" : "no", rr);
   SUISFillSignalMeta(signal, engineCode, score, tags, note);
   return(true);
  }


bool SUISBuildAddOnSignal(const MqlRates &rates[], const double emaM5, const double atr, const SUISRegime regime, const bool sell, SUISSignal &signal)
  {
   if(!SUIS_EnableAddOnEngine)
      return(false);
   if(sell && !SUIS_EnableSellAddOns)
      return(false);
   if(!sell && !SUIS_EnableBuyAddOns)
      return(false);
   if(sell)
     {
      if(!SUISRegimeIsBear(regime) || (!SUISRegimeIsStrong(regime) && !SUIS_AddOnAllowWeakRegime))
         return(false);
     }
   else
     {
      if(!SUISRegimeIsBull(regime) || (!SUISRegimeIsStrong(regime) && !SUIS_AddOnAllowWeakRegime))
         return(false);
     }

   if(SUISCountOpenAddOnsByType(sell) >= SUIS_AddOnMaxPerSide)
      return(false);
   if(!SUISHasQualifiedLeadPosition(sell, SUIS_AddOnMinProgressR))
      return(false);

   int currentHour = SUISHourOf(TimeCurrent());
   if(sell)
     {
      if(!SUISHourInSession(currentHour, SUIS_SellSessionStartHour, SUIS_SellSessionEndHour))
         return(false);
     }
   else
     {
      if(!SUISHourInSession(currentHour, SUIS_BuySessionStartHour, SUIS_BuySessionEndHour))
         return(false);
      if(SUIS_UseBuyCoreHours && !SUISBuyHourPreferred(currentHour))
         return(false);
      if(SUISBuyHourBlocked(currentHour))
         return(false);
     }
   if(SUISEngineHourBlocked(sell ? "AS" : "AB", currentHour))
      return(false);

   const MqlRates bar = rates[1];
   const MqlRates prev = rates[2];
   double bodyRatio = SUISBodyRatio(bar);
   if(bodyRatio < SUIS_AddOnMinBodyRatio)
      return(false);
   if(!SUISDirectionalHoldOk(sell, rates, atr))
      return(false);

   if(sell)
     {
      if(bar.close >= bar.open || bar.close >= emaM5)
         return(false);
      if(bar.close > (prev.low - (atr * SUIS_AddOnBreakATR)))
         return(false);
      double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
      if(bid <= 0.0)
         return(false);
      double triggerHigh = MathMax(bar.high, prev.high);
      double stopDistance = SUISClamp((triggerHigh - bid) + (atr * SUIS_StopBufferATR), SUIS_MinSLUsd, SUIS_MaxSLUsd);
      double stopLoss = SUISNormalizePrice(bid + stopDistance);
      double takeProfit = SUISNormalizePrice(bid - (stopDistance * SUIS_AddOnRR));
      if(!SUISStopsValid(true, bid, stopLoss, takeProfit))
         return(false);
      double riskUsd = SUISRiskBudgetUsd(true, regime) * SUIS_AddOnRiskMultiplier;
      double lot = SUISLotForRisk(true, bid, stopLoss, riskUsd);
      if(lot < SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN))
         return(false);

      signal.valid = true;
      signal.sell = true;
      signal.entry = bid;
      signal.stopLoss = stopLoss;
      signal.takeProfit = takeProfit;
      signal.lot = lot;
      signal.stopDistance = stopDistance;
      signal.rr = SUIS_AddOnRR;
      if(!SUISBearSafePass("AS", regime, 76, currentHour, bodyRatio, 0.0))
        {
         SUISRejectedSignalLog("SELL", "AS", "bear safe mode", 76, regime, currentHour, bodyRatio, 0.0,
                              StringFormat("blockWeakAddOns=%s", SUIS_BearSafeBlockWeakAddOns ? "yes" : "no"));
         return(false);
        }
      string tags = SUISAppendTag("", SUISRegimeIsStrong(regime) ? "RG" : "WG");
      tags = SUISAppendTag(tags, "AD");
      tags = SUISAppendTag(tags, "CT");
      string note = StringFormat("SELL ADD score=%d progress>=%.2f body=%.2f regime=%s hour=%02d rr=%.2f",
                                 76, SUIS_AddOnMinProgressR, bodyRatio, SUISRegimeLabel(regime), currentHour, SUIS_AddOnRR);
      SUISFillSignalMeta(signal, "AS", 76, tags, note);
      return(true);
     }

   if(bar.close <= bar.open || bar.close <= emaM5)
      return(false);
   if(bar.close < (prev.high + (atr * SUIS_AddOnBreakATR)))
      return(false);
   double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   if(ask <= 0.0)
      return(false);
   double triggerLow = MathMin(bar.low, prev.low);
   double stopDistance = SUISClamp((ask - triggerLow) + (atr * SUIS_StopBufferATR), SUIS_MinSLUsd, SUIS_MaxSLUsd);
   double stopLoss = SUISNormalizePrice(ask - stopDistance);
   double takeProfit = SUISNormalizePrice(ask + (stopDistance * SUIS_AddOnRR));
   if(!SUISStopsValid(false, ask, stopLoss, takeProfit))
      return(false);
   double riskUsd = SUISBuyRiskBudgetUsd(regime, SUIS_AddOnRiskMultiplier);
   double lot = SUISLotForRisk(false, ask, stopLoss, riskUsd);
   if(lot < SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN))
      return(false);

   signal.valid = true;
   signal.sell = false;
   signal.entry = ask;
   signal.stopLoss = stopLoss;
   signal.takeProfit = takeProfit;
   signal.lot = lot;
   signal.stopDistance = stopDistance;
   signal.rr = SUIS_AddOnRR;
   string tags = SUISAppendTag("", SUISRegimeIsStrong(regime) ? "RG" : "WG");
   tags = SUISAppendTag(tags, "AD");
   tags = SUISAppendTag(tags, "CT");
   string note = StringFormat("BUY ADD score=%d progress>=%.2f body=%.2f regime=%s hour=%02d rr=%.2f",
                              76, SUIS_AddOnMinProgressR, bodyRatio, SUISRegimeLabel(regime), currentHour, SUIS_AddOnRR);
   SUISFillSignalMeta(signal, "AB", 76, tags, note);
   return(true);
  }


bool SUISSubmitSignal(const SUISSignal &signal)
  {
   g_trade.SetExpertMagicNumber(SUIS_MAGIC);
   g_trade.SetDeviationInPoints(20);
   g_trade.SetTypeFillingBySymbol(_Symbol);

   PrintFormat("SUIS ENTRY %s | engine=%s (%s) | score=%d grade=%s | tags=%s | lot=%.2f rr=%.2f sl=%.2f tp=%.2f | note=%s",
               signal.sell ? "SELL" : "BUY",
               SUISEngineLabel(signal.engineCode),
               signal.engineCode,
               signal.score,
               signal.grade,
               SUISTagsHuman(signal.tags),
               signal.lot,
               signal.rr,
               signal.stopLoss,
               signal.takeProfit,
               signal.note);

   if(signal.sell)
      return(g_trade.Sell(signal.lot, _Symbol, 0.0, signal.stopLoss, signal.takeProfit, signal.comment));
   return(g_trade.Buy(signal.lot, _Symbol, 0.0, signal.stopLoss, signal.takeProfit, signal.comment));
  }


void SUISManagePositions()
  {
   SUISRegime regime = SUISDetectRegime();
   double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   if(bid <= 0.0 || ask <= 0.0)
      return;
   double emaM5 = SUISIndicatorValue(g_emaM5, 1);
   double atrM5 = SUISIndicatorValue(g_atrM5, 1);

   g_trade.SetExpertMagicNumber(SUIS_MAGIC);
   g_trade.SetDeviationInPoints(20);
   g_trade.SetTypeFillingBySymbol(_Symbol);
   bool canSendTradeRequest = SUISTradeSessionLikelyOpen();

   for(int i = PositionsTotal() - 1; i >= 0; i--)
     {
      ulong ticket = PositionGetTicket(i);
      if(ticket == 0 || !PositionSelectByTicket(ticket))
         continue;
      if(PositionGetString(POSITION_SYMBOL) != _Symbol)
         continue;
      if((ulong)PositionGetInteger(POSITION_MAGIC) != SUIS_MAGIC)
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
      int barsHeld = (int)((TimeCurrent() - (datetime)PositionGetInteger(POSITION_TIME)) / PeriodSeconds(SUIS_EXEC_TF));
      double progressR = favorable / riskDistance;
      if(favorable >= (riskDistance * SUIS_BreakevenR))
        {
         double desiredSl = (type == POSITION_TYPE_BUY)
                            ? SUISNormalizePrice(openPrice + SUIS_BreakevenLockUsd)
                            : SUISNormalizePrice(openPrice - SUIS_BreakevenLockUsd);
         if(SUISStopsValid(type == POSITION_TYPE_SELL, openPrice, desiredSl, takeProfit))
           {
            if(type == POSITION_TYPE_BUY && stopLoss < desiredSl)
              {
               if(canSendTradeRequest && g_trade.PositionModify(ticket, desiredSl, takeProfit))
                  SUISExitActionLog("MOVE_SL_TO_BE", ticket, comment, "progress reached breakeven threshold", barsHeld, progressR, desiredSl, takeProfit);
              }
            if(type == POSITION_TYPE_SELL && stopLoss > desiredSl)
              {
               if(canSendTradeRequest && g_trade.PositionModify(ticket, desiredSl, takeProfit))
                  SUISExitActionLog("MOVE_SL_TO_BE", ticket, comment, "progress reached breakeven threshold", barsHeld, progressR, desiredSl, takeProfit);
              }
	           }
	        }

	      if(SUIS_EnableTPManager)
	        {
	         double initialVolume = SUISInitialVolume(ticket, currentVolume);
	         int tpStage = SUISTPStage(ticket);
	         if(tpStage < 1 && favorable >= (riskDistance * SUIS_TP1R))
	           {
	            bool stageAdvanced = false;
	            double closeVolume = SUISPartialCloseVolume(initialVolume, currentVolume);
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
	               double runnerRr = MathMax(SUIS_RunnerRR, takeProfit > 0.0 ? MathAbs(takeProfit - openPrice) / riskDistance : SUIS_RunnerRR);
	               double runnerTp = (type == POSITION_TYPE_BUY)
	                                 ? SUISNormalizePrice(openPrice + (riskDistance * runnerRr))
	                                 : SUISNormalizePrice(openPrice - (riskDistance * runnerRr));
	               double runnerSl = (type == POSITION_TYPE_BUY)
	                                 ? SUISNormalizePrice(MathMax(stopLoss, openPrice + SUIS_BreakevenLockUsd))
	                                 : SUISNormalizePrice(MathMin(stopLoss, openPrice - SUIS_BreakevenLockUsd));
			               if(SUISStopFitsMarket(type, currentPrice, runnerSl) &&
			                  SUISTakeProfitFitsMarket(type, currentPrice, runnerTp) &&
			                  SUISStopsValid(type == POSITION_TYPE_SELL, openPrice, runnerSl, runnerTp))
                            {
			                  if(canSendTradeRequest && g_trade.PositionModify(ticket, runnerSl, runnerTp))
                              SUISExitActionLog("TP1_RUNNER_SET", ticket, comment, "partial close done; runner TP/SL adjusted", barsHeld, progressR, runnerSl, runnerTp);
                            }
			               SUISSetTPStage(ticket, 1);
			               PrintFormat("SUIS TP1 | ticket=%I64u | %s | closedVolume=%.2f runnerRR=%.2f", ticket, comment, closeVolume, runnerRr);
		               continue;
		              }
		           }

	         if(SUISTPStage(ticket) >= 1 && atrM5 > 0.0 && favorable >= (riskDistance * SUIS_TrailStartR))
	           {
	            if(PositionSelectByTicket(ticket))
	              {
	               stopLoss = PositionGetDouble(POSITION_SL);
	               takeProfit = PositionGetDouble(POSITION_TP);
	               currentPrice = (type == POSITION_TYPE_BUY) ? SymbolInfoDouble(_Symbol, SYMBOL_BID) : SymbolInfoDouble(_Symbol, SYMBOL_ASK);
	              }
	            double trailDistance = atrM5 * SUIS_TrailATR;
	            double desiredSl = stopLoss;
	            if(type == POSITION_TYPE_BUY)
	               desiredSl = SUISNormalizePrice(MathMax(stopLoss, MathMax(openPrice + SUIS_TrailLockUsd, currentPrice - trailDistance)));
	            else
	               desiredSl = SUISNormalizePrice(MathMin(stopLoss, MathMin(openPrice - SUIS_TrailLockUsd, currentPrice + trailDistance)));
	            if(SUISStopFitsMarket(type, currentPrice, desiredSl) &&
	               SUISTakeProfitFitsMarket(type, currentPrice, takeProfit) &&
	               ((type == POSITION_TYPE_BUY && desiredSl > stopLoss) || (type == POSITION_TYPE_SELL && desiredSl < stopLoss)))
                 {
	               if(canSendTradeRequest && g_trade.PositionModify(ticket, desiredSl, takeProfit))
                     SUISExitActionLog("TRAIL_SL", ticket, comment, "ATR trailing after TP1", barsHeld, progressR, desiredSl, takeProfit);
                 }
	           }
	        }

	      bool weakOutsideBaseSell = SUIS_WeakOutsideSellQuickExit &&
	                                 type == POSITION_TYPE_SELL &&
	                                 StringFind(comment, "|BE|") >= 0 &&
	                                 StringFind(comment, "|WG|") >= 0 &&
	                                 StringFind(comment, "|XH|") >= 0;
	      if(weakOutsideBaseSell &&
	         barsHeld >= SUIS_WeakOutsideSellExitBars &&
	         PositionGetDouble(POSITION_PROFIT) < 0.0)
	        {
	         if(canSendTradeRequest && g_trade.PositionClose(ticket))
               SUISExitActionLog("WEAK_SELL_QUICK_EXIT", ticket, comment, "weak outside-session sell stayed negative", barsHeld, progressR, stopLoss, takeProfit);
	         continue;
	        }
	      if(SUIS_FastFailBuyGuard && type == POSITION_TYPE_BUY && barsHeld <= SUIS_FastFailBars && emaM5 > 0.0)
	        {
         bool scopeOk = !SUIS_FastFailPullbackOnly || (StringFind(comment, "|PB|") >= 0);
	         progressR = favorable / riskDistance;
         double failBuffer = (atrM5 > 0.0) ? (atrM5 * SUIS_HoldBufferATR) : 0.0;
         bool lostTrend = currentPrice <= (emaM5 + failBuffer);
	         if(scopeOk && lostTrend && progressR < SUIS_FastFailMinProgressR && PositionGetDouble(POSITION_PROFIT) < 0.0)
	           {
	            if(canSendTradeRequest && g_trade.PositionClose(ticket))
                  SUISExitActionLog("FAST_FAIL_CLOSE", ticket, comment, "buy lost EMA before progress", barsHeld, progressR, stopLoss, takeProfit);
	            continue;
	           }
        }
      bool regimeFlip = SUIS_CloseOnRegimeFlip &&
                        ((type == POSITION_TYPE_BUY && !SUISRegimeIsBull(regime)) ||
                         (type == POSITION_TYPE_SELL && !SUISRegimeIsBear(regime)));
      int maxHoldBars = SUIS_MaxHoldBars;
      if(type == POSITION_TYPE_BUY && StringFind(comment, "|SB|") >= 0)
         maxHoldBars = SUIS_BullSubMaxHoldBars;
      if(type == POSITION_TYPE_BUY && StringFind(comment, "|IB|") >= 0)
         maxHoldBars = SUIS_ImpulseMaxHoldBars;
      if(type == POSITION_TYPE_BUY && StringFind(comment, "|ZB|") >= 0)
         maxHoldBars = SUIS_ZoneMaxHoldBars;
      if(type == POSITION_TYPE_BUY && StringFind(comment, "|AB|") >= 0)
         maxHoldBars = SUIS_AddOnMaxHoldBars;
      if(type == POSITION_TYPE_SELL && StringFind(comment, "|SS|") >= 0)
         maxHoldBars = SUIS_BearSubMaxHoldBars;
      if(type == POSITION_TYPE_SELL && StringFind(comment, "|IS|") >= 0)
         maxHoldBars = SUIS_ImpulseMaxHoldBars;
      if(type == POSITION_TYPE_SELL && StringFind(comment, "|ZS|") >= 0)
         maxHoldBars = SUIS_ZoneMaxHoldBars;
      if(type == POSITION_TYPE_SELL && StringFind(comment, "|AS|") >= 0)
         maxHoldBars = SUIS_AddOnMaxHoldBars;
	      bool timeExpired = barsHeld >= maxHoldBars;
	      bool timeCloseProfitOnly = SUISEngineTimeCloseProfitOnly(type, comment);
	      bool canTimeClose = !timeCloseProfitOnly || PositionGetDouble(POSITION_PROFIT) > 0.0;
	      if(regimeFlip || (timeExpired && canTimeClose))
        {
         string closeReason = regimeFlip ? "regime flipped against position" : "max hold bars reached";
         if(canSendTradeRequest && g_trade.PositionClose(ticket))
            SUISExitActionLog(regimeFlip ? "REGIME_FLIP_CLOSE" : "TIME_CLOSE", ticket, comment, closeReason, barsHeld, progressR, stopLoss, takeProfit);
        }
     }
  }


bool SUISEvaluateEntries()
  {
   SUISRegime regime = SUISDetectRegime();
   if(regime == SUIS_REGIME_NONE)
      return(false);
   if(!SUISSpreadAllowed())
      return(false);
   if(!SUISRiskGuardAllowsTrading(false))
      return(false);
   string structuralReason = "";
   if(!SUISStructuralPriceGateAllowsTrading(structuralReason))
     {
      SUISRiskGuardLog("entry blocked: " + structuralReason);
      return(false);
     }
   SUISRegime entryRegime = regime;
   if(regime == SUIS_REGIME_MIXED)
     {
      if(!SUIS_EnableMixedMomentumEntries)
         return(false);
      entryRegime = SUISMixedBiasBull() ? SUIS_REGIME_WEAK_BULL : SUIS_REGIME_WEAK_BEAR;
     }
   if(SUISCountOpenPositions() >= SUISAllowedMaxPositions(entryRegime))
      return(false);

   MqlRates rates[];
   if(!SUISCopyRates(rates, 80))
      return(false);

   double atr = SUISIndicatorValue(g_atrM5, 1);
   double emaM5 = SUISIndicatorValue(g_emaM5, 1);
   if(atr <= 0.0 || emaM5 <= 0.0)
      return(false);

   SUISSignal signal;
   signal.valid = false;
   if(SUISRegimeIsBear(entryRegime))
     {
      if(SUISOppositePositionBlocks(true))
         return(false);
      if(SUISBuildBearSubSignal(rates, emaM5, atr, entryRegime, signal))
        {
         if(SUISSubmitSignal(signal, entryRegime))
            return(true);
        }
      if(SUISBuildImpulsePullbackSignal(rates, emaM5, atr, entryRegime, true, signal))
        {
         if(SUISSubmitSignal(signal, entryRegime))
            return(true);
        }
      if(SUISBuildZoneRetestSignal(rates, emaM5, atr, entryRegime, true, signal))
        {
         if(SUISSubmitSignal(signal, entryRegime))
            return(true);
        }
      if(SUISBuildAddOnSignal(rates, emaM5, atr, entryRegime, true, signal))
        {
         if(SUISSubmitSignal(signal, entryRegime))
            return(true);
        }
      if(SUISBuildSellSignal(rates, emaM5, atr, entryRegime, signal))
        {
         if(SUISSubmitSignal(signal, entryRegime))
            return(true);
        }
     }
   else if(SUISRegimeIsBull(entryRegime))
     {
      if(SUISOppositePositionBlocks(false))
         return(false);
      if(SUISBuildBullSubSignal(rates, emaM5, atr, entryRegime, signal))
        {
         if(SUISSubmitSignal(signal, entryRegime))
            return(true);
        }
      if(SUISBuildImpulsePullbackSignal(rates, emaM5, atr, entryRegime, false, signal))
        {
         if(SUISSubmitSignal(signal, entryRegime))
            return(true);
        }
      if(SUISBuildZoneRetestSignal(rates, emaM5, atr, entryRegime, false, signal))
        {
         if(SUISSubmitSignal(signal, entryRegime))
            return(true);
        }
      if(SUISBuildAddOnSignal(rates, emaM5, atr, entryRegime, false, signal))
        {
         if(SUISSubmitSignal(signal, entryRegime))
            return(true);
        }
      if(SUISBuildBuySignal(rates, emaM5, atr, entryRegime, signal))
        {
         if(SUISSubmitSignal(signal, entryRegime))
            return(true);
        }
     }

   return(false);
  }


int OnInit()
  {
   if(_Period != SUIS_EXEC_TF)
     {
      Print("SuisM5_v2 requires M5.");
      return(INIT_PARAMETERS_INCORRECT);
     }

   SUISClearState();
   SUISResetDailyGuardIfNeeded();
   SUISResetWeeklyGuardIfNeeded();
   g_accountStartEquity = AccountInfoDouble(ACCOUNT_EQUITY);
   g_accountHighEquity = g_accountStartEquity;
   g_equityCircuitStopped = false;

   g_trade.SetExpertMagicNumber(SUIS_MAGIC);
   g_trade.SetDeviationInPoints(20);
   g_trade.SetTypeFillingBySymbol(_Symbol);

   g_emaFastH1 = iMA(_Symbol, PERIOD_H1, SUIS_H1FastEMA, 0, MODE_EMA, PRICE_CLOSE);
   g_emaSlowH1 = iMA(_Symbol, PERIOD_H1, SUIS_H1SlowEMA, 0, MODE_EMA, PRICE_CLOSE);
   g_emaFastH4 = iMA(_Symbol, PERIOD_H4, SUIS_H4FastEMA, 0, MODE_EMA, PRICE_CLOSE);
   g_emaSlowH4 = iMA(_Symbol, PERIOD_H4, SUIS_H4SlowEMA, 0, MODE_EMA, PRICE_CLOSE);
   g_adxH1 = iADX(_Symbol, PERIOD_H1, SUIS_H1ADXPeriod);
   g_atrH1 = iATR(_Symbol, PERIOD_H1, SUIS_H1ATRPeriod);
   g_emaFastD1 = iMA(_Symbol, PERIOD_D1, SUIS_D1FastEMA, 0, MODE_EMA, PRICE_CLOSE);
   g_emaSlowD1 = iMA(_Symbol, PERIOD_D1, SUIS_D1SlowEMA, 0, MODE_EMA, PRICE_CLOSE);
   g_atrD1 = iATR(_Symbol, PERIOD_D1, SUIS_D1ATRPeriod);
   g_emaM5 = iMA(_Symbol, SUIS_EXEC_TF, SUIS_M5TrendEMA, 0, MODE_EMA, PRICE_CLOSE);
   g_atrM5 = iATR(_Symbol, SUIS_EXEC_TF, SUIS_M5ATRPeriod);

   if(g_emaFastH1 == INVALID_HANDLE || g_emaSlowH1 == INVALID_HANDLE ||
      g_emaFastH4 == INVALID_HANDLE || g_emaSlowH4 == INVALID_HANDLE ||
      g_adxH1 == INVALID_HANDLE || g_atrH1 == INVALID_HANDLE ||
      g_emaFastD1 == INVALID_HANDLE || g_emaSlowD1 == INVALID_HANDLE || g_atrD1 == INVALID_HANDLE ||
      g_emaM5 == INVALID_HANDLE || g_atrM5 == INVALID_HANDLE)
     {
      Print("SuisM5_v2 failed to create indicators.");
      return(INIT_FAILED);
     }

   PrintFormat("SuisM5_v2 SUIS AGGRESSIVE FREQUENCY PROFILE Suis v2 | symbol=%s tf=M5 risk=%.2f buy=%s sell=%s sellRisk=%.2f weakSellRisk=%.2f sellSession=%02d-%02d maxPos=%d dailyLoss=%.2f closeOnStop=%s weeklyLoss=%.2f equityCircuit=%.2f macro=%s macroBearScore=%d priceGate=%s minD1Close=%.2f buyBlocks BO=%s PB=%s ZB=%s sellBlocks BO=%s ZS=all overextensionD1=%.2f",
               _Symbol,
               SUIS_RiskPercent,
               SUIS_EnableBuys ? "true" : "false",
               SUIS_EnableSells ? "true" : "false",
               SUIS_SellRiskMultiplier,
               SUIS_WeakSellRiskMultiplier,
               SUIS_SellSessionStartHour,
               SUIS_SellSessionEndHour,
               SUIS_MaxPositions,
               SUIS_DailyMaxLossPct,
               (SUIS_DailyClosePositionsOnStop || SUIS_ClosePositionsOnSafetyStop) ? "true" : "false",
               SUIS_WeeklyMaxLossPct,
               SUIS_MaxEquityDrawdownPct,
               SUIS_EnableMacroRegimeSwitch ? "on" : "off",
               SUIS_MacroBearMinScore,
               SUIS_EnableStructuralPriceGate ? "on" : "off",
               SUIS_MinD1CloseForTrading,
               SUIS_BlockBuyBreakHours,
               SUIS_BlockBuyPullbackHours,
               SUIS_BlockBuyZoneHours,
               SUIS_BlockSellBreakHours,
               SUIS_MaxBuyD1FastDistanceATR);

   return(INIT_SUCCEEDED);
  }


void OnDeinit(const int reason)
  {
   SUISClearState();

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
   if(g_emaFastD1 != INVALID_HANDLE)
      IndicatorRelease(g_emaFastD1);
   if(g_emaSlowD1 != INVALID_HANDLE)
      IndicatorRelease(g_emaSlowD1);
   if(g_atrD1 != INVALID_HANDLE)
      IndicatorRelease(g_atrD1);
   if(g_emaM5 != INVALID_HANDLE)
      IndicatorRelease(g_emaM5);
   if(g_atrM5 != INVALID_HANDLE)
      IndicatorRelease(g_atrM5);
  }


void OnTick()
  {
   SUISRiskGuardAllowsTrading(true);
   SUISManagePositions();
   if(!SUISNewBar())
      return;
   bool entered = SUISEvaluateEntries();
   SUISStatusLog(entered);
  }


string SUISEntryCommentForPosition(const long positionId)
  {
   if(positionId == 0)
      return("");

   HistorySelect(0, TimeCurrent());
   for(int i = HistoryDealsTotal() - 1; i >= 0; i--)
     {
      ulong ticket = HistoryDealGetTicket(i);
      if(ticket == 0 || !HistoryDealSelect(ticket))
         continue;
      if(HistoryDealGetString(ticket, DEAL_SYMBOL) != _Symbol)
         continue;
      if((ulong)HistoryDealGetInteger(ticket, DEAL_MAGIC) != SUIS_MAGIC)
         continue;
      if((long)HistoryDealGetInteger(ticket, DEAL_POSITION_ID) != positionId)
         continue;
      long entry = HistoryDealGetInteger(ticket, DEAL_ENTRY);
      if(entry == DEAL_ENTRY_IN || entry == DEAL_ENTRY_INOUT)
         return(HistoryDealGetString(ticket, DEAL_COMMENT));
     }
   return("");
  }


int SUISScoreFromComment(const string comment)
  {
   int marker = StringFind(comment, "|S");
   if(marker < 0)
      return(0);

   string text = "";
   for(int i = marker + 2; i < StringLen(comment); i++)
     {
      ushort ch = StringGetCharacter(comment, i);
      if(ch < '0' || ch > '9')
         break;
      text += ShortToString(ch);
     }
   if(text == "")
      return(0);
   return((int)StringToInteger(text));
  }


void SUISRecordEngineFailGuardLoss(const string entryComment, const double pnl)
  {
   if(!SUIS_EnableEngineFailGuard || pnl >= -0.01)
      return;

   int score = SUISScoreFromComment(entryComment);
   if(score < SUIS_EngineFailMinScore)
      return;

   if(StringFind(entryComment, "|ZB|") >= 0 || StringFind(entryComment, "BUY_ZONE") >= 0)
     {
      g_dailyBuyZoneHighScoreLosses++;
      if(SUIS_BuyZoneDailyLossLimit > 0 && g_dailyBuyZoneHighScoreLosses >= SUIS_BuyZoneDailyLossLimit)
        {
         g_dailyBuyZoneStopped = true;
         SUISRiskGuardLog(StringFormat("BUY_ZONE paused after high-score losses=%d score=%d pnl=%.2f",
                                      g_dailyBuyZoneHighScoreLosses, score, pnl), true);
        }
     }
   else if(StringFind(entryComment, "|PB|") >= 0 || StringFind(entryComment, "BUY_PULLBACK") >= 0)
     {
      g_dailyBuyPullbackHighScoreLosses++;
      if(SUIS_BuyPullbackDailyLossLimit > 0 && g_dailyBuyPullbackHighScoreLosses >= SUIS_BuyPullbackDailyLossLimit)
        {
         g_dailyBuyPullbackStopped = true;
         SUISRiskGuardLog(StringFormat("BUY_PULLBACK paused after high-score losses=%d score=%d pnl=%.2f",
                                      g_dailyBuyPullbackHighScoreLosses, score, pnl), true);
        }
     }
  }


void OnTradeTransaction(const MqlTradeTransaction &trans,
                        const MqlTradeRequest &request,
                        const MqlTradeResult &result)
  {
   if(trans.type != TRADE_TRANSACTION_DEAL_ADD)
      return;
   if(!HistoryDealSelect(trans.deal))
      return;
   if(HistoryDealGetString(trans.deal, DEAL_SYMBOL) != _Symbol)
      return;
   if((ulong)HistoryDealGetInteger(trans.deal, DEAL_MAGIC) != SUIS_MAGIC)
      return;

   long entry = HistoryDealGetInteger(trans.deal, DEAL_ENTRY);
   if(entry != DEAL_ENTRY_OUT && entry != DEAL_ENTRY_OUT_BY && entry != DEAL_ENTRY_INOUT)
      return;

   double pnl = HistoryDealGetDouble(trans.deal, DEAL_PROFIT) +
                HistoryDealGetDouble(trans.deal, DEAL_SWAP) +
                HistoryDealGetDouble(trans.deal, DEAL_COMMISSION);
   string entryComment = SUISEntryCommentForPosition((long)HistoryDealGetInteger(trans.deal, DEAL_POSITION_ID));
   SUISRecordEngineFailGuardLoss(entryComment, pnl);

   if(SUIS_MaxConsecutiveLosses <= 0 || SUIS_LossCooldownMinutes <= 0)
      return;
   if(pnl < -0.01)
      g_consecutiveLosses++;
   else if(pnl > 0.01)
      g_consecutiveLosses = 0;

   if(g_consecutiveLosses >= SUIS_MaxConsecutiveLosses)
     {
      g_lossCooldownUntil = TimeCurrent() + (SUIS_LossCooldownMinutes * 60);
      SUISRiskGuardLog(StringFormat("loss streak cooldown start losses=%d pnl=%.2f", g_consecutiveLosses, pnl), true);
      g_consecutiveLosses = 0;
     }
  }
