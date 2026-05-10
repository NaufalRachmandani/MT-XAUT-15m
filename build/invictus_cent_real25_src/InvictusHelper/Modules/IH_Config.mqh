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

enum ENUM_IH_GRADE
{
   IH_GRADE_A,
   IH_GRADE_B,
   IH_GRADE_REJECT
};

enum ENUM_IH_RESULT
{
   IH_RESULT_PENDING,     // Limit order not yet filled
   IH_RESULT_ACTIVE,      // Filled, waiting for TP/SL
   IH_RESULT_TP_HIT,      // TP reached
   IH_RESULT_SL_HIT,      // SL reached
   IH_RESULT_EXPIRED      // Limit order expired (never filled)
};

//=== TF-Dependent Parameters (set at runtime by IH_InitParams) ===
int    IH_SwingLookback;
double IH_MinBreakATR;
double IH_MinBodyRatio;
int    IH_MaxBOSBarsBack;
int    IH_ZoneSearchWindow;
double IH_MaxZoneRange;
int    IH_MinScoreA;
int    IH_MinScoreB;
int    IH_GoldBuyBonus;
double IH_MinSLDollar;
double IH_MaxSLDollar;
double IH_TP1_RR;
double IH_ATRBufferSL;
int    IH_PendingExpiryBars;
double IH_EntryBodyRatio;     // entry at X% of body B (0.5=50%, 0.3=30%)

void IH_InitParams()
{
   if(_Period <= PERIOD_M15)
   {
      //=== M15 SCALPING — QUALITY FOCUSED ===
      IH_SwingLookback    = 2;
      IH_MinBreakATR      = 0.30;    // break harus cukup signifikan
      IH_MinBodyRatio     = 0.45;    // BOS candle harus punya body solid
      IH_MaxBOSBarsBack   = 60;      // 60 bar M15 = 15 jam
      IH_ZoneSearchWindow = 8;       // 8 bar M15 = 2 jam
      IH_MaxZoneRange     = 20.0;    // zone M15 harus compact ($20 max)
      IH_MinScoreA        = 80;      // hanya signal kuat
      IH_MinScoreB        = 65;
      IH_GoldBuyBonus     = 10;
      IH_MinSLDollar      = 25.0;
      IH_MaxSLDollar      = 25.0;
      IH_TP1_RR           = 1.5;     // RR 1:1.5
      IH_ATRBufferSL      = 0.5;
      IH_PendingExpiryBars = 8;      // 8 bar = 2 jam (jangan terlalu lama)
      IH_EntryBodyRatio   = 0.50;    // entry di 50% body B
   }
   else
   {
      //=== H4 DEFAULT (sama persis dengan V1.0) ===
      IH_SwingLookback    = 2;
      IH_MinBreakATR      = 0.35;
      IH_MinBodyRatio     = 0.50;
      IH_MaxBOSBarsBack   = 50;
      IH_ZoneSearchWindow = 6;
      IH_MaxZoneRange     = 100.0;
      IH_MinScoreA        = 80;
      IH_MinScoreB        = 65;
      IH_GoldBuyBonus     = 10;
      IH_MinSLDollar      = 30.0;
      IH_MaxSLDollar      = 85.0;
      IH_TP1_RR           = 1.5;     // RR 1:1.5
      IH_ATRBufferSL      = 1.0;
      IH_PendingExpiryBars = 2;
      IH_EntryBodyRatio   = 0.50;   // entry di 50% body B (EA default)
   }

   Print("[IH] Params loaded for ", EnumToString(_Period),
         " | SL: $", IH_MinSLDollar, "-$", IH_MaxSLDollar,
         " | BOS: ", IH_MaxBOSBarsBack, " bars | Zone: ", IH_ZoneSearchWindow, " bars");
}

//=== Session Filter — hidden from settings ===
// input group "══════ Session Filter ══════"
// input bool     IH_FilterSessions      = true;   // Only show signals during active sessions
// input int      IH_AsiaStart           = 1;      // Asia session start (server hour)
// input int      IH_AsiaEnd             = 4;      // Asia session end
// input int      IH_LondonStart         = 9;      // London session start
// input int      IH_LondonEnd           = 12;     // London session end
// input int      IH_NYStart             = 14;     // NY session start
// input int      IH_NYEnd               = 17;     // NY session end
#define IH_FilterSessions true
#define IH_AsiaStart      1
#define IH_AsiaEnd        4
#define IH_LondonStart    9
#define IH_LondonEnd      12
#define IH_NYStart        14
#define IH_NYEnd          17

//=== Display Options ===
input group "══════ Display Options ══════"
input int      IH_ScanYears           = 1;      // Scan period in years
input bool     IH_ShowZones           = false;   // Draw S/D zone rectangles
input bool     IH_ShowBOS             = true;    // Draw BOS markers
input bool     IH_ShowFVG             = true;    // Draw Fair Value Gaps
input bool     IH_ShowSessions        = false;   // Draw session backgrounds
input bool     IH_ShowDashboard       = true;    // Draw info dashboard
input bool     IH_ShowGradeB          = false;   // Also show Grade B signals (dimmed)
input int      IH_SignalLabelSize     = 8;       // Label font size
input int      IH_TableMaxRows        = 5;       // Signal table rows (max 10)

