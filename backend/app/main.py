import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import create_tables
from app.routers import predictions, sensors, alerts, news

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Disaster Management API...")
    create_tables()
    logger.info("Database tables created/verified.")
    logger.info("ML models loaded.")
    yield
    logger.info("Shutting down Disaster Management API.")


app = FastAPI(
    title="Disaster Management System API",
    description="AI-powered disaster prediction and alert management system",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(predictions.router, prefix="/api", tags=["Predictions"])
app.include_router(sensors.router, prefix="/api", tags=["Sensors"])
app.include_router(alerts.router, prefix="/api", tags=["Alerts"])
app.include_router(news.router, prefix="/api", tags=["News"])


@app.get("/", tags=["Health"])
async def root():
    return {"status": "ok", "service": "Disaster Management API"}


@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "service": "Disaster Management API",
        "version": "1.0.0",
    }
