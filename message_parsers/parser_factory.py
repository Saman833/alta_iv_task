from message_parsers.email.email_text_parser import EmailTextParser
from message_parsers.telegram.telegram_text_parser import TelegramTextParser
from message_parsers.telegram.telegram_voice_parser import TelegramVoiceParser

class ParserFactory:
    def __init__(self):
        pass 
    def get_parser(self, source: str, raw_data: dict):
        """
        simply choose the right parser 
        """
        try : 
            if source == 'email':
                return EmailTextParser()
            elif source == 'telegram':
                # Check if message exists in the update
                message = raw_data.get('message')
                if not message:
                    print(f"No message found in Telegram update: {raw_data}")
                    return None
                
                # Check for voice message first
                if message.get("voice"):
                    return TelegramVoiceParser()
                # Check for text message
                elif message.get("text"):
                    return TelegramTextParser()
                else:
                    print(f"Unsupported message type in Telegram update: {message}")
                    return None
            return None 
        except Exception as e:
            print(f"Error in get_parser: {e}")
            return None
           