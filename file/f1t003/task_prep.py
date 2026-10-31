from datetime import datetime
from collections import Counter
import os
import glob
import i18n
from openpyxl import load_workbook
from openpyxl.styles import PatternFill, Font
import utils.utils as ut
import utils.utils_log as utLOG
from config import config as cfg

# Race sheet columns written by F1T001 / F1T002: Pos | No | Driver | Team | Gap | Tyres | Laps per stint
RACE_COLUMNS = 7
COL_POS, COL_NO, COL_DRIVER, COL_TEAM, COL_GAP, COL_TYRES, COL_STINTS = range(RACE_COLUMNS)
NOT_CLASSIFIED = ("DNF", "DNS", "DSQ")

# Points for positions 1-10 (main race, without sprint and fastest lap)
POINTS = (25, 18, 15, 12, 10, 8, 6, 4, 2, 1)

# Statistics sheet: one row per race, status in the last column
STATS_HEADERS = ("col_race", "col_winner", "col_winner_team", "col_classified", "col_dnf", "col_avg_pits", "col_strategy", "col_status")
COL_STATUS = len(STATS_HEADERS)


def setup(source_folder):
    """Pickup files with pattern *RACES*.xlsx (output of F1T001 / F1T002)"""
    pattern = os.path.join(source_folder, "*RACES*.xlsx")
    return [os.path.basename(p) for p in glob.glob(pattern)]


def choose():
    """FILE mode works on local files only - there is nothing to select"""
    utLOG.stage_to_log(2)  # Mark Prepare at end


def do_logic(RACES_files, source_folder, destination_folder, log_folder):
    """Do logic
    - reads race sheets (one per race) from _files
    - computes statistics per race and a summary in 'search_and_mark' / 'summarize'
    - the effect of the execution of the logic is stored in _files (sheet 'Statistics')
    - moves the _files file to out/
    """
    for RACES_filename in RACES_files:
        has_error = False
        wb = None
        source_path = os.path.join(source_folder, RACES_filename)

        try:
            with open(source_path, 'rb') as file:  # File will be closed automatically
                wb = load_workbook(file)
                stats_name = i18n.t('stats_sheet')
                if stats_name in wb.sheetnames:  # re-run: build statistics again
                    del wb[stats_name]
                race_sheets = wb.worksheets[1:]
                stats = wb.create_sheet(stats_name)
                stats.append([i18n.t(h) for h in STATS_HEADERS])
                for cell in stats[1]:
                    cell.font = Font(bold=True)
                gray = PatternFill(start_color=cfg.GRAY, end_color=cfg.GRAY, fill_type="solid")
                red = PatternFill(start_color=cfg.RED, end_color=cfg.RED, fill_type="solid")
                processed_counter = 0
                not_saved_counter = 0
                total_rows = len(race_sheets)
                all_races = []

                utLOG.stage_to_log(3)
                utLOG.done_to_log(0, 0, RACES_filename)

                if total_rows == 0:
                    stats.append([i18n.t('err_no_races')])
                    stats.cell(row=2, column=1).fill = red
                    has_error = True

                for row_index, race_sheet in enumerate(race_sheets, start=1):
                    print(i18n.t('race_sheet', n=race_sheet.title), flush=True)
                    race = search_and_mark(race_sheet)

                    if isinstance(race, dict):
                        all_races.append(race["rows"])
                        values = race_stats_row(race_sheet.title, race["rows"]) if cfg.DRYRUN != 1 else [race_sheet.title]
                        stats.append(values + [""] * (COL_STATUS - 1 - len(values)) + [i18n.t('race_ok')])
                        stats.cell(row=stats.max_row, column=COL_STATUS).fill = gray
                    else:
                        stats.append([race_sheet.title] + [""] * (COL_STATUS - 2) + [str(race)])
                        stats.cell(row=stats.max_row, column=COL_STATUS).fill = red
                        has_error = True
                        not_saved_counter += 1

                    processed_counter += 1
                    progress = (processed_counter / total_rows) * 100
                    print(i18n.t('file_progress', n=f'{progress:.1f}%\n{row_index} of {total_rows} sheets'), flush=True)
                    utLOG.done_to_log(str(processed_counter), str(processed_counter - not_saved_counter), RACES_filename)

                if all_races and cfg.DRYRUN != 1:
                    write_summary(stats, summarize(all_races))

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


