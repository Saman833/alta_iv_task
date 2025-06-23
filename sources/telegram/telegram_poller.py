import requests
import time
from config import config
from services.message_service import MessageService


class TelegramPoller:
    def __init__(self, message_service: MessageService):
        self.bot_token = config.TELEGRAM_BOT_TOKEN
        self.api_url = config.config_json.get("telegram_api_url") + self.bot_token
        self.file_url = config.config_json.get("telegram_file_api_url") + self.bot_token
        self.message_service = message_service
        self.sleep_time = config.config_json.get("telegram_poller_sleep_time")
        self.offset = self.message_service.get_first_unread_source_id_telegram() 
        

    def get_updates(self, offset=None):
        params = {"timeout": 30}
        if offset:
            params["offset"] = offset
        response = requests.get(f"{self.api_url}/getUpdates", params=params)
        try:
            data = response.json()
        except Exception as e:
            print(f"Error decoding Telegram API response: {e}")
            return []
        if not data.get("ok"):
            print("Telegram API error:", data)
            return []
        return data.get("result", [])
        
    def start_polling(self):
        print("Starting Telegram polling...")
        while True:
            try:
                updates = self.get_updates(self.offset)
                
                for update in updates:
                    self.message_service.process_message(source='telegram', raw_data=update)
                    self.offset = update["update_id"] + 1
                
                time.sleep(self.sleep_time)
                
            except Exception as e:
                print(f"Error in Telegram polling: {e}")
                time.sleep(self.sleep_time)


if __name__ == "__main__":
    telegram_poller = TelegramPoller(message_service=MessageService())
    telegram_poller.start_polling()

