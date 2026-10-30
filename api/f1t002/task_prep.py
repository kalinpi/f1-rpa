from datetime import datetime
import os
import glob
import requests
from robocorp import log
import i18n
from openpyxl import load_workbook
from openpyxl.styles import PatternFill
import utils.utils as ut
import utils.utils_log as utLOG
from config import config as cfg

# Output columns: D..L
COL_TEMP = "D"
COL_FEELS = "E"
COL_HUMIDITY = "F"
COL_PRESSURE = "G"
COL_WIND = "H"
COL_DESC = "I"
COL_SUNRISE = "J"
COL_SUNSET = "K"
COL_ERROR = "L"

# Result column -> key returned by 'search_and_mark'
RESULT_KEYS = {
    COL_TEMP: "temp",
    COL_FEELS: "feels",
    COL_HUMIDITY: "humidity",
    COL_PRESSURE: "pressure",
    COL_WIND: "wind",
    COL_DESC: "desc",
    COL_SUNRISE: "sunrise",
    COL_SUNSET: "sunset",
}

HEADERS = {
    COL_TEMP: "temp (°C)",
    COL_FEELS: "odczuwalna (°C)",
    COL_HUMIDITY: "wilgotność (%)",
    COL_PRESSURE: "ciśnienie (hPa)",
    COL_WIND: "wiatr (m/s)",
    COL_DESC: "opis",
    COL_SUNRISE: "wschód słońca",
    COL_SUNSET: "zachód słońca",
    COL_ERROR: "opis_bledu",
}


def setup(source_folder):
    """Pickup files with pattern *CITIES*.xlsx"""
    pattern = os.path.join(source_folder, "*CITIES*.xlsx")
    return [os.path.basename(p) for p in glob.glob(pattern)]


def choose():
    """Checks that the API key is available - API mode does not navigate anywhere"""
    with log.suppress():
        if cfg.DRYRUN != 1 and len(cfg.XAPIKEY) == 0:
            utLOG.end_error_to_log(i18n.t('err_apikey'))
            print(i18n.t('err_apikey'), flush=True)
            exit(1)
    print(i18n.t('api_connection_check'), flush=True)
    utLOG.stage_to_log(2)  # Mark Prepare at end


def do_logic(WEATHER_files, source_folder, destination_folder, log_folder):
    """Do logic
    - reads cities from _files
    - executes logic in 'search_and_mark'
    - the effect of the execution of the logic is stored in _files
    - moves the _files file to out/
    """
    OFFSET = 1

    for WEATHER_filename in WEATHER_files:
        has_error = False
        wb = None
        source_path = os.path.join(source_folder, WEATHER_filename)

        try:
            dict_CITIES = open_CITIES(source_path)
            with open(source_path, 'rb') as file:  # File will be closed automatically
                wb = load_workbook(file)
                sheet = wb.worksheets[0]
                write_headers(sheet)
                gray = PatternFill(start_color=cfg.GRAY, end_color=cfg.GRAY, fill_type="solid")
                red = PatternFill(start_color=cfg.RED, end_color=cfg.RED, fill_type="solid")
                processed_counter = 0
                not_saved_counter = 0
                total_rows = len(dict_CITIES)

                utLOG.stage_to_log(3)
                utLOG.done_to_log(0, 0, WEATHER_filename)

                for row_index, (key, value) in enumerate(dict_CITIES.items(), start=1):
                    cell_row = row_index + OFFSET
                    weather = search_and_mark(value["city"], value["country_code"])

                    if isinstance(weather, dict):
                        for col, key_name in RESULT_KEYS.items():
                            sheet[f"{col}{cell_row}"].value = weather.get(key_name, "")
                            sheet[f"{col}{cell_row}"].fill = gray
                    else:
                        sheet[f"{COL_ERROR}{cell_row}"].value = str(weather)
                        sheet[f"{COL_ERROR}{cell_row}"].fill = red
                        has_error = True
                        not_saved_counter += 1

                    processed_counter += 1
                    progress = (processed_counter / total_rows) * 100
                    print(i18n.t('file_progress', n=f'{progress:.1f}%\n{row_index} of {total_rows} rows'), flush=True)
                    utLOG.done_to_log(str(processed_counter), str(processed_counter - not_saved_counter), WEATHER_filename)

        except Exception as e:
            utLOG.end_error_to_log(i18n.t('unexpected_error', e=e))
            print(i18n.t('unexpected_error', e=e))
            exit(1)
        finally:
            if wb is not None:
                wb.save(source_path)

        if has_error:
            ut.move_file_prefix(source_folder, destination_folder, WEATHER_filename, "ERROR_")
        else:
            ut.move_file(source_folder, destination_folder, WEATHER_filename)

        utLOG.end_sucess_to_log()  # close last JSON_LOG
        cfg.JSON_LOG_PATH = f'{log_folder}{cfg.MODE}{cfg.TYPE}_{datetime.now().strftime("_%Y-%m-%d_%H-%M-%S")}_log.json'  # Create new JSON_LOG
        utLOG.start_log()  # start new  JSON_LOG


