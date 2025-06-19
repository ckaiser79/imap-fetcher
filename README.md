# About

Downloads emails from an IMAP mailbox for further processing and saves processed emails in the archive.

# Usage

```bash

# List Emails in INBOX
python3 -m main --list

# List all fqn of the directories on the server
python3 -m main --list-directories

# Get details of a single email inkl. their internal IDs
python3 -m main --download 3 --parser-strategy lib.default_parser.DefaultPlainTextParser

# E-Mail ID 5 ins Archiv verschieben
python3 -m main --archive 1

# Overwrite configuration using command line
python3 -m main --list --username new@domain.com --password geheim123


# Download, tranform and archive emails using a custom parser
python3 -m main --process-all --parser-strategy vendor.my_parser.MyParser
```
