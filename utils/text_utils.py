"""
Utility functions for handling text encoding and processing 
Suggest you not to change anything here 
"""

import unicodedata
import re

def clean_text(text: str) -> str:
    """
    Clean and normalize text to handle encoding issues and special characters.
    """
    if not text:
        return ""
    
    try:
        # First, try to handle any encoding issues
        if isinstance(text, bytes):
            text = text.decode('utf-8', errors='ignore')
        
        # Normalize Unicode characters
        text = unicodedata.normalize('NFKC', text)
        
        # Replace problematic characters
        text = text.replace('\x9d', "'")  # Replace smart right double quotation mark
        text = text.replace('\x9c', '"')  # Replace smart left double quotation mark
        text = text.replace('\x93', '"')  # Replace smart left double quotation mark
        text = text.replace('\x94', '"')  # Replace smart right double quotation mark
        text = text.replace('\x91', "'")  # Replace smart left single quotation mark
        text = text.replace('\x92', "'")  # Replace smart right single quotation mark
        text = text.replace('\x85', '...')  # Replace horizontal ellipsis
        text = text.replace('\x96', '-')   # Replace en dash
        text = text.replace('\x97', '--')  # Replace em dash
        
        # Remove or replace other problematic characters
        text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
        
        # Strip extra whitespace
        text = ' '.join(text.split())
        
        return text
        
    except Exception as e:
        # If all else fails, try to recover as much as possible
        print(f"Warning: Error cleaning text: {e}")
        try:
            return text.encode('utf-8', errors='ignore').decode('utf-8')
        except:
            return str(text)[:1000]  # Return first 1000 characters as fallback

def safe_json_string(text: str) -> str:
    """
    Convert text to a safe JSON string format.
    """
    if not text:
        return ""
    
    cleaned = clean_text(text)
    
    # Escape JSON special characters
    cleaned = cleaned.replace('\\', '\\\\')
    cleaned = cleaned.replace('"', '\\"')
    cleaned = cleaned.replace('\n', '\\n')
    cleaned = cleaned.replace('\r', '\\r')
    cleaned = cleaned.replace('\t', '\\t')
    
    return cleaned 