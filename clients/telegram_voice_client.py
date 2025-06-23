import requests
from config import config

class TelegramVoiceClient:
    def __init__(self):
        self.telegram_bot_token = config.TELEGRAM_BOT_TOKEN
        self.telegram_api_url = config.config_json["telegram_api_url"]
        self.telegram_file_api_url = config.config_json["telegram_file_api_url"]

    def get_telegram_file_path(self, file_id: str) -> str:
        url = f"{self.telegram_api_url}{self.telegram_bot_token}/getFile"
        resp = requests.get(url, params={"file_id": file_id})
        resp.raise_for_status()
        return resp.json()["result"]["file_path"]

    def get_voice_message(self, file_path: str) -> bytes:
        url = f"{self.telegram_file_api_url}{self.telegram_bot_token}/{file_path}"
        resp = requests.get(url)
        resp.raise_for_status()
        return resp.content
    
    
    
    
    