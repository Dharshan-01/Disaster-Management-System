import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_send_sos_alert_simulated():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/alerts/sos",
            json={
                "disaster_type": "wildfire",
                "location": "California Coast",
                "message": "High wildfire risk detected. Evacuate immediately.",
                "phone_numbers": ["whatsapp:+1234567890"],
            },
        )
    assert response.status_code == 200
    data = response.json()
    assert "alert_id" in data
    assert data["status"] in ("sent", "failed")
    assert "sent_to" in data
    assert "timestamp" in data


@pytest.mark.asyncio
async def test_send_sos_no_recipients():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/alerts/sos",
            json={
                "disaster_type": "flood",
                "location": "River Valley",
                "message": "Flood warning issued.",
                "phone_numbers": [],
            },
        )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_get_alerts():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        await client.post(
            "/api/alerts/sos",
            json={
                "disaster_type": "cyclone",
                "location": "Bay of Bengal",
                "message": "Cyclone warning!",
                "phone_numbers": ["whatsapp:+9876543210"],
            },
        )
        response = await client.get("/api/alerts")
    assert response.status_code == 200
    data = response.json()
    assert "alerts" in data
    assert "total" in data
    assert len(data["alerts"]) >= 1


@pytest.mark.asyncio
async def test_alert_stored_in_db():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        post_response = await client.post(
            "/api/alerts/sos",
            json={
                "disaster_type": "earthquake",
                "location": "Tokyo",
                "message": "Major earthquake detected.",
                "phone_numbers": ["whatsapp:+1112223333"],
            },
        )
        assert post_response.status_code == 200
        alert_id = post_response.json()["alert_id"]

        get_response = await client.get("/api/alerts")

    alerts = get_response.json()["alerts"]
    ids = [a["id"] for a in alerts]
    assert alert_id in ids
