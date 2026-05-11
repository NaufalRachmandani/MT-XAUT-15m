# V1 vs V2Live Parameter Diff

V2Live starts from V1 and uses a cent-account micro-risk profile.

| Parameter | V1 Default | V2Live Value | Changed |
| --- | ---: | ---: | --- |
| BT_RiskPercent | 3 | 1 | yes |
| BT_UseFixedLot | false | false |  |
| BT_FixedLot | 0.01 | 0.01 |  |
| BT_CompoundingPer | 500 | 1000 | yes |
| BT_MaxLotCap | 1.5 | 0.25 | yes |
| BT_EnableSideways | true | true |  |
| BT_MinSLDollar | 25 | 25 |  |
| BT_MaxSLDollar | 25 | 25 |  |
| EnableReversalClose | true | true |  |
| SidewaysMinMethods | 4 | 4 |  |
| BB_Period | 20 | 20 |  |
| BB_Deviation | 2 | 2 |  |
| KC_ATRMultiplier | 1.5 | 1.5 |  |
| MTF_H1_ADX_Max | 25 | 25 |  |
| MTF_H4_ADX_Max | 22 | 22 |  |
| ATR_CompressionRatio | 0.65 | 0.65 |  |
| BBWidth_RelativeRatio | 0.7 | 0.7 |  |
| PriceRange_ATRMult | 2.3 | 2.3 |  |
| RangeBounce_LotMult | 0.25 | 0.15 | yes |
| RangeBounce_MaxBuy | 2 | 1 | yes |
| RangeBounce_MaxSell | 0 | 0 |  |
| RangeBounce_EntryPct | 0.25 | 0.25 |  |
| RangeBounce_MaxEntriesPerRange | 4 | 2 | yes |
| Guard_EnableBadHourFilter | true | true |  |
| Guard_BlockHour04 | true | true |  |
| Guard_BlockHour05 | true | true |  |
| Guard_BlockHour10 | true | true |  |
| Guard_BlockHour11 | true | true |  |
| Guard_EnableDropCatcherHourFilter | true | true |  |
| Guard_DC_BlockHour00 | true | true |  |
| Guard_DC_BlockHour01 | true | true |  |
| Guard_DC_BlockHour10 | true | true |  |
| Guard_DC_BlockHour23 | true | true |  |
| Guard_MaxTrendPosLowBalance | 3 | 2 | yes |
| Guard_MaxTrendPosMidBalance | 3 | 3 |  |
| Guard_MaxTrendPosHighBalance | 2 | 2 |  |
| EnableDropCatcher | true | true |  |
| DropCatcher_BodyATR | 1.8 | 1.8 |  |
| DropCatcher_MinBodyDlr | 12 | 12 |  |
| DropCatcher_VolMult | 1.3 | 1.3 |  |
| DropCatcher_MaxATR | 15 | 15 |  |
| DropCatcher_SL_ATR | 2 | 2 |  |
| DropCatcher_RR | 3 | 3 |  |
| DropCatcher_LotMult | 0.25 | 0.1 | yes |
| DropCatcher_TrailATR | 1 | 1 |  |
