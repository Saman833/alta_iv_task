import os
import base64
import time
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from services.message_service import MessageService
from config import config 
from google.auth.transport.requests import Request

class EmailPoller:
    def __init__(self, message_service : MessageService): 
        self.credentials_path = config.config_json["email_poller_credentials_path"]
        self.token_path = config.config_json["email_poller_token_path"]
        self.service = None
        self.scopes = [config.config_json["email_poller_scope"]]
        self.is_running = False
        self.message_service = message_service
        self.sleep_time = config.config_json["email_poller_sleep_time"]

    def authenticate_gmail(self):
        creds = None
        # If token.json exists, load credentials from it
        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(self.token_path, self.scopes)
        # If no valid credentials, go through the OAuth flow
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.credentials_path, self.scopes)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(self.token_path, 'w') as token:
                token.write(creds.to_json())
        return creds

    def fetch_and_mark_unread_emails_batch(self):
        """Alternative method using batch operations for better performance."""
        # Get unread message IDs
        response = self.service.users().messages().list(
            userId='me',
            labelIds=['UNREAD'],
            maxResults=5
        ).execute()

        messages = response.get('messages', [])

        if not messages:
            print("No new unread emails.")
            return

        print(f"Found {len(messages)} unread emails. Processing in batch...")

        message_ids = [msg['id'] for msg in messages]
        
        batch = self.service.new_batch_http_request()
        
        for msg_id in message_ids:
            batch.add(
                self.service.users().messages().get(
                    userId='me',
                    id=msg_id,
                    format='metadata',
                    metadataHeaders=['Subject', 'From']
                )
            )
        
        batch.execute()
 
        for msg in messages:
            try:
                msg_id = msg['id']
                msg_data = self.service.users().messages().get(
                    userId='me',
                    id=msg_id,
                    format='metadata',
                    metadataHeaders=['Subject', 'From']
                ).execute()
                
                if self.message_service:
                    self.message_service.process_message(source='email', raw_data=msg_data)
                else:
                    print(f"Message service not available. Raw data: {msg_data}")

            except Exception as e:
                print(f"Error processing message {msg_id}: {e}")
                continue
        
        if message_ids:
            try:
                self.service.users().messages().batchModify(
                    userId='me',
                    body={
                        'ids': message_ids,
                        'removeLabelIds': ['UNREAD']
                    }
                ).execute()
                print(f"✓ Marked {len(message_ids)} emails as read in batch")
            except Exception as e:
                print(f"Error marking emails as read: {e}")

    def start_polling(self):
        self.is_running = True
        creds = self.authenticate_gmail()
        self.service = build('gmail', 'v1', credentials=creds)

        while self.is_running:
            self.fetch_and_mark_unread_emails_batch()
            time.sleep(self.sleep_time)


if __name__ == '__main__':
    poller = EmailPoller(message_service=MessageService())
    poller.start_polling()
