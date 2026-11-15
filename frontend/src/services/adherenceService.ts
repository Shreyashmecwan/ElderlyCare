import { api } from './api';
import { MedicationLog, AdherenceStats } from '../types';

export const adherenceService = {
  async getDailyLogs(profileId: string, date?: string): Promise<MedicationLog[]> {
    const url = date ? `/adherence/daily?profile_id=${profileId}&date=${date}` : `/adherence/daily?profile_id=${profileId}`;
    const res = await api.get(url);
    return res.data.data;
  },

  async updateDoseStatus(logId: string, status: string, notes?: string): Promise<MedicationLog> {
    const res = await api.post(`/adherence/${logId}/status`, { status, notes });
    return res.data.data;
  },

  async getAdherenceStats(profileId: string, days: number = 7): Promise<AdherenceStats> {
    const res = await api.get(`/adherence/stats?profile_id=${profileId}&days=${days}`);
    return res.data.data;
  },

  async getAuditTrail(profileId: string) {
    const res = await api.get(`/adherence/audit-trail?profile_id=${profileId}`);
    return res.data.data;
  }
};
