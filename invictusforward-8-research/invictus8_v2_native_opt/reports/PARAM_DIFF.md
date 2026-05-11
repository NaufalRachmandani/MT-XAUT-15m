# V1 vs V2 Parameter Diff

V1 is the first tuned version. V2 is the selected native MT5 optimization profile.

| Parameter | V1 Default | V2 Selected | Changed |
| --- | ---: | ---: | --- |
| BT_RiskPercent | 3 | 3 |  |
| BT_UseFixedLot | false | false |  |
| BT_FixedLot | 0.01 | 0.01 |  |
| BT_CompoundingPer | 500 | 400 | yes |
| BT_MaxLotCap | 1.5 | 1.5 |  |
| BT_EnableSideways | true | true |  |
| BT_MinSLDollar | 25 | 25 |  |
| BT_MaxSLDollar | 25 | 25 |  |
| EnableReversalClose | true | true |  |
| SidewaysMinMethods | 4 | 3 | yes |
| BB_Period | 20 | 20 |  |
| BB_Deviation | 2 | 2 |  |
| KC_ATRMultiplier | 1.5 | 1.5 |  |
| MTF_H1_ADX_Max | 25 | 21 | yes |
| MTF_H4_ADX_Max | 22 | 23 | yes |
| ATR_CompressionRatio | 0.65 | 0.65 |  |
| BBWidth_RelativeRatio | 0.7 | 0.7 |  |
| PriceRange_ATRMult | 2.3 | 2 | yes |
| RangeBounce_LotMult | 0.25 | 0.5 | yes |
| RangeBounce_MaxBuy | 2 | 3 | yes |
| RangeBounce_MaxSell | 0 | 1 | yes |
| RangeBounce_EntryPct | 0.25 | 0.35 | yes |
| RangeBounce_MaxEntriesPerRange | 4 | 6 | yes |
| Guard_EnableBadHourFilter | true | true |  |
| Guard_BlockHour04 | true | true |  |
| Guard_BlockHour05 | true | true |  |
| Guard_BlockHour10 | true | false | yes |
| Guard_BlockHour11 | true | false | yes |
| Guard_EnableDropCatcherHourFilter | true | true |  |
| Guard_DC_BlockHour00 | true | false | yes |
| Guard_DC_BlockHour01 | true | true |  |
| Guard_DC_BlockHour10 | true | false | yes |
| Guard_DC_BlockHour23 | true | false | yes |
| Guard_MaxTrendPosLowBalance | 3 | 3 |  |
| Guard_MaxTrendPosMidBalance | 3 | 2 | yes |
| Guard_MaxTrendPosHighBalance | 2 | 4 | yes |
| EnableDropCatcher | true | true |  |
| DropCatcher_BodyATR | 1.8 | 1.8 |  |
| DropCatcher_MinBodyDlr | 12 | 10 | yes |
| DropCatcher_VolMult | 1.3 | 1.6 | yes |
| DropCatcher_MaxATR | 15 | 20 | yes |
| DropCatcher_SL_ATR | 2 | 2.2 | yes |
| DropCatcher_RR | 3 | 4 | yes |
| DropCatcher_LotMult | 0.25 | 0.5 | yes |
| DropCatcher_TrailATR | 1 | 0.8 | yes |
