//+------------------------------------------------------------------+
//|                                                 IH_Detector.mqh  |
//|                  InvictusHelper — BOS, Zone, FVG Detection        |
//|          All detection relative to a reference bar (refBar)       |
//+------------------------------------------------------------------+
#ifndef IH_DETECTOR_MQH
#define IH_DETECTOR_MQH

#include "IH_Config.mqh"

//+------------------------------------------------------------------+
//| Class: CIH_Detector                                              |
//+------------------------------------------------------------------+
class CIH_Detector
{
private:
   string   m_symbol;
   int      m_atrHandleH4;

   //--- Helpers
   double   CandleBody(double o, double c)           { return MathAbs(c - o); }
   double   CandleRange(double h, double l)          { return h - l; }
   double   UpperWick(double h, double o, double c)  { return h - MathMax(o, c); }
   double   LowerWick(double l, double o, double c)  { return MathMin(o, c) - l; }
   bool     IsBull(double o, double c)               { return c > o; }
   bool     IsBear(double o, double c)               { return c < o; }

public:
                  CIH_Detector() : m_atrHandleH4(INVALID_HANDLE) {}
                 ~CIH_Detector() { Deinit(); }

   bool           Init(string symbol);
   void           Deinit();
   double         GetATR(int shift);

   //--- Bias detection at historical bar
   ENUM_IH_BIAS   DetectBias(int refBar,
                              const double &high[],
                              const double &low[],
                              const double &close[],
                              int totalBars);

   //--- Swing detection
   bool           FindSwingHigh(int refBar, int lookback, int searchBars,
                                const double &high[], int totalBars,
                                double &price, int &bar);
   bool           FindSwingLow(int refBar, int lookback, int searchBars,
                               const double &low[], int totalBars,
                               double &price, int &bar);

   //--- BOS detection at refBar
   IH_BOSInfo     AnalyzeBOS(int refBar, bool lookForBullish,
                              const double &open[], const double &high[],
                              const double &low[], const double &close[],
                              int totalBars);

   //--- BOS classification
   ENUM_IH_BOS_QUALITY ClassifyBOS(int bosBarAbs, bool isBullish,
                                     const double &open[], const double &high[],
                                     const double &low[], const double &close[],
                                     int totalBars);

   //--- FVG detection
   bool           DetectFVG(int bosBarAbs, bool isBullish,
                            const double &high[], const double &low[],
                            int totalBars,
                            double &fvgH, double &fvgL);

   //--- Liquidity sweep
   bool           DetectSweep(int bosBarAbs, double swingPrice, bool isBullish,
                              const double &high[], const double &low[],
                              const double &close[], int totalBars);

   //--- Retest detection
   bool           DetectRetest(int bosBarAbs, double swingPrice, bool isBullish,
                               const double &open[], const double &high[],
                               const double &low[], const double &close[],
                               int refBar, int totalBars);

   //--- Zone detection (Candle A/B)
   bool           DetectZone(int refBar, bool lookForBullish,
                             const double &open[], const double &high[],
                             const double &low[], const double &close[],
                             const datetime &time[], int totalBars,
                             IH_Zone &zone);

   //--- Session check
   bool           IsActiveSession(datetime t);
};

//+------------------------------------------------------------------+
bool CIH_Detector::Init(string symbol)
{
   m_symbol = symbol;
   m_atrHandleH4 = iATR(symbol, _Period, 14);
   if(m_atrHandleH4 == INVALID_HANDLE)
   {
      Print("[IH] Failed to create ATR handle");
      return false;
   }
   return true;
}

//+------------------------------------------------------------------+
void CIH_Detector::Deinit()
{
   if(m_atrHandleH4 != INVALID_HANDLE)
   {
      IndicatorRelease(m_atrHandleH4);
      m_atrHandleH4 = INVALID_HANDLE;
   }
}

//+------------------------------------------------------------------+
double CIH_Detector::GetATR(int shift)
{
   double buf[];
   if(CopyBuffer(m_atrHandleH4, 0, shift, 1, buf) <= 0) return 0;
   return buf[0];
}

