from datetime import datetime
from models import Source, ContentType

class TelegramTextParser:
    def __init__(self):
        pass
    
    def parse(self, raw_data: dict) -> dict:
        """Parse Telegram message and return structured data."""
        message = raw_data.get('message')
        if not message:
            raise ValueError("No message found in raw_data")
        
        # Extract text content
        text = message.get('text')
        if not text:
            raise ValueError("No text content found in message")
        
        # Extract message metadata
        message_id = message.get('message_id')
        chat_id = message.get('chat', {}).get('id')
        user_info = message.get('from', {})
        user_id = user_info.get('id')
        username = user_info.get('username')
        first_name = user_info.get('first_name')
        last_name = user_info.get('last_name')
        date_timestamp = message.get('date')
        
        # Convert timestamp to datetime
        timestamp = datetime.fromtimestamp(date_timestamp)
        
    
        content_data = {
            'source_id': str(message_id),
            'content_type': ContentType.TEXT,
            'content_data': text,
            'content_html': None,  # No HTML for Telegram text messages
            'source': Source.TELEGRAM,
            'timestamp': timestamp
        }
        
        sender_data = {
            'source_id': str(user_id),
            'username': username,
            'first_name': first_name,
            'last_name': last_name,
            'source': Source.TELEGRAM
        }
        
        
        parsed_data = {
            'type': 'text',
            'content_data': content_data,
            'sender_data': sender_data,
        }
        
        return parsed_data


"""
example of telegram text raw_message :
{
    "update_id": 700929842,
    "message": {
      "message_id": 9,
      "from": {
        "id": 1021474158,
        "is_bot": false,
        "first_name": "saman",
        "username": "S_sa_f_ss_A",
        "language_code": "en"
      },
      "chat": {
        "id": 1021474158,
        "first_name": "saman",
        "username": "S_sa_f_ss_A",
        "type": "private"
      },
      "date": 1750635741,
      "text": "A text"
    }
  }







"""