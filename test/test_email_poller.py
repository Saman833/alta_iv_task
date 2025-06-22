import unittest
from unittest.mock import Mock, patch, MagicMock, mock_open
import json
import os
from sources.email.email_poller import EmailPoller

class TestEmailPoller(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Mock config
        self.mock_config = Mock()
        self.mock_config.config_json = {
            "email_poller_credentials_path": "test_credentials.json",
            "email_poller_token_path": "test_token.json",
            "email_poller_scope": "https://www.googleapis.com/auth/gmail.readonly",
            "email_poller_sleep_time": 60
        }
        
        # Mock message service
        self.mock_message_service = Mock()
        
        # Sample Gmail API response
        self.sample_gmail_response = {
            "id": "test_message_id",
            "threadId": "test_thread_id",
            "labelIds": ["UNREAD", "INBOX"],
            "snippet": "This is a test email snippet",
            "payload": {
                "headers": [
                    {"name": "Subject", "value": "Test Subject"},
                    {"name": "From", "value": "test@example.com"},
                    {"name": "Date", "value": "Mon, 1 Jan 2024 12:00:00 +0000"}
                ]
            }
        }

    @patch('sources.email.email_poller.config')
    @patch('sources.email.email_poller.InstalledAppFlow')
    @patch('sources.email.email_poller.build')
    def test_authenticate_gmail_success(self, mock_build, mock_flow, mock_config):
        """Test successful Gmail authentication."""
        # Setup mocks
        mock_config.config_json = self.mock_config.config_json
        
        mock_creds = Mock()
        mock_creds.to_json.return_value = '{"access_token": "test_token"}'
        
        mock_flow_instance = Mock()
        mock_flow_instance.run_local_server.return_value = mock_creds
        mock_flow.from_client_secrets_file.return_value = mock_flow_instance
        
        # Test
        with patch('builtins.open', mock_open()) as mock_file:
            poller = EmailPoller(self.mock_message_service)
            result = poller.authenticate_gmail()
            
            # Assertions
            self.assertEqual(result, mock_creds)
            mock_flow.from_client_secrets_file.assert_called_once_with(
                "test_credentials.json", 
                ["https://www.googleapis.com/auth/gmail.readonly"]
            )
            mock_flow_instance.run_local_server.assert_called_once_with(port=0)
            mock_file.assert_called_once_with("test_token.json", 'w')

    @patch('sources.email.email_poller.config')
    @patch('sources.email.email_poller.InstalledAppFlow')
    def test_authenticate_gmail_failure(self, mock_flow, mock_config):
        """Test Gmail authentication failure."""
        # Setup mocks
        mock_config.config_json = self.mock_config.config_json
        
        mock_flow_instance = Mock()
        mock_flow_instance.run_local_server.side_effect = Exception("Authentication failed")
        mock_flow.from_client_secrets_file.return_value = mock_flow_instance
        
        # Test
        poller = EmailPoller(self.mock_message_service)
        
        with self.assertRaises(Exception):
            poller.authenticate_gmail()

    @patch('sources.email.email_poller.config')
    @patch('sources.email.email_poller.build')
    def test_fetch_and_mark_unread_emails_batch_no_messages(self, mock_build, mock_config):
        """Test when no unread emails are found."""
        # Setup mocks
        mock_config.config_json = self.mock_config.config_json
        
        mock_service = Mock()
        mock_messages_list = Mock()
        mock_messages_list.execute.return_value = {"messages": []}
        mock_service.users.return_value.messages.return_value.list.return_value = mock_messages_list
        mock_build.return_value = mock_service
        
        # Test
        poller = EmailPoller(self.mock_message_service)
        poller.service = mock_service
        
        # Capture print output
        with patch('builtins.print') as mock_print:
            poller.fetch_and_mark_unread_emails_batch()
            mock_print.assert_called_with("No new unread emails.")

    @patch('sources.email.email_poller.config')
    @patch('sources.email.email_poller.build')
    def test_fetch_and_mark_unread_emails_batch_with_messages(self, mock_build, mock_config):
        """Test processing unread emails with message service."""
        # Setup mocks
        mock_config.config_json = self.mock_config.config_json
        
        mock_service = Mock()
        
        # Mock list response
        mock_list_response = Mock()
        mock_list_response.execute.return_value = {
            "messages": [{"id": "msg1"}, {"id": "msg2"}]
        }
        
        # Mock get response
        mock_get_response = Mock()
        mock_get_response.execute.return_value = self.sample_gmail_response
        
        # Mock batch modify response
        mock_batch_modify = Mock()
        mock_batch_modify.execute.return_value = {}
        
        # Setup service chain
        mock_service.users.return_value.messages.return_value.list.return_value = mock_list_response
        mock_service.users.return_value.messages.return_value.get.return_value = mock_get_response
        mock_service.users.return_value.messages.return_value.batchModify.return_value = mock_batch_modify
        mock_service.new_batch_http_request.return_value = Mock()
        
        mock_build.return_value = mock_service
        
        # Test
        poller = EmailPoller(self.mock_message_service)
        poller.service = mock_service
        
        poller.fetch_and_mark_unread_emails_batch()
        
        # Verify message service was called
        self.assertEqual(self.mock_message_service.process_message.call_count, 2)

    @patch('sources.email.email_poller.config')
    @patch('sources.email.email_poller.build')
    def test_fetch_and_mark_unread_emails_batch_no_message_service(self, mock_build, mock_config):
        """Test processing emails without message service."""
        # Setup mocks
        mock_config.config_json = self.mock_config.config_json
        
        mock_service = Mock()
        mock_list_response = Mock()
        mock_list_response.execute.return_value = {
            "messages": [{"id": "msg1"}]
        }
        mock_get_response = Mock()
        mock_get_response.execute.return_value = self.sample_gmail_response
        
        mock_service.users.return_value.messages.return_value.list.return_value = mock_list_response
        mock_service.users.return_value.messages.return_value.get.return_value = mock_get_response
        mock_service.new_batch_http_request.return_value = Mock()
        
        mock_build.return_value = mock_service
        
        # Test without message service
        poller = EmailPoller(Mock())
        poller.service = mock_service
        poller.fetch_and_mark_unread_emails_batch()

    @patch('sources.email.email_poller.config')
    @patch('sources.email.email_poller.time.sleep')
    @patch('sources.email.email_poller.InstalledAppFlow')
    @patch('sources.email.email_poller.build')
    def test_start_polling(self, mock_build, mock_flow, mock_sleep, mock_config):
        """Test the polling loop."""
        # Setup mocks
        mock_config.config_json = self.mock_config.config_json
        
        mock_creds = Mock()
        mock_flow_instance = Mock()
        mock_flow_instance.run_local_server.return_value = mock_creds
        mock_flow.from_client_secrets_file.return_value = mock_flow_instance
        
        mock_service = Mock()
        mock_build.return_value = mock_service
        
        # Test
        with patch('builtins.open', mock_open()):
            poller = EmailPoller(self.mock_message_service)
            
            # Set is_running to False after first iteration to stop the loop
            def stop_after_first_call():
                poller.is_running = False
            
            with patch.object(poller, 'fetch_and_mark_unread_emails_batch', side_effect=stop_after_first_call):
                poller.start_polling()
                
                # Verify authentication was called
                mock_flow.from_client_secrets_file.assert_called_once()
                mock_build.assert_called_once_with('gmail', 'v1', credentials=mock_creds)

    def test_email_poller_initialization(self):
        """Test EmailPoller initialization with different parameters."""
        # Test with message service
        poller_with_service = EmailPoller(self.mock_message_service)
        self.assertEqual(poller_with_service.message_service, self.mock_message_service)
        self.assertFalse(poller_with_service.is_running)
        
        # Test without message service
        poller_without_service = EmailPoller(Mock())
        self.assertIsInstance(poller_without_service, EmailPoller)

if __name__ == '__main__':
    unittest.main() 