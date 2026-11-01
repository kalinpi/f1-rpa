import os
from dotenv import load_dotenv
import i18n
from cryptography.fernet import Fernet
from robocorp import log

class Config:
    """Robot/service configuration loaded from environment variables."""
    def __init__(self):
        self.VERSION = "2.2.2"
        self.FRAMEWORK = "ROBOCORP PYTHON"
        self.fernet_key_path = "/rpa/.rpa.key"

        self.load_env()
        self.set_translation()

    def load_env(self):
        load_dotenv()
        self.SECURED = int(os.getenv("SECURED", "0"))
        load_dotenv(dotenv_path=".envs")
        
        # LibreOffice profile base
        self.LIBREOFFICE_PROFILE_BASE = os.getenv('LIBREOFFICE_PROFILE_BASE',str("/t"+"mp/libreoffice_profiles"))
        
        # Main variables
        self.MODE = os.getenv('MODE', "")
        self.TYPE = os.getenv('TYPE', "")
        self.LANGUAGE = os.getenv('LANGUAGE', "")
        self.XAPIKEY = self._read_env_var('XAPIKEY')
        self.JSON_LOG_PATH = ""
        self.CFN = ""
        self.WAIT = int(os.getenv('WAIT_TO_RESPONSE', "0"))
        self.DRYRUN = int(os.getenv('DRYRUN'))
        self.NOTFOUND = "NOTFOUND"
        self.URL = ""

        # Files
        self.SHARED = os.getenv('SHARED', "")
        self.SDIR = os.getenv('SDIR', "")
        self.UNITS = os.getenv('UNITS')

        # Dolog
        self.MONTH = os.getenv("MONTH")
        self.YEAR = os.getenv("YEAR")

        # Browser
        self.USER = self._read_env_var('USER_LOGIN')
        self.PASSWORD = self._read_env_var('USER_PASS')
        self.URL_PROD = os.getenv('URL_PROD', "")
        self.URL_TEST = os.getenv('URL_TEST', "")

        # Colors
        self.RED = os.getenv('RED', "")
        self.GREEN = os.getenv('GREEN', "")
        self.GRAY = os.getenv('GRAY', "")
        self.WHITE = os.getenv('WHITE', "")

        # RDP
        self.RDP_SERVER_IP = self._read_env_var('RDP_SERVER_IP')
        self.RDP_LOGIN = self._read_env_var('RDP_LOGIN')
        self.RDP_PASS = self._read_env_var('RDP_PASS')
        self.RDP_RESOLUTION = os.getenv('RDP_RESOLUTION', "")
        self.APP_EXE_PATH = os.getenv('APP_EXE_PATH', "")
        self.RDP_DRIVE = os.getenv('RDP_DRIVE', "")
        self.RDP_CERT_FINGERPRINT = os.getenv("RDP_CERT_FINGERPRINT", "")

        # Printing
        self.LPD_PORT = int(os.getenv('LPD_PORT', 515))
        self.PRINT_SERVER_IP = os.getenv('PRINT_SERVER_IP', "")
        self.QUEUE_NAME = os.getenv('QUEUE_NAME', "")
        self.LOG_PATH = os.getenv('LOG_PATH', "")

        # SMTP
        self.SMTP_HOST = self._read_env_var('SMTP_HOST')
        self.SMTP_PORT = int(os.getenv('SMTP_PORT', 25))
        self.SMTP_USER = self._read_env_var('SMTP_USER')
        self.SMTP_PASSWORD = self._read_env_var('SMTP_PASSWORD')
        self.SMTP_SENDER = self._read_env_var('SMTP_SENDER')

        # O365 Mail API
        self.O365_CLIENT_ID = self._read_env_var('O365_CLIENT_ID')
        self.O365_TENANT_ID = self._read_env_var('O365_TENANT_ID')
        self.O365_SCOPES = os.getenv('O365_SCOPES', "")
        self.O365_MAILBOX = os.getenv('O365_MAILBOX', "")
        self.O365_DESTINATION_FOLDER = os.getenv('O365_DESTINATION_FOLDER', "")
        
    def set_translation(self):
        i18n.set('filename_format', '{locale}.{format}')
        i18n.set('locale', self.LANGUAGE)
        i18n.set('file_format', 'yaml')
        i18n.load_path.append('./translations')

    def _read_env_var(self, var_name):
        """Decrypt variable only if SECURED=1, otherwise return value from env"""
        with log.suppress():
            val = os.getenv(var_name, "")
            if self.SECURED and val:
                if not os.path.exists(self.fernet_key_path):
                    raise FileNotFoundError("SECURED=1 but key file not found")
                with open(self.fernet_key_path, "rb") as f:
                    key = f.read().strip()
                fernet = Fernet(key)
                try:
                    return fernet.decrypt(val.encode()).decode()
                except Exception:
                    return ""
            return val

config = Config()
