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

    def search_uid(self, message_id: str) -> str | None:
        """message_id is the Message-ID header value"""
        logger.debug(f"Searching UID for message with ID: {message_id}")

        result, data = self.conn.uid('search', None, f'(HEADER Message-ID "{message_id}")')
        if result != 'OK' or not data[0]:
            logger.error(f"Message with ID {message_id} not found: {result}")
            return None
        
        # first uid
        return data[0].split()[0].decode()

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

    def list_emails(self) -> list[Message]:
        id_list = self.get_all_mail_ids()
        result = list()
        for num in id_list:
            _, msg_data = self.conn.fetch(str(num), '(BODY.PEEK[HEADER.FIELDS (MESSAGE-ID SUBJECT FROM DATE)])')
            message = msg_data[0][1].decode()
            logger.debug(f"{num}: {message.strip()}")
            result.append(message)
        return result

    def select_inbox(self):
        self.conn.select(self.config.get("inbox_folder"))
        logger.debug(f"Selected inbox folder: {self.config.get('inbox_folder')}")

    def _fetch(self, mail_id: int) -> Message:
        _, data = self.conn.fetch(str(mail_id), '(RFC822)')
        return email.message_from_bytes(data[0][1])
    
    def fetch_email(self, mail_id: int) -> Message:
        """Fetch an email by its ID returned by get_all_mail_ids."""
        self.conn.select(self.config.get("inbox_folder"))
        return self._fetch(mail_id)

    def get_all_mail_ids(self) -> list[int]:

        self.conn.select(self.config.get("inbox_folder"))
        _, data = self.conn.search(None, 'ALL')

        str_ids = data[0].split()
        result = list(map(int, str_ids))

        return result

    def move_to_archive(self, uid: str):
        archive = self.config.get("archive_folder")
        
        self.conn.uid("COPY", uid, archive)
        self.conn.uid('STORE', uid, '+FLAGS', '\\Deleted')
        self.conn.expunge()
        
        logger.debug(f"Mail {uid} archived to '{archive}'.")
