# Install v11 Live ke MT5 VPS

Isi paket ini sengaja minimal: hanya 2 file `.ex5` untuk live.

1. Buka MT5 VPS.
2. Klik `File` -> `Open Data Folder`.
3. Copy folder `MQL5` dari paket ini ke Data Folder MT5 VPS.
4. Restart MT5 atau klik kanan `Navigator` -> `Refresh`.
5. Buka 2 chart `XAUUSDc` timeframe `M5`.
6. Attach `InvictusBullM5_v11` ke chart pertama.
7. Attach `InvictusBearM5_v11` ke chart kedua.
8. Pastikan `Algo Trading` ON.

Default terbaru sudah punya Daily Guard aktif di dalam `.ex5`:

- Daily loss cap: 8%
- Profit lock: mulai +12%, giveback 4%
- Cooldown: 3 loss beruntun -> pause 180 menit
- Tidak force-close posisi saat daily guard kena