//=== Show/Hide Controls ===
input group "══════ Show/Hide Controls ══════"
input bool     IH_ShowExpiredSignal      = true;    // Show expired signals
input bool     IH_ShowBuySignal          = true;    // Show buy signals
input bool     IH_ShowSellSignal         = true;    // Show sell signals
input bool     IH_ShowLineTP             = false;   // Show take profit line
input bool     IH_ShowLineSL             = false;   // Show stop loss line
input bool     IH_ShowLabelEntry         = true;    // Show entry/result label
input bool     IH_ShowLabelTP            = true;    // Show take profit label
input bool     IH_ShowLabelSL            = true;    // Show stop loss label
input bool     IH_ShowBOSImpulsive       = true;    // Show BOS impulsive highlight
input bool     IH_ShowBOSCorrective      = true;    // Show BOS corrective highlight
input bool     IH_ShowSwingBullish       = false;   // Show swing H/L bullish background
input bool     IH_ShowSwingBearish       = false;   // Show swing H/L bearish background
input bool     IH_ShowArrowBuy           = true;    // Show buy entry arrow
input bool     IH_ShowArrowSell          = true;    // Show sell entry arrow
input bool     IH_ShowTableSignal        = true;    // Show signal table
input bool     IH_ShowAllBOS            = true;    // Show all BOS (without signal)

//--- Internal (not shown in settings)
#define IH_BOSBoxPadding 30

//=== Colors — hidden from settings ===
// input group "══════ Colors ══════"
// input color    IH_DemandZoneColor     = clrDodgerBlue;    // Demand zone (buy)
// input color    IH_SupplyZoneColor     = clrOrange;        // Supply zone (sell)
// input color    IH_EntryLineColor      = clrWhite;         // Entry level line
// input color    IH_SLLineColor         = clrRed;           // Stop Loss line
// input color    IH_TPLineColor         = clrLime;          // Take Profit line
// input color    IH_WinColor            = clrLime;          // TP hit result
// input color    IH_LossColor           = clrRed;           // SL hit result
// input color    IH_BOSImpulsiveColor   = clrDeepSkyBlue;   // BOS impulsive
// input color    IH_BOSCorrectiveColor  = clrGold;          // BOS corrective
// input color    IH_FVGBullColor        = clrRoyalBlue;     // Bullish FVG
// input color    IH_FVGBearColor        = clrIndianRed;     // Bearish FVG
// input color    IH_AsiaColor           = C'20,30,60';      // Asia session bg
// input color    IH_LondonColor         = C'15,50,25';      // London session bg
// input color    IH_NYColor             = C'55,45,10';      // NY session bg
// input color    IH_GradeBColor         = clrGray;          // Grade B signal color
// input color    IH_ExpiredColor        = clrDarkGray;      // Expired order color
#define IH_DemandZoneColor    clrDodgerBlue
#define IH_SupplyZoneColor    clrOrange
#define IH_EntryLineColor     clrWhite
#define IH_SLLineColor        clrRed
#define IH_TPLineColor        clrLime
#define IH_WinColor           clrLime
#define IH_LossColor          clrRed
#define IH_BOSImpulsiveColor  clrDeepSkyBlue
#define IH_BOSCorrectiveColor clrGold
#define IH_FVGBullColor       clrRoyalBlue
#define IH_FVGBearColor       clrIndianRed
#define IH_AsiaColor          C'20,30,60'
#define IH_LondonColor        C'15,50,25'
#define IH_NYColor            C'55,45,10'
#define IH_GradeBColor        clrGray
#define IH_ExpiredColor       clrDarkGray

//--- Prefix for all chart objects
#define IH_PREFIX "IH_"

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

//--- Signal structure (the main output)
struct IH_Signal
{
   //--- Identity
   int            id;
   datetime       signalTime;       // time of signal bar
   int            signalBar;        // bar index when detected

   //--- Direction & scoring
   bool           isBuy;
   int            score;
   ENUM_IH_GRADE  grade;
   string         breakdown;

   //--- Trade levels
   double         entryPrice;
   double         slPrice;
   double         tp1Price;
   double         slDistance;        // in dollars
   double         tp1Distance;      // in dollars

   //--- Zone info
   double         zoneHigh;
   double         zoneLow;
   datetime       zoneTime;         // Candle B open time

   //--- BOS info
   ENUM_IH_BOS_QUALITY bosQuality;
   int            bosBar;          // bar index of BOS candle (snapshot, may shift)
   datetime       bosTime;         // BOS candle time (stable for drawing)
   double         bosHigh;         // BOS candle high
   double         bosLow;          // BOS candle low
   double         swingPrice;      // swing level that was broken
   datetime       swingTime;       // swing bar time (for drawing)
   bool           hasFVG;
   bool           hasSweep;
   bool           hasRetest;

   //--- Trade result
   ENUM_IH_RESULT result;
   datetime       fillTime;         // when limit order filled
   int            fillBar;
   datetime       resolveTime;      // when TP/SL hit
   int            resolveBar;
   double         profitDollar;     // per 0.01 lot

   //--- Drawing state
   bool           drawn;            // already has chart objects
};

#endif
