//+------------------------------------------------------------------+
//|                                             IH_TradeManager.mqh  |
//|                 InvictusHelper — Position & Order Management     |
//|                                                                  |
//|  Depends on (declared in InvictusDevelopment.mq5 before include):|
//|    g_trade, gs_trade    — CTrade objects                        |
//|    g_detector           — CIH_Detector                          |
//|    EA_MAGIC_BT, EA_MAGIC_SIDEWAYS — magic number defines        |
//|    LogWrite()           — from IH_Logger.mqh                    |
//+------------------------------------------------------------------+
#ifndef IH_TRADEMANAGER_MQH
#define IH_TRADEMANAGER_MQH

//============================================================
//  PARTIAL CLOSE TRACKING
//============================================================
ulong  g_partialTickets[];
int    g_partialCount = 0;

bool IsPartialDone(ulong ticket)
{
   for(int i = 0; i < g_partialCount; i++)
      if(g_partialTickets[i] == ticket) return true;
   return false;
}

void AddPartialDone(ulong ticket)
{
   g_partialCount++;
   ArrayResize(g_partialTickets, g_partialCount);
   g_partialTickets[g_partialCount - 1] = ticket;
}

void RemovePartialDone(ulong ticket)
{
   for(int i = 0; i < g_partialCount; i++)
   {
      if(g_partialTickets[i] == ticket)
      {
         g_partialTickets[i] = g_partialTickets[g_partialCount - 1];
         g_partialCount--;
         ArrayResize(g_partialTickets, MathMax(g_partialCount, 0));
         return;
      }
   }
}

//+------------------------------------------------------------------+
//  Hitung open positions + pending orders untuk magic number tertentu
//+------------------------------------------------------------------+
int CountPositions(long magicNumber)
{
   int count = 0;
   //--- Count open positions
   for(int i = 0; i < PositionsTotal(); i++)
   {
      if(PositionGetTicket(i) > 0 &&
         PositionGetInteger(POSITION_MAGIC) == magicNumber)
         count++;
   }
   //--- Count pending orders (BuyLimit/SellLimit yang belum filled)
   for(int i = 0; i < OrdersTotal(); i++)
   {
      if(OrderGetTicket(i) > 0 &&
         OrderGetInteger(ORDER_MAGIC) == magicNumber)
         count++;
   }
   return count;
}

//+------------------------------------------------------------------+
//  Cancel pending orders jika bias berubah atau posisi sudah penuh
//+------------------------------------------------------------------+
void ManagePendingOrders()
{
   //--- Butuh minimal 12 bar untuk deteksi bias
   double high[], low[], close[];
   if(CopyHigh(_Symbol, _Period, 0, 12, high)   < 12) return;
   if(CopyLow(_Symbol, _Period, 0, 12, low)     < 12) return;
   if(CopyClose(_Symbol, _Period, 0, 12, close) < 12) return;
   ArraySetAsSeries(high, true);
   ArraySetAsSeries(low, true);
   ArraySetAsSeries(close, true);

   ENUM_IH_BIAS bias = g_detector.DetectBias(1, high, low, close, 12);
   bool biasBuy = (bias == IH_BIAS_BULLISH || bias == IH_BIAS_NEUTRAL);

   //--- Hitung open positions per magic (tanpa pending) untuk cek maxPos
   int openBT = 0;
   for(int i = 0; i < PositionsTotal(); i++)
   {
      if(PositionGetTicket(i) > 0 &&
         PositionGetInteger(POSITION_MAGIC) == EA_MAGIC_BT &&
         PositionGetString(POSITION_SYMBOL) == _Symbol)
         openBT++;
   }
   double bal = AccountInfoDouble(ACCOUNT_BALANCE);
   int maxPos = (bal <= 20000.0) ? 5 : (bal <= 50000.0) ? 3 : 3;
   bool posFull = (openBT >= maxPos);

   for(int i = OrdersTotal() - 1; i >= 0; i--)
   {
      ulong ticket = OrderGetTicket(i);
      if(ticket <= 0) continue;
      if(OrderGetInteger(ORDER_MAGIC) != EA_MAGIC_BT) continue;
      if(OrderGetString(ORDER_SYMBOL) != _Symbol) continue;

      long type = OrderGetInteger(ORDER_TYPE);
      bool isBuyOrder  = (type == ORDER_TYPE_BUY_LIMIT);
      bool isSellOrder = (type == ORDER_TYPE_SELL_LIMIT);

      //--- Cancel pending jika open positions sudah >= maxPos
      if(posFull)
      {
         g_trade.OrderDelete(ticket);
         LogWrite("[CANCEL] " + (isBuyOrder ? "BuyLimit" : "SellLimit") +
                  " #" + IntegerToString(ticket) +
                  " — positions full " + IntegerToString(openBT) + "/" + IntegerToString(maxPos));
         continue;
      }

      //--- Cancel BUY LIMIT jika bias sudah berubah ke Bearish
      if(isBuyOrder && !biasBuy)
      {
         g_trade.OrderDelete(ticket);
         LogWrite("[CANCEL] BuyLimit #" + IntegerToString(ticket) + " — bias berubah ke Bearish");
      }
      //--- Cancel SELL LIMIT jika bias sudah berubah ke Bullish
      if(isSellOrder && biasBuy)
      {
         g_trade.OrderDelete(ticket);
         LogWrite("[CANCEL] SellLimit #" + IntegerToString(ticket) + " — bias berubah ke Bullish");
      }
   }
}

