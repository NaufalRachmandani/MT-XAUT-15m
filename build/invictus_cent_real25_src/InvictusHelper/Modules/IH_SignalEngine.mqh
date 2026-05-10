//+------------------------------------------------------------------+
//|                                             IH_SignalEngine.mqh  |
//|              InvictusHelper — Scoring, Signals, Trade Simulator   |
//|              v1.2 — Full EA rule matching (cooldown, killswitch,  |
//|                     max positions, same-dir block after SL)       |
//+------------------------------------------------------------------+
#ifndef IH_SIGNAL_ENGINE_MQH
#define IH_SIGNAL_ENGINE_MQH

#include "IH_Config.mqh"
#include "IH_Detector.mqh"

//+------------------------------------------------------------------+
//--- Debug file writer (writes to MQL5/Files/IH_Debug.log)
void WriteDebug(datetime barTime, string msg)
{
   int h = FileOpen("IH_Debug.log", FILE_WRITE|FILE_READ|FILE_TXT|FILE_ANSI);
   if(h != INVALID_HANDLE)
   {
      FileSeek(h, 0, SEEK_END);
      FileWriteString(h, TimeToString(barTime) + " | " + msg + "\n");
      FileClose(h);
   }
}

void ResetDebugLog()
{
   int h = FileOpen("IH_Debug.log", FILE_WRITE|FILE_TXT|FILE_ANSI);
   if(h != INVALID_HANDLE)
   {
      FileWriteString(h, "=== IH Debug Log Reset: " + TimeToString(TimeCurrent()) + " ===\n");
      FileClose(h);
   }
}

class CIH_SignalEngine
{
private:
   CIH_Detector  *m_detector;
   string          m_symbol;

   //--- Signal storage
   IH_Signal       m_signals[];
   int             m_signalCount;
   int             m_nextId;

   //--- EA state simulation
   int             m_lastSignalBar;
   int             m_lastSLBar;          // bar where last SL hit occurred
   bool            m_lastSLWasBuy;       // direction of last SL (for same-dir block)
   bool            m_dirBlocked;         // [SAME-DIR-BLOCK] active
   int             m_dailyWins;          // wins today (KillSwitch)
   int             m_dailyLosses;        // losses today
   int             m_currentDay;         // day of year for daily reset

   //--- Zone cooldown (matches EA: EntryCalculator.mqh)
   double          m_lastZonePrice;      // last signal entry price
   datetime        m_lastZoneTime;       // last signal time

   //--- Stats
   int             m_wins;
   int             m_losses;
   int             m_expired;
   int             m_active;
   double          m_totalProfit;

   //--- Internal scoring
   int             ScoreVolatility(int refBar);
   int             ScoreBOSBonus(const IH_BOSInfo &bos);
   int             ScoreTrend(int refBar, bool isBullish,
                              const double &high[], const double &low[], int totalBars);
   double          CalcSL(const IH_Zone &zone, bool isBuy, int refBar);
   double          CalcTP1(double entry, double sl, bool isBuy);

   //--- Count currently active/pending signals at a given bar
   int             CountActiveAt(int refBar);
   int             CountPendingAt(int refBar);

   //--- Daily reset check
   void            CheckDailyReset(datetime barTime);

public:
                   CIH_SignalEngine();
                  ~CIH_SignalEngine();

   bool            Init(string symbol, CIH_Detector *detector);

   bool            ProcessBar(int refBar,
                              const datetime &time[],
                              const double &open[],
                              const double &high[],
                              const double &low[],
                              const double &close[],
                              int totalBars);

   void            SimulateTrade(IH_Signal &sig,
                                 const double &open[],
                                 const double &high[],
                                 const double &low[],
                                 const datetime &time[],
                                 int totalBars);

   void            UpdateActive(const double &open[],
                                const double &high[],
                                const double &low[],
                                const datetime &time[],
                                int totalBars);

