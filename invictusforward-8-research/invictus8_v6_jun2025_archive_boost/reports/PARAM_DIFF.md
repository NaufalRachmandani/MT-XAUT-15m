# Param Diff: V5 Max vs V6 Selected Profit-Balanced

Selected V6 set: `invictusforward-8-research/invictus8_v6_jun2025_archive_boost/sets/InvictusForward8_V6_selected_profit_balanced_not_live.set`

| Parameter | V5 max | V6 selected | Note |
| --- | ---: | ---: | --- |
| `BT_RiskPercent` | 1 | 1 | Same risk percent in both selected aggressive profiles. |
| `BT_CompoundingPer` | 125 | 100 | V6 profit-balanced increases compounding versus V5 max. |
| `BT_MaxLotCap` | 1.5 | 1.75 | V6 profit-balanced increases max lot cap versus V5 max. |
| `RangeBounce_LotMult` | 0.15 | 0.15 |  |
| `RangeBounce_MaxBuy` | 1 | 1 |  |
| `RangeBounce_MaxSell` | 0 | 0 |  |
| `RangeBounce_MaxEntriesPerRange` | 2 | 2 |  |
| `Guard_MaxTrendPosLowBalance` | 2 | 2 |  |
| `Guard_MaxTrendPosMidBalance` | 3 | 3 |  |
| `Guard_MaxTrendPosHighBalance` | 2 | 2 |  |
| `V5_EnableTrendQualityScaling` | true | true |  |
| `V5_TrendScore85LotMult` | 0.6 | 0.6 |  |
| `V5_TrendScore90LotMult` | 0.85 | 0.85 |  |
| `V5_TrendScore95LotMult` | 1 | 1 |  |
| `V5_TrendHour09LotMult` | 0.7 | 0.7 |  |
| `V5_TrendHour12LotMult` | 0.8 | 0.8 |  |
| `V5_TrendHour15LotMult` | 0.55 | 0.55 |  |
| `V6_EnableArchiveHourScaling` | not present | true | New archive guard master switch. |
| `V6_TrendHour07LotMult` | not present | 0.8 | Reduce H07 trend exposure from archive diagnosis. |
| `V6_TrendHour08LotMult` | not present | 0.6 | Reduce H08 trend exposure from archive diagnosis. |
| `V6_TrendHour13LotMult` | not present | 1 | Multiplier present but selected set hard-blocks H13. |
| `V6_TrendHour16LotMult` | not present | 0.4 | Reduce H16 trend exposure without full block. |
| `V6_BlockTrendHour13` | not present | true | Hard block worst archive trend cluster. |
| `V6_BlockTrendHour16` | not present | false |  |
| `V6_BlockRangeBounceHour01` | not present | true | Block RB leakage in full archive. |
| `V6_BlockRangeBounceHour17` | not present | true | Block RB leakage in full archive. |