//+------------------------------------------------------------------+
//  TP Swap: entry termurah → TP terjauh, entry termahal → TP terdekat
//  Posisi termahal close duluan = kurangi risiko exposure
//+------------------------------------------------------------------+
void ManageTPSwap()
{
   //--- Collect trending BUY positions (parallel arrays)
   ulong  tickets[];
   double entries[];
   double tps[];
   double sls[];
   int count = 0;

   for(int i = 0; i < PositionsTotal(); i++)
   {
      ulong ticket = PositionGetTicket(i);
      if(ticket <= 0) continue;
      if(PositionGetInteger(POSITION_MAGIC) != EA_MAGIC_BT) continue;
      if(PositionGetInteger(POSITION_TYPE) != POSITION_TYPE_BUY) continue;

      ArrayResize(tickets, count + 1);
      ArrayResize(entries, count + 1);
      ArrayResize(tps, count + 1);
      ArrayResize(sls, count + 1);
      tickets[count] = ticket;
      entries[count] = PositionGetDouble(POSITION_PRICE_OPEN);
      tps[count]     = PositionGetDouble(POSITION_TP);
      sls[count]     = PositionGetDouble(POSITION_SL);
      count++;
   }

   if(count < 2) return;

   //--- Sort by entry price ascending (bubble sort, count kecil)
   for(int i = 0; i < count - 1; i++)
      for(int j = i + 1; j < count; j++)
         if(entries[i] > entries[j])
         {
            ulong  tmpT = tickets[i]; tickets[i] = tickets[j]; tickets[j] = tmpT;
            double tmpE = entries[i];  entries[i] = entries[j];  entries[j] = tmpE;
            double tmpP = tps[i];      tps[i] = tps[j];          tps[j] = tmpP;
            double tmpS = sls[i];      sls[i] = sls[j];          sls[j] = tmpS;
         }

   //--- Collect TPs lalu sort descending (terbesar dulu)
   double sortedTP[];
   ArrayResize(sortedTP, count);
   for(int i = 0; i < count; i++) sortedTP[i] = tps[i];
   for(int i = 0; i < count - 1; i++)
      for(int j = i + 1; j < count; j++)
         if(sortedTP[i] < sortedTP[j])
         {
            double tmp = sortedTP[i];
            sortedTP[i] = sortedTP[j];
            sortedTP[j] = tmp;
         }

   //--- Assign: entry termurah (idx 0) → TP terbesar (sortedTP[0])
   //            entry termahal (idx count-1) → TP terkecil (sortedTP[count-1])
   for(int i = 0; i < count; i++)
   {
      double newTP = sortedTP[i];

      //--- Skip jika TP sudah sama
      if(MathAbs(newTP - tps[i]) < 0.01) continue;

      newTP = NormalizeDouble(newTP, 2);
      if(g_trade.PositionModify(tickets[i], sls[i], newTP))
      {
         double tpDist = newTP - entries[i];
         double slDist = entries[i] - sls[i];
         LogWrite("[TP-SWAP] #" + IntegerToString(tickets[i]) +
                  " Entry:" + DoubleToString(entries[i], 2) +
                  " TP:" + DoubleToString(tps[i], 2) +
                  " -> " + DoubleToString(newTP, 2) +
                  " RR:" + (slDist > 0 ? DoubleToString(tpDist / slDist, 1) : "n/a"));
      }
   }
}

