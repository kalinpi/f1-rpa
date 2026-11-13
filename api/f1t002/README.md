# F1T002

## General information

| Item | Value |
|---|---|
| **Business owner** | |
| **RPA service** | ServiceDesk → Request/Incident → Category → RPA |
| **Robot account (system)** | |
| **AD account (network/resources)** | |

## Description

The robot retrieves Formula 1 race results from the [OpenF1 API](https://openf1.org) (no API key, data from the 2023 season).

Task `prep`:

1. Looks for `*RACES*.xlsx` files in `SHARED/in/` (column A – year, column B – GP name, circuit or country in any form, e.g. `baku`, `Monaco`, `cota`).
2. Translates the GP name using the dictionary `SHARED/dicts/GP_DICT.xlsx` and finds the race.
3. Fetches the classification, drivers and tyre strategies, and adds a separate sheet for every race (e.g. `2025 Baku`).
4. Writes the status of each row in column C and moves the file to `SHARED/out/`.

Details and diagrams: [docs/EN/README.md](docs/EN/README.md)

## Run

```
./F1T002.sh prep
```

## Results

#### `SHARED/out/` – processed files

- column C: `OK` (gray background) or an error description (red background), e.g. GP not found, ambiguous GP name, race cancelled
- one sheet per race: Pos | No | Driver | Team | Gap to leader / DNF | Tyres (e.g. `HM`) | Laps per stint (e.g. `40/11`)
- file name with the date and time of processing, or with the `ERROR_` prefix if anything failed

#### `SHARED/log/prep/` – robot run

- `log.html` – the robot's actions step by step and any errors
- `stdout_<date>.log` – console messages

#### `./log/` – statistics (local)

- `f1t002-logs.xlsx` – robot work statistics collected from `.json` files by the `Dolog` task

## Configuration (.env)

| Variable | Description |
|---|---|
| `MODE` | operation mode (`PROD` / `TEST`) |
| `TYPE` | robot type (`API`) |
| `SHARED` | path to the shared resource (empty = local operation) |
| `SDIR` | local folder with test data (`./testcifs`) |
| `URL_PROD`, `URL_TEST` | OpenF1 API address |
| `LANGUAGE` | message language (`pl` / `en`) |
| `WAIT_TO_RESPONSE` | request timeout in ms (minimum 5 s is used) |
| `DRYRUN` | test mode without API requests (`0` / `1`) |
| `RED`, `GREEN`, `GRAY`, `WHITE` | cell colors (ARGB) |
| `SECURED` | decrypt `.envs` variables (`0` / `1`) |