def search_and_mark(race_sheet):
    """Reads one race sheet (header in row 1, drivers from row 2)
    Returns a dictionary {"rows": [[Pos, No, Driver, Team, Gap, Tyres, Stints], ...]} or an error description (str)
    """
    header = [c.value for c in race_sheet[1][:RACE_COLUMNS]]
    if len(header) < RACE_COLUMNS or any(h in (None, "") for h in header):
        return i18n.t('err_race_sheet')
    rows = [list(r[:RACE_COLUMNS]) for r in race_sheet.iter_rows(min_row=2, values_only=True) if r[COL_DRIVER]]
    if not rows:
        return i18n.t('err_race_empty')
    return {"rows": rows}


def race_stats_row(title, rows):
    """Statistics of one race: Race | Winner | Winner team | Classified | DNF/DNS/DSQ | Avg pit stops | Most common strategy"""
    winner = next((r for r in rows if position(r) == 1), None)
    classified = [r for r in rows if is_classified(r)]
    return [
        title,
        winner[COL_DRIVER] if winner else "",
        winner[COL_TEAM] if winner else "",
        len(classified),
        len(rows) - len(classified),
        avg_pit_stops(rows),
        most_common_strategy(classified),
    ]


def summarize(all_races):
    """Summary over all races: strategy, pit stops, DNF, best team by points, most wins"""
    all_rows = [r for rows in all_races for r in rows]
    team_points = Counter()
    wins = Counter()
    for r in all_rows:
        pos = position(r)
        if pos and pos <= len(POINTS):
            team_points[r[COL_TEAM]] += POINTS[pos - 1]
        if pos == 1:
            wins[r[COL_DRIVER]] += 1
    best_team = team_points.most_common(1)
    most_wins = wins.most_common(1)
    return [
        ("sum_races", len(all_races)),
        ("sum_strategy", most_common_strategy([r for r in all_rows if is_classified(r)])),
        ("sum_avg_pits", avg_pit_stops(all_rows)),
        ("sum_dnf", sum(1 for r in all_rows if not is_classified(r))),
        ("sum_best_team", f"{best_team[0][0]} ({best_team[0][1]})" if best_team else ""),
        ("sum_most_wins", f"{most_wins[0][0]} ({most_wins[0][1]})" if most_wins else ""),
    ]


def write_summary(stats, summary):
    """Writes the summary block below the race table: label in column A, value in column B"""
    stats.append([])
    stats.append([i18n.t('sum_title')])
    stats.cell(row=stats.max_row, column=1).font = Font(bold=True)
    for key, value in summary:
        stats.append([i18n.t(key), value])


def position(row):
    """Finishing position as int, None for DNF without position"""
    try:
        return int(row[COL_POS])
    except (TypeError, ValueError):
        return None


def is_classified(row):
    """Driver finished the race (gap is not DNF / DNS / DSQ)"""
    return str(row[COL_GAP] or "").upper() not in NOT_CLASSIFIED


def avg_pit_stops(rows):
    """Average number of pit stops = tyre sets - 1, only drivers with tyre data"""
    stops = [len(str(r[COL_TYRES])) - 1 for r in rows if r[COL_TYRES]]
    return round(sum(stops) / len(stops), 2) if stops else ""


def most_common_strategy(rows):
    """Most common tyre strategy (e.g. 'MH'), first one wins a tie"""
    strategies = Counter(str(r[COL_TYRES]) for r in rows if r[COL_TYRES])
    return strategies.most_common(1)[0][0] if strategies else ""
