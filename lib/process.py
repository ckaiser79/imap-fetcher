import os
from email.policy import default
from email.message import Message
from lib.custom_exceptions import UnparseableEmailException
from lib.setup_logger import logger

from lib.imap_client import IMAPClient
from lib.parser_strategy import EmailParserStrategy
from lib.config import Configuration


class MailProcessor:
    def __init__(self, parser_strategy: EmailParserStrategy, config: Configuration):
        
        self.parser_strategy = parser_strategy
        self.config = config

        self.retry_count: int = 0
        self.max_retries: int = 5
        
        self.error_dir = self.config.get("error_dir")
        os.makedirs(self.error_dir, exist_ok=True)

    def fetch_emails(self, imap_client: IMAPClient) -> list[Message]:
        
        email_ids: list[int] = imap_client.get_all_mail_ids() 
        logger.info(f"Found {len(email_ids)} emails to process.\n")

        result: list[Message] = list()

        if len(email_ids) == 0:
            return result
        
        imap_client.select_inbox()
        for mail_id in email_ids:
            message = imap_client.fetch(mail_id)
            logger.debug(f"Fetched email ID {mail_id} with Message-ID: {message.get('Message-ID')}")
            result.append(message)

        return result

    def process_all(self) -> None:

        if self.retry_count > self.max_retries:   
            logger.error("Too many retries, giving up.")
            return

        try:
            self._process_all()
        except Exception as e:
            logger.warning(f"Error processing emails: {e.__class__} {e}")
            self.retry_count += 1
            logger.info(f"Retrying... ({self.retry_count})")
            self.process_all()

    def _process_all(self) -> None:
     
        imap_client = IMAPClient(self.config)
        imap_client.login()

        try:
            inbox_messages = self.fetch_emails(imap_client)
            logger.debug(f"Fetched {len(inbox_messages)} emails from inbox.")

            for message in inbox_messages:
                message_id_header = message['Message-ID']
                subject = message['Subject']

                logger.info(f"Processing email ID {message_id_header}, '{subject}'")

                archive_ready: bool = self.parse_message(message)
                
                if archive_ready:

                    message_uid = imap_client.search_uid_by_message_id(message_id_header)
                    if message_uid is None:
                        logger.error(f"Message UID not found for ID {message_id_header}, archiving skipped")
                    else:
                        imap_client.move_to_archive(message_uid)
                        logger.debug(f"Mail archived ID {message_id_header}.")    
        finally:
            imap_client.disconnect()   
        

    def parse_message(self, message) -> bool:
        try:
            self.parser_strategy.parse(message)
            archive_ready = True
        except UnparseableEmailException as e:
            archive_ready = False
            logger.warning(f"Failed to parse email: {e.__class__.__name__} - {e}")

        return archive_ready

    def _save_failed_email(self, mail_id, message):

        if not message:
            logger.warning(f"No message to save for mail ID {mail_id}.")
            return
        
        logger.info(f"Saving failed email {mail_id} to {self.error_dir}...")
        path = os.path.join(self.error_dir, f"email_{mail_id}.eml")
        try:
            with open(path, "wb") as f:
                f.write(message.as_bytes(policy=default))
        except Exception as e:
            logger.error(f"Failed to save email {mail_id}: {e}")
