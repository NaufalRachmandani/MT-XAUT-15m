# Invictus Forward-8 V8 Risk-Certified Stress Validation

Authority: native MT5 Strategy Tester `.htm` reports. Python was used only for orchestration, parsing, and Monte Carlo trade-order stress from native report deals.

Safety: all generated tester configs use `AllowLiveTrading=0`, `Visual=0`, `ShutdownTerminal=1`, `UseRemote=0`, `UseCloud=0`, and sound events disabled.

## Candidate Ranking

| Rank | Profile | Score | Live-ready | Min cent YTD net | Max cent YTD DD | Max cent YTD LL | Min USD archive net | Max USD archive DD | Max MC p95 DD | Fail reasons |
| ---: | --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 1 | V6 profit-balanced raw | -3,746.46 | no | 13,840.67 | 17.52% | 1,041.40 | 19,701.34 | 16.61% | 128.24% | Monte Carlo p95 DD > 40% |
| 2 | V8 V5max micro 200 cap1.00 | -12,798.08 | no | 7,894.02 | 21.28% | 370.30 | 11,549.85 | 67.36% | 74.94% | USD archive DD > 45% under delay stress; Monte Carlo p95 DD > 40% |
| 3 | V7 soft H8 m25 raw | -13,000.11 | no | 14,270.04 | 17.49% | 1,203.40 | 34,190.53 | 30.17% | 242.72% | Monte Carlo p95 DD > 40% |
| 4 | V8 V6balance micro 250 cap0.75 | -17,540.64 | no | 2,440.25 | 36.03% | 147.90 | 5,413.13 | 31.20% | 47.59% | cent YTD DD > 30% under delay stress; Monte Carlo p95 DD > 40% |
| 5 | V8 V5max guard moderate | -17,899.33 | no | 1,934.43 | 27.28% | 277.70 | -396.43 | 46.16% | 42.31% | usd_real38:usd_jun2025_now: net <= 0 at delay 100; usd_real38:usd_jun2025_now: net <= 0 at delay 300; USD archive DD > 45% under delay stress; Monte Carlo p95 DD > 40% |
| 6 | V8 V7H8m25 micro 250 cap0.75 | -18,161.77 | no | 2,490.85 | 36.03% | 162.00 | 6,041.59 | 33.96% | 52.36% | cent YTD DD > 30% under delay stress; Monte Carlo p95 DD > 40% |
| 7 | V8 V5max guard strict | -19,956.53 | no | -167.50 | 28.28% | 192.90 | -396.43 | 46.16% | 39.64% | cent:ytd_2026: net <= 0 at delay 0; cent:ytd_2026: net <= 0 at delay 100; cent:ytd_2026: net <= 0 at delay 300; cent:ytd_2026: net <= 0 at delay 500; usd_real38:usd_jun2025_now: net <= 0 at delay 100; usd_real38:usd_jun2025_now: net <= 0 at delay 300; USD archive DD > 45% under delay stress |
| 8 | V8 V6balance micro 200 cap1.00 | -22,265.27 | no | 4,000.96 | 47.86% | 244.70 | 6,761.84 | 40.94% | 59.27% | cent YTD DD > 30% under delay stress; Monte Carlo p95 DD > 40% |
| 9 | V8 V7H8m25 micro 200 cap1.00 | -22,540.54 | no | 3,759.59 | 46.69% | 254.50 | 7,626.15 | 42.19% | 64.19% | cent YTD DD > 30% under delay stress; Monte Carlo p95 DD > 40% |
| 10 | V5 max raw | -23,160.61 | no | 18,178.99 | 30.29% | 3,732.50 | 17,946.58 | 28.51% | 262.05% | cent YTD DD > 30% under delay stress; Monte Carlo p95 DD > 40% |
| 11 | V8 V6balance guard moderate | -24,475.06 | no | -215.70 | 34.50% | 241.10 | -495.55 | 56.18% | 49.55% | cent:ytd_2026: net <= 0 at delay 0; cent:ytd_2026: net <= 0 at delay 100; cent:ytd_2026: net <= 0 at delay 300; cent:ytd_2026: net <= 0 at delay 500; usd_real38:usd_jun2025_now: net <= 0 at delay 100; usd_real38:usd_jun2025_now: net <= 0 at delay 300; cent YTD DD > 30% under delay stress; USD archive DD > 45% under delay stress; Monte Carlo p95 DD > 40% |
| 12 | V8 V7H8m25 guard moderate | -24,475.06 | no | -215.70 | 34.50% | 241.10 | -495.55 | 56.18% | 49.55% | cent:ytd_2026: net <= 0 at delay 0; cent:ytd_2026: net <= 0 at delay 100; cent:ytd_2026: net <= 0 at delay 300; cent:ytd_2026: net <= 0 at delay 500; usd_real38:usd_jun2025_now: net <= 0 at delay 100; usd_real38:usd_jun2025_now: net <= 0 at delay 300; cent YTD DD > 30% under delay stress; USD archive DD > 45% under delay stress; Monte Carlo p95 DD > 40% |

## Native Stress Matrix

