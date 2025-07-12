import os
import json 
from dotenv import load_dotenv

    
class Config:
    def __init__(self):
        load_dotenv()
        self.SQL_URI = os.getenv("SQL_URI", "sqlite:///./test.db")
        self.TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        self.config_json = json.load(open("config.json"))

config = Config()
