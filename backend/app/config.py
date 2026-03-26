from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./disaster_management.db"
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_WHATSAPP_FROM: str = "whatsapp:+14155238886"
    ALERT_RECIPIENTS: str = ""
    NEWS_RSS_FEEDS: str = ""
    RISK_THRESHOLD: float = 0.6

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
