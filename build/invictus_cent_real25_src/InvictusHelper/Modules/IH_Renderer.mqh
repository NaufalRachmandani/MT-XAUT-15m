//+------------------------------------------------------------------+
//|                                                 IH_Renderer.mqh  |
//|          InvictusHelper — All Chart Drawing (persistent objects)   |
//|          v1.2 — Lines only in candle area, labels outside right   |
//|                 Anti-collision for nearby labels                   |
//+------------------------------------------------------------------+
#ifndef IH_RENDERER_MQH
#define IH_RENDERER_MQH

#include "IH_Config.mqh"
#include "IH_SignalEngine.mqh"

//+------------------------------------------------------------------+
//| Class: CIH_Renderer                                              |
//+------------------------------------------------------------------+
class CIH_Renderer
{
private:
   long     m_chartId;

   //--- Label collision tracking
   double   m_usedPrices[];     // prices where labels are placed
   datetime m_usedTimes[];      // times where labels are placed
   int      m_usedCount;
   double   m_minLabelGap;      // minimum dollar gap between labels

   //--- Object creation helpers
   bool     CreateTrendLine(string name, datetime t1, double p1,
                            datetime t2, double p2,
                            color clr, int width, ENUM_LINE_STYLE style,
                            bool back=false);
   bool     CreateRectangle(string name, datetime t1, double p1,
                            datetime t2, double p2,
                            color clr, bool fill, bool back=true);
   bool     CreateLabel(string name, datetime t, double price,
                        string text, color clr, int fontSize,
                        ENUM_ANCHOR_POINT anchor=ANCHOR_LEFT);
   bool     CreateScreenLabel(string name, int x, int y,
                              string text, color clr, int fontSize);
   void     DeleteByPrefix(string prefix);

   //--- Anti-collision: adjust price to avoid overlap
   double   AdjustLabelPrice(double price, datetime t, double direction);
   void     RegisterLabel(double price, datetime t);

public:
                  CIH_Renderer() : m_chartId(0), m_usedCount(0), m_minLabelGap(28.0) {}
                 ~CIH_Renderer() {}

   void           Init(long chartId) { m_chartId = chartId; }

   //--- Draw individual signal with all components
   void           DrawSignal(const IH_Signal &sig, const datetime &time[],
                              const double &high[], const double &low[], int totalBars);

   //--- Draw all BOS Impulsive candles (independent of signals)
   void           DrawAllBOS(CIH_Detector &detector,
                              const double &open[], const double &high[],
                              const double &low[], const double &close[],
                              const datetime &time[], int totalBars, int startBar);

   //--- Draw session background rectangles
   void           DrawSessions(const datetime &time[], int totalBars);

   //--- Draw dashboard panel
   void           DrawDashboard(int wins, int losses, int expired, int active,
                                double totalProfit, int totalSignals,
                                datetime periodStart = 0, datetime periodEnd = 0);

   //--- Draw signal table (bottom-left, last 5 signals)
   void           DrawSignalTable(CIH_SignalEngine &engine);

   //--- Draw swing high/low markers
   void           DrawSwings(CIH_Detector &detector,
                              const double &high[], const double &low[],
                              const datetime &time[], int totalBars);

   //--- Reset label collision tracker (call before full redraw)
   void           ResetCollision();

   //--- Cleanup
   void           DeleteAll();
};

//+------------------------------------------------------------------+
//| Adjust label price to avoid collision with existing labels       |
//| direction: +1 = push up, -1 = push down                         |
//+------------------------------------------------------------------+
double CIH_Renderer::AdjustLabelPrice(double price, datetime t, double direction)
{
   double adjusted = price;
   int maxRetries = 10;
   int barSpan = PeriodSeconds(_Period);

   for(int retry = 0; retry < maxRetries; retry++)
   {
      bool collision = false;
      for(int i = 0; i < m_usedCount; i++)
      {
         //--- Check labels within 20 bars time range
         if(MathAbs((long)t - (long)m_usedTimes[i]) > barSpan * 20)
            continue;

         if(MathAbs(adjusted - m_usedPrices[i]) < m_minLabelGap)
         {
            collision = true;
            //--- Push in the given direction
            adjusted += direction * m_minLabelGap;
            break;
         }
      }
      if(!collision) break;
   }
   return adjusted;
}

//+------------------------------------------------------------------+
void CIH_Renderer::RegisterLabel(double price, datetime t)
{
   int newSize = m_usedCount + 1;
   ArrayResize(m_usedPrices, newSize, 200);
   ArrayResize(m_usedTimes, newSize, 200);
   m_usedPrices[m_usedCount] = price;
   m_usedTimes[m_usedCount]  = t;
   m_usedCount = newSize;
}

//+------------------------------------------------------------------+
void CIH_Renderer::ResetCollision()
{
   m_usedCount = 0;
   ArrayResize(m_usedPrices, 0);
   ArrayResize(m_usedTimes, 0);
}

//+------------------------------------------------------------------+
bool CIH_Renderer::CreateTrendLine(string name, datetime t1, double p1,
                                    datetime t2, double p2,
                                    color clr, int width, ENUM_LINE_STYLE style,
                                    bool back)
{
   if(ObjectFind(m_chartId, name) >= 0) return true;
   if(!ObjectCreate(m_chartId, name, OBJ_TREND, 0, t1, p1, t2, p2))
      return false;
   ObjectSetInteger(m_chartId, name, OBJPROP_COLOR, clr);
   ObjectSetInteger(m_chartId, name, OBJPROP_WIDTH, width);
   ObjectSetInteger(m_chartId, name, OBJPROP_STYLE, style);
   ObjectSetInteger(m_chartId, name, OBJPROP_RAY_RIGHT, false);
   ObjectSetInteger(m_chartId, name, OBJPROP_BACK, back);
   ObjectSetInteger(m_chartId, name, OBJPROP_SELECTABLE, false);
   ObjectSetInteger(m_chartId, name, OBJPROP_HIDDEN, true);
   return true;
}

