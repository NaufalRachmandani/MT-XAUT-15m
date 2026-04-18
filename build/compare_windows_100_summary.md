# Compare Windows on $100

Setup umum:
- Symbol `XAUUSDc`
- Period `M15`
- Deposit `100 USD`
- Leverage `1:100`
- Modelling `Every tick`

## 6 Bulan Terakhir

Window: `2025.10.18 - 2026.04.15`

| Version | Net Profit | PF | Win Rate | Trades | Balance DD | Equity DD |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| base | -93.61 | 0.12 | 30.00% | 10 | 93.61% | 94.81% |
| v1 | -91.91 | 0.31 | 35.00% | 40 | 92.02% | 93.43% |
| v2 | 223.97 | 1.06 | 49.38% | 1043 | 84.88% | 84.13% |
| v3 | 210.33 | 1.04 | 50.55% | 1084 | 89.94% | 90.07% |
| v4 | 208.73 | 1.04 | 50.42% | 1079 | 89.74% | 89.89% |
| v5 | 278.04 | 1.20 | 52.08% | 672 | 52.61% | 54.24% |

## Dari Awal 2025

Window: `2025.01.01 - 2026.04.15`

| Version | Net Profit | PF | Win Rate | Trades | Balance DD | Equity DD |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| base | 341.92 | 1.08 | 41.39% | 563 | 63.03% | 65.97% |
| v1 | 1076.45 | 1.41 | 49.46% | 552 | 28.13% | 29.53% |
| v2 | 2511.59 | 1.03 | 49.31% | 2890 | 85.28% | 85.67% |
| v3 | 5735.02 | 1.03 | 50.03% | 2866 | 90.34% | 90.88% |
| v4 | 14968.71 | 1.04 | 50.32% | 2832 | 87.94% | 88.29% |
| v5 | 8337.70 | 1.09 | 50.90% | 2222 | 76.95% | 78.05% |

## Takeaways

- `v5` adalah versi terbaik untuk `6 bulan terakhir` jika targetnya kombinasi profit, PF, dan drawdown yang masih masuk akal.
- `v1` adalah versi paling sehat untuk `full period dari awal 2025` jika prioritasnya robustness, karena PF `1.41` dan equity DD hanya `29.53%`.
- `v4` memberi profit absolut terbesar pada full period, tetapi DD tetap sangat tinggi, sehingga lebih cocok dibaca sebagai versi paling agresif, bukan paling aman.
- `base` dan `v1` menunjukkan market regime effect yang jelas: dua versi ini gagal di recent window, tetapi tidak gagal pada full-period.
- `v2-v4` cenderung kuat di gross profit saat window diperpanjang, tetapi drawdown tetap ekstrem untuk modal `100 USD`.
- Secara praktis, ranking versi berubah tergantung regime:
  - Recent market: `v5` > `v2`/`v3`/`v4` >> `base`/`v1`
  - Full-period: `v1` unggul di risk-adjusted quality, `v4` unggul di raw profit, `v5` ada di tengah sebagai kompromi.