def write_headers(sheet):
    """Writes the result column headers in row 1 when they are missing"""
    for col, title in HEADERS.items():
        if not sheet[f"{col}1"].value:
            sheet[f"{col}1"].value = title


def open_CITIES(filename):
    """ Opens an Excel workbook and builds a dictionary of cities (A=city, B=country, C=country_code) """
    with open(filename, 'rb') as file:  # File will close automatically after exiting the block
        wb = load_workbook(file)
        sheet = wb.worksheets[0]
        dict_CITIES = {}
        i = 2  # Data starts at row 2
        j = 0
        while sheet[f"A{i}"].value is not None:
            dict_CITIES[j] = {
                "city": sheet[f"A{i}"].value,
                "country": sheet[f"B{i}"].value,
                "country_code": sheet[f"C{i}"].value
            }
            i += 1
            j += 1
    return dict_CITIES


def search_and_mark(city, country_code=""):
    """Gets the weather for a city from the REST API
    Returns a dictionary with the readings, or NOT_FOUND / SERVER_ERROR / API_ERROR
    """
    if cfg.DRYRUN == 1:
        return {key_name: "DRYRUN" for key_name in RESULT_KEYS.values()}

    item_id = f"{city},{country_code}" if country_code else f"{city}"
    params = {"q": item_id, "units": "metric", "lang": cfg.LANGUAGE, "appid": cfg.XAPIKEY}
    try:
        response = requests.get(cfg.URL, params=params, timeout=cfg.WAIT)
        response_code = response.status_code
        tmp_desc = i18n.t('api_error', item_id=item_id, status_code=response_code)

        if response_code == 200:
            data = response.json()
            main = data.get("main", {})
            sun = data.get("sys", {})
            return {
                "temp": main.get("temp", ""),
                "feels": main.get("feels_like", ""),
                "humidity": main.get("humidity", ""),
                "pressure": main.get("pressure", ""),
                "wind": data.get("wind", {}).get("speed", ""),
                "desc": (data.get("weather", [{}])[0] or {}).get("description", ""),
                "sunrise": format_time(sun.get("sunrise")),
                "sunset": format_time(sun.get("sunset")),
            }
        elif response_code == 404:
            log.info(tmp_desc)
            print(f'{tmp_desc} - error', flush=True)
            return "NOT_FOUND"
        elif response_code == 500:
            log.info(tmp_desc)
            print(f'{tmp_desc} - skip', flush=True)
            return "SERVER_ERROR"
        else:
            log.info(tmp_desc)
            print(f'{tmp_desc} - skip', flush=True)
            return "API_ERROR"
    except Exception as e:
        return f"ERROR: {e}"


def format_time(timestamp):
    """Formats a Unix timestamp (seconds) as HH:MM:SS"""
    if not timestamp:
        return ""
    try:
        return datetime.fromtimestamp(int(timestamp)).strftime("%H:%M:%S")
    except Exception:
        return ""
