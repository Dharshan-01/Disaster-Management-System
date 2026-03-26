import { useEffect, useState, useRef, useCallback } from 'react';
import { Radio, Wifi, WifiOff } from 'lucide-react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend,
} from 'recharts';
import { SensorReading } from '../types';
import SensorCard from '../components/SensorCard';
import { api } from '../services/api';

const DISASTER_TYPES = ['all', 'wildfire', 'flood', 'cyclone', 'earthquake', 'landslide'];

interface ChartPoint {
  time: string;
  [key: string]: string | number;
}

const LINE_COLORS = ['#60a5fa', '#34d399', '#f59e0b', '#f87171', '#a78bfa', '#fb923c'];

export default function Sensors() {
  const [sensors, setSensors] = useState<SensorReading[]>([]);
  const [wsConnected, setWsConnected] = useState(false);
  const [filter, setFilter] = useState('all');
  const [selected, setSelected] = useState<string | null>(null);
  const [history, setHistory] = useState<Map<string, ChartPoint[]>>(new Map());
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Load initial sensors from REST
  useEffect(() => {
    api.getSensors()
      .then(data => {
        if (Array.isArray(data)) {
          setSensors(data as SensorReading[]);
          if (data.length > 0 && !selected) {
            setSelected((data[0] as SensorReading).location);
          }
        }
      })
      .catch(() => {/* non-critical, WS will populate */});
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const connectWs = useCallback(() => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) return;

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const ws = new WebSocket(`${protocol}//${window.location.host}/ws/sensors`);
    wsRef.current = ws;

    ws.onopen = () => setWsConnected(true);

    ws.onmessage = (evt: MessageEvent) => {
      try {
        const data = JSON.parse(evt.data as string) as SensorReading | SensorReading[];
        const incoming: SensorReading[] = Array.isArray(data) ? data : [data];

        setSensors(prev => {
          const map = new Map(prev.map(s => [s.location, s]));
          incoming.forEach(s => map.set(s.location, s));
          return Array.from(map.values());
        });

        setSelected(prev => prev ?? (incoming[0]?.location ?? null));

        // Append to history (keep last 20 per location)
        setHistory(prev => {
          const next = new Map(prev);
          incoming.forEach(s => {
            const pts = next.get(s.location) ?? [];
            const point: ChartPoint = {
              time: new Date(s.timestamp).toLocaleTimeString(),
              ...s.readings,
            };
            next.set(s.location, [...pts.slice(-19), point]);
          });
          return next;
        });
      } catch {
        // Ignore parse errors
      }
    };

    ws.onclose = () => {
      setWsConnected(false);
      reconnectTimer.current = setTimeout(connectWs, 3000);
    };

    ws.onerror = () => ws.close();
  }, []);

  useEffect(() => {
    connectWs();
    return () => {
      if (reconnectTimer.current) clearTimeout(reconnectTimer.current);
      wsRef.current?.close();
    };
  }, [connectWs]);

  const filtered = filter === 'all' ? sensors : sensors.filter(s => s.disaster_type === filter);
  const selectedSensor = sensors.find(s => s.location === selected);
  const chartData = selected ? (history.get(selected) ?? []) : [];
  const chartKeys = selectedSensor ? Object.keys(selectedSensor.readings) : [];

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 flex flex-col gap-8">

        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Radio className="text-green-400" size={24} />
            <h1 className="text-2xl font-bold">Live Sensor Monitoring</h1>
          </div>
          <div className="flex items-center gap-2">
            {wsConnected ? (
              <>
                <Wifi className="text-green-400" size={18} />
                <span className="text-green-400 text-sm font-medium">🟢 Live</span>
              </>
            ) : (
              <>
                <WifiOff className="text-red-400" size={18} />
                <span className="text-red-400 text-sm font-medium">🔴 Disconnected</span>
              </>
            )}
          </div>
        </div>

        {/* Disaster Type Filter */}
        <div className="flex flex-wrap gap-2">
          {DISASTER_TYPES.map(type => (
            <button
              key={type}
              onClick={() => setFilter(type)}
              className={`px-4 py-1.5 rounded-full text-sm font-medium capitalize transition-colors ${
                filter === type
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-800 text-gray-300 border border-gray-600 hover:bg-gray-700'
              }`}
            >
              {type === 'all' ? 'All Types' : type}
            </button>
          ))}
        </div>

        {/* Sensor Cards Grid */}
        {filtered.length === 0 ? (
          <div className="bg-gray-800 border border-gray-700 rounded-xl p-8 text-center text-gray-500">
            {wsConnected ? 'Waiting for sensor data...' : 'Connecting to sensor network...'}
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {filtered.map((sensor, i) => {
              const key = sensor.sensor_id ?? `${sensor.location}-${i}`;
              return (
                <div
                  key={key}
                  onClick={() => setSelected(sensor.location)}
                  className={`cursor-pointer transition-all ${
                    selected === sensor.location ? 'ring-2 ring-blue-500 rounded-xl' : ''
                  }`}
                >
                  <SensorCard sensor={sensor} />
                </div>
              );
            })}
          </div>
        )}

        {/* Time-Series Chart */}
        {selected && (
          <section>
            <h2 className="text-lg font-semibold text-gray-200 mb-4">
              📈 Sensor History — <span className="text-blue-400">{selected}</span>
              <span className="text-gray-500 text-sm font-normal ml-2">(last 20 readings)</span>
            </h2>
            {chartData.length < 2 ? (
              <div className="bg-gray-800 border border-gray-700 rounded-xl p-8 text-center text-gray-500 text-sm">
                Waiting for more data points... ({chartData.length} / 20)
              </div>
            ) : (
              <div className="bg-gray-800 border border-gray-700 rounded-xl p-4">
                <ResponsiveContainer width="100%" height={280}>
                  <LineChart data={chartData} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                    <XAxis dataKey="time" tick={{ fill: '#9ca3af', fontSize: 11 }} />
                    <YAxis tick={{ fill: '#9ca3af', fontSize: 11 }} />
                    <Tooltip
                      contentStyle={{ background: '#1f2937', border: '1px solid #374151', borderRadius: 8, color: '#f9fafb' }}
                    />
                    <Legend wrapperStyle={{ color: '#d1d5db', fontSize: 12 }} />
                    {chartKeys.map((key, idx) => (
                      <Line
                        key={key}
                        type="monotone"
                        dataKey={key}
                        stroke={LINE_COLORS[idx % LINE_COLORS.length]}
                        strokeWidth={2}
                        dot={false}
                        name={key.replace(/_/g, ' ')}
                      />
                    ))}
                  </LineChart>
                </ResponsiveContainer>
              </div>
            )}
          </section>
        )}
      </div>
    </div>
  );
}
