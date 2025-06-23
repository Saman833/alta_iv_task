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
        subject=self.extract_subject(raw_data)

        content_data, html_content = self._extract_content(raw_data)
        
        final_content_data = content_data if content_data else snippet
        
        content_data ={ 
            'source_id': gmail_id,       
            'content_type': ContentType.TEXT,
            'content_data': final_content_data,
            'content_html': html_content,
            'source': Source.EMAIL,
            'timestamp': timestamp,
            'subject': subject
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
    def extract_subject(self, raw_data: dict) -> str:
        """Extract subject from Gmail API response."""
        subject = ""
        headers = raw_data.get('payload', {}).get('headers', [])
        for header in headers:
            if header['name'] == 'Subject':
                subject = header['value']
        return subject

"""
example of raw data for email : 
{ 'historyId': '3118',
  'id': '197982890e12e974',
  'internalDate': '1750604461000',
  'labelIds': ['UNREAD', 'INBOX'],
  'snippet': 'Test for the whole Json',
  'threadId': '197982890e12e974',
  'sizeEstimate': 5662,
  'payload': { 
    'partId': '',
    'mimeType': 'multipart/alternative',
    'filename': '',
    'headers': [ 
      { 'name': 'Delivered-To', 'value': 'saman.interview.task@gmail.com'},
      { 'name': 'Received', 'value': 'by 2002:a05:7208:13c6:b0:a2:b3d9:5ed2 with SMTP id r6csp14867rbe;        Sun, 22 Jun 2025 08:01:25 -0700 (PDT)'},
      { 'name': 'X-Received', 'value': 'by 2002:a05:6808:2202:b0:406:d4d2:ac06 with SMTP id 5614622812f47-40ac6f5f00emr7685795b6e.9.1750604485104;        Sun, 22 Jun 2025 08:01:25 -0700 (PDT)'},
      { 'name': 'ARC-Seal', 'value': 'i=1; a=rsa-sha256; t=1750604485; cv=none; d=google.com; s=arc-20240605; b=c1h8bbkariSwNOst...'},
      { 'name': 'ARC-Message-Signature', 'value': 'i=1; a=rsa-sha256; c=relaxed/relaxed; d=google.com; s=arc-20240605; h=to:subject:message-id:date:from:mime-version:dkim-signature; bh=bYWwV33Y87CznJrfH79CLq9Bp6XWQP1v4tORnypYHn4=; b=...'},
      { 'name': 'From', 'value': 'saman ahmadifar <s.ahmadifar2005@gmail.com>'},
      { 'name': 'Date', 'value': 'Sun, 22 Jun 2025 17:01:01 +0200'},
      { 'name': 'Subject', 'value': 'Test for the whole json'},
      { 'name': 'To', 'value': '"saman.interview.task@gmail.com" <saman.interview.task@gmail.com>'},
      { 'name': 'Content-Type', 'value': 'multipart/alternative; boundary="000000000000c8e6d206382a5d2e"'}
    ],
    'body': {'size': 0},
    'parts': [ 
      { 'partId': '0',
        'mimeType': 'text/plain',
        'filename': '',
        'headers': [{'name': 'Content-Type', 'value': 'text/plain; charset="UTF-8"'}],
        'body': {'size': 25, 'data': 'VGVzdCBmb3IgdGhlIHdob2xlIEpzb24NCg=='} 
      },
      { 'partId': '1',
        'mimeType': 'text/html',
        'filename': '',
        'headers': [{'name': 'Content-Type', 'value': 'text/html; charset="UTF-8"'}],
        'body': {'size': 47, 'data': 'PGRpdiBkaXI9ImF1dG8iPlRlc3QgZm9yIHRoZSB3aG9sZSBKc29uPC9kaXY-DQo='} 
      }
    ]
  }
}

"""
