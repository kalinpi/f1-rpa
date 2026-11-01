from datetime import datetime
import os
import re
import glob
import functools
import time
import unicodedata
from robocorp import browser
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
FIRST_YEAR = 1950        # first Formula One World Championship season
MIN_TIMEOUT = 20000      # ms - Playwright timeout when cfg.WAIT based value is too short for Wikipedia
PAGE_PAUSE = 5           # seconds between page loads - Crawl-delay from Wikipedia robots.txt
PAGE_RETRIES = 3         # attempts when a page does not load

# Wikipedia pages: season article with the calendar, race article with the classification
SEASON_PAGE = "/wiki/{year}_Formula_One_World_Championship"
RACE_PAGE = "/wiki/{year}_{name}"
RACE_TABLE = "xpath=//*[@id='Race_classification']/following::table[contains(@class,'wikitable')][1]"

# Words skipped when comparing GP names ("Grand Prix Włoch" = "Włoch")
SKIP_WORDS = ("grand", "prix", "gp")

# Wikipedia position of a driver without a finishing place -> gap column (same values as F1T002)
NOT_CLASSIFIED = {"RET": "DNF", "NC": "DNF", "DSQ": "DSQ", "EX": "DSQ", "DNS": "DNS", "DNQ": "DNS", "DNPQ": "DNS", "WD": "DNS"}

# Race sheet columns - the same as F1T002, tyres and stints are not published on Wikipedia (left empty)
RESULT_HEADERS = ("col_pos", "col_no", "col_driver", "col_team", "col_gap", "col_tyres", "col_stints")

# Reads the calendar table of a season page: [{gp, link, country, circuit}, ...] or null
JS_CALENDAR = """() => {
    const head = t => t.rows.length ? t.rows[0].innerText : "";
    const cal = [...document.querySelectorAll("table.wikitable")].find(t => /Round/.test(head(t)) && /Circuit/.test(head(t)));
    if (!cal) return null;
    return [...cal.rows].slice(1).filter(r => r.cells.length >= 4).map(r => {
        const gpLink = r.cells[1].querySelector("a");
        const flag = r.cells[2].querySelector("span.flagicon a");
        return {
            gp: r.cells[1].innerText.trim(),
            link: gpLink ? gpLink.title : r.cells[1].innerText.trim(),
            country: flag ? flag.title : "",
            circuit: r.cells[2].innerText.trim()
        };
    });
}"""

# Reads a classification table: rows of cells {t: text without footnotes, a: first link text}
JS_TABLE = """t => [...t.rows].map(r => [...r.cells].map(c => {
    const x = c.cloneNode(true);
    x.querySelectorAll("sup").forEach(s => s.remove());
    const a = x.querySelector("a");
    return {t: x.textContent.replace(/\\s+/g, " ").trim(), a: a ? a.textContent.trim() : ""};
}))"""


def setup(source_folder):
    """Pickup files with pattern *RACES*.xlsx"""
    pattern = os.path.join(source_folder, "*RACES*.xlsx")
    return [os.path.basename(p) for p in glob.glob(pattern)]


