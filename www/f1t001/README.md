# F1T001

## 📋 General Information
| | |
|---|---|
| **Business Owner** | xxxxx@xxx.pl |
| **RPA Service** | ServiceDesk → Request/Incident → Category → RPA |
| **Robot account (system)** | `xxx_F1T` |
| **AD account (network/resources)** | `xxx_F1T_ad` |

## Description

The robot retrieves Formula 1 race results from a [website](https://en.wikipedia.org) (Wikipedia, data from the 1950 season) and consists of tasks:

⚡ prep - checks whether there is data in `SHARED\in\` in a file named `*RACES*.xlsx` (A = year, B = GP name, circuit or country in any form), translates the GP name using `SHARED\dicts\GP_DICT.xlsx`, finds the race in the season calendar and reads the classification from the race page (scraping). For every race it adds a sheet (e.g. `2025 Azerbaijan`), writes the status of each row in column C and moves the file to `SHARED\out\`.

> ℹ️ **WWW mode (scraping).** The robot opens the season page in a browser
> (`/wiki/{year}_Formula_One_World_Championship`), matches the GP in the calendar table by country (flag),
> GP name, circuit or city, then reads the `Race_classification` table from the race page.
> Wikipedia does not publish tyre strategies, so the Tyres and Laps per stint columns are empty
> (full data for seasons from 2023 is provided by robot F1T002).
> The robot waits 5 s between page loads (`Crawl-delay` from Wikipedia `robots.txt`).

[📖 Detailed task description](docs/EN/README.md)

## ▶️ Run

```
./F1T001.sh prep
```

## Results

🚀 After running the robot, check the processed files in `SHARED/out/`

#### A→ In the `SHARED/out` subfolder

- `*RACES*.xlsx` files already processed by the robot
- column C contains `OK` (gray) or an error description (red), e.g. GP not found, ambiguous GP name, no results (race not held yet)
- a sheet for every race: Pos | No | Driver | Team | Gap to leader / DNF / DNS / DSQ | Tyres (empty) | Laps per stint (empty)
- files have the processing date and time added to their name
- files with errors get the `ERROR_` prefix

#### B→ In the `SHARED/log` subfolder

- `log.html` file with the robot's step-by-step actions and possible errors
- `stdout.log` file with console messages from the robot run

#### C→ In the local `./log` subfolder
- `f1t001-logs.xlsx` file with sheets of statistics collected from `.json` files

## ⚙️ Configuration (.env)
- *MODE* → working mode (`PROD` / `TEST`)
- *TYPE* → robot connection type `WWW`
- *SHARED* → path to the shared resource (empty = local work)
- *SDIR* → local folder with test data (`./testcifs`)
- *URL_PROD*, *URL_TEST* → website address (Wikipedia)
- *LANGUAGE* → language of robot messages (`pl` / `en`)
- *WAIT_TO_RESPONSE* → browser action delay (ms), page timeout = 50 × value (minimum 20 s)
- *DRYRUN* → test mode without reading results from the website (`0` / `1`)
- *RED*, *GREEN*, *GRAY*, *WHITE* → cell colors (ARGB)
- *SECURED* → decrypt `.envs` variables with Fernet (`0` / `1`)
- In WWW mode, no login and password are needed in the `.envs` file
