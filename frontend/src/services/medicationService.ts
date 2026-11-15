import { api } from './api';
import { Medication } from '../types';

export const medicationService = {
  async listMedications(profileId: string, status: 'active' | 'inactive' | 'all' = 'active'): Promise<Medication[]> {
    const res = await api.get(`/medications?profile_id=${profileId}&status=${status}`);
    return res.data.data;
  },

  async getMedication(id: string): Promise<Medication> {
    const res = await api.get(`/medications/${id}`);
    return res.data.data;
  },

  async addMedication(data: Partial<Medication>): Promise<Medication> {
    const res = await api.post('/medications', data);
    return res.data.data;
  },

  async updateMedication(id: string, data: Partial<Medication>): Promise<Medication> {
    const res = await api.put(`/medications/${id}`, data);
    return res.data.data;
  },

  async deleteMedication(id: string): Promise<void> {
    await api.delete(`/medications/${id}`);
  }
};