//+------------------------------------------------------------------+
//  Stepped Trailing Stop — lock profit bertahap
//  Step 1: profit >= 1R ($25)  → SL ke entry + $2 (breakeven + buffer)
//  Step 2: profit >= 1.5R      → SL ke entry + 0.5R ($12.50)
//  Step 3: profit >= 2R        → SL ke entry + 1R ($25)
//  Jalan setiap tick, berlaku untuk BUY trending + sideways
//+------------------------------------------------------------------+
void ManageTrailing()
{
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      ulong ticket = PositionGetTicket(i);
      if(ticket <= 0) continue;
      long magic = PositionGetInteger(POSITION_MAGIC);
      if(magic != EA_MAGIC_BT && magic != EA_MAGIC_SIDEWAYS && magic != EA_MAGIC_DC) continue;
      long posType = PositionGetInteger(POSITION_TYPE);

      double entry = PositionGetDouble(POSITION_PRICE_OPEN);
      double curSL = PositionGetDouble(POSITION_SL);
      double curTP = PositionGetDouble(POSITION_TP);
      double bid   = SymbolInfoDouble(_Symbol, SYMBOL_BID);
      double ask   = SymbolInfoDouble(_Symbol, SYMBOL_ASK);

      //--- Hitung SL distance original (1R)
      double oneR;
      double newSL = curSL;

      if(posType == POSITION_TYPE_BUY)
      {
         if(curSL < entry)
            oneR = entry - curSL;
         else
            oneR = IH_MaxSLDollar;
         if(oneR < 2.0) continue;

         double floatProfit = bid - entry;
         double tpDist = curTP - entry;
         bool tightTP = (tpDist > 0 && tpDist < oneR);

         if(tightTP)
         {
            //--- Tight TP path (setelah ManageTPSwap assign TP lebih dekat)
            //    Scale partial/breakeven/trail ke TP distance

            //--- Partial close 50% at 50% TP dist
            if(floatProfit >= tpDist * 0.5 && !IsPartialDone(ticket))
            {
               double curVol = PositionGetDouble(POSITION_VOLUME);
               double closeVol = NormalizeDouble(curVol * 0.5, 2);
               if(closeVol >= 0.01 && closeVol < curVol)
               {
                  if(magic == EA_MAGIC_BT)
                     g_trade.PositionClosePartial(ticket, closeVol);
                  else
                     gs_trade.PositionClosePartial(ticket, closeVol);
                  AddPartialDone(ticket);
                  LogWrite("[PARTIAL-TTP] #" + IntegerToString(ticket) +
                           " Close:" + DoubleToString(closeVol, 2) +
                           " of " + DoubleToString(curVol, 2) +
                           " @ 50%TP=$" + DoubleToString(floatProfit, 2));
               }
            }

            //--- Step 3: profit >= 80% TP dist → lock 40% + ATR trail
            if(floatProfit >= tpDist * 0.8)
            {
               double dynATR = g_detector.GetATR(0);
               double lockMin = entry + tpDist * 0.4;
               double atrSL = (dynATR > 0) ? bid - dynATR * 1.5 : lockMin;
               newSL = MathMax(atrSL, lockMin);
            }
            //--- Step 2: profit >= 60% TP dist → lock 20%
            else if(floatProfit >= tpDist * 0.6)
               newSL = entry + tpDist * 0.2;
            //--- Step 1: profit >= 40% TP dist → breakeven
            else if(floatProfit >= tpDist * 0.4)
            {
               double trailATR = g_detector.GetATR(0);
               double buffer = (trailATR > 0) ? MathMax(1.0, MathMin(trailATR * 0.3, 5.0)) : 2.0;
               newSL = entry + buffer;
            }
         }
         else
         {
            //--- Normal path: threshold berdasar 1R (SL distance)

            //--- Partial close 50% at 1R (once per position)
            if(floatProfit >= oneR && !IsPartialDone(ticket))
            {
               double curVol = PositionGetDouble(POSITION_VOLUME);
               double closeVol = NormalizeDouble(curVol * 0.5, 2);
               if(closeVol >= 0.01 && closeVol < curVol)
               {
                  if(magic == EA_MAGIC_BT)
                     g_trade.PositionClosePartial(ticket, closeVol);
                  else
                     gs_trade.PositionClosePartial(ticket, closeVol);
                  AddPartialDone(ticket);
                  LogWrite("[PARTIAL] #" + IntegerToString(ticket) +
                           " Close:" + DoubleToString(closeVol, 2) +
                           " of " + DoubleToString(curVol, 2) +
                           " @ 1R=$" + DoubleToString(floatProfit, 2));
               }
            }

            //--- Step 3: profit >= 2R → lock 1R + ATR dynamic trail
            if(floatProfit >= oneR * 2.0)
            {
               double dynATR = g_detector.GetATR(0);
               double atrSL = (dynATR > 0) ? bid - dynATR * 1.5 : entry + oneR;
               newSL = MathMax(atrSL, entry + oneR);
            }
            //--- Step 2: profit >= 1.5R → lock 0.5R profit
            else if(floatProfit >= oneR * 1.5)
               newSL = entry + oneR * 0.5;
            //--- Step 1: profit >= 1R → breakeven + ATR-adaptive buffer
            else if(floatProfit >= oneR)
            {
               double trailATR = g_detector.GetATR(0);
               double buffer = (trailATR > 0) ? MathMax(1.0, MathMin(trailATR * 0.3, 5.0)) : 2.0;
               newSL = entry + buffer;
            }
         }

         //--- Hanya geser SL naik, jangan turun
         newSL = NormalizeDouble(newSL, 2);
         if(newSL > curSL + 0.01)
         {
            if(magic == EA_MAGIC_BT)
               g_trade.PositionModify(ticket, newSL, curTP);
            else
               gs_trade.PositionModify(ticket, newSL, curTP);

            LogWrite("[TRAIL] #" + IntegerToString(ticket) +
                     (magic == EA_MAGIC_BT ? " TR" : " SW") +
                     " Entry:" + DoubleToString(entry, 2) +
                     " SL:" + DoubleToString(curSL, 2) +
                     " -> " + DoubleToString(newSL, 2) +
                     " Profit:$" + DoubleToString(floatProfit, 2) +
                     (tightTP ? " TTP" : ""));
         }
      }
      else if(posType == POSITION_TYPE_SELL)
      {
         if(curSL > entry)
            oneR = curSL - entry;
         else
            oneR = IH_MaxSLDollar;
         if(oneR < 2.0) continue;

         double floatProfit = entry - ask;

         //--- Drop Catcher: ATR-based trailing, no partial close
         if(magic == EA_MAGIC_DC)
         {
            double dcATR = g_detector.GetATR(0);
            if(dcATR <= 0) continue;
            if(floatProfit >= oneR * 1.5)
            {
               newSL = ask + dcATR * DropCatcher_TrailATR;
               newSL = NormalizeDouble(newSL, 2);
               if(newSL < curSL - 0.01)
               {
                  gdc_trade.PositionModify(ticket, newSL, curTP);
                  LogWrite("[DC-TRAIL] #" + IntegerToString(ticket) +
                           " Entry:" + DoubleToString(entry, 2) +
                           " SL:" + DoubleToString(curSL, 2) +
                           " -> " + DoubleToString(newSL, 2) +
                           " Profit:$" + DoubleToString(floatProfit, 2));
               }
            }
            continue;
         }

         //--- Normal SELL: partial close 50% at 1R (once per position)
         if(floatProfit >= oneR && !IsPartialDone(ticket))
         {
            double curVol = PositionGetDouble(POSITION_VOLUME);
            double closeVol = NormalizeDouble(curVol * 0.5, 2);
            if(closeVol >= 0.01 && closeVol < curVol)
            {
               g_trade.PositionClosePartial(ticket, closeVol);
               AddPartialDone(ticket);
               LogWrite("[PARTIAL] #" + IntegerToString(ticket) +
                        " SELL Close:" + DoubleToString(closeVol, 2) +
                        " of " + DoubleToString(curVol, 2) +
                        " @ 1R=$" + DoubleToString(floatProfit, 2));
            }
         }

         if(floatProfit >= oneR * 2.0)
         {
            double dynATR = g_detector.GetATR(0);
            double atrSL = (dynATR > 0) ? ask + dynATR * 1.5 : entry - oneR;
            newSL = MathMin(atrSL, entry - oneR);
         }
         else if(floatProfit >= oneR * 1.5)
            newSL = entry - oneR * 0.5;
         else if(floatProfit >= oneR)
         {
            double trailATR = g_detector.GetATR(0);
            double buffer = (trailATR > 0) ? MathMax(1.0, MathMin(trailATR * 0.3, 5.0)) : 2.0;
            newSL = entry - buffer;
         }

         newSL = NormalizeDouble(newSL, 2);
         if(newSL < curSL - 0.01)
         {
            g_trade.PositionModify(ticket, newSL, curTP);
            LogWrite("[TRAIL] #" + IntegerToString(ticket) +
                     " TR-SELL Entry:" + DoubleToString(entry, 2) +
                     " SL:" + DoubleToString(curSL, 2) +
                     " -> " + DoubleToString(newSL, 2) +
                     " Profit:$" + DoubleToString(floatProfit, 2));
         }
      }
   }
}

//+------------------------------------------------------------------+
//  Close individual position if floating profit and open > 5 hours
//+------------------------------------------------------------------+
void CheckTimedProfitClose()
{
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      ulong ticket = PositionGetTicket(i);
      if(ticket <= 0) continue;
      long magic = PositionGetInteger(POSITION_MAGIC);
      if(magic != EA_MAGIC_BT && magic != EA_MAGIC_SIDEWAYS && magic != EA_MAGIC_DC) continue;

      double profit = PositionGetDouble(POSITION_PROFIT) +
                      PositionGetDouble(POSITION_SWAP);
      double lot = PositionGetDouble(POSITION_VOLUME);
      double minProfit = (lot / 0.01) * 15.0;  // $15 per 0.01 lot
      if(profit < minProfit) continue;

      datetime openTime = (datetime)PositionGetInteger(POSITION_TIME);
      if((int)(TimeCurrent() - openTime) < 18000) continue;  // < 5 jam

      //--- Profit + open > 5 jam → close
      if(magic == EA_MAGIC_BT)
         g_trade.PositionClose(ticket);
      else if(magic == EA_MAGIC_SIDEWAYS)
         gs_trade.PositionClose(ticket);
      else
         gdc_trade.PositionClose(ticket);
   }
}

#endif
