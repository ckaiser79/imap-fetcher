import configparser
import os

class Configuration:
    DEFAULTS = {
        "imap_server": "localhost",
        "imap_port": 993,
        "username": None,
        "password": None,
        "parser_strategy": "lib.default_parser.DefaultPlainTextParser",
        "inbox_folder": "INBOX",
        "archive_folder": "Archive",
        "error_dir": "failed_emails",
        "log_file": "imap-fetcher.log",

        "list": False,
        "process_all": False,
        "download": None,
    }

    def __init__(self, ini_path=None, env_prefix="", cli_args=None):
        self.config = configparser.ConfigParser()
        if ini_path:
            self.config.read(ini_path)

        self.env_prefix = env_prefix
        self.cli_args = cli_args or {}

    def exists(self, key) -> bool:
        value = self.get_optional(key)
        return value is not None

    def get_optional(self, key) -> str | None:
        # 1. CLI argument
        if key in self.cli_args and self.cli_args[key] is not None:
            return str(self.cli_args[key])

        # 2. Environment variable
        env_key = f"{self.env_prefix}{key}".upper()
        if env_key in os.environ:
            return os.environ[env_key]

        # 3. INI file
        if self.config.has_option('imap', key):
            return self.config.get('imap', key)

        # 4. Defaults
        if key in self.DEFAULTS:
            return self.DEFAULTS[key]
        
        return None
    
    def get(self, key) -> str:
        value = self.get_optional(key)
        if value is not None:
            return value
        raise KeyError(f"Configuration key '{key}' not found in any source.")
    
    def get_int(self, key) -> int:
        value = self.get(key)
        try:
            return int(value)
        except ValueError:
            raise ValueError(f"Invalid integer value for key '{key}': {value}")


    def get_bool(self, key) -> bool:
        value = self.get(key).lower()
        if value in ['true', '1', 'yes']:
            return True
        elif value in ['false', '0', 'no']:
            return False
        raise ValueError(f"Invalid boolean value for key '{key}': {value}")

    def dump(self):
        """Optional: print current config for debugging."""
        for key in self.DEFAULTS:
            print(f"{key} = {self.get(key)}")