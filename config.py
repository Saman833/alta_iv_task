import os
import json 
from dotenv import load_dotenv

class Config:
    def __init__(self):
        load_dotenv()
        
        # Use Railway's SQLAlchemy URIs directly
        self.SQL_URI = os.getenv("SQL_URI", "sqlite:///./test.db")
        self.SYNC_SQL_URI = os.getenv("SYNC_SQL_URI", "sqlite:///./test.db")
        
        # Fallback to individual components if URIs not provided
        if not self.SQL_URI or self.SQL_URI == "sqlite:///./test.db":
            self.POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
            self.POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "")
            self.POSTGRES_SERVER = os.getenv("PGHOST", "localhost")
            self.POSTGRES_PORT = int(os.getenv("PGPORT", "5432"))
            self.POSTGRES_DB = os.getenv("POSTGRES_DB", "railway")
        
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
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        """Use Railway's sync SQL URI or build from components"""
        # Debug: Print all relevant environment variables
        print(f"🔧 Environment variables:")
        print(f"   SQL_URI: {os.getenv('SQL_URI', 'NOT_SET')}")
        print(f"   SYNC_SQL_URI: {os.getenv('SYNC_SQL_URI', 'NOT_SET')}")
        print(f"   PGHOST: {os.getenv('PGHOST', 'NOT_SET')}")
        
        if self.SYNC_SQL_URI and self.SYNC_SQL_URI != "sqlite:///./test.db":
            print(f"🔧 Using Railway sync URI: {self.SYNC_SQL_URI}")
            return self.SYNC_SQL_URI
        
        # Fallback to building from components
        try:
            print(f"🔧 Building sync PostgreSQL URL with:")
            print(f"   User: {self.POSTGRES_USER}")
            print(f"   Host: {self.POSTGRES_SERVER}")
            print(f"   Port: {self.POSTGRES_PORT}")
            print(f"   Database: {self.POSTGRES_DB}")
            
            return (
                f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
                f"@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
            )
        except Exception as e:
            print(f"⚠️  Error building PostgreSQL URL: {e}")
            print(f"   Falling back to SQLite for local development")
            return "sqlite:///./test.db"

    @property
    def ASYNC_SQLALCHEMY_DATABASE_URI(self) -> str:
        """Use Railway's async SQL URI or build from components"""
        if self.SQL_URI and self.SQL_URI != "sqlite:///./test.db":
            print(f"🔧 Using Railway async URI: {self.SQL_URI}")
            return self.SQL_URI
        
        # Fallback to building from components
        try:
            return (
                f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
                f"@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
            )
        except Exception as e:
            print(f"⚠️  Error building async PostgreSQL URL: {e}")
            return self.SQLALCHEMY_DATABASE_URI

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
