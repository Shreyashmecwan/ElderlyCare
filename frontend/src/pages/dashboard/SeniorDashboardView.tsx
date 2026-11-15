import React, { useState } from 'react';
import { 
  CheckCircle2, 
  Clock, 
  AlertTriangle, 
  PhoneCall, 
  Calendar, 
  Pill, 
  Sparkles,
  Loader2,
  AlertCircle
} from 'lucide-react';
import { adherenceService } from '../../services/adherenceService';

interface SeniorDashboardProps {
  data: any;
  onRefresh: () => void;
}

export const SeniorDashboardView: React.FC<SeniorDashboardProps> = ({ data, onRefresh }) => {
  const [markingId, setMarkingId] = useState<string | null>(null);
  const [feedbackMsg, setFeedbackMsg] = useState<string | null>(null);

  const { profile, summary, next_dose, today_doses, next_appointment, emergency_contact } = data;

  const handleMarkDose = async (logId: string, status: 'TAKEN' | 'SKIPPED') => {
    setMarkingId(logId);
    try {
      await adherenceService.updateDoseStatus(logId, status);
      setFeedbackMsg(status === 'TAKEN' ? 'Great job! Medication recorded as taken.' : 'Medication marked as skipped.');
      setTimeout(() => setFeedbackMsg(null), 3000);
      onRefresh();
    } catch (e: any) {
      alert(e.response?.data?.error?.message || 'Failed to update dose');
    } finally {
      setMarkingId(null);
    }
  };

  return (
    <div className="space-y-6">
      {/* Friendly Accessible Greeting Banner */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-700 rounded-3xl p-6 sm:p-8 text-white shadow-xl shadow-blue-500/20">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div>
            <div className="inline-flex items-center gap-2 bg-white/15 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider text-blue-100 mb-3">
              <Sparkles className="w-4 h-4 text-amber-300" />
              <span>Today's Healthcare Routine</span>
            </div>
            <h1 className="text-3xl sm:text-4xl font-black tracking-tight">
              Hello, {profile?.full_name || 'Friend'}!
            </h1>
            <p className="mt-2 text-base sm:text-lg text-blue-100 font-medium">
              You've completed <strong className="text-white font-bold">{summary?.taken_today || 0} of {summary?.total_today || 0}</strong> scheduled doses today.
            </p>
          </div>

          {/* Quick Emergency Action Call Card */}
          {emergency_contact && emergency_contact.phone && (
            <div className="bg-white/10 backdrop-blur-md border border-white/20 p-4 rounded-2xl flex items-center gap-4">
              <div className="w-12 h-12 rounded-xl bg-red-500 flex items-center justify-center text-white shadow-lg">
                <PhoneCall className="w-6 h-6" />
              </div>
              <div>
                <p className="text-xs uppercase font-bold tracking-wider text-red-200">Emergency Contact</p>
                <p className="font-bold text-white text-base">{emergency_contact.name}</p>
                <a
                  href={`tel:${emergency_contact.phone}`}
                  className="inline-block text-xs font-black text-amber-300 hover:underline"
                >
                  Call: {emergency_contact.phone}
                </a>
              </div>
            </div>
          )}
        </div>
      </div>

      {feedbackMsg && (
        <div className="p-4 bg-emerald-100 border-2 border-emerald-500 rounded-2xl text-emerald-900 font-bold text-lg flex items-center gap-3 animate-bounce">
          <CheckCircle2 className="w-6 h-6 text-emerald-600 flex-shrink-0" />
          <span>{feedbackMsg}</span>
        </div>
      )}

      {/* Hero: Next Dose Card (Ultra-accessible, massive buttons) */}
      {next_dose ? (
        <div className="bg-white border-2 border-blue-200 rounded-3xl p-6 sm:p-8 shadow-xl shadow-slate-200/50">
          <div className="flex items-center gap-2 text-blue-700 font-bold text-sm uppercase tracking-wider mb-2">
            <Clock className="w-5 h-5 text-blue-600" />
            <span>Next Upcoming Dose</span>
          </div>
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-6">
            <div>
              <h2 className="text-2xl sm:text-3xl font-black text-slate-900">
                {next_dose.medication_name} ({next_dose.dosage} {next_dose.unit})
              </h2>
              <div className="mt-2 flex flex-wrap items-center gap-3 text-slate-600 font-medium text-base">
                <span className="bg-blue-50 text-blue-800 px-3 py-1 rounded-xl font-bold">
                  Scheduled for {next_dose.scheduled_time} ({next_dose.label || 'Dose'})
                </span>
                {next_dose.instructions && (
                  <span className="text-slate-500 italic">Instructions: {next_dose.instructions}</span>
                )}
              </div>
            </div>

            {/* Big Action Buttons */}
            <div className="flex items-center gap-3">
              <button
                type="button"
                onClick={() => handleMarkDose(next_dose.id, 'TAKEN')}
                disabled={markingId === next_dose.id}
                className="flex-1 sm:flex-none px-8 py-5 bg-emerald-600 hover:bg-emerald-700 active:scale-95 text-white font-black text-lg sm:text-xl rounded-2xl shadow-xl shadow-emerald-600/30 transition-all flex items-center justify-center gap-3 min-w-[200px]"
              >
                {markingId === next_dose.id ? (
                  <Loader2 className="w-6 h-6 animate-spin" />
                ) : (
                  <CheckCircle2 className="w-7 h-7" />
                )}
                <span>I Took It!</span>
              </button>

              <button
                type="button"
                onClick={() => handleMarkDose(next_dose.id, 'SKIPPED')}
                disabled={markingId === next_dose.id}
                className="px-5 py-5 bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-base rounded-2xl transition-all"
              >
                Skip
              </button>
            </div>
          </div>
        </div>
      ) : (
        <div className="bg-emerald-50 border-2 border-emerald-200 rounded-3xl p-6 text-center">
          <div className="w-12 h-12 mx-auto rounded-full bg-emerald-100 flex items-center justify-center text-emerald-600 mb-2">
            <CheckCircle2 className="w-6 h-6" />
          </div>
          <h3 className="text-xl font-bold text-emerald-900">All Done for Right Now!</h3>
          <p className="text-emerald-700 text-sm mt-1">
            You have no pending medications right now. Great job keeping up with your health!
          </p>
        </div>
      )}

      {/* Today's Schedule Checklist */}
      <div className="bg-white rounded-3xl border border-slate-200 p-6 sm:p-8 shadow-sm">
        <h3 className="text-xl font-black text-slate-900 mb-4 flex items-center gap-2">
          <Pill className="w-6 h-6 text-blue-600" />
          <span>Today's Complete Schedule</span>
        </h3>

        {today_doses && today_doses.length > 0 ? (
          <div className="space-y-3">
            {today_doses.map((dose: any) => {
              const isTaken = dose.status === 'TAKEN';
              const isMissed = dose.status === 'MISSED';
              const isSkipped = dose.status === 'SKIPPED';
              const isUpcoming = dose.status === 'UPCOMING';

              return (
                <div
                  key={dose.id}
                  className={`p-4 sm:p-5 rounded-2xl border-2 flex flex-col sm:flex-row sm:items-center justify-between gap-4 transition-all ${
                    isTaken 
                      ? 'bg-emerald-50/50 border-emerald-200' 
                      : isMissed 
                      ? 'bg-red-50/50 border-red-200'
                      : isSkipped
                      ? 'bg-slate-50 border-slate-200 opacity-60'
                      : 'bg-white border-slate-200 hover:border-blue-300'
                  }`}
                >
                  <div className="flex items-center gap-4">
                    <div className="w-14 h-14 rounded-2xl flex items-center justify-center font-black text-sm bg-slate-100 text-slate-800 border border-slate-200">
                      {dose.scheduled_time}
                    </div>
                    <div>
                      <h4 className="text-lg font-bold text-slate-900">
                        {dose.medication_name} ({dose.dosage} {dose.unit})
                      </h4>
                      <p className="text-xs text-slate-500 font-medium">
                        {dose.label || 'Dose'} • {dose.instructions || 'Standard administration'}
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    {isTaken && (
                      <span className="inline-flex items-center gap-1.5 px-4 py-2 bg-emerald-600 text-white rounded-xl font-bold text-sm">
                        <CheckCircle2 className="w-4 h-4" />
                        Taken
                      </span>
                    )}

                    {isMissed && (
                      <span className="inline-flex items-center gap-1.5 px-4 py-2 bg-red-600 text-white rounded-xl font-bold text-sm">
                        <AlertTriangle className="w-4 h-4" />
                        Missed
                      </span>
                    )}

                    {isSkipped && (
                      <span className="inline-flex items-center gap-1.5 px-4 py-2 bg-slate-200 text-slate-700 rounded-xl font-bold text-sm">
                        Skipped
                      </span>
                    )}

                    {isUpcoming && (
                      <button
                        type="button"
                        onClick={() => handleMarkDose(dose.id, 'TAKEN')}
                        disabled={markingId === dose.id}
                        className="px-5 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-bold rounded-xl text-sm transition shadow-sm"
                      >
                        {markingId === dose.id ? 'Saving...' : 'Mark Taken'}
                      </button>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <p className="text-slate-500 text-sm">No scheduled medications recorded for today.</p>
        )}
      </div>

      {/* Upcoming Doctor Appointment Widget */}
      {next_appointment && (
        <div className="bg-gradient-to-br from-indigo-50 to-blue-50 border border-blue-200 rounded-3xl p-6">
          <div className="flex items-center gap-2 text-indigo-800 font-bold text-xs uppercase tracking-wider mb-2">
            <Calendar className="w-4 h-4" />
            <span>Next Doctor Appointment</span>
          </div>
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <h4 className="text-xl font-black text-slate-900">
                Dr. {next_appointment.doctor_name} — {next_appointment.specialty}
              </h4>
              <p className="text-slate-600 text-sm font-medium mt-1">
                {next_appointment.appointment_date} at {next_appointment.appointment_time} • {next_appointment.hospital_clinic}
              </p>
            </div>
            <span className="px-4 py-2 bg-indigo-600 text-white text-xs font-bold rounded-xl uppercase tracking-wider self-start sm:self-auto">
              Confirmed
            </span>
          </div>
        </div>
      )}
    </div>
  );
};
