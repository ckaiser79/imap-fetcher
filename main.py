import argparse
from config import Configuration
from imap_client import IMAPClient
from process import MailProcessor
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
    parser.add_argument('--help', action='store_true', help="Print usage and exit")
    parser.add_argument('--verbose', action='store_true', help="Enable verbosity mode")

    args = parser.parse_args()

    if args.help:
       parser.print_help()
       exit(2)

    config = Configuration(
        ini_path=args.config,
        env_prefix="IMAP_FETCH_",
        cli_args=vars(args)
    )

    try:
        parser_strategy = load_parser(config.get("parser_strategy"))
    except Exception as e:
        print(f"Error loading parser strategy: {e}")
        return

    client = IMAPClient(config)
    try:
        client.login()

        if config.get_bool("process_all"):
            processor = MailProcessor(client, parser, config)
            processor.process_all()
            return
        else:
    
            if config.get_bool("list"):
                client.list_emails()
            elif args.download:
                message = client.fetch_email(config.get_int("download"))
                print(f"Downloaded email:\n{message.as_string()}")
            elif args.archive:
                client.move_to_archive(config.get_int("archive"))
    finally:
        client.disconnect()

if __name__ == "__main__":
    main()