//+------------------------------------------------------------------+
bool CIH_Renderer::CreateRectangle(string name, datetime t1, double p1,
                                    datetime t2, double p2,
                                    color clr, bool fill, bool back)
{
   if(ObjectFind(m_chartId, name) >= 0)
   {
      //--- Update existing rectangle coordinates
      ObjectSetInteger(m_chartId, name, OBJPROP_TIME, 0, t1);
      ObjectSetDouble(m_chartId, name, OBJPROP_PRICE, 0, p1);
      ObjectSetInteger(m_chartId, name, OBJPROP_TIME, 1, t2);
      ObjectSetDouble(m_chartId, name, OBJPROP_PRICE, 1, p2);
      ObjectSetInteger(m_chartId, name, OBJPROP_COLOR, clr);
      return true;
   }
   if(!ObjectCreate(m_chartId, name, OBJ_RECTANGLE, 0, t1, p1, t2, p2))
      return false;
   ObjectSetInteger(m_chartId, name, OBJPROP_COLOR, clr);
   ObjectSetInteger(m_chartId, name, OBJPROP_FILL, fill);
   ObjectSetInteger(m_chartId, name, OBJPROP_BACK, back);
   ObjectSetInteger(m_chartId, name, OBJPROP_SELECTABLE, false);
   ObjectSetInteger(m_chartId, name, OBJPROP_HIDDEN, true);
   return true;
}

//+------------------------------------------------------------------+
bool CIH_Renderer::CreateLabel(string name, datetime t, double price,
                                string text, color clr, int fontSize,
                                ENUM_ANCHOR_POINT anchor)
{
   if(ObjectFind(m_chartId, name) >= 0) return true;
   if(!ObjectCreate(m_chartId, name, OBJ_TEXT, 0, t, price))
      return false;
   ObjectSetString(m_chartId, name, OBJPROP_TEXT, text);
   ObjectSetString(m_chartId, name, OBJPROP_FONT, "Consolas");
   ObjectSetInteger(m_chartId, name, OBJPROP_FONTSIZE, fontSize);
   ObjectSetInteger(m_chartId, name, OBJPROP_COLOR, clr);
   ObjectSetInteger(m_chartId, name, OBJPROP_ANCHOR, anchor);
   ObjectSetInteger(m_chartId, name, OBJPROP_SELECTABLE, false);
   ObjectSetInteger(m_chartId, name, OBJPROP_HIDDEN, true);
   return true;
}

//+------------------------------------------------------------------+
bool CIH_Renderer::CreateScreenLabel(string name, int x, int y,
                                      string text, color clr, int fontSize)
{
   if(ObjectFind(m_chartId, name) >= 0)
   {
      ObjectSetString(m_chartId, name, OBJPROP_TEXT, text);
      ObjectSetInteger(m_chartId, name, OBJPROP_COLOR, clr);
      return true;
   }
   if(!ObjectCreate(m_chartId, name, OBJ_LABEL, 0, 0, 0))
      return false;
   ObjectSetInteger(m_chartId, name, OBJPROP_XDISTANCE, x);
   ObjectSetInteger(m_chartId, name, OBJPROP_YDISTANCE, y);
   ObjectSetInteger(m_chartId, name, OBJPROP_CORNER, CORNER_RIGHT_UPPER);
   ObjectSetString(m_chartId, name, OBJPROP_TEXT, text);
   ObjectSetString(m_chartId, name, OBJPROP_FONT, "Consolas");
   ObjectSetInteger(m_chartId, name, OBJPROP_FONTSIZE, fontSize);
   ObjectSetInteger(m_chartId, name, OBJPROP_COLOR, clr);
   ObjectSetInteger(m_chartId, name, OBJPROP_ANCHOR, ANCHOR_LEFT_UPPER);
   ObjectSetInteger(m_chartId, name, OBJPROP_SELECTABLE, false);
   ObjectSetInteger(m_chartId, name, OBJPROP_HIDDEN, true);
   return true;
}

//+------------------------------------------------------------------+
void CIH_Renderer::DeleteByPrefix(string prefix)
{
   int total = ObjectsTotal(m_chartId);
   for(int i = total - 1; i >= 0; i--)
   {
      string name = ObjectName(m_chartId, i);
      if(StringFind(name, prefix) == 0)
         ObjectDelete(m_chartId, name);
   }
}

//+------------------------------------------------------------------+
void CIH_Renderer::DeleteAll()
{
   DeleteByPrefix(IH_PREFIX);
   ResetCollision();
}

