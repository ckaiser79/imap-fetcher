import os
from email.policy import default
from lib.custom_exceptions import UnparseableEmailException
from lib.setup_logger import logger


class MailProcessor:
    def __init__(self, imap_client, parser_strategy, config):
        self.imap_client = imap_client
        self.parser_strategy = parser_strategy
        self.config = config

        self.error_dir = self.config.get("error_dir")
        os.makedirs(self.error_dir, exist_ok=True)

    def process_all(self) -> None:

        email_ids: list[int] = self.imap_client.get_all_mail_ids() 
        logger.info(f"Found {len(email_ids)} emails to process.\n")
        if len(email_ids) == 0:
            return 0
        
        self.imap_client.select_inbox()
        
        failures: int = 0
        archived : int = 0

        for mail_id in email_ids:
            message = None
            try:
                
                message = self.imap_client._fetch(mail_id)

                archive_ready: bool = self.parse_message(message, mail_id)
                
                if archive_ready:
                    self.imap_client.move_to_archive(mail_id)
                    logger.debug("✓ Mail archived ID {mail_id}.\n")
                    archived  += 1

            except Exception as e:
                logger.warning(f"✗ Failed to process mail ID {mail_id}: {e}")
                self._save_failed_email(mail_id, message)
                failures += 1

        logger.info(f"\nProcessed {len(email_ids)} emails with {failures} failures.")
        if failures > 0:
            raise Exception(f"\n{failures} emails failed to process. Check {self.error_dir} for details or rerun.")


    def parse_message(self, message, mail_id) -> bool:
        try:
            self.parser_strategy.parse(message)
            archive_ready = True
        except UnparseableEmailException as e:
            archive_ready = False
            logger.warning(f"✗ Failed to parse email ID {mail_id}: {e.__class__.__name__} - {e}")

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
