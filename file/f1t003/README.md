# F1T003

## 📋 General Information
| | |
|---|---|
| **Business Owner** | xxxxx@xxx.pl |
| **RPA Service** | ServiceDesk → Request/Incident → Category → RPA |
| **Robot account (system)** | `xxx_F1T` |
| **AD account (network/resources)** | `xxx_F1T_ad` |

## Description

The robot computes Formula 1 race statistics from the output file of F1T001 / F1T002 (no Internet connection needed) and consists of tasks:

⚡ prep - checks whether there is data in `SHARED\in\` in a file named *RACES*.xlsx (one sheet per race: Pos | No | Driver | Team | Gap | Tyres | Laps per stint), computes statistics for every race and a summary, adds the `Statistics` sheet and moves the file to `SHARED\out\`.

[📖 Detailed task description](docs/EN/README.md)

## ▶️ Run

```
./F1T003.sh prep
```

## Results

🚀 After running the robot, check the processed files in `SHARED/out/`.

#### A → In the `SHARED/out` subfolder

- `*RACES*.xlsx` files that the robot has processed
- `Statistics` sheet: one row per race (winner, winner team, classified, DNF/DNS/DSQ, average pit stops, most common tyre strategy, status)
- summary below the table: number of races, most common strategy, average pit stops, total DNF, best team (points 25-18-15-12-10-8-6-4-2-1), most wins
- files include the date and time of processing appended
- files with errors (e.g. a sheet in a wrong format) are prefixed with `ERROR_`

#### B → In the `SHARED/log` subfolder

- `log.html` contains the robot's step-by-step actions and any errors
- `stdout.log` contains console messages from the robot's run

#### C → In the local `./log` subfolder

- `f1t003-logs.xlsx` contains sheets with statistics collected from `.json` files

## ⚙️ Configuration (.env)
- *MODE* → operation mode (`PROD` / `TEST`)
- *TYPE* → robot connection type `FIL`
- *SHARED* → path to the shared resource (empty = local operation)
- *SDIR* → local folder with test data (`./testcifs`)
- *URL_PROD*, *URL_TEST* → not used (FILE mode)
- *LANGUAGE* → robot message language (`pl` / `en`)
- *WAIT_TO_RESPONSE* → not used (FILE mode)
- *DRYRUN* → test mode, statuses only without statistics (`0` / `1`)
- *RED*, *GREEN*, *GRAY*, *WHITE* → cell colors (ARGB)
- *SECURED* → decrypt `.envs` variables with Fernet (`0` / `1`)