//+------------------------------------------------------------------+
//| Draw signal: LINES ONLY, no labels. Color = result.              |
//| Green=TP hit, Red=SL hit, Gray=Expired, White=Active             |
//+------------------------------------------------------------------+
void CIH_Renderer::DrawSignal(const IH_Signal &sig, const datetime &time[],
                               const double &high[], const double &low[], int totalBars)
{
   string idStr = IntegerToString(sig.id);
   string prefix = IH_PREFIX + "S" + idStr + "_";

   bool isExpired = (sig.result == IH_RESULT_EXPIRED);
   int   fs       = IH_SignalLabelSize;
   int   barSpan  = PeriodSeconds(_Period);

   // ============================================================
   // 1b. BOS CANDLE HIGHLIGHT — always drawn independently of
   //     buy/sell/expired filters
   // ============================================================
   bool showThisBOS = IH_ShowBOS && !isExpired && sig.bosTime > 0;
   if(showThisBOS)
   {
      if(sig.bosQuality == IH_BOS_IMPULSIVE && !IH_ShowBOSImpulsive) showThisBOS = false;
      if(sig.bosQuality == IH_BOS_CORRECTIVE && !IH_ShowBOSCorrective) showThisBOS = false;
   }
   if(showThisBOS)
   {
      //--- Colors: magenta=impulsive, cyan=corrective (unique, not used elsewhere)
      color bosClr = (sig.bosQuality == IH_BOS_IMPULSIVE)
                     ? clrMagenta : clrAqua;
      color bosBg  = (sig.bosQuality == IH_BOS_IMPULSIVE)
                     ? C'40,0,40' : C'0,35,35';

      //--- Use unique name per BOS candle time (avoid duplicate rectangles)
      string bosTimeStr = TimeToString(sig.bosTime, TIME_DATE | TIME_MINUTES);
      StringReplace(bosTimeStr, ".", "");
      StringReplace(bosTimeStr, ":", "");
      StringReplace(bosTimeStr, " ", "");
      string bosPrefix = IH_PREFIX + "BOS_" + bosTimeStr + "_";

      //--- BOS candle boundaries (padded both sides to cover candle)
      double bosHi = sig.bosHigh;
      double bosLo = sig.bosLow;
      int oneBar = PeriodSeconds(_Period);
      int pad = oneBar * IH_BOSBoxPadding / 100;
      datetime tBos1 = sig.bosTime - pad;
      datetime tBos2 = sig.bosTime + oneBar + pad;

      //--- Skip if this BOS candle already drawn by another signal
      if(ObjectFind(m_chartId, bosPrefix + "BG") < 0)
      {
         //--- Filled background (behind candles)
         CreateRectangle(bosPrefix + "BG",
                         tBos1, bosHi, tBos2, bosLo,
                         bosBg, true, true);

         //--- Border (in front)
         CreateRectangle(bosPrefix + "BD",
                         tBos1, bosHi, tBos2, bosLo,
                         bosClr, false, false);
      }

      //--- Label above/below
      string bosTag = (sig.bosQuality == IH_BOS_IMPULSIVE) ? "IMP" : "COR";
      double lblOff = (bosHi - bosLo) * 0.3 + 5.0;
      double lblY = sig.isBuy ? bosHi + lblOff : bosLo - lblOff;
      ENUM_ANCHOR_POINT anchor = sig.isBuy ? ANCHOR_LOWER : ANCHOR_UPPER;
      CreateLabel(prefix + "BOS_L", sig.bosTime, lblY, bosTag, bosClr, fs, anchor);

      //--- Swing level line (from swing bar to BOS candle)
      if(sig.swingPrice > 0)
      {
         datetime tSwStart = (sig.swingTime > 0) ? sig.swingTime : sig.bosTime - barSpan * 8;
         datetime tSwEnd   = sig.bosTime + PeriodSeconds(_Period);
         CreateTrendLine(prefix + "SWL", tSwStart, sig.swingPrice,
                         tSwEnd, sig.swingPrice,
                         bosClr, 1, STYLE_DASH, true);
      }
   }

   // ============================================================
   // Signal filter: skip trade box, lines, labels, arrows
   // if direction or expired is hidden
   // ============================================================
   if(!IH_ShowExpiredSignal && isExpired) return;
   if(!IH_ShowBuySignal && sig.isBuy) return;
   if(!IH_ShowSellSignal && !sig.isBuy) return;

   color entryClr = isExpired ? clrSilver : clrWhite;
   color tpClr    = isExpired ? C'70,70,70' : clrLime;
   color slClr    = isExpired ? C'70,70,70' : clrRed;
   color zoneClr  = sig.isBuy ? IH_DemandZoneColor : IH_SupplyZoneColor;

   //--- Time boundaries for lines
   datetime tSignal = sig.signalTime;
   datetime tEnd;
   if(sig.result == IH_RESULT_TP_HIT || sig.result == IH_RESULT_SL_HIT)
      tEnd = sig.resolveTime;
   else if(isExpired)
      tEnd = tSignal + IH_PendingExpiryBars * barSpan;
   else
      tEnd = TimeCurrent();

   datetime tLabel = tEnd + barSpan * 2;

   // ============================================================
   // 1. ZONE — from Candle B to trade end
   // ============================================================
   if(IH_ShowZones && sig.zoneTime > 0)
   {
      int zPad = PeriodSeconds(_Period) * IH_BOSBoxPadding / 100;
      datetime tZ1 = sig.zoneTime - zPad;
      datetime tZ2 = tEnd;

      //--- Filled background (dark tint, behind candles)
      color zFill = isExpired ? C'25,25,25'
                   : (sig.isBuy ? C'10,25,50' : C'50,25,10');
      CreateRectangle(prefix + "ZONE",
                      tZ1, sig.zoneHigh,
                      tZ2, sig.zoneLow,
                      zFill, true, true);

      //--- Bright border (in front, visible)
      color zBorder = isExpired ? clrSilver : zoneClr;
      CreateRectangle(prefix + "ZONE_BD",
                      tZ1, sig.zoneHigh,
                      tZ2, sig.zoneLow,
                      zBorder, false, false);
   }

   // ============================================================
   // 2. TRADE BOX — colored rectangle showing the trade range
   //    Green=TP hit, Red=SL hit, Gray=Expired, Blue=Active
   // ============================================================

   //--- Tooltip text
   string dir = sig.isBuy ? "BUY" : "SELL";
   string gr  = (sig.grade == IH_GRADE_A) ? "A" : "B";
   string bos = (sig.bosQuality == IH_BOS_IMPULSIVE) ? "Impulsive" : "Corrective";

   if(!isExpired)
   {
      //--- TP zone box + line
      if(IH_ShowLineTP)
      {
         color tpBoxClr = (sig.result == IH_RESULT_TP_HIT) ? C'0,50,0' : C'15,30,15';
         CreateRectangle(prefix + "TP_BOX",
                         tSignal, sig.entryPrice,
                         tEnd, sig.tp1Price,
                         tpBoxClr, true, true);
         CreateTrendLine(prefix + "T", tSignal, sig.tp1Price, tEnd, sig.tp1Price,
                         tpClr, 1, STYLE_SOLID);
      }

      //--- SL zone box + line
      if(IH_ShowLineSL)
      {
         color slBoxClr = (sig.result == IH_RESULT_SL_HIT) ? C'50,0,0' : C'30,15,15';
         CreateRectangle(prefix + "SL_BOX",
                         tSignal, sig.entryPrice,
                         tEnd, sig.slPrice,
                         slBoxClr, true, true);
         CreateTrendLine(prefix + "S", tSignal, sig.slPrice, tEnd, sig.slPrice,
                         slClr, 1, STYLE_SOLID);
      }
   }

   //--- Entry line (from Candle B to label)
   datetime tLineFrom = (sig.zoneTime > 0) ? sig.zoneTime : tSignal;
   datetime tLineTo = tEnd + barSpan;
   CreateTrendLine(prefix + "E", tLineFrom, sig.entryPrice, tLineTo, sig.entryPrice,
                   entryClr, 1, STYLE_DASH);

   //--- Entry arrow at fill position (only when limit order filled)
   bool isFilled = (sig.result == IH_RESULT_ACTIVE ||
                    sig.result == IH_RESULT_TP_HIT ||
                    sig.result == IH_RESULT_SL_HIT);
   bool showArrow = isFilled &&
                    ((sig.isBuy && IH_ShowArrowBuy) || (!sig.isBuy && IH_ShowArrowSell));
   if(showArrow && sig.fillTime > 0)
   {
      string arName = prefix + "AR";
      if(ObjectFind(m_chartId, arName) < 0)
      {
         color arClr = sig.isBuy ? clrDodgerBlue : clrGold;
         int arCode  = sig.isBuy ? 217 : 218;  // ▲ buy, ▼ sell
         ObjectCreate(m_chartId, arName, OBJ_ARROW, 0, sig.fillTime, sig.entryPrice);
         ObjectSetInteger(m_chartId, arName, OBJPROP_ARROWCODE, arCode);
         ObjectSetInteger(m_chartId, arName, OBJPROP_COLOR, arClr);
         ObjectSetInteger(m_chartId, arName, OBJPROP_WIDTH, 1);
         ObjectSetInteger(m_chartId, arName, OBJPROP_SELECTABLE, false);
         ObjectSetInteger(m_chartId, arName, OBJPROP_HIDDEN, true);
      }
   }

   // ============================================================
   // 3. RESULT LABEL — small, at the RIGHT END of the box
   //    Only 1 label per signal, placed after the last candle
   // ============================================================
   datetime tLbl = tEnd + barSpan;

   string lblText;
   color  lblClr;

   if(sig.result == IH_RESULT_TP_HIT)
   {
      lblText = StringFormat("%s +$%.0f", dir, sig.profitDollar);
      lblClr  = IH_WinColor;
   }
   else if(sig.result == IH_RESULT_SL_HIT)
   {
      lblText = StringFormat("%s -$%.0f", dir, sig.slDistance);
      lblClr  = IH_LossColor;
   }
   else if(sig.result == IH_RESULT_EXPIRED)
   {
      lblText = StringFormat("%s EXP", dir);
      lblClr  = IH_ExpiredColor;
   }
   else
   {
      //--- LIVE: "BUY LIMIT - 4769 (TP 4889, SL 4618)"
      string limitDir = sig.isBuy ? "BUY LIMIT" : "SELL LIMIT";
      lblText = StringFormat("%s - %.0f (TP %.0f, SL %.0f)",
                              limitDir, sig.entryPrice, sig.tp1Price, sig.slPrice);
      lblClr  = clrYellow;
   }

   //--- Create label or update text/color in-place
   if(IH_ShowLabelEntry)
   {
      string lblName = prefix + "LBL";
      if(ObjectFind(m_chartId, lblName) >= 0)
      {
         ObjectSetString(m_chartId, lblName, OBJPROP_TEXT, lblText);
         ObjectSetInteger(m_chartId, lblName, OBJPROP_COLOR, lblClr);
      }
      else
      {
         CreateLabel(lblName, tLbl, sig.entryPrice, lblText, lblClr, fs, ANCHOR_LEFT);
      }
   }

   //--- TP price label (small text near TP line)
   if(IH_ShowLabelTP && !isExpired && IH_ShowLineTP)
   {
      string tpLblName = prefix + "TP_LBL";
      string tpText = StringFormat("TP %.0f", sig.tp1Price);
      color  tpLblClr = clrLime;
      if(ObjectFind(m_chartId, tpLblName) >= 0)
      {
         ObjectSetString(m_chartId, tpLblName, OBJPROP_TEXT, tpText);
         ObjectSetInteger(m_chartId, tpLblName, OBJPROP_COLOR, tpLblClr);
      }
      else
      {
         double tpLblY = sig.isBuy ? sig.tp1Price + 3.0 : sig.tp1Price - 3.0;
         ENUM_ANCHOR_POINT tpAnchor = sig.isBuy ? ANCHOR_LOWER : ANCHOR_UPPER;
         CreateLabel(tpLblName, tLbl, tpLblY, tpText, tpLblClr, fs - 1, tpAnchor);
      }
   }

   //--- SL price label (small text near SL line)
   if(IH_ShowLabelSL && !isExpired && IH_ShowLineSL)
   {
      string slLblName = prefix + "SL_LBL";
      string slText = StringFormat("SL %.0f", sig.slPrice);
      color  slLblClr = clrRed;
      if(ObjectFind(m_chartId, slLblName) >= 0)
      {
         ObjectSetString(m_chartId, slLblName, OBJPROP_TEXT, slText);
         ObjectSetInteger(m_chartId, slLblName, OBJPROP_COLOR, slLblClr);
      }
      else
      {
         double slLblY = sig.isBuy ? sig.slPrice - 3.0 : sig.slPrice + 3.0;
         ENUM_ANCHOR_POINT slAnchor = sig.isBuy ? ANCHOR_UPPER : ANCHOR_LOWER;
         CreateLabel(slLblName, tLbl, slLblY, slText, slLblClr, fs - 1, slAnchor);
      }
   }

   // ============================================================
   // 4. TOOLTIPS on lines for hover detail
   // ============================================================
   string tip = StringFormat("%s @ %.2f | Grade %s | Score %d\nBOS: %s\nSL: %.2f (-$%.0f) | TP: %.2f (+$%.0f)",
                              dir, sig.entryPrice, gr, sig.score, bos,
                              sig.slPrice, sig.slDistance, sig.tp1Price, sig.tp1Distance);
   ObjectSetString(m_chartId, prefix + "E", OBJPROP_TOOLTIP, tip);
   ObjectSetInteger(m_chartId, prefix + "E", OBJPROP_SELECTABLE, true);
   ObjectSetInteger(m_chartId, prefix + "E", OBJPROP_HIDDEN, false);
}

