# F1T003 Checklist

1. ✅ Code implemented according to the diagrams

2. ✅ Task entry condition
    + Prep - files in the `in/` folder matching `*RACES*.xlsx` (F1T001 / F1T002 output)
    + Dolog - `*.json` files in the `log/` folder

3. ✅ Task completion condition
    + Prep - after processing, files from the `in/` folder are moved to `out/` (with the date or with the `ERROR_` prefix)
    + Dolog - `*.json` files from the `log/` folder are deleted

4. ✅ Work recording (protection against re-running)
    + Prep - status of every sheet in column H of the `Statistics` sheet; re-processing builds the statistics again
    + Dolog - `*.json` files deleted from the `log/` folder

5. ✅ Dynamic response timeout
    + Prep - not applicable (FILE mode, no network connections)

6. ✅ Error handling (try/except)
    + Prep - continue working when a sheet has a wrong format or no results (error description in red)

7. ✅ Task messages in separate files
    + Prep - messages and statistics headers in `translations/pl.yaml`, `en.yaml`

8. ✅ Diagrams
    + ✅ Infrastructure
    + ✅ Component (prep)
    + ✅ Sequence (dolog, copied from WTH001)
    + ✅ Function descriptions in code

9. ❌ Fixes from/to the v2 template
    + ✅ Fixes pulled into Dolog (identical to v2)
    + ❌ Fixes reported to v2 (WAIT_TO_RESPONSE in ms passed to requests as seconds; `.json` log name with one-second precision – a fast run overwrites the closed log)

10. ✅ Work calculation
    + ✅ Run saved to `.json`
    + ✅ Excel formulas in Dolog statistics

11. ❌ Verification of the `F1T003.sh` file and proxy
    + ✅ `bash -n` syntax
    + ❌ Run via `rcc` and proxy on the server

12. ✅ Documentation
    + ✅ `docs/README.md` (PL/EN)
    + ✅ Robot `README.md` / `README_pl.md`

13. ❌ Pilot - verification and tuning on the target environment (repeat items 1-12)
