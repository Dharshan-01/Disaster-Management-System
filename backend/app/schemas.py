from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class PredictionRequest(BaseModel):
    disaster_type: str
    features: Dict[str, float]
    location: str = "Unknown"


class PredictionResponse(BaseModel):
    disaster_type: str
    risk_score: float
    risk_level: str
    contributing_factors: List[str]
    timestamp: datetime
    location: str


class SensorData(BaseModel):
    sensor_id: str
    disaster_type: str
    location: str
    readings: Dict[str, float]
    timestamp: Optional[datetime] = None


class AlertRequest(BaseModel):
    disaster_type: str
    location: str
    message: str
    phone_numbers: List[str] = []


class AlertResponse(BaseModel):
    alert_id: int
    status: str
    sent_to: List[str]
    timestamp: datetime


class NewsItemSchema(BaseModel):
    id: Optional[int] = None
    title: str
    summary: str
    source: str
    published_at: datetime
    link: str
    disaster_tags: List[str] = []

    class Config:
        from_attributes = True
