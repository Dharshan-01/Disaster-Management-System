const API_BASE = '/api';

export const api = {
  // Predictions
  getAllPredictions: () => fetch(`${API_BASE}/predict/all`).then(r => r.json()).then(d => d.predictions ?? d),
  getPrediction: (type: string, features: Record<string, number>, location: string) =>
    fetch(`${API_BASE}/predict/${type}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ disaster_type: type, features, location })
    }).then(r => r.json()),
  getPredictionHistory: () => fetch(`${API_BASE}/predict/history`).then(r => r.json()),

  // Sensors
  getSensors: () => fetch(`${API_BASE}/sensors`).then(r => r.json()).then(d => {
    const raw = d.sensors ?? d;
    return Object.values(raw) as import('../types').SensorReading[];
  }),
  getSensorByLocation: (location: string) => fetch(`${API_BASE}/sensors/${location}`).then(r => r.json()),

  // Alerts
  getAlerts: () => fetch(`${API_BASE}/alerts`).then(r => r.json()).then(d => d.alerts ?? d),
  sendSOSAlert: (data: { disaster_type: string; location: string; message: string; phone_numbers: string[] }) =>
    fetch(`${API_BASE}/alerts/sos`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    }).then(r => r.json()),

  // News
  getNews: () => fetch(`${API_BASE}/news`).then(r => r.json()).then(d => d.news ?? d),
  refreshNews: () => fetch(`${API_BASE}/news/refresh`).then(r => r.json()).then(d => d.news ?? d),
};
