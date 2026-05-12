//+------------------------------------------------------------------+
//|                                                   IH_Logger.mqh  |
//|                       InvictusHelper — File-Based Logging        |
//+------------------------------------------------------------------+
#ifndef IH_LOGGER_MQH
#define IH_LOGGER_MQH

int g_logHandle = INVALID_HANDLE;

int TimeToStruct2Year(datetime t)  { MqlDateTime d; TimeToStruct(t,d); return d.year; }
int TimeToStruct2Month(datetime t) { MqlDateTime d; TimeToStruct(t,d); return d.mon; }

void LogOpen()
{
   string fname = "InvictusForward-8_" +
                  IntegerToString(TimeToStruct2Year(TimeCurrent())) +
                  StringFormat("%02d", TimeToStruct2Month(TimeCurrent())) +
                  ".log";
   g_logHandle = FileOpen(fname, FILE_WRITE | FILE_READ | FILE_TXT | FILE_SHARE_READ | FILE_ANSI);
   if(g_logHandle != INVALID_HANDLE)
      FileSeek(g_logHandle, 0, SEEK_END);
}

void LogClose()
{
   if(g_logHandle != INVALID_HANDLE)
   {
      FileClose(g_logHandle);
      g_logHandle = INVALID_HANDLE;
   }
}

void LogWrite(string msg)
{
   string line = TimeToString(TimeCurrent(), TIME_DATE|TIME_SECONDS) + " | " + msg;
   Print(line);
   if(g_logHandle != INVALID_HANDLE)
   {
      FileWriteString(g_logHandle, line + "\n");
      FileFlush(g_logHandle);
   }
}

#endif
