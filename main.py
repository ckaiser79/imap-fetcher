#!env python3
# -*- coding: utf-8 -*-
import argparse
from lib.config import Configuration
from lib.imap_client import IMAPClient
from lib.process import MailProcessor
from importlib import import_module
from lib.setup_logger import setup_logging
from lib.parser_strategy import EmailParserStrategy
from lib.default_parser import DefaultPlainTextParser

def load_parser(config: Configuration) -> EmailParserStrategy:
    strategy_path: str = config.get("parser_strategy")
    module_name, class_name = strategy_path.rsplit(".", 1)
    module = import_module(module_name)
    return getattr(module, class_name)(config)

def main():
    parser = argparse.ArgumentParser(description="IMAP CLI Client")
    parser.add_argument('--config', default='config.ini', help="INI config file")
    parser.add_argument('--imap-server')
    parser.add_argument('--imap-port', type=int)
    parser.add_argument('--username')
    parser.add_argument('--password')
    parser.add_argument('--inbox-folder')
    parser.add_argument('--archive-folder')
    parser.add_argument('--parser-strategy')
    parser.add_argument('--error-dir', help="Directory to save failed emails")

    parser.add_argument('--list', action='store_true')
    parser.add_argument('--list-directories', action='store_true')
    
    parser.add_argument('--process-all', action='store_true',  help="Process all emails in the inbox and delgate to strategy parser")
    parser.add_argument('--download', help="Download email by is mail id (integer) and parse it with strategy parser")
    parser.add_argument('--archive', help="Move email with field Message-ID to archive folder")
    parser.add_argument('--verbose', action='store_true', help="Enable verbosity mode")

    parser.add_argument('--log-file')

    args = parser.parse_args()

    config = Configuration(
        ini_path=args.config,
        env_prefix="IMAP_FETCH_",
        cli_args=vars(args)
    )

    logger = setup_logging(config)

    parser_strategy: EmailParserStrategy = DefaultPlainTextParser(config)
    if config.get_bool("process_all") or config.exists("download"):    
        parser_strategy = load_parser(config)
        
    result: int = 0

    if config.get_bool("process_all"):
        processor = MailProcessor(parser_strategy, config)
        try:
            processor.process_all()
        except Exception as e:
            logger.error(f"Error processing emails: {e}")
            print(f"Error processing emails: {e}")
            result = 2
    else:
        client = IMAPClient(config)
        try:
            client.login()
    
            if config.get_bool("list"):
                messages = client.list_emails()
                for message in messages:
                    print(message)
            elif config.get_bool("list_directories"):
                directories = client.list_directories()
                for directory in directories:
                    print(directory)
            elif config.exists("download"):
                download_mail_id: int = config.get_int("download")
                message = client.fetch_email_from_inbox(download_mail_id)
                if message is None:
                    print(f"Email with ID {download_mail_id} not found in {config.get("inbox_folder")}.")
                    return
                
                logger.debug(f"{message.as_string()}")
                parser_strategy.parse(message)

            elif config.exists("archive"):
                download_mail_id: int = config.get_int("archive")
                message = client.fetch_email_from_inbox(download_mail_id)

                uid = message.get("X-IMAP-Fetcher-UID")
                if uid is None:
                    print(f"Email with Mail ID {download_mail_id} not found in {config.get('inbox_folder')}.")
                else:
                    client.move_to_archive(uid)
        finally:
            client.disconnect()

    exit(result)

if __name__ == "__main__":
    main()
