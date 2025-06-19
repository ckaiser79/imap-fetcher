from email.message import Message
from lib.parser_strategy import EmailParserStrategy
from lib.config import Configuration

class DefaultPlainTextParser(EmailParserStrategy):

    def __init__(self, config: Configuration):
        self.config = config

    def parse(self, msg: Message) -> None:
        
        for key in msg.keys():
            if key.lower().startswith("x-imap-fetcher-"):
                print(f"{key}: {msg.get(key)}")

        print(f"Subject: {msg.get('Subject')}")
        print(f"From: {msg.get('From')}")
        print(f"Date: {msg.get('Date')}")
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                print("\nBody:")
                print(part.get_payload(decode=True).decode(errors='replace'))
                break
