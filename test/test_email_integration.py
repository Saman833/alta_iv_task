import pytest
from unittest.mock import Mock, patch
from sources.email.email_poller import EmailPoller

class TestEmailIntegration:
    """Integration tests for EmailPoller with realistic data."""
    
    @pytest.fixture
    def sample_gmail_data(self):
        """Sample Gmail API response data."""
        return {
            "id": "18c1234567890abcdef",
            "threadId": "18c1234567890abcdef",
            "labelIds": ["UNREAD", "INBOX"],
            "snippet": "This is a test email about project updates...",
            "historyId": "12345",
            "internalDate": "1704067200000",
            "payload": {
                "partId": "",
                "mimeType": "text/plain",
                "filename": "",
                "headers": [
                    {
                        "name": "Delivered-To",
                        "value": "user@gmail.com"
                    },
                    {
                        "name": "Received",
                        "value": "by 2002:a05:6a00:1234:0:0:0:0 with SMTP id..."
                    },
                    {
                        "name": "Date",
                        "value": "Mon, 1 Jan 2024 12:00:00 +0000"
                    },
                    {
                        "name": "From",
                        "value": "John Doe <john.doe@company.com>"
                    },
                    {
                        "name": "To",
                        "value": "user@gmail.com"
                    },
                    {
                        "name": "Subject",
                        "value": "Project Update - Q1 2024"
                    },
                    {
                        "name": "Message-ID",
                        "value": "<1234567890.abcdef@company.com>"
                    }
                ],
                "body": {
                    "data": "VGhpcyBpcyBhIHRlc3QgZW1haWwgYm9keQ==",
                    "size": 20
                }
            },
            "sizeEstimate": 1234
        }
    
    @pytest.fixture
    def mock_message_service(self):
        """Mock message service for testing."""
        service = Mock()
        service.process_message = Mock()
        return service
    
    @pytest.fixture
    def email_poller(self, mock_message_service):
        """Create EmailPoller instance with mocked dependencies."""
        with patch('sources.email.email_poller.config') as mock_config:
            mock_config.config_json = {
                "email_poller_credentials_path": "test_credentials.json",
                "email_poller_token_path": "test_token.json",
                "email_poller_scope": "https://www.googleapis.com/auth/gmail.readonly",
                "email_poller_sleep_time": 60
            }
            return EmailPoller(mock_message_service)
    
    def test_process_real_gmail_data(self, email_poller, mock_message_service, sample_gmail_data):
        """Test processing realistic Gmail API data."""
        # Mock the Gmail service
        mock_service = Mock()
        
        # Mock list response
        mock_list_response = Mock()
        mock_list_response.execute.return_value = {
            "messages": [{"id": sample_gmail_data["id"]}]
        }
        
        # Mock get response
        mock_get_response = Mock()
        mock_get_response.execute.return_value = sample_gmail_data
        
        # Mock batch modify response
        mock_batch_modify = Mock()
        mock_batch_modify.execute.return_value = {}
        
        # Setup service chain
        mock_service.users.return_value.messages.return_value.list.return_value = mock_list_response
        mock_service.users.return_value.messages.return_value.get.return_value = mock_get_response
        mock_service.users.return_value.messages.return_value.batchModify.return_value = mock_batch_modify
        mock_service.new_batch_http_request.return_value = Mock()
        
        email_poller.service = mock_service
        
        # Process the email
        email_poller.fetch_and_mark_unread_emails_batch()
        
        # Verify message service was called with correct data
        mock_message_service.process_message.assert_called_once_with(
            source='email', raw_data=sample_gmail_data
        )
        
        # Verify the data structure is preserved
        called_kwargs = mock_message_service.process_message.call_args[1]
        assert called_kwargs['source'] == 'email'
        assert called_kwargs['raw_data']["id"] == sample_gmail_data["id"]
        assert called_kwargs['raw_data']["threadId"] == sample_gmail_data["threadId"]
        assert called_kwargs['raw_data']["payload"]["headers"] == sample_gmail_data["payload"]["headers"]
    
    def test_handle_multiple_emails(self, email_poller, mock_message_service):
        """Test handling multiple emails in one batch."""
        # Create multiple sample emails
        email1 = {
            "id": "email1",
            "threadId": "thread1",
            "snippet": "First email",
            "payload": {"headers": [{"name": "Subject", "value": "Email 1"}]}
        }
        email2 = {
            "id": "email2", 
            "threadId": "thread2",
            "snippet": "Second email",
            "payload": {"headers": [{"name": "Subject", "value": "Email 2"}]}
        }
        
        # Mock service
        mock_service = Mock()
        mock_list_response = Mock()
        mock_list_response.execute.return_value = {
            "messages": [{"id": "email1"}, {"id": "email2"}]
        }
        
        # Mock get responses
        mock_get_response = Mock()
        mock_get_response.execute.side_effect = [email1, email2]
        
        mock_batch_modify = Mock()
        mock_batch_modify.execute.return_value = {}
        
        mock_service.users.return_value.messages.return_value.list.return_value = mock_list_response
        mock_service.users.return_value.messages.return_value.get.return_value = mock_get_response
        mock_service.users.return_value.messages.return_value.batchModify.return_value = mock_batch_modify
        mock_service.new_batch_http_request.return_value = Mock()
        
        email_poller.service = mock_service
        
        # Process emails
        email_poller.fetch_and_mark_unread_emails_batch()
        
        # Verify both emails were processed
        assert mock_message_service.process_message.call_count == 2

        # Verify correct data was passed
        calls = mock_message_service.process_message.call_args_list
        
        # Check first call - should be called with source='email', raw_data=email_data
        first_call_kwargs = calls[0][1]  # Get keyword arguments of first call
        assert first_call_kwargs['source'] == 'email'
        assert first_call_kwargs['raw_data']["id"] == "email1"
        
        # Check second call - should be called with source='email', raw_data=email_data  
        second_call_kwargs = calls[1][1]  # Get keyword arguments of second call
        assert second_call_kwargs['source'] == 'email'
        assert second_call_kwargs['raw_data']["id"] == "email2"
    
    def test_handle_gmail_api_errors(self, email_poller, mock_message_service):
        """Test handling Gmail API errors gracefully."""
        mock_service = Mock()
        
        # Mock list response with error
        mock_list_response = Mock()
        mock_list_response.execute.side_effect = Exception("Gmail API error")
        
        mock_service.users.return_value.messages.return_value.list.return_value = mock_list_response
        
        email_poller.service = mock_service
        
        # Should handle error gracefully
        with pytest.raises(Exception):
            email_poller.fetch_and_mark_unread_emails_batch()
    
    def test_handle_empty_response(self, email_poller, mock_message_service):
        """Test handling empty Gmail API response."""
        mock_service = Mock()
        
        # Mock empty response
        mock_list_response = Mock()
        mock_list_response.execute.return_value = {}
        
        mock_service.users.return_value.messages.return_value.list.return_value = mock_list_response
        
        email_poller.service = mock_service
        
        # Should handle gracefully
        with patch('builtins.print') as mock_print:
            email_poller.fetch_and_mark_unread_emails_batch()
            mock_print.assert_called_with("No new unread emails.")

if __name__ == '__main__':
    pytest.main([__file__]) 