//+------------------------------------------------------------------+
//| Bias at historical bar using H4 trend (HH/HL or LL/LH count)    |
//+------------------------------------------------------------------+
ENUM_IH_BIAS CIH_Detector::DetectBias(int refBar,
                                        const double &high[],
                                        const double &low[],
                                        const double &close[],
                                        int totalBars)
{
   //--- Need 10 bars behind refBar
   if(refBar + 10 >= totalBars) return IH_BIAS_BULLISH; // default bullish for gold

   //--- Count higher-highs (bullish) and lower-lows (bearish) in 9 bars
   int hhCount = 0, llCount = 0;
   for(int k = refBar + 1; k < refBar + 10 && k + 1 < totalBars; k++)
   {
      if(high[k] > high[k + 1]) hhCount++;
      if(low[k] < low[k + 1])   llCount++;
   }

   if(llCount >= 6) return IH_BIAS_BEARISH;
   if(hhCount >= 5) return IH_BIAS_BULLISH;
   return IH_BIAS_BULLISH; // default bullish for gold
}

//+------------------------------------------------------------------+
//| Find swing high using fractal method (relative to refBar)        |
//| All indices are absolute (AsSeries: 0=newest)                    |
//+------------------------------------------------------------------+
bool CIH_Detector::FindSwingHigh(int refBar, int lookback, int searchBars,
                                  const double &high[], int totalBars,
                                  double &price, int &bar)
{
   int start = refBar + lookback + 1;
   int end   = refBar + lookback + searchBars;

   for(int i = start; i <= end && i + lookback < totalBars; i++)
   {
      bool isSwing = true;

      //--- Left side: bars closer to current (lower index)
      for(int j = 1; j <= lookback; j++)
      {
         if(i - j < 0 || high[i - j] >= high[i]) { isSwing = false; break; }
      }
      if(!isSwing) continue;

      //--- Right side: bars further from current (higher index)
      for(int j = 1; j <= lookback; j++)
      {
         if(i + j >= totalBars || high[i + j] >= high[i]) { isSwing = false; break; }
      }

      if(isSwing)
      {
         price = high[i];
         bar   = i;
         return true;
      }
   }
   return false;
}

//+------------------------------------------------------------------+
bool CIH_Detector::FindSwingLow(int refBar, int lookback, int searchBars,
                                 const double &low[], int totalBars,
                                 double &price, int &bar)
{
   int start = refBar + lookback + 1;
   int end   = refBar + lookback + searchBars;

   for(int i = start; i <= end && i + lookback < totalBars; i++)
   {
      bool isSwing = true;

      for(int j = 1; j <= lookback; j++)
      {
         if(i - j < 0 || low[i - j] <= low[i]) { isSwing = false; break; }
      }
      if(!isSwing) continue;

      for(int j = 1; j <= lookback; j++)
      {
         if(i + j >= totalBars || low[i + j] <= low[i]) { isSwing = false; break; }
      }

      if(isSwing)
      {
         price = low[i];
         bar   = i;
         return true;
      }
   }
   return false;
}

//+------------------------------------------------------------------+
//| Classify BOS candle as Impulsive or Corrective                   |
//+------------------------------------------------------------------+
ENUM_IH_BOS_QUALITY CIH_Detector::ClassifyBOS(int bosBarAbs, bool isBullish,
                                                 const double &open[], const double &high[],
                                                 const double &low[], const double &close[],
                                                 int totalBars)
{
   if(bosBarAbs < 0 || bosBarAbs + 4 >= totalBars) return IH_BOS_CORRECTIVE;

   double range = CandleRange(high[bosBarAbs], low[bosBarAbs]);
   if(range <= 0) return IH_BOS_CORRECTIVE;

   double body = CandleBody(open[bosBarAbs], close[bosBarAbs]);
   if((body / range) < IH_MinBodyRatio) return IH_BOS_CORRECTIVE;

   //--- Momentum: at least 1 of 3 preceding bars in same direction
   int momCount = 0;
   for(int i = bosBarAbs + 1; i <= bosBarAbs + 3 && i < totalBars; i++)
   {
      if(isBullish && IsBull(open[i], close[i])) momCount++;
      else if(!isBullish && IsBear(open[i], close[i])) momCount++;
   }
   if(momCount < 1) return IH_BOS_CORRECTIVE;

   //--- Wick check
   double oppWick = isBullish
      ? UpperWick(high[bosBarAbs], open[bosBarAbs], close[bosBarAbs])
      : LowerWick(low[bosBarAbs], open[bosBarAbs], close[bosBarAbs]);
   if((oppWick / range) > 0.40) return IH_BOS_CORRECTIVE;

   return IH_BOS_IMPULSIVE;
}

