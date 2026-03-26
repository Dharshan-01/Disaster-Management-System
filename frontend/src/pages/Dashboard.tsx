import { useEffect, useState, useCallback } from 'react';
import { RefreshCw, AlertTriangle, TrendingUp, Bell, Radio } from 'lucide-react';
import { api } from '../services/api';
import { PredictionResult, Alert, SensorReading } from '../types';
import RiskGauge from '../components/RiskGauge';
import AlertBanner from '../components/AlertBanner';

function useNow() {
  const [now, setNow] = useState(new Date());
  useEffect(() => {
    const id = setInterval(() => setNow(new Date()), 1000);
    return () => clearInterval(id);
  }, []);
  return now;
}

interface PredictionsMap {
  [key: string]: PredictionResult;
}

export default function Dashboard() {
  const now = useNow();
  const [predictions, setPredictions] = useState<PredictionsMap>({});
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [sensors, setSensors] = useState<SensorReading[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastRefresh, setLastRefresh] = useState<Date | null>(null);

  const fetchAll = useCallback(async () => {
    try {
      const [predData, alertData, sensorData] = await Promise.all([
        api.getAllPredictions().catch(() => ({})),
        api.getAlerts().catch(() => []),
        api.getSensors().catch(() => []),
      ]);
      setPredictions(predData as PredictionsMap);
      setAlerts(Array.isArray(alertData) ? (alertData as Alert[]) : []);
      setSensors(Array.isArray(sensorData) ? (sensorData as SensorReading[]) : []);
      setError(null);
      setLastRefresh(new Date());
    } catch {
      setError('Backend connecting... Retrying shortly.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchAll();
    const id = setInterval(fetchAll, 30_000);
    return () => clearInterval(id);
  }, [fetchAll]);

  const predEntries = Object.entries(predictions);
  const highRiskCount = predEntries.filter(([, p]) => p.risk_level === 'HIGH').length;
  const recentAlerts = alerts.slice(0, 3);

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 flex flex-col gap-8">

        {/* Header */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-white">Next-Gen Disaster Management Dashboard</h1>
            <p className="text-gray-400 text-sm mt-1">
              {now.toLocaleDateString(undefined, { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}
              {' · '}
              {now.toLocaleTimeString()}
            </p>
          </div>
          <button
            onClick={fetchAll}
            disabled={loading}
            className="flex items-center gap-2 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
          >
            <RefreshCw size={14} className={loading ? 'animate-spin' : ''} />
            Refresh
          </button>
        </div>

        {/* Error banner */}
        {error && (
          <div className="flex items-center gap-3 bg-yellow-900/40 border border-yellow-600/50 rounded-lg px-4 py-3">
            <AlertTriangle className="text-yellow-400 shrink-0" size={18} />
            <span className="text-yellow-300 text-sm">{error}</span>
          </div>
        )}

        {/* Alert Banner (high-risk alerts) */}
        {alerts.length > 0 && <AlertBanner alerts={alerts} />}

        {/* Quick Stats */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          {[
            { icon: Bell,       label: 'Total Alerts',    value: alerts.length,      color: 'text-blue-400' },
            { icon: AlertTriangle, label: 'High Risk Areas', value: highRiskCount,   color: 'text-red-400' },
            { icon: Radio,      label: 'Active Sensors',  value: sensors.length,     color: 'text-green-400' },
            { icon: TrendingUp, label: 'Predictions Run', value: predEntries.length, color: 'text-purple-400' },
          ].map(({ icon: Icon, label, value, color }) => (
            <div key={label} className="bg-gray-800 border border-gray-700 rounded-xl p-4 flex items-center gap-3">
              <Icon className={color} size={22} />
              <div>
                <div className="text-xl font-bold text-white">{value}</div>
                <div className="text-gray-400 text-xs">{label}</div>
              </div>
            </div>
          ))}
        </div>

        {/* Prediction Cards */}
        <section>
          <h2 className="text-lg font-semibold text-gray-200 mb-4 flex items-center gap-2">
            <TrendingUp size={18} className="text-blue-400" />
            Disaster Risk Predictions
            {lastRefresh && (
              <span className="text-xs text-gray-500 font-normal ml-2">
                Last updated {lastRefresh.toLocaleTimeString()}
              </span>
            )}
          </h2>

          {loading && predEntries.length === 0 ? (
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="rounded-xl bg-gray-800 border border-gray-700 h-48 animate-pulse" />
              ))}
            </div>
          ) : predEntries.length === 0 ? (
            <div className="bg-gray-800 border border-gray-700 rounded-xl p-8 text-center text-gray-400">
              No prediction data available. Ensure the backend is running.
            </div>
          ) : (
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
              {predEntries.map(([type, pred]) => (
                <div key={type} className="flex flex-col gap-3">
                  <RiskGauge
                    riskScore={pred.risk_score}
                    riskLevel={pred.risk_level}
                    disasterType={type}
                  />
                  <div className="bg-gray-800 border border-gray-700 rounded-xl p-3 flex flex-col gap-1.5 text-xs">
                    <div className="text-gray-300 font-medium">📍 {pred.location || 'N/A'}</div>
                    {pred.contributing_factors && pred.contributing_factors.length > 0 && (
                      <div>
                        <div className="text-gray-500 mb-1">Key factors:</div>
                        {pred.contributing_factors.slice(0, 3).map(f => (
                          <div key={f} className="text-gray-400 truncate">• {f}</div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>

        {/* Recent Alerts */}
        <section>
          <h2 className="text-lg font-semibold text-gray-200 mb-4 flex items-center gap-2">
            <Bell size={18} className="text-red-400" />
            Recent Alerts
          </h2>
          {recentAlerts.length === 0 ? (
            <div className="bg-gray-800 border border-gray-700 rounded-xl p-6 text-center text-gray-500 text-sm">
              No alerts on record.
            </div>
          ) : (
            <div className="flex flex-col gap-2">
              {recentAlerts.map((alert, i) => {
                const key = alert.alert_id ?? alert.id ?? String(i);
                const ts = alert.sent_at ?? alert.timestamp;
                return (
                  <div key={key} className="bg-gray-800 border border-gray-700 rounded-xl px-4 py-3 flex items-center justify-between gap-4">
                    <div className="flex items-center gap-3 min-w-0">
                      <span className="text-lg shrink-0">
                        {alert.disaster_type === 'wildfire' ? '🔥' :
                         alert.disaster_type === 'flood' ? '🌊' :
                         alert.disaster_type === 'cyclone' ? '🌀' :
                         alert.disaster_type === 'earthquake' ? '🫨' : '⛰️'}
                      </span>
                      <div className="min-w-0">
                        <div className="text-white text-sm font-medium truncate capitalize">
                          {alert.disaster_type} — {alert.location}
                        </div>
                        <div className="text-gray-400 text-xs truncate">{alert.message}</div>
                      </div>
                    </div>
                    <div className="flex items-center gap-3 shrink-0">
                      <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                        alert.status === 'sent' ? 'bg-green-500/20 text-green-300' : 'bg-gray-600/40 text-gray-400'
                      }`}>{alert.status}</span>
                      {ts && <span className="text-gray-500 text-xs">{new Date(ts).toLocaleTimeString()}</span>}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </section>

        {/* Live Sensor Overview */}
        <section>
          <h2 className="text-lg font-semibold text-gray-200 mb-4 flex items-center gap-2">
            <Radio size={18} className="text-green-400" />
            Live Sensor Overview
          </h2>
          {sensors.length === 0 ? (
            <div className="bg-gray-800 border border-gray-700 rounded-xl p-6 text-center text-gray-500 text-sm">
              No sensor data available.
            </div>
          ) : (
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
              {sensors.map((sensor, i) => {
                const key = sensor.sensor_id ?? `${sensor.location}-${i}`;
                return (
                  <div key={key} className="bg-gray-800 border border-gray-700 rounded-xl p-3 flex flex-col gap-1.5">
                    <div className="flex items-center justify-between">
                      <span className="text-white text-xs font-semibold">{sensor.location}</span>
                      {sensor.risk_score !== undefined && (
                        <span className={`text-xs font-bold ${
                          sensor.risk_score >= 0.7 ? 'text-red-400' :
                          sensor.risk_score >= 0.4 ? 'text-yellow-400' : 'text-green-400'
                        }`}>{Math.round(sensor.risk_score * 100)}%</span>
                      )}
                    </div>
                    <div className="text-gray-400 text-xs capitalize">{sensor.disaster_type}</div>
                    <div className="text-gray-500 text-xs">{Object.keys(sensor.readings).length} readings</div>
                  </div>
                );
              })}
            </div>
          )}
        </section>
      </div>
    </div>
  );
}
