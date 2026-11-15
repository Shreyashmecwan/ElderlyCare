import { api } from './api';
import { Appointment } from '../types';

export const appointmentService = {
  async listAppointments(profileId: string, filter: 'upcoming' | 'past' | 'all' = 'upcoming'): Promise<Appointment[]> {
    const res = await api.get(`/appointments?profile_id=${profileId}&filter=${filter}`);
    return res.data.data;
  },

  async createAppointment(data: Partial<Appointment>): Promise<Appointment> {
    const res = await api.post('/appointments', data);
    return res.data.data;
  },

  async updateAppointment(id: string, data: Partial<Appointment>): Promise<Appointment> {
    const res = await api.put(`/appointments/${id}`, data);
    return res.data.data;
  },

  async cancelAppointment(id: string): Promise<Appointment> {
    const res = await api.patch(`/appointments/${id}/cancel`);
    return res.data.data;
  },

  async deleteAppointment(id: string): Promise<void> {
    await api.delete(`/appointments/${id}`);
  }
};
