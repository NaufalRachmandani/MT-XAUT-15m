# v6 Aggressive Follow-up: Limit Entry Retest

Eksperimen lanjutan dilakukan setelah sweep leverage + risk selesai.

Tujuan:
- ambil preset champion `b_r175`
- hidupkan kembali trend `market-or-limit` entry ala `base`
- tetap pertahankan fixed-fractional sizing `v6`
- bandingkan `1:100` vs `1:500`

Window test:
- `XAUUSDc`
- `M15`
- `2025.10.18 - 2026.04.15`
- `Deposit 100 USD`
- `Every tick`

Hasil:

| Variant | Leverage | Net Profit | Profit % | PF | Win Rate | Trades | EqDD |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `b_r175` market-only champion | `1:100` | `107.90` | `107.90%` | `1.08` | `53.27%` | `1102` | `62.65%` |
| `b_r175` market-only champion | `1:500` | `107.90` | `107.90%` | `1.08` | `53.27%` | `1102` | `62.65%` |
| `b_r175` + limit-retest trend entry | `1:100` | `13.21` | `13.21%` | `1.03` | `53.96%` | `732` | `42.92%` |
| `b_r175` + limit-retest trend entry | `1:500` | `13.21` | `13.21%` | `1.03` | `53.96%` | `732` | `42.92%` |

Kesimpulan:
- leverage tetap tidak memberi pengaruh nyata
- menghidupkan kembali trend limit entry justru menurunkan profit drastis pada recent 6 bulan
- bottleneck utama untuk target profit tinggi saat ini bukan leverage dan bukan sekadar execution path
- langkah berikutnya yang lebih masuk akal adalah bedah ulang kualitas entry atau target structure, bukan menambah gas lagi
