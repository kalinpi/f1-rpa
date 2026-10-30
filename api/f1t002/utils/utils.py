import os
import shutil
import i18n
import inspect
from robocorp import browser
import subprocess
from datetime import datetime
import time
import tempfile
import msoffcrypto
from pathlib import Path
from config import config as cfg

def open_the_intranet_website(url):
    browser.goto(url)
 
def move_file(source_folder, destination_folder, filename):
    """Moves the file to the destination folder by adding a timestamp to the name."""
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    current_datetime = datetime.now()
    formatted_datetime = current_datetime.strftime('%Y-%m-%d_%H-%M-%S')
    filename_with_datetime = f"{formatted_datetime}_{filename}"

    source_path = os.path.join(source_folder, filename)
    destination_path = os.path.join(destination_folder, filename_with_datetime)

    if os.path.isfile(source_path):
        shutil.move(source_path, destination_path)

def move_file_prefix(source_folder, destination_folder, filename, prefix):
    """Moves the file to the destination folder with the specified name prefix."""
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    source_path = os.path.join(source_folder, filename)
    destination_path = os.path.join(destination_folder, prefix+filename)

    #Check if item is a file (ignoring subfolders)
    if os.path.isfile(source_path):
        #Move file to destination folder, overwriting it in case of collision
        shutil.move(source_path, destination_path)

def current_function_name():
    return inspect.stack()[1].function

def connect_to_folder(path):
    """Connects to the folder """
    if os.path.exists(path):
       return True
    else:
       print(i18n.t('folder_not_exist',n=f'{path}'), flush=True)
       return False 

def _get_libreoffice_profile_uri():
    """
    Returns LibreOffice profile URI for headless conversion.
    Uses /tmp/libreoffice_profiles as default base.
    """
    profile_base = cfg.LIBREOFFICE_PROFILE_BASE
    current_dir = os.path.basename(os.getcwd())
    profile_dir = Path(f"{profile_base}/{current_dir}_{cfg.CFN}")
    profile_dir.mkdir(parents=True, exist_ok=True)
    return profile_dir.as_uri()

def libreoffice_xls_to_xlsx(input_path, output_path):
    """
    Uses LibraOffice. Installation required on the server where RPA is running:
    - input_path: file to save
    - output_path: directory where to save with the name given in input_path
    """
    if not os.path.isfile(input_path):
        raise FileNotFoundError(input_path)

    if not os.path.isdir(output_path):
        raise FileNotFoundError(output_path)


    profile_uri = _get_libreoffice_profile_uri()
    try:
        subprocess.run([
            "libreoffice", "--headless",
            f"-env:UserInstallation={profile_uri}",
            "--convert-to", "xlsx", "--calc", "--infilter='Excel 2007 XML'",
            "--outdir", output_path,
            input_path
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception as e:
        print(i18n.t('err_xls_conversion',n=f'{input_path} — {e}'), flush=True)
        return False

def libreoffice_docx_to_pdf_batch(docx_files: list[str], output_dir: str) -> bool:
    """
    Converts multiple DOCX files to PDF in a single LibreOffice batch operation.

    Args:
        docx_files (list[str]): List of DOCX file paths to convert.
        output_dir (str): Directory where PDF files will be saved.

    Returns:
        bool: True if conversion succeeded, False otherwise.
    """
    if not docx_files:
        return True

    profile_uri = _get_libreoffice_profile_uri()

    try:
        subprocess.run(
            [
                "libreoffice",
                "--headless",
                "--nofirststartwizard",
                f"-env:UserInstallation={profile_uri}",
                "--convert-to", "pdf",
                "--outdir", output_dir,
                *docx_files,
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return True
    except Exception as e:
        print(i18n.t('batch_pdf_conversion_error', e=e), flush=True)
        return False    
    
def encrypt_xlsx(filepath: str, password: str) -> str:
    """
    Encrypts an Excel file with a native password (compatible with MS Excel / LibreOffice).
    
    Args:
        filepath (str): path to the xlsx file
        password (str): password to protect the file

    Returns:
        str: path to the encrypted file (same as input)
    """
    # Create a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.tmp') as tmp_file:
        tmp_path = tmp_file.name
    
    try:
        # Encrypt to temporary file
        with open(filepath, "rb") as f_in, open(tmp_path, "wb") as f_out:
            office_file = msoffcrypto.OfficeFile(f_in)
            office_file.encrypt(password, f_out)
        
        # Replace original file with encrypted one
        shutil.move(tmp_path, filepath)
        
        return filepath
        
    except Exception as e:
        # Remove temporary file in case of error
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise e
    
def wait_for_file_complete(filepath, timeout=30, stable_time=2):
    """Waits until the file stops changing (fully written to disk)."""
    start_time = time.time()
    last_size = -1
    stable_since = None
    
    while time.time() - start_time < timeout:
        if os.path.exists(filepath):
            try:
                current_size = os.path.getsize(filepath)
                
                if current_size == last_size and current_size > 0:
                    if stable_since is None:
                        stable_since = time.time()
                    elif time.time() - stable_since >= stable_time:
                        return True
                else:
                    stable_since = None
                    last_size = current_size
                    
            except OSError:
                pass
        
        time.sleep(0.5)
    
    return False

def libreoffice_recalc_xlsx(input_path, output_path=None):
    """
    Recalculates formulas in an Excel .xlsx file using LibreOffice Calc (Linux only).
    - input_path: path to the .xlsx file to recalculate
    - output_path: directory where to save the recalculated file (default: same as input)
    Returns True if successful, False otherwise.
    """
    if not os.path.isfile(input_path):
        raise FileNotFoundError(input_path)

    if output_path is None:
        output_path = os.path.dirname(input_path)
    elif not os.path.isdir(output_path):
        raise FileNotFoundError(output_path)

    profile_uri = _get_libreoffice_profile_uri()
    base_name = os.path.splitext(os.path.basename(input_path))[0]

    try:
        # 1) Convert xlsx -> ods to force Calc import/recalculation pipeline
        subprocess.run([
            "libreoffice", "--headless",
            f"-env:UserInstallation={profile_uri}",
            "--calc",
            "--convert-to", "ods",
            "--outdir", output_path,
            input_path
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        generated_ods = os.path.join(output_path, f"{base_name}.ods")
        if not os.path.exists(generated_ods):
            raise FileNotFoundError(generated_ods)

        # 2) Convert ods -> xlsx; this output is the recalculated workbook
        subprocess.run([
            "libreoffice", "--headless",
            f"-env:UserInstallation={profile_uri}",
            "--calc",
            "--convert-to", "xlsx",
            "--outdir", output_path,
            generated_ods
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        return True
    except Exception as e:
        print(i18n.t('err_xls_conversion', n=f'{input_path} — {e}'), flush=True)
        return False
    finally:
        if os.path.exists(generated_ods):
            try:
                os.remove(generated_ods)
            except OSError:
                pass