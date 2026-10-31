# F1T002

## 📋 General Information
| | |
|---|---|
| **Business Owner** | xxxxx@xxx.pl |
| **RPA Service** | ServiceDesk → Request/Incident → Category → RPA |
| **Robot account (system)** | `xxx_F1T` |
| **AD account (network/resources)** | `xxx_F1T_ad` |

## Description

The robot retrieves Formula 1 race results from the OpenF1 REST API (https://api.openf1.org/v1, no API key, data from the 2023 season) and consists of tasks:

⚡ prep - checks whether there is data in `SHARED\in\` in a file named *RACES*.xlsx (A = year, B = GP name, circuit or country in any form), translates the GP name using `SHARED\dicts\GP_DICT.xlsx`, finds the race and fetches the classification, drivers and tyre strategies. For every race it adds a sheet (e.g. `2025 Baku`), writes the status of each row in column C and moves the file to `SHARED\out\`.

[📖 Detailed task description](docs/EN/README.md)

## ▶️ Run

```
./F1T002.sh prep
```

## Results

🚀 After running the robot, check the processed files in `SHARED/out/`.

#### A → In the `SHARED/out` subfolder

- `*RACES*.xlsx` files that the robot has processed
- column C contains `OK` (gray) or the error description (red), e.g. GP not found, ambiguous GP name, race cancelled
- one sheet per race: Pos | No | Driver | Team | Gap to leader / DNF | Tyres (e.g. `HM`) | Laps per stint (e.g. `40/11`)
- files include the date and time of processing appended
- files with errors are prefixed with `ERROR_`

#### B → In the `SHARED/log` subfolder

- `log.html` contains the robot's step-by-step actions and any errors
- `stdout.log` contains console messages from the robot's run

#### C → In the local `./log` subfolder

- `f1t002-logs.xlsx` contains sheets with statistics collected from `.json` files

## ⚙️ Configuration (.env)
- *MODE* → operation mode (`PROD` / `TEST`)
- *TYPE* → robot connection type `API`
- *SHARED* → path to the shared resource (empty = local operation)
- *SDIR* → local folder with test data (`./testcifs`)
- *URL_PROD*, *URL_TEST* → OpenF1 API address
- *LANGUAGE* → robot message language (`pl` / `en`)
- *WAIT_TO_RESPONSE* → request timeout (ms, minimum 5 s is used)
- *DRYRUN* → test mode without API requests (`0` / `1`)
- *RED*, *GREEN*, *GRAY*, *WHITE* → cell colors (ARGB)
- *SECURED* → decrypt `.envs` variables with Fernet (`0` / `1`)
