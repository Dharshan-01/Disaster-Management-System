# 🚨 Next-Gen Disaster Management System

A **proactive, cloud-powered** disaster management platform that uses five specialized Machine Learning models to predict disasters before they strike. It bridges government officials and the public through an automated WhatsApp SOS alert system, live sensor monitoring, and a public news feed — all in one seamless full-stack application.

---

## ✨ Key Features

| Feature | Description |
|---|---|
| 🤖 **5 ML Prediction Models** | RandomForest classifiers for Wildfire, Flood, Cyclone, Earthquake, and Landslide |
| 📡 **Live Sensor Dashboard** | Real-time sensor readings via WebSocket with time-series charts |
| 🚨 **WhatsApp SOS Alerts** | Automated emergency notifications via Twilio WhatsApp API |
| 📰 **Public News Feed** | Disaster news aggregation with RSS feed support |
| 🗺️ **Risk Assessment** | Per-location risk scoring (LOW / MEDIUM / HIGH) with contributing factors |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    React Frontend                        │
│  Dashboard │ Sensors (WS) │ SOS Alerts │ News Feed      │
└──────────────────────┬──────────────────────────────────┘
                       │ HTTP / WebSocket
┌──────────────────────▼──────────────────────────────────┐
│                 FastAPI Backend                          │
│  /api/predict  │  /api/sensors  │  /api/alerts  │  /api/news │
│  WS: /api/ws/sensors                                    │
└──────────┬──────────────┬───────────────┬───────────────┘
           │              │               │
    ┌──────▼──────┐ ┌─────▼──────┐ ┌─────▼──────┐
    │  5 ML Models│ │  SQLite DB │ │  Twilio    │
    │  (sklearn)  │ │            │ │  WhatsApp  │
    └─────────────┘ └────────────┘ └────────────┘
```

### ML Models

Each model is a `RandomForestClassifier` that auto-trains on first run using synthetic data. Models are persisted as `.pkl` files for fast loading.

| Model | Input Features |
|---|---|
| 🔥 Wildfire | temperature, humidity, wind speed, drought index, vegetation density |
| 🌊 Flood | rainfall, river level, soil moisture, upstream rainfall, elevation |
| 🌀 Cyclone | sea surface temp, wind speed, atmospheric pressure, distance to coast |
| 🫨 Earthquake | recent tremors, fault distance, historical magnitude, ground deformation, radon |
| ⛰️ Landslide | rainfall 48h, slope angle, soil saturation, vegetation cover |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+

### 1. Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`.  
Swagger docs: `http://localhost:8000/docs`

### 2. Frontend

```bash
cd frontend
npm install
npm run dev       # Dev server at http://localhost:3000
# or
npm run build     # Production build in frontend/dist/
```

### 3. Docker Compose (full stack)

```bash
# Copy and configure environment variables
cp backend/.env.example backend/.env

# Start all services
docker compose up --build
```

Frontend: `http://localhost:3000` | Backend API: `http://localhost:8000`

---

## ⚙️ Configuration

Copy `backend/.env.example` to `backend/.env` and fill in your credentials:

```env
# Database
DATABASE_URL=sqlite:///./disaster_management.db

# Twilio WhatsApp (optional — alerts are simulated if not set)
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
ALERT_RECIPIENTS=whatsapp:+1234567890,whatsapp:+0987654321

# News RSS feeds (optional — sample data used if not set)
NEWS_RSS_FEEDS=https://feeds.bbci.co.uk/news/world/rss.xml

# Risk alert threshold
RISK_THRESHOLD=0.6
```

---

## 🧪 Running Tests

```bash
cd backend
pytest tests/ -v
```

All 19 tests cover: ML model predictions, API endpoints (predict, sensors, alerts), and database operations.

---

## 📡 API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/predict/all` | Run all 5 disaster predictions |
| `POST` | `/api/predict/{type}` | Predict for a specific disaster type |
| `GET` | `/api/predict/history` | Get prediction history |
| `GET` | `/api/sensors` | Get all sensor readings |
| `POST` | `/api/sensors` | Submit a new sensor reading |
| `WS` | `/api/ws/sensors` | Live sensor stream (5s updates) |
| `POST` | `/api/alerts/sos` | Send WhatsApp SOS alert |
| `GET` | `/api/alerts` | Get all alerts |
| `GET` | `/api/news` | Get disaster news |
| `GET` | `/api/news/refresh` | Refresh news from RSS feeds |

---

## 📁 Project Structure

```
Disaster-Management-System/
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI app, serves frontend
│   │   ├── config.py         # Environment configuration
│   │   ├── database.py       # SQLAlchemy models
│   │   ├── schemas.py        # Pydantic request/response types
│   │   ├── models/           # 5 ML prediction models
│   │   └── routers/          # API route handlers
│   ├── trained_models/       # Auto-generated .pkl model files
│   ├── tests/                # pytest test suite (19 tests)
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── pages/            # Dashboard, Sensors, Alerts, News
│   │   ├── components/       # Reusable UI components
│   │   ├── services/         # API client
│   │   └── types/            # TypeScript interfaces
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml
└── README.md
```

---

## 🛡️ License

MIT License — Copyright 2026 DHARSHAN KUMAR K S