   int             GetSignalCount() const { return m_signalCount; }
   bool            GetSignal(int idx, IH_Signal &sig) const;
   int             GetWins()    const { return m_wins; }
   int             GetLosses()  const { return m_losses; }
   int             GetExpired() const { return m_expired; }
   int             GetActive()  const { return m_active; }
   double          GetTotalProfit() const { return m_totalProfit; }
   void            Reset();
   void            ShiftBars(int shift);
};

//+------------------------------------------------------------------+
CIH_SignalEngine::CIH_SignalEngine()
{
   m_detector = NULL;
   m_signalCount = 0;
   m_nextId = 0;
   m_lastSignalBar = 99999;
   m_lastSLBar = 99999;
   m_lastSLWasBuy = false;
   m_dirBlocked = false;
   m_dailyWins = 0;
   m_dailyLosses = 0;
   m_currentDay = -1;
   m_lastZonePrice = 0;
   m_lastZoneTime = 0;
   m_wins = m_losses = m_expired = m_active = 0;
   m_totalProfit = 0;
}

CIH_SignalEngine::~CIH_SignalEngine() {}

bool CIH_SignalEngine::Init(string symbol, CIH_Detector *detector)
{
   m_symbol   = symbol;
   m_detector = detector;
   Reset();
   return true;
}

void CIH_SignalEngine::Reset()
{
   ArrayResize(m_signals, 0);
   m_signalCount = 0;
   m_nextId = 0;
   m_lastSignalBar = 99999;
   m_lastSLBar = 99999;
   m_lastSLWasBuy = false;
   m_dirBlocked = false;
   m_dailyWins = 0;
   m_dailyLosses = 0;
   m_currentDay = -1;
   m_lastZonePrice = 0;
   m_lastZoneTime = 0;
   m_wins = m_losses = m_expired = m_active = 0;
   m_totalProfit = 0;
   ResetDebugLog();
}

//+------------------------------------------------------------------+
//| Shift stored bar indices when new bars arrive (AsSeries)         |
//+------------------------------------------------------------------+
void CIH_SignalEngine::ShiftBars(int shift)
{
   if(shift <= 0) return;
   if(m_lastSignalBar < 99999) m_lastSignalBar += shift;
   if(m_lastSLBar < 99999)     m_lastSLBar += shift;
}

bool CIH_SignalEngine::GetSignal(int idx, IH_Signal &sig) const
{
   if(idx < 0 || idx >= m_signalCount) return false;
   sig = m_signals[idx];
   return true;
}

//+------------------------------------------------------------------+
//| Count signals that are ACTIVE (filled, not resolved) at refBar   |
//+------------------------------------------------------------------+
int CIH_SignalEngine::CountActiveAt(int refBar)
{
   int count = 0;
   for(int i = 0; i < m_signalCount; i++)
   {
      //--- Signal was filled and not yet resolved at this bar
      if(m_signals[i].result == IH_RESULT_ACTIVE ||
         (m_signals[i].result == IH_RESULT_TP_HIT && m_signals[i].resolveBar < refBar) ||
         (m_signals[i].result == IH_RESULT_SL_HIT && m_signals[i].resolveBar < refBar))
      {
         //--- Was it filled before refBar and resolved after refBar?
         if(m_signals[i].fillBar >= refBar && m_signals[i].signalBar >= refBar)
         {
            if(m_signals[i].result == IH_RESULT_ACTIVE)
               count++;
            else if(m_signals[i].resolveBar < refBar)
               count++;  // was active at refBar
         }
      }
   }
   return count;
}

