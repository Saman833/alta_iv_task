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
            if source == 'telegram' and raw_data['message'].get("voice"):
                return TelegramVoiceParser()
            elif source == 'telegram' and raw_data['message'].get("text"):
                return TelegramTextParser()
            return None 
        except Exception as e:
            print(f"Error in get_parser: {e}")
            return None
           