//+------------------------------------------------------------------+
//| Draw session background rectangles                               |
//+------------------------------------------------------------------+
void CIH_Renderer::DrawSessions(const datetime &time[], int totalBars)
{
   if(!IH_ShowSessions) return;

   int limit = MathMin(totalBars, 200);
   int sessionIdx = 0;

   for(int i = limit - 1; i >= 1; i--)
   {
      MqlDateTime dt;
      TimeToStruct(time[i], dt);
      int hour = dt.hour;

      color sessClr = clrNONE;
      if(hour >= IH_AsiaStart && hour < IH_AsiaEnd)
         sessClr = IH_AsiaColor;
      else if(hour >= IH_LondonStart && hour < IH_LondonEnd)
         sessClr = IH_LondonColor;
      else if(hour >= IH_NYStart && hour < IH_NYEnd)
         sessClr = IH_NYColor;
      else continue;

      datetime tStart = time[i];
      datetime tEnd = tStart + PeriodSeconds(_Period);

      double barH = iHigh(_Symbol, _Period, i);
      double barL = iLow(_Symbol, _Period, i);
      if(barH <= 0 || barL <= 0) continue;

      double pad = (barH - barL) * 0.5;

      string name = IH_PREFIX + "SESS_" + IntegerToString(sessionIdx++);
      CreateRectangle(name, tStart, barH + pad, tEnd, barL - pad,
                      sessClr, true, true);
   }
}

