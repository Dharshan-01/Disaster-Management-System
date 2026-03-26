export interface PredictionResult {
  disaster_type: string;
  risk_score: number;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH';
  contributing_factors: string[];
  timestamp: string;
  location: string;
}

export interface SensorReading {
  sensor_id: string;
  disaster_type: string;
  location: string;
  readings: Record<string, number>;
  timestamp: string;
  risk_score?: number;
}

export interface Alert {
  alert_id?: string;
  id?: string;
  disaster_type: string;
  location: string;
  message: string;
  sent_at?: string;
  timestamp?: string;
  recipients?: string[];
  status: string;
}

export interface NewsItem {
  id: string;
  title: string;
  summary: string;
  source: string;
  published_at: string;
  link: string;
  disaster_tags: string[];
}