//+------------------------------------------------------------------+
//| Count signals that are PENDING (not yet filled) at refBar        |
//+------------------------------------------------------------------+
int CIH_SignalEngine::CountPendingAt(int refBar)
{
   int count = 0;
   for(int i = 0; i < m_signalCount; i++)
   {
      if(m_signals[i].signalBar >= refBar)
      {
         //--- If fill happened after refBar or never filled
         if(m_signals[i].result == IH_RESULT_PENDING ||
            m_signals[i].result == IH_RESULT_EXPIRED ||
            (m_signals[i].fillBar < refBar && m_signals[i].fillBar >= 0))
         {
            // check if pending at refBar
            if(m_signals[i].fillBar < refBar || m_signals[i].result == IH_RESULT_EXPIRED)
            {
               int expiryBar = m_signals[i].signalBar - IH_PendingExpiryBars;
               if(refBar >= expiryBar && refBar <= m_signals[i].signalBar)
                  count++;
            }
         }
      }
   }
   return count;
}

//+------------------------------------------------------------------+
//| Check if we crossed into a new day → reset daily counters        |
//+------------------------------------------------------------------+
void CIH_SignalEngine::CheckDailyReset(datetime barTime)
{
   MqlDateTime dt;
   TimeToStruct(barTime, dt);
   int dayOfYear = dt.day_of_year;

   if(dayOfYear != m_currentDay)
   {
      m_currentDay = dayOfYear;
      m_dailyWins = 0;
      m_dailyLosses = 0;
      //--- Reset direction block on new day
      m_dirBlocked = false;
   }
}

//+------------------------------------------------------------------+
int CIH_SignalEngine::ScoreVolatility(int refBar)
{
   double atr14 = m_detector.GetATR(refBar);
   if(atr14 <= 0) return 0;

   double sum = 0;
   int count = 0;
   for(int i = refBar; i < refBar + 50; i++)
   {
      double v = m_detector.GetATR(i);
      if(v > 0) { sum += v; count++; }
   }
   if(count < 20) return 0;
   double atr50 = sum / count;

   if(atr14 < 1.3 * atr50) return 15;
   return 0;
}

int CIH_SignalEngine::ScoreBOSBonus(const IH_BOSInfo &bos)
{
   int bonus = 0;
   if(bos.hasFVG)    bonus += 10;
   if(bos.hasRetest) bonus += 10;
   if(bos.hasSweep)  bonus += 5;
   return bonus;
}

int CIH_SignalEngine::ScoreTrend(int refBar, bool isBullish,
                                  const double &high[], const double &low[],
                                  int totalBars)
{
   if(refBar + 11 >= totalBars) return 0;

   if(isBullish)
   {
      int hhCount = 0;
      for(int k = refBar + 1; k < refBar + 10 && k + 1 < totalBars; k++)
         if(high[k] > high[k + 1]) hhCount++;
      if(hhCount >= 5) return 20;
   }
   else
   {
      int llCount = 0;
      for(int k = refBar + 1; k < refBar + 10 && k + 1 < totalBars; k++)
         if(low[k] < low[k + 1]) llCount++;
      if(llCount >= 5) return 20;
   }
   return 0;
}

double CIH_SignalEngine::CalcSL(const IH_Zone &zone, bool isBuy, int refBar)
{
   double atr = m_detector.GetATR(refBar);
   double buffer = atr * IH_ATRBufferSL;

   double sl;
   if(isBuy)
      sl = zone.priceLow - buffer;
   else
      sl = zone.priceHigh + buffer;

   double dist = MathAbs(zone.entryPrice - sl);
   if(dist < IH_MinSLDollar)
      sl = isBuy ? zone.entryPrice - IH_MinSLDollar
                 : zone.entryPrice + IH_MinSLDollar;
   if(dist > IH_MaxSLDollar)
      sl = isBuy ? zone.entryPrice - IH_MaxSLDollar
                 : zone.entryPrice + IH_MaxSLDollar;

   return NormalizeDouble(sl, 2);
}

double CIH_SignalEngine::CalcTP1(double entry, double sl, bool isBuy)
{
   double slDist = MathAbs(entry - sl);
   double tpDist = slDist * IH_TP1_RR;
   double tp = isBuy ? entry + tpDist : entry - tpDist;
   return NormalizeDouble(tp, 2);
}

