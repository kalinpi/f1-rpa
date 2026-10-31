# F1 RPA

Three RPA robots working on Formula 1 race data, built according to the
[Poczta Polska RPA standard](https://gitlab.com/pocztapolska/rpa)
(Robocorp + Python, Excel in / Excel out).

The user drops an Excel file with a list of races (year + Grand Prix name) into a shared folder.
The robot fetches the results and saves an Excel file with the classification, teams and tyre strategies of every race.

## Robots

| Robot | Type | Description | Status |
|---|---|---|---|
| [F1T001](www/f1t001/) | WWW | Race results scraped from a website (Playwright) | ⏳ planned |
| [F1T002](api/f1t002/README.md) | API | Race results and tyre strategies from [OpenF1 API](https://openf1.org) (2023+) | ✅ ready (local tests) |
| [F1T003](file/f1t003/README.md) | FILE | Statistics computed offline from the F1T001 / F1T002 output (most common tyre strategy, pit stops, DNF count, best team…) | ✅ ready (local tests) |

Naming: `F1T` = topic (F1) + robot number. `001` WWW, `002` API, `003` FILE – same as in the Poczta repo.

## How a robot works

1. A user puts `*RACES*.xlsx` into `in/` (column A – year, column B – GP name, circuit or country in any form, e.g. `baku`, `Monaco`, `cota`).
2. The robot (task `prep`) translates the name using the shared dictionary `dicts/GP_DICT.xlsx` and finds the race.
3. For every race it adds a new sheet (e.g. `2025 Baku`): position, number, driver, team, gap to leader / DNF, tyres (e.g. `SHS`) and laps per stint (e.g. `13/42/10`).
4. The status of each row (OK or error in red) is written next to the input data.
5. The file is moved to `out/` with the execution date, or with the `ERROR_` prefix if anything failed.
6. Every run leaves a `.json` log; task `Dolog` collects them into an Excel sheet with work statistics (1 processed row = 1 minute saved).

Details and diagrams: [api/f1t002/docs/EN/README.md](api/f1t002/docs/EN/README.md) ([PL](api/f1t002/docs/PL/README.md)).

## Repository structure

```
f1-rpa/
├── api/f1t002/    ← API robot (OpenF1)
├── www/f1t001/    ← WWW robot (scraping)
└── file/f1t003/   ← FILE robot (statistics from Excel)
```

Each robot has the same layout as in the Poczta repo: `tasks.py` (entry point), `task_prep.py` (business logic),
`task_dolog.py` (log statistics), `translations/` (PL/EN messages), `testcifs/` (test folders `in/`, `out/`, `dicts/`, `log/`)
and `docs/` (PlantUML diagrams, PL and EN).

## Author

Piotr Kalinowski ([@kalinpi](https://github.com/kalinpi)) – preparation for an internship at Poczta Polska (RPA department).
