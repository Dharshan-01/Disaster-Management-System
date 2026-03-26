from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from app.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class SensorReading(Base):
    __tablename__ = "sensor_readings"

    id = Column(Integer, primary_key=True, index=True)
    disaster_type = Column(String, index=True)
    location = Column(String)
    timestamp = Column(DateTime, default=lambda: datetime.utcnow())
    raw_data = Column(Text)
    risk_score = Column(Float, nullable=True)
    model_version = Column(String, default="1.0.0")


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    disaster_type = Column(String)
    location = Column(String)
    message = Column(Text)
    sent_at = Column(DateTime, default=lambda: datetime.utcnow())
    recipients = Column(Text)
    status = Column(String, default="pending")


class NewsItem(Base):
    __tablename__ = "news_items"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    summary = Column(Text)
    source = Column(String)
    published_at = Column(DateTime, default=lambda: datetime.utcnow())
    link = Column(String)
    disaster_tags = Column(Text)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    Base.metadata.create_all(bind=engine)
