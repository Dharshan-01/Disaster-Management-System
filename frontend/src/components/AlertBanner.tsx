import { useState } from 'react';
import { AlertTriangle, X } from 'lucide-react';
import { Alert } from '../types';

interface AlertBannerProps {
  alerts: Alert[];
}

export default function AlertBanner({ alerts }: AlertBannerProps) {
  const [dismissed, setDismissed] = useState<Set<string>>(new Set());

  const highAlerts = alerts.filter(a => {
    const key = a.alert_id ?? a.id ?? `${a.location}-${a.sent_at ?? a.timestamp}`;
    return !dismissed.has(key);
  });

  if (highAlerts.length === 0) return null;

  return (
    <div className="flex flex-col gap-2">
      {highAlerts.map(alert => {
        const key = alert.alert_id ?? alert.id ?? `${alert.location}-${alert.sent_at ?? alert.timestamp}`;
        return (
          <div
            key={key}
            className="flex items-start gap-3 bg-red-900/60 border border-red-500/60 rounded-lg px-4 py-3"
          >
            <AlertTriangle className="text-red-400 shrink-0 mt-0.5" size={18} />
            <div className="flex-1 min-w-0">
              <span className="text-red-200 font-semibold text-sm capitalize">
                {alert.disaster_type} Alert — {alert.location}
              </span>
              <p className="text-red-300 text-xs mt-0.5 truncate">{alert.message}</p>
            </div>
            <button
              onClick={() => setDismissed(prev => new Set([...prev, key]))}
              className="text-red-400 hover:text-red-200 shrink-0 transition-colors"
              aria-label="Dismiss alert"
            >
              <X size={16} />
            </button>
          </div>
        );
      })}
    </div>
  );
}
