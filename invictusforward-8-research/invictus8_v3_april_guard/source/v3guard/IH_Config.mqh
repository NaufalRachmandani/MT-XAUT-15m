//+------------------------------------------------------------------+
//|                                                   IH_Config.mqh  |
//|                       InvictusHelper — Config, Structs, Enums     |
//+------------------------------------------------------------------+
#ifndef IH_CONFIG_MQH
#define IH_CONFIG_MQH

//--- Enumerations (matching EA)
enum ENUM_IH_BIAS
{
   IH_BIAS_BULLISH,
   IH_BIAS_BEARISH,
   IH_BIAS_NEUTRAL
};

enum ENUM_IH_BOS_QUALITY
{
   IH_BOS_IMPULSIVE,
   IH_BOS_CORRECTIVE,
   IH_BOS_NONE
};

//=== TF-Dependent Parameters (set at runtime by IH_InitParams) ===
int    IH_SwingLookback;
double IH_MinBreakATR;
double IH_MinBodyRatio;
int    IH_MaxBOSBarsBack;
int    IH_ZoneSearchWindow;
double IH_MaxZoneRange;
int    IH_MinScoreA;
int    IH_GoldBuyBonus;
double IH_MinSLDollar;    // set from input BT_MinSLDollar
double IH_MaxSLDollar;    // set from input BT_MaxSLDollar
double IH_TP1_RR;
double IH_ATRBufferSL;
int    IH_PendingExpiryBars;
double IH_EntryBodyRatio;     // entry at X% of body B (0.5=50%, 0.3=30%)

void IH_InitParams()
{
   //=== M15 SCALPING — QUALITY FOCUSED ===
   IH_SwingLookback    = 2;
   IH_MinBreakATR      = 0.30;    // break harus cukup signifikan
   IH_MinBodyRatio     = 0.45;    // BOS candle harus punya body solid
   IH_MaxBOSBarsBack   = 60;      // 60 bar M15 = 15 jam
   IH_ZoneSearchWindow = 8;       // 8 bar M15 = 2 jam
   IH_MaxZoneRange     = 20.0;    // zone M15 harus compact ($20 max)
   IH_MinScoreA        = 80;      // hanya signal kuat
   IH_GoldBuyBonus     = 10;
   IH_MinSLDollar      = 25.0;
   IH_MaxSLDollar      = 30.0;
   IH_TP1_RR           = 1.5;
   IH_ATRBufferSL      = 0.5;
   IH_PendingExpiryBars = 8;      // 8 bar = 2 jam (jangan terlalu lama)
   IH_EntryBodyRatio   = 0.50;    // entry di 50% body B

   Print("[IH] Params loaded for M15",
         " | SL: $", IH_MinSLDollar, "-$", IH_MaxSLDollar,
         " | BOS: ", IH_MaxBOSBarsBack, " bars | Zone: ", IH_ZoneSearchWindow, " bars");
}

//=== Reversal Close (Iter 2a) ===
input group "══════ Reversal Close ══════"
input bool   EnableReversalClose = true;    // Close BUY on strong bearish reversal

//=== Advanced Sideways Detection (Iter 3) ===
input group "══════ Sideways Detection ══════"
input int    SidewaysMinMethods    = 4;     // Min methods to confirm sideways (of 8 max weighted)
input int    BB_Period             = 20;    // Bollinger Band period
input double BB_Deviation          = 2.0;   // Bollinger Band deviation
input double KC_ATRMultiplier      = 1.5;   // Keltner Channel ATR multiplier
input int    MTF_H1_ADX_Max        = 25;    // H1 ADX max for sideways
input int    MTF_H4_ADX_Max        = 22;    // H4 ADX max for sideways
input double ATR_CompressionRatio  = 0.65;  // ATR14 < X * ATR50 = compressed
input double BBWidth_RelativeRatio = 0.70;  // BB width < X * avg = narrow
input double PriceRange_ATRMult    = 2.3;   // 30-bar range < X * ATR = contained

//=== Range Bounce (Iter 5) ===
input group "══════ Range Bounce ══════"
input double RangeBounce_LotMult     = 0.15;   // Lot = X * trending lot (conservative)
input int    RangeBounce_MaxBuy      = 1;      // Max simultaneous BUY bounce
input int    RangeBounce_MaxSell     = 0;      // Max simultaneous SELL bounce (0=disabled)
input double RangeBounce_EntryPct    = 0.25;   // Entry zone % from edge (lower/upper 25%)
input int    RangeBounce_MaxEntriesPerRange = 2; // Max range entries per detected range/day

