import json
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db, SensorReading
from app.schemas import PredictionRequest, PredictionResponse
from app.models import PREDICTORS

router = APIRouter()

DEFAULT_READINGS = {
    "wildfire": {
        "temperature_c": 25.0,
        "humidity_pct": 50.0,
        "wind_speed_kmh": 20.0,
        "drought_index": 3.0,
        "vegetation_density": 0.5,
        "distance_to_road_km": 5.0,
    },
    "flood": {
        "rainfall_mm_24h": 30.0,
        "river_level_m": 2.0,
        "soil_moisture_pct": 50.0,
        "upstream_rainfall_mm": 40.0,
        "elevation_m": 100.0,
        "drainage_capacity": 0.7,
    },
    "cyclone": {
        "sea_surface_temp_c": 26.0,
        "wind_speed_kmh": 60.0,
        "atmospheric_pressure_hpa": 1005.0,
        "distance_to_coast_km": 200.0,
        "ocean_heat_content": 60.0,
    },
    "earthquake": {
        "recent_tremors_count": 2.0,
        "fault_distance_km": 20.0,
        "historical_magnitude_avg": 4.0,
        "ground_deformation_mm": 1.0,
        "radon_level_ppm": 15.0,
    },
    "landslide": {
        "rainfall_mm_48h": 50.0,
        "slope_angle_deg": 20.0,
        "soil_saturation_pct": 60.0,
        "vegetation_cover_pct": 40.0,
        "slope_aspect_deg": 180.0,
    },
}


# Static routes must come before parameterized routes to avoid shadowing
@router.get("/predict/all")
async def predict_all(location: str = "Default Location", db: Session = Depends(get_db)):
    results = {}
    for disaster_type, predictor in PREDICTORS.items():
        features = DEFAULT_READINGS.get(disaster_type, {})
        try:
            result = predictor(features)
            reading = SensorReading(
                disaster_type=disaster_type,
                location=location,
                raw_data=json.dumps(features),
                risk_score=result["risk_score"],
                model_version="1.0.0",
            )
            db.add(reading)
            results[disaster_type] = {
                **result,
                "location": location,
                "timestamp": datetime.utcnow().isoformat(),
            }
        except Exception as e:
            results[disaster_type] = {"error": str(e)}

    db.commit()
    return {"predictions": results, "timestamp": datetime.utcnow().isoformat()}


@router.get("/predict/history")
async def prediction_history(
    skip: int = 0,
    limit: int = 50,
    disaster_type: str = None,
    db: Session = Depends(get_db),
):
    query = db.query(SensorReading)
    if disaster_type:
        query = query.filter(SensorReading.disaster_type == disaster_type.lower())
    readings = query.order_by(SensorReading.timestamp.desc()).offset(skip).limit(limit).all()

    return {
        "history": [
            {
                "id": r.id,
                "disaster_type": r.disaster_type,
                "location": r.location,
                "timestamp": r.timestamp.isoformat(),
                "risk_score": r.risk_score,
                "model_version": r.model_version,
                "raw_data": json.loads(r.raw_data) if r.raw_data else {},
            }
            for r in readings
        ],
        "total": query.count(),
    }


@router.post("/predict/{disaster_type}", response_model=PredictionResponse)
async def predict_disaster(
    disaster_type: str,
    request: PredictionRequest,
    db: Session = Depends(get_db),
):
    disaster_type = disaster_type.lower()
    if disaster_type not in PREDICTORS:
        raise HTTPException(
            status_code=404,
            detail=f"Disaster type '{disaster_type}' not found. Available: {list(PREDICTORS.keys())}",
        )

    try:
        result = PREDICTORS[disaster_type](request.features)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

    reading = SensorReading(
        disaster_type=disaster_type,
        location=request.location,
        raw_data=json.dumps(request.features),
        risk_score=result["risk_score"],
        model_version="1.0.0",
    )
    db.add(reading)
    db.commit()

    return PredictionResponse(
        disaster_type=disaster_type,
        risk_score=result["risk_score"],
        risk_level=result["risk_level"],
        contributing_factors=result["contributing_factors"],
        timestamp=datetime.utcnow(),
        location=request.location,
    )
