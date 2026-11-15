import { api } from './api';

export const dashboardService = {
  async getElderlyDashboard(profileId?: string) {
    const url = profileId ? `/dashboard/elderly?profile_id=${profileId}` : '/dashboard/elderly';
    const res = await api.get(url);
    return res.data.data;
  },

  async getFamilyDashboard() {
    const res = await api.get('/dashboard/family');
    return res.data.data;
  },

  async getCaretakerDashboard() {
    const res = await api.get('/dashboard/caretaker');
    return res.data.data;
  }
};