| Profile | Account | Window | Delay | Net | PF | Trades | Win rate | Eq DD | Largest loss | History | Validation |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- | ---: | --- | --- |
| V5 max raw | cent | last_month | 0 | 2,571.90 | 7.35 | 37 | 83.78% | 492.40000000 (13.75840970%) | 162.00 | 100% real ticks | OK |
| V5 max raw | cent | last_month | 100 | 2,562.40 | 8.01 | 38 | 86.84% | 492.40000000 (13.79541434%) | 162.00 | 100% real ticks | OK |
| V5 max raw | cent | last_month | 300 | 2,574.50 | 8.08 | 38 | 86.84% | 492.40000000 (13.80663201%) | 162.00 | 100% real ticks | OK |
| V5 max raw | cent | last_month | 500 | 2,572.60 | 8.10 | 38 | 86.84% | 492.40000000 (13.77997158%) | 160.40 | 100% real ticks | OK |
| V5 max raw | cent | oos_may | 0 | 975.90 | 48.60 | 11 | 90.91% | 287.20000000 (14.64484218%) | 20.50 | 100% real ticks | OK |
| V5 max raw | cent | oos_may | 100 | 1,022.00 | 0.00 | 11 | 100.00% | 287.20000000 (14.30920233%) | 0.00 | 100% real ticks | OK |
| V5 max raw | cent | oos_may | 300 | 1,025.40 | 0.00 | 11 | 100.00% | 287.20000000 (14.35138917%) | 0.00 | 100% real ticks | OK |
| V5 max raw | cent | oos_may | 500 | 1,022.60 | 0.00 | 11 | 100.00% | 287.20000000 (14.33491390%) | 0.00 | 100% real ticks | OK |
| V5 max raw | cent | ytd_2026 | 0 | 18,178.99 | 2.42 | 167 | 79.64% | 8 332.80000000 (30.28810579%) | 3,732.50 | 100% real ticks | OK |
| V5 max raw | cent | ytd_2026 | 100 | 19,839.91 | 2.52 | 169 | 81.07% | 8 347.10000000 (28.59868081%) | 3,732.50 | 100% real ticks | OK |
| V5 max raw | cent | ytd_2026 | 300 | 19,831.01 | 2.51 | 169 | 81.07% | 8 318.60000000 (28.53760249%) | 3,732.50 | 100% real ticks | OK |
| V5 max raw | cent | ytd_2026 | 500 | 18,727.89 | 2.46 | 169 | 81.07% | 8 342.50000000 (29.71992929%) | 3,732.50 | 100% real ticks | OK |
| V5 max raw | usd_real38 | usd_jun2025_now | 100 | 17,946.58 | 1.76 | 410 | 69.76% | 7 555.61 (28.51%) | 3,741.15 | 100% real ticks | OK |
| V5 max raw | usd_real38 | usd_jun2025_now | 300 | 26,559.57 | 2.00 | 413 | 70.46% | 8 352.76 (23.26%) | 3,741.15 | 100% real ticks | OK |
| V5 max raw | usd_real38 | usd_jun_dec_2025 | 100 | -57.18 | 0.99 | 241 | 62.66% | 4 692.72 (87.19%) | 1,028.82 | 100% real ticks | OK |
| V5 max raw | usd_real38 | usd_jun_dec_2025 | 300 | 51.49 | 1.00 | 243 | 63.37% | 5 253.59 (87.48%) | 1,154.28 | 100% real ticks | OK |
| V6 profit-balanced raw | cent | last_month | 0 | 2,594.02 | 6.26 | 36 | 86.11% | 615.40000000 (17.17064970%) | 231.40 | 100% real ticks | OK |
| V6 profit-balanced raw | cent | last_month | 100 | 2,587.42 | 6.23 | 36 | 86.11% | 615.40000000 (17.20280876%) | 231.40 | 100% real ticks | OK |
| V6 profit-balanced raw | cent | last_month | 300 | 2,602.62 | 6.28 | 36 | 86.11% | 615.40000000 (17.22351170%) | 231.40 | 100% real ticks | OK |
| V6 profit-balanced raw | cent | last_month | 500 | 2,600.62 | 6.30 | 36 | 86.11% | 615.40000000 (17.18071646%) | 229.10 | 100% real ticks | OK |
| V6 profit-balanced raw | cent | oos_may | 0 | 1,124.00 | 0.00 | 10 | 100.00% | 369.20000000 (17.49431387%) | 0.00 | 100% real ticks | OK |
| V6 profit-balanced raw | cent | oos_may | 100 | 1,126.60 | 0.00 | 10 | 100.00% | 369.20000000 (17.47361446%) | 0.00 | 100% real ticks | OK |
| V6 profit-balanced raw | cent | oos_may | 300 | 1,130.60 | 0.00 | 10 | 100.00% | 369.20000000 (17.53835922%) | 0.00 | 100% real ticks | OK |
| V6 profit-balanced raw | cent | oos_may | 500 | 1,126.40 | 0.00 | 10 | 100.00% | 369.20000000 (17.51838671%) | 0.00 | 100% real ticks | OK |
| V6 profit-balanced raw | cent | ytd_2026 | 0 | 15,817.91 | 3.05 | 156 | 80.13% | 2 954.60000000 (17.52451893%) | 1,041.40 | 100% real ticks | OK |
| V6 profit-balanced raw | cent | ytd_2026 | 100 | 15,865.94 | 2.99 | 158 | 81.01% | 2 954.60000000 (17.47494363%) | 1,041.40 | 100% real ticks | OK |
| V6 profit-balanced raw | cent | ytd_2026 | 300 | 13,841.97 | 2.85 | 157 | 80.89% | 2 585.00000000 (17.48989257%) | 902.60 | 100% real ticks | OK |
| V6 profit-balanced raw | cent | ytd_2026 | 500 | 13,840.67 | 2.86 | 157 | 80.89% | 2 585.00000000 (17.43774439%) | 893.60 | 100% real ticks | OK |
| V6 profit-balanced raw | usd_real38 | usd_jun2025_now | 100 | 19,701.34 | 2.21 | 375 | 70.67% | 3 449.54 (16.61%) | 1,265.60 | 100% real ticks | OK |
| V6 profit-balanced raw | usd_real38 | usd_jun2025_now | 300 | 20,275.15 | 2.22 | 374 | 70.59% | 3 449.54 (16.26%) | 1,288.62 | 100% real ticks | OK |
| V6 profit-balanced raw | usd_real38 | usd_jun_dec_2025 | 100 | 62.61 | 1.01 | 216 | 63.43% | 1 538.95 (63.77%) | 574.84 | 100% real ticks | OK |
| V6 profit-balanced raw | usd_real38 | usd_jun_dec_2025 | 300 | 122.03 | 1.02 | 216 | 63.43% | 1 683.03 (65.57%) | 599.84 | 100% real ticks | OK |
| V7 soft H8 m25 raw | cent | last_month | 0 | 2,273.82 | 5.61 | 34 | 85.29% | 574.60000000 (17.50696226%) | 231.40 | 100% real ticks | OK |
| V7 soft H8 m25 raw | cent | last_month | 100 | 2,263.52 | 5.57 | 34 | 85.29% | 574.60000000 (17.56207579%) | 231.40 | 100% real ticks | OK |
| V7 soft H8 m25 raw | cent | last_month | 300 | 2,276.12 | 5.62 | 34 | 85.29% | 574.60000000 (17.59003213%) | 231.40 | 100% real ticks | OK |
| V7 soft H8 m25 raw | cent | last_month | 500 | 2,275.32 | 5.64 | 34 | 85.29% | 574.60000000 (17.54009588%) | 229.10 | 100% real ticks | OK |
| V7 soft H8 m25 raw | cent | oos_may | 0 | 1,124.00 | 0.00 | 10 | 100.00% | 369.20000000 (17.49431387%) | 0.00 | 100% real ticks | OK |
| V7 soft H8 m25 raw | cent | oos_may | 100 | 1,126.60 | 0.00 | 10 | 100.00% | 369.20000000 (17.47361446%) | 0.00 | 100% real ticks | OK |
| V7 soft H8 m25 raw | cent | oos_may | 300 | 1,130.60 | 0.00 | 10 | 100.00% | 369.20000000 (17.53835922%) | 0.00 | 100% real ticks | OK |
| V7 soft H8 m25 raw | cent | oos_may | 500 | 1,126.40 | 0.00 | 10 | 100.00% | 369.20000000 (17.51838671%) | 0.00 | 100% real ticks | OK |
| V7 soft H8 m25 raw | cent | ytd_2026 | 0 | 16,255.64 | 2.97 | 157 | 80.25% | 2 995.40000000 (17.33515405%) | 1,203.40 | 100% real ticks | OK |
| V7 soft H8 m25 raw | cent | ytd_2026 | 100 | 15,676.75 | 2.91 | 157 | 80.89% | 2 913.40000000 (17.44650333%) | 1,134.00 | 100% real ticks | OK |
| V7 soft H8 m25 raw | cent | ytd_2026 | 300 | 14,329.24 | 2.83 | 156 | 80.77% | 2 667.20000000 (17.47169209%) | 1,041.40 | 100% real ticks | OK |
| V7 soft H8 m25 raw | cent | ytd_2026 | 500 | 14,270.04 | 2.81 | 156 | 80.77% | 2 667.20000000 (17.48578074%) | 1,031.00 | 100% real ticks | OK |
| V7 soft H8 m25 raw | usd_real38 | usd_jun2025_now | 100 | 34,190.53 | 2.19 | 377 | 70.56% | 5 826.23 (30.17%) | 2,738.30 | 100% real ticks | OK |
| V7 soft H8 m25 raw | usd_real38 | usd_jun2025_now | 300 | 36,500.33 | 2.25 | 378 | 70.37% | 6 323.37 (29.36%) | 2,738.30 | 100% real ticks | OK |
| V7 soft H8 m25 raw | usd_real38 | usd_jun_dec_2025 | 100 | 1,449.78 | 1.15 | 218 | 63.30% | 2 504.12 (58.87%) | 817.60 | 100% real ticks | OK |
| V7 soft H8 m25 raw | usd_real38 | usd_jun_dec_2025 | 300 | 1,371.29 | 1.14 | 219 | 63.01% | 2 548.67 (58.60%) | 842.38 | 100% real ticks | OK |
| V8 V5max guard moderate | cent | last_month | 0 | 1,528.30 | 5.30 | 33 | 81.82% | 369.20000000 (14.68166009%) | 162.00 | 100% real ticks | OK |
| V8 V5max guard moderate | cent | last_month | 100 | 1,382.10 | 5.05 | 36 | 80.56% | 347.90000000 (24.68247651%) | 162.00 | 100% real ticks | OK |
| V8 V5max guard moderate | cent | last_month | 300 | 1,388.40 | 5.08 | 36 | 80.56% | 354.30000000 (24.96121606%) | 162.00 | 100% real ticks | OK |
| V8 V5max guard moderate | cent | last_month | 500 | 1,390.40 | 5.10 | 36 | 80.56% | 353.60000000 (24.88910412%) | 160.40 | 100% real ticks | OK |
| V8 V5max guard moderate | cent | oos_may | 0 | 828.50 | 41.41 | 10 | 90.00% | 246.20000000 (13.43739766%) | 20.50 | 100% real ticks | OK |
| V8 V5max guard moderate | cent | oos_may | 100 | 859.10 | 0.00 | 10 | 100.00% | 246.20000000 (13.21666309%) | 0.00 | 100% real ticks | OK |
| V8 V5max guard moderate | cent | oos_may | 300 | 861.70 | 0.00 | 10 | 100.00% | 246.20000000 (13.25294719%) | 0.00 | 100% real ticks | OK |
| V8 V5max guard moderate | cent | oos_may | 500 | 858.60 | 0.00 | 10 | 100.00% | 246.20000000 (13.24439184%) | 0.00 | 100% real ticks | OK |
| V8 V5max guard moderate | cent | ytd_2026 | 0 | 1,934.43 | 1.82 | 146 | 76.03% | 636.20000000 (27.27973373%) | 277.70 | 100% real ticks | OK |
| V8 V5max guard moderate | cent | ytd_2026 | 100 | 3,181.63 | 2.43 | 145 | 78.62% | 574.60000000 (13.71381918%) | 254.50 | 100% real ticks | OK |
| V8 V5max guard moderate | cent | ytd_2026 | 300 | 2,803.73 | 2.25 | 147 | 77.55% | 600.20000000 (26.59477599%) | 254.50 | 100% real ticks | OK |
| V8 V5max guard moderate | cent | ytd_2026 | 500 | 2,792.73 | 2.24 | 147 | 77.55% | 598.90000000 (26.65765526%) | 252.00 | 100% real ticks | OK |
| V8 V5max guard moderate | usd_real38 | usd_jun2025_now | 100 | -396.43 | 0.00 | 2 | 0.00% | 517.40 (46.16%) | 199.79 | 100% real ticks | OK |
| V8 V5max guard moderate | usd_real38 | usd_jun2025_now | 300 | -396.15 | 0.00 | 2 | 0.00% | 517.40 (46.14%) | 199.79 | 100% real ticks | OK |
| V8 V5max guard moderate | usd_real38 | usd_jun_dec_2025 | 100 | -396.43 | 0.00 | 2 | 0.00% | 517.40 (46.16%) | 199.79 | 100% real ticks | OK |
| V8 V5max guard moderate | usd_real38 | usd_jun_dec_2025 | 300 | -396.15 | 0.00 | 2 | 0.00% | 517.40 (46.14%) | 199.79 | 100% real ticks | OK |
| V8 V5max guard strict | cent | last_month | 0 | 1,242.80 | 4.44 | 36 | 77.78% | 328.40000000 (14.61112777%) | 162.00 | 100% real ticks | OK |
| V8 V5max guard strict | cent | last_month | 100 | 1,276.70 | 5.01 | 35 | 80.00% | 328.40000000 (14.39465732%) | 138.80 | 100% real ticks | OK |
| V8 V5max guard strict | cent | last_month | 300 | 1,282.20 | 5.04 | 35 | 80.00% | 328.40000000 (14.42310648%) | 138.80 | 100% real ticks | OK |
| V8 V5max guard strict | cent | last_month | 500 | 1,280.40 | 5.05 | 35 | 80.00% | 328.40000000 (14.39907537%) | 137.50 | 100% real ticks | OK |
| V8 V5max guard strict | cent | oos_may | 0 | 828.70 | 41.42 | 10 | 90.00% | 246.20000000 (13.43593102%) | 20.50 | 100% real ticks | OK |
| V8 V5max guard strict | cent | oos_may | 100 | 856.50 | 0.00 | 10 | 100.00% | 246.20000000 (13.23513601%) | 0.00 | 100% real ticks | OK |
| V8 V5max guard strict | cent | oos_may | 300 | 860.30 | 0.00 | 10 | 100.00% | 246.20000000 (13.26294241%) | 0.00 | 100% real ticks | OK |
| V8 V5max guard strict | cent | oos_may | 500 | 856.90 | 0.00 | 10 | 100.00% | 246.20000000 (13.25651518%) | 0.00 | 100% real ticks | OK |
| V8 V5max guard strict | cent | ytd_2026 | 0 | -167.50 | 0.13 | 3 | 66.67% | 328.10000000 (28.26986042%) | 192.90 | 100% real ticks | OK |
| V8 V5max guard strict | cent | ytd_2026 | 100 | -167.40 | 0.13 | 3 | 66.67% | 328.20000000 (28.27360441%) | 192.90 | 100% real ticks | OK |
| V8 V5max guard strict | cent | ytd_2026 | 300 | -167.30 | 0.13 | 3 | 66.67% | 328.30000000 (28.27734711%) | 192.90 | 100% real ticks | OK |
| V8 V5max guard strict | cent | ytd_2026 | 500 | -167.20 | 0.13 | 3 | 66.67% | 328.20000000 (28.26873385%) | 192.90 | 100% real ticks | OK |
| V8 V5max guard strict | usd_real38 | usd_jun2025_now | 100 | -396.43 | 0.00 | 2 | 0.00% | 517.40 (46.16%) | 199.79 | 100% real ticks | OK |
| V8 V5max guard strict | usd_real38 | usd_jun2025_now | 300 | -396.15 | 0.00 | 2 | 0.00% | 517.40 (46.14%) | 199.79 | 100% real ticks | OK |
| V8 V5max guard strict | usd_real38 | usd_jun_dec_2025 | 100 | -396.43 | 0.00 | 2 | 0.00% | 517.40 (46.16%) | 199.79 | 100% real ticks | OK |
| V8 V5max guard strict | usd_real38 | usd_jun_dec_2025 | 300 | -396.15 | 0.00 | 2 | 0.00% | 517.40 (46.14%) | 199.79 | 100% real ticks | OK |
| V8 V5max micro 200 cap1.00 | cent | last_month | 0 | 1,390.88 | 6.77 | 37 | 83.78% | 230.00000000 (17.93118976%) | 92.50 | 100% real ticks | OK |
| V8 V5max micro 200 cap1.00 | cent | last_month | 100 | 1,385.58 | 7.98 | 35 | 85.71% | 205.60000000 (16.89426262%) | 69.50 | 100% real ticks | OK |
| V8 V5max micro 200 cap1.00 | cent | last_month | 300 | 1,392.98 | 8.06 | 35 | 85.71% | 208.70000000 (17.07044080%) | 69.50 | 100% real ticks | OK |
| V8 V5max micro 200 cap1.00 | cent | last_month | 500 | 1,391.48 | 8.07 | 35 | 85.71% | 208.50000000 (17.04989822%) | 68.80 | 100% real ticks | OK |
| V8 V5max micro 200 cap1.00 | cent | oos_may | 0 | 495.60 | 25.18 | 11 | 90.91% | 123.00000000 (8.32036799%) | 20.50 | 100% real ticks | OK |
| V8 V5max micro 200 cap1.00 | cent | oos_may | 100 | 555.70 | 0.00 | 11 | 100.00% | 125.40000000 (11.59286309%) | 0.00 | 100% real ticks | OK |
| V8 V5max micro 200 cap1.00 | cent | oos_may | 300 | 557.50 | 0.00 | 11 | 100.00% | 125.40000000 (11.59286309%) | 0.00 | 100% real ticks | OK |
| V8 V5max micro 200 cap1.00 | cent | oos_may | 500 | 555.70 | 0.00 | 11 | 100.00% | 125.40000000 (11.57894737%) | 0.00 | 100% real ticks | OK |
| V8 V5max micro 200 cap1.00 | cent | ytd_2026 | 0 | 8,217.38 | 3.08 | 163 | 79.75% | 1 068.10000000 (21.01988953%) | 370.30 | 100% real ticks | OK |
| V8 V5max micro 200 cap1.00 | cent | ytd_2026 | 100 | 7,894.02 | 3.06 | 166 | 81.33% | 999.20000000 (20.88708486%) | 347.20 | 100% real ticks | OK |
| V8 V5max micro 200 cap1.00 | cent | ytd_2026 | 300 | 7,958.08 | 3.03 | 166 | 81.33% | 1 036.50000000 (21.27603759%) | 370.30 | 100% real ticks | OK |
| V8 V5max micro 200 cap1.00 | cent | ytd_2026 | 500 | 8,050.78 | 3.06 | 166 | 81.33% | 1 035.90000000 (21.09312950%) | 366.60 | 100% real ticks | OK |
| V8 V5max micro 200 cap1.00 | usd_real38 | usd_jun2025_now | 100 | 11,549.85 | 2.01 | 408 | 69.85% | 1 842.20 (64.34%) | 506.24 | 100% real ticks | OK |
| V8 V5max micro 200 cap1.00 | usd_real38 | usd_jun2025_now | 300 | 14,540.36 | 2.16 | 410 | 70.49% | 2 146.77 (67.36%) | 621.29 | 100% real ticks | OK |
| V8 V5max micro 200 cap1.00 | usd_real38 | usd_jun_dec_2025 | 100 | 304.85 | 1.05 | 239 | 62.34% | 1 842.20 (64.34%) | 326.21 | 100% real ticks | OK |
| V8 V5max micro 200 cap1.00 | usd_real38 | usd_jun_dec_2025 | 300 | 428.54 | 1.06 | 239 | 62.76% | 2 146.77 (67.36%) | 376.39 | 100% real ticks | OK |
| V8 V6balance guard moderate | cent | last_month | 0 | 999.02 | 3.25 | 34 | 82.35% | 476.60000000 (29.53236254%) | 231.40 | 100% real ticks | OK |
| V8 V6balance guard moderate | cent | last_month | 100 | 1,696.32 | 5.26 | 33 | 81.82% | 451.40000000 (16.82054572%) | 208.30 | 100% real ticks | OK |
| V8 V6balance guard moderate | cent | last_month | 300 | 1,703.42 | 5.29 | 33 | 81.82% | 451.40000000 (16.86516551%) | 208.30 | 100% real ticks | OK |
| V8 V6balance guard moderate | cent | last_month | 500 | 1,701.92 | 5.31 | 33 | 81.82% | 451.40000000 (16.82368023%) | 206.20 | 100% real ticks | OK |
| V8 V6balance guard moderate | cent | oos_may | 0 | 1,104.60 | 0.00 | 9 | 100.00% | 369.20000000 (17.65662363%) | 0.00 | 100% real ticks | OK |
| V8 V6balance guard moderate | cent | oos_may | 100 | 1,103.80 | 0.00 | 9 | 100.00% | 369.20000000 (17.66422659%) | 0.00 | 100% real ticks | OK |
| V8 V6balance guard moderate | cent | oos_may | 300 | 1,109.20 | 0.00 | 9 | 100.00% | 369.20000000 (17.71848155%) | 0.00 | 100% real ticks | OK |
| V8 V6balance guard moderate | cent | oos_may | 500 | 1,104.80 | 0.00 | 9 | 100.00% | 369.20000000 (17.69979385%) | 0.00 | 100% real ticks | OK |
| V8 V6balance guard moderate | cent | ytd_2026 | 0 | -215.70 | 0.11 | 3 | 66.67% | 413.10000000 (34.49974946%) | 241.10 | 100% real ticks | OK |
| V8 V6balance guard moderate | cent | ytd_2026 | 100 | -215.60 | 0.11 | 3 | 66.67% | 413.20000000 (34.50233801%) | 241.10 | 100% real ticks | OK |
| V8 V6balance guard moderate | cent | ytd_2026 | 300 | -215.50 | 0.11 | 3 | 66.67% | 413.30000000 (34.50492570%) | 241.10 | 100% real ticks | OK |
| V8 V6balance guard moderate | cent | ytd_2026 | 500 | -215.40 | 0.11 | 3 | 66.67% | 413.20000000 (34.49657706%) | 241.10 | 100% real ticks | OK |
| V8 V6balance guard moderate | usd_real38 | usd_jun2025_now | 100 | -495.55 | 0.00 | 2 | 0.00% | 646.75 (56.18%) | 249.74 | 100% real ticks | OK |
| V8 V6balance guard moderate | usd_real38 | usd_jun2025_now | 300 | -495.19 | 0.00 | 2 | 0.00% | 646.75 (56.16%) | 249.74 | 100% real ticks | OK |
| V8 V6balance guard moderate | usd_real38 | usd_jun_dec_2025 | 100 | -495.55 | 0.00 | 2 | 0.00% | 646.75 (56.18%) | 249.74 | 100% real ticks | OK |
| V8 V6balance guard moderate | usd_real38 | usd_jun_dec_2025 | 300 | -495.19 | 0.00 | 2 | 0.00% | 646.75 (56.16%) | 249.74 | 100% real ticks | OK |
| V8 V6balance micro 200 cap1.00 | cent | last_month | 0 | 1,045.48 | 5.74 | 36 | 86.11% | 208.20000000 (16.23162482%) | 92.50 | 100% real ticks | OK |
| V8 V6balance micro 200 cap1.00 | cent | last_month | 100 | 994.08 | 6.01 | 34 | 85.29% | 183.80000000 (15.10294489%) | 69.50 | 100% real ticks | OK |
| V8 V6balance micro 200 cap1.00 | cent | last_month | 300 | 999.08 | 6.06 | 34 | 85.29% | 187.00000000 (15.29550757%) | 69.50 | 100% real ticks | OK |
| V8 V6balance micro 200 cap1.00 | cent | last_month | 500 | 998.48 | 6.07 | 34 | 85.29% | 186.60000000 (15.25904560%) | 68.80 | 100% real ticks | OK |
| V8 V6balance micro 200 cap1.00 | cent | oos_may | 0 | 498.80 | 0.00 | 10 | 100.00% | 142.90000000 (13.28807885%) | 0.00 | 100% real ticks | OK |
| V8 V6balance micro 200 cap1.00 | cent | oos_may | 100 | 499.60 | 0.00 | 10 | 100.00% | 142.90000000 (13.30663935%) | 0.00 | 100% real ticks | OK |
| V8 V6balance micro 200 cap1.00 | cent | oos_may | 300 | 501.30 | 0.00 | 10 | 100.00% | 142.90000000 (13.31159758%) | 0.00 | 100% real ticks | OK |
| V8 V6balance micro 200 cap1.00 | cent | oos_may | 500 | 499.20 | 0.00 | 10 | 100.00% | 142.90000000 (13.29425993%) | 0.00 | 100% real ticks | OK |
| V8 V6balance micro 200 cap1.00 | cent | ytd_2026 | 0 | 4,000.96 | 2.51 | 149 | 79.19% | 789.70000000 (47.85710234%) | 231.40 | 100% real ticks | OK |
| V8 V6balance micro 200 cap1.00 | cent | ytd_2026 | 100 | 4,305.09 | 2.56 | 153 | 80.39% | 649.70000000 (39.33949848%) | 244.70 | 100% real ticks | OK |
| V8 V6balance micro 200 cap1.00 | cent | ytd_2026 | 300 | 4,310.82 | 2.54 | 153 | 80.39% | 698.50000000 (40.90893384%) | 244.70 | 100% real ticks | OK |
| V8 V6balance micro 200 cap1.00 | cent | ytd_2026 | 500 | 4,311.79 | 2.55 | 153 | 80.39% | 686.50000000 (40.65688738%) | 242.30 | 100% real ticks | OK |
| V8 V6balance micro 200 cap1.00 | usd_real38 | usd_jun2025_now | 100 | 6,761.84 | 1.87 | 363 | 69.42% | 942.05 (40.94%) | 368.18 | 100% real ticks | OK |
| V8 V6balance micro 200 cap1.00 | usd_real38 | usd_jun2025_now | 300 | 7,394.03 | 1.95 | 364 | 69.51% | 1 013.81 (19.03%) | 391.18 | 100% real ticks | OK |
| V8 V6balance micro 200 cap1.00 | usd_real38 | usd_jun_dec_2025 | 100 | 425.67 | 1.11 | 207 | 61.35% | 697.93 (35.65%) | 199.94 | 100% real ticks | OK |
| V8 V6balance micro 200 cap1.00 | usd_real38 | usd_jun_dec_2025 | 300 | 417.93 | 1.11 | 207 | 61.35% | 709.03 (36.16%) | 199.94 | 100% real ticks | OK |
| V8 V6balance micro 250 cap0.75 | cent | last_month | 0 | 749.02 | 5.34 | 32 | 84.38% | 145.90000000 (12.09362438%) | 69.50 | 100% real ticks | OK |
| V8 V6balance micro 250 cap0.75 | cent | last_month | 100 | 723.02 | 5.16 | 32 | 84.38% | 145.00000000 (12.16319688%) | 69.50 | 100% real ticks | OK |
| V8 V6balance micro 250 cap0.75 | cent | last_month | 300 | 727.32 | 5.22 | 32 | 84.38% | 147.70000000 (12.33999777%) | 69.50 | 100% real ticks | OK |
| V8 V6balance micro 250 cap0.75 | cent | last_month | 500 | 727.52 | 5.23 | 32 | 84.38% | 147.10000000 (12.28678954%) | 68.80 | 100% real ticks | OK |
| V8 V6balance micro 250 cap0.75 | cent | oos_may | 0 | 356.10 | 0.00 | 10 | 100.00% | 103.40000000 (9.78703265%) | 0.00 | 100% real ticks | OK |
| V8 V6balance micro 250 cap0.75 | cent | oos_may | 100 | 357.30 | 0.00 | 10 | 100.00% | 103.40000000 (9.79723328%) | 0.00 | 100% real ticks | OK |
| V8 V6balance micro 250 cap0.75 | cent | oos_may | 300 | 357.90 | 0.00 | 10 | 100.00% | 103.40000000 (9.80001896%) | 0.00 | 100% real ticks | OK |
| V8 V6balance micro 250 cap0.75 | cent | oos_may | 500 | 356.50 | 0.00 | 10 | 100.00% | 103.40000000 (9.79073951%) | 0.00 | 100% real ticks | OK |
| V8 V6balance micro 250 cap0.75 | cent | ytd_2026 | 0 | 2,755.55 | 2.47 | 146 | 78.77% | 501.30000000 (36.02611473%) | 147.90 | 100% real ticks | OK |
| V8 V6balance micro 250 cap0.75 | cent | ytd_2026 | 100 | 2,636.45 | 2.44 | 146 | 79.45% | 449.70000000 (32.26453098%) | 146.80 | 100% real ticks | OK |
| V8 V6balance micro 250 cap0.75 | cent | ytd_2026 | 300 | 2,440.25 | 2.35 | 146 | 79.45% | 448.90000000 (32.16789852%) | 146.80 | 100% real ticks | OK |
| V8 V6balance micro 250 cap0.75 | cent | ytd_2026 | 500 | 2,461.35 | 2.36 | 146 | 79.45% | 448.40000000 (32.12056012%) | 145.30 | 100% real ticks | OK |
| V8 V6balance micro 250 cap0.75 | usd_real38 | usd_jun2025_now | 100 | 5,413.13 | 1.86 | 362 | 69.34% | 673.65 (15.10%) | 276.13 | 100% real ticks | OK |
| V8 V6balance micro 250 cap0.75 | usd_real38 | usd_jun2025_now | 300 | 5,488.78 | 1.87 | 363 | 69.42% | 691.73 (31.20%) | 276.13 | 100% real ticks | OK |
| V8 V6balance micro 250 cap0.75 | usd_real38 | usd_jun_dec_2025 | 100 | 565.49 | 1.17 | 207 | 61.35% | 556.21 (28.08%) | 174.95 | 100% real ticks | OK |
| V8 V6balance micro 250 cap0.75 | usd_real38 | usd_jun_dec_2025 | 300 | 532.45 | 1.16 | 207 | 61.35% | 567.07 (28.97%) | 174.95 | 100% real ticks | OK |
| V8 V7H8m25 guard moderate | cent | last_month | 0 | 999.02 | 3.25 | 34 | 82.35% | 476.60000000 (29.53236254%) | 231.40 | 100% real ticks | OK |
| V8 V7H8m25 guard moderate | cent | last_month | 100 | 1,696.32 | 5.26 | 33 | 81.82% | 451.40000000 (16.82054572%) | 208.30 | 100% real ticks | OK |
| V8 V7H8m25 guard moderate | cent | last_month | 300 | 1,703.42 | 5.29 | 33 | 81.82% | 451.40000000 (16.86516551%) | 208.30 | 100% real ticks | OK |
| V8 V7H8m25 guard moderate | cent | last_month | 500 | 1,701.92 | 5.31 | 33 | 81.82% | 451.40000000 (16.82368023%) | 206.20 | 100% real ticks | OK |
| V8 V7H8m25 guard moderate | cent | oos_may | 0 | 1,104.60 | 0.00 | 9 | 100.00% | 369.20000000 (17.65662363%) | 0.00 | 100% real ticks | OK |
| V8 V7H8m25 guard moderate | cent | oos_may | 100 | 1,103.80 | 0.00 | 9 | 100.00% | 369.20000000 (17.66422659%) | 0.00 | 100% real ticks | OK |
| V8 V7H8m25 guard moderate | cent | oos_may | 300 | 1,109.20 | 0.00 | 9 | 100.00% | 369.20000000 (17.71848155%) | 0.00 | 100% real ticks | OK |
| V8 V7H8m25 guard moderate | cent | oos_may | 500 | 1,104.80 | 0.00 | 9 | 100.00% | 369.20000000 (17.69979385%) | 0.00 | 100% real ticks | OK |
| V8 V7H8m25 guard moderate | cent | ytd_2026 | 0 | -215.70 | 0.11 | 3 | 66.67% | 413.10000000 (34.49974946%) | 241.10 | 100% real ticks | OK |
| V8 V7H8m25 guard moderate | cent | ytd_2026 | 100 | -215.60 | 0.11 | 3 | 66.67% | 413.20000000 (34.50233801%) | 241.10 | 100% real ticks | OK |
| V8 V7H8m25 guard moderate | cent | ytd_2026 | 300 | -215.50 | 0.11 | 3 | 66.67% | 413.30000000 (34.50492570%) | 241.10 | 100% real ticks | OK |
| V8 V7H8m25 guard moderate | cent | ytd_2026 | 500 | -215.40 | 0.11 | 3 | 66.67% | 413.20000000 (34.49657706%) | 241.10 | 100% real ticks | OK |
| V8 V7H8m25 guard moderate | usd_real38 | usd_jun2025_now | 100 | -495.55 | 0.00 | 2 | 0.00% | 646.75 (56.18%) | 249.74 | 100% real ticks | OK |
| V8 V7H8m25 guard moderate | usd_real38 | usd_jun2025_now | 300 | -495.19 | 0.00 | 2 | 0.00% | 646.75 (56.16%) | 249.74 | 100% real ticks | OK |
| V8 V7H8m25 guard moderate | usd_real38 | usd_jun_dec_2025 | 100 | -495.55 | 0.00 | 2 | 0.00% | 646.75 (56.18%) | 249.74 | 100% real ticks | OK |
| V8 V7H8m25 guard moderate | usd_real38 | usd_jun_dec_2025 | 300 | -495.19 | 0.00 | 2 | 0.00% | 646.75 (56.16%) | 249.74 | 100% real ticks | OK |
| V8 V7H8m25 micro 200 cap1.00 | cent | last_month | 0 | 982.38 | 5.45 | 34 | 85.29% | 186.50000000 (14.53985605%) | 92.50 | 100% real ticks | OK |
| V8 V7H8m25 micro 200 cap1.00 | cent | last_month | 100 | 836.98 | 5.21 | 32 | 84.38% | 182.30000000 (13.61686286%) | 69.50 | 100% real ticks | OK |
| V8 V7H8m25 micro 200 cap1.00 | cent | last_month | 300 | 840.78 | 5.26 | 32 | 84.38% | 182.30000000 (13.59452317%) | 69.50 | 100% real ticks | OK |
| V8 V7H8m25 micro 200 cap1.00 | cent | last_month | 500 | 840.28 | 5.27 | 32 | 84.38% | 182.30000000 (13.56014202%) | 68.80 | 100% real ticks | OK |
| V8 V7H8m25 micro 200 cap1.00 | cent | oos_may | 0 | 498.80 | 0.00 | 10 | 100.00% | 142.90000000 (13.28807885%) | 0.00 | 100% real ticks | OK |
| V8 V7H8m25 micro 200 cap1.00 | cent | oos_may | 100 | 499.60 | 0.00 | 10 | 100.00% | 142.90000000 (13.30663935%) | 0.00 | 100% real ticks | OK |
| V8 V7H8m25 micro 200 cap1.00 | cent | oos_may | 300 | 501.30 | 0.00 | 10 | 100.00% | 142.90000000 (13.31159758%) | 0.00 | 100% real ticks | OK |
| V8 V7H8m25 micro 200 cap1.00 | cent | oos_may | 500 | 499.20 | 0.00 | 10 | 100.00% | 142.90000000 (13.29425993%) | 0.00 | 100% real ticks | OK |
| V8 V7H8m25 micro 200 cap1.00 | cent | ytd_2026 | 0 | 3,759.59 | 2.40 | 147 | 78.91% | 770.50000000 (46.69355116%) | 231.40 | 100% real ticks | OK |
| V8 V7H8m25 micro 200 cap1.00 | cent | ytd_2026 | 100 | 4,008.09 | 2.47 | 150 | 80.00% | 668.80000000 (40.49600829%) | 254.50 | 100% real ticks | OK |
| V8 V7H8m25 micro 200 cap1.00 | cent | ytd_2026 | 300 | 4,010.32 | 2.44 | 150 | 80.00% | 738.40000000 (43.24575054%) | 244.70 | 100% real ticks | OK |
| V8 V7H8m25 micro 200 cap1.00 | cent | ytd_2026 | 500 | 4,001.09 | 2.45 | 150 | 80.00% | 680.10000000 (40.27785740%) | 252.00 | 100% real ticks | OK |
| V8 V7H8m25 micro 200 cap1.00 | usd_real38 | usd_jun2025_now | 100 | 7,626.15 | 1.93 | 366 | 69.40% | 1 146.30 (41.64%) | 414.20 | 100% real ticks | OK |
| V8 V7H8m25 micro 200 cap1.00 | usd_real38 | usd_jun2025_now | 300 | 8,377.39 | 2.00 | 366 | 69.40% | 1 186.36 (42.19%) | 460.22 | 100% real ticks | OK |
| V8 V7H8m25 micro 200 cap1.00 | usd_real38 | usd_jun_dec_2025 | 100 | 760.70 | 1.21 | 209 | 61.24% | 674.65 (30.05%) | 222.98 | 100% real ticks | OK |
| V8 V7H8m25 micro 200 cap1.00 | usd_real38 | usd_jun_dec_2025 | 300 | 754.67 | 1.21 | 209 | 61.24% | 685.92 (30.49%) | 222.98 | 100% real ticks | OK |
| V8 V7H8m25 micro 250 cap0.75 | cent | last_month | 0 | 749.02 | 5.34 | 32 | 84.38% | 145.90000000 (12.09362438%) | 69.50 | 100% real ticks | OK |
| V8 V7H8m25 micro 250 cap0.75 | cent | last_month | 100 | 723.02 | 5.16 | 32 | 84.38% | 145.00000000 (12.16319688%) | 69.50 | 100% real ticks | OK |
| V8 V7H8m25 micro 250 cap0.75 | cent | last_month | 300 | 727.32 | 5.22 | 32 | 84.38% | 147.70000000 (12.33999777%) | 69.50 | 100% real ticks | OK |
| V8 V7H8m25 micro 250 cap0.75 | cent | last_month | 500 | 727.52 | 5.23 | 32 | 84.38% | 147.10000000 (12.28678954%) | 68.80 | 100% real ticks | OK |
| V8 V7H8m25 micro 250 cap0.75 | cent | oos_may | 0 | 356.10 | 0.00 | 10 | 100.00% | 103.40000000 (9.78703265%) | 0.00 | 100% real ticks | OK |
| V8 V7H8m25 micro 250 cap0.75 | cent | oos_may | 100 | 357.30 | 0.00 | 10 | 100.00% | 103.40000000 (9.79723328%) | 0.00 | 100% real ticks | OK |
| V8 V7H8m25 micro 250 cap0.75 | cent | oos_may | 300 | 357.90 | 0.00 | 10 | 100.00% | 103.40000000 (9.80001896%) | 0.00 | 100% real ticks | OK |
| V8 V7H8m25 micro 250 cap0.75 | cent | oos_may | 500 | 356.50 | 0.00 | 10 | 100.00% | 103.40000000 (9.79073951%) | 0.00 | 100% real ticks | OK |
| V8 V7H8m25 micro 250 cap0.75 | cent | ytd_2026 | 0 | 2,638.55 | 2.41 | 144 | 78.47% | 501.30000000 (36.02611473%) | 162.00 | 100% real ticks | OK |
| V8 V7H8m25 micro 250 cap0.75 | cent | ytd_2026 | 100 | 2,537.95 | 2.39 | 144 | 79.17% | 449.70000000 (32.26453098%) | 162.00 | 100% real ticks | OK |
| V8 V7H8m25 micro 250 cap0.75 | cent | ytd_2026 | 300 | 2,490.85 | 2.37 | 144 | 79.17% | 448.90000000 (32.16789852%) | 146.80 | 100% real ticks | OK |
| V8 V7H8m25 micro 250 cap0.75 | cent | ytd_2026 | 500 | 2,496.85 | 2.38 | 144 | 79.17% | 448.40000000 (32.12056012%) | 145.30 | 100% real ticks | OK |
| V8 V7H8m25 micro 250 cap0.75 | usd_real38 | usd_jun2025_now | 100 | 6,041.59 | 1.91 | 363 | 69.15% | 900.27 (33.96%) | 299.14 | 100% real ticks | OK |
| V8 V7H8m25 micro 250 cap0.75 | usd_real38 | usd_jun2025_now | 300 | 6,607.65 | 1.99 | 364 | 69.23% | 901.65 (33.45%) | 322.15 | 100% real ticks | OK |
| V8 V7H8m25 micro 250 cap0.75 | usd_real38 | usd_jun_dec_2025 | 100 | 796.02 | 1.26 | 208 | 61.06% | 539.65 (24.87%) | 174.95 | 100% real ticks | OK |
| V8 V7H8m25 micro 250 cap0.75 | usd_real38 | usd_jun_dec_2025 | 300 | 788.22 | 1.25 | 208 | 61.06% | 551.01 (25.36%) | 174.95 | 100% real ticks | OK |