def choose():
    """Checks that the start page (Wikipedia) is open - the site has no cookie consent to accept"""
    print(i18n.t('site_check', n=cfg.URL), flush=True)
    try:
        title = browser.page().title()
    except Exception as e:
        title = str(e)
    if "Wikipedia" not in title:
        utLOG.end_error_to_log(i18n.t('site_failed', n=cfg.URL))
        print(i18n.t('site_failed', n=cfg.URL), flush=True)
        exit(1)
    print(i18n.t('site_ok', n=title), flush=True)
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
        cfg.JSON_LOG_PATH = f'{log_folder}{cfg.MODE}{cfg.TYPE}_{datetime.now().strftime("_%Y-%m-%d_%H-%M-%S_%f")}_log.json'  # Create new JSON_LOG (microseconds: a fast run must not overwrite the closed log)
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
    """Reads the result of one race from Wikipedia
    Returns a dictionary {"sheet": "2025 Azerbaijan", "rows": [...]} or an error description (str)
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
        name = short_name(race["gp"])
        rows = build_rows(race_table(year, race["link"]))
        if not rows:
            return i18n.t('err_no_results', n=f'{year} {name}')
        return {"sheet": f'{year} {name}', "rows": rows}
    except Exception as e:
        log.info(f"{year} {gp}: {e}")
        return f"{i18n.t('err_page')}{str(e).splitlines()[0] if str(e) else type(e).__name__}"


def find_race(year, gp, dict_GP):
    """Finds the race in the season calendar for a year and GP name (translated by the GP dictionary)
    Returns the calendar row or an error description (str): no calendar / not found / ambiguous
    """
    name = normalize(dict_GP.get(normalize(gp), gp))
    calendar = season_calendar(year)
    if calendar is None:
        return i18n.t('err_season', n=year)
    hits = [race for race in calendar if matches(name, race)] if name else []

    if not hits:
        return i18n.t('err_gp_not_found', n=gp)
    if len(hits) > 1:
        return i18n.t('err_gp_ambiguous', n=gp, m=", ".join(short_name(race["gp"]) for race in hits))
    return hits[0]


def matches(name, race):
    """GP name (normalized) is the country of the race or a phrase of the GP name / circuit and city"""
    return (name == normalize(race["country"])
            or f" {name} " in f' {normalize(race["gp"])} '
            or f" {name} " in f' {normalize(race["circuit"])} ')


@functools.cache
def season_calendar(year):
    """Calendar of a season - read once per year, the list is reused for next rows"""
    print(i18n.t('season_page', n=year), flush=True)
    page = open_page(SEASON_PAGE.format(year=year))
    return page.evaluate(JS_CALENDAR) if page else None


def race_table(year, link):
    """Race classification table of a race page as rows of cells, [] when the page or the table is missing"""
    page = open_page(RACE_PAGE.format(year=year, name=link.replace(" ", "_")))
    if page is None or not page.locator("h1").first.inner_text().startswith(str(year)):
        return []
    table = page.locator(RACE_TABLE)
    if table.count() == 0:
        return []
    return table.first.evaluate(JS_TABLE)


def open_page(path):
    """Opens a Wikipedia page with a pause before every load (robots.txt Crawl-delay) and retries
    Returns the page or None when the article does not exist (HTTP 404)
    """
    for attempt in range(1, PAGE_RETRIES + 1):
        time.sleep(PAGE_PAUSE)
        page = browser.page()  # a new tab when the previous one was closed after an error
        try:
            response = page.goto(f"{cfg.URL}{path}", wait_until="domcontentloaded", timeout=page_timeout())
            if response is not None and response.status == 404:
                return None
            if response is None or not response.ok:
                raise Exception(f"HTTP {response.status if response else '-'} {path}")
            return page
        except Exception as e:  # Playwright TimeoutError is not the built-in TimeoutError
            log.info(f"{path} attempt {attempt}: {e}")
            if attempt == PAGE_RETRIES:
                raise
            close_page(page)


def close_page(page):
    """Closes a broken tab (e.g. crashed renderer), so browser.page() opens a new one"""
    try:
        page.close()
    except Exception:
        pass


def build_rows(table):
    """Converts the classification table into rows: Pos | No | Driver | Team | Gap | Tyres | Laps per stint
    Columns are found by header names, rows of other length (source, fastest lap notes) are skipped
    """
    if not table:
        return []
    header = [cell["t"] for cell in table[0]]
    col = {key: next((i for i, h in enumerate(header) if h.startswith(key)), None) for key in ("Pos", "No", "Driver", "Constructor", "Time")}
    if None in (col["Pos"], col["Driver"], col["Constructor"], col["Time"]):
        return []
    rows = []
    for cells in table[1:]:
        if len(cells) != len(header):
            continue
        pos = cells[col["Pos"]]["t"]
        number = cells[col["No"]]["t"] if col["No"] is not None else ""
        team = cells[col["Constructor"]]
        rows.append([
            int(pos) if pos.isdigit() else "",
            int(number) if number.isdigit() else number,
            cells[col["Driver"]]["t"],
            team["a"] or team["t"],
            format_gap(pos, cells[col["Time"]]["t"]),
            "",
            "",
        ])
    return rows


def format_gap(pos, time_text):
    """Gap to leader: '0' for the winner, '+14.609', '+1 LAP' or DSQ / DNS / DNF
    Minutes are converted to seconds like in F1T002: '+1:07.606' -> '+67.606'
    """
    if not pos.isdigit():
        return NOT_CLASSIFIED.get(pos.upper(), "DNF")
    if pos == "1":
        return "0"
    minutes = re.fullmatch(r"\+(\d+):(\d+(?:\.\d+)?)", time_text)
    if minutes:
        return f"+{int(minutes[1]) * 60 + float(minutes[2]):.3f}"
    return time_text.upper() if "lap" in time_text.lower() else time_text


def write_race_sheet(wb, race):
    """Adds a sheet '{year} {GP}' with the race result table"""
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


def short_name(gp):
    """GP name without 'Grand Prix': 'Azerbaijan Grand Prix' -> 'Azerbaijan'"""
    return " ".join(str(gp).replace("Grand Prix", " ").split())


def page_timeout():
    """Playwright timeout in ms (cfg.WAIT is in ms, Playwright counts ms too)"""
    return max(cfg.WAIT * 50, MIN_TIMEOUT)


def normalize(text):
    """Lowercase, without diacritics, punctuation and 'grand prix' / 'gp' words: 'Circuit de Spa-Francorchamps, Stavelot' -> 'circuit de spa francorchamps stavelot'"""
    text = str(text).lower().replace("ł", "l")
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return " ".join(w for w in re.split(r"[^a-z0-9]+", text) if w and w not in SKIP_WORDS)
