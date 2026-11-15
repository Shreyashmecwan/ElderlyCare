import React, { useState } from 'react';
import { 
  Users, 
  Clock, 
  CheckCircle2, 
  AlertTriangle, 
  Pill, 
  Calendar, 
  Search, 
  Loader2,
  FileText
} from 'lucide-react';
import { adherenceService } from '../../services/adherenceService';

interface CaretakerDashboardProps {
  data: any;
  onRefresh: () => void;
  onOpenPasscode: () => void;
}

export const CaretakerDashboardView: React.FC<CaretakerDashboardProps> = ({ data, onRefresh, onOpenPasscode }) => {
  const { assigned_patients, master_daily_doses, upcoming_appointments } = data;
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedPatientId, setSelectedPatientId] = useState<string>('ALL');
  const [markingId, setMarkingId] = useState<string | null>(null);

  const handleUpdateDose = async (logId: string, status: string) => {
    setMarkingId(logId);
    try {
      await adherenceService.updateDoseStatus(logId, status);
      onRefresh();
    } catch (e: any) {
      alert(e.response?.data?.error?.message || 'Failed to update dose');
    } finally {
      setMarkingId(null);
    }
  };

  const filteredDoses = (master_daily_doses || []).filter((dose: any) => {
    const matchesPatient = selectedPatientId === 'ALL' || dose.patient_id === selectedPatientId;
    const matchesSearch = dose.medication_name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
                          dose.patient_name?.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesPatient && matchesSearch;
  });

  return (
    <div className="space-y-8">
      {/* Caretaker Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-black text-slate-900 tracking-tight">Caretaker Clinical Station</h1>
          <p className="text-slate-600 font-medium">Daily administration rounds and patient supervision</p>
        </div>
        <button
          onClick={onOpenPasscode}
          className="px-5 py-3 bg-purple-600 hover:bg-purple-700 text-white font-bold text-sm rounded-2xl shadow-lg shadow-purple-500/20 transition self-start sm:self-auto"
        >
          + Add Assigned Patient (Passcode)
        </button>
      </div>

      {/* Patient Caseload Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white p-5 rounded-2xl border border-slate-200">
          <p className="text-xs font-bold uppercase tracking-wider text-slate-500">Active Patients</p>
          <p className="text-3xl font-black text-slate-900 mt-1">{assigned_patients?.length || 0}</p>
        </div>
        <div className="bg-white p-5 rounded-2xl border border-slate-200">
          <p className="text-xs font-bold uppercase tracking-wider text-slate-500">Today's Scheduled Rounds</p>
          <p className="text-3xl font-black text-blue-600 mt-1">{master_daily_doses?.length || 0}</p>
        </div>
        <div className="bg-white p-5 rounded-2xl border border-slate-200">
          <p className="text-xs font-bold uppercase tracking-wider text-slate-500">Doses Administered</p>
          <p className="text-3xl font-black text-emerald-600 mt-1">
            {master_daily_doses?.filter((d: any) => d.status === 'TAKEN').length || 0}
          </p>
        </div>
        <div className="bg-white p-5 rounded-2xl border border-slate-200">
          <p className="text-xs font-bold uppercase tracking-wider text-slate-500">Pending / Overdue</p>
          <p className="text-3xl font-black text-amber-600 mt-1">
            {master_daily_doses?.filter((d: any) => d.status === 'UPCOMING' || d.status === 'MISSED').length || 0}
          </p>
        </div>
      </div>

      {/* Master Daily Administration Timeline */}
      <div className="bg-white border border-slate-200 rounded-3xl p-6 sm:p-8 shadow-sm">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
          <div>
            <h2 className="text-xl font-black text-slate-900 flex items-center gap-2">
              <Clock className="w-5 h-5 text-purple-600" />
              <span>Master Administration Timeline</span>
            </h2>
            <p className="text-xs text-slate-500">Sorted chronologically across all assigned individuals</p>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            {/* Filter by Patient */}
            <select
              value={selectedPatientId}
              onChange={(e) => setSelectedPatientId(e.target.value)}
              className="px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-bold text-slate-700"
            >
              <option value="ALL">All Patients ({assigned_patients?.length || 0})</option>
              {assigned_patients?.map((p: any) => (
                <option key={p.profile_id} value={p.profile_id}>
                  {p.full_name}
                </option>
              ))}
            </select>

            {/* Search Input */}
            <div className="relative">
              <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
              <input
                type="text"
                placeholder="Search medication or patient..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-9 pr-3 py-1.5 text-xs bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500"
              />
            </div>
          </div>
        </div>

        {filteredDoses && filteredDoses.length > 0 ? (
          <div className="divide-y divide-slate-100">
            {filteredDoses.map((dose: any) => {
              const isTaken = dose.status === 'TAKEN';
              const isMissed = dose.status === 'MISSED';
              const isUpcoming = dose.status === 'UPCOMING';

              return (
                <div key={dose.id} className="py-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                  <div className="flex items-start gap-4">
                    <div className="px-3 py-2 bg-purple-50 border border-purple-200 rounded-xl font-mono text-sm font-black text-purple-900">
                      {dose.scheduled_time}
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-black text-base text-slate-900">{dose.medication_name}</span>
                        <span className="text-xs px-2 py-0.5 bg-slate-100 rounded-md font-bold text-slate-600">
                          {dose.dosage} {dose.unit}
                        </span>
                        <span className="text-xs px-2 py-0.5 bg-blue-50 text-blue-700 rounded-md font-bold">
                          Patient: {dose.patient_name}
                        </span>
                      </div>
                      <p className="text-xs text-slate-500 mt-1">
                        {dose.label || 'Dose'} • {dose.instructions || 'Standard routine'}
                        {dose.notes && <span className="ml-2 text-slate-700 italic font-medium">({dose.notes})</span>}
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center gap-2 self-end sm:self-auto">
                    {isTaken ? (
                      <span className="px-4 py-1.5 bg-emerald-50 text-emerald-800 border border-emerald-200 rounded-xl text-xs font-black flex items-center gap-1.5">
                        <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                        Administered
                      </span>
                    ) : (
                      <>
                        <button
                          type="button"
                          onClick={() => handleUpdateDose(dose.id, 'TAKEN')}
                          disabled={markingId === dose.id}
                          className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs rounded-xl shadow-sm transition flex items-center gap-1.5"
                        >
                          {markingId === dose.id ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <CheckCircle2 className="w-3.5 h-3.5" />}
                          <span>Administer</span>
                        </button>
                        <button
                          type="button"
                          onClick={() => handleUpdateDose(dose.id, 'SKIPPED')}
                          disabled={markingId === dose.id}
                          className="px-3 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-xs rounded-xl transition"
                        >
                          Skip
                        </button>
                      </>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <p className="text-center py-8 text-sm text-slate-500">No scheduled doses match the selected filters.</p>
        )}
      </div>
    </div>
  );
};
