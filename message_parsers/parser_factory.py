from message_parsers.email.email_text_parser import EmailTextParser

class ParserFactory:
    def __init__(self):
        pass
        
    def get_parser(self, source: str, raw_data: dict):
        """Get appropriate parser based on source."""
        if source == 'email':
            return EmailTextParser()
        # Add more parsers here for other sources (telegram, slack, etc.)
        return None 
           