//+------------------------------------------------------------------+
//| Main processing: evaluate one bar for signals                    |
//| Implements ALL EA filters: cooldown, killswitch, max pos, etc.   |
//+------------------------------------------------------------------+
bool CIH_SignalEngine::ProcessBar(int refBar,
                                   const datetime &time[],
                                   const double &open[],
                                   const double &high[],
                                   const double &low[],
                                   const double &close[],
                                   int totalBars)
{
   //--- Minimum lookback required
   if(refBar + IH_MaxBOSBarsBack + IH_SwingLookback + 5 >= totalBars)
      return false;

   //--- Same bar check
   if(m_lastSignalBar == refBar && m_signalCount > 0)
      return false;

   //--- Daily reset (KillSwitch)
   CheckDailyReset(time[refBar]);

   //--- KillSwitch: max wins per day (H4=3, M15=10 for scalping)
   int maxWins = (_Period <= PERIOD_M15) ? 10 : 3;
   if(m_dailyWins >= maxWins)
      return false;

   //--- Session filter (disabled for M15 scalping — trade all sessions)
   if(_Period > PERIOD_M15)
   {
      if(!m_detector.IsActiveSession(time[refBar]))
         return false;
   }

   //--- Weekend filter
   MqlDateTime dt;
   TimeToStruct(time[refBar], dt);
   if(dt.day_of_week == 0 || dt.day_of_week == 6) return false;
   if(dt.day_of_week == 5 && dt.hour >= 15) return false;

   //--- After-loss cooldown: skip 2 H4 bars after last SL hit
   if(m_lastSLBar < 99999 && (m_lastSLBar - refBar) < 2)
      return false;

   //--- Detect bias
   ENUM_IH_BIAS bias = m_detector.DetectBias(refBar, high, low, close, totalBars);
   bool isBuy = (bias == IH_BIAS_BULLISH || bias == IH_BIAS_NEUTRAL);
   string biasStr = (bias == IH_BIAS_BULLISH) ? "BULL" :
                    (bias == IH_BIAS_BEARISH) ? "BEAR" : "NEUTRAL";

   //--- [SAME-DIR-BLOCK] After SL, block same direction until new day or profit
   //    Disabled for M15 scalping (too restrictive)
   if(_Period > PERIOD_M15)
   {
      if(m_dirBlocked && isBuy == m_lastSLWasBuy)
      {
         WriteDebug(time[refBar], "REJECT: same-dir-block " + (isBuy?"BUY":"SELL"));
         return false;
      }
   }

   //--- Detect BOS
   IH_BOSInfo bos = m_detector.AnalyzeBOS(refBar, isBuy, open, high, low, close, totalBars);
   if(bos.quality == IH_BOS_NONE)
   {
      WriteDebug(time[refBar], "REJECT: no BOS | bias=" + biasStr +
                 " looking=" + (isBuy?"BUY":"SELL"));
      return false;
   }

   //--- Detect S/D Zone
   IH_Zone zone;
   if(!m_detector.DetectZone(refBar, isBuy, open, high, low, close, time, totalBars, zone))
   {
      WriteDebug(time[refBar], "REJECT: no zone | bias=" + biasStr +
                 " BOS=" + (bos.quality==IH_BOS_IMPULSIVE?"IMP":"COR") +
                 " dir=" + (isBuy?"BUY":"SELL"));
      return false;
   }

   //--- Zone cooldown: skip if same zone attempted recently (matches EA: ZoneCooldownBars=2)
   double zoneTolerance = 1.0;  // $1 tolerance (same as EA)
   if(m_lastZonePrice > 0 && MathAbs(zone.entryPrice - m_lastZonePrice) < zoneTolerance)
   {
      int cooldownSec = 2 * PeriodSeconds(_Period);  // 2 H4 bars = 8 hours
      if((int)(time[refBar] - m_lastZoneTime) < cooldownSec)
      {
         WriteDebug(time[refBar], "REJECT: zone cooldown | entry=" + DoubleToString(zone.entryPrice,2) +
                    " lastZone=" + DoubleToString(m_lastZonePrice,2));
         return false;
      }
   }

   //--- Confluence scoring
   int score = 0;
   string breakdown = "";

   score += 40;
   breakdown += "Zone:+40 ";

   int volScore = ScoreVolatility(refBar);
   score += volScore;
   if(volScore > 0) breakdown += "Vol:+15 ";

   int bonusScore = ScoreBOSBonus(bos);
   score += bonusScore;
   if(bonusScore > 0) breakdown += "BOS:+" + IntegerToString(bonusScore) + " ";

   int trendScore = ScoreTrend(refBar, isBuy, high, low, totalBars);
   score += trendScore;
   if(trendScore > 0) breakdown += "Trend:+20 ";

   if(isBuy && IH_GoldBuyBonus > 0)
   {
      score += IH_GoldBuyBonus;
      breakdown += "Gold:+" + IntegerToString(IH_GoldBuyBonus) + " ";
   }

   //--- Grade
   ENUM_IH_GRADE grade;
   if(score >= IH_MinScoreA) grade = IH_GRADE_A;
   else if(score >= IH_MinScoreB) grade = IH_GRADE_B;
   else grade = IH_GRADE_REJECT;

   if(grade == IH_GRADE_REJECT) return false;
   if(grade == IH_GRADE_B && !IH_ShowGradeB) return false;

   //--- Create signal
   IH_Signal sig;
   ZeroMemory(sig);
   sig.id          = m_nextId++;
   sig.signalTime  = time[refBar];
   sig.signalBar   = refBar;
   sig.isBuy       = isBuy;
   sig.score       = score;
   sig.grade       = grade;
   sig.breakdown   = breakdown;
   sig.entryPrice  = NormalizeDouble(zone.entryPrice, 2);
   sig.zoneHigh    = zone.priceHigh;
   sig.zoneLow     = zone.priceLow;
   sig.zoneTime    = zone.timeCreated;
   sig.bosQuality  = bos.quality;
   sig.bosBar      = bos.bosBar;
   sig.bosTime     = (bos.bosBar >= 0 && bos.bosBar < totalBars) ? time[bos.bosBar] : 0;
   sig.bosHigh     = (bos.bosBar >= 0 && bos.bosBar < totalBars) ? high[bos.bosBar] : 0;
   sig.bosLow      = (bos.bosBar >= 0 && bos.bosBar < totalBars) ? low[bos.bosBar]  : 0;
   sig.swingPrice  = bos.swingPrice;
   sig.swingTime   = (bos.swingBar >= 0 && bos.swingBar < totalBars) ? time[bos.swingBar] : 0;
   sig.hasFVG      = bos.hasFVG;
   sig.hasSweep    = bos.hasSweep;
   sig.hasRetest   = bos.hasRetest;

   sig.slPrice     = CalcSL(zone, isBuy, refBar);
   sig.tp1Price    = CalcTP1(sig.entryPrice, sig.slPrice, isBuy);
   sig.slDistance   = MathAbs(sig.entryPrice - sig.slPrice);
   sig.tp1Distance  = MathAbs(sig.tp1Price - sig.entryPrice);

   sig.result      = IH_RESULT_PENDING;
   sig.drawn       = false;

   //--- Simulate trade outcome
   SimulateTrade(sig, open, high, low, time, totalBars);

   //--- Store signal
   int newSize = m_signalCount + 1;
   ArrayResize(m_signals, newSize, 100);
   m_signals[m_signalCount] = sig;
   m_signalCount = newSize;

   //--- Update zone cooldown tracking
   m_lastZonePrice = sig.entryPrice;
   m_lastZoneTime  = sig.signalTime;

   //--- Update stats & EA state
   if(sig.result == IH_RESULT_TP_HIT)
   {
      m_wins++;
      m_dailyWins++;
      m_totalProfit += sig.profitDollar;
      //--- TP hit clears direction block
      m_dirBlocked = false;
   }
   else if(sig.result == IH_RESULT_SL_HIT)
   {
      m_losses++;
      m_dailyLosses++;
      m_totalProfit += sig.profitDollar;
      //--- SL hit: set after-loss cooldown & direction block
      m_lastSLBar = sig.resolveBar;
      m_lastSLWasBuy = sig.isBuy;
      m_dirBlocked = true;
   }
   else if(sig.result == IH_RESULT_EXPIRED) { m_expired++; }
   else { m_active++; }

   m_lastSignalBar = refBar;

   return true;
}

