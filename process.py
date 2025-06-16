import os
import email
from email.policy import default


class MailProcessor:
    def __init__(self, imap_client, parser_strategy, config):
        self.imap_client = imap_client
        self.parser_strategy = parser_strategy
        self.config = config
        self.error_dir = self.config.get("error_dir") or "failed_emails"
        os.makedirs(self.error_dir, exist_ok=True)

    def process_all(self):
        print("Connecting and processing inbox...")
        self.imap_client.connect()

        email_ids = self.imap_client.get_all_mail_ids()
        print(f"Found {len(email_ids)} emails to process.\n")

        for mail_id in email_ids:
            try:
                print(f"Processing mail ID: {mail_id.decode()}")

                message = self.imap_client.fetch_email(mail_id)

                self.parser_strategy.parse(message)

                self.imap_client.move_to_archive(mail_id)
                print("✓ Mail archived.\n")

            except Exception as e:
                print(f"✗ Failed to process mail ID {mail_id.decode()}: {e}")
                self._save_failed_email(mail_id.decode(), message)

        self.imap_client.disconnect()

    def _save_failed_email(self, mail_id, message):
        path = os.path.join(self.error_dir, f"email_{mail_id}.eml")
        try:
            with open(path, "wb") as f:
                f.write(message.as_bytes(policy=default))
            print(f"Saved failed email to {path}\n")
        except Exception as e:
            print(f"Failed to save email {mail_id}: {e}")
