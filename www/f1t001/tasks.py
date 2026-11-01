import os
from robocorp import browser
from robocorp.tasks import task
import i18n
from datetime import datetime
from config import config as cfg
import utils.utils as ut
import utils.utils_log as utLOG
import task_prep as EXT
from task_dolog import process_logs

source_folder = './in/'
destination_folder = './out/'
log_folder = './log/'
dict_folder = './dicts/'
files = []
cfg.set_translation()
cfg.VERSION = cfg.VERSION+"/1.0.0"

@task
def prep():
    """Triggers the main robot flow:
    - Sets the SHARED/local mode and paths,
    - Initializes the JSON log,
    - Opens the resource (URL dependent on MODE),
    - Performs extension steps (EXT.*),
    - Cleans the log.
    Exit from the system:
    - when the configuration is incorrect or there is no access to folders.
    """
    if len(cfg.SHARED) >0:
        global source_folder, destination_folder, dict_folder
        source_folder = source_folder.replace("./", cfg.SDIR+"/" )
        destination_folder = destination_folder.replace("./", cfg.SDIR+"/" )
        dict_folder = dict_folder.replace("./", cfg.SDIR+"/" )
        if not (ut.connect_to_folder(source_folder) and ut.connect_to_folder(destination_folder) and ut.connect_to_folder(dict_folder)):
            exit(1)

    """SET log to json"""
    #Log Configuration
    cfg.CFN=ut.current_function_name()
    cfg.JSON_LOG_PATH = f'{log_folder}{cfg.MODE}{cfg.TYPE}_{datetime.now().strftime("_%Y-%m-%d_%H-%M-%S")}_log.json'
    utLOG.start_log()
    print(i18n.t('step_0',n=f'{cfg.CFN} - {cfg.VERSION} - {cfg.FRAMEWORK}'), flush=True)

    if cfg.DRYRUN:
        print(i18n.t('dryrun_enabled'), flush=True)

    """Navigates to the given URL"""
    browser.configure(slowmo=cfg.WAIT)
    #browser.configure(headless=True)

    match cfg.MODE:
        case "PROD":
            cfg.URL=cfg.URL_PROD
        case "TEST":
            browser.configure_context(ignore_https_errors = True)
            cfg.URL=cfg.URL_TEST
        case _:
            utLOG.end_error_to_log(i18n.t('err_incorrect_mode'))
            print(i18n.t('err_incorrect_mode'), flush=True)
            exit(1)

    # Extention code start
    files=EXT.setup(source_folder)
    if len(files) == 0:
        utLOG.end_error_to_log(i18n.t('file_in_miss'))
        print(i18n.t('file_in_miss'), flush=True)
        exit(0)

    ut.open_the_intranet_website(cfg.URL)
    EXT.choose()
    EXT.do_logic(files,source_folder,destination_folder,dict_folder,log_folder)

    # Extention code stop

    utLOG.clean_log()

@task
def Dolog():
    """Aggregates JSON logs into an Excel workbook:
    - Searches for logs for cfg. YEAR/cfg. MONTH,
    - Builds the {YYYY-MM} sheet and updates 'Together'.
    Tool version: 1.5.0 (doc).
   """
    current_dir = os.path.basename(os.getcwd())
    workbook_name = f"{current_dir[:7]}-logs.xlsx"
    workbook_path = os.path.join(log_folder, workbook_name)
    cfg.CFN=ut.current_function_name()
    if not os.path.exists(log_folder):
        print(i18n.t('folder_not_exist',n=f'{log_folder}'), flush=True)
        return
    process_logs(cfg.YEAR, cfg.MONTH, log_folder, workbook_path)
