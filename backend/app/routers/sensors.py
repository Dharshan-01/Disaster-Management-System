import json
import random
import asyncio
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app.database import get_db, SensorReading
from app.schemas import SensorData

router = APIRouter()

BASELINE_SENSORS = {
    "Location_A": {
        "wildfire": {
            "temperature_c": 28.0,
            "humidity_pct": 45.0,
            "wind_speed_kmh": 15.0,
            "drought_index": 4.0,
            "vegetation_density": 0.6,
            "distance_to_road_km": 3.0,
        }
    },
    "Location_B": {
        "flood": {
            "rainfall_mm_24h": 55.0,
            "river_level_m": 3.2,
            "soil_moisture_pct": 65.0,
            "upstream_rainfall_mm": 70.0,
            "elevation_m": 50.0,
            "drainage_capacity": 0.5,
        }
    },
    "Location_C": {
        "cyclone": {
            "sea_surface_temp_c": 27.0,
            "wind_speed_kmh": 90.0,
            "atmospheric_pressure_hpa": 990.0,
            "distance_to_coast_km": 300.0,
            "ocean_heat_content": 80.0,
        }
    },
    "Location_D": {
        "earthquake": {
            "recent_tremors_count": 5.0,
            "fault_distance_km": 12.0,
            "historical_magnitude_avg": 4.5,
            "ground_deformation_mm": 2.5,
            "radon_level_ppm": 30.0,
        }
    },
    "Location_E": {
        "landslide": {
            "rainfall_mm_48h": 80.0,
            "slope_angle_deg": 25.0,
            "soil_saturation_pct": 70.0,
            "vegetation_cover_pct": 35.0,
            "slope_aspect_deg": 200.0,
        }
    },
}


def _add_noise(readings: dict, noise_pct: float = 0.05) -> dict:
    noisy = {}
    for k, v in readings.items():
        noise = v * noise_pct * (random.random() * 2 - 1)
        noisy[k] = round(v + noise, 4)
    return noisy


@router.get("/sensors")
async def get_all_sensors(db: Session = Depends(get_db)):
    latest = {}
    for location, sensor_types in BASELINE_SENSORS.items():
        for disaster_type, readings in sensor_types.items():
            row = (
                db.query(SensorReading)
                .filter(
                    SensorReading.location == location,
                    SensorReading.disaster_type == disaster_type,
                )
                .order_by(SensorReading.timestamp.desc())
                .first()
            )
            latest[f"{location}_{disaster_type}"] = {
                "location": location,
                "disaster_type": disaster_type,
                "readings": json.loads(row.raw_data) if row and row.raw_data else readings,
                "risk_score": row.risk_score if row else None,
                "timestamp": row.timestamp.isoformat() if row else datetime.utcnow().isoformat(),
            }
    return {"sensors": latest}


@router.get("/sensors/{location}")
async def get_sensor_by_location(location: str, db: Session = Depends(get_db)):
    rows = (
        db.query(SensorReading)
        .filter(SensorReading.location == location)
        .order_by(SensorReading.timestamp.desc())
        .limit(20)
        .all()
    )
    if not rows:
        if location in BASELINE_SENSORS:
            return {
                "location": location,
                "readings": BASELINE_SENSORS[location],
                "from_baseline": True,
            }
        raise HTTPException(status_code=404, detail=f"No sensor data for location '{location}'")

    return {
        "location": location,
        "readings": [
            {
                "id": r.id,
                "disaster_type": r.disaster_type,
                "timestamp": r.timestamp.isoformat(),
                "raw_data": json.loads(r.raw_data) if r.raw_data else {},
                "risk_score": r.risk_score,
            }
            for r in rows
        ],
    }


@router.post("/sensors", status_code=201)
async def submit_sensor_reading(data: SensorData, db: Session = Depends(get_db)):
    reading = SensorReading(
        disaster_type=data.disaster_type.lower(),
        location=data.location,
        raw_data=json.dumps(data.readings),
        timestamp=data.timestamp or datetime.utcnow(),
    )
    db.add(reading)
    db.commit()
    db.refresh(reading)
    return {
        "id": reading.id,
        "status": "stored",
        "timestamp": reading.timestamp.isoformat(),
    }


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        import json as _json
        for connection in list(self.active_connections):
            try:
                await connection.send_text(_json.dumps(message))
            except Exception:
                self.disconnect(connection)


manager = ConnectionManager()


@router.websocket("/ws/sensors")
async def websocket_sensors(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            payload = {
                "timestamp": datetime.utcnow().isoformat(),
                "sensors": {},
            }
            for location, sensor_types in BASELINE_SENSORS.items():
                for disaster_type, readings in sensor_types.items():
                    payload["sensors"][f"{location}_{disaster_type}"] = {
                        "location": location,
                        "disaster_type": disaster_type,
                        "readings": _add_noise(readings),
                    }
            await websocket.send_json(payload)
            await asyncio.sleep(5)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception:
        manager.disconnect(websocket)
