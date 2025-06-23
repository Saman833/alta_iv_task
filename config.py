import os
import json 
from dotenv import load_dotenv
from pydantic import PostgresDsn
from pydantic_core import MultiHostUrl

    
class Config:
    def __init__(self):
        load_dotenv()
        self.SQL_URL = os.getenv("SQL_URL", "sqlite:///./test.db")
        
        # PostgreSQL connection details
        self.POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
        self.POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "")
        self.POSTGRES_SERVER = os.getenv("PGHOST", os.getenv("RAILWAY_TCP_PROXY_DOMAIN", "localhost"))
        self.POSTGRES_PORT = int(os.getenv("PGPORT", os.getenv("RAILWAY_TCP_PROXY_PORT", "5432")))
        self.POSTGRES_DB = os.getenv("PGDATABASE", os.getenv("POSTGRES_DB", "railway"))
        
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

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn:
        """Build PostgreSQL URL using Pydantic for validation"""
        try:
            return MultiHostUrl.build(
                scheme="postgresql+asyncpg",
                username=self.POSTGRES_USER,
                password=self.POSTGRES_PASSWORD,
                host=self.POSTGRES_SERVER,
                port=self.POSTGRES_PORT,
                path=f"/{self.POSTGRES_DB}",
            )
        except Exception as e:
            print(f"⚠️  Error building PostgreSQL URL: {e}")
            print(f"   Using fallback SQL_URL: {self.SQL_URL}")
            return self.SQL_URL

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
