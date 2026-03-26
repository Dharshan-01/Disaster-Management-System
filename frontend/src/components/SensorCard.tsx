import { SensorReading } from '../types';
import { formatDistanceToNow } from '../utils/formatDistanceToNow';

interface SensorCardProps {
  sensor: SensorReading;
}

const DISASTER_EMOJI: Record<string, string> = {
  wildfire: '🔥',
  flood: '🌊',
  cyclone: '🌀',
  earthquake: '🫨',
  landslide: '⛰️',
};

function riskColor(score?: number): string {
  if (score === undefined) return 'border-gray-600';
  if (score >= 0.7) return 'border-red-500';
  if (score >= 0.4) return 'border-yellow-400';
  return 'border-green-500';
}

function riskBg(score?: number): string {
  if (score === undefined) return '';
  if (score >= 0.7) return 'bg-red-900/20';
  if (score >= 0.4) return 'bg-yellow-900/20';
  return 'bg-green-900/20';
}

export default function SensorCard({ sensor }: SensorCardProps) {
  const emoji = DISASTER_EMOJI[sensor.disaster_type.toLowerCase()] ?? '📡';
  const time = formatDistanceToNow(sensor.timestamp);

  return (
    <div className={`rounded-xl border-2 ${riskColor(sensor.risk_score)} ${riskBg(sensor.risk_score)} bg-gray-800 p-4 flex flex-col gap-3`}>
      <div className="flex items-start justify-between gap-2">
        <div className="flex items-center gap-2">
          <span className="text-xl">{emoji}</span>
          <div>
            <div className="text-white font-semibold text-sm">{sensor.location}</div>
            <div className="text-gray-400 text-xs capitalize">{sensor.disaster_type} sensor</div>
          </div>
        </div>
        {sensor.risk_score !== undefined && (
          <span
            className={`text-xs font-bold px-2 py-0.5 rounded-full ${
              sensor.risk_score >= 0.7
                ? 'bg-red-500/20 text-red-300'
                : sensor.risk_score >= 0.4
                ? 'bg-yellow-500/20 text-yellow-300'
                : 'bg-green-500/20 text-green-300'
            }`}
          >
            {Math.round(sensor.risk_score * 100)}%
          </span>
        )}
      </div>

      <div className="grid grid-cols-2 gap-x-4 gap-y-1.5">
        {Object.entries(sensor.readings).map(([key, value]) => (
          <div key={key} className="flex justify-between text-xs">
            <span className="text-gray-400 truncate mr-1">{key.replace(/_/g, ' ')}</span>
            <span className="text-gray-200 font-mono font-medium shrink-0">{typeof value === 'number' ? value.toFixed(1) : value}</span>
          </div>
        ))}
      </div>

      <div className="text-gray-500 text-xs border-t border-gray-700 pt-2 flex items-center gap-1">
        <span className="inline-block w-1.5 h-1.5 rounded-full bg-green-500" />
        Updated {time}
      </div>
    </div>
  );
}
