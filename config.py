import os
import json 
from dotenv import load_dotenv

    
class Config:
    def __init__(self):
        load_dotenv()
        self.SQL_URL = os.getenv("SQL_URL", "sqlite:///./test.db")
        
        
        self.TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        self.config_json = json.load(open("config.json"))
        # Gmail credentials as individual environment variables
        self.GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
        self.GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
        self.GOOGLE_REFRESH_TOKEN = os.getenv("GOOGLE_REFRESH_TOKEN")
        self.GOOGLE_ACCESS_TOKEN = os.getenv("GOOGLE_ACCESS_TOKEN")
        self.GOOGLE_AUTH_URI = os.getenv("GOOGLE_AUTH_URI")
        self.GOOGLE_TOKEN_URI = os.getenv("GOOGLE_TOKEN_URI")
        self.GOOGLE_PROVIDER_CERT_URL = os.getenv("GOOGLE_PROVIDER_CERT_URL")
        self.TOKEN_GOOGLE_CLIENT_ID=os.getenv("TOKEN_GOOGLE_CLIENT_ID")
        self.TOKEN_GOOGLE_CLIENT_SECRET=os.getenv("TOKEN_GOOGLE_CLIENT_SECRET")

        # OAuth Tokens
        self.TOKEN_GOOGLE_ACCESS_TOKEN=os.getenv("TOKEN_GOOGLE_ACCESS_TOKEN")
        self.TOKEN_GOOGLE_REFRESH_TOKEN=os.getenv("TOKEN_GOOGLE_REFRESH_TOKEN")

         
        self.TOKEN_GOOGLE_TOKEN_URI=os.getenv("TOKEN_GOOGLE_TOKEN_URI")
        self.TOKEN_GOOGLE_SCOPES=os.getenv("TOKEN_GOOGLE_SCOPES")
        self.TOKEN_GOOGLE_TOKEN_EXPIRY=os.getenv("TOKEN_GOOGLE_TOKEN_EXPIRY")
    def create_token_json(self):
        token_js={"token": self.TOKEN_GOOGLE_ACCESS_TOKEN, "refresh_token": self.TOKEN_GOOGLE_REFRESH_TOKEN, "token_uri": self.TOKEN_GOOGLE_TOKEN_URI, "client_id": self.TOKEN_GOOGLE_CLIENT_ID, "client_secret": self.TOKEN_GOOGLE_CLIENT_SECRET, 
              "scopes": [self.TOKEN_GOOGLE_SCOPES], "universe_domain": "googleapis.com", "account": "", "expiry": self.TOKEN_GOOGLE_TOKEN_EXPIRY}
        with open(self.config_json["email_poller_token_path"], "w") as f:
            json.dump(token_js, f)
        
    def create_email_credentials_json(self):
        credentials = {
    "installed": {
    "client_id": self.GOOGLE_CLIENT_ID,
    "client_secret": self.GOOGLE_CLIENT_SECRET,
    "refresh_token": self.GOOGLE_REFRESH_TOKEN,
    "access_token": self.GOOGLE_ACCESS_TOKEN,
    "auth_uri": self.GOOGLE_AUTH_URI,
    "token_uri": self.GOOGLE_TOKEN_URI,
    "provider_cert_url": self.GOOGLE_PROVIDER_CERT_URL
        }
    }
        with open(self.config_json["email_poller_credentials_path"], "w") as f:
            json.dump(credentials, f)

    def setup_sql_url(self):
        pass

config = Config()
config.create_token_json()
config.create_email_credentials_json()