## Monte Carlo Trade-Order Stress

| Profile | Account | Window | Delay | Trades | Native DD | MC median DD | MC p95 DD | MC p99 DD | MC ruin rate |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| V5 max raw | cent | ytd_2026 | 100 | 167 | 28.60% | 49.47% | 231.98% | 401.16% | 20.44% |
| V5 max raw | usd_real38 | usd_jun2025_now | 100 | 404 | 28.51% | 62.71% | 262.05% | 426.63% | 27.10% |
| V6 profit-balanced raw | cent | ytd_2026 | 100 | 156 | 17.47% | 33.53% | 103.62% | 144.99% | 5.92% |
| V6 profit-balanced raw | usd_real38 | usd_jun2025_now | 100 | 370 | 16.61% | 41.19% | 128.24% | 202.00% | 10.78% |
| V7 soft H8 m25 raw | cent | ytd_2026 | 100 | 155 | 17.45% | 35.27% | 113.47% | 170.14% | 7.58% |
| V7 soft H8 m25 raw | usd_real38 | usd_jun2025_now | 100 | 372 | 30.17% | 58.73% | 242.72% | 369.56% | 26.28% |
| V8 V5max guard moderate | cent | ytd_2026 | 100 | 144 | 13.71% | 20.05% | 42.31% | 59.31% | 0.00% |
| V8 V5max guard moderate | usd_real38 | usd_jun2025_now | 100 | 2 | 46.16% | 39.64% | 39.64% | 39.64% | 0.00% |
| V8 V5max guard strict | cent | ytd_2026 | 100 | 3 | 28.27% | 19.07% | 19.29% | 19.29% | 0.00% |
| V8 V5max guard strict | usd_real38 | usd_jun2025_now | 100 | 2 | 46.16% | 39.64% | 39.64% | 39.64% | 0.00% |
| V8 V6balance guard moderate | cent | ytd_2026 | 100 | 3 | 34.50% | 23.83% | 24.11% | 24.11% | 0.00% |
| V8 V6balance guard moderate | usd_real38 | usd_jun2025_now | 100 | 2 | 56.18% | 49.55% | 49.55% | 49.55% | 0.00% |
| V8 V7H8m25 guard moderate | cent | ytd_2026 | 100 | 3 | 34.50% | 23.83% | 24.11% | 24.11% | 0.00% |
| V8 V7H8m25 guard moderate | usd_real38 | usd_jun2025_now | 100 | 2 | 56.18% | 49.55% | 49.55% | 49.55% | 0.00% |
| V8 V5max micro 200 cap1.00 | cent | ytd_2026 | 100 | 164 | 20.89% | 20.13% | 47.94% | 65.16% | 0.04% |
| V8 V5max micro 200 cap1.00 | usd_real38 | usd_jun2025_now | 100 | 404 | 64.34% | 30.55% | 74.94% | 105.73% | 1.30% |
| V8 V6balance micro 200 cap1.00 | cent | ytd_2026 | 100 | 151 | 39.34% | 18.54% | 39.05% | 50.08% | 0.00% |
| V8 V6balance micro 200 cap1.00 | usd_real38 | usd_jun2025_now | 100 | 359 | 40.94% | 26.55% | 59.27% | 83.07% | 0.28% |
| V8 V6balance micro 250 cap0.75 | cent | ytd_2026 | 100 | 145 | 32.26% | 14.25% | 27.70% | 36.58% | 0.00% |
| V8 V6balance micro 250 cap0.75 | usd_real38 | usd_jun2025_now | 100 | 358 | 15.10% | 22.87% | 47.59% | 66.68% | 0.04% |
| V8 V7H8m25 micro 200 cap1.00 | cent | ytd_2026 | 100 | 148 | 40.50% | 19.08% | 40.50% | 54.13% | 0.00% |
| V8 V7H8m25 micro 200 cap1.00 | usd_real38 | usd_jun2025_now | 100 | 362 | 41.64% | 27.95% | 64.19% | 90.86% | 0.48% |
| V8 V7H8m25 micro 250 cap0.75 | cent | ytd_2026 | 100 | 143 | 32.26% | 14.76% | 28.93% | 37.36% | 0.00% |
| V8 V7H8m25 micro 250 cap0.75 | usd_real38 | usd_jun2025_now | 100 | 359 | 33.96% | 24.21% | 52.36% | 70.92% | 0.16% |

