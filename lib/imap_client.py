import imaplib
import email
from email.message import Message
from lib.setup_logger import logger

class IMAPClient:
    def __init__(self, config):
        self.config = config
        self.conn = imaplib.IMAP4_SSL(
            self.config.get("imap_server"),
            self.config.get_int("imap_port")
        )

    def login(self):
        logger.debug(f"Login to {self.config.get('imap_server')}...")
        
        self.conn.login(
            self.config.get("username"),
            self.config.get("password")
        )
        
        logger.debug("Connected.")

    def disconnect(self):
        if self.conn:
            self.conn.logout()
            logger.debug("Disconnected.")

    def list_emails(self):
        id_list = self.get_all_mail_ids()

        for num in id_list:
            _, msg_data = self.conn.fetch(str(num), '(BODY.PEEK[HEADER.FIELDS (SUBJECT FROM DATE)])')
            message = msg_data[0][1].decode()
            logger.debug(f"\nID: {num}\n{message.strip()}")

    def select_inbox(self):
        self.conn.select(self.config.get("inbox_folder"))
        logger.debug(f"Selected inbox folder: {self.config.get('inbox_folder')}")

    def _fetch(self, mail_id: int) -> Message:
        _, data = self.conn.fetch(str(mail_id), '(RFC822)')
        return email.message_from_bytes(data[0][1])
    
    def fetch_email(self, mail_id: int) -> Message:
        self.conn.select(self.config.get("inbox_folder"))
        return self._fetch(mail_id)

    def get_all_mail_ids(self) -> list[int]:

        self.conn.select(self.config.get("inbox_folder"))
        _, data = self.conn.search(None, 'ALL')

        str_ids = data[0].split()
        result = list(map(int, str_ids))

        return result

    def move_to_archive(self, mail_id):
        archive = self.config.get("archive_folder")
        self.conn.select(self.config.get("inbox_folder"))
        self.conn.copy(str(mail_id), archive)
        self.conn.store(str(mail_id), '+FLAGS', '\\Deleted')
        self.conn.expunge()
        
        logger.debug(f"Mail {mail_id} archived.")
