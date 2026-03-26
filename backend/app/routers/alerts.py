import json
import logging
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db, Alert
from app.schemas import AlertRequest, AlertResponse
from app.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)


def _send_whatsapp(to: str, message: str) -> bool:
    if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN:
        logger.info(f"[SIMULATED] WhatsApp to {to}: {message}")
        return True
    try:
        from twilio.rest import Client
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        client.messages.create(
            body=message,
            from_=settings.TWILIO_WHATSAPP_FROM,
            to=to,
        )
        return True
    except Exception as e:
        logger.error(f"Twilio error sending to {to}: {e}")
        return False


@router.post("/alerts/sos", response_model=AlertResponse)
async def send_sos_alert(request: AlertRequest, db: Session = Depends(get_db)):
    recipients = list(request.phone_numbers)

    if settings.ALERT_RECIPIENTS:
        configured = [r.strip() for r in settings.ALERT_RECIPIENTS.split(",") if r.strip()]
        for c in configured:
            if c not in recipients:
                recipients.append(c)

    if not recipients:
        raise HTTPException(status_code=400, detail="No recipients specified and none configured.")

    message_body = (
        f"🚨 DISASTER ALERT 🚨\n"
        f"Type: {request.disaster_type.upper()}\n"
        f"Location: {request.location}\n"
        f"Message: {request.message}\n"
        f"Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}"
    )

    sent_to = []
    for recipient in recipients:
        success = _send_whatsapp(recipient, message_body)
        if success:
            sent_to.append(recipient)

    status = "sent" if sent_to else "failed"

    alert = Alert(
        disaster_type=request.disaster_type,
        location=request.location,
        message=message_body,
        sent_at=datetime.utcnow(),
        recipients=json.dumps(sent_to),
        status=status,
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)

    return AlertResponse(
        alert_id=alert.id,
        status=status,
        sent_to=sent_to,
        timestamp=alert.sent_at,
    )


@router.get("/alerts")
async def get_alerts(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    alerts = db.query(Alert).order_by(Alert.sent_at.desc()).offset(skip).limit(limit).all()
    return {
        "alerts": [
            {
                "id": a.id,
                "disaster_type": a.disaster_type,
                "location": a.location,
                "message": a.message,
                "sent_at": a.sent_at.isoformat(),
                "recipients": json.loads(a.recipients) if a.recipients else [],
                "status": a.status,
            }
            for a in alerts
        ],
        "total": db.query(Alert).count(),
    }