## Decision

Best scored candidate: `V6 profit-balanced raw`.

A profile is marked live-ready only if it remains net-positive under delay stress, keeps cent YTD DD at or below 30%, keeps USD Jun2025-now DD at or below 45%, and Monte Carlo p95 DD at or below 40%. If no profile passes, the correct recommendation is not live-ready.

Final recommendation: **not live-ready for 1000 USC yet**.

What the stress test showed:

- `V5 max raw` is still the highest cent profit style, but its cent YTD DD reaches `30.29%` under delay stress and largest cent YTD loss is `3,732.50 USC`.
- `V6 profit-balanced raw` is the best native-score baseline: cent YTD stays profitable under all tested delays with max DD around `17.52%`, and USD Jun2025-now DD is around `16.61%`. Its weakness is Monte Carlo trade-order risk, which means the result is path-sensitive.
- `V8 V5max micro 200 cap1.00` is the best manual micro-risk candidate: cent YTD net is still `7,894.02-8,217.38 USC`, largest cent YTD loss falls to `370.30 USC`, and cent Monte Carlo p95 DD drops sharply versus V5/V6. It is still rejected as live-ready because USD Jun2025-now DD is too high under delay stress.
- The V8 stop-trading risk-guard variants are rejected. They reduce some loss size, but they often stop after early losses and skip recovery trades, causing negative YTD/ archive results.
- The V6/V7 micro `250 cap0.75` profiles are useful archive-safe references, but their cent YTD chronological DD is still above the 30% gate.

