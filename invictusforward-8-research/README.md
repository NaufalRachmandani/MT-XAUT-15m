# InvictusForward-8 Research Folder

## Contents

- `source/original/InvictusForward-8`: untouched source extracted from the zip.
- `source/tuned/InvictusForward-8-Tuned`: tuned EA source plus compiled `InvictusForward-8-Tuned.ex5`.
- `backtests/cent_native_2026_lev2000_compare`: native MT5 cent-account Base vs Tuned comparison for 2026-only windows.
- `backtests/tuned_realticks_lev2000`: MT5 reports, `.ini` tester configs, images, compile log, and parsed summary.
- `sets/InvictusForward-8-Tuned-research.set`: tuned input defaults.
- `tools/run_cent_native_compare.py`: reproducible native MT5 runner for `XAUUSDc`, `USC`, `Model=4`, and `Leverage=1:2000`.
- `tools/run_tuned_backtests.py`: reproducible MT5 runner for `Model=4` real ticks and `Leverage=1:2000`.
- `notes/RESEARCH.md`: research summary and baseline-vs-tuned comparison.

## Run

```bash
python3 invictusforward-8-research/tools/run_tuned_backtests.py --cases d100_last_week d100_last_month d100_ytd_2026
```

Cent native compare:

```bash
python3 invictusforward-8-research/tools/run_cent_native_compare.py --timeout 2400
```

Every generated tester `.ini` uses:

- `Model=4`
- `Leverage=1:2000`
- `UseLocal=1`
- `UseRemote=0`
- `UseCloud=0`
