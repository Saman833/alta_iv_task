import os

from dotenv import load_dotenv


class Config:
    def __init__(self):
        load_dotenv()
        self.SQL_URI = os.getenv("SQL_URI", "")


config = Config()