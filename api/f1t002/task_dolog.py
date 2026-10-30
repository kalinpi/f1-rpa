import os
import json
import i18n
from datetime import datetime
from openpyxl.styles import NamedStyle
from openpyxl import Workbook, load_workbook
from config import config as cfg

def convert_value(value):
    """Convert a string value to int or float if possible, otherwise return the original value. Useful for normalizing log data types."""
    if isinstance(value, str):
        try:
            return int(value)
        except ValueError:
            try:
                return float(value)
            except ValueError:
                return value  
    return value

def sort_sheets(workbook):
    """Move the translated summary sheet to the first position, then place the first monthly sheet after it."""
    summary_sheet_name = i18n.t('log_sheet_sum_name')
    if summary_sheet_name in workbook.sheetnames:
        workbook.move_sheet(summary_sheet_name, offset=-workbook.sheetnames.index(summary_sheet_name))

    monthly_sheets = [name for name in workbook.sheetnames if name != summary_sheet_name]
    if monthly_sheets:
        first_monthly = monthly_sheets[0]
        summary_idx = workbook.sheetnames.index(summary_sheet_name)
        first_monthly_idx = workbook.sheetnames.index(first_monthly)
        if first_monthly_idx != summary_idx + 1:
            workbook.move_sheet(first_monthly, offset=(summary_idx + 1) - first_monthly_idx)

def find_first_empty_row(sheet):
    """Find the first empty row in the sheet by checking the first 20 columns. Used to append new log entries without overwriting existing data."""
    row = 2
    while any(sheet.cell(row=row, column=col).value for col in range(1, 20)):
        row += 1
    return row

