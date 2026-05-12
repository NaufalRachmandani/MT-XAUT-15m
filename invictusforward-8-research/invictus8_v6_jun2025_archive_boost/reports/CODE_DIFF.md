# Code Diff: V5 Max vs V6 Archive Boost

V6 starts from the V5 boost source and keeps the same core modules: trend breakout, range bounce, drop catcher, V5 score/hour quality scaling, bad-hour guards, and drop-catcher guards.

## Added Inputs

`IH_Config.mqh` adds a new `V6 Archive Guard` input group:

| Input | Purpose |
| --- | --- |
| `V6_EnableArchiveHourScaling` | Master switch for archive-derived controls. |
| `V6_TrendHour07LotMult` | Scales trend lots at hour 07. |
| `V6_TrendHour08LotMult` | Scales trend lots at hour 08. |
| `V6_TrendHour13LotMult` | Scales trend lots at hour 13 unless hard-blocked. |
| `V6_TrendHour16LotMult` | Scales trend lots at hour 16. |
| `V6_BlockTrendHour13` | Hard-blocks the worst archive trend hour cluster. |
| `V6_BlockTrendHour16` | Optional hard block for trend H16. |
| `V6_BlockRangeBounceHour01` | Blocks range-bounce H01 leakage seen in full archive. |
| `V6_BlockRangeBounceHour17` | Blocks range-bounce H17 leakage seen in full archive. |

## Logic Changes

- `V5TrendQualityLotMultiplier(score, hour)` now applies optional V6 hour multipliers and hard blocks after V5 score/hour scaling.
- `ProcessSideways()` now optionally blocks range-bounce entries at H01 and H17.
- Order comments changed from `IF8V5Q_*` to `IF8V6A_*` for trade diagnosis.
- `OnTester()` CSV logging was expanded to include every V6 archive guard input.

## Not Changed

- No live trading behavior was enabled.
- Core entry detectors were not rewritten.
- V5 guardrails remain active by default in the V6 selected set.
- Drop-catcher logic remains unchanged except the diagnostic order comment.