//+------------------------------------------------------------------+
//| Draw dashboard — using Comment() (top-left, auto-sized, no clip) |
//+------------------------------------------------------------------+
void CIH_Renderer::DrawDashboard(int wins, int losses, int expired, int active,
                                  double totalProfit, int totalSignals,
                                  datetime periodStart, datetime periodEnd)
{
   if(!IH_ShowDashboard) { Comment(""); return; }

   int totalResolved = wins + losses;
   double winRate = totalResolved > 0 ? (double)wins / totalResolved * 100.0 : 0;
   string plSign = totalProfit >= 0 ? "+" : "";

   //--- Format period string
   string periodStr = "";
   if(periodStart > 0)
   {
      MqlDateTime dtS, dtE;
      TimeToStruct(periodStart, dtS);

      string months[] = {"","Jan","Feb","Mar","Apr","May","Jun",
                         "Jul","Aug","Sep","Oct","Nov","Dec"};

      string startStr = StringFormat("%d %s %d (%02d:%02d)",
                         dtS.day, months[dtS.mon], dtS.year, dtS.hour, dtS.min);

      string endStr = "Now";
      if(periodEnd > 0 && periodEnd < TimeCurrent())
      {
         TimeToStruct(periodEnd, dtE);
         endStr = StringFormat("%d %s %d (%02d:%02d)",
                   dtE.day, months[dtE.mon], dtE.year, dtE.hour, dtE.min);
      }

      periodStr = startStr + " - " + endStr;
   }

   string c = "";
   c += "  ══════════════════════════════════\n";
   c += "       INVICTUS HELPER v1.0\n";
   c += "  ══════════════════════════════════\n";
   if(periodStr != "")
      c += "   Period:  " + periodStr + "\n";
   c += StringFormat("   Signals:    %d\n", totalSignals);
   c += StringFormat("   Win:        %d\n", wins);
   c += StringFormat("   Loss:       %d\n", losses);
   c += StringFormat("   WinRate:    %.0f%%\n", winRate);
   c += StringFormat("   Expired:    %d\n", expired);
   c += StringFormat("   Active:     %d\n", active);
   c += "  ──────────────────────────────────\n";
   c += StringFormat("   Net P&L:    %s$%.0f /0.01lot\n", plSign, totalProfit);
   c += "  ──────────────────────────────────\n";
   c += StringFormat("   SL: $%.0f-$%.0f    TP: RR%.1f\n",
                      IH_MinSLDollar, IH_MaxSLDollar, IH_TP1_RR);
   c += "  ══════════════════════════════════";

   Comment(c);
}

