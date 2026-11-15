import React, { useEffect, useState } from 'react';
import { 
  Pill, 
  Plus, 
  AlertTriangle, 
  Clock, 
  Trash2, 
  Edit3, 
  Check, 
  X, 
  Loader2, 
  Sparkles,
  PackageCheck
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { medicationService } from '../services/medicationService';
import { Medication, FrequencyType } from '../types';

export const MedicationsPage: React.FC = () => {
  const { user, activeProfileId } = useAuth();
  const [medications, setMedications] = useState<Medication[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [statusFilter, setStatusFilter] = useState<'active' | 'inactive' | 'all'>('active');

  // Form State
  const [name, setName] = useState('');
  const [dosage, setDosage] = useState('');
  const [unit, setUnit] = useState('mg');
  const [instructions, setInstructions] = useState('');
  const [doctor, setDoctor] = useState('');
  const [inventory, setInventory] = useState('30');
  const [threshold, setThreshold] = useState('7');
  const [startDate, setStartDate] = useState(new Date().toISOString().split('T')[0]);
  const [schedules, setSchedules] = useState<{ time_of_day: string; label: string }[]>([
    { time_of_day: '08:00', label: 'Morning' }
  ]);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const fetchMedications = async () => {
    if (!activeProfileId) return;
    setIsLoading(true);
    try {
      const data = await medicationService.listMedications(activeProfileId, statusFilter);
      setMedications(data);
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchMedications();
  }, [activeProfileId, statusFilter]);

  const handleAddSchedule = () => {
    setSchedules([...schedules, { time_of_day: '20:00', label: 'Evening' }]);
  };

  const handleRemoveSchedule = (index: number) => {
    setSchedules(schedules.filter((_, i) => i !== index));
  };

  const handleScheduleChange = (index: number, field: string, val: string) => {
    const updated = [...schedules];
    updated[index] = { ...updated[index], [field]: val };
    setSchedules(updated);
  };

  const handleCreateMedication = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!activeProfileId || !name || !dosage) return;

    setIsSubmitting(true);
    try {
      await medicationService.addMedication({
        profile_id: activeProfileId,
        name,
        dosage,
        unit,
        instructions,
        prescribing_doctor: doctor,
        current_inventory: parseInt(inventory) || 30,
        refill_alert_threshold: parseInt(threshold) || 7,
        start_date: startDate,
        schedules: schedules.map(s => ({
          time_of_day: s.time_of_day,
          label: s.label,
          days_of_week: 'DAILY',
          reminder_enabled: true,
          dose_quantity: '1 dose'
        })) as any
      });
      setIsModalOpen(false);
      resetForm();
      fetchMedications();
    } catch (err: any) {
      alert(err.response?.data?.error?.message || 'Failed to add medication');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDiscontinue = async (medId: string) => {
    if (!confirm('Are you sure you want to discontinue this medication? It will be archived in medical history.')) return;
    try {
      await medicationService.deleteMedication(medId);
      fetchMedications();
    } catch (e: any) {
      alert(e.response?.data?.error?.message || 'Failed to discontinue medication');
    }
  };

  const resetForm = () => {
    setName('');
    setDosage('');
    setUnit('mg');
    setInstructions('');
    setDoctor('');
    setInventory('30');
    setThreshold('7');
    setSchedules([{ time_of_day: '08:00', label: 'Morning' }]);
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-black text-slate-900 tracking-tight">Medications & Prescriptions</h1>
          <p className="text-slate-600 font-medium">Manage daily schedules, dosage strengths, and inventory refills</p>
        </div>

        <button
          onClick={() => setIsModalOpen(true)}
          className="px-5 py-3 bg-blue-600 hover:bg-blue-700 text-white font-bold text-sm rounded-2xl shadow-lg shadow-blue-500/20 transition flex items-center gap-2 self-start sm:self-auto"
        >
          <Plus className="w-5 h-5" />
          <span>Add New Medication</span>
        </button>
      </div>

      {/* Filter Tabs */}
      <div className="flex gap-2 p-1.5 bg-slate-100 rounded-2xl max-w-xs">
        <button
          onClick={() => setStatusFilter('active')}
          className={`flex-1 py-1.5 text-xs font-bold rounded-xl transition ${
            statusFilter === 'active' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-600 hover:text-slate-900'
          }`}
        >
          Active
        </button>
        <button
          onClick={() => setStatusFilter('inactive')}
          className={`flex-1 py-1.5 text-xs font-bold rounded-xl transition ${
            statusFilter === 'inactive' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-600 hover:text-slate-900'
          }`}
        >
          Discontinued History
        </button>
        <button
          onClick={() => setStatusFilter('all')}
          className={`flex-1 py-1.5 text-xs font-bold rounded-xl transition ${
            statusFilter === 'all' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-600 hover:text-slate-900'
          }`}
        >
          All
        </button>
      </div>

      {/* Medication Grid */}
      {isLoading ? (
        <div className="py-20 text-center">
          <Loader2 className="w-8 h-8 animate-spin text-blue-600 mx-auto" />
          <p className="text-sm font-semibold text-slate-500 mt-2">Loading prescriptions...</p>
        </div>
      ) : medications.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {medications.map((med) => (
            <div key={med.id} className="bg-white rounded-3xl border border-slate-200 p-6 shadow-sm flex flex-col justify-between">
              <div>
                <div className="flex items-start justify-between gap-3 mb-3">
                  <div>
                    <h3 className="text-xl font-bold text-slate-900">{med.name}</h3>
                    <span className="text-sm font-bold text-blue-600">{med.strength}</span>
                  </div>
                  {med.needs_refill && (
                    <span className="px-2.5 py-1 bg-amber-100 text-amber-800 rounded-full text-xs font-bold flex items-center gap-1">
                      <AlertTriangle className="w-3.5 h-3.5" />
                      Refill Soon
                    </span>
                  )}
                </div>

                {med.instructions && (
                  <p className="text-sm text-slate-600 bg-slate-50 p-3 rounded-xl mb-4 font-medium">
                    <em>{med.instructions}</em>
                  </p>
                )}

                <div className="space-y-2 text-xs font-medium text-slate-600 mb-4">
                  <div className="flex items-center gap-1.5">
                    <Clock className="w-4 h-4 text-slate-400" />
                    <span>
                      Daily Times: {med.schedules?.map(s => `${s.time_of_day} (${s.label || 'Dose'})`).join(', ') || 'None set'}
                    </span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <PackageCheck className="w-4 h-4 text-slate-400" />
                    <span>
                      Inventory: <strong className={med.needs_refill ? 'text-amber-600 font-bold' : 'text-slate-800'}>{med.current_inventory} doses remaining</strong> (Alert at {med.refill_alert_threshold})
                    </span>
                  </div>
                  {med.prescribing_doctor && (
                    <p className="text-slate-500">Prescribed by: {med.prescribing_doctor}</p>
                  )}
                </div>
              </div>

              {med.is_active && (
                <div className="pt-4 border-t border-slate-100 flex items-center justify-between">
                  <span className="text-xs text-emerald-600 font-bold uppercase tracking-wider">● Active Prescription</span>
                  <button
                    onClick={() => handleDiscontinue(med.id)}
                    className="p-2 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-xl transition"
                    title="Discontinue Medication"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              )}
            </div>
          ))}
        </div>
      ) : (
        <div className="bg-white border border-slate-200 rounded-3xl p-12 text-center">
          <Pill className="w-12 h-12 text-slate-300 mx-auto mb-3" />
          <h3 className="text-lg font-bold text-slate-900">No Medications Listed</h3>
          <p className="text-sm text-slate-500 max-w-sm mx-auto mt-1 mb-4">
            Click 'Add New Medication' to create schedules and configure dose reminders.
          </p>
        </div>
      )}

      {/* Add Medication Dialog Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4 overflow-y-auto">
          <div className="relative w-full max-w-xl bg-white rounded-3xl shadow-2xl border border-slate-200 overflow-hidden my-8">
            <div className="bg-gradient-to-r from-blue-600 to-indigo-600 px-6 py-5 text-white flex items-center justify-between">
              <h3 className="text-xl font-bold flex items-center gap-2">
                <Pill className="w-6 h-6" />
                <span>Add New Medication</span>
              </h3>
              <button onClick={() => setIsModalOpen(false)} className="text-white/80 hover:text-white">
                <X className="w-6 h-6" />
              </button>
            </div>

            <form onSubmit={handleCreateMedication} className="p-6 space-y-4 max-h-[80vh] overflow-y-auto">
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <div className="sm:col-span-2">
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1">
                    Medication Name *
                  </label>
                  <input
                    type="text"
                    required
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="e.g. Metformin or Lisinopril"
                    className="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm font-semibold focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1">
                    Strength / Unit *
                  </label>
                  <div className="flex gap-2">
                    <input
                      type="text"
                      required
                      value={dosage}
                      onChange={(e) => setDosage(e.target.value)}
                      placeholder="500"
                      className="w-full px-3 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm font-semibold focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    <select
                      value={unit}
                      onChange={(e) => setUnit(e.target.value)}
                      className="px-2 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs font-bold text-slate-700"
                    >
                      <option value="mg">mg</option>
                      <option value="ml">ml</option>
                      <option value="tablet">tablet</option>
                      <option value="capsule">capsule</option>
                      <option value="drops">drops</option>
                      <option value="IU">IU</option>
                    </select>
                  </div>
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1">
                  Instructions
                </label>
                <input
                  type="text"
                  value={instructions}
                  onChange={(e) => setInstructions(e.target.value)}
                  placeholder="e.g. Take with breakfast; swallow with full glass of water"
                  className="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm font-medium focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              {/* Scheduled Administration Times */}
              <div className="p-4 bg-blue-50/60 border border-blue-200 rounded-2xl">
                <div className="flex items-center justify-between mb-3">
                  <span className="text-xs font-bold uppercase tracking-wider text-blue-900">
                    Administration Times (Daily)
                  </span>
                  <button
                    type="button"
                    onClick={handleAddSchedule}
                    className="text-xs font-bold text-blue-700 hover:text-blue-900 flex items-center gap-1"
                  >
                    <Plus className="w-4 h-4" />
                    <span>Add Dose Time</span>
                  </button>
                </div>

                <div className="space-y-2">
                  {schedules.map((s, idx) => (
                    <div key={idx} className="flex items-center gap-2">
                      <input
                        type="time"
                        value={s.time_of_day}
                        onChange={(e) => handleScheduleChange(idx, 'time_of_day', e.target.value)}
                        className="px-3 py-2 bg-white border border-slate-200 rounded-xl text-sm font-mono font-bold"
                      />
                      <input
                        type="text"
                        value={s.label}
                        onChange={(e) => handleScheduleChange(idx, 'label', e.target.value)}
                        placeholder="Label e.g. Breakfast"
                        className="flex-1 px-3 py-2 bg-white border border-slate-200 rounded-xl text-sm font-medium"
                      />
                      {schedules.length > 1 && (
                        <button
                          type="button"
                          onClick={() => handleRemoveSchedule(idx)}
                          className="p-2 text-red-500 hover:bg-red-50 rounded-xl"
                        >
                          <X className="w-4 h-4" />
                        </button>
                      )}
                    </div>
                  ))}
                </div>
              </div>

              {/* Inventory & Prescriber */}
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1">
                    Current Stock
                  </label>
                  <input
                    type="number"
                    value={inventory}
                    onChange={(e) => setInventory(e.target.value)}
                    className="w-full px-3 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm font-semibold"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1">
                    Refill Alert
                  </label>
                  <input
                    type="number"
                    value={threshold}
                    onChange={(e) => setThreshold(e.target.value)}
                    className="w-full px-3 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm font-semibold"
                  />
                </div>
                <div className="col-span-2 sm:col-span-1">
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1">
                    Start Date
                  </label>
                  <input
                    type="date"
                    value={startDate}
                    onChange={(e) => setStartDate(e.target.value)}
                    className="w-full px-3 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm font-semibold"
                  />
                </div>
              </div>

              <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2.5 text-sm font-semibold text-slate-600 hover:text-slate-800"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="px-6 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-bold text-sm rounded-xl shadow-md transition flex items-center gap-2"
                >
                  {isSubmitting && <Loader2 className="w-4 h-4 animate-spin" />}
                  <span>Save Medication</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
