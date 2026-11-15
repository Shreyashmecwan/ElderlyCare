import React, { useEffect, useState } from 'react';
import { 
  Bell, 
  Mail, 
  CheckCircle2, 
  AlertTriangle, 
  Send, 
  Settings, 
  ShieldAlert, 
  Loader2,
  Clock,
  Sparkles
} from 'lucide-react';
import { notificationService } from '../services/notificationService';
import { AppNotification } from '../types';

export const NotificationsPage: React.FC = () => {
  const [notifications, setNotifications] = useState<AppNotification[]>([]);
  const [emailStatus, setEmailStatus] = useState<any>(null);
  const [preferences, setPreferences] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSendingTest, setIsSendingTest] = useState(false);
  const [testResultMsg, setTestResultMsg] = useState<string | null>(null);

  const fetchNotificationData = async () => {
    setIsLoading(true);
    try {
      const [notifsData, prefsData] = await Promise.all([
        notificationService.listNotifications(),
        notificationService.getPreferences()
      ]);
      setNotifications(notifsData.notifications);
      setEmailStatus(notifsData.email_service_status);
      setPreferences(prefsData);
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchNotificationData();
  }, []);

  const handleTogglePref = async (key: string, val: boolean) => {
    const updated = { ...preferences, [key]: val };
    setPreferences(updated);
    try {
      await notificationService.updatePreferences({ [key]: val });
    } catch (e) {
      console.error('Failed to update preferences', e);
    }
  };

  const handleSendTestEmail = async () => {
    setIsSendingTest(true);
    setTestResultMsg(null);
    try {
      const res = await notificationService.sendTestEmail();
      setTestResultMsg(`Test triggered! Recorded status: ${res.data.status}`);
      fetchNotificationData();
    } catch (e: any) {
      setTestResultMsg(`Error: ${e.response?.data?.error?.message || 'Failed to dispatch test'}`);
    } finally {
      setIsSendingTest(false);
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'SENT':
        return (
          <span className="px-2.5 py-1 bg-emerald-100 text-emerald-800 rounded-full font-bold text-xs flex items-center gap-1">
            <CheckCircle2 className="w-3.5 h-3.5" />
            Delivered (Resend)
          </span>
        );
      case 'FAILED':
        return (
          <span className="px-2.5 py-1 bg-red-100 text-red-800 rounded-full font-bold text-xs flex items-center gap-1">
            <AlertTriangle className="w-3.5 h-3.5" />
            Failed
          </span>
        );
      case 'SIMULATED_NOT_CONFIGURED':
        return (
          <span className="px-2.5 py-1 bg-amber-100 text-amber-800 rounded-full font-bold text-xs flex items-center gap-1">
            <ShieldAlert className="w-3.5 h-3.5" />
            API Key Pending
          </span>
        );
      default:
        return (
          <span className="px-2.5 py-1 bg-slate-100 text-slate-700 rounded-full font-bold text-xs">
            {status}
          </span>
        );
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-black text-slate-900 tracking-tight">Email & In-App Notifications</h1>
          <p className="text-slate-600 font-medium">Automated medication reminders, missed dose alerts, and delivery audit</p>
        </div>

        <button
          onClick={handleSendTestEmail}
          disabled={isSendingTest}
          className="px-5 py-3 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white font-bold text-sm rounded-2xl shadow-lg shadow-blue-500/20 transition flex items-center gap-2 self-start sm:self-auto"
        >
          {isSendingTest ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
          <span>Send Test Email</span>
        </button>
      </div>

      {testResultMsg && (
        <div className="p-4 bg-blue-50 border border-blue-200 rounded-2xl text-blue-900 font-semibold text-sm">
          {testResultMsg}
        </div>
      )}

      {/* Real Email Provider Transparency Banner */}
      {emailStatus && (
        <div className="bg-white border border-slate-200 rounded-3xl p-6 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className={`w-12 h-12 rounded-2xl flex items-center justify-center ${
              emailStatus.is_configured ? 'bg-emerald-100 text-emerald-600' : 'bg-amber-100 text-amber-600'
            }`}>
              <Mail className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="font-bold text-slate-900 text-lg">Resend Email Gateway</h3>
                <span className={`px-2.5 py-0.5 rounded-full text-xs font-black uppercase tracking-wider ${
                  emailStatus.is_configured ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800'
                }`}>
                  {emailStatus.is_configured ? 'Production Active' : 'Configuration Key Pending'}
                </span>
              </div>
              <p className="text-xs text-slate-500 mt-0.5">
                Dispatching from: <strong>{emailStatus.mail_from}</strong> • APScheduler interval: 60s
              </p>
            </div>
          </div>

          <div className="text-xs text-slate-500 max-w-sm">
            {emailStatus.is_configured ? (
              <span className="text-emerald-700 font-medium">✓ Connected to official Resend REST API endpoint.</span>
            ) : (
              <span>To deliver real emails to inboxes, add your <code>RESEND_API_KEY=re_...</code> in your environment file.</span>
            )}
          </div>
        </div>
      )}

      {/* Notification Preferences */}
      {preferences && (
        <div className="bg-white border border-slate-200 rounded-3xl p-6 sm:p-8 shadow-sm">
          <h2 className="text-xl font-black text-slate-900 mb-4 flex items-center gap-2">
            <Settings className="w-5 h-5 text-blue-600" />
            <span>Email Alert Preferences</span>
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <label className="flex items-center justify-between p-4 bg-slate-50 rounded-2xl cursor-pointer hover:bg-slate-100 transition">
              <div>
                <p className="font-bold text-slate-900 text-sm">Medication Reminders</p>
                <p className="text-xs text-slate-500">Upcoming dose reminders before scheduled times</p>
              </div>
              <input
                type="checkbox"
                checked={preferences.email_medication_reminders}
                onChange={(e) => handleTogglePref('email_medication_reminders', e.target.checked)}
                className="w-5 h-5 text-blue-600 rounded-lg focus:ring-blue-500 cursor-pointer"
              />
            </label>

            <label className="flex items-center justify-between p-4 bg-slate-50 rounded-2xl cursor-pointer hover:bg-slate-100 transition">
              <div>
                <p className="font-bold text-slate-900 text-sm">Missed Dose Alerts</p>
                <p className="text-xs text-slate-500">Immediate escalation emails to family & caretakers</p>
              </div>
              <input
                type="checkbox"
                checked={preferences.email_missed_dose_alerts}
                onChange={(e) => handleTogglePref('email_missed_dose_alerts', e.target.checked)}
                className="w-5 h-5 text-blue-600 rounded-lg focus:ring-blue-500 cursor-pointer"
              />
            </label>

            <label className="flex items-center justify-between p-4 bg-slate-50 rounded-2xl cursor-pointer hover:bg-slate-100 transition">
              <div>
                <p className="font-bold text-slate-900 text-sm">Appointment Reminders</p>
                <p className="text-xs text-slate-500">Advance 24-hour and day-of doctor visit reminders</p>
              </div>
              <input
                type="checkbox"
                checked={preferences.email_appointment_reminders}
                onChange={(e) => handleTogglePref('email_appointment_reminders', e.target.checked)}
                className="w-5 h-5 text-blue-600 rounded-lg focus:ring-blue-500 cursor-pointer"
              />
            </label>

            <label className="flex items-center justify-between p-4 bg-slate-50 rounded-2xl cursor-pointer hover:bg-slate-100 transition">
              <div>
                <p className="font-bold text-slate-900 text-sm">Daily Health Summaries</p>
                <p className="text-xs text-slate-500">Evening digest of adherence and daily completion</p>
              </div>
              <input
                type="checkbox"
                checked={preferences.email_daily_summary}
                onChange={(e) => handleTogglePref('email_daily_summary', e.target.checked)}
                className="w-5 h-5 text-blue-600 rounded-lg focus:ring-blue-500 cursor-pointer"
              />
            </label>
          </div>
        </div>
      )}

      {/* Real Email Dispatch Logs */}
      <div className="bg-white border border-slate-200 rounded-3xl p-6 sm:p-8 shadow-sm">
        <h2 className="text-xl font-black text-slate-900 mb-2 flex items-center gap-2">
          <Clock className="w-5 h-5 text-indigo-600" />
          <span>Real Notification Delivery Audit Logs</span>
        </h2>
        <p className="text-xs text-slate-500 mb-6">
          Full audit history of system-triggered emails and their actual delivery status.
        </p>

        {isLoading ? (
          <div className="py-12 text-center">
            <Loader2 className="w-6 h-6 animate-spin text-blue-600 mx-auto" />
          </div>
        ) : notifications.length > 0 ? (
          <div className="divide-y divide-slate-100">
            {notifications.map((n) => (
              <div key={n.id} className="py-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div>
                  <div className="flex items-center gap-2">
                    <h4 className="font-bold text-slate-900 text-sm">{n.title}</h4>
                    <span className="text-[10px] font-bold text-slate-500 uppercase px-2 py-0.5 bg-slate-100 rounded-md">
                      {n.type}
                    </span>
                  </div>
                  <p className="text-xs text-slate-500 mt-1">
                    Recipient: <strong className="text-slate-700">{n.recipient_email}</strong> • Sent:{' '}
                    {n.created_at ? new Date(n.created_at).toLocaleString() : 'N/A'}
                  </p>
                  {n.error_message && (
                    <p className="text-xs text-amber-700 mt-1 font-medium bg-amber-50 p-2 rounded-lg">
                      {n.error_message}
                    </p>
                  )}
                </div>

                <div className="self-start sm:self-auto">
                  {getStatusBadge(n.status)}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-slate-500 text-sm">No notification records found.</p>
        )}
      </div>
    </div>
  );
};