def process_logs(year, month, log_folder, workbook_path): 
    """
    Process log files for a given year and month:
    - Loads .json log files matching the period
    - Updates or creates Excel sheets with log data
    - Copies statistics, applies formatting, and manages summary formulas
    - Handles errors and removes processed log files
    - Updates the 'Sum' summary sheet and sorts entries by date
    """
    # Search for .json log files for the specified year and month
    log_files = sorted(
        [f for f in os.listdir(log_folder) 
        if f.endswith(".json") and f"{cfg.MODE}{cfg.TYPE}__{year}-{month}" in f],
        key=lambda x: os.path.getmtime(os.path.join(log_folder, x))
    )
    if not log_files:
        print(i18n.t('err_filenotfound',n=f'{year}-{month}'), flush=True)
        return

    # Load existing Excel file or create a new one
    if os.path.exists(workbook_path):
        workbook = load_workbook(workbook_path)
    else:
        workbook = Workbook()
        del workbook[workbook.active.title]

    # Open existing sheet or create a new one for the given year and month
    sheet_name = f"{year}-{month}"
    summary_sheet_name = i18n.t('log_sheet_sum_name')
    if sheet_name in workbook.sheetnames:
        sheet = workbook[sheet_name]
    else:
        sheet = workbook.create_sheet(title=sheet_name)

    # Get the first log file and check if it contains a valid JSON dictionary
    first_log_path = os.path.join(log_folder, log_files[0])
    with open(first_log_path, 'r', encoding='utf-8') as first_file:
        try:
            first_data = json.load(first_file)
            if not isinstance(first_data, dict):
                print(i18n.t('err_data',n=f'{log_files[0]}'), flush=True)
                return
        except json.JSONDecodeError:
            print(i18n.t('err_decode',n=f'{log_files[0]}'), flush=True)
            return

    # Define cell formatting styles
    if "time_style" in workbook.named_styles:
        time_style = "time_style"
    else:
        time_style = NamedStyle(name="time_style", number_format="[h]:mm:ss")
        workbook.add_named_style(time_style)

    if "integer_style" not in workbook.named_styles:
        integer_style = NamedStyle(name="integer_style", number_format="0")
        workbook.add_named_style(integer_style)
    else:
        integer_style = "integer_style"

    if "decimal_style" in workbook.named_styles:
        decimal_style = "decimal_style"
    else:
        decimal_style = NamedStyle(name="decimal_style", number_format="0.00")
        workbook.add_named_style(decimal_style)

    # Write headers from data if the sheet is empty
    if sheet.max_row == 0 or all(cell.value is None for cell in sheet[1]):
        for col, header in enumerate(first_data.keys(), start=1):
            sheet.cell(row=1, column=col, value=header)

    # Copy statistics from the first monthly sheet
    monthly_sheets = [name for name in workbook.sheetnames if name not in (summary_sheet_name, sheet_name)]
    if monthly_sheets:
        first_monthly = monthly_sheets[0]
        src_sheet = workbook[first_monthly]
        # Determine the range of rows to copy based on non-empty rows in columns T to AA
        max_stat_row = 1
        for row in range(1, src_sheet.max_row + 1):
            if any(src_sheet.cell(row=row, column=col).value is not None for col in range(20, 28)):
                max_stat_row = row
        # Copy values from range T1:AA[max_stat_row]
        for row in range(1, max_stat_row + 1):
            for col in range(20, 28):
                src_cell = src_sheet.cell(row=row, column=col)
                dest_cell = sheet.cell(row=row, column=col)
                dest_cell.value = src_cell.value

                if col in (22, 23):  # V, W - decimal
                    dest_cell.style = decimal_style
                elif col == 24:  # X - robot working time
                    dest_cell.style = time_style
                elif col in (25, 26, 27):  # Y, Z, AA - integer
                    dest_cell.style = integer_style

    start_row = find_first_empty_row(sheet)

    # Iterate through all log files and load data into the sheet
    for log_file in log_files:
        log_path = os.path.join(log_folder, log_file)
        with open(log_path, 'r', encoding='utf-8') as file:
            try:
                data = json.load(file)
            except json.JSONDecodeError:
                print(i18n.t('err_decode',n=f'{log_file}'), flush=True)
                continue

        # Check if data is a dictionary and save it to the sheet
        if isinstance(data, dict):
            for col, value in enumerate(data.values(), start=1):
                sheet.cell(row=start_row, column=col, value=convert_value(value))
            start_row += 1 
        else:
            print(i18n.t('err_format',n=f'{log_file}'), flush=True)

        os.remove(log_path) 
        print(i18n.t('delete',n=f'{log_file}'), flush=True)
    

    # Add summary formulas and headers to the monthly sheet
    sheet.cell(row=1, column=21, value=i18n.t('log_header_total'))

    sheet.cell(row=1, column=22, value=i18n.t('log_header_hours_saved'))
    sheet.cell(row=1, column=23, value=i18n.t('log_header_md_saved'))
    sheet.cell(row=1, column=24, value=i18n.t('log_header_robot_work_time'))

    sheet["V2"].style = decimal_style
    sheet["W2"].style = decimal_style        
    sheet["X2"].style = time_style
    
    sheet.cell(row=1, column=25, value='0')
    sheet.cell(row=1, column=26, value='3')
    sheet.cell(row=1, column=27, value='5')

    # =======================================================
    #           --- Handling the "Sum" sheet ---
    # =======================================================

    if summary_sheet_name in workbook.sheetnames:
        summary_sheet = workbook[summary_sheet_name]
    else:
        summary_sheet = workbook.create_sheet(title=summary_sheet_name)

    # Add column headers to the summary sheet
    if all(cell.value is None for cell in summary_sheet[1]):
        headers = [
            i18n.t('log_header_total'),
            i18n.t('log_header_hours_saved'),
            i18n.t('log_header_md_saved'),
            i18n.t('log_header_robot_work_time'),
            "0",
            "3",
            "5",
            i18n.t('log_header_status_ok_percent'),
        ]
        summary_sheet.cell(row=1, column=1, value=None)
        for col, name in enumerate(headers, start=2):
            summary_sheet.cell(row=1, column=col, value=name)
        summary_sheet.cell(row=2, column=1, value=i18n.t('log_sheet_month_sum'))

    columns_data = {
        2: f"='{sheet_name}'!U2",  # 'Sum'
        3: f"='{sheet_name}'!V2",  # Hours saved
        4: f"='{sheet_name}'!W2",  # MD saved
        5: f"='{sheet_name}'!X2",  # Robot working time
        6: f"='{sheet_name}'!Y2",  # 0
        7: f"='{sheet_name}'!Z2",  # 3
        8: f"='{sheet_name}'!AA2",  # 5
    }
    
    # Check if an entry with the same sheet name already exists in column A
    found_row = None
    for row in range(3, summary_sheet.max_row + 1):
        if summary_sheet.cell(row=row, column=1).value == sheet.title:
            found_row = row
            break
    if found_row:
        target_row = found_row
    else:
        target_row = find_first_empty_row(summary_sheet)

    # Insert or update data in the appropriate row
    for col, formula in columns_data.items():
        cell = summary_sheet.cell(row=target_row, column=col, value=formula)
        if col in (3, 4):
            cell.style = decimal_style
        elif col == 5:
            cell.style = time_style
    summary_sheet.cell(row=target_row, column=1, value=sheet.title)
    cell = summary_sheet.cell(row=target_row, column=9, value=f"=H{target_row}*100/SUM(F{target_row}:H{target_row})")
    cell.style = integer_style

    # Set summary formulas in the second row of the "Sum" sheet
    summary_sheet.cell(row=2, column=2, value=f"=SUM(B3:B{summary_sheet.max_row})")
    cell = summary_sheet.cell(row=2, column=3, value=f"=SUM(C3:C{summary_sheet.max_row})")
    cell.style = decimal_style
    cell = summary_sheet.cell(row=2, column=4, value=f"=SUM(D3:D{summary_sheet.max_row})")
    cell.style = decimal_style
    cell = summary_sheet.cell(row=2, column=5, value=f"=SUM(E3:E{summary_sheet.max_row})")
    cell.style = time_style
    summary_sheet.cell(row=2, column=6, value=f"=SUM(F3:F{summary_sheet.max_row})")
    summary_sheet.cell(row=2, column=7, value=f"=SUM(G3:G{summary_sheet.max_row})")
    summary_sheet.cell(row=2, column=8, value=f"=SUM(H3:H{summary_sheet.max_row})")
    cell = summary_sheet.cell(row=2, column=9, value="=H2*100/SUM(F2:H2)")
    cell.style = integer_style

    # =======================================================
    #           --- Sorting the "Sum" sheet ---
    # =======================================================

    # Sort rows in the "Sum" sheet from oldest to newest date
    data_rows = []
    for row in range(3, summary_sheet.max_row + 1):
        row_values = [summary_sheet.cell(row=row, column=col).value for col in range(1, 10)]
        if row_values[0]:
            data_rows.append(row_values)

    # Sort by date in sheet name (column 1), format YYYY-MM
    def parse_date(val):
        try:
            return datetime.strptime(val, "%Y-%m")
        except Exception:
            return datetime.min
    data_rows.sort(key=lambda r: parse_date(r[0]), reverse=False)

    # Remove old rows
    if summary_sheet.max_row >= 3:
        summary_sheet.delete_rows(3, summary_sheet.max_row - 2)

    # Insert sorted rows and set styles
    for idx, row_values in enumerate(data_rows, start=3):
        for col, value in enumerate(row_values, start=1):
            if col == 9:
                cell = summary_sheet.cell(row=idx, column=col, value=f"=H{idx}*100/SUM(F{idx}:H{idx})")
                cell.style = integer_style
            else:
                cell = summary_sheet.cell(row=idx, column=col, value=value)
                if col in (3, 4):
                    cell.style = decimal_style
                elif col == 5:
                    cell.style = time_style

    try:
        sort_sheets(workbook)
        # Ensure Excel will recalculate formulas when the file is opened
        try:
            workbook.calc_properties.fullCalcOnLoad = True
        except Exception:
            pass
        workbook.save(workbook_path)
        # Recalculate formulas using LibreOffice (Linux only)
        try:
            import shutil
            if shutil.which("libreoffice"):
                from utils.utils import libreoffice_recalc_xlsx
                libreoffice_recalc_xlsx(workbook_path)
            else:
                print("LibreOffice is not installed or not found in PATH. Skipping recalculation.", flush=True)
        except Exception as e:
            print(f"LibreOffice recalc failed: {e}", flush=True)
        print(i18n.t('save',n=f'sheet {sheet_name} file {workbook_path} and in sheet {summary_sheet_name}'), flush=True)
    except PermissionError:
        print("The file containing aggregated logs is open! Close it and run the script again.", flush=True)