//=== Research Guardrails (Forward-8 May 2026 audit) ===
input group "══════ Research Guardrails ══════"
input bool   Guard_EnableBadHourFilter = true; // Block hours with persistent negative expectancy
input bool   Guard_BlockHour04         = true; // YTD: weak hour
input bool   Guard_BlockHour05         = true; // YTD/last week: worst hour
input bool   Guard_BlockHour10         = true; // YTD/last week: weak hour
input bool   Guard_BlockHour11         = true; // YTD: weak hour
input bool   Guard_EnableTrendFillHourFilter = true; // Cancel/avoid Trend orders in loss-cluster hours
input bool   Guard_TR_BlockHour00      = true;
input bool   Guard_TR_BlockHour01      = true;
input bool   Guard_TR_BlockHour04      = true;
input bool   Guard_TR_BlockHour05      = true;
input bool   Guard_TR_BlockHour10      = true;
input bool   Guard_TR_BlockHour11      = true;
input bool   Guard_TR_BlockHour19      = true;
input bool   Guard_TR_BlockHour20      = true;
input bool   Guard_TR_BlockHour22      = true;
input bool   Guard_TR_BlockHour23      = true;
input int    Guard_TrendMinScoreAdd    = 10;   // Raise Trend score threshold; 10 means 90/100
input bool   Guard_AllowTrendCorrective = true; // False = IMP-only Trend entries
input int    Guard_TrendLossCooldownBars = 8;  // Extended cooldown once loss streak triggers
input int    Guard_TrendLossCooldownTrigger = 2;
input int    Guard_MaxTrendDailyLossCount = 3; // Stricter than V1/V2 default 5; 0 disables
input bool   Guard_EnableDropCatcherHourFilter = true; // Separate DC leak filter
input bool   Guard_DC_BlockHour00      = true;
input bool   Guard_DC_BlockHour01      = true;
input bool   Guard_DC_BlockHour10      = true;
input bool   Guard_DC_BlockHour23      = true;
input int    Guard_MaxTrendPosLowBalance  = 2; // <= 20k balance
input int    Guard_MaxTrendPosMidBalance  = 3; // <= 50k balance
input int    Guard_MaxTrendPosHighBalance = 2; // > 50k balance

//=== Drop Catcher SELL (Iter 4) ===
input group "══════ Drop Catcher SELL ══════"
input bool   EnableDropCatcher       = true;   // Enable SELL drop catcher
input double Trend_LotMult           = 1.0;    // Trend lot multiplier for V3 guard tests
input double DropCatcher_BodyATR     = 1.8;    // Bearish body > X * ATR
input double DropCatcher_MinBodyDlr  = 12.0;   // Minimum body size ($) — absolute floor
input double DropCatcher_VolMult     = 1.3;    // Tick volume > X * avg 20-bar
input double DropCatcher_MaxATR      = 15.0;   // Skip when ATR > X (extreme volatility)
input double DropCatcher_SL_ATR      = 2.0;    // SL = X * ATR (wider to survive noise)
input double DropCatcher_RR          = 3.0;    // RR target (3:1)
input double DropCatcher_LotMult     = 0.10;   // Lot = X * normal trending lot
input double DropCatcher_TrailATR    = 1.0;    // Trail SL = ask + X * ATR

//--- BOS Info structure
struct IH_BOSInfo
{
   ENUM_IH_BOS_QUALITY quality;
   double   swingPrice;
   double   breakPrice;
   double   breakDist;
   int      swingBar;        // bar index of swing point
   int      bosBar;          // bar index of break candle (relative to refBar)
   bool     hasFVG;
   double   fvgHigh;
   double   fvgLow;
   bool     hasSweep;
   bool     hasRetest;
};

//--- S/D Zone structure
struct IH_Zone
{
   double   priceHigh;
   double   priceLow;
   double   entryPrice;      // 50% body B
   int      candleBBar;      // bar index of Candle B (absolute)
   datetime timeCreated;
   int      testCount;
   bool     isBullish;
   bool     isValid;
};

#endif
