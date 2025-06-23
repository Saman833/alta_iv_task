import os
import json 
from dotenv import load_dotenv

    
class Config:
    def __init__(self):
        load_dotenv()
        self.SQL_URI = os.getenv("SQL_URI", "sqlite:///./test.db")
        self.TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

        # Gmail credentials as individual environment variables
        self.GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
        self.GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
        self.GOOGLE_REFRESH_TOKEN = os.getenv("GOOGLE_REFRESH_TOKEN")
        self.GOOGLE_ACCESS_TOKEN = os.getenv("GOOGLE_ACCESS_TOKEN")
        self.GOOGLE_AUTH_URI = os.getenv("GOOGLE_AUTH_URI")
        self.GOOGLE_TOKEN_URI = os.getenv("GOOGLE_TOKEN_URI")
        self.GOOGLE_PROVIDER_CERT_URL = os.getenv("GOOGLE_PROVIDER_CERT_URL")
        
        self.config_json = json.load(open("config.json"))
def create_email_credentials_json(config):
    """
    create a json file with the email credentials
    """
    credentials = {
        "installed": {
    "client_id": config.GOOGLE_CLIENT_ID,
    "client_secret": config.GOOGLE_CLIENT_SECRET,
    "refresh_token": config.GOOGLE_REFRESH_TOKEN,
    "access_token": config.GOOGLE_ACCESS_TOKEN,
    "auth_uri": config.GOOGLE_AUTH_URI,
    "token_uri": config.GOOGLE_TOKEN_URI,
    "provider_cert_url": config.GOOGLE_PROVIDER_CERT_URL
    }
    }
    with open(config.config_json["email_poller_credentials_path"], "w") as f:
        json.dump(credentials, f)

config = Config()
create_email_credentials_json(config)
