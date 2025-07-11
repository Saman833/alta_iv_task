import requests

class TelegramMessager:
    def __init__(self, bot_token: str):
        self.bot_token = bot_token
    def send_message(self, chat_id: str, message: str):
        data={
        "chat_id": chat_id,
        "text": message,
        }
        response = requests.post(f"https://api.telegram.org/bot{self.bot_token}/sendMessage", data=data)