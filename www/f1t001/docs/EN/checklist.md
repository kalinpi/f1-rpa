# F1T001 Checklist

1. ✅ Code implemented according to the diagrams

2. ✅ Task entry condition
    + Prep - files in the `in/` folder matching `*RACES*.xlsx`
    + Dolog - `*.json` files in the `log/` folder

3. ✅ Task completion condition
    + Prep - after processing, files from the `in/` folder are moved to `out/` (with the date or with the `ERROR_` prefix)
    + Dolog - `*.json` files from the `log/` folder are deleted

4. ✅ Work recording (protection against re-running)
    + Prep - status saved in column C (OK / error description)
    + Dolog - `*.json` files deleted from the `log/` folder

5. ✅ Dynamic response timeout
    + Prep - action delay and page timeout from the `WAIT_TO_RESPONSE` variable in `.env` (ms, minimum 20 s), 5 s pause between pages (Wikipedia `Crawl-delay`)

6. ✅ Error handling (try/except)
    + Prep - page load retried in a new tab after an error (e.g. browser tab crash), work continues when a race page is missing

7. ✅ Task messages in separate files
    + Prep - messages about a GP not found, an ambiguous GP name and missing results on the website (`translations/pl.yaml`, `en.yaml`)

8. ✅ Diagrams
    + ✅ Infrastructure
    + ✅ Component (prep)
    + ✅ Sequence (dolog, copied from WTH001)
    + ✅ Function descriptions in code

9. 🔄 Fixes from/to the v2 template
    + ✅ Fixes pulled into Dolog (identical to v2)
    + ⏳ Fixes reported to v2 (`.json` log name with one-second precision – a fast run overwrites the closed log; an unavailable URL in `ut.open_the_intranet_website` ends the task with a traceback without writing the error to the `.json` log)

10. ✅ Work calculation
    + ✅ Run saved to `.json`
    + ✅ Excel formulas in Dolog statistics

11. 🔄 Verification of the `F1T001.sh` file and proxy
    + ✅ `bash -n` syntax
    + ⏳ Run via `rcc` and proxy on the server

12. ✅ Documentation
    + ✅ `docs/README.md` (PL/EN)
    + ✅ Robot `README.md` / `README_pl.md`

13. ⏳ Pilot - verification and tuning on the target environment (repeat items 1-12)
