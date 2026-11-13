# F1T001

## General information

| Item | Value |
|---|---|
| **Business owner** | |
| **RPA service** | ServiceDesk → Request/Incident → Category → RPA |
| **Robot account (system)** | |
| **AD account (network/resources)** | |

## Description

The robot retrieves Formula 1 race results from [Wikipedia](https://en.wikipedia.org) (scraping, data from the 1950 season).

Task `prep`:

1. Looks for `*RACES*.xlsx` files in `SHARED/in/` (column A – year, column B – GP name, circuit or country in any form, e.g. `baku`, `monako`, `cota`).
2. Translates the GP name using the dictionary `SHARED/dicts/GP_DICT.xlsx` and finds the race in the season calendar (`/wiki/{year}_Formula_One_World_Championship`) by country, GP name, circuit or city.
3. Reads the `Race_classification` table from the race page and adds a separate sheet for every race (e.g. `2025 Azerbaijan`).
4. Writes the status of each row in column C and moves the file to `SHARED/out/`.

Wikipedia does not publish tyre strategies, so the Tyres and Laps per stint columns are empty (full data for seasons from 2023 is provided by robot F1T002). The robot waits 5 s between page loads (`Crawl-delay` from Wikipedia `robots.txt`).

Details and diagrams: [docs/EN/README.md](docs/EN/README.md)

## Run

```
./F1T001.sh prep
```

## Results

#### `SHARED/out/` – processed files

- column C: `OK` (gray background) or an error description (red background), e.g. GP not found, ambiguous GP name, no results (race not held yet)
- one sheet per race: Pos | No | Driver | Team | Gap to leader / DNF / DNS / DSQ | Tyres (empty) | Laps per stint (empty)
- file name with the date and time of processing, or with the `ERROR_` prefix if anything failed

#### `SHARED/log/prep/` – robot run

- `log.html` – the robot's actions step by step and any errors
- `stdout_<date>.log` – console messages

#### `./log/` – statistics (local)

- `f1t001-logs.xlsx` – robot work statistics collected from `.json` files by the `Dolog` task

## Configuration (.env)

| Variable | Description |
|---|---|
| `MODE` | operation mode (`PROD` / `TEST`) |
| `TYPE` | robot type (`WWW`) |
| `SHARED` | path to the shared resource (empty = local operation) |
| `SDIR` | local folder with test data (`./testcifs`) |
| `URL_PROD`, `URL_TEST` | website address (Wikipedia) |
| `LANGUAGE` | message language (`pl` / `en`) |
| `WAIT_TO_RESPONSE` | browser action delay in ms; page timeout = 50 × value (minimum 20 s) |
| `DRYRUN` | test mode without reading results from the website (`0` / `1`) |
| `RED`, `GREEN`, `GRAY`, `WHITE` | cell colors (ARGB) |
| `SECURED` | decrypt `.envs` variables (`0` / `1`) |

The robot does not log in to the website, so no login and password are needed in `.envs`.
