//+------------------------------------------------------------------+
//|                                              InvictusHelper.mq5  |
//|                    Visual Signal Analyzer for Invictus EA         |
//|           Shows historical + live signals with Entry/TP/SL/Result |
//+------------------------------------------------------------------+
#property copyright   "Invictus Trading System"
#property version     "1.00"
#property description "Visual companion for Invictus EA — XAUUSD H4"
#property description "Shows all historical signals with Entry, SL, TP levels"
#property description "and trade outcomes (TP Hit / SL Hit / Expired / Active)"
#property indicator_chart_window
#property indicator_buffers 0
#property indicator_plots   0

//--- Includes
#include "Modules\IH_Config.mqh"
#include "Modules\IH_Detector.mqh"
#include "Modules\IH_SignalEngine.mqh"
#include "Modules\IH_Renderer.mqh"

//--- Module instances
CIH_Detector      g_detector;
CIH_SignalEngine   g_engine;
CIH_Renderer       g_renderer;

//--- State
bool     g_initialized = false;
int      g_lastProcessedBar = -1;
datetime g_periodStart = 0;

//+------------------------------------------------------------------+
int OnInit()
{
   //--- Initialize TF-dependent parameters
   IH_InitParams();

   string sym = _Symbol;
   if(StringFind(sym, "XAUUSD") < 0 && StringFind(sym, "GOLD") < 0)
      Print("[IH] WARNING: Designed for XAUUSD. Current: ", sym);

   if(!g_detector.Init(sym))     { Print("[IH] FATAL: Detector init failed"); return INIT_FAILED; }
   if(!g_engine.Init(sym, &g_detector)) { Print("[IH] FATAL: Engine init failed"); return INIT_FAILED; }

   g_renderer.Init(ChartID());
   IndicatorSetString(INDICATOR_SHORTNAME, "InvictusHelper (" + EnumToString(_Period) + " SMC)");
   IndicatorSetInteger(INDICATOR_DIGITS, 2);

   g_initialized = true;
   Print("[IH] InvictusHelper v2.0 initialized on ", EnumToString(_Period), " — scanning history...");
   return INIT_SUCCEEDED;
}

//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
   g_renderer.DeleteAll();
   g_detector.Deinit();
   Comment("");
   Print("[IH] InvictusHelper deinitialized — reason: ", reason);
}

