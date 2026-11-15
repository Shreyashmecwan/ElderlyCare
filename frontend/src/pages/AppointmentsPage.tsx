import React, { useEffect, useState } from 'react';
import { 
  Calendar as CalendarIcon, 
  Plus, 
  Clock, 
  MapPin, 
  User, 
  X, 
  Loader2, 
  Ban, 
  CheckCircle2 
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { appointmentService } from '../services/appointmentService';
import { Appointment, AppointmentType } from '../types';

export const AppointmentsPage: React.FC = () => {
  const { activeProfileId } = useAuth();
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [filter, setFilter] = useState<'upcoming' | 'past' | 'all'>('upcoming');
  const [isLoading, setIsLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);

  // Form State
  const [doctorName, setDoctorName] = useState('');
  const [specialty, setSpecialty] = useState('');
  const [hospitalClinic, setHospitalClinic] = useState('');
  const [location, setLocation] = useState('');
  const [date, setDate] = useState(new Date().toISOString().split('T')[0]);
  const [time, setTime] = useState('10:00');
  const [type, setType] = useState<AppointmentType>('IN_PERSON');
  const [notes, setNotes] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const fetchAppointments = async () => {
    if (!activeProfileId) return;
    setIsLoading(true);
    try {
      const data = await appointmentService.listAppointments(activeProfileId, filter);
      setAppointments(data);
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchAppointments();
  }, [activeProfileId, filter]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!activeProfileId || !doctorName || !date || !time) return;

    setIsSubmitting(true);
    try {
      await appointmentService.createAppointment({
        profile_id: activeProfileId,
        doctor_name: doctorName,
        specialty,
        hospital_clinic: hospitalClinic,
        location,
        appointment_date: date,
        appointment_time: time,
        appointment_type: type,
        notes
      });
      setIsModalOpen(false);
      resetForm();
      fetchAppointments();
    } catch (err: any) {
      alert(err.response?.data?.error?.message || 'Failed to schedule appointment');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCancel = async (id: string) => {
    if (!confirm('Are you sure you want to cancel this appointment?')) return;
    try {
      await appointmentService.cancelAppointment(id);
      fetchAppointments();
    } catch (e: any) {
      alert(e.response?.data?.error?.message || 'Failed to cancel appointment');
    }
  };

  const resetForm = () => {
    setDoctorName('');
    setSpecialty('');
    setHospitalClinic('');
    setLocation('');
    setTime('10:00');
    setNotes('');
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-black text-slate-900 tracking-tight">Doctor Appointments</h1>
          <p className="text-slate-600 font-medium">Coordinate healthcare visits, checkups, and reminder notifications</p>
        </div>

        <button
          onClick={() => setIsModalOpen(true)}
          className="px-5 py-3 bg-blue-600 hover:bg-blue-700 text-white font-bold text-sm rounded-2xl shadow-lg shadow-blue-500/20 transition flex items-center gap-2 self-start sm:self-auto"
        >
          <Plus className="w-5 h-5" />
          <span>Book Appointment</span>
        </button>
      </div>

      {/* Filter Tabs */}
      <div className="flex gap-2 p-1.5 bg-slate-100 rounded-2xl max-w-xs">
        <button
          onClick={() => setFilter('upcoming')}
          className={`flex-1 py-1.5 text-xs font-bold rounded-xl transition ${
            filter === 'upcoming' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-600 hover:text-slate-900'
          }`}
        >
          Upcoming
        </button>
        <button
          onClick={() => setFilter('past')}
          className={`flex-1 py-1.5 text-xs font-bold rounded-xl transition ${
            filter === 'past' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-600 hover:text-slate-900'
          }`}
        >
          Past
        </button>
        <button
          onClick={() => setFilter('all')}
          className={`flex-1 py-1.5 text-xs font-bold rounded-xl transition ${
            filter === 'all' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-600 hover:text-slate-900'
          }`}
        >
          All
        </button>
      </div>

      {/* Appointment Cards */}
      {isLoading ? (
        <div className="py-20 text-center">
          <Loader2 className="w-8 h-8 animate-spin text-blue-600 mx-auto" />
          <p className="text-sm font-semibold text-slate-500 mt-2">Loading appointments...</p>
        </div>
      ) : appointments.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {appointments.map((appt) => {
            const isCancelled = appt.status === 'CANCELLED';
            const isCompleted = appt.status === 'COMPLETED';

            return (
              <div 
                key={appt.id} 
                className={`bg-white rounded-3xl border p-6 shadow-sm flex flex-col justify-between transition-all ${
                  isCancelled ? 'border-red-200 opacity-60' : 'border-slate-200 hover:border-blue-300'
                }`}
              >
                <div>
                  <div className="flex items-start justify-between gap-3 mb-3">
                    <div>
                      <h3 className="text-xl font-bold text-slate-900">Dr. {appt.doctor_name}</h3>
                      <span className="text-xs font-bold text-blue-600">{appt.specialty || 'General Practitioner'}</span>
                    </div>
                    <span className={`px-2.5 py-1 rounded-full text-xs font-black uppercase tracking-wider ${
                      isCancelled 
                        ? 'bg-red-100 text-red-800' 
                        : isCompleted 
                        ? 'bg-emerald-100 text-emerald-800' 
                        : 'bg-indigo-100 text-indigo-800'
                    }`}>
                      {appt.status}
                    </span>
                  </div>

                  <div className="space-y-2 py-3 border-y border-slate-100 text-sm text-slate-600 font-medium">
                    <div className="flex items-center gap-2">
                      <CalendarIcon className="w-4 h-4 text-slate-400" />
                      <span>{appt.appointment_date} at {appt.appointment_time}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <MapPin className="w-4 h-4 text-slate-400" />
                      <span className="truncate">{appt.hospital_clinic || appt.location || 'Clinic'}</span>
                    </div>
                  </div>

                  {appt.notes && (
                    <p className="text-xs text-slate-500 italic mt-3 bg-slate-50 p-2.5 rounded-xl">
                      Note: {appt.notes}
                    </p>
                  )}
                </div>

                {!isCancelled && !isCompleted && (
                  <div className="pt-4 mt-4 border-t border-slate-100 flex justify-end">
                    <button
                      onClick={() => handleCancel(appt.id)}
                      className="text-xs font-bold text-red-600 hover:text-red-700 flex items-center gap-1 hover:underline"
                    >
                      <Ban className="w-3.5 h-3.5" />
                      <span>Cancel Visit</span>
                    </button>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      ) : (
        <div className="bg-white border border-slate-200 rounded-3xl p-12 text-center">
          <CalendarIcon className="w-12 h-12 text-slate-300 mx-auto mb-3" />
          <h3 className="text-lg font-bold text-slate-900">No Appointments Recorded</h3>
          <p className="text-sm text-slate-500 max-w-sm mx-auto mt-1 mb-4">
            Click 'Book Appointment' to schedule clinic checkups and setup email reminders.
          </p>
        </div>
      )}

      {/* Book Appointment Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4 overflow-y-auto">
          <div className="relative w-full max-w-lg bg-white rounded-3xl shadow-2xl border border-slate-200 overflow-hidden my-8">
            <div className="bg-gradient-to-r from-blue-600 to-indigo-600 px-6 py-5 text-white flex items-center justify-between">
              <h3 className="text-xl font-bold flex items-center gap-2">
                <CalendarIcon className="w-6 h-6" />
                <span>Book Medical Appointment</span>
              </h3>
              <button onClick={() => setIsModalOpen(false)} className="text-white/80 hover:text-white">
                <X className="w-6 h-6" />
              </button>
            </div>

            <form onSubmit={handleCreate} className="p-6 space-y-4">
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1">
                  Doctor or Clinician Name *
                </label>
                <input
                  type="text"
                  required
                  value={doctorName}
                  onChange={(e) => setDoctorName(e.target.value)}
                  placeholder="e.g. Robert Hayes"
                  className="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm font-semibold focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1">
                    Specialty
                  </label>
                  <input
                    type="text"
                    value={specialty}
                    onChange={(e) => setSpecialty(e.target.value)}
                    placeholder="e.g. Cardiologist"
                    className="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm font-semibold"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1">
                    Visit Type
                  </label>
                  <select
                    value={type}
                    onChange={(e) => setType(e.target.value as AppointmentType)}
                    className="w-full px-3 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs font-bold text-slate-700"
                  >
                    <option value="IN_PERSON">In-Person Visit</option>
                    <option value="VIRTUAL">Virtual / Telehealth</option>
                    <option value="HOME_VISIT">Home Visit</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1">
                  Hospital or Clinic Name
                </label>
                <input
                  type="text"
                  value={hospitalClinic}
                  onChange={(e) => setHospitalClinic(e.target.value)}
                  placeholder="e.g. Springfield Memorial Health Institute"
                  className="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm font-medium"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1">
                    Date *
                  </label>
                  <input
                    type="date"
                    required
                    value={date}
                    onChange={(e) => setDate(e.target.value)}
                    className="w-full px-3 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm font-semibold"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1">
                    Time (HH:MM) *
                  </label>
                  <input
                    type="time"
                    required
                    value={time}
                    onChange={(e) => setTime(e.target.value)}
                    className="w-full px-3 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm font-semibold font-mono"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-1">
                  Preparation & Clinical Notes
                </label>
                <textarea
                  rows={3}
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  placeholder="e.g. Fast for 10 hours prior to visit; bring recent blood pressure logs"
                  className="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm font-medium"
                />
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
                  <span>Book Appointment</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
