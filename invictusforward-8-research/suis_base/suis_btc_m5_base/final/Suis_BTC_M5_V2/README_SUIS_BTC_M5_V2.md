# Suis_BTC_M5_V2

Baked no-set EX5 for BTC M5 cent-account validation.

- EA folder: `Suis_BTC_M5_V2`
- EX5: `Suis_BTC_M5_V2.ex5`
- Baked variant: `v2_qnty_r155_rr76_h17_zone`
- Symbol used for validation: `BTCUSDc`
- Period: `M5`
- Execution: `20 ms`
- Tick model: real ticks, `100%` history quality
- Expert parameters: empty in tester ini

## Validation Result

- Net profit: `14326.68` USC
- Profit percent: `1432.67%`
- Profit factor: `2.09`
- Trades: `266`
- Win rate: `74.44%`
- Max DD Any: `27.79%`
- Largest loss: `-620.94` USC

## Migration

Attach `Suis_BTC_M5_V2.ex5` to a fresh `BTCUSDc,M5` chart on the cent account, then migrate the MT5 VPS. Do not load a `.set` file; defaults are baked into the EX5.