//+------------------------------------------------------------------+
int OnCalculate(const int rates_total,
                const int prev_calculated,
                const datetime &time[],
                const double &open[],
                const double &high[],
                const double &low[],
                const double &close[],
                const long &tick_volume[],
                const long &volume[],
                const int &spread[])
{
   if(!g_initialized) return 0;
   if(rates_total < 100) return 0;

   ArraySetAsSeries(time, true);
   ArraySetAsSeries(open, true);
   ArraySetAsSeries(high, true);
   ArraySetAsSeries(low, true);
   ArraySetAsSeries(close, true);

   if(prev_calculated == 0)
   {
      g_renderer.DeleteAll();
      g_renderer.ResetCollision();
      g_engine.Reset();

      //--- [REVERTABLE] Find startBar
      int startBar;
      if(_Period <= PERIOD_M15)
      {
         //--- M15 backtest: skip historical scan, start from 0 via incremental
         startBar = 1;  // no history scan
         g_periodStart = time[0];
         g_lastProcessedBar = rates_total;
         Print("[IH] M15 mode: starting fresh, signals will build incrementally...");

         //--- Draw dashboard with zeros
         g_renderer.DrawDashboard(0, 0, 0, 0, 0, 0, time[0], time[0]);
         return rates_total;
      }
      else
      {
         //--- H4: scan N years back
         int years = MathMax(1, IH_ScanYears);
         datetime scanStart = TimeCurrent() - years * 365 * 24 * 3600;
         startBar = rates_total - 1;
         for(int b = 0; b < rates_total; b++)
         {
            if(time[b] <= scanStart) { startBar = b; break; }
         }
         startBar = MathMin(startBar, rates_total - 70);
      }
      if(startBar < 5) return 0;

      g_periodStart = time[startBar];
      Print("[IH] Scanning ", startBar, " bars for signals...");

      for(int i = startBar; i >= 1; i--)
         g_engine.ProcessBar(i, time, open, high, low, close, rates_total);

      //--- Draw all signals (lines on chart)
      int total = g_engine.GetSignalCount();
      for(int s = 0; s < total; s++)
      {
         IH_Signal sig;
         if(g_engine.GetSignal(s, sig))
            g_renderer.DrawSignal(sig, time, high, low, rates_total);
      }

      //--- Draw all BOS Impulsive (independent of signals)
      g_renderer.DrawAllBOS(g_detector, open, high, low, close, time, rates_total, startBar);

      //--- Draw swing high/low markers
      g_renderer.DrawSwings(g_detector, high, low, time, rates_total);

      //--- Draw sessions
      g_renderer.DrawSessions(time, rates_total);

      //--- Draw dashboard (top-left via Comment)
      g_renderer.DrawDashboard(g_engine.GetWins(), g_engine.GetLosses(),
                               g_engine.GetExpired(), g_engine.GetActive(),
                               g_engine.GetTotalProfit(), total,
                               g_periodStart, time[0]);

      //--- Draw signal table (bottom-left)
      g_renderer.DrawSignalTable(g_engine);

      g_lastProcessedBar = rates_total;

      Print("[IH] Scan complete: ", total, " signals | ",
            "W:", g_engine.GetWins(), " L:", g_engine.GetLosses(),
            " Exp:", g_engine.GetExpired(), " Act:", g_engine.GetActive(),
            " | Net: $", DoubleToString(g_engine.GetTotalProfit(), 1));
   }
   else
   {
      int newBars = rates_total - prev_calculated;
      if(newBars > 0)
      {
         //--- Shift stored bar indices so cooldown/duplicate checks stay correct
         g_engine.ShiftBars(newBars);

         for(int i = newBars + 1; i >= 1; i--)
         {
            if(g_engine.ProcessBar(i, time, open, high, low, close, rates_total))
            {
               IH_Signal sig;
               if(g_engine.GetSignal(g_engine.GetSignalCount() - 1, sig))
                  g_renderer.DrawSignal(sig, time, high, low, rates_total);
            }
         }

         g_engine.UpdateActive(open, high, low, time, rates_total);

         //--- Redraw only recently-resolved signals (status changed from ACTIVE/PENDING)
         int totalSig = g_engine.GetSignalCount();
         for(int s = 0; s < totalSig; s++)
         {
            IH_Signal sig;
            if(!g_engine.GetSignal(s, sig)) continue;

            //--- Only redraw if signal was just resolved (TP/SL/Expired)
            //    or is still active (label needs to stay in place)
            if(sig.result == IH_RESULT_TP_HIT || sig.result == IH_RESULT_SL_HIT ||
               sig.result == IH_RESULT_EXPIRED)
            {
               //--- Check if label still shows old status (BUY LIMIT / LIVE)
               string lblName = IH_PREFIX + "S" + IntegerToString(sig.id) + "_LBL";
               string existingText = ObjectGetString(0, lblName, OBJPROP_TEXT);
               if(StringFind(existingText, "LIMIT") >= 0 || StringFind(existingText, "LIVE") >= 0)
                  g_renderer.DrawSignal(sig, time, high, low, rates_total);
            }
         }

         g_renderer.DrawDashboard(g_engine.GetWins(), g_engine.GetLosses(),
                                  g_engine.GetExpired(), g_engine.GetActive(),
                                  g_engine.GetTotalProfit(), totalSig,
                                  g_periodStart, time[0]);

         g_renderer.DrawSignalTable(g_engine);
      }
   }

   return rates_total;
}

//+------------------------------------------------------------------+
void OnChartEvent(const int id, const long &lparam,
                  const double &dparam, const string &sparam)
{
}
//+------------------------------------------------------------------+
