# F1T003

## General information

| Item | Value |
|---|---|
| **Business owner** | |
| **RPA service** | ServiceDesk → Request/Incident → Category → RPA |
| **Robot account (system)** | |
| **AD account (network/resources)** | |

## Description

The robot computes Formula 1 race statistics from the output file of robot F1T001 or F1T002 (no Internet connection needed).

Task `prep`:

1. Looks for `*RACES*.xlsx` files in `SHARED/in/` with one sheet per race (Pos | No | Driver | Team | Gap | Tyres | Laps per stint).
2. Computes statistics for every race and a summary of all races.
3. Adds the `Statistics` sheet and moves the file to `SHARED/out/`.

Details and diagrams: [docs/EN/README.md](docs/EN/README.md)

## Run

```
./F1T003.sh prep
```

## Results

#### `SHARED/out/` – processed files

- `Statistics` sheet: one row per race (winner, winner team, classified, DNF/DNS/DSQ, average pit stops, most common tyre strategy, status)
- summary below the table: number of races, most common strategy, average pit stops, total DNF, best team (points 25-18-15-12-10-8-6-4-2-1), most wins
- file name with the date and time of processing, or with the `ERROR_` prefix if anything failed (e.g. a sheet in a wrong format)

#### `SHARED/log/prep/` – robot run

- `log.html` – the robot's actions step by step and any errors
- `stdout_<date>.log` – console messages

#### `./log/` – statistics (local)

- `f1t003-logs.xlsx` – robot work statistics collected from `.json` files by the `Dolog` task

## Configuration (.env)

| Variable | Description |
|---|---|
| `MODE` | operation mode (`PROD` / `TEST`) |
| `TYPE` | robot type (`FIL`) |
| `SHARED` | path to the shared resource (empty = local operation) |
| `SDIR` | local folder with test data (`./testcifs`) |
| `URL_PROD`, `URL_TEST` | not used (FILE robot) |
| `LANGUAGE` | message language (`pl` / `en`) |
| `WAIT_TO_RESPONSE` | not used (FILE robot) |
| `DRYRUN` | test mode – statuses only, no statistics (`0` / `1`) |
| `RED`, `GREEN`, `GRAY`, `WHITE` | cell colors (ARGB) |
| `SECURED` | decrypt `.envs` variables (`0` / `1`) |
