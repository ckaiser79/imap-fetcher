import logging
from lib.config import Configuration

logger = logging.getLogger("imap-fetcher")

def setup_logging(config: Configuration) -> None:
    if config.get_bool("verbose"):
       log_level = logging.DEBUG
    else:
        log_level = logging.INFO
    logging.basicConfig(filename=config.get('log_file'), filemode='w', level=log_level, encoding='utf-8')
