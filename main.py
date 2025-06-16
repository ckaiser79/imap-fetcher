#!env python3
# -*- coding: utf-8 -*-
import argparse
from lib.config import Configuration
from lib.imap_client import IMAPClient
from lib.process import MailProcessor
from importlib import import_module


def load_parser(strategy_path: str):
    module_name, class_name = strategy_path.rsplit(".", 1)
    module = import_module(module_name)
    return getattr(module, class_name)()


def main():
    parser = argparse.ArgumentParser(description="IMAP CLI Client")
    parser.add_argument('--config', default='config.ini', help="INI config file")
    parser.add_argument('--imap_server')
    parser.add_argument('--imap_port', type=int)
    parser.add_argument('--username')
    parser.add_argument('--password')
    parser.add_argument('--inbox_folder')
    parser.add_argument('--archive_folder')
    parser.add_argument('--parser_strategy', default='default_parser.DefaultPlainTextParser')

    parser.add_argument('--list', action='store_true')
    parser.add_argument('--process_all', action='store_true',  help="Process all emails in the inbox and delgate to strategy parser")
    parser.add_argument('--download', type=int, help="Download email by ID")
    parser.add_argument('--archive')
    parser.add_argument('--clear_archive', action='store_true')
    #parser.add_argument('--help', action='store_true', help="Print usage and exit")
    parser.add_argument('--verbose', action='store_true', help="Enable verbosity mode")

    args = parser.parse_args()

    #if args.help:
    #   parser.print_help()
    #   exit(2)

    config = Configuration(
        ini_path=args.config,
        env_prefix="IMAP_FETCH_",
        cli_args=vars(args)
    )

    parser_strategy = None
    if config.get_bool("process_all") or config.exists("download"):    
        parser_strategy = load_parser(config.get("parser_strategy"))
        
    client = IMAPClient(config)
    try:
        client.login()

        if config.get_bool("process_all"):
            processor = MailProcessor(client, parser_strategy, config)
            processor.process_all()
            return
        else:
    
            if config.get_bool("list"):
                client.list_emails()
            elif args.download:
                message = client.fetch_email(config.get_int("download"))
                if message is None:
                    print(f"Email with ID {args.download} not found.")
                    return
                if config.get_bool("verbose"):
                    print(f"Downloaded email:\n{message.as_string()}")

                if parser_strategy != None:
                  parser_strategy.parse(message)
            elif args.archive:
                client.move_to_archive(config.get_int("archive"))
    finally:
        client.disconnect()

if __name__ == "__main__":
    main()
