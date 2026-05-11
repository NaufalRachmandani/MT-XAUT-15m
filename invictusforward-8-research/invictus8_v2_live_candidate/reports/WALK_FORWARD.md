# V2Live Walk-Forward

Native MT5 optimization was run per train window, then candidates were validated on Mar, Apr, and May using `.htm` reports.

## Optimization Phases

| Phase | Train | Validation | Completed | Pass Rows |
| --- | --- | --- | --- | ---: |
| wf_a | 2026.01.01 to 2026.02.28 | 2026.03.01 to 2026.03.31 | True | 1555 |
| wf_b | 2026.02.01 to 2026.03.31 | 2026.04.01 to 2026.04.30 | True | 1825 |
| wf_c | 2026.01.01 to 2026.04.30 | 2026.05.01 to 2026.05.10 | True | 1256 |

## V1 Validation Baselines

| Window | Net | PF | Eq DD | Largest Loss | Max Consecutive Losses |
| --- | ---: | ---: | --- | ---: | --- |
| validate_mar | 862.80 | 3.31 | 159.40000000 (12.64477233%) | -67.60 | 3 (-91.60000000) |
| validate_apr | -180.67 | 0.72 | 356.74900000 (30.85847257%) | -50.00 | 5 (-216.40000000) |
| validate_may | 254.28 | 6.11 | 134.30000000 (9.67174264%) | -49.80 | 1 (-49.80000000) |

## Candidate Gate

Screened candidates: `150`. Passed all gates: `0`.
Selected candidate: `none`.

| Candidate | Passed | Median Score | Fail Reasons |
| ---: | --- | ---: | --- |
| 1 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 2 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 3 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 4 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 5 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 6 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 7 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 8 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 9 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 10 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 11 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 12 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 13 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 14 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 15 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 16 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 17 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 18 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 19 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 20 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 21 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 22 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 23 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 24 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 25 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 26 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 27 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 28 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 29 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 30 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 31 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 32 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 33 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 34 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 35 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 36 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 37 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 38 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 39 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 40 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 41 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 42 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 43 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 44 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 45 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 46 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 47 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 48 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 49 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 50 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 51 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 52 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 53 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 54 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 55 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 56 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 57 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 58 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 59 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 60 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 61 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 62 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 63 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 64 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 65 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 66 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 67 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 68 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 69 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 70 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 71 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 72 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 73 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 74 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 75 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 76 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 77 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 78 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 79 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 80 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 81 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 82 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 83 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 84 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 85 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 86 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 87 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 88 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 89 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 90 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 91 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 92 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 93 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 94 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 95 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 96 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 97 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 98 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 99 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 100 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 101 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 102 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 103 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 104 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 105 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 106 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 107 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 108 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 109 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 110 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 111 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 112 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 113 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 114 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 115 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 116 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 117 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 118 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 119 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 120 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 121 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 122 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 123 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 124 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 125 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 126 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 127 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 128 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 129 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 130 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 131 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 132 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 133 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 134 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 135 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 136 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 137 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 138 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 139 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 140 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 141 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 142 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 143 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 144 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 145 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 146 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 147 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 148 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 149 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
| 150 | False | 70.5662 | validate_apr: PF < 1.15; validate_apr: equity DD > V1; validate_apr: max consecutive losses > V1; validate_apr: net <= 0; validate_may: equity DD > V1 |