//+------------------------------------------------------------------+
//| Detect FVG near BOS candle                                       |
//+------------------------------------------------------------------+
bool CIH_Detector::DetectFVG(int bosBarAbs, bool isBullish,
                              const double &high[], const double &low[],
                              int totalBars,
                              double &fvgH, double &fvgL)
{
   for(int start = MathMax(bosBarAbs - 1, 0); start <= bosBarAbs + 1; start++)
   {
      int c0 = start, c1 = start + 1, c2 = start + 2;
      if(c2 >= totalBars) continue;

      if(isBullish && high[c2] < low[c0])
      {
         fvgH = low[c0];
         fvgL = high[c2];
         return true;
      }
      if(!isBullish && low[c2] > high[c0])
      {
         fvgH = low[c2];
         fvgL = high[c0];
         return true;
      }
   }
   return false;
}

//+------------------------------------------------------------------+
//| Detect liquidity sweep before BOS                                |
//+------------------------------------------------------------------+
bool CIH_Detector::DetectSweep(int bosBarAbs, double swingPrice, bool isBullish,
                                const double &high[], const double &low[],
                                const double &close[], int totalBars)
{
   for(int i = bosBarAbs + 1; i <= bosBarAbs + 5 && i < totalBars; i++)
   {
      if(isBullish && low[i] < swingPrice && close[i] > swingPrice)
         return true;
      if(!isBullish && high[i] > swingPrice && close[i] < swingPrice)
         return true;
   }
   return false;
}

//+------------------------------------------------------------------+
//| Detect BOS retest after break                                    |
//+------------------------------------------------------------------+
bool CIH_Detector::DetectRetest(int bosBarAbs, double swingPrice, bool isBullish,
                                 const double &open[], const double &high[],
                                 const double &low[], const double &close[],
                                 int refBar, int totalBars)
{
   double atr = GetATR(bosBarAbs);
   if(atr <= 0) return false;
   double tol = atr * 0.5;

   int maxCheck = MathMin(bosBarAbs - refBar, 10);
   for(int i = bosBarAbs - 1; i >= refBar + 1 && i >= bosBarAbs - maxCheck; i--)
   {
      if(i < 0 || i >= totalBars) continue;
      double range = CandleRange(high[i], low[i]);
      if(range <= 0) continue;

      if(isBullish)
      {
         if(low[i] <= swingPrice + tol && low[i] >= swingPrice - tol)
         {
            double lw = LowerWick(low[i], open[i], close[i]);
            if((lw / range) > 0.50 && IsBull(open[i], close[i])) return true;
            if(i + 1 < totalBars && IsBull(open[i], close[i]) &&
               CandleBody(open[i], close[i]) > CandleBody(open[i+1], close[i+1]))
               return true;
         }
      }
      else
      {
         if(high[i] >= swingPrice - tol && high[i] <= swingPrice + tol)
         {
            double uw = UpperWick(high[i], open[i], close[i]);
            if((uw / range) > 0.50 && IsBear(open[i], close[i])) return true;
            if(i + 1 < totalBars && IsBear(open[i], close[i]) &&
               CandleBody(open[i], close[i]) > CandleBody(open[i+1], close[i+1]))
               return true;
         }
      }
   }
   return false;
}

//+------------------------------------------------------------------+
//| Full BOS analysis at a given reference bar                       |
//+------------------------------------------------------------------+
IH_BOSInfo CIH_Detector::AnalyzeBOS(int refBar, bool lookForBullish,
                                      const double &open[], const double &high[],
                                      const double &low[], const double &close[],
                                      int totalBars)
{
   IH_BOSInfo info;
   ZeroMemory(info);
   info.quality = IH_BOS_NONE;

   //--- Find swing point
   double swingPrice = 0;
   int    swingBar   = 0;
   bool   found;

   if(lookForBullish)
      found = FindSwingHigh(refBar, IH_SwingLookback, IH_MaxBOSBarsBack, high, totalBars, swingPrice, swingBar);
   else
      found = FindSwingLow(refBar, IH_SwingLookback, IH_MaxBOSBarsBack, low, totalBars, swingPrice, swingBar);

   if(!found) return info;

   //--- Check if any bar between swing and refBar broke the swing (close beyond)
   for(int i = swingBar - 1; i >= refBar + 1; i--)
   {
      if(i < 0 || i >= totalBars) continue;

      bool broken = false;
      if(lookForBullish && close[i] > swingPrice) broken = true;
      if(!lookForBullish && close[i] < swingPrice) broken = true;

      if(broken)
      {
         double breakDist = MathAbs(close[i] - swingPrice);

         //--- Validate min break distance
         double atr = GetATR(refBar);
         if(atr <= 0) atr = GetATR(i);
         if(atr > 0 && breakDist < atr * IH_MinBreakATR)
            return info; // too small

         info.swingPrice = swingPrice;
         info.breakPrice = close[i];
         info.breakDist  = breakDist;
         info.swingBar   = swingBar;
         info.bosBar     = i;
         info.quality    = ClassifyBOS(i, lookForBullish, open, high, low, close, totalBars);

         if(info.quality != IH_BOS_NONE)
         {
            //--- FVG
            info.hasFVG = DetectFVG(i, lookForBullish, high, low, totalBars, info.fvgHigh, info.fvgLow);

            //--- Sweep
            info.hasSweep = DetectSweep(i, swingPrice, lookForBullish, high, low, close, totalBars);

            //--- Retest
            info.hasRetest = DetectRetest(i, swingPrice, lookForBullish, open, high, low, close, refBar, totalBars);
         }
         return info;
      }
   }
   return info;
}

