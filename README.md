# About

Downloads emails from an IMAP mailbox for further processing and saves processed emails in the archive.

# Usage

```bash

# Emails auflisten
python3 -m main --list

# E-Mail ID 5 herunterladen
python3 -m main --download 5

# E-Mail ID 5 ins Archiv verschieben
python3 -m main --archive 5

# Konfiguration überschreiben
python3 -m main --list --username new@domain.com --password geheim123


# Download, tranform and archive emails
python3 -m main --process_all --parser_strategy vendor.my_parser.MyParser
```
