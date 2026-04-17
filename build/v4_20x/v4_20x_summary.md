# v4 20x Summary

Champion: iterasi 04 `buy_break_024`
Guardrail: PF >= 1.18, trades >= 3200, equity DD <= 28.0%

| Iter | Name | Accepted | Net Profit | PF | WR | Trades | Eq DD | Buy PnL | break | bosq | premium | tests | fvg | Takeaway |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 01 | baseline_v3_clone | yes | 573362.84 | 1.19 | 49.82% | 3428 | 23.08% | 492723.47 | 0 | 0 | 0 | 0 | 0 | Baseline champion awal. |
| 02 | buy_premium_cap_075 | no | 297445.55 | 1.17 | 48.73% | 2598 | 28.69% | 229994.20 | 0 | 0 | 1239 | 0 | 0 | Ditolak: drawdown melewati guardrail. |
| 03 | buy_premium_cap_060 | no | 254420.24 | 1.16 | 48.63% | 2546 | 32.52% | 191212.67 | 0 | 0 | 1317 | 0 | 0 | Ditolak: drawdown melewati guardrail. |
| 04 | buy_break_024 | yes | 638117.15 | 1.21 | 50.12% | 3398 | 23.04% | 556706.63 | 69 | 0 | 0 | 0 | 0 | Dibawa ke baseline berikutnya. |
| 05 | buy_break_028 | no | 619877.42 | 1.21 | 50.10% | 3363 | 23.41% | 537762.14 | 118 | 0 | 0 | 0 | 0 | Buy filter struktural aktif, tetapi terlalu banyak opportunity yang terpotong. |
| 06 | buy_highscore_impulsive | no | 547363.46 | 1.21 | 50.39% | 3221 | 22.65% | 453611.09 | 72 | 243 | 0 | 0 | 0 | Buy filter struktural aktif, tetapi terlalu banyak opportunity yang terpotong. |
| 07 | buy_low_rr_145 | no | 615521.67 | 1.21 | 50.10% | 3401 | 23.37% | 535267.78 | 69 | 0 | 0 | 0 | 0 | Buy filter struktural aktif, tetapi terlalu banyak opportunity yang terpotong. |
| 08 | buy_low_rr_135_lot_090 | no | 592578.00 | 1.21 | 50.19% | 3393 | 22.71% | 509632.92 | 69 | 0 | 0 | 0 | 0 | Buy filter struktural aktif, tetapi terlalu banyak opportunity yang terpotong. |
| 09 | buy_mid_rr_155 | no | 573224.31 | 1.20 | 50.46% | 3397 | 23.15% | 497202.23 | 68 | 0 | 0 | 0 | 0 | Buy filter struktural aktif, tetapi terlalu banyak opportunity yang terpotong. |
| 10 | buy_breakeven_085r | no | 551880.97 | 1.20 | 51.55% | 3391 | 24.20% | 455530.88 | 69 | 0 | 0 | 0 | 0 | Buy filter struktural aktif, tetapi terlalu banyak opportunity yang terpotong. |
| 11 | buy_breakeven_070r | no | 510769.87 | 1.20 | 52.86% | 3394 | 22.70% | 420527.45 | 70 | 0 | 0 | 0 | 0 | Buy filter struktural aktif, tetapi terlalu banyak opportunity yang terpotong. |
| 12 | buy_zone_tests_1 | no | 386311.34 | 1.18 | 49.69% | 2898 | 29.81% | 310882.86 | 73 | 0 | 0 | 632 | 0 | Ditolak: drawdown melewati guardrail. |
| 13 | buy_low_fvg | no | 529804.23 | 1.21 | 49.84% | 3124 | 24.65% | 446796.76 | 74 | 0 | 0 | 0 | 371 | Ditolak: trade count turun terlalu jauh. |
| 14 | combo_premium075_break024 | no | 320686.18 | 1.19 | 48.93% | 2561 | 36.53% | 250207.47 | 79 | 0 | 1214 | 0 | 0 | Ditolak: drawdown melewati guardrail. |
| 15 | combo_premium075_lowrr145 | no | 308266.55 | 1.18 | 48.93% | 2561 | 37.36% | 238503.02 | 79 | 0 | 1214 | 0 | 0 | Ditolak: drawdown melewati guardrail. |
| 16 | combo_break024_lowrr145 | no | 615521.67 | 1.21 | 50.10% | 3401 | 23.37% | 535267.78 | 69 | 0 | 0 | 0 | 0 | Buy filter struktural aktif, tetapi terlalu banyak opportunity yang terpotong. |
| 17 | combo_premium075_break024_be085 | no | 306655.82 | 1.19 | 50.08% | 2562 | 23.69% | 226897.32 | 79 | 0 | 1214 | 0 | 0 | Ditolak: trade count turun terlalu jauh. |
| 18 | combo_premium075_break024_zone1 | no | 186820.77 | 1.14 | 48.54% | 2326 | 39.24% | 129529.28 | 80 | 0 | 866 | 649 | 0 | Ditolak: drawdown melewati guardrail. |
| 19 | combo_premium075_break024_lowrr145_be085 | no | 297528.39 | 1.19 | 50.08% | 2562 | 24.24% | 218366.94 | 79 | 0 | 1214 | 0 | 0 | Ditolak: trade count turun terlalu jauh. |
| 20 | champion_challenge | no | 214579.77 | 1.18 | 50.09% | 2346 | 28.10% | 145176.92 | 80 | 283 | 1197 | 0 | 0 | Ditolak: drawdown melewati guardrail. |