//+------------------------------------------------------------------+
void CIH_SignalEngine::SimulateTrade(IH_Signal &sig,
                                      const double &open[],
                                      const double &high[],
                                      const double &low[],
                                      const datetime &time[],
                                      int totalBars)
{
   int refBar = sig.signalBar;

   //--- Step 1: Check if limit order fills within expiry window (8 hours, matches EA PendingExpiryHours=8)
   int fillBar = -1;
   int expirySec = IH_PendingExpiryBars * PeriodSeconds(_Period);  // 2 * 4h = 8 hours
   datetime expiryTime = sig.signalTime + expirySec;

   for(int i = refBar; i >= 0; i--)
   {
      if(i >= totalBars) continue;
      if(time[i] > expiryTime) break;  // past expiry window

      if(sig.isBuy)
      {
         if(low[i] <= sig.entryPrice) { fillBar = i; break; }
      }
      else
      {
         if(high[i] >= sig.entryPrice) { fillBar = i; break; }
      }
   }

   if(fillBar < 0)
   {
      //--- Check if we have enough data to confirm expiry
      //    If newest bar (time[0]) hasn't reached expiryTime yet, signal is still PENDING
      if(time[0] < expiryTime)
         sig.result = IH_RESULT_PENDING;
      else
         sig.result = IH_RESULT_EXPIRED;
      return;
   }

   sig.fillBar  = fillBar;
   sig.fillTime = time[fillBar];
   sig.result   = IH_RESULT_ACTIVE;

   //--- Step 2: Walk forward from fill to check TP/SL
   for(int i = fillBar; i >= 0; i--)
   {
      if(i >= totalBars) continue;

      if(sig.isBuy)
      {
         bool slHit = (low[i] <= sig.slPrice);
         bool tpHit = (high[i] >= sig.tp1Price);

         if(slHit && tpHit)
         {
            double distToSL = MathAbs(open[i] - sig.slPrice);
            double distToTP = MathAbs(open[i] - sig.tp1Price);
            if(distToSL <= distToTP) tpHit = false; else slHit = false;
         }

         if(slHit)
         {
            sig.result       = IH_RESULT_SL_HIT;
            sig.resolveBar   = i;
            sig.resolveTime  = time[i];
            sig.profitDollar = -(sig.slDistance);
            return;
         }
         if(tpHit)
         {
            sig.result       = IH_RESULT_TP_HIT;
            sig.resolveBar   = i;
            sig.resolveTime  = time[i];
            sig.profitDollar = sig.tp1Distance;
            return;
         }
      }
      else
      {
         bool slHit = (high[i] >= sig.slPrice);
         bool tpHit = (low[i] <= sig.tp1Price);

         if(slHit && tpHit)
         {
            double distToSL = MathAbs(open[i] - sig.slPrice);
            double distToTP = MathAbs(open[i] - sig.tp1Price);
            if(distToSL <= distToTP) tpHit = false; else slHit = false;
         }

         if(slHit)
         {
            sig.result       = IH_RESULT_SL_HIT;
            sig.resolveBar   = i;
            sig.resolveTime  = time[i];
            sig.profitDollar = -(sig.slDistance);
            return;
         }
         if(tpHit)
         {
            sig.result       = IH_RESULT_TP_HIT;
            sig.resolveBar   = i;
            sig.resolveTime  = time[i];
            sig.profitDollar = sig.tp1Distance;
            return;
         }
      }
   }

   sig.result = IH_RESULT_ACTIVE;
}

