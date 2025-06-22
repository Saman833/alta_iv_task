import os
import json 
from dotenv import load_dotenv

class Config:
    def __init__(self):
        load_dotenv()
        self.SQL_URI = os.getenv("SQL_URI", "sqlite:///./test.db")
        self.config_json = json.load(open("config.json"))

config = Config()