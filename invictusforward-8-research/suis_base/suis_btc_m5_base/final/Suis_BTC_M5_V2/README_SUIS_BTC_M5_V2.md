# Suis_BTC_M5_V2

Baked no-set EX5 for BTC M5 cent-account validation.

- EA folder: `Suis_BTC_M5_V2`
- EX5: `Suis_BTC_M5_V2.ex5`
- Baked variant: `v2_mt5opt_r15_rr76_score42`
- Symbol used for validation: `BTCUSDc`
- Period: `M5`
- Execution: `20 ms`
- Tick model: real ticks, `100%` history quality
- Expert parameters: empty in tester ini

## Validation Result

- Net profit: `10173.73` USC
- Profit percent: `1017.37%`
- Profit factor: `2.00`
- Trades: `193`
- Win rate: `74.09%`
- Max DD Any: `28.60%`
- Largest loss: `-623.38` USC

## Migration

Attach `Suis_BTC_M5_V2.ex5` to a fresh `BTCUSDc,M5` chart on the cent account, then migrate the MT5 VPS. Do not load a `.set` file; defaults are baked into the EX5.
