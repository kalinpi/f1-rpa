from datetime import datetime
import os
import glob
import functools
import time
import unicodedata
import requests
from robocorp import log
import i18n
from openpyxl import load_workbook
from openpyxl.styles import PatternFill, Font
import utils.utils as ut
import utils.utils_log as utLOG
from config import config as cfg

# Input columns: A=year, B=GP name; output column: C=status
COL_YEAR = "A"
COL_GP = "B"
COL_STATUS = "C"

GP_DICT_FILE = "GP_DICT.xlsx"
FIRST_YEAR = 2023        # OpenF1 has race data from the 2023 season
MIN_TIMEOUT = 5          # seconds - cfg.WAIT is in ms and too short for requests
API_PAUSE = 2.1          # seconds between requests - keeps below the OpenF1 limit of 30 requests/min
API_RETRIES = 4          # attempts when OpenF1 answers 429 (too many requests)
API_RETRY_WAIT = 15      # seconds, multiplied by the attempt number

# OpenF1 session fields compared with the GP name
MATCH_FIELDS = ("country_name", "location", "circuit_short_name")

# Words skipped in GP names: "Grand Prix Włoch" == "GP Włoch" == "Włoch"
SKIP_WORDS = ("grand", "prix", "gp")

TYRES = {"SOFT": "S", "MEDIUM": "M", "HARD": "H", "INTERMEDIATE": "I", "WET": "W"}

# Race sheet columns (translation keys)
RESULT_HEADERS = ("col_pos", "col_no", "col_driver", "col_team", "col_gap", "col_tyres", "col_stints")


def setup(source_folder):
    """Pickup files with pattern *RACES*.xlsx"""
    pattern = os.path.join(source_folder, "*RACES*.xlsx")
    return [os.path.basename(p) for p in glob.glob(pattern)]


def choose():
    """Checks the OpenF1 API connection - API mode does not navigate anywhere"""
    print(i18n.t('api_connection_check'), flush=True)
    if cfg.DRYRUN != 1:
        try:
            status = requests.get(f"{cfg.URL}/sessions", params={"session_key": "latest"}, timeout=api_timeout()).status_code
        except requests.RequestException as e:
            status = e
        if status != 200:
            desc = f"{i18n.t('api_connection_failed')}{status}"
            utLOG.end_error_to_log(desc)
            print(desc, flush=True)
            exit(1)
        print(i18n.t('api_connection_success'), flush=True)
    utLOG.stage_to_log(2)  # Mark Prepare at end


def do_logic(RACES_files, source_folder, destination_folder, dict_folder, log_folder):
    """Do logic
    - reads the GP dictionary from dict_folder and races from _files
    - executes logic in 'search_and_mark'
    - the effect of the execution of the logic is stored in _files (status + one sheet per race)
    - moves the _files file to out/
    """
    OFFSET = 1

    dict_path = os.path.join(dict_folder, GP_DICT_FILE)
    if not os.path.isfile(dict_path):
        utLOG.end_error_to_log(i18n.t('gp_dict_miss', n=dict_path))
        print(i18n.t('gp_dict_miss', n=dict_path), flush=True)
        exit(1)
    dict_GP = open_GP_DICT(dict_path)
    print(i18n.t('gp_dict_loaded', n=len(dict_GP)), flush=True)

    for RACES_filename in RACES_files:
        has_error = False
        wb = None
        source_path = os.path.join(source_folder, RACES_filename)

        try:
            dict_RACES = open_RACES(source_path)
            with open(source_path, 'rb') as file:  # File will be closed automatically
                wb = load_workbook(file)
                sheet = wb.worksheets[0]
                if not sheet[f"{COL_STATUS}1"].value:
                    sheet[f"{COL_STATUS}1"].value = i18n.t('col_status')
                gray = PatternFill(start_color=cfg.GRAY, end_color=cfg.GRAY, fill_type="solid")
                red = PatternFill(start_color=cfg.RED, end_color=cfg.RED, fill_type="solid")
                processed_counter = 0
                not_saved_counter = 0
                total_rows = len(dict_RACES)

                utLOG.stage_to_log(3)
                utLOG.done_to_log(0, 0, RACES_filename)

                for row_index, (key, value) in enumerate(dict_RACES.items(), start=1):
                    cell_row = row_index + OFFSET
                    print(i18n.t('race_progress', n=f'{value["year"]} {value["gp"]}'), flush=True)
                    race = search_and_mark(value["year"], value["gp"], dict_GP)
                    status = sheet[f"{COL_STATUS}{cell_row}"]

                    if isinstance(race, dict):
                        write_race_sheet(wb, race)
                        status.value = i18n.t('race_ok')
                        status.fill = gray
                    else:
                        status.value = str(race)
                        status.fill = red
                        has_error = True
                        not_saved_counter += 1

                    processed_counter += 1
                    progress = (processed_counter / total_rows) * 100
                    print(i18n.t('file_progress', n=f'{progress:.1f}%\n{row_index} of {total_rows} rows'), flush=True)
                    utLOG.done_to_log(str(processed_counter), str(processed_counter - not_saved_counter), RACES_filename)

        except Exception as e:
            utLOG.end_error_to_log(i18n.t('unexpected_error', e=e))
            print(i18n.t('unexpected_error', e=e))
            exit(1)
        finally:
            if wb is not None:
                wb.save(source_path)

        if has_error:
            ut.move_file_prefix(source_folder, destination_folder, RACES_filename, "ERROR_")
        else:
            ut.move_file(source_folder, destination_folder, RACES_filename)

        utLOG.end_sucess_to_log()  # close last JSON_LOG
        cfg.JSON_LOG_PATH = f'{log_folder}{cfg.MODE}{cfg.TYPE}_{datetime.now().strftime("_%Y-%m-%d_%H-%M-%S")}_log.json'  # Create new JSON_LOG
        utLOG.start_log()  # start new  JSON_LOG


