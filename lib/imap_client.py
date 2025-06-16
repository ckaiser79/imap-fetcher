import imaplib
import email
from email.message import Message

class IMAPClient:
    def __init__(self, config):
        self.config = config
        self.conn = imaplib.IMAP4_SSL(
            self.config.get("imap_server"),
            self.config.get_int("imap_port")
        )

    def login(self):
        print(f"Login to {self.config.get('imap_server')}...")
        
        self.conn.login(
            self.config.get("username"),
            self.config.get("password")
        )
        if self.config.get_bool("verbose"):
            print("Connected.")

    def disconnect(self):
        if self.conn:
            self.conn.logout()
            if self.config.get_bool("verbose"):
                print("Disconnected.")

    def list_emails(self):
        self.conn.select(self.config.get("inbox_folder"))
        _, data = self.conn.search(None, 'ALL')
        for num in data[0].split():
            _, msg_data = self.conn.fetch(num, '(BODY.PEEK[HEADER.FIELDS (SUBJECT FROM DATE)])')
            print(f"\nID: {num.decode()}\n{msg_data[0][1].decode().strip()}")

    def fetch_email(self, mail_id):
        self.conn.select(self.config.get("inbox_folder"))
        _, data = self.conn.fetch(str(mail_id), '(RFC822)')
        return email.message_from_bytes(data[0][1])

    def get_all_mail_ids(self):
        self.conn.select(self.config.get("inbox_folder"))
        _, data = self.conn.search(None, 'ALL')
        return data[0].split()

    def move_to_archive(self, mail_id):
        archive = self.config.get("archive_folder")
        self.conn.select(self.config.get("inbox_folder"))
        self.conn.copy(str(mail_id), archive)
        self.conn.store(str(mail_id), '+FLAGS', '\\Deleted')
        self.conn.expunge()
        if self.config.get_bool("verbose"):
          print(f"Mail {mail_id} archived.")