//+------------------------------------------------------------------+
//| Detect S/D Zone (Candle A/B) at refBar                           |
//| Returns the best (freshest) zone matching direction              |
//+------------------------------------------------------------------+
bool CIH_Detector::DetectZone(int refBar, bool lookForBullish,
                               const double &open[], const double &high[],
                               const double &low[], const double &close[],
                               const datetime &time[], int totalBars,
                               IH_Zone &zone)
{
   ZeroMemory(zone);

   //--- Search bars refBar+1 to refBar+ZoneSearchWindow as Candle B
   for(int b = refBar + 1; b <= refBar + IH_ZoneSearchWindow; b++)
   {
      int a = b + 1; // Candle A
      if(a >= totalBars) continue;

      double bRange = high[b] - low[b];
      if(bRange > IH_MaxZoneRange || bRange <= 0) continue;

      if(lookForBullish)
      {
         //--- Bullish: Candle B bullish, body close > Candle A body top
         if(!IsBull(open[b], close[b])) continue;
         double aBodyTop = MathMax(open[a], close[a]);
         if(close[b] <= aBodyTop) continue;

         zone.priceHigh   = close[b];
         zone.priceLow    = open[b];
         zone.entryPrice  = zone.priceLow + (zone.priceHigh - zone.priceLow) * IH_EntryBodyRatio;
         zone.candleBBar  = b;
         zone.timeCreated = time[b];
         zone.isBullish   = true;
         zone.isValid     = true;
         zone.testCount   = 0;

         //--- Count tests between Candle B and refBar
         for(int j = b - 1; j >= refBar + 1; j--)
         {
            if(low[j] <= zone.priceHigh && high[j] >= zone.priceLow)
               zone.testCount++;
         }
         if(zone.testCount > 1) zone.isValid = false;
         if(zone.isValid) return true;
      }
      else
      {
         //--- Bearish: Candle B bearish, body close < Candle A body bottom
         if(!IsBear(open[b], close[b])) continue;
         double aBodyBot = MathMin(open[a], close[a]);
         if(close[b] >= aBodyBot) continue;

         zone.priceHigh   = open[b];
         zone.priceLow    = close[b];
         zone.entryPrice  = zone.priceLow + (zone.priceHigh - zone.priceLow) * IH_EntryBodyRatio;
         zone.candleBBar  = b;
         zone.timeCreated = time[b];
         zone.isBullish   = false;
         zone.isValid     = true;
         zone.testCount   = 0;

         for(int j = b - 1; j >= refBar + 1; j--)
         {
            if(low[j] <= zone.priceHigh && high[j] >= zone.priceLow)
               zone.testCount++;
         }
         if(zone.testCount > 1) zone.isValid = false;
         if(zone.isValid) return true;
      }
   }
   return false;
}

//+------------------------------------------------------------------+
//| Check if time is within active trading session                   |
//+------------------------------------------------------------------+
bool CIH_Detector::IsActiveSession(datetime t)
{
   if(!IH_FilterSessions) return true;

   MqlDateTime dt;
   TimeToStruct(t, dt);
   int hour = dt.hour;
   int barDuration = MathMax(1, PeriodSeconds(_Period) / 3600);
   int barEnd = hour + barDuration;  // bar covers [hour, hour+duration)

   //--- Check if H4 bar window overlaps with any session window
   //    Overlap condition: barStart < sessionEnd AND barEnd > sessionStart
   if(hour < IH_AsiaEnd   && barEnd > IH_AsiaStart)   return true;
   if(hour < IH_LondonEnd && barEnd > IH_LondonStart) return true;
   if(hour < IH_NYEnd     && barEnd > IH_NYStart)      return true;

   return false;
}

#endif
