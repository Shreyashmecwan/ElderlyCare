import React from 'react';
import { Link } from 'react-router-dom';
import { 
  Users, 
  Heart, 
  AlertTriangle, 
  Calendar, 
  CheckCircle2, 
  ArrowRight, 
  Plus, 
  ShieldCheck, 
  Activity,
  KeyRound
} from 'lucide-react';

interface FamilyDashboardProps {
  data: any;
  onRefresh: () => void;
  onOpenPasscode: () => void;
}

export const FamilyDashboardView: React.FC<FamilyDashboardProps> = ({ data, onOpenPasscode }) => {
  const { monitored_profiles, missed_alerts, upcoming_appointments } = data;

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-black text-slate-900 tracking-tight">Family Care Dashboard</h1>
          <p className="text-slate-600 font-medium">Monitoring your loved ones' health routines and adherence</p>
        </div>

        <button
          onClick={onOpenPasscode}
          className="px-5 py-3 bg-blue-600 hover:bg-blue-700 text-white font-bold text-sm rounded-2xl shadow-lg shadow-blue-500/20 transition flex items-center gap-2 self-start sm:self-auto"
        >
          <KeyRound className="w-4 h-4" />
          <span>Connect Another Senior</span>
        </button>
      </div>

      {/* Missed Dose Escalation Banner (Crucial for Family Peace of Mind) */}
      {missed_alerts && missed_alerts.length > 0 && (
        <div className="bg-red-50 border-2 border-red-300 rounded-3xl p-6 shadow-md">
          <div className="flex items-center gap-2.5 text-red-800 font-black text-sm uppercase tracking-wider mb-3">
            <AlertTriangle className="w-5 h-5 text-red-600" />
            <span>Attention: Unconfirmed / Missed Medications ({missed_alerts.length})</span>
          </div>
          <div className="space-y-3">
            {missed_alerts.map((alert: any) => (
              <div key={alert.id} className="bg-white p-4 rounded-2xl border border-red-200 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div>
                  <h4 className="font-bold text-slate-900 text-base">
                    {alert.medication_name} ({alert.dosage} {alert.unit})
                  </h4>
                  <p className="text-xs text-red-600 font-medium">
                    Scheduled for {alert.scheduled_date} at {alert.scheduled_time} ({alert.label || 'Dose'})
                  </p>
                </div>
                <Link
                  to="/adherence"
                  className="px-4 py-2 bg-red-100 hover:bg-red-200 text-red-800 font-bold text-xs rounded-xl self-start sm:self-auto transition"
                >
                  View Details & Confirm
                </Link>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Connected Seniors Status Grid */}
      <div>
        <h2 className="text-xl font-black text-slate-900 mb-4 flex items-center gap-2">
          <Users className="w-5 h-5 text-blue-600" />
          <span>Connected Loved Ones</span>
        </h2>

        {monitored_profiles && monitored_profiles.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {monitored_profiles.map((p: any) => (
              <div key={p.profile_id} className="bg-white border border-slate-200 rounded-3xl p-6 shadow-sm hover:shadow-md transition-all">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h3 className="text-xl font-bold text-slate-900">{p.full_name}</h3>
                    <span className="text-xs font-semibold text-blue-600 bg-blue-50 px-2.5 py-0.5 rounded-full">
                      {p.relationship || 'Family Member'}
                    </span>
                  </div>
                  <div className="p-3 bg-emerald-50 text-emerald-700 rounded-2xl font-black text-sm">
                    {p.adherence_rate_7d}% Adherence
                  </div>
                </div>

                <div className="space-y-2 py-3 border-y border-slate-100 text-sm">
                  <div className="flex justify-between text-slate-600">
                    <span>Today's Total Doses:</span>
                    <strong className="text-slate-900">{p.today_total}</strong>
                  </div>
                  <div className="flex justify-between text-slate-600">
                    <span>Administered:</span>
                    <strong className="text-emerald-700">{p.today_taken}</strong>
                  </div>
                  <div className="flex justify-between text-slate-600">
                    <span>Pending / Missed:</span>
                    <strong className={p.today_missed > 0 ? 'text-red-600' : 'text-slate-700'}>
                      {p.today_missed > 0 ? `${p.today_missed} Missed` : 'All On Track'}
                    </strong>
                  </div>
                </div>

                <div className="mt-4 flex items-center gap-2">
                  <Link
                    to={`/medications`}
                    className="flex-1 py-2.5 text-center bg-slate-100 hover:bg-slate-200 text-slate-800 text-xs font-bold rounded-xl transition"
                  >
                    Medications
                  </Link>
                  <Link
                    to={`/adherence`}
                    className="flex-1 py-2.5 text-center bg-blue-50 hover:bg-blue-100 text-blue-700 text-xs font-bold rounded-xl transition"
                  >
                    View Report
                  </Link>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="bg-white border border-slate-200 rounded-3xl p-8 text-center">
            <Users className="w-12 h-12 text-slate-300 mx-auto mb-3" />
            <h3 className="text-lg font-bold text-slate-800">No Loved Ones Connected Yet</h3>
            <p className="text-sm text-slate-500 max-w-md mx-auto mt-1 mb-4">
              Enter the passcode shared by your elderly family member to monitor their medication routine.
            </p>
            <button
              onClick={onOpenPasscode}
              className="px-5 py-2.5 bg-blue-600 text-white font-bold text-sm rounded-xl"
            >
              Enter Passcode
            </button>
          </div>
        )}
      </div>

      {/* Upcoming Family Appointments */}
      {upcoming_appointments && upcoming_appointments.length > 0 && (
        <div className="bg-white border border-slate-200 rounded-3xl p-6 sm:p-8">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-black text-slate-900 flex items-center gap-2">
              <Calendar className="w-5 h-5 text-indigo-600" />
              <span>Upcoming Appointments</span>
            </h2>
            <Link to="/appointments" className="text-sm font-bold text-blue-600 hover:underline flex items-center gap-1">
              <span>View All</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {upcoming_appointments.map((appt: any) => (
              <div key={appt.id} className="p-4 bg-slate-50 border border-slate-200 rounded-2xl">
                <div className="flex items-center justify-between">
                  <h4 className="font-bold text-slate-900 text-base">Dr. {appt.doctor_name}</h4>
                  <span className="text-xs bg-indigo-100 text-indigo-800 px-2.5 py-0.5 rounded-full font-bold">
                    {appt.specialty || 'Checkup'}
                  </span>
                </div>
                <p className="text-xs text-slate-500 font-medium mt-1">
                  {appt.appointment_date} at {appt.appointment_time} • {appt.hospital_clinic}
                </p>
                {appt.notes && <p className="text-xs text-slate-600 mt-2 italic">Note: {appt.notes}</p>}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
