import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

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

_ALLOW_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=_ALLOW_ORIGINS,
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
    # Serve the frontend if built
    frontend_index = Path(__file__).parent.parent.parent / "frontend" / "dist" / "index.html"
    if frontend_index.exists():
        return FileResponse(str(frontend_index))
    return {"status": "ok", "service": "Disaster Management API"}


# Mount the React frontend static files if the build exists
_frontend_dist = Path(__file__).parent.parent.parent / "frontend" / "dist"
if _frontend_dist.exists():
    app.mount("/assets", StaticFiles(directory=str(_frontend_dist / "assets")), name="assets")

    @app.get("/{path:path}", include_in_schema=False)
    async def spa_fallback(path: str):
        index = _frontend_dist / "index.html"
        return FileResponse(str(index))