//+------------------------------------------------------------------+
void CIH_SignalEngine::UpdateActive(const double &open[],
                                     const double &high[],
                                     const double &low[],
                                     const datetime &time[],
                                     int totalBars)
{
   for(int s = 0; s < m_signalCount; s++)
   {
      if(m_signals[s].result != IH_RESULT_ACTIVE &&
         m_signals[s].result != IH_RESULT_PENDING)
         continue;

      if(m_signals[s].result == IH_RESULT_PENDING)
      {
         if(m_signals[s].isBuy && low[0] <= m_signals[s].entryPrice)
         {
            m_signals[s].fillBar = 0;
            m_signals[s].fillTime = time[0];
            m_signals[s].result = IH_RESULT_ACTIVE;
         }
         else if(!m_signals[s].isBuy && high[0] >= m_signals[s].entryPrice)
         {
            m_signals[s].fillBar = 0;
            m_signals[s].fillTime = time[0];
            m_signals[s].result = IH_RESULT_ACTIVE;
         }
         else
         {
            //--- Time-based expiry (matches EA: PendingExpiryHours=8)
            int expSec = IH_PendingExpiryBars * PeriodSeconds(_Period);
            if(time[0] >= m_signals[s].signalTime + expSec)
            {
               m_signals[s].result = IH_RESULT_EXPIRED;
               m_expired++;
            }
            continue;
         }
      }

      if(m_signals[s].result == IH_RESULT_ACTIVE)
      {
         bool isBuy = m_signals[s].isBuy;
         if(isBuy)
         {
            if(low[0] <= m_signals[s].slPrice)
            {
               m_signals[s].result = IH_RESULT_SL_HIT;
               m_signals[s].resolveBar = 0;
               m_signals[s].resolveTime = time[0];
               m_signals[s].profitDollar = -(m_signals[s].slDistance);
               m_active--; m_losses++; m_dailyLosses++;
               m_totalProfit += m_signals[s].profitDollar;
               m_lastSLBar = 0;
               m_lastSLWasBuy = isBuy;
               m_dirBlocked = true;
            }
            else if(high[0] >= m_signals[s].tp1Price)
            {
               m_signals[s].result = IH_RESULT_TP_HIT;
               m_signals[s].resolveBar = 0;
               m_signals[s].resolveTime = time[0];
               m_signals[s].profitDollar = m_signals[s].tp1Distance;
               m_active--; m_wins++; m_dailyWins++;
               m_totalProfit += m_signals[s].profitDollar;
               m_dirBlocked = false;
            }
         }
         else
         {
            if(high[0] >= m_signals[s].slPrice)
            {
               m_signals[s].result = IH_RESULT_SL_HIT;
               m_signals[s].resolveBar = 0;
               m_signals[s].resolveTime = time[0];
               m_signals[s].profitDollar = -(m_signals[s].slDistance);
               m_active--; m_losses++; m_dailyLosses++;
               m_totalProfit += m_signals[s].profitDollar;
               m_lastSLBar = 0;
               m_lastSLWasBuy = isBuy;
               m_dirBlocked = true;
            }
            else if(low[0] <= m_signals[s].tp1Price)
            {
               m_signals[s].result = IH_RESULT_TP_HIT;
               m_signals[s].resolveBar = 0;
               m_signals[s].resolveTime = time[0];
               m_signals[s].profitDollar = m_signals[s].tp1Distance;
               m_active--; m_wins++; m_dailyWins++;
               m_totalProfit += m_signals[s].profitDollar;
               m_dirBlocked = false;
            }
         }
      }
   }
}

#endif
