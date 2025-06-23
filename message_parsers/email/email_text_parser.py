import base64
from datetime import datetime
from models.content import Content, ContentType, Source

class EmailTextParser:
    def __init__(self):
        pass 
    def convert_to_timestamp(self, internal_date: str) -> datetime:
        """
        add this later to utils as it would be used in other parsers too with a good chance
        
        """
        return datetime.fromtimestamp(int(internal_date) / 1000)
    
    def parse(self, raw_data: dict) -> dict:
        """Parse Gmail API response and return structured data."""
        

        gmail_id = raw_data.get('id') 
        snippet = raw_data.get('snippet', '')
        internal_date = raw_data.get('internalDate')
        
        timestamp = self.convert_to_timestamp(internal_date)

        content_data, html_content = self._extract_content(raw_data)
        
        final_content_data = content_data if content_data else snippet
        
        content_data ={ 
            'source_id': gmail_id,       
            'content_type': ContentType.TEXT,
            'content_data': final_content_data,
            'content_html': html_content,
            'source': Source.EMAIL,
            'timestamp': timestamp
        }
        
        parsed_data = {
            'type': 'text',
            'source': Source.EMAIL,
            'source_id': gmail_id,
            'content_data': content_data,
            'content_html': html_content,
        }
        return parsed_data
    

    
    def _extract_content(self, raw_data: dict) -> tuple[str, str]:
        """Extract text and HTML content from Gmail API response."""
        text_content = ""
        html_content = ""
        
        payload = raw_data.get('payload', {})
        
        # Check if email has parts (multipart)
        if 'parts' in payload:
            for part in payload['parts']:
                mime_type = part.get('mimeType', '')
                body_data = part.get('body', {}).get('data', '')
                
                if mime_type == 'text/plain' and body_data:
                    text_content = self._decode_base64(body_data)
                elif mime_type == 'text/html' and body_data:
                    html_content = self._decode_base64(body_data)
        
        # If no parts, check if it's a simple email
        elif payload.get('mimeType') == 'text/plain':
            body_data = payload.get('body', {}).get('data', '')
            if body_data:
                text_content = self._decode_base64(body_data)
        
        elif payload.get('mimeType') == 'text/html':
            body_data = payload.get('body', {}).get('data', '')
            if body_data:
                html_content = self._decode_base64(body_data)
        
        return text_content, html_content
    
    def _decode_base64(self, data: str) -> str:
        """Decode base64 data from Gmail API."""
        try:
            # Gmail uses URL-safe base64, so we need to handle padding
            # Replace URL-safe characters and add padding if needed
            data = data.replace('-', '+').replace('_', '/')
            padding = 4 - (len(data) % 4)
            if padding != 4:
                data += '=' * padding
            
            decoded_bytes = base64.b64decode(data)
            return decoded_bytes.decode('utf-8')
        except Exception as e:
            print(f"Error decoding base64 data: {e}")
            return ""