//+------------------------------------------------------------------+
//| Draw signal table — bottom-left, last 5 signals, newest on top   |
//+------------------------------------------------------------------+
void CIH_Renderer::DrawSignalTable(CIH_SignalEngine &engine)
{
   if(!IH_ShowTableSignal)
   {
      DeleteByPrefix(IH_PREFIX + "TBL_");
      return;
   }

   string tp = IH_PREFIX + "TBL_";
   int fs = 8;
   int lh = 20;       // line height (more spacing between rows)
   int padL = 15;      // from left edge
   int padB = 10;      // from bottom edge
   int maxRows = MathMax(1, MathMin(IH_TableMaxRows, 10));

   int totalSig = engine.GetSignalCount();
   int showCount = MathMin(totalSig, maxRows);

   //--- Table dimensions
   int tableH = lh * (showCount + 2) + 10;  // +2 for header + separator
   int tableW = 500;
   int baseY = padB;   // bottom-up, so row 0 = bottom

   //--- Background panel
   string bg = tp + "BG";
   if(ObjectFind(m_chartId, bg) < 0)
   {
      ObjectCreate(m_chartId, bg, OBJ_RECTANGLE_LABEL, 0, 0, 0);
      ObjectSetInteger(m_chartId, bg, OBJPROP_CORNER, CORNER_LEFT_LOWER);
      ObjectSetInteger(m_chartId, bg, OBJPROP_SELECTABLE, false);
      ObjectSetInteger(m_chartId, bg, OBJPROP_HIDDEN, true);
   }
   ObjectSetInteger(m_chartId, bg, OBJPROP_XDISTANCE, padL - 5);
   ObjectSetInteger(m_chartId, bg, OBJPROP_YDISTANCE, baseY + tableH);
   ObjectSetInteger(m_chartId, bg, OBJPROP_XSIZE, tableW);
   ObjectSetInteger(m_chartId, bg, OBJPROP_YSIZE, tableH);
   ObjectSetInteger(m_chartId, bg, OBJPROP_BGCOLOR, C'15,17,25');
   ObjectSetInteger(m_chartId, bg, OBJPROP_BORDER_COLOR, C'50,55,75');
   ObjectSetInteger(m_chartId, bg, OBJPROP_BORDER_TYPE, BORDER_FLAT);

   //--- Helper lambda-like: create table cell (CORNER_LEFT_LOWER, y grows upward)
   //    Row 0 = bottom row (newest signal), header at top

   //--- Header row (topmost in the table)
   //    Consolas is monospaced, so fixed char widths align columns
   //    #(2) TIME(14) SIGNAL(6) ENTRY(7) TP(7) SL(7) EXPIRED(14) STATUS(10)
   int headerY = baseY + tableH - lh - 2;
   string hdrText = " #  TIME (WIB)      SIGNAL ENTRY    TP    SL   STATUS     ";

   string hdrName = tp + "HDR";
   if(ObjectFind(m_chartId, hdrName) >= 0)
   {
      ObjectSetString(m_chartId, hdrName, OBJPROP_TEXT, hdrText);
   }
   else
   {
      ObjectCreate(m_chartId, hdrName, OBJ_LABEL, 0, 0, 0);
      ObjectSetInteger(m_chartId, hdrName, OBJPROP_CORNER, CORNER_LEFT_LOWER);
      ObjectSetInteger(m_chartId, hdrName, OBJPROP_XDISTANCE, padL);
      ObjectSetInteger(m_chartId, hdrName, OBJPROP_YDISTANCE, headerY);
      ObjectSetString(m_chartId, hdrName, OBJPROP_TEXT, hdrText);
      ObjectSetString(m_chartId, hdrName, OBJPROP_FONT, "Consolas");
      ObjectSetInteger(m_chartId, hdrName, OBJPROP_FONTSIZE, fs);
      ObjectSetInteger(m_chartId, hdrName, OBJPROP_COLOR, clrGold);
      ObjectSetInteger(m_chartId, hdrName, OBJPROP_ANCHOR, ANCHOR_LEFT_LOWER);
      ObjectSetInteger(m_chartId, hdrName, OBJPROP_SELECTABLE, false);
      ObjectSetInteger(m_chartId, hdrName, OBJPROP_HIDDEN, true);
   }

   //--- Separator
   string sepText = " -------------------------------------------------------";
   string sepName = tp + "SEP";
   if(ObjectFind(m_chartId, sepName) >= 0)
      ObjectSetString(m_chartId, sepName, OBJPROP_TEXT, sepText);
   else
   {
      ObjectCreate(m_chartId, sepName, OBJ_LABEL, 0, 0, 0);
      ObjectSetInteger(m_chartId, sepName, OBJPROP_CORNER, CORNER_LEFT_LOWER);
      ObjectSetInteger(m_chartId, sepName, OBJPROP_XDISTANCE, padL);
      ObjectSetInteger(m_chartId, sepName, OBJPROP_YDISTANCE, headerY - lh);
      ObjectSetString(m_chartId, sepName, OBJPROP_TEXT, sepText);
      ObjectSetString(m_chartId, sepName, OBJPROP_FONT, "Consolas");
      ObjectSetInteger(m_chartId, sepName, OBJPROP_FONTSIZE, fs - 1);
      ObjectSetInteger(m_chartId, sepName, OBJPROP_COLOR, C'50,55,75');
      ObjectSetInteger(m_chartId, sepName, OBJPROP_ANCHOR, ANCHOR_LEFT_LOWER);
      ObjectSetInteger(m_chartId, sepName, OBJPROP_SELECTABLE, false);
      ObjectSetInteger(m_chartId, sepName, OBJPROP_HIDDEN, true);
   }

   //--- Data rows (newest first = highest index)
   for(int r = 0; r < maxRows; r++)
   {
      string rowName = tp + "R" + IntegerToString(r);
      int sigIdx = totalSig - 1 - r;  // newest first
      int rowY = headerY - lh * (r + 2);  // +2 = skip header + separator

      if(sigIdx < 0)
      {
         //--- Empty row
         if(ObjectFind(m_chartId, rowName) >= 0)
            ObjectSetString(m_chartId, rowName, OBJPROP_TEXT, "");
         else
         {
            ObjectCreate(m_chartId, rowName, OBJ_LABEL, 0, 0, 0);
            ObjectSetInteger(m_chartId, rowName, OBJPROP_CORNER, CORNER_LEFT_LOWER);
            ObjectSetInteger(m_chartId, rowName, OBJPROP_XDISTANCE, padL);
            ObjectSetInteger(m_chartId, rowName, OBJPROP_YDISTANCE, rowY);
            ObjectSetString(m_chartId, rowName, OBJPROP_TEXT, "");
            ObjectSetString(m_chartId, rowName, OBJPROP_FONT, "Consolas");
            ObjectSetInteger(m_chartId, rowName, OBJPROP_FONTSIZE, fs);
            ObjectSetInteger(m_chartId, rowName, OBJPROP_COLOR, clrWhite);
            ObjectSetInteger(m_chartId, rowName, OBJPROP_ANCHOR, ANCHOR_LEFT_LOWER);
            ObjectSetInteger(m_chartId, rowName, OBJPROP_SELECTABLE, false);
            ObjectSetInteger(m_chartId, rowName, OBJPROP_HIDDEN, true);
         }
         continue;
      }

      IH_Signal sig;
      if(!engine.GetSignal(sigIdx, sig)) continue;

      //--- Format time (server → WIB via GMT)
      //    server_gmt = TimeCurrent() - TimeGMT() (broker's GMT offset)
      //    WIB = GMT+7 = server_time - server_gmt + 7h
      int srvGMT = (int)(TimeCurrent() - TimeGMT());
      int toWIB  = 7 * 3600 - srvGMT;
      datetime wibTime = sig.signalTime + toWIB;
      MqlDateTime dt;
      TimeToStruct(wibTime, dt);
      string timeStr = StringFormat("%02d %s %02d:%02d",
                                     dt.day, MonthShort(dt.mon), dt.hour, dt.min);

      //--- Signal direction (fixed 4 chars)
      string sigStr = sig.isBuy ? "BUY " : "SELL";

      //--- Status: DONE (TP/SL hit), EXPIRED, WAITING
      string statusStr;
      color  rowClr;
      if(sig.result == IH_RESULT_TP_HIT)
      {
         statusStr = StringFormat("DONE +$%.0f", sig.profitDollar);
         rowClr = IH_WinColor;
      }
      else if(sig.result == IH_RESULT_SL_HIT)
      {
         statusStr = StringFormat("DONE -$%.0f", sig.slDistance);
         rowClr = IH_LossColor;
      }
      else if(sig.result == IH_RESULT_EXPIRED)
      {
         statusStr = "EXPIRED";
         rowClr = IH_ExpiredColor;
      }
      else
      {
         statusStr = "WAITING";
         rowClr = clrYellow;
      }

      //--- Build row text — must match header exactly
      //    " #  TIME (WIB)      SIGNAL ENTRY    TP    SL   STATUS"
      string rowText = StringFormat("%2d  %-14s  %-4s %5.0f %5.0f %5.0f  %s",
                                     r + 1, timeStr, sigStr,
                                     sig.entryPrice, sig.tp1Price, sig.slPrice,
                                     statusStr);

      if(ObjectFind(m_chartId, rowName) >= 0)
      {
         ObjectSetString(m_chartId, rowName, OBJPROP_TEXT, rowText);
         ObjectSetInteger(m_chartId, rowName, OBJPROP_COLOR, rowClr);
      }
      else
      {
         ObjectCreate(m_chartId, rowName, OBJ_LABEL, 0, 0, 0);
         ObjectSetInteger(m_chartId, rowName, OBJPROP_CORNER, CORNER_LEFT_LOWER);
         ObjectSetInteger(m_chartId, rowName, OBJPROP_XDISTANCE, padL);
         ObjectSetInteger(m_chartId, rowName, OBJPROP_YDISTANCE, rowY);
         ObjectSetString(m_chartId, rowName, OBJPROP_TEXT, rowText);
         ObjectSetString(m_chartId, rowName, OBJPROP_FONT, "Consolas");
         ObjectSetInteger(m_chartId, rowName, OBJPROP_FONTSIZE, fs);
         ObjectSetInteger(m_chartId, rowName, OBJPROP_COLOR, rowClr);
         ObjectSetInteger(m_chartId, rowName, OBJPROP_ANCHOR, ANCHOR_LEFT_LOWER);
         ObjectSetInteger(m_chartId, rowName, OBJPROP_SELECTABLE, false);
         ObjectSetInteger(m_chartId, rowName, OBJPROP_HIDDEN, true);
      }
   }
}

