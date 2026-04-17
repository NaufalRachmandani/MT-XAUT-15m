#property script_show_inputs

void OnStart()
  {
   const string symbol = _Symbol;
   const bool selected = SymbolSelect(symbol, true);
   PrintFormat("SelectStartSymbol: symbol=%s selected=%s", symbol, selected ? "true" : "false");
  }
