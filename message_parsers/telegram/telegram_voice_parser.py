from datetime import datetime
from models import Source, ContentType

class TelegramVoiceParser:
    def __init__(self):
        pass
    
    def parse(self, raw_data: dict) -> dict:

        """
        Parse Telegram voice message and return structured data 
        the goal is to make the parsed data as similar as possible to other parsers return values 
        if it want mvp for sure having diffrent table for each or having content_data schema was nessary 

        """

        message = raw_data.get('message')
        if not message:
            raise ValueError("No message found in raw_data")
        
        voice = message.get('voice')
        if not voice:
            raise ValueError("No voice content found in message")
        
        # Extract message metadata
        message_id = message.get('message_id')
        user_info = message.get('from', {})
        user_id = user_info.get('id')
        username = user_info.get('username')
        first_name = user_info.get('first_name')
        last_name = user_info.get('last_name')
        date_timestamp = message.get('date')
    
        timestamp = datetime.fromtimestamp(date_timestamp)
        
    
        voice_data = f"file_id:{voice.get('file_id')},duration:{voice.get('duration')},mime_type:{voice.get('mime_type')},file_size:{voice.get('file_size')}"
    
        content_data = {
            'source_id': str(message_id),
            'content_type': ContentType.VOICE,
            'content_data': voice_data,
            'content_html': None,  
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
            'type': 'voice',
            'voice_file_id': voice.get('file_id'),
            'content_data': content_data,
            'sender_data': sender_data,
        }
        
        return parsed_data
