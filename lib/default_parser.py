from email.message import Message
from parser_strategy import EmailParserStrategy

class DefaultPlainTextParser(EmailParserStrategy):
    def parse(self, msg: Message) -> None:
        print(f"Subject: {msg.get('Subject')}")
        print(f"From: {msg.get('From')}")
        print(f"Date: {msg.get('Date')}")
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                print("\nBody:")
                print(part.get_payload(decode=True).decode(errors='replace'))
                break