def open_GP_DICT(filename):
    """ Opens an Excel workbook and builds a dictionary of GP aliases (A=alias, B=name), keys normalized """
    with open(filename, 'rb') as file:  # File will close automatically after exiting the block
        sheet = load_workbook(file).worksheets[0]
        dict_GP = {}
        for alias, name in sheet.iter_rows(min_row=2, max_col=2, values_only=True):  # Data starts at row 2
            if alias and name:
                dict_GP[normalize(alias)] = str(name)
    return dict_GP


def open_RACES(filename):
    """ Opens an Excel workbook and builds a dictionary of races (A=year, B=GP name)
    Reads until both A and B are empty, so a row with a missing year is reported, not skipped
    """
    with open(filename, 'rb') as file:  # File will close automatically after exiting the block
        sheet = load_workbook(file).worksheets[0]
        dict_RACES = {}
        i = 2  # Data starts at row 2
        j = 0
        while sheet[f"{COL_YEAR}{i}"].value is not None or sheet[f"{COL_GP}{i}"].value is not None:
            dict_RACES[j] = {
                "year": sheet[f"{COL_YEAR}{i}"].value,
                "gp": sheet[f"{COL_GP}{i}"].value
            }
            i += 1
            j += 1
    return dict_RACES


def search_and_mark(year, gp, dict_GP):
    """Gets the result of one race from OpenF1 API
    Returns a dictionary {"sheet": "2025 Baku", "rows": [...]} or an error description (str)
    """
    if year is None or gp is None or str(gp).strip() == "":
        return i18n.t('err_gp_empty')
    try:
        year = int(year)
    except (TypeError, ValueError):
        return i18n.t('err_year', n=year)
    if year < FIRST_YEAR or year > datetime.now().year:
        return i18n.t('err_year_range', n=year, m=FIRST_YEAR)

    if cfg.DRYRUN == 1:
        return {"sheet": f"{year} {gp}", "rows": [["DRYRUN"] * len(RESULT_HEADERS)]}

    try:
        race = find_race(year, gp, dict_GP)
        if isinstance(race, str):
            return race
        session_key = race["session_key"]
        results = api_get("session_result", session_key=session_key)
        if not results:
            return i18n.t('err_no_results', n=f'{year} {race["location"]}')
        drivers = api_get("drivers", session_key=session_key)
        stints = api_get("stints", session_key=session_key)
        return {"sheet": f'{year} {race["location"]}', "rows": build_rows(results, drivers, stints)}
    except Exception as e:
        log.info(f"{year} {gp}: {e}")
        return f"{i18n.t('err_api_request')}{e}"


