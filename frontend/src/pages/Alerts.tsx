import { useEffect, useState, FormEvent } from 'react';
import { Bell, Send, CheckCircle, XCircle, AlertTriangle } from 'lucide-react';
import { api } from '../services/api';
import { Alert } from '../types';

const DISASTER_TYPES = ['wildfire', 'flood', 'cyclone', 'earthquake', 'landslide'];

interface Toast {
  type: 'success' | 'error';
  message: string;
}

export default function Alerts() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [toast, setToast] = useState<Toast | null>(null);

  // Form state
  const [disasterType, setDisasterType] = useState(DISASTER_TYPES[0]);
  const [location, setLocation] = useState('');
  const [message, setMessage] = useState('');
  const [phones, setPhones] = useState('');

  useEffect(() => {
    fetchAlerts();
  }, []);

  useEffect(() => {
    if (!toast) return;
    const id = setTimeout(() => setToast(null), 4000);
    return () => clearTimeout(id);
  }, [toast]);

  function fetchAlerts() {
    setLoading(true);
    api.getAlerts()
      .then(data => setAlerts(Array.isArray(data) ? (data as Alert[]) : []))
      .catch(() => setAlerts([]))
      .finally(() => setLoading(false));
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!location.trim() || !message.trim()) return;

    setSubmitting(true);
    try {
      const phoneList = phones
        .split(',')
        .map(p => p.trim())
        .filter(p => p.length > 0);

      await api.sendSOSAlert({
        disaster_type: disasterType,
        location: location.trim(),
        message: message.trim(),
        phone_numbers: phoneList,
      });

      setToast({ type: 'success', message: 'SOS alert sent successfully!' });
      setLocation('');
      setMessage('');
      setPhones('');
      fetchAlerts();
    } catch {
      setToast({ type: 'error', message: 'Failed to send alert. Please try again.' });
    } finally {
      setSubmitting(false);
    }
  }

  const sentCount = alerts.filter(a => a.status === 'sent').length;
  const successRate = alerts.length > 0 ? Math.round((sentCount / alerts.length) * 100) : 0;

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8 flex flex-col gap-8">

        {/* Header */}
        <div className="flex items-center gap-3">
          <Bell className="text-red-400" size={24} />
          <h1 className="text-2xl font-bold">SOS Alert Management</h1>
        </div>

        {/* Toast */}
        {toast && (
          <div className={`flex items-center gap-3 rounded-lg px-4 py-3 border ${
            toast.type === 'success'
              ? 'bg-green-900/50 border-green-600/50 text-green-300'
              : 'bg-red-900/50 border-red-600/50 text-red-300'
          }`}>
            {toast.type === 'success' ? <CheckCircle size={18} /> : <XCircle size={18} />}
            <span className="text-sm font-medium">{toast.message}</span>
          </div>
        )}

        {/* Stats */}
        <div className="grid grid-cols-3 gap-4">
          {[
            { label: 'Total Alerts', value: alerts.length, color: 'text-blue-400' },
            { label: 'Sent Successfully', value: sentCount, color: 'text-green-400' },
            { label: 'Success Rate', value: `${successRate}%`, color: 'text-purple-400' },
          ].map(({ label, value, color }) => (
            <div key={label} className="bg-gray-800 border border-gray-700 rounded-xl p-4 text-center">
              <div className={`text-2xl font-bold ${color}`}>{value}</div>
              <div className="text-gray-400 text-xs mt-1">{label}</div>
            </div>
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-5 gap-8">
          {/* SOS Form */}
          <div className="lg:col-span-2">
            <div className="bg-gray-800 border border-gray-700 rounded-xl p-6">
              <h2 className="text-lg font-semibold text-white mb-5 flex items-center gap-2">
                <AlertTriangle className="text-yellow-400" size={20} />
                Send SOS Alert
              </h2>
              <form onSubmit={handleSubmit} className="flex flex-col gap-4">
                {/* Disaster Type */}
                <div>
                  <label className="block text-sm text-gray-400 mb-1.5">Disaster Type</label>
                  <select
                    value={disasterType}
                    onChange={e => setDisasterType(e.target.value)}
                    className="w-full bg-gray-900 border border-gray-600 text-white rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 capitalize"
                  >
                    {DISASTER_TYPES.map(t => (
                      <option key={t} value={t} className="capitalize">{t}</option>
                    ))}
                  </select>
                </div>

                {/* Location */}
                <div>
                  <label className="block text-sm text-gray-400 mb-1.5">Location</label>
                  <input
                    type="text"
                    value={location}
                    onChange={e => setLocation(e.target.value)}
                    placeholder="e.g. Location_A, City Name"
                    required
                    className="w-full bg-gray-900 border border-gray-600 text-white rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 placeholder-gray-600"
                  />
                </div>

                {/* Message */}
                <div>
                  <label className="block text-sm text-gray-400 mb-1.5">Message</label>
                  <textarea
                    value={message}
                    onChange={e => setMessage(e.target.value)}
                    placeholder="Describe the emergency situation..."
                    required
                    rows={4}
                    className="w-full bg-gray-900 border border-gray-600 text-white rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 placeholder-gray-600 resize-none"
                  />
                </div>

                {/* Phone Numbers */}
                <div>
                  <label className="block text-sm text-gray-400 mb-1.5">Phone Numbers (comma-separated)</label>
                  <input
                    type="text"
                    value={phones}
                    onChange={e => setPhones(e.target.value)}
                    placeholder="+1234567890, +0987654321"
                    className="w-full bg-gray-900 border border-gray-600 text-white rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 placeholder-gray-600"
                  />
                </div>

                <button
                  type="submit"
                  disabled={submitting}
                  className="flex items-center justify-center gap-2 bg-red-600 hover:bg-red-500 disabled:opacity-50 text-white px-4 py-2.5 rounded-lg text-sm font-semibold transition-colors mt-1"
                >
                  <Send size={15} />
                  {submitting ? 'Sending...' : 'Send SOS Alert'}
                </button>
              </form>
            </div>
          </div>

          {/* Alert History Table */}
          <div className="lg:col-span-3">
            <div className="bg-gray-800 border border-gray-700 rounded-xl p-6 flex flex-col gap-4">
              <h2 className="text-lg font-semibold text-white">Alert History</h2>
              {loading ? (
                <div className="flex flex-col gap-2">
                  {[...Array(4)].map((_, i) => (
                    <div key={i} className="h-14 bg-gray-700 rounded-lg animate-pulse" />
                  ))}
                </div>
              ) : alerts.length === 0 ? (
                <div className="text-center text-gray-500 py-8">No alerts recorded yet.</div>
              ) : (
                <div className="flex flex-col gap-2 overflow-y-auto max-h-[480px] pr-1">
                  {alerts.map((alert, i) => {
                    const key = alert.alert_id ?? alert.id ?? String(i);
                    const ts = alert.sent_at ?? alert.timestamp;
                    return (
                      <div key={key} className="bg-gray-900 rounded-lg px-4 py-3 flex items-start justify-between gap-3">
                        <div className="flex items-start gap-2.5 min-w-0">
                          <span className="text-base shrink-0 mt-0.5">
                            {alert.disaster_type === 'wildfire' ? '🔥' :
                             alert.disaster_type === 'flood' ? '🌊' :
                             alert.disaster_type === 'cyclone' ? '🌀' :
                             alert.disaster_type === 'earthquake' ? '🫨' : '⛰️'}
                          </span>
                          <div className="min-w-0">
                            <div className="text-white text-sm font-medium capitalize truncate">
                              {alert.disaster_type} — {alert.location}
                            </div>
                            <div className="text-gray-400 text-xs truncate">{alert.message}</div>
                            {ts && (
                              <div className="text-gray-600 text-xs mt-0.5">
                                {new Date(ts).toLocaleString()}
                              </div>
                            )}
                          </div>
                        </div>
                        <span className={`text-xs px-2.5 py-1 rounded-full font-semibold shrink-0 ${
                          alert.status === 'sent'
                            ? 'bg-green-500/20 text-green-300'
                            : alert.status === 'failed'
                            ? 'bg-red-500/20 text-red-300'
                            : 'bg-gray-600/40 text-gray-400'
                        }`}>{alert.status}</span>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
