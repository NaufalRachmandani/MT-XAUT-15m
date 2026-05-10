#property copyright "Learning project"
#property version   "1.00"
#property strict

#include <Trade/Trade.mqh>

enum PositionSizingMode
  {
   POSITION_SIZE_FIXED_LOT = 0,
   POSITION_SIZE_PERCENT_RISK = 1
  };

input int                InpFastMAPeriod       = 20;
input int                InpSlowMAPeriod       = 50;
input int                InpATRPeriod          = 14;
input double             InpSLATRMultiplier    = 2.0;
input double             InpTakeProfitRR       = 2.0;
input int                InpMaxSpreadPoints    = 20;
input PositionSizingMode InpSizingMode         = POSITION_SIZE_FIXED_LOT;
input double             InpFixedLotSize       = 0.01;
input double             InpRiskPercent        = 1.0;
input ulong              InpMagicNumber        = 20260410;

CTrade trade;

int      fastMaHandle    = INVALID_HANDLE;
int      slowMaHandle    = INVALID_HANDLE;
int      atrHandle       = INVALID_HANDLE;
datetime lastBarTime     = 0;

int OnInit()
  {
   if(InpFastMAPeriod <= 0 || InpSlowMAPeriod <= 0 || InpATRPeriod <= 0)
     {
      Print("Indicator periods must be greater than zero.");
      return(INIT_PARAMETERS_INCORRECT);
     }

   if(InpFastMAPeriod >= InpSlowMAPeriod)
     {
      Print("Fast MA period must be smaller than slow MA period.");
      return(INIT_PARAMETERS_INCORRECT);
     }

   if(InpSLATRMultiplier <= 0.0 || InpTakeProfitRR <= 0.0)
     {
      Print("ATR stop multiplier and risk reward must be greater than zero.");
      return(INIT_PARAMETERS_INCORRECT);
     }

   if(InpFixedLotSize <= 0.0)
     {
      Print("Fixed lot size must be greater than zero.");
      return(INIT_PARAMETERS_INCORRECT);
     }

   if(InpRiskPercent <= 0.0)
     {
      Print("Risk percent must be greater than zero.");
      return(INIT_PARAMETERS_INCORRECT);
     }

   fastMaHandle = iMA(_Symbol, PERIOD_CURRENT, InpFastMAPeriod, 0, MODE_EMA, PRICE_CLOSE);
   slowMaHandle = iMA(_Symbol, PERIOD_CURRENT, InpSlowMAPeriod, 0, MODE_EMA, PRICE_CLOSE);
   atrHandle    = iATR(_Symbol, PERIOD_CURRENT, InpATRPeriod);

   if(fastMaHandle == INVALID_HANDLE || slowMaHandle == INVALID_HANDLE || atrHandle == INVALID_HANDLE)
     {
      Print("Failed to create indicator handles.");
      return(INIT_FAILED);
     }

   trade.SetExpertMagicNumber((int)InpMagicNumber);
   trade.SetTypeFillingBySymbol(_Symbol);
   trade.SetDeviationInPoints(10);

   return(INIT_SUCCEEDED);
  }

void OnDeinit(const int reason)
  {
   if(fastMaHandle != INVALID_HANDLE)
      IndicatorRelease(fastMaHandle);

   if(slowMaHandle != INVALID_HANDLE)
      IndicatorRelease(slowMaHandle);

   if(atrHandle != INVALID_HANDLE)
      IndicatorRelease(atrHandle);
  }

void OnTick()
  {
   if(!IsNewBar())
      return;

   if(HasOpenPosition())
      return;

   if(!IsSpreadAllowed())
      return;

   double fastMa[3];
   double slowMa[3];
   double atrValues[2];

   ArraySetAsSeries(fastMa, true);
   ArraySetAsSeries(slowMa, true);
   ArraySetAsSeries(atrValues, true);

   if(CopyBuffer(fastMaHandle, 0, 0, 3, fastMa) < 3)
     {
      Print("Unable to read fast MA values.");
      return;
     }

   if(CopyBuffer(slowMaHandle, 0, 0, 3, slowMa) < 3)
     {
      Print("Unable to read slow MA values.");
      return;
     }

   if(CopyBuffer(atrHandle, 0, 0, 2, atrValues) < 2)
     {
      Print("Unable to read ATR values.");
      return;
     }

   double atr = atrValues[1];
   if(atr <= 0.0)
     {
      Print("ATR value is invalid.");
      return;
     }

   bool bullishCross = fastMa[2] <= slowMa[2] && fastMa[1] > slowMa[1];
   bool bearishCross = fastMa[2] >= slowMa[2] && fastMa[1] < slowMa[1];

   if(!bullishCross && !bearishCross)
      return;

   double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);

   if(ask <= 0.0 || bid <= 0.0)
     {
      Print("Invalid market prices received.");
      return;
     }

   if(bullishCross)
      OpenPosition(ORDER_TYPE_BUY, ask, atr);

   if(bearishCross)
      OpenPosition(ORDER_TYPE_SELL, bid, atr);
  }

