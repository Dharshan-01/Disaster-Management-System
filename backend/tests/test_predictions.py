import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.models.wildfire import predict as wildfire_predict
from app.models.flood import predict as flood_predict
from app.models.cyclone import predict as cyclone_predict
from app.models.earthquake import predict as earthquake_predict
from app.models.landslide import predict as landslide_predict


@pytest.mark.asyncio
async def test_wildfire_model_low_risk():
    result = wildfire_predict({
        "temperature_c": 20.0,
        "humidity_pct": 70.0,
        "wind_speed_kmh": 10.0,
        "drought_index": 1.0,
        "vegetation_density": 0.3,
        "distance_to_road_km": 2.0,
    })
    assert "risk_score" in result
    assert "risk_level" in result
    assert "contributing_factors" in result
    assert result["risk_level"] in ("LOW", "MEDIUM", "HIGH")


@pytest.mark.asyncio
async def test_wildfire_model_high_risk():
    result = wildfire_predict({
        "temperature_c": 40.0,
        "humidity_pct": 10.0,
        "wind_speed_kmh": 60.0,
        "drought_index": 9.0,
        "vegetation_density": 0.9,
        "distance_to_road_km": 20.0,
    })
    assert result["risk_score"] >= 0.4
    assert result["risk_level"] in ("MEDIUM", "HIGH")


@pytest.mark.asyncio
async def test_flood_model():
    result = flood_predict({
        "rainfall_mm_24h": 120.0,
        "river_level_m": 6.0,
        "soil_moisture_pct": 85.0,
        "upstream_rainfall_mm": 150.0,
        "elevation_m": 20.0,
        "drainage_capacity": 0.2,
    })
    assert result["risk_level"] in ("MEDIUM", "HIGH")
    assert 0.0 <= result["risk_score"] <= 1.0


@pytest.mark.asyncio
async def test_cyclone_model():
    result = cyclone_predict({
        "sea_surface_temp_c": 30.0,
        "wind_speed_kmh": 150.0,
        "atmospheric_pressure_hpa": 940.0,
        "distance_to_coast_km": 100.0,
        "ocean_heat_content": 120.0,
    })
    assert result["risk_level"] in ("MEDIUM", "HIGH")


@pytest.mark.asyncio
async def test_earthquake_model():
    result = earthquake_predict({
        "recent_tremors_count": 15.0,
        "fault_distance_km": 2.0,
        "historical_magnitude_avg": 6.5,
        "ground_deformation_mm": 8.0,
        "radon_level_ppm": 70.0,
    })
    assert result["risk_level"] in ("MEDIUM", "HIGH")


@pytest.mark.asyncio
async def test_landslide_model():
    result = landslide_predict({
        "rainfall_mm_48h": 200.0,
        "slope_angle_deg": 40.0,
        "soil_saturation_pct": 95.0,
        "vegetation_cover_pct": 10.0,
        "slope_aspect_deg": 270.0,
    })
    assert result["risk_level"] in ("MEDIUM", "HIGH")


@pytest.mark.asyncio
async def test_predict_api_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/predict/wildfire",
            json={
                "disaster_type": "wildfire",
                "features": {
                    "temperature_c": 38.0,
                    "humidity_pct": 15.0,
                    "wind_speed_kmh": 55.0,
                    "drought_index": 8.0,
                    "vegetation_density": 0.8,
                    "distance_to_road_km": 10.0,
                },
                "location": "California",
            },
        )
    assert response.status_code == 200
    data = response.json()
    assert "risk_score" in data
    assert "risk_level" in data
    assert data["disaster_type"] == "wildfire"


@pytest.mark.asyncio
async def test_predict_all_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/predict/all")
    assert response.status_code == 200
    data = response.json()
    assert "predictions" in data
    for disaster in ["wildfire", "flood", "cyclone", "earthquake", "landslide"]:
        assert disaster in data["predictions"]


@pytest.mark.asyncio
async def test_predict_invalid_disaster_type():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/predict/volcano",
            json={"disaster_type": "volcano", "features": {}, "location": "Iceland"},
        )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_risk_level_categorization():
    result = wildfire_predict({
        "temperature_c": 15.0,
        "humidity_pct": 80.0,
        "wind_speed_kmh": 5.0,
        "drought_index": 0.5,
        "vegetation_density": 0.1,
        "distance_to_road_km": 1.0,
    })
    score_str = str(result["risk_score"])
    decimals = len(score_str.split(".")[-1]) if "." in score_str else 0
    assert decimals <= 4
    if result["risk_score"] >= 0.7:
        assert result["risk_level"] == "HIGH"
    elif result["risk_score"] >= 0.4:
        assert result["risk_level"] == "MEDIUM"
    else:
        assert result["risk_level"] == "LOW"