//+------------------------------------------------------------------+
//| Helper: month short name                                         |
//+------------------------------------------------------------------+
string MonthShort(int mon)
{
   string months[] = {"","Jan","Feb","Mar","Apr","May","Jun",
                      "Jul","Aug","Sep","Oct","Nov","Dec"};
   if(mon >= 1 && mon <= 12) return months[mon];
   return "???";
}

//+------------------------------------------------------------------+
//| Draw Swing zigzag background rectangles                          |
//| Scan OLD→NEW (high index→low index in AsSeries)                  |
//| Build zigzag: keep extreme per segment (highest SH, lowest SL)   |
//| SL→SH leg: bullish (blue bg), SH→SL leg: bearish (purple bg)    |
//+------------------------------------------------------------------+
void CIH_Renderer::DrawSwings(CIH_Detector &detector,
                               const double &high[], const double &low[],
                               const datetime &time[], int totalBars)
{
   if(!IH_ShowBOS) return;

   int lookback = IH_SwingLookback;
   int maxBars = totalBars - lookback - 1;
   if(maxBars < lookback + 5) return;

   string sp = IH_PREFIX + "SW_";

   //--- Step 1: Collect all raw swings
   //    Scan from HIGH index to LOW index = OLD to NEW (AsSeries)
   int    rawBar[];
   double rawPrice[];
   int    rawType[];   // 1=SH, -1=SL
   int    rawCount = 0;

   for(int i = maxBars - 1; i >= lookback; i--)
   {
      if(i + lookback >= totalBars) continue;

      //--- Check swing high
      bool isSH = true;
      for(int j = 1; j <= lookback; j++)
      {
         if(i - j < 0 || high[i - j] >= high[i]) { isSH = false; break; }
      }
      if(isSH)
      {
         for(int j = 1; j <= lookback; j++)
         {
            if(i + j >= totalBars || high[i + j] >= high[i]) { isSH = false; break; }
         }
      }

      //--- Check swing low
      bool isSL = true;
      for(int j = 1; j <= lookback; j++)
      {
         if(i - j < 0 || low[i - j] <= low[i]) { isSL = false; break; }
      }
      if(isSL)
      {
         for(int j = 1; j <= lookback; j++)
         {
            if(i + j >= totalBars || low[i + j] <= low[i]) { isSL = false; break; }
         }
      }

      if(isSH)
      {
         int n = rawCount++;
         ArrayResize(rawBar, rawCount, 500);
         ArrayResize(rawPrice, rawCount, 500);
         ArrayResize(rawType, rawCount, 500);
         rawBar[n]   = i;
         rawPrice[n] = high[i];
         rawType[n]  = 1;
      }
      if(isSL)
      {
         int n = rawCount++;
         ArrayResize(rawBar, rawCount, 500);
         ArrayResize(rawPrice, rawCount, 500);
         ArrayResize(rawType, rawCount, 500);
         rawBar[n]   = i;
         rawPrice[n] = low[i];
         rawType[n]  = -1;
      }
   }

   if(rawCount < 2) return;

   //--- Step 2: Build proper zigzag — alternate SH/SL, keep extremes
   //    If consecutive same type: keep highest SH or lowest SL
   int    zzBar[];
   double zzPrice[];
   int    zzType[];
   int    zzCount = 0;

   // Seed with first swing
   ArrayResize(zzBar, 1); ArrayResize(zzPrice, 1); ArrayResize(zzType, 1);
   zzBar[0] = rawBar[0]; zzPrice[0] = rawPrice[0]; zzType[0] = rawType[0];
   zzCount = 1;

   for(int r = 1; r < rawCount; r++)
   {
      int lastType = zzType[zzCount - 1];

      if(rawType[r] == lastType)
      {
         //--- Same type consecutive: replace if more extreme
         if(rawType[r] == 1 && rawPrice[r] > zzPrice[zzCount - 1])
         {
            // Higher swing high — replace
            zzBar[zzCount - 1]   = rawBar[r];
            zzPrice[zzCount - 1] = rawPrice[r];
         }
         else if(rawType[r] == -1 && rawPrice[r] < zzPrice[zzCount - 1])
         {
            // Lower swing low — replace
            zzBar[zzCount - 1]   = rawBar[r];
            zzPrice[zzCount - 1] = rawPrice[r];
         }
         // else: ignore (not more extreme)
      }
      else
      {
         //--- Different type: add to zigzag
         zzCount++;
         ArrayResize(zzBar, zzCount, 500);
         ArrayResize(zzPrice, zzCount, 500);
         ArrayResize(zzType, zzCount, 500);
         zzBar[zzCount - 1]   = rawBar[r];
         zzPrice[zzCount - 1] = rawPrice[r];
         zzType[zzCount - 1]  = rawType[r];
      }
   }

   //--- Step 3: Draw background rectangles between each zigzag pair
   int bgIdx = 0;

   for(int z = 0; z < zzCount - 1; z++)
   {
      int    bar1  = zzBar[z];
      int    bar2  = zzBar[z + 1];
      double price1 = zzPrice[z];
      double price2 = zzPrice[z + 1];
      int    type1  = zzType[z];

      //--- Time: bar1 is older (higher index), bar2 is newer (lower index)
      //    In AsSeries, higher index = older. time[higher] < time[lower]
      datetime t1 = time[bar1];
      datetime t2 = time[bar2];
      double pHi = MathMax(price1, price2);
      double pLo = MathMin(price1, price2);

      string bgName = sp + "BG" + IntegerToString(bgIdx++);
      if(ObjectFind(m_chartId, bgName) < 0)
      {
         if(type1 == -1 && IH_ShowSwingBullish)
         {
            //--- SL → SH = bullish leg
            CreateRectangle(bgName, t1, pHi, t2, pLo, C'15,20,35', true, true);
         }
         else if(type1 == 1 && IH_ShowSwingBearish)
         {
            //--- SH → SL = bearish leg
            CreateRectangle(bgName, t1, pHi, t2, pLo, C'30,15,30', true, true);
         }
      }
   }
}