Best files for manual follow-up backtest:

- Safer baseline: `sets/InvictusForward8_V8_v6balance_raw.set`
- Micro-risk manual candidate: `sets/InvictusForward8_V8_v8_v5max_micro200_cap100.set`
- Archive-safe reference: `sets/InvictusForward8_V8_v8_v7h8m25_micro250_cap075.set`

Next tuning direction should not be a generic equity stop. The evidence points to targeted loss-cluster filtering or module/hour-specific lot scaling, especially on the trades that cause the USD Jun2025-now DD spike, while preserving the recovery trades that make 2026 profitable.

## Files

- Results: `/Users/naufalrachmandani/Hobby/MT5 XAU Bot/invictusforward-8-research/invictus8_v8_risk_certified/reports/results.json`
- Comparison: `/Users/naufalrachmandani/Hobby/MT5 XAU Bot/invictusforward-8-research/invictus8_v8_risk_certified/reports/comparison.json`
- Monte Carlo: `/Users/naufalrachmandani/Hobby/MT5 XAU Bot/invictusforward-8-research/invictus8_v8_risk_certified/reports/monte_carlo.json`
- Native reports: `/Users/naufalrachmandani/Hobby/MT5 XAU Bot/invictusforward-8-research/invictus8_v8_risk_certified/native_stress`
