import React, { useEffect, useState } from 'react';
import { 
  BarChart2, 
  CheckCircle2, 
  AlertTriangle, 
  Clock, 
  Calendar, 
  TrendingUp, 
  ShieldCheck, 
  Loader2,
  FileText
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { adherenceService } from '../services/adherenceService';
import { AdherenceStats, MedicationLog } from '../types';

export const AdherencePage: React.FC = () => {
  const { activeProfileId } = useAuth();
  const [stats, setStats] = useState<AdherenceStats | null>(null);
  const [auditLogs, setAuditLogs] = useState<any[]>([]);
  const [periodDays, setPeriodDays] = useState<number>(7);
  const [selectedDate, setSelectedDate] = useState<string>(new Date().toISOString().split('T')[0]);
  const [dailyLogs, setDailyLogs] = useState<MedicationLog[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const fetchAdherenceData = async () => {
    if (!activeProfileId) return;
    setIsLoading(true);
    try {
      const [statsData, logsData, auditData] = await Promise.all([
        adherenceService.getAdherenceStats(activeProfileId, periodDays),
        adherenceService.getDailyLogs(activeProfileId, selectedDate),
        adherenceService.getAuditTrail(activeProfileId)
      ]);
      setStats(statsData);
      setDailyLogs(logsData);
      setAuditLogs(auditData);
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchAdherenceData();
  }, [activeProfileId, periodDays, selectedDate]);

  const handleMarkDose = async (logId: string, status: string) => {
    try {
      await adherenceService.updateDoseStatus(logId, status);
      fetchAdherenceData();
    } catch (e: any) {
      alert(e.response?.data?.error?.message || 'Failed to update dose status');
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-black text-slate-900 tracking-tight">Adherence Tracking & Compliance</h1>
          <p className="text-slate-600 font-medium">Real-time medication adherence metrics, verification logs, and audit trails</p>
        </div>

        {/* Period Selector */}
        <div className="flex gap-2 p-1.5 bg-slate-100 rounded-2xl self-start sm:self-auto">
          <button
            onClick={() => setPeriodDays(7)}
            className={`px-4 py-2 text-xs font-bold rounded-xl transition ${
              periodDays === 7 ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            Past 7 Days
          </button>
          <button
            onClick={() => setPeriodDays(30)}
            className={`px-4 py-2 text-xs font-bold rounded-xl transition ${
              periodDays === 30 ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            Past 30 Days
          </button>
        </div>
      </div>

      {isLoading ? (
        <div className="py-20 text-center">
          <Loader2 className="w-8 h-8 animate-spin text-blue-600 mx-auto" />
          <p className="text-sm font-semibold text-slate-500 mt-2">Calculating compliance metrics...</p>
        </div>
      ) : (
        <>
          {/* Key Metric Highlights */}
          {stats && (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-bold uppercase tracking-wider text-slate-500">Adherence Score</span>
                  <TrendingUp className="w-5 h-5 text-emerald-600" />
                </div>
                <div className="text-4xl font-black text-slate-900">{stats.adherence_rate}%</div>
                <p className="text-xs text-slate-500 mt-1">Based on {stats.period_days}-day scheduled records</p>
              </div>

              <div className="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-bold uppercase tracking-wider text-slate-500">Taken Doses</span>
                  <CheckCircle2 className="w-5 h-5 text-emerald-600" />
                </div>
                <div className="text-4xl font-black text-emerald-600">{stats.taken}</div>
                <p className="text-xs text-slate-500 mt-1">Confirmed on-time or logged</p>
              </div>

              <div className="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-bold uppercase tracking-wider text-slate-500">Missed Doses</span>
                  <AlertTriangle className="w-5 h-5 text-red-600" />
                </div>
                <div className="text-4xl font-black text-red-600">{stats.missed}</div>
                <p className="text-xs text-slate-500 mt-1">Overdue without confirmation</p>
              </div>

              <div className="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-bold uppercase tracking-wider text-slate-500">Skipped (Physician Order)</span>
                  <Clock className="w-5 h-5 text-slate-400" />
                </div>
                <div className="text-4xl font-black text-slate-700">{stats.skipped}</div>
                <p className="text-xs text-slate-500 mt-1">Authorized skips or pauses</p>
              </div>
            </div>
          )}

          {/* Daily Trend Visualizer Chart */}
          {stats && stats.daily_breakdown && (
            <div className="bg-white border border-slate-200 rounded-3xl p-6 sm:p-8 shadow-sm">
              <h2 className="text-xl font-black text-slate-900 mb-6 flex items-center gap-2">
                <BarChart2 className="w-5 h-5 text-blue-600" />
                <span>Daily Compliance Breakdown</span>
              </h2>

              <div className="grid grid-cols-7 gap-3">
                {stats.daily_breakdown.map((day) => {
                  const pct = day.total > 0 ? Math.round((day.taken / day.total) * 100) : 100;
                  return (
                    <div key={day.date} className="flex flex-col items-center">
                      <div className="w-full bg-slate-100 rounded-2xl h-36 p-2 flex flex-col justify-end relative overflow-hidden">
                        <div
                          style={{ height: `${pct}%` }}
                          className={`w-full rounded-xl transition-all ${
                            pct >= 80 ? 'bg-emerald-500' : pct >= 50 ? 'bg-amber-500' : 'bg-red-500'
                          }`}
                        />
                        <span className="absolute inset-x-0 bottom-2 text-center text-[10px] font-black text-slate-800">
                          {pct}%
                        </span>
                      </div>
                      <span className="text-xs font-bold text-slate-700 mt-2">{day.day_name}</span>
                      <span className="text-[10px] text-slate-400">{day.date.split('-').slice(1).join('/')}</span>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Date Inspection & Verification */}
          <div className="bg-white border border-slate-200 rounded-3xl p-6 sm:p-8 shadow-sm">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
              <div>
                <h2 className="text-xl font-black text-slate-900 flex items-center gap-2">
                  <Calendar className="w-5 h-5 text-indigo-600" />
                  <span>Dose Logs for Selected Date</span>
                </h2>
                <p className="text-xs text-slate-500">Audit status and record caregiver confirmations</p>
              </div>

              <div className="flex items-center gap-2">
                <span className="text-xs font-bold text-slate-600">Select Date:</span>
                <input
                  type="date"
                  value={selectedDate}
                  onChange={(e) => setSelectedDate(e.target.value)}
                  className="px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-bold font-mono"
                />
              </div>
            </div>

            {dailyLogs.length > 0 ? (
              <div className="divide-y divide-slate-100">
                {dailyLogs.map((log) => (
                  <div key={log.id} className="py-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                    <div className="flex items-start gap-4">
                      <div className="px-3 py-2 bg-slate-100 border border-slate-200 rounded-xl font-mono text-sm font-black text-slate-800">
                        {log.scheduled_time}
                      </div>
                      <div>
                        <h4 className="font-bold text-slate-900 text-base">
                          {log.medication_name} ({log.dosage} {log.unit})
                        </h4>
                        <p className="text-xs text-slate-500 font-medium">
                          {log.label || 'Dose'} • {log.instructions || 'Standard'}
                          {log.recorded_by_name && (
                            <span className="ml-2 text-indigo-600 font-semibold">• Logged by {log.recorded_by_name}</span>
                          )}
                        </p>
                      </div>
                    </div>

                    <div className="flex items-center gap-2">
                      <span className={`px-3 py-1 rounded-xl text-xs font-black uppercase tracking-wider ${
                        log.status === 'TAKEN'
                          ? 'bg-emerald-100 text-emerald-800'
                          : log.status === 'MISSED'
                          ? 'bg-red-100 text-red-800'
                          : log.status === 'SKIPPED'
                          ? 'bg-slate-100 text-slate-700'
                          : 'bg-blue-100 text-blue-800'
                      }`}>
                        {log.status}
                      </span>

                      {log.status !== 'TAKEN' && (
                        <button
                          onClick={() => handleMarkDose(log.id, 'TAKEN')}
                          className="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs rounded-xl"
                        >
                          Mark Taken
                        </button>
                      )}
                      {log.status === 'UPCOMING' && (
                        <button
                          onClick={() => handleMarkDose(log.id, 'SKIPPED')}
                          className="px-3 py-1.5 bg-slate-200 hover:bg-slate-300 text-slate-700 font-bold text-xs rounded-xl"
                        >
                          Skip
                        </button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-center py-8 text-sm text-slate-500">No scheduled doses for this date.</p>
            )}
          </div>

          {/* Immutable Audit Trail Section */}
          <div className="bg-white border border-slate-200 rounded-3xl p-6 sm:p-8 shadow-sm">
            <h2 className="text-xl font-black text-slate-900 mb-4 flex items-center gap-2">
              <ShieldCheck className="w-5 h-5 text-blue-600" />
              <span>Immutable Healthcare Audit Trail</span>
            </h2>
            <p className="text-xs text-slate-500 mb-6">
              Official record of all dose updates, status corrections, and user actions.
            </p>

            {auditLogs && auditLogs.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-50 text-slate-500 uppercase tracking-wider font-bold border-b border-slate-200">
                    <tr>
                      <th className="py-3 px-4">Timestamp</th>
                      <th className="py-3 px-4">Action</th>
                      <th className="py-3 px-4">Authorized User</th>
                      <th className="py-3 px-4">Record Details</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 text-slate-700 font-medium">
                    {auditLogs.map((log: any) => (
                      <tr key={log.id} className="hover:bg-slate-50">
                        <td className="py-3 px-4 whitespace-nowrap text-slate-500 font-mono">
                          {log.created_at ? new Date(log.created_at).toLocaleString() : 'N/A'}
                        </td>
                        <td className="py-3 px-4 font-bold text-slate-900">
                          {log.action}
                        </td>
                        <td className="py-3 px-4 font-semibold text-blue-600">
                          {log.user_name || 'System'}
                        </td>
                        <td className="py-3 px-4 text-slate-600 max-w-md truncate">
                          {log.details || 'Event logged'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <p className="text-slate-500 text-sm">No audit logs recorded yet.</p>
            )}
          </div>
        </>
      )}
    </div>
  );
};