//+------------------------------------------------------------------+
//| Draw ALL BOS Impulsive candles — independent of signal detection  |
//+------------------------------------------------------------------+
void CIH_Renderer::DrawAllBOS(CIH_Detector &detector,
                               const double &open[], const double &high[],
                               const double &low[], const double &close[],
                               const datetime &time[], int totalBars, int startBar)
{
   if(!IH_ShowAllBOS) return;

   int barSpan = PeriodSeconds(_Period);
   int pad = barSpan * IH_BOSBoxPadding / 100;
   int fs = IH_SignalLabelSize;

   //--- Standalone BOS colors
   //    Impulsive: olive/yellow-green
   //    Corrective: dim purple
   color abosImpClr  = C'160,180,50';
   color abosImpBg   = C'25,30,5';
   color abosImpLine = C'130,150,40';
   color abosCorClr  = C'130,90,160';
   color abosCorBg   = C'20,12,28';
   color abosCorLine = C'100,70,130';

   for(int refBar = startBar; refBar >= 1; refBar--)
   {
      if(refBar + IH_MaxBOSBarsBack + IH_SwingLookback + 5 >= totalBars) continue;

      //--- Detect bias for this bar
      ENUM_IH_BIAS bias = detector.DetectBias(refBar, high, low, close, totalBars);
      bool lookBullish = (bias == IH_BIAS_BULLISH || bias == IH_BIAS_NEUTRAL);
      bool lookBearish = (bias == IH_BIAS_BEARISH);

      //--- Try bullish BOS (uptrend/neutral only)
      if(lookBullish)
      {
      IH_BOSInfo bosBull = detector.AnalyzeBOS(refBar, true, open, high, low, close, totalBars);
      if(bosBull.quality != IH_BOS_NONE && bosBull.bosBar > 0 && bosBull.bosBar < totalBars)
      {
         string bosTimeStr = TimeToString(time[bosBull.bosBar], TIME_DATE | TIME_MINUTES);
         StringReplace(bosTimeStr, ".", "");
         StringReplace(bosTimeStr, ":", "");
         StringReplace(bosTimeStr, " ", "");
         string bosPrefix = IH_PREFIX + "ABOS_" + bosTimeStr + "_";

         if(ObjectFind(m_chartId, bosPrefix + "BG") < 0)
         {
            datetime tBos1 = time[bosBull.bosBar] - pad;
            datetime tBos2 = time[bosBull.bosBar] + barSpan + pad;
            double bosHi = high[bosBull.bosBar];
            double bosLo = low[bosBull.bosBar];

            bool isImpBull = (bosBull.quality == IH_BOS_IMPULSIVE);
            color cBull  = isImpBull ? abosImpClr  : abosCorClr;
            color bgBull = isImpBull ? abosImpBg   : abosCorBg;
            color lnBull = isImpBull ? abosImpLine : abosCorLine;
            string tagBull = isImpBull ? "IMP" : "COR";

            CreateRectangle(bosPrefix + "BG", tBos1, bosHi, tBos2, bosLo,
                            bgBull, true, true);
            CreateRectangle(bosPrefix + "BD", tBos1, bosHi, tBos2, bosLo,
                            cBull, false, false);

            double lblOff = (bosHi - bosLo) * 0.3 + 5.0;
            CreateLabel(bosPrefix + "L", time[bosBull.bosBar], bosHi + lblOff,
                        tagBull, cBull, fs, ANCHOR_LOWER);

            //--- Swing level line (from swing bar to BOS bar)
            if(bosBull.swingBar > 0 && bosBull.swingBar < totalBars)
            {
               datetime tSwStart = time[bosBull.swingBar];
               datetime tSwEnd   = time[bosBull.bosBar] + barSpan;
               CreateTrendLine(bosPrefix + "SWL", tSwStart, bosBull.swingPrice,
                               tSwEnd, bosBull.swingPrice,
                               lnBull, 1, STYLE_DASH, true);
            }
         }
      }
      } // end bullish

      //--- Try bearish BOS (downtrend only)
      if(lookBearish)
      {
      IH_BOSInfo bosBear = detector.AnalyzeBOS(refBar, false, open, high, low, close, totalBars);
      if(bosBear.quality != IH_BOS_NONE && bosBear.bosBar > 0 && bosBear.bosBar < totalBars)
      {
         string bosTimeStr = TimeToString(time[bosBear.bosBar], TIME_DATE | TIME_MINUTES);
         StringReplace(bosTimeStr, ".", "");
         StringReplace(bosTimeStr, ":", "");
         StringReplace(bosTimeStr, " ", "");
         string bosPrefix = IH_PREFIX + "ABOS_" + bosTimeStr + "_";

         if(ObjectFind(m_chartId, bosPrefix + "BG") < 0)
         {
            datetime tBos1 = time[bosBear.bosBar] - pad;
            datetime tBos2 = time[bosBear.bosBar] + barSpan + pad;
            double bosHi = high[bosBear.bosBar];
            double bosLo = low[bosBear.bosBar];

            bool isImpBear = (bosBear.quality == IH_BOS_IMPULSIVE);
            color cBear  = isImpBear ? abosImpClr  : abosCorClr;
            color bgBear = isImpBear ? abosImpBg   : abosCorBg;
            color lnBear = isImpBear ? abosImpLine : abosCorLine;
            string tagBear = isImpBear ? "IMP" : "COR";

            CreateRectangle(bosPrefix + "BG", tBos1, bosHi, tBos2, bosLo,
                            bgBear, true, true);
            CreateRectangle(bosPrefix + "BD", tBos1, bosHi, tBos2, bosLo,
                            cBear, false, false);

            double lblOff = (bosHi - bosLo) * 0.3 + 5.0;
            CreateLabel(bosPrefix + "L", time[bosBear.bosBar], bosLo - lblOff,
                        tagBear, cBear, fs, ANCHOR_UPPER);

            //--- Swing level line (from swing bar to BOS bar)
            if(bosBear.swingBar > 0 && bosBear.swingBar < totalBars)
            {
               datetime tSwStart = time[bosBear.swingBar];
               datetime tSwEnd   = time[bosBear.bosBar] + barSpan;
               CreateTrendLine(bosPrefix + "SWL", tSwStart, bosBear.swingPrice,
                               tSwEnd, bosBear.swingPrice,
                               lnBear, 1, STYLE_DASH, true);
            }
         }
      }
      } // end bearish
   }
}

#endif