bool IsNewBar()
  {
   datetime currentBarTime = iTime(_Symbol, PERIOD_CURRENT, 0);
   if(currentBarTime == 0)
      return(false);

   if(currentBarTime == lastBarTime)
      return(false);

   lastBarTime = currentBarTime;
   return(true);
  }

bool HasOpenPosition()
  {
   for(int i = PositionsTotal() - 1; i >= 0; i--)
     {
      ulong ticket = PositionGetTicket(i);
      if(ticket == 0)
         continue;

      string positionSymbol = PositionGetString(POSITION_SYMBOL);
      long   positionMagic  = PositionGetInteger(POSITION_MAGIC);

      if(positionSymbol == _Symbol && (ulong)positionMagic == InpMagicNumber)
         return(true);
     }

   return(false);
  }

bool IsSpreadAllowed()
  {
   double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);

   if(ask <= 0.0 || bid <= 0.0)
      return(false);

   double spreadPoints = (ask - bid) / _Point;
   if(spreadPoints > InpMaxSpreadPoints)
     {
      Print("Spread filter blocked entry. Current spread: ", DoubleToString(spreadPoints, 1), " points.");
      return(false);
     }

   return(true);
  }

void OpenPosition(ENUM_ORDER_TYPE orderType, double entryPrice, double atr)
  {
   double stopDistance = atr * InpSLATRMultiplier;
   if(stopDistance <= 0.0)
      return;

   double volume = CalculateVolume(stopDistance);
   if(volume <= 0.0)
     {
      Print("Calculated volume is invalid.");
      return;
     }

   double stopLoss   = 0.0;
   double takeProfit = 0.0;

   if(orderType == ORDER_TYPE_BUY)
     {
      stopLoss   = entryPrice - stopDistance;
      takeProfit = entryPrice + (stopDistance * InpTakeProfitRR);
      stopLoss   = NormalizePrice(stopLoss);
      takeProfit = NormalizePrice(takeProfit);

      if(!trade.Buy(volume, _Symbol, 0.0, stopLoss, takeProfit, "Learning MA crossover"))
         Print("Buy order failed. Retcode: ", trade.ResultRetcode(), " ", trade.ResultRetcodeDescription());
     }
   else if(orderType == ORDER_TYPE_SELL)
     {
      stopLoss   = entryPrice + stopDistance;
      takeProfit = entryPrice - (stopDistance * InpTakeProfitRR);
      stopLoss   = NormalizePrice(stopLoss);
      takeProfit = NormalizePrice(takeProfit);

      if(!trade.Sell(volume, _Symbol, 0.0, stopLoss, takeProfit, "Learning MA crossover"))
         Print("Sell order failed. Retcode: ", trade.ResultRetcode(), " ", trade.ResultRetcodeDescription());
     }
  }

double CalculateVolume(double stopDistance)
  {
   double volume = InpFixedLotSize;

   if(InpSizingMode == POSITION_SIZE_PERCENT_RISK)
     {
      double accountBalance = AccountInfoDouble(ACCOUNT_BALANCE);
      double riskAmount     = accountBalance * (InpRiskPercent / 100.0);
      double tickValue      = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE);
      double tickSize       = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);

      if(riskAmount <= 0.0 || tickValue <= 0.0 || tickSize <= 0.0)
         return(0.0);

      double lossPerLot = (stopDistance / tickSize) * tickValue;
      if(lossPerLot <= 0.0)
         return(0.0);

      volume = riskAmount / lossPerLot;
     }

   return(NormalizeVolume(volume));
  }

double NormalizeVolume(double volume)
  {
   double minVolume  = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
   double maxVolume  = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX);
   double stepVolume = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);

   if(minVolume <= 0.0 || maxVolume <= 0.0 || stepVolume <= 0.0)
      return(0.0);

   volume = MathMax(volume, minVolume);
   volume = MathMin(volume, maxVolume);
   volume = MathFloor(volume / stepVolume) * stepVolume;
   volume = MathMax(volume, minVolume);

   int volumeDigits = CountVolumeDigits(stepVolume);

   return(NormalizeDouble(volume, volumeDigits));
  }

int CountVolumeDigits(double stepVolume)
  {
   int volumeDigits = 0;

   while(volumeDigits < 8)
     {
      double scaled = stepVolume * MathPow(10.0, volumeDigits);
      if(MathAbs(scaled - MathRound(scaled)) < 1e-8)
         return(volumeDigits);

      volumeDigits++;
     }

   return(8);
  }

double NormalizePrice(double price)
  {
   return(NormalizeDouble(price, (int)SymbolInfoInteger(_Symbol, SYMBOL_DIGITS)));
  }