def find_race(year, gp, dict_GP):
    """Finds the race session for a year and GP name (translated by the GP dictionary)
    Returns the OpenF1 session or an error description (str): not found / cancelled / ambiguous
    """
    name = normalize(dict_GP.get(normalize(gp), gp))
    sessions = race_sessions(year)
    hits = [s for s in sessions if name in (normalize(s.get(f, "")) for f in MATCH_FIELDS)]
    active = [s for s in hits if not s.get("is_cancelled")]

    if not hits:
        return i18n.t('err_gp_not_found', n=gp)
    if not active:
        return i18n.t('err_gp_cancelled', n=gp)
    if len(active) > 1:
        return i18n.t('err_gp_ambiguous', n=gp, m=", ".join(s["location"] for s in active))
    return active[0]


@functools.cache
def race_sessions(year):
    """All race sessions of a season - asked once per year, the list is reused for next rows"""
    return api_get("sessions", year=year, session_name="Race")


def build_rows(results, drivers, stints):
    """Joins results, drivers and stints into rows: Pos | No | Driver | Team | Gap | Tyres | Laps per stint"""
    drivers_by_no = {d["driver_number"]: d for d in drivers}
    rows = []
    for result in sorted(results, key=lambda r: (r.get("position") is None, r.get("position") or 0)):
        number = result["driver_number"]
        driver = drivers_by_no.get(number, {})
        own_stints = sorted((s for s in stints if s["driver_number"] == number), key=lambda s: s["stint_number"])
        rows.append([
            result.get("position") or "",
            number,
            driver.get("full_name", ""),
            driver.get("team_name", ""),
            format_gap(result),
            "".join(TYRES.get(s.get("compound"), "?") for s in own_stints),
            "/".join(stint_laps(s) for s in own_stints),
        ])
    return rows


def format_gap(result):
    """Gap to leader: '0' for the winner, '+14.609', '+1 LAP' or DSQ / DNS / DNF"""
    for flag in ("dsq", "dns", "dnf"):
        if result.get(flag):
            return flag.upper()
    gap = result.get("gap_to_leader")
    if gap is None:
        return ""
    if isinstance(gap, (int, float)):
        return "0" if gap == 0 else f"+{gap:.3f}"
    return str(gap)


def stint_laps(stint):
    """Number of laps driven on one set of tyres, '?' when OpenF1 has no lap range"""
    if stint.get("lap_start") is None or stint.get("lap_end") is None:
        return "?"
    return str(stint["lap_end"] - stint["lap_start"] + 1)


def write_race_sheet(wb, race):
    """Adds a sheet '{year} {location}' with the race result table"""
    ws = wb.create_sheet(sheet_title(wb, race["sheet"]))
    ws.append([i18n.t(h) for h in RESULT_HEADERS])
    for cell in ws[1]:
        cell.font = Font(bold=True)
    for row in race["rows"]:
        ws.append(row)


def sheet_title(wb, title):
    """Excel sheet name: without []:*?/\\ chars, max 31 chars, unique in the workbook"""
    title = "".join(" " if c in '[]:*?/\\' else c for c in str(title))[:31]
    unique, n = title, 2
    while unique in wb.sheetnames:
        suffix = f" ({n})"
        unique = title[:31 - len(suffix)] + suffix
        n += 1
    return unique


def api_get(endpoint, **params):
    """GET {URL}/{endpoint} with a pause between requests and retry on HTTP 429
    Returns a list of records ([] when OpenF1 has no results - HTTP 404)
    """
    for attempt in range(1, API_RETRIES + 1):
        time.sleep(API_PAUSE)
        response = requests.get(f"{cfg.URL}/{endpoint}", params=params, timeout=api_timeout())
        if response.status_code == 429 and attempt < API_RETRIES:
            wait = API_RETRY_WAIT * attempt
            print(i18n.t('api_rate_limit', n=wait), flush=True)
            time.sleep(wait)
            continue
        if response.status_code == 404:
            return []
        response.raise_for_status()
        data = response.json()
        return data if isinstance(data, list) else []


def api_timeout():
    """Request timeout in seconds - WAIT_TO_RESPONSE in .env is in ms"""
    return max(cfg.WAIT / 1000, MIN_TIMEOUT)


def normalize(text):
    """Lowercase, without diacritics and 'grand prix' / 'gp' words: 'Grand Prix Włoch' -> 'wloch'"""
    text = str(text).lower().replace("ł", "l")
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return " ".join(w for w in text.replace("-", " ").split() if w not in SKIP_WORDS)
