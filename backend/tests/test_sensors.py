import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_get_all_sensors():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/sensors")
    assert response.status_code == 200
    data = response.json()
    assert "sensors" in data
    assert len(data["sensors"]) > 0


@pytest.mark.asyncio
async def test_post_sensor_reading():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/sensors",
            json={
                "sensor_id": "sensor_001",
                "disaster_type": "flood",
                "location": "Test_Location",
                "readings": {
                    "rainfall_mm_24h": 45.0,
                    "river_level_m": 2.5,
                    "soil_moisture_pct": 60.0,
                    "upstream_rainfall_mm": 55.0,
                    "elevation_m": 80.0,
                    "drainage_capacity": 0.6,
                },
            },
        )
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "stored"
    assert "id" in data


@pytest.mark.asyncio
async def test_get_sensor_by_location():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        await client.post(
            "/api/sensors",
            json={
                "sensor_id": "sensor_002",
                "disaster_type": "wildfire",
                "location": "Test_Forest",
                "readings": {
                    "temperature_c": 30.0,
                    "humidity_pct": 40.0,
                    "wind_speed_kmh": 25.0,
                    "drought_index": 5.0,
                    "vegetation_density": 0.7,
                    "distance_to_road_km": 8.0,
                },
            },
        )
        response = await client.get("/api/sensors/Test_Forest")
    assert response.status_code == 200
    data = response.json()
    assert data["location"] == "Test_Forest"


@pytest.mark.asyncio
async def test_get_sensor_location_not_found():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/sensors/NonExistentLocation_XYZ")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_sensor_baseline_location():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/sensors/Location_A")
    assert response.status_code == 200
