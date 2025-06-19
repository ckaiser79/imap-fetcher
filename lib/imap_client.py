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

    def search_uid_by_message_id(self, message_id: str) -> str | None:
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
            message = "X-IMAP-Fetcher-Mail-ID: " + str(num) + "\n" + message.strip()
            result.append(message)
        return result

    def select_inbox(self):
        self.conn.select(self.config.get("inbox_folder"))
        logger.debug(f"Selected inbox folder: {self.config.get('inbox_folder')}")

    def fetch(self, mail_id: int) -> Message:
        
        _, data = self.conn.fetch(str(mail_id), '(RFC822)')

        message: Message = email.message_from_bytes(data[0][1])
        message.add_header("X-IMAP-Fetcher-Mail-ID", str(mail_id))

        if message.get('Message-ID'):
            message_id: str | None = message.get('Message-ID')
            if message_id:
                uid: str | None = self.search_uid_by_message_id(message_id)
                message.add_header("X-IMAP-Fetcher-UID", str(uid))

        return message
    
    def fetch_email_from_inbox(self, mail_id: int) -> Message:
        """Fetch an email by its ID returned by get_all_mail_ids."""
        self.conn.select(self.config.get("inbox_folder"))
        return self.fetch(mail_id)

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

    def list_directories(self) -> list[str]:
        """List all directories (folders) in the IMAP account."""
        result, data = self.conn.list()
        if result != 'OK':
            logger.error(f"Failed to list directories: {data}")
            return []
        
        directories = [line.decode().split(' "/" ')[-1] for line in data]
        logger.debug(f"Directories: {directories}")
        return directories