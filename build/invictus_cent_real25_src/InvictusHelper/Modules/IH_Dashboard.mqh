//+------------------------------------------------------------------+
//|                                               IH_Dashboard.mqh   |
//|          InvictusHelper — Dashboard using Comment() for simplicity|
//|          No pixel alignment issues, always fits                   |
//+------------------------------------------------------------------+
#ifndef IH_DASHBOARD_MQH
#define IH_DASHBOARD_MQH

#include "IH_Config.mqh"

//+------------------------------------------------------------------+
void DrawDashboardComment(int wins, int losses, int expired, int active,
                          double totalProfit, int totalSignals)
{
   if(!IH_ShowDashboard) { Comment(""); return; }

   int totalResolved = wins + losses;
   double winRate = totalResolved > 0 ? (double)wins / totalResolved * 100.0 : 0;
   string plSign = totalProfit >= 0 ? "+" : "";

   string txt = "";
   txt += "══════════════════════════════\n";
   txt += "     INVICTUS HELPER v1.0\n";
   txt += "══════════════════════════════\n";
   txt += StringFormat("  Signals:    %d\n", totalSignals);
   txt += StringFormat("  Win:        %d\n", wins);
   txt += StringFormat("  Loss:       %d\n", losses);
   txt += StringFormat("  WinRate:    %.0f%%\n", winRate);
   txt += StringFormat("  Expired:    %d\n", expired);
   txt += StringFormat("  Active:     %d\n", active);
   txt += "──────────────────────────────\n";
   txt += StringFormat("  Net P&L:    %s$%.0f /0.01lot\n", plSign, totalProfit);
   txt += "──────────────────────────────\n";
   txt += StringFormat("  SL: $%.0f-$%.0f   TP: RR%.1f\n",
                        IH_MinSLDollar, IH_MaxSLDollar, IH_TP1_RR);
   txt += "══════════════════════════════";

   Comment(txt);
}

#endif
