interface RiskGaugeProps {
  riskScore: number;
  riskLevel: string;
  disasterType: string;
}

const DISASTER_CONFIG: Record<string, { emoji: string; label: string }> = {
  wildfire:   { emoji: '🔥', label: 'Wildfire' },
  flood:      { emoji: '🌊', label: 'Flood' },
  cyclone:    { emoji: '🌀', label: 'Cyclone' },
  earthquake: { emoji: '🫨', label: 'Earthquake' },
  landslide:  { emoji: '⛰️', label: 'Landslide' },
};

const LEVEL_CONFIG: Record<string, { ring: string; bg: string; text: string; badge: string }> = {
  LOW:    { ring: 'border-green-500',  bg: 'bg-green-900/30',  text: 'text-green-400',  badge: 'bg-green-500/20 text-green-300 border border-green-500/40' },
  MEDIUM: { ring: 'border-yellow-400', bg: 'bg-yellow-900/30', text: 'text-yellow-300', badge: 'bg-yellow-500/20 text-yellow-300 border border-yellow-500/40' },
  HIGH:   { ring: 'border-red-500',    bg: 'bg-red-900/30',    text: 'text-red-400',    badge: 'bg-red-500/20 text-red-300 border border-red-500/40' },
};

export default function RiskGauge({ riskScore, riskLevel, disasterType }: RiskGaugeProps) {
  const level = LEVEL_CONFIG[riskLevel] ?? LEVEL_CONFIG['LOW'];
  const disaster = DISASTER_CONFIG[disasterType.toLowerCase()] ?? { emoji: '⚠️', label: disasterType };
  const pct = Math.round(riskScore * 100);

  // Arc parameters
  const r = 38;
  const cx = 50;
  const cy = 54;
  const circumference = Math.PI * r; // half-circle arc length
  const arcLen = (pct / 100) * circumference;
  const trackColor = '#374151';
  const fillColor =
    riskLevel === 'HIGH' ? '#ef4444' : riskLevel === 'MEDIUM' ? '#eab308' : '#22c55e';

  return (
    <div className={`rounded-xl p-4 ${level.bg} border ${level.ring} border-opacity-50 flex flex-col items-center gap-3`}>
      {/* Semicircular gauge */}
      <div className="relative w-28 h-16 flex items-end justify-center">
        <svg viewBox="0 0 100 60" className="absolute inset-0 w-full h-full overflow-visible">
          {/* Track */}
          <path
            d={`M ${cx - r} ${cy} A ${r} ${r} 0 0 1 ${cx + r} ${cy}`}
            fill="none"
            stroke={trackColor}
            strokeWidth="8"
            strokeLinecap="round"
          />
          {/* Fill */}
          <path
            d={`M ${cx - r} ${cy} A ${r} ${r} 0 0 1 ${cx + r} ${cy}`}
            fill="none"
            stroke={fillColor}
            strokeWidth="8"
            strokeLinecap="round"
            strokeDasharray={`${arcLen} ${circumference}`}
          />
        </svg>
        {/* Center label */}
        <div className="relative z-10 flex flex-col items-center leading-none mb-0.5">
          <span className="text-lg">{disaster.emoji}</span>
        </div>
      </div>

      {/* Score */}
      <div className={`text-3xl font-bold ${level.text}`}>{pct}%</div>

      {/* Disaster name */}
      <div className="text-gray-200 font-semibold text-sm">{disaster.label}</div>

      {/* Level badge */}
      <span className={`text-xs font-bold px-3 py-1 rounded-full uppercase tracking-wider ${level.badge}`}>
        {riskLevel}
      </span>
    </div>
  